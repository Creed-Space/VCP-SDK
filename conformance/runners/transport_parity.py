#!/usr/bin/env python3
"""Check Python and Rust transport primitives against shared fixtures."""

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

ROOT = Path(__file__).resolve().parents[2]
PYTHON_SRC = ROOT / "python" / "src"
RUST_BINARY = ROOT / "rust" / "target" / "debug" / "vcp-cli"
FIXTURE_DIR = ROOT / "conformance" / "transport"
FIXTURES = {
    name: FIXTURE_DIR / f"{name}.json"
    for name in (
        "content_canonicalization",
        "content_hashing",
        "manifest_canonicalization",
        "signature_verification",
        "bundle_verification",
    )
}


def ensure_python() -> None:
    if str(PYTHON_SRC) not in sys.path:
        sys.path.insert(0, str(PYTHON_SRC))


def load(name: str) -> list[dict[str, Any]]:
    return json.loads(FIXTURES[name].read_text(encoding="utf-8"))["vectors"]


def rust(command: str, value: Any, *extra: str) -> tuple[bool, str]:
    suffix = ".json" if isinstance(value, (dict, list)) else ".txt"
    with tempfile.NamedTemporaryFile(
        "w", suffix=suffix, encoding="utf-8", delete=False
    ) as handle:
        path = Path(handle.name)
        if isinstance(value, (dict, list)):
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
        output = (
            result.stdout.strip() if result.stdout.strip() else result.stderr.strip()
        )
        return result.returncode == 0, output
    finally:
        path.unlink(missing_ok=True)


def python_signature(manifest: dict[str, Any], seed_byte: int) -> tuple[str, bytes]:
    ensure_python()
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from vcp.canonicalize import canonicalize_manifest

    key = Ed25519PrivateKey.from_private_bytes(bytes([seed_byte]) * 32)
    signature = base64.b64encode(key.sign(canonicalize_manifest(manifest))).decode(
        "ascii"
    )
    public = key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return signature, public


def python_verify(manifest: dict[str, Any], public_key: bytes, signature: str) -> bool:
    ensure_python()
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    from vcp.canonicalize import canonicalize_manifest

    raw = signature.removeprefix("base64:")
    try:
        decoded = base64.b64decode(raw, validate=True)
        Ed25519PublicKey.from_public_bytes(public_key).verify(
            decoded, canonicalize_manifest(manifest)
        )
    except (binascii.Error, InvalidSignature, ValueError):
        return False
    return True


def build_rust() -> None:
    subprocess.run(
        [
            "cargo",
            "build",
            "--quiet",
            "--manifest-path",
            str(ROOT / "rust" / "Cargo.toml"),
            "-p",
            "vcp-cli",
        ],
        cwd=ROOT,
        check=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-build", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if not args.skip_build:
        build_rust()
    ensure_python()
    from vcp.canonicalize import (
        canonicalize_content,
        canonicalize_manifest,
        compute_content_hash,
        verify_content_hash,
    )
    from vcp.orchestrator import Orchestrator, classify_temporal_claims
    from vcp.trust import TrustConfig
    from vcp.types import VerificationResult

    failures: list[str] = []
    results: list[dict[str, Any]] = []

    for vector in load("content_canonicalization"):
        expected = vector["expected"]
        raw = vector["input"]
        try:
            py = canonicalize_content(raw).decode("utf-8")
            py_valid = True
        except ValueError as error:
            py, py_valid = str(error), False
        rs_valid, rs_raw = rust("canonicalize-content", raw)
        rs = json.loads(rs_raw) if rs_valid else rs_raw
        expected_valid = expected["valid"]
        if py_valid != expected_valid or rs_valid != expected_valid:
            failures.append(f"{vector['id']}: canonicalization validity mismatch")
        if expected_valid and (
            py != expected["canonical"] or rs != expected["canonical"]
        ):
            failures.append(f"{vector['id']}: canonical bytes mismatch")
        if py_valid != rs_valid or (py_valid and py != rs):
            failures.append(f"{vector['id']}: Python and Rust canonicalization differ")
        results.append({"id": vector["id"], "python": py_valid, "rust": rs_valid})

    for vector in load("content_hashing"):
        expected = vector["expected"]
        values = [
            vector[key] for key in ("input", "input_a", "input_b") if key in vector
        ]
        py_hashes: list[str] = []
        rs_hashes: list[str] = []
        for value in values:
            try:
                py_hashes.append(compute_content_hash(value))
            except ValueError as error:
                py_hashes.append(f"ERROR:{error}")
            ok, output = rust("hash", value)
            rs_hashes.append(output if ok else f"ERROR:{output}")
        if py_hashes != rs_hashes:
            failures.append(f"{vector['id']}: Python and Rust hashes differ")
        if "hash" in expected and py_hashes[0] != expected["hash"]:
            failures.append(f"{vector['id']}: hash does not match fixture")
        if "hashes_equal" in expected:
            equal = len(py_hashes) == 2 and py_hashes[0] == py_hashes[1]
            if equal != expected["hashes_equal"]:
                failures.append(f"{vector['id']}: equality decision mismatch")
        if "verification_result" in expected:
            claimed = vector.get("claimed_hash", py_hashes[0])
            verified = verify_content_hash(vector["input"], claimed)
            if verified != expected["verification_result"]:
                failures.append(f"{vector['id']}: verification decision mismatch")
        if "hash_prefix" in expected and not py_hashes[0].startswith(
            expected["hash_prefix"]
        ):
            failures.append(f"{vector['id']}: hash prefix mismatch")
        if (
            "hash_hex_length" in expected
            and len(py_hashes[0].removeprefix("sha256:")) != expected["hash_hex_length"]
        ):
            failures.append(f"{vector['id']}: digest length mismatch")
        results.append({"id": vector["id"], "python": py_hashes, "rust": rs_hashes})

    for vector in load("manifest_canonicalization"):
        expected = vector["expected"]["canonical_json"]
        py = canonicalize_manifest(vector["input"]).decode("utf-8")
        rs_ok, rs = rust("canonicalize-manifest", vector["input"])
        if not rs_ok or py != expected or rs != expected or py != rs:
            failures.append(f"{vector['id']}: manifest canonicalization mismatch")
        results.append({"id": vector["id"], "python": py, "rust": rs})

    for vector in load("signature_verification"):
        case_id = vector["id"]
        procedure = vector["procedure"]
        passed = True
        if procedure == "sign_with_short_key":
            try:
                from cryptography.hazmat.primitives.asymmetric.ed25519 import (
                    Ed25519PrivateKey,
                )

                Ed25519PrivateKey.from_private_bytes(bytes(vector["key_bytes"]))
                passed = False
            except ValueError:
                passed = True
            # The corresponding Rust core negative unit is part of the focused command below.
        elif procedure == "verify_with_short_key":
            passed = not python_verify(
                vector["manifest"], bytes(vector["key_bytes"]), vector["signature"]
            )
        elif procedure == "verify_with_invalid_base64":
            _, public = python_signature(vector["manifest"], vector["seed_byte"])
            passed = not python_verify(vector["manifest"], public, vector["signature"])
            rs_ok, _ = rust(
                "verify-manifest-signature",
                vector["manifest"],
                public.hex(),
                vector["signature"],
            )
            passed = passed and not rs_ok
        else:
            seed = vector.get("seed_byte", vector.get("sign_seed_byte"))
            signing_manifest = vector.get(
                "manifest",
                vector.get("original_manifest", vector.get("manifest_for_signing")),
            )
            verify_manifest = vector.get(
                "tampered_manifest",
                vector.get("manifest_for_verification", signing_manifest),
            )
            py_sig, public = python_signature(signing_manifest, seed)
            rs_ok, rs_sig = rust("sign-manifest", signing_manifest, str(seed))
            passed = rs_ok and rs_sig == py_sig
            verify_public = public
            if procedure == "sign_with_seed_verify_with_different_seed":
                _, verify_public = python_signature(
                    signing_manifest, vector["verify_seed_byte"]
                )
            expected_verify = not (
                procedure
                in {
                    "sign_with_seed_verify_with_different_seed",
                    "sign_original_verify_tampered",
                }
            )
            py_verified = python_verify(verify_manifest, verify_public, py_sig)
            rs_verified, _ = rust(
                "verify-manifest-signature",
                verify_manifest,
                verify_public.hex(),
                py_sig,
            )
            passed = (
                passed
                and py_verified == expected_verify
                and rs_verified == expected_verify
            )
            if procedure == "sign_and_verify_with_base64_prefix":
                py_prefixed = python_verify(
                    verify_manifest, verify_public, f"base64:{py_sig}"
                )
                rs_prefixed, _ = rust(
                    "verify-manifest-signature",
                    verify_manifest,
                    verify_public.hex(),
                    f"base64:{py_sig}",
                )
                passed = passed and py_prefixed and rs_prefixed
            if procedure == "sign_twice_compare":
                second_py, _ = python_signature(signing_manifest, seed)
                second_rs_ok, second_rs = rust(
                    "sign-manifest", signing_manifest, str(seed)
                )
                passed = (
                    passed
                    and second_py == py_sig
                    and second_rs_ok
                    and second_rs == rs_sig
                )
        if not passed:
            failures.append(f"{case_id}: signature procedure failed")
        results.append({"id": case_id, "python": passed, "rust": passed})

    rust_negative = subprocess.run(
        [
            "cargo",
            "test",
            "--quiet",
            "--manifest-path",
            str(ROOT / "rust" / "Cargo.toml"),
            "-p",
            "vcp-core",
            "transport::tests::sign_rejects_wrong_key_length",
        ],
        cwd=ROOT,
        check=False,
    )
    if rust_negative.returncode:
        failures.append("sig-err-001: Rust short signing key was not rejected")

    for vector in load("bundle_verification")[:3]:
        case_id = vector["id"]
        if case_id == "bv-001":
            content = vector["content"]
            expected_hash = compute_content_hash(content)
            manifest = deepcopy(vector["manifest_template"])
            manifest["bundle"]["content_hash"] = expected_hash
            expected_valid = True
        elif case_id == "bv-002":
            content = vector["tampered_content"]
            expected_hash = compute_content_hash(vector["original_content"])
            manifest = {"bundle": {"id": "tampered", "content_hash": expected_hash}}
            expected_valid = False
        else:
            content = vector["content"]
            manifest = vector["manifest"]
            expected_hash = manifest["bundle"]["content_hash"]
            expected_valid = True
        py_valid = verify_content_hash(content, expected_hash)
        # Invoke the CLI with two files because `verify` takes a manifest and content path.
        with tempfile.TemporaryDirectory() as directory:
            manifest_path = Path(directory) / "manifest.json"
            content_path = Path(directory) / "content.md"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            content_path.write_text(content, encoding="utf-8")
            command = subprocess.run(
                [str(RUST_BINARY), "verify", str(manifest_path), str(content_path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            rust_valid = command.returncode == 0
        if py_valid != expected_valid or rust_valid != expected_valid:
            failures.append(f"{case_id}: bundle content decision mismatch")
        results.append({"id": case_id, "python": py_valid, "rust": rust_valid})

    for vector in load("bundle_verification")[3:]:
        case_id = vector["id"]
        if case_id in {"bv-004", "bv-005"}:
            timestamps = vector["manifest"]["timestamps"]
            parse = lambda value: datetime.fromisoformat(value.replace("Z", "+00:00"))
            py_result = classify_temporal_claims(
                parse(timestamps["iat"]),
                parse(timestamps["nbf"]),
                parse(timestamps["exp"]),
                parse(vector["reference_time"]),
            )
            expected_name = vector["expected"]["temporal_validity"]
            expected_result = getattr(VerificationResult, expected_name)
            rs_ok, rs_raw = rust(
                "classify-temporal",
                {
                    "timestamps": timestamps,
                    "reference_time": vector["reference_time"],
                    "max_exp_days": 90,
                },
            )
            rs_result = json.loads(rs_raw) if rs_ok else None
            if (
                py_result is not expected_result
                or rs_result != expected_result.name.lower()
            ):
                failures.append(f"{case_id}: temporal classification mismatch")
            results.append(
                {
                    "id": case_id,
                    "python": py_result.name.lower(),
                    "rust": rs_result,
                }
            )
        elif case_id == "bv-006":
            content = "x" * 262_145
            py_allowed = len(content.encode("utf-8")) <= Orchestrator.MAX_CONTENT_SIZE
            rs_ok, rs_raw = rust("content-policy", content)
            rs_policy = json.loads(rs_raw) if rs_ok else {}
            if py_allowed or rs_policy.get("size_allowed") is not False:
                failures.append(f"{case_id}: oversized content was not rejected")
            results.append(
                {
                    "id": case_id,
                    "python": {"size_allowed": py_allowed},
                    "rust": rs_policy,
                }
            )
        elif case_id == "bv-007":
            py_findings = Orchestrator(TrustConfig()).scan_for_injection(
                vector["content"]
            )
            rs_ok, rs_raw = rust("content-policy", vector["content"])
            rs_policy = json.loads(rs_raw) if rs_ok else {}
            if not py_findings or not rs_policy.get("injection_findings"):
                failures.append(f"{case_id}: injection content was not detected")
            results.append(
                {
                    "id": case_id,
                    "python": {"injection_findings": py_findings},
                    "rust": rs_policy,
                }
            )
        else:
            try:
                canonicalize_content(vector["content"])
                py_valid = True
            except ValueError:
                py_valid = False
            rs_ok, rs_raw = rust("content-policy", vector["content"])
            rs_policy = json.loads(rs_raw) if rs_ok else {}
            if py_valid or rs_policy.get("canonical_valid") is not False:
                failures.append(f"{case_id}: forbidden Unicode was not rejected")
            results.append(
                {
                    "id": case_id,
                    "python": {"canonical_valid": py_valid},
                    "rust": rs_policy,
                }
            )

    report = {
        "schema": "vcp-conformance-report/1",
        "profile": "transport-parity",
        "implementations": ["python", "rust"],
        "fixture_sha256": {
            path.relative_to(ROOT).as_posix(): hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
            for path in FIXTURES.values()
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
        f"Transport parity passed: {len(results)} checked cases across Python and Rust."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
