#!/usr/bin/env python3
"""Check Python and Rust VCP/I behavior against the shared identity fixtures."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_SRC = ROOT / "python" / "src"
RUST_MANIFEST = ROOT / "rust" / "Cargo.toml"
RUST_BINARY = ROOT / "rust" / "target" / "debug" / "vcp-cli"
PARSING = ROOT / "conformance" / "identity" / "token_parsing.json"
CANONICALIZATION = ROOT / "conformance" / "identity" / "token_canonicalization.json"


def load(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))["vectors"]


def python_token(raw: str) -> dict[str, Any]:
    if str(PYTHON_SRC) not in sys.path:
        sys.path.insert(0, str(PYTHON_SRC))
    from vcp.identity import Token

    try:
        token = Token.parse(raw)
    except Exception as error:
        return {"valid": False, "error": f"{type(error).__name__}: {error}"}
    return {
        "valid": True,
        "domain": token.domain,
        "approach": token.approach,
        "role": token.role,
        "version": token.version,
        "namespace": token.namespace,
        "path": list(token.path),
        "depth": token.depth,
        "canonical_display": token.full,
        "parent_canonical": token.parent().canonical if token.parent() else None,
        "has_parent": token.parent() is not None,
        "uri_with_registry_creed_space": token.to_uri(),
    }


def rust_token(raw: str) -> dict[str, Any]:
    result = subprocess.run(
        [str(RUST_BINARY), "parse-token", raw],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=10,
        check=False,
    )
    if result.returncode:
        return {"valid": False, "error": result.stderr.strip()}
    token, _ = json.JSONDecoder().raw_decode(result.stdout.lstrip())
    segments = token["segments"]
    version_record = token.get("version")
    version = None
    if version_record:
        version = ".".join(str(version_record[key]) for key in ("major", "minor", "patch"))
    full = ".".join(segments)
    if version:
        full += f"@{version}"
    if token.get("namespace"):
        full += f":{token['namespace']}"
    return {
        "valid": True,
        "domain": segments[0],
        "approach": segments[-2],
        "role": segments[-1],
        "version": version,
        "namespace": token.get("namespace"),
        "path": segments[1:-2],
        "depth": len(segments),
        "canonical_display": full,
        "parent_canonical": ".".join(segments[:-1]) if len(segments) > 3 else None,
        "has_parent": len(segments) > 3,
        "uri_with_registry_creed_space": (
            f"creed://creed.space/{'.'.join(segments)}" + (f"@{version}" if version else "")
        ),
    }


def canonicalize_python(raw: str) -> tuple[bool, str]:
    if str(PYTHON_SRC) not in sys.path:
        sys.path.insert(0, str(PYTHON_SRC))
    from vcp.identity import canonicalize_token

    try:
        return True, canonicalize_token(raw)
    except Exception as error:
        return False, f"{type(error).__name__}: {error}"


def canonicalize_rust(raw: str) -> tuple[bool, str]:
    result = subprocess.run(
        [str(RUST_BINARY), "canonicalize-token", raw],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=10,
        check=False,
    )
    return result.returncode == 0, (
        result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
    )


def check_expected(case_id: str, actual: dict[str, Any], expected: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if actual["valid"] != expected.get("valid", True):
        failures.append(f"{case_id}: valid={actual['valid']}, expected={expected.get('valid', True)}")
        return failures
    if not actual["valid"]:
        return failures
    for key in (
        "domain",
        "approach",
        "role",
        "version",
        "namespace",
        "path",
        "depth",
        "canonical_display",
        "parent_canonical",
        "has_parent",
        "uri_with_registry_creed_space",
    ):
        if key in expected and actual.get(key) != expected[key]:
            failures.append(f"{case_id}: {key}={actual.get(key)!r}, expected={expected[key]!r}")
    if "version_major" in expected and actual.get("version"):
        components = [int(part) for part in actual["version"].split(".")]
        for index, key in enumerate(("version_major", "version_minor", "version_patch")):
            if key in expected and components[index] != expected[key]:
                failures.append(f"{case_id}: {key}={components[index]}, expected={expected[key]}")
    return failures


def build_rust() -> None:
    subprocess.run(
        ["cargo", "build", "--quiet", "--manifest-path", str(RUST_MANIFEST), "-p", "vcp-cli"],
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

    failures: list[str] = []
    cases: list[dict[str, Any]] = []
    for vector in load(PARSING):
        case_id = vector["id"]
        expected = vector["expected"]
        if "ancestor" in vector:
            from vcp.identity import Token

            ancestor = Token.parse(vector["ancestor"])
            descendant = Token.parse(vector["descendant"])
            python_values = {
                "is_ancestor": ancestor.is_ancestor_of(descendant),
                "is_descendant": descendant.is_descendant_of(ancestor),
                "reverse_is_ancestor": descendant.is_ancestor_of(ancestor),
            }
            rust_result = subprocess.run(
                [
                    str(RUST_BINARY),
                    "token-hierarchy",
                    vector["ancestor"],
                    vector["descendant"],
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            rust_values = json.loads(rust_result.stdout) if rust_result.returncode == 0 else {}
            for key, value in expected.items():
                if python_values[key] != value:
                    failures.append(f"{case_id}: Python hierarchy {key} mismatch")
                if rust_values.get(key) != value:
                    failures.append(f"{case_id}: Rust hierarchy {key} mismatch")
            cases.append({"id": case_id, "python": python_values, "rust": rust_values})
            continue
        raw = vector["input"]
        py = python_token(raw)
        rs = rust_token(raw)
        if "pattern" in vector and py["valid"] and rs["valid"]:
            from vcp.identity import Token

            py["matches"] = Token.parse(raw).matches_pattern(vector["pattern"])
            command = subprocess.run(
                [str(RUST_BINARY), "match-token", raw, vector["pattern"]],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            rs["matches"] = command.stdout.strip() == "true" if command.returncode == 0 else None
            if py["matches"] != expected["matches"]:
                failures.append(f"{case_id}: Python pattern result mismatch")
            if rs["matches"] != expected["matches"]:
                failures.append(f"{case_id}: Rust pattern result mismatch")
        else:
            failures.extend(f"Python {failure}" for failure in check_expected(case_id, py, expected))
            failures.extend(f"Rust {failure}" for failure in check_expected(case_id, rs, expected))
        if py["valid"] != rs["valid"]:
            failures.append(f"{case_id}: Python and Rust validity differ")
        cases.append({"id": case_id, "python": py, "rust": rs})

    for vector in load(CANONICALIZATION):
        case_id = vector["id"]
        expected = vector["expected"]["canonical"]
        py_ok, py = canonicalize_python(vector["input"])
        rs_ok, rs = canonicalize_rust(vector["input"])
        if not py_ok or py != expected:
            failures.append(f"{case_id}: Python canonical={py!r}, expected={expected!r}")
        if not rs_ok or rs != expected:
            failures.append(f"{case_id}: Rust canonical={rs!r}, expected={expected!r}")
        cases.append({"id": case_id, "python": py, "rust": rs})

    report = {
        "schema": "vcp-conformance-report/1",
        "profile": "identity-parity",
        "implementations": ["python", "rust"],
        "fixture_sha256": {
            path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (PARSING, CANONICALIZATION)
        },
        "cases": cases,
        "summary": {
            "total": len(cases),
            "passed": len(cases) if not failures else len(cases) - len({f.split(':')[0] for f in failures}),
            "failed": len({failure.split(":")[0].split()[-1] for failure in failures}),
        },
        "attestation": "unsigned-local-result",
        "failures": failures,
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    if failures:
        print("\n".join(f"ERROR: {failure}" for failure in failures), file=sys.stderr)
        return 1
    print(f"Identity parity passed: {len(cases)} cases across Python and Rust.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
