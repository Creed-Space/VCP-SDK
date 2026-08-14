#!/usr/bin/env python3
"""Run the VCP/A operational state-machine profile against Python."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_SRC = ROOT / "python" / "src"
FIXTURE = ROOT / "conformance" / "adaptation" / "state_machine.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if str(PYTHON_SRC) not in sys.path:
        sys.path.insert(0, str(PYTHON_SRC))
    from vcp.adaptation.state_machine import VCPStateMachine

    document = json.loads(FIXTURE.read_text(encoding="utf-8"))
    machine = VCPStateMachine()
    failures: list[str] = []
    results: list[dict[str, Any]] = []
    for case in document["vectors"]:
        actual = machine.evaluate(
            case["initial_state"], case["input"], case.get("preconditions")
        )
        checked_expected = {
            key: value for key, value in case["expected"].items() if key != "note"
        }
        for key, value in checked_expected.items():
            if actual.get(key) != value:
                failures.append(
                    f"{case['id']}: {key}={actual.get(key)!r}, expected={value!r}"
                )
        results.append({"id": case["id"], "python": actual})
    report = {
        "schema": "vcp-conformance-report/1",
        "profile": "adaptation-operational-state-machine",
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
    print(f"State-machine conformance passed: {len(results)} Python cases; Rust unsupported.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
