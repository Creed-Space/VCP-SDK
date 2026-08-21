#!/usr/bin/env python3
"""Run canonical capability negotiation vectors against every SDK runtime."""

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
WEBMCP_RUNNER = ROOT / "webmcp" / "scripts" / "run-negotiation.mjs"
FIXTURE = ROOT / "conformance" / "extensions" / "capability_negotiation.json"


def capture(call: Any, value: dict[str, Any]) -> dict[str, Any]:
    """Capture an expected validation rejection without comparing error prose."""
    try:
        return {"rejected": False, "value": call(value)}
    except (KeyError, RuntimeError, TypeError, ValueError) as error:
        return {
            "rejected": True,
            "error_type": type(error).__name__,
            "error": str(error)[:500],
        }


def python_result(value: dict[str, Any]) -> dict[str, Any]:
    if str(PYTHON_SRC) not in sys.path:
        sys.path.insert(0, str(PYTHON_SRC))
    from vcp.negotiation import negotiate_handshake

    client = value["client_hello"]
    server = value["server_capabilities"]
    return negotiate_handshake(client, server)


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


def webmcp_result(value: dict[str, Any]) -> dict[str, Any]:
    with tempfile.NamedTemporaryFile(
        "w", suffix=".json", encoding="utf-8", delete=False
    ) as handle:
        path = Path(handle.name)
        json.dump(value, handle)
    try:
        result = subprocess.run(
            ["node", str(WEBMCP_RUNNER), str(path)],
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
    subprocess.run(
        ["npm", "run", "build", "--silent"],
        cwd=ROOT / "webmcp",
        check=True,
        timeout=120,
    )
    document = json.loads(FIXTURE.read_text(encoding="utf-8"))
    failures: list[str] = []
    results: list[dict[str, Any]] = []
    for case in document["test_cases"]:
        expected_rejection = case["expected"].get("rejected") is True
        py_capture = capture(python_result, case["input"])
        rs_capture = capture(rust_result, case["input"])
        web_capture = capture(webmcp_result, case["input"])
        if expected_rejection:
            for implementation, captured in (
                ("Python", py_capture),
                ("Rust", rs_capture),
                ("WebMCP", web_capture),
            ):
                if not captured["rejected"]:
                    failures.append(
                        f"{case['id']}: {implementation} accepted an invalid handshake"
                    )
            results.append(
                {
                    "id": case["id"],
                    "python": py_capture,
                    "rust": rs_capture,
                    "webmcp": web_capture,
                }
            )
            continue

        expected = case["expected"]["server_ack"]
        if py_capture["rejected"]:
            failures.append(f"{case['id']}: Python unexpectedly rejected input")
        if rs_capture["rejected"]:
            failures.append(f"{case['id']}: Rust unexpectedly rejected input")
        if web_capture["rejected"]:
            failures.append(f"{case['id']}: WebMCP unexpectedly rejected input")
        py = py_capture.get("value")
        rs = rs_capture.get("value")
        web = web_capture.get("value")
        if py != expected:
            failures.append(f"{case['id']}: Python result differs from expected")
        if rs != expected:
            failures.append(f"{case['id']}: Rust result differs from expected")
        if py != rs:
            failures.append(f"{case['id']}: Python and Rust differ")
        if web != expected:
            failures.append(f"{case['id']}: WebMCP result differs from expected")
        if web != py or web != rs:
            failures.append(f"{case['id']}: WebMCP and native SDKs differ")
        results.append({"id": case["id"], "python": py, "rust": rs, "webmcp": web})
    report = {
        "schema": "vcp-conformance-report/1",
        "profile": "versioned-capability-negotiation",
        "implementations": ["python", "rust", "webmcp"],
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
    print(
        f"Negotiation parity passed: {len(results)} cases across Python, Rust, and WebMCP."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
