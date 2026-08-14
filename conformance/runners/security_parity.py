#!/usr/bin/env python3
"""Run shared revocation vectors and fail-closed scope policy checks."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = (
    ROOT / "conformance" / "security" / "revocation-responses.json",
    ROOT / "conformance" / "security" / "revocation-crl-responses.json",
)


def run(
    label: str, command: list[str], cwd: Path = ROOT
) -> tuple[dict[str, object], str | None]:
    result = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        capture_output=True,
        timeout=180,
        check=False,
    )
    combined = result.stdout + result.stderr
    record: dict[str, object] = {
        "label": label,
        "command": command,
        "exit_code": result.returncode,
        "output_sha256": hashlib.sha256(combined.encode()).hexdigest(),
    }
    failure = None if result.returncode == 0 else f"{label} failed:\n{combined[-4000:]}"
    return record, failure


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    python = sys.executable
    commands = (
        (
            "python-shared-revocation-vectors",
            [
                python,
                "-m",
                "pytest",
                "-q",
                "python/tests/vcp/test_revocation.py::TestOnlineCheck::test_shared_online_response_contract_matches_python_parser",
                "python/tests/vcp/test_revocation.py::TestCRLCheck::test_shared_crl_response_contract_matches_python_parser",
            ],
            ROOT,
        ),
        (
            "python-fail-closed-policy",
            [
                python,
                "-m",
                "pytest",
                "-q",
                "python/tests/vcp/test_orchestrator_security.py::test_audience_scope_fails_closed_without_runtime_audience",
                "python/tests/vcp/test_orchestrator_security.py::test_region_scope_fails_closed_without_runtime_region",
                "python/tests/vcp/test_orchestrator_security.py::test_unexpected_revocation_error_is_fail_closed",
                "python/tests/vcp/test_revocation.py::TestRevocationStatus::test_unavailable_is_distinct_and_fail_closed",
            ],
            ROOT,
        ),
        (
            "rust-shared-revocation-vectors",
            ["cargo", "test", "-q", "-p", "vcp-core", "shared_"],
            ROOT / "rust",
        ),
        (
            "rust-scope-policy",
            [
                "cargo",
                "test",
                "-q",
                "-p",
                "vcp-core",
                "scope_mismatch_wrong_environment",
            ],
            ROOT / "rust",
        ),
        (
            "rust-audience-region-policy",
            [
                "cargo",
                "test",
                "-q",
                "-p",
                "vcp-core",
                "audience_and_region_scopes_require_explicit_runtime_context",
            ],
            ROOT / "rust",
        ),
        (
            "rust-unavailable-revocation-policy",
            [
                "cargo",
                "test",
                "-q",
                "-p",
                "vcp-core",
                "configured_unavailable_revocation_source_fails_closed",
            ],
            ROOT / "rust",
        ),
    )
    records: list[dict[str, object]] = []
    failures: list[str] = []
    for label, command, cwd in commands:
        record, failure = run(label, command, cwd)
        records.append(record)
        if failure:
            failures.append(failure)
    fixture_cases = sum(
        len(json.loads(path.read_text(encoding="utf-8"))["vectors"])
        for path in FIXTURES
    )
    report = {
        "schema": "vcp-conformance-report/1",
        "profile": "revocation-and-scope-policy",
        "implementations": ["python", "rust"],
        "fixture_sha256": {
            path.relative_to(ROOT).as_posix(): hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
            for path in FIXTURES
        },
        "summary": {
            "fixture_cases": fixture_cases,
            "policy_checks": len(commands) - 2,
            "failures": len(failures),
        },
        "commands": records,
        "failures": failures,
        "attestation": "unsigned-local-result",
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print(
        f"Security parity passed: {fixture_cases} revocation vectors and fail-closed "
        "scope, audience, region, and unavailable-source checks."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
