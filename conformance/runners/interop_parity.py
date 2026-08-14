#!/usr/bin/env python3
"""Check complete-bundle and cross-implementation roundtrip fixtures."""

from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import json
import subprocess
import sys
import tempfile
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
PYTHON_SRC = ROOT / "python" / "src"
RUST_BINARY = ROOT / "rust" / "target" / "debug" / "vcp-cli"
COMPLETE = ROOT / "conformance" / "interop" / "complete_bundle.json"
ROUNDTRIP = ROOT / "conformance" / "interop" / "cross_impl_roundtrip.json"
MANIFEST_SCHEMA = ROOT / "schemas" / "vcp-manifest-v2.schema.json"


def rust_file(
    command: str, value: str | bytes | dict[str, Any], *extra: str
) -> tuple[bool, str]:
    binary = isinstance(value, bytes)
    suffix = ".json" if isinstance(value, dict) else ".bin" if binary else ".txt"
    mode = "wb" if binary else "w"
    kwargs: dict[str, Any] = {} if binary else {"encoding": "utf-8"}
    with tempfile.NamedTemporaryFile(
        mode, suffix=suffix, delete=False, **kwargs
    ) as handle:
        path = Path(handle.name)
        if isinstance(value, dict):
            json.dump(value, handle, ensure_ascii=False)
        else:
            handle.write(value)
    try:
        result = subprocess.run(
            [str(RUST_BINARY), command, str(path), *extra],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=15,
            check=False,
        )
        output = result.stdout.strip() or result.stderr.strip()
        return result.returncode == 0, output
    finally:
        path.unlink(missing_ok=True)


def public_bytes(private_key: Any) -> bytes:
    from cryptography.hazmat.primitives import serialization

    return private_key.public_key().public_bytes(
        serialization.Encoding.Raw,
        serialization.PublicFormat.Raw,
    )


def build_rust() -> None:
    subprocess.run(
        ["cargo", "build", "--quiet", "-p", "vcp-cli"],
        cwd=ROOT / "rust",
        check=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-build", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if not args.skip_build:
        build_rust()
    if str(PYTHON_SRC) not in sys.path:
        sys.path.insert(0, str(PYTHON_SRC))

    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives.asymmetric.ed25519 import (
        Ed25519PrivateKey,
        Ed25519PublicKey,
    )
    from vcp.bundle import canonicalize_safety_attestation
    from vcp.canonicalize import (
        canonicalize_manifest,
        compute_content_hash,
    )
    from vcp.identity import Token
    from vcp.semantics.csm1 import CSM1Code

    failures: list[str] = []
    results: list[dict[str, Any]] = []
    schema = json.loads(MANIFEST_SCHEMA.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)

    complete = json.loads(COMPLETE.read_text(encoding="utf-8"))
    for case in complete["vectors"]:
        case_id = case["id"]
        manifest = case["manifest"]
        content = case["content"]
        errors = sorted(
            validator.iter_errors(manifest), key=lambda item: list(item.path)
        )
        if errors:
            failures.append(f"{case_id}: schema failed: {errors[0].message}")

        py_hash = compute_content_hash(content)
        rs_hash_ok, rs_hash = rust_file("hash", content)
        if (
            not rs_hash_ok
            or py_hash != rs_hash
            or py_hash != manifest["bundle"]["content_hash"]
        ):
            failures.append(f"{case_id}: content hashes differ")

        fixture_keys = case["fixture_keys"]
        issuer = Ed25519PrivateKey.from_private_bytes(
            bytes([fixture_keys["issuer_seed_byte"]]) * 32
        )
        auditor = Ed25519PrivateKey.from_private_bytes(
            bytes([fixture_keys["auditor_seed_byte"]]) * 32
        )
        issuer_public = public_bytes(issuer)
        auditor_public = public_bytes(auditor)
        claimed_issuer = base64.b64decode(
            manifest["issuer"]["public_key"].removeprefix("ed25519:"), validate=True
        )
        if claimed_issuer != issuer_public:
            failures.append(f"{case_id}: issuer fixture key is not bound to manifest")

        signature = manifest["signature"]["value"]
        try:
            Ed25519PublicKey.from_public_bytes(issuer_public).verify(
                base64.b64decode(signature.removeprefix("base64:"), validate=True),
                canonicalize_manifest(manifest),
            )
            py_manifest_signature = True
        except (binascii.Error, InvalidSignature, ValueError):
            py_manifest_signature = False
        rs_manifest_signature, _ = rust_file(
            "verify-manifest-signature", manifest, issuer_public.hex(), signature
        )
        if not py_manifest_signature or not rs_manifest_signature:
            failures.append(
                f"{case_id}: manifest signature did not verify in both implementations"
            )

        attestation_payload = canonicalize_safety_attestation(
            manifest["safety_attestation"], manifest["bundle"]["content_hash"]
        )
        attestation_signature = manifest["safety_attestation"]["signature"]
        try:
            Ed25519PublicKey.from_public_bytes(auditor_public).verify(
                base64.b64decode(
                    attestation_signature.removeprefix("base64:"), validate=True
                ),
                attestation_payload,
            )
            py_attestation = True
        except (binascii.Error, InvalidSignature, ValueError):
            py_attestation = False
        rs_attestation, _ = rust_file(
            "verify-ed25519",
            attestation_payload,
            auditor_public.hex(),
            attestation_signature,
        )
        if not py_attestation or not rs_attestation:
            failures.append(
                f"{case_id}: safety attestation did not verify in both implementations"
            )

        reference = datetime.fromisoformat(
            case["reference_time"].replace("Z", "+00:00")
        )
        timestamps = manifest["timestamps"]
        nbf = datetime.fromisoformat(timestamps["nbf"].replace("Z", "+00:00"))
        exp = datetime.fromisoformat(timestamps["exp"].replace("Z", "+00:00"))
        temporal_valid = nbf <= reference <= exp
        if not temporal_valid:
            failures.append(
                f"{case_id}: reference_time is outside the fixture temporal window"
            )
        results.append(
            {
                "suite": "complete_bundle",
                "id": case_id,
                "python": {
                    "schema": not errors,
                    "content_hash": py_hash == manifest["bundle"]["content_hash"],
                    "manifest_signature": py_manifest_signature,
                    "attestation_signature": py_attestation,
                    "temporal_window": temporal_valid,
                },
                "rust": {
                    "content_hash": rs_hash_ok
                    and rs_hash == manifest["bundle"]["content_hash"],
                    "manifest_signature": rs_manifest_signature,
                    "attestation_signature": rs_attestation,
                },
            }
        )

    roundtrip = json.loads(ROUNDTRIP.read_text(encoding="utf-8"))
    for case in roundtrip["vectors"]:
        case_id = case["id"]
        py: Any
        rs: Any
        if case_id == "xrt-001":
            manifest = deepcopy(case["manifest"])
            content_hash = compute_content_hash(case["content"])
            manifest["bundle"]["content_hash"] = content_hash
            private = Ed25519PrivateKey.from_private_bytes(bytes([73]) * 32)
            public = public_bytes(private)
            manifest["issuer"]["public_key"] = "ed25519:" + base64.b64encode(
                public
            ).decode("ascii")
            manifest["signature"] = {
                "algorithm": "ed25519",
                "value": "",
                "signed_fields": list(manifest),
            }
            py_signature = base64.b64encode(
                private.sign(canonicalize_manifest(manifest))
            ).decode("ascii")
            rs_sign_ok, rs_signature = rust_file("sign-manifest", manifest, "73")
            py_verified_rs = False
            if rs_sign_ok:
                try:
                    Ed25519PublicKey.from_public_bytes(public).verify(
                        base64.b64decode(rs_signature, validate=True),
                        canonicalize_manifest(manifest),
                    )
                    py_verified_rs = True
                except (binascii.Error, InvalidSignature, ValueError):
                    py_verified_rs = False
            rs_verified_py, _ = rust_file(
                "verify-manifest-signature", manifest, public.hex(), py_signature
            )
            py = {
                "content_hash": content_hash,
                "signature": py_signature,
                "verified_rust_signature": py_verified_rs,
            }
            rs = {
                "content_hash": rust_file("hash", case["content"])[1],
                "signature": rs_signature,
                "verified_python_signature": rs_verified_py,
            }
            if (
                not rs_sign_ok
                or py["content_hash"] != rs["content_hash"]
                or py_signature != rs_signature
                or not py_verified_rs
                or not rs_verified_py
            ):
                failures.append(f"{case_id}: sign-and-verify roundtrip differs")
        elif case_id == "xrt-002":
            py = compute_content_hash(case["content"])
            ok, rs = rust_file("hash", case["content"])
            if not ok or py != rs:
                failures.append(f"{case_id}: content hash roundtrip differs")
        elif case_id == "xrt-003":
            py = [Token.parse(raw).full for raw in case["tokens"]]
            rs = []
            for raw in case["tokens"]:
                command = subprocess.run(
                    [str(RUST_BINARY), "canonicalize-token", raw],
                    cwd=ROOT,
                    text=True,
                    capture_output=True,
                    check=False,
                )
                rs.append(command.stdout.strip() if command.returncode == 0 else None)
            if py != rs:
                failures.append(f"{case_id}: identity token roundtrip differs")
        elif case_id == "xrt-004":
            py = []
            rs = []
            for raw in case["codes"]:
                encoded = CSM1Code.parse(raw).encode()
                py.append(encoded.split(":", 1)[0].split("@", 1)[0])
                command = subprocess.run(
                    [str(RUST_BINARY), "parse-csm1", raw],
                    cwd=ROOT,
                    text=True,
                    capture_output=True,
                    check=False,
                )
                rust_encoded = next(
                    (
                        line.partition(":")[2].strip()
                        for line in command.stdout.splitlines()
                        if line.startswith("encoded:")
                    ),
                    "",
                )
                rs.append(rust_encoded.split(":", 1)[0].split("@", 1)[0])
            if py != case["expected"]["canonical_nano_forms"] or rs != py:
                failures.append(f"{case_id}: CSM-1 canonical roundtrip differs")
        else:
            py = canonicalize_manifest(case["manifest"]).decode("utf-8")
            ok, rs = rust_file("canonicalize-manifest", case["manifest"])
            if not ok or py != rs or py != case["expected"]["canonical_json"]:
                failures.append(
                    f"{case_id}: manifest canonicalization roundtrip differs"
                )
        results.append(
            {"suite": "cross_impl_roundtrip", "id": case_id, "python": py, "rust": rs}
        )

    report = {
        "schema": "vcp-conformance-report/1",
        "profile": "interop-parity",
        "implementations": ["python", "rust"],
        "fixture_sha256": {
            path.relative_to(ROOT).as_posix(): hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
            for path in (COMPLETE, ROUNDTRIP, MANIFEST_SCHEMA)
        },
        "summary": {"cases": len(results), "failures": len(failures)},
        "results": results,
        "failures": failures,
        "attestation": "unsigned-local-result",
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    if failures:
        print("\n".join(f"ERROR: {failure}" for failure in failures), file=sys.stderr)
        return 1
    print(
        f"Interoperability parity passed: {len(results)} cases across Python and Rust."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
