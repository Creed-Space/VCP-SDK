#!/usr/bin/env python3
"""Run checked Python and Rust CSM-1 decisions against shared fixtures."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PYTHON_SRC = ROOT / "python" / "src"
RUST_MANIFEST = ROOT / "rust" / "Cargo.toml"
RUST_BINARY = ROOT / "rust" / "target" / "debug" / "vcp-cli"
PARSING = ROOT / "conformance" / "semantics" / "csm1_parsing.json"
ENCODING = ROOT / "conformance" / "semantics" / "csm1_encoding.json"


def python_decision(raw: str) -> tuple[bool, str | None, str | None]:
    if str(PYTHON_SRC) not in sys.path:
        sys.path.insert(0, str(PYTHON_SRC))
    from vcp.semantics.csm1 import CSM1Code

    try:
        code = CSM1Code.parse(raw)
    except ValueError as exc:
        return False, None, f"{type(exc).__name__}: {exc}"
    return True, code.encode(), None


def rust_decision(raw: str) -> tuple[bool, str | None, str | None]:
    result = subprocess.run(
        [str(RUST_BINARY), "parse-csm1", raw],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=10,
        check=False,
    )
    if result.returncode != 0:
        return False, None, result.stderr.strip() or result.stdout.strip()
    encoded = None
    for line in result.stdout.splitlines():
        if line.startswith("encoded:"):
            encoded = line.partition(":")[2].strip()
    if not encoded:
        return True, None, "Rust CLI returned no encoded value"
    return True, encoded, None


def load_vectors(path: Path) -> list[dict[str, object]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["vectors"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-build", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    if not args.skip_build:
        build = subprocess.run(
            [
                "cargo",
                "build",
                "--quiet",
                "--manifest-path",
                str(RUST_MANIFEST),
                "-p",
                "vcp-cli",
            ],
            cwd=ROOT,
            check=False,
        )
        if build.returncode:
            return build.returncode
    if not RUST_BINARY.is_file():
        print(f"ERROR: Rust CLI is missing: {RUST_BINARY}", file=sys.stderr)
        return 1

    failures: list[str] = []
    checked = 0
    for vector in load_vectors(PARSING):
        checked += 1
        case_id = str(vector["id"])
        raw = str(vector["input"])
        expected_valid = bool(vector["expected"]["valid"])
        py_valid, py_encoded, py_error = python_decision(raw)
        rs_valid, rs_encoded, rs_error = rust_decision(raw)
        if py_valid != expected_valid:
            failures.append(
                f"{case_id}: Python valid={py_valid}, expected={expected_valid}: {py_error}"
            )
        if rs_valid != expected_valid:
            failures.append(
                f"{case_id}: Rust valid={rs_valid}, expected={expected_valid}: {rs_error}"
            )
        if py_valid != rs_valid:
            failures.append(f"{case_id}: Python and Rust decisions differ")
        if py_valid and rs_valid and py_encoded != rs_encoded:
            failures.append(
                f"{case_id}: canonical encodings differ: "
                f"Python={py_encoded!r}, Rust={rs_encoded!r}"
            )

    for vector in load_vectors(ENCODING):
        checked += 1
        case_id = str(vector["id"])
        raw = str(vector["input"])
        expected = vector["expected"]
        expected_encoded = expected.get("to_micro", expected.get("to_nano"))
        py_valid, py_encoded, py_error = python_decision(raw)
        rs_valid, rs_encoded, rs_error = rust_decision(raw)
        if not py_valid:
            failures.append(f"{case_id}: Python rejected encoding vector: {py_error}")
        if not rs_valid:
            failures.append(f"{case_id}: Rust rejected encoding vector: {rs_error}")
        if py_encoded != expected_encoded:
            failures.append(
                f"{case_id}: Python encoded {py_encoded!r}, expected {expected_encoded!r}"
            )
        if rs_encoded != expected_encoded:
            failures.append(
                f"{case_id}: Rust encoded {rs_encoded!r}, expected {expected_encoded!r}"
            )
        if py_encoded != rs_encoded:
            failures.append(f"{case_id}: Python and Rust canonical encodings differ")

    report = {
        "schema": "vcp-conformance-report/1",
        "profile": "csm1-parity",
        "implementations": ["python", "rust"],
        "fixture_sha256": {
            path.relative_to(ROOT).as_posix(): hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
            for path in (PARSING, ENCODING)
        },
        "summary": {
            "cases": checked,
            "failures": len(failures),
        },
        "failures": failures,
        "attestation": "unsigned-local-result",
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}", file=sys.stderr)
        print(
            f"CSM-1 parity failed: {len(failures)} issue(s) in {checked} cases.",
            file=sys.stderr,
        )
        return 1
    print(f"CSM-1 parity passed: {checked} cases across Python and Rust.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
