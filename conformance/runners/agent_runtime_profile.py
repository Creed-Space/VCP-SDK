"""Candidate runner for VCP Agent Runtime Profile contract fixtures."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "schemas" / "vcp-agent-runtime-profile-v0.1.schema.json"
FIXTURES = tuple(
    sorted((ROOT / "conformance" / "agent-runtime").glob("*_contracts.json"))
)


def load_object(path: Path) -> dict[str, Any]:
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return loaded


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    schema = load_object(SCHEMA)
    fixtures = [load_object(path) for path in FIXTURES]
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    failures: list[str] = []
    cases: list[dict[str, Any]] = []
    for fixture in fixtures:
        fixture_cases = fixture.get("test_cases")
        if not isinstance(fixture_cases, list):
            raise TypeError("fixture cases must be an array")
        cases.extend(fixture_cases)
    for case in cases:
        if not isinstance(case, dict):
            failures.append("non-object case")
            continue
        errors = list(validator.iter_errors(case.get("document")))
        actual_valid = not errors
        if actual_valid != case.get("expected_valid"):
            failures.append(str(case.get("id", "unnamed")))
    report = {
        "schema": "vcp-conformance-report/1",
        "profile": "agent-runtime-profile-0.1.0",
        "implementations": {"python": "passed" if not failures else "failed"},
        "fixture_sha256": {
            **{
                path.relative_to(ROOT).as_posix(): hashlib.sha256(
                    path.read_bytes()
                ).hexdigest()
                for path in FIXTURES
            },
            SCHEMA.relative_to(ROOT).as_posix(): hashlib.sha256(
                SCHEMA.read_bytes()
            ).hexdigest(),
        },
        "summary": {"cases": len(cases), "failures": len(failures)},
        "failures": failures,
        "attestation": "unsigned-local-result",
    }
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if failures:
        print(f"Agent Runtime Profile fixture failures: {failures}", file=sys.stderr)
        return 1
    print(f"Agent Runtime Profile candidate: {len(cases)} contract cases passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
