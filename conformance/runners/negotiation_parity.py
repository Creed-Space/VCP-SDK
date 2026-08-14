#!/usr/bin/env python3
"""Run versioned capability negotiation vectors against Python and Rust."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_SRC = ROOT / "python" / "src"
RUST_BINARY = ROOT / "rust" / "target" / "debug" / "vcp-cli"
FIXTURE = ROOT / "conformance" / "extensions" / "capability_negotiation.json"


def python_result(value: dict[str, Any]) -> dict[str, Any]:
    if str(PYTHON_SRC) not in sys.path:
        sys.path.insert(0, str(PYTHON_SRC))
    from vcp.negotiation import negotiate_versioned

    client = value["client_hello"]
    server = value["server_capabilities"]
    return negotiate_versioned(
        client["vcp_version"],
        client.get("extensions", []),
        server["vcp_version"],
        server.get("extensions", []),
    )


def rust_result(value: dict[str, Any]) -> dict[str, Any]:
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8", delete=False) as handle:
        path = Path(handle.name)
        json.dump(value, handle)
    try:
        result = subprocess.run(
            [str(RUST_BINARY), "negotiate-extensions", str(path)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=10,
            check=False,
        )
    finally:
        path.unlink(missing_ok=True)
    if result.returncode:
        raise RuntimeError(result.stderr.strip())
    return json.loads(result.stdout)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-build", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if not args.skip_build:
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
    document = json.loads(FIXTURE.read_text(encoding="utf-8"))
    failures: list[str] = []
    results: list[dict[str, Any]] = []
    for case in document["test_cases"]:
        expected = case["expected"]["server_ack"]
        py = python_result(case["input"])
        rs = rust_result(case["input"])
        if py != expected:
            failures.append(f"{case['id']}: Python result differs from expected")
        if rs != expected:
            failures.append(f"{case['id']}: Rust result differs from expected")
        if py != rs:
            failures.append(f"{case['id']}: Python and Rust differ")
        results.append({"id": case["id"], "python": py, "rust": rs})
    report = {
        "schema": "vcp-conformance-report/1",
        "profile": "versioned-capability-negotiation",
        "implementations": ["python", "rust"],
        "fixture_sha256": hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
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
    print(f"Negotiation parity passed: {len(results)} cases across Python and Rust.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
