"""
VCP Skill Security Module

Signs skill directories with VCP/T manifests and verifies their provenance.
Thin wrapper around existing VCP cryptographic primitives.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import yaml
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from .canonicalize import canonicalize_content, canonicalize_manifest
from .trust import TrustConfig


# ---------------------------------------------------------------------------
# Frontmatter parsing
# ---------------------------------------------------------------------------


def _parse_frontmatter(content: str) -> dict[str, Any]:
    """Extract YAML frontmatter from markdown.

    Parses the YAML block between opening and closing ``---`` delimiters
    at the very start of a file.

    Args:
        content: Raw markdown string (may or may not have frontmatter).

    Returns:
        Parsed frontmatter as a dict, or empty dict if none found.
    """
    if not content.startswith("---"):
        return {}
    try:
        end = content.index("---", 3)
    except ValueError:
        return {}
    raw = content[3:end]
    parsed = yaml.safe_load(raw)
    return parsed if isinstance(parsed, dict) else {}


# ---------------------------------------------------------------------------
# Content hashing
# ---------------------------------------------------------------------------


def compute_skill_hash(skill_dir: Path) -> str:
    """Compute a deterministic SHA-256 hash over all ``.md`` files in a skill directory.

    Files are sorted by their path relative to *skill_dir* and concatenated
    with deterministic separators before canonicalization and hashing.

    Args:
        skill_dir: Root directory of the skill.

    Returns:
        Hash string in the format ``"sha256:{hex}"``.

    Raises:
        FileNotFoundError: If *skill_dir* does not exist or contains no
            ``.md`` files.
    """
    skill_dir = skill_dir.resolve()
    if not skill_dir.is_dir():
        raise FileNotFoundError(f"Skill directory not found: {skill_dir}")

    md_files = sorted(skill_dir.rglob("*.md"), key=lambda p: p.relative_to(skill_dir).as_posix())

    if not md_files:
        raise FileNotFoundError(f"No .md files found in {skill_dir}")

    parts: list[str] = []
    for md_file in md_files:
        rel = md_file.relative_to(skill_dir).as_posix()
        file_content = md_file.read_text(encoding="utf-8")
        parts.append(f"=== {rel} ===\n{file_content}\n")

    combined = "\n".join(parts)
    canonical = canonicalize_content(combined)
    digest = hashlib.sha256(canonical).hexdigest()
    return f"sha256:{digest}"


def _list_skill_files(skill_dir: Path) -> list[str]:
    """Return sorted relative POSIX paths of all ``.md`` files in *skill_dir*."""
    skill_dir = skill_dir.resolve()
    return sorted(
        p.relative_to(skill_dir).as_posix()
        for p in skill_dir.rglob("*.md")
    )


# ---------------------------------------------------------------------------
# Key helpers
# ---------------------------------------------------------------------------


def _load_private_key(key_path: Path) -> Ed25519PrivateKey:
    """Load an Ed25519 private key from a PEM file.

    Args:
        key_path: Path to a PEM-encoded PKCS8 private key.

    Returns:
        The loaded Ed25519 private key.

    Raises:
        FileNotFoundError: If the key file does not exist.
        ValueError: If the key is not a valid Ed25519 private key.
    """
    if not key_path.is_file():
        raise FileNotFoundError(f"Signing key not found: {key_path}")

    pem_data = key_path.read_bytes()
    # Strip any trailing comments (e.g. pragma lines)
    lines = [
        line for line in pem_data.split(b"\n")
        if not line.startswith(b"#")
    ]
    pem_clean = b"\n".join(lines)

    private_key = serialization.load_pem_private_key(pem_clean, password=None)
    if not isinstance(private_key, Ed25519PrivateKey):
        raise ValueError("Key is not an Ed25519 private key")
    return private_key


def _derive_key_id(private_key: Ed25519PrivateKey) -> str:
    """Derive a stable key ID from the public key bytes.

    Uses the first 16 hex characters of the SHA-256 hash of the raw
    public key bytes, consistent with VCP key ID conventions.

    Args:
        private_key: An Ed25519 private key.

    Returns:
        Key ID string (e.g. ``"a1b2c3d4e5f67890"``).
    """
    pub_bytes = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return hashlib.sha256(pub_bytes).hexdigest()[:16]


def _public_key_b64(private_key: Ed25519PrivateKey) -> str:
    """Return the base64-encoded raw public key."""
    pub_bytes = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return base64.b64encode(pub_bytes).decode("ascii")


# ---------------------------------------------------------------------------
# Signing
# ---------------------------------------------------------------------------


def sign_skill(
    skill_dir: Path,
    key_path: Path,
    issuer: str = "creed.space",
    expires_days: int = 90,
) -> dict[str, Any]:
    """Sign a skill directory and write ``manifest.json``.

    Reads all ``.md`` files, computes a content hash, builds a
    skill-specific VCP manifest, signs it with the provided Ed25519 key,
    and writes the result to ``manifest.json`` inside *skill_dir*.

    Args:
        skill_dir: Root directory of the skill.
        key_path: Path to a PEM-encoded Ed25519 private key.
        issuer: Issuer identifier (default ``"creed.space"``).
        expires_days: Days until the manifest expires (default 90).

    Returns:
        The manifest as a dict (also written to disk).

    Raises:
        FileNotFoundError: If skill dir, SKILL.md, or key file is missing.
    """
    skill_dir = skill_dir.resolve()

    # -- Parse SKILL.md frontmatter for metadata --------------------------
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        raise FileNotFoundError(f"SKILL.md not found in {skill_dir}")

    frontmatter = _parse_frontmatter(skill_md.read_text(encoding="utf-8"))
    skill_name = frontmatter.get("name", skill_dir.name)
    skill_version = str(frontmatter.get("version", "0.1.0"))

    # -- Content hash -----------------------------------------------------
    content_hash = compute_skill_hash(skill_dir)
    files = _list_skill_files(skill_dir)

    # -- Load signing key -------------------------------------------------
    private_key = _load_private_key(key_path)
    key_id = _derive_key_id(private_key)

    # -- Build manifest (without signature value) -------------------------
    now = datetime.now(tz=timezone.utc)
    manifest: dict[str, Any] = {
        "vcp_version": "1.0",
        "type": "skill",
        "skill": {
            "name": skill_name,
            "version": skill_version,
            "content_hash": content_hash,
            "files": files,
        },
        "issuer": {
            "id": issuer,
            "key_id": key_id,
        },
        "timestamps": {
            "iat": now.isoformat(),
            "nbf": now.isoformat(),
            "exp": (now + timedelta(days=expires_days)).isoformat(),
            "jti": str(uuid.uuid4()),
        },
        "signature": {
            "algorithm": "ed25519",
            "value": "",
            "signed_fields": ["vcp_version", "type", "skill", "issuer", "timestamps"],
        },
    }

    # -- Canonicalize and sign --------------------------------------------
    canonical = canonicalize_manifest(manifest)
    raw_sig = private_key.sign(canonical)
    sig_b64 = base64.b64encode(raw_sig).decode("ascii")
    manifest["signature"]["value"] = f"base64:{sig_b64}"

    # -- Write manifest.json to skill directory ---------------------------
    manifest_path = skill_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    return manifest


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------


def verify_skill(
    skill_dir: Path,
    trust_config: TrustConfig | None = None,
) -> tuple[bool, str]:
    """Verify a signed skill directory.

    Checks the content hash and, if a :class:`TrustConfig` is provided,
    verifies the Ed25519 signature and temporal validity.

    Args:
        skill_dir: Root directory of the skill (must contain
            ``manifest.json``).
        trust_config: Optional trust configuration for full cryptographic
            verification.  When ``None``, only structural checks (hash
            match and valid JSON) are performed.

    Returns:
        A ``(valid, reason)`` tuple.  *valid* is ``True`` when all checks
        pass; *reason* is a human-readable explanation.
    """
    skill_dir = skill_dir.resolve()
    manifest_path = skill_dir / "manifest.json"

    # -- Load manifest ----------------------------------------------------
    if not manifest_path.is_file():
        return False, "manifest.json not found in skill directory"

    try:
        manifest: dict[str, Any] = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return False, f"Failed to parse manifest.json: {exc}"

    # -- Structural checks ------------------------------------------------
    for required in ("vcp_version", "type", "skill", "issuer", "timestamps", "signature"):
        if required not in manifest:
            return False, f"Missing required field: {required}"

    if manifest.get("type") != "skill":
        return False, f"Expected type 'skill', got '{manifest.get('type')}'"

    # -- Content hash verification ----------------------------------------
    try:
        computed_hash = compute_skill_hash(skill_dir)
    except FileNotFoundError as exc:
        return False, f"Content hash computation failed: {exc}"

    expected_hash = manifest.get("skill", {}).get("content_hash", "")
    if computed_hash != expected_hash:
        return False, "Content modified after signing"

    # -- Temporal checks --------------------------------------------------
    try:
        nbf = datetime.fromisoformat(manifest["timestamps"]["nbf"])
        exp = datetime.fromisoformat(manifest["timestamps"]["exp"])
    except (KeyError, ValueError) as exc:
        return False, f"Invalid timestamps: {exc}"

    now = datetime.now(tz=timezone.utc)
    # Handle manifests that may have been created without explicit tz info
    if nbf.tzinfo is None:
        nbf = nbf.replace(tzinfo=timezone.utc)
    if exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)

    if now < nbf:
        return False, f"Manifest not yet valid (nbf: {nbf.isoformat()})"
    if now > exp:
        return False, f"Manifest expired (exp: {exp.isoformat()})"

    # -- Signature verification -------------------------------------------
    if trust_config is not None:
        issuer_id = manifest.get("issuer", {}).get("id", "")
        key_id = manifest.get("issuer", {}).get("key_id")

        anchor = trust_config.get_issuer_key(issuer_id, key_id)
        if anchor is None:
            return False, f"Untrusted issuer: {issuer_id} (key_id={key_id})"

        # Decode the anchor's public key
        try:
            pub_bytes = base64.b64decode(anchor.public_key)
            public_key = Ed25519PublicKey.from_public_key_bytes(pub_bytes)
        except Exception as exc:
            return False, f"Failed to load issuer public key: {exc}"

        # Extract signature
        sig_value = manifest.get("signature", {}).get("value", "")
        if not sig_value.startswith("base64:"):
            return False, "Invalid signature format (expected 'base64:' prefix)"

        try:
            sig_bytes = base64.b64decode(sig_value[7:])
        except Exception as exc:
            return False, f"Failed to decode signature: {exc}"

        # Canonicalize manifest (excludes signature) and verify
        canonical = canonicalize_manifest(manifest)
        try:
            public_key.verify(sig_bytes, canonical)
        except Exception:
            return False, "Invalid signature"

    # -- All checks passed ------------------------------------------------
    iat = manifest["timestamps"].get("iat", "unknown")
    issuer_id = manifest.get("issuer", {}).get("id", "unknown")
    return True, f"Verified: {issuer_id}, signed {iat}, expires {exp.isoformat()}"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for skill signing and verification.

    Supports two sub-commands:

    * ``sign`` -- Sign a skill directory with an Ed25519 key.
    * ``verify`` -- Verify a signed skill directory.

    Args:
        argv: Command-line arguments (defaults to ``sys.argv[1:]``).

    Returns:
        Exit code (0 = success, 1 = failure).
    """
    parser = argparse.ArgumentParser(
        prog="vcp.skill_security",
        description="Sign and verify VCP skill directories.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # -- sign -------------------------------------------------------------
    sign_parser = subparsers.add_parser("sign", help="Sign a skill directory")
    sign_parser.add_argument("skill_dir", type=Path, help="Path to skill directory")
    sign_parser.add_argument("--key", type=Path, required=True, help="Path to Ed25519 signing key (PEM)")
    sign_parser.add_argument("--issuer", default="creed.space", help="Issuer identifier (default: creed.space)")
    sign_parser.add_argument("--expires", type=int, default=90, help="Days until expiration (default: 90)")

    # -- verify -----------------------------------------------------------
    verify_parser = subparsers.add_parser("verify", help="Verify a signed skill directory")
    verify_parser.add_argument("skill_dir", type=Path, help="Path to skill directory")
    verify_parser.add_argument("--trust-config", type=Path, default=None, help="Path to trust config JSON")

    args = parser.parse_args(argv)

    if args.command == "sign":
        try:
            manifest = sign_skill(
                skill_dir=args.skill_dir,
                key_path=args.key,
                issuer=args.issuer,
                expires_days=args.expires,
            )
            skill_name = manifest.get("skill", {}).get("name", "unknown")
            issuer_id = manifest.get("issuer", {}).get("id", "unknown")
            exp = manifest.get("timestamps", {}).get("exp", "unknown")
            print(f"Signed: {skill_name} by {issuer_id} (expires {exp})")
            return 0
        except (FileNotFoundError, ValueError, OSError) as exc:
            print(f"FAILED: {exc}", file=sys.stderr)
            return 1

    if args.command == "verify":
        trust_cfg = None
        if args.trust_config:
            try:
                trust_cfg = TrustConfig.from_file(str(args.trust_config))
            except (OSError, json.JSONDecodeError) as exc:
                print(f"FAILED: Could not load trust config: {exc}", file=sys.stderr)
                return 1

        valid, reason = verify_skill(skill_dir=args.skill_dir, trust_config=trust_cfg)
        if valid:
            print(reason)
            return 0
        else:
            print(f"FAILED: {reason}")
            return 1

    return 1


if __name__ == "__main__":
    sys.exit(main())
