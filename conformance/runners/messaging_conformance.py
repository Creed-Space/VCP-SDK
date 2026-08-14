#!/usr/bin/env python3
"""Run the selected VCP Inter-Agent Messaging v2.0 envelope suite."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_SRC = ROOT / "python" / "src"
FIXTURE = ROOT / "conformance" / "adaptation" / "messaging.json"


def classify_error(error: str) -> str:
    """Map human-readable validator output to stable conformance metadata."""
    mappings = (
        ("vcp_message must be", "invalid_version"),
        ("type must be one of", "invalid_type"),
        ("message_id", "invalid_message_id"),
        ("sender is required", "missing_sender"),
        ("recipient is required", "missing_recipient"),
        ("timestamp", "invalid_timestamp"),
        ("payload must be", "invalid_payload"),
        ("severity must be", "invalid_severity"),
        ("requires_ack", "ack_required"),
    )
    for fragment, code in mappings:
        if fragment in error:
            return code
    return "validation_error"


def run_case(data: dict[str, Any]) -> dict[str, Any]:
    if str(PYTHON_SRC) not in sys.path:
        sys.path.insert(0, str(PYTHON_SRC))
    from vcp.messaging import message_from_dict, message_to_dict, validate_message

    try:
        message = message_from_dict(data)
    except KeyError as error:
        field = str(error.args[0])
        return {"valid": False, "error_codes": [f"missing_{field}"]}
    errors = validate_message(message)
    serialized = message_to_dict(message)
    roundtrip = message_to_dict(message_from_dict(serialized)) == serialized
    return {
        "valid": not errors,
        "error_codes": sorted({classify_error(error) for error in errors}),
        "roundtrip": roundtrip,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    document = json.loads(FIXTURE.read_text(encoding="utf-8"))
    failures: list[str] = []
    results: list[dict[str, Any]] = []
    for case in document["test_cases"]:
        actual = run_case(case["input"])
        expected = case["expected"]
        if actual["valid"] != expected["valid"]:
            failures.append(
                f"{case['id']}: valid={actual['valid']!r}, expected={expected['valid']!r}"
            )
        if actual["error_codes"] != sorted(expected.get("error_codes", [])):
            failures.append(
                f"{case['id']}: errors={actual['error_codes']!r}, "
                f"expected={expected.get('error_codes', [])!r}"
            )
        if not actual.get("roundtrip", True):
            failures.append(f"{case['id']}: serialization roundtrip failed")
        results.append({"id": case["id"], "python": actual})

    report = {
        "schema": "vcp-conformance-report/1",
        "profile": "messaging-2.0",
        "implementations": {"python": "passed" if not failures else "failed", "rust": "unsupported"},
        "fixture_sha256": hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
        "summary": {"cases": len(results), "failures": len(failures), "unsupported": 1},
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
    print(f"Messaging conformance passed: {len(results)} Python cases; Rust unsupported.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
