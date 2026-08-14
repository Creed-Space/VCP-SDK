"""Security regression tests for signed VCP skills."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from vcp.skill_security import (
    MAX_SKILL_FILE_BYTES,
    compute_skill_hash,
    main,
    sign_skill,
    verify_skill,
)
from vcp.trust import TrustAnchor, TrustConfig


def _make_signed_skill(tmp_path: Path) -> tuple[Path, TrustConfig]:
    skill = tmp_path / "skill"
    skill.mkdir()
    (skill / "SKILL.md").write_text(
        "---\nname: safe-skill\nversion: 1.0.0\n---\n# Safe skill\n",
        encoding="utf-8",
    )
    private_key = Ed25519PrivateKey.generate()
    key_path = tmp_path / "key.pem"
    key_path.write_bytes(
        private_key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )
    manifest = sign_skill(skill, key_path, issuer="test-issuer")
    public_key = private_key.public_key().public_bytes(
        serialization.Encoding.Raw,
        serialization.PublicFormat.Raw,
    )
    import base64

    now = datetime.now(timezone.utc)
    anchor = TrustAnchor(
        id="test-issuer",
        key_id=manifest["issuer"]["key_id"],
        algorithm="ed25519",
        public_key=base64.b64encode(public_key).decode("ascii"),
        anchor_type="issuer",
        valid_from=now - timedelta(days=1),
        valid_until=now + timedelta(days=1),
    )
    trust = TrustConfig()
    trust.add_issuer("test-issuer", anchor)
    return skill, trust


def test_trusted_signature_verification_succeeds(tmp_path: Path) -> None:
    skill, trust = _make_signed_skill(tmp_path)
    valid, reason = verify_skill(skill, trust)
    assert valid, reason


def test_verification_requires_explicit_trust_mode(tmp_path: Path) -> None:
    skill, _trust = _make_signed_skill(tmp_path)
    valid, reason = verify_skill(skill)
    assert not valid
    assert "Trust configuration is required" in reason

    structural, structural_reason = verify_skill(skill, allow_structural_only=True)
    assert structural, structural_reason


def test_manifest_signed_fields_must_be_complete(tmp_path: Path) -> None:
    skill, trust = _make_signed_skill(tmp_path)
    manifest_path = skill / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["signature"]["signed_fields"].remove("skill")
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    valid, reason = verify_skill(skill, trust)
    assert not valid
    assert "signed_fields" in reason


def test_declared_file_list_must_match_directory(tmp_path: Path) -> None:
    skill, _trust = _make_signed_skill(tmp_path)
    manifest_path = skill / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["skill"]["files"] = []
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    valid, reason = verify_skill(skill, allow_structural_only=True)
    assert not valid
    assert "file list" in reason


def test_symbolic_links_are_rejected(tmp_path: Path) -> None:
    skill = tmp_path / "skill"
    skill.mkdir()
    outside = tmp_path / "outside.md"
    outside.write_text("outside", encoding="utf-8")
    (skill / "SKILL.md").symlink_to(outside)
    with pytest.raises(ValueError, match="Symbolic links"):
        compute_skill_hash(skill)


def test_oversized_markdown_is_rejected(tmp_path: Path) -> None:
    skill = tmp_path / "skill"
    skill.mkdir()
    (skill / "SKILL.md").write_bytes(b"x" * (MAX_SKILL_FILE_BYTES + 1))
    with pytest.raises(ValueError, match="exceeds"):
        compute_skill_hash(skill)


def test_cli_requires_explicit_verification_mode(tmp_path: Path) -> None:
    skill, _trust = _make_signed_skill(tmp_path)
    assert main(["verify", str(skill)]) == 1
    assert main(["verify", str(skill), "--structural-only"]) == 0
