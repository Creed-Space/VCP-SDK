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
import os
import sys
import tempfile
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

MAX_SKILL_MARKDOWN_FILES = 256
MAX_SKILL_FILE_BYTES = 1_048_576
MAX_SKILL_TOTAL_BYTES = 4_194_304
MAX_SKILL_MANIFEST_BYTES = 65_536
SIGNED_SKILL_FIELDS = ("vcp_version", "type", "skill", "issuer", "timestamps")

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


def _skill_markdown_files(skill_dir: Path) -> list[Path]:
    """Return bounded, regular Markdown files without following links."""
    try:
        root = skill_dir.resolve(strict=True)
    except OSError as exc:
        raise FileNotFoundError(f"Skill directory not found: {skill_dir}") from exc
    if not root.is_dir():
        raise FileNotFoundError(f"Skill directory not found: {skill_dir}")

    files: list[Path] = []
    total_bytes = 0
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        directory = Path(dirpath)
        for name in [*dirnames, *filenames]:
            candidate = directory / name
            if candidate.is_symlink():
                raise ValueError(f"Symbolic links are not allowed in signed skills: {candidate}")
        for name in filenames:
            if not name.endswith(".md"):
                continue
            candidate = directory / name
            try:
                resolved = candidate.resolve(strict=True)
                resolved.relative_to(root)
                stat = candidate.stat()
            except (OSError, ValueError) as exc:
                raise ValueError(f"Unsafe skill file path: {candidate}") from exc
            if not candidate.is_file():
                raise ValueError(f"Skill content must be a regular file: {candidate}")
            if stat.st_size > MAX_SKILL_FILE_BYTES:
                raise ValueError(f"Skill file exceeds {MAX_SKILL_FILE_BYTES} bytes: {candidate}")
            total_bytes += stat.st_size
            if total_bytes > MAX_SKILL_TOTAL_BYTES:
                raise ValueError(f"Skill Markdown exceeds {MAX_SKILL_TOTAL_BYTES} total bytes")
            files.append(candidate)
            if len(files) > MAX_SKILL_MARKDOWN_FILES:
                raise ValueError(f"Skill exceeds {MAX_SKILL_MARKDOWN_FILES} Markdown files")

    if not files:
        raise FileNotFoundError(f"No .md files found in {root}")
    return sorted(files, key=lambda path: path.relative_to(root).as_posix())


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
    skill_dir = skill_dir.resolve(strict=True)
    md_files = _skill_markdown_files(skill_dir)

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
    skill_dir = skill_dir.resolve(strict=True)
    return [p.relative_to(skill_dir).as_posix() for p in _skill_markdown_files(skill_dir)]


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
    lines = [line for line in pem_data.split(b"\n") if not line.startswith(b"#")]
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
    if not 1 <= expires_days <= 90:
        raise ValueError("expires_days must be between 1 and 90")
    skill_dir = skill_dir.resolve(strict=True)

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
        "vcp_version": "2.0",
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
            "signed_fields": list(SIGNED_SKILL_FIELDS),
        },
    }

    # -- Canonicalize and sign --------------------------------------------
    canonical = canonicalize_manifest(manifest)
    raw_sig = private_key.sign(canonical)
    sig_b64 = base64.b64encode(raw_sig).decode("ascii")
    manifest["signature"]["value"] = f"base64:{sig_b64}"

    # -- Write manifest.json to skill directory ---------------------------
    manifest_path = skill_dir / "manifest.json"
    if manifest_path.is_symlink():
        raise ValueError("manifest.json must not be a symbolic link")
    payload = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    if len(payload.encode("utf-8")) > MAX_SKILL_MANIFEST_BYTES:
        raise ValueError(f"manifest.json exceeds {MAX_SKILL_MANIFEST_BYTES} bytes")
    fd, temp_name = tempfile.mkstemp(prefix=".manifest-", suffix=".tmp", dir=skill_dir)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temp_name, 0o644)
        os.replace(temp_name, manifest_path)
    finally:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass

    return manifest


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------


def verify_skill(
    skill_dir: Path,
    trust_config: TrustConfig | None = None,
    *,
    allow_structural_only: bool = False,
) -> tuple[bool, str]:
    """Verify a signed skill directory.

    Checks the content hash and, if a :class:`TrustConfig` is provided,
    verifies the Ed25519 signature and temporal validity.

    Args:
        skill_dir: Root directory of the skill (must contain
            ``manifest.json``).
        trust_config: Trust configuration for cryptographic verification.
        allow_structural_only: Explicitly allow hash and structure checks
            without establishing signer trust.

    Returns:
        A ``(valid, reason)`` tuple.  *valid* is ``True`` when all checks
        pass; *reason* is a human-readable explanation.
    """
    try:
        skill_dir = skill_dir.resolve(strict=True)
    except OSError as exc:
        return False, f"Skill directory not found: {exc}"
    manifest_path = skill_dir / "manifest.json"

    # -- Load manifest ----------------------------------------------------
    if manifest_path.is_symlink():
        return False, "manifest.json must not be a symbolic link"
    if not manifest_path.is_file():
        return False, "manifest.json not found in skill directory"
    try:
        if manifest_path.stat().st_size > MAX_SKILL_MANIFEST_BYTES:
            return False, f"manifest.json exceeds {MAX_SKILL_MANIFEST_BYTES} bytes"
    except OSError as exc:
        return False, f"Could not inspect manifest.json: {exc}"

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
        files = _list_skill_files(skill_dir)
        computed_hash = compute_skill_hash(skill_dir)
    except (FileNotFoundError, OSError, ValueError, UnicodeError) as exc:
        return False, f"Content hash computation failed: {exc}"

    skill = manifest.get("skill")
    if not isinstance(skill, dict):
        return False, "Invalid skill object"
    expected_hash = skill.get("content_hash", "")
    if computed_hash != expected_hash:
        return False, "Content modified after signing"
    if skill.get("files") != files:
        return False, "Signed skill file list does not match directory contents"

    # -- Temporal checks --------------------------------------------------
    try:
        nbf = datetime.fromisoformat(manifest["timestamps"]["nbf"])
        exp = datetime.fromisoformat(manifest["timestamps"]["exp"])
    except (KeyError, ValueError) as exc:
        return False, f"Invalid timestamps: {exc}"

    now = datetime.now(tz=timezone.utc)
    if nbf.tzinfo is None or nbf.utcoffset() is None:
        return False, "Invalid timestamps: nbf must include a timezone"
    if exp.tzinfo is None or exp.utcoffset() is None:
        return False, "Invalid timestamps: exp must include a timezone"

    if now < nbf:
        return False, f"Manifest not yet valid (nbf: {nbf.isoformat()})"
    if now > exp:
        return False, f"Manifest expired (exp: {exp.isoformat()})"

    # -- Signature verification -------------------------------------------
    signature = manifest.get("signature")
    if not isinstance(signature, dict):
        return False, "Invalid signature object"
    if signature.get("algorithm") != "ed25519":
        return False, "Invalid signature algorithm (expected ed25519)"
    declared_fields = signature.get("signed_fields")
    expected_fields = set(manifest) - {"signature"}
    if (
        not isinstance(declared_fields, list)
        or any(not isinstance(field, str) for field in declared_fields)
        or len(declared_fields) != len(set(declared_fields))
        or set(declared_fields) != expected_fields
    ):
        return False, "signed_fields must cover every non-signature top-level field exactly once"

    if trust_config is None and not allow_structural_only:
        return False, "Trust configuration is required (or explicitly allow structural-only checks)"

    if trust_config is not None:
        issuer_id = manifest.get("issuer", {}).get("id", "")
        key_id = manifest.get("issuer", {}).get("key_id")

        anchor = trust_config.get_issuer_key(issuer_id, key_id)
        if anchor is None:
            return False, f"Untrusted issuer: {issuer_id} (key_id={key_id})"

        # Decode the anchor's public key
        try:
            if anchor.algorithm.lower() != "ed25519":
                return False, "Trusted issuer key must use ed25519"
            pub_value = anchor.public_key.removeprefix("base64:")
            pub_bytes = base64.b64decode(pub_value, validate=True)
            if len(pub_bytes) != 32:
                return False, "Issuer public key must be 32 bytes"
            public_key = Ed25519PublicKey.from_public_bytes(pub_bytes)
        except Exception as exc:
            return False, f"Failed to load issuer public key: {exc}"

        # Extract signature
        sig_value = signature.get("value", "")
        if not sig_value.startswith("base64:"):
            return False, "Invalid signature format (expected 'base64:' prefix)"

        try:
            sig_bytes = base64.b64decode(sig_value[7:], validate=True)
            if len(sig_bytes) != 64:
                return False, "Ed25519 signature must be 64 bytes"
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
    sign_parser.add_argument(
        "--key",
        type=Path,
        required=True,
        help="Path to Ed25519 signing key (PEM)",
    )
    sign_parser.add_argument(
        "--issuer",
        default="creed.space",
        help="Issuer identifier (default: creed.space)",
    )
    sign_parser.add_argument(
        "--expires",
        type=int,
        default=90,
        help="Days until expiration (default: 90)",
    )

    # -- verify -----------------------------------------------------------
    verify_parser = subparsers.add_parser("verify", help="Verify a signed skill directory")
    verify_parser.add_argument("skill_dir", type=Path, help="Path to skill directory")
    verify_mode = verify_parser.add_mutually_exclusive_group()
    verify_mode.add_argument(
        "--trust-config",
        type=Path,
        default=None,
        help="Path to trust config JSON",
    )
    verify_mode.add_argument(
        "--structural-only",
        action="store_true",
        help="Explicitly skip issuer trust and signature verification",
    )

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

        if trust_cfg is None and not args.structural_only:
            print("FAILED: verification requires --trust-config or --structural-only")
            return 1
        valid, reason = verify_skill(
            skill_dir=args.skill_dir,
            trust_config=trust_cfg,
            allow_structural_only=args.structural_only,
        )
        if valid:
            print(reason)
            return 0
        else:
            print(f"FAILED: {reason}")
            return 1

    return 1


if __name__ == "__main__":
    sys.exit(main())
