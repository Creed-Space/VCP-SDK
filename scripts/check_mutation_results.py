#!/usr/bin/env python3
"""Summarize mutmut metadata and enforce a bounded mutation-quality policy."""

from __future__ import annotations

import argparse
import fnmatch
import json
from collections import Counter
from pathlib import Path
from typing import Any


def _status(exit_code: int | None) -> str:
    if exit_code in {1, 3}:
        return "killed"
    if exit_code == 0:
        return "survived"
    if exit_code in {5, 33}:
        return "no_tests"
    if exit_code == 34:
        return "skipped"
    if exit_code == 35:
        return "suspicious"
    if exit_code in {-24, 24, 36, 152, 255}:
        return "timeout"
    if exit_code == 37:
        return "caught_by_type_check"
    if exit_code in {-11, -9}:
        return "segfault"
    if exit_code == 2:
        return "interrupted"
    if exit_code is None:
        return "not_checked"
    return "suspicious"


def load_results(mutants_dir: Path, pattern: str) -> dict[str, int | None]:
    selected: dict[str, int | None] = {}
    for meta_path in sorted(mutants_dir.rglob("*.meta")):
        data: dict[str, Any] = json.loads(meta_path.read_text(encoding="utf-8"))
        for name, exit_code in data.get("exit_code_by_key", {}).items():
            if fnmatch.fnmatch(name, pattern):
                selected[name] = exit_code
    return selected


def evaluate(
    selected: dict[str, int | None], minimum_score: float
) -> tuple[dict[str, Any], list[str]]:
    by_status = {name: _status(code) for name, code in selected.items()}
    counts = Counter(by_status.values())
    effective_killed = counts["killed"] + counts["caught_by_type_check"]
    score_denominator = effective_killed + counts["survived"]
    score = (
        100.0
        if score_denominator == 0
        else effective_killed * 100.0 / score_denominator
    )

    failures: list[str] = []
    if not selected:
        failures.append("no mutants matched the requested pattern")
    infrastructure_statuses = (
        "not_checked",
        "no_tests",
        "timeout",
        "suspicious",
        "interrupted",
        "segfault",
    )
    for status in infrastructure_statuses:
        if counts[status]:
            failures.append(f"{counts[status]} selected mutants have status {status}")
    if score < minimum_score:
        failures.append(
            f"mutation score {score:.2f}% is below the {minimum_score:.2f}% floor"
        )

    evidence = {
        "schema_version": 1,
        "policy": "selected critical mutants; fail on infrastructure gaps or score regression",
        "minimum_score_percent": minimum_score,
        "score_percent": round(score, 2),
        "selected_mutants": len(selected),
        "counts": dict(sorted(counts.items())),
        "mutants_by_status": {
            status: sorted(name for name, value in by_status.items() if value == status)
            for status in sorted(set(by_status.values()))
        },
        "failures": failures,
    }
    return evidence, failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mutants_dir", type=Path)
    parser.add_argument("--pattern", required=True)
    parser.add_argument("--minimum-score", type=float, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if not 0 <= args.minimum_score <= 100:
        parser.error("--minimum-score must be between 0 and 100")

    selected = load_results(args.mutants_dir, args.pattern)
    evidence, failures = evaluate(selected, args.minimum_score)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")

    counts = evidence["counts"]
    print(
        f"{args.pattern}: score {evidence['score_percent']:.2f}%/"
        f"{args.minimum_score:.2f}%, selected {evidence['selected_mutants']}, "
        f"killed {counts.get('killed', 0)}, survived {counts.get('survived', 0)}"
    )
    for failure in failures:
        print(f"FAIL: {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
