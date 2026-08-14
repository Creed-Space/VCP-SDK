#!/usr/bin/env python3
"""Run competence-extension vectors against the claiming Python SDK."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_SRC = ROOT / "python" / "src"
FIXTURE = ROOT / "conformance" / "extensions" / "competence.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if str(PYTHON_SRC) not in sys.path:
        sys.path.insert(0, str(PYTHON_SRC))
    from vcp.extensions.competence import (
        CompetenceClaim,
        CompetenceCriterion,
        CompetenceMeasurementBasis,
        CompetenceProfile,
        apply_decay,
    )

    document = json.loads(FIXTURE.read_text(encoding="utf-8"))
    failures: list[str] = []
    results: list[dict[str, Any]] = []
    for case in document["test_cases"]:
        value = case["input"]
        case_id = case["id"]
        if case_id.startswith("decay-"):
            score = apply_decay(**value)
            actual: dict[str, Any] = {"score": score}
            expected = case["expected"]
            if "score" in expected and score != expected["score"]:
                failures.append(f"{case_id}: score differs")
            if "less_than" in expected and not score < expected["less_than"]:
                failures.append(f"{case_id}: score did not decay")
            if "greater_than" in expected and not score > expected["greater_than"]:
                failures.append(f"{case_id}: score crossed the midpoint")
        elif case_id == "evidence-dampens-decay":
            common = {key: value[key] for key in ("score", "days_elapsed", "decay_rate")}
            low = apply_decay(**common, evidence_count=0)
            high = apply_decay(**common, evidence_count=100)
            actual = {"low_evidence": low, "high_evidence": high}
            if not high > low:
                failures.append(f"{case_id}: evidence did not dampen decay")
        elif case_id == "domain-fallback":
            claim = CompetenceClaim(
                domain="general",
                criterion=CompetenceCriterion(value["criterion"]),
                score=value["general_score"],
                measurement_basis=CompetenceMeasurementBasis.ASSESSED,
            )
            profile = CompetenceProfile(claims=[claim])
            score = profile.score_for(claim.criterion, value["requested_domain"])
            actual = {"score": score}
            if score != case["expected"]["score"]:
                failures.append(f"{case_id}: general-domain fallback differs")
        else:
            claims = [
                CompetenceClaim(
                    domain="general",
                    criterion=CompetenceCriterion(item["criterion"]),
                    score=item["score"],
                    measurement_basis=CompetenceMeasurementBasis.ASSESSED,
                )
                for item in value["claims"]
            ]
            meets = CompetenceProfile(claims=claims).meets_requirements(value["requirements"])
            actual = {"meets": meets}
            if meets != case["expected"]["meets"]:
                failures.append(f"{case_id}: requirements decision differs")
        results.append({"id": case_id, "python": actual})

    report = {
        "schema": "vcp-conformance-report/1",
        "profile": "competence",
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
    print(f"Competence conformance passed: {len(results)} Python cases; Rust unsupported.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
