#!/usr/bin/env python3
"""Enforce per-module statement and branch floors for security-critical code."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

THRESHOLDS = {
    "src/vcp/bundle.py": {"statements": 75.0, "branches": 50.0},
    "src/vcp/canonicalize.py": {"statements": 90.0, "branches": 78.0},
    "src/vcp/enforcement.py": {"statements": 90.0, "branches": 76.0},
    "src/vcp/identity/token.py": {"statements": 75.0, "branches": 68.0},
    "src/vcp/orchestrator.py": {"statements": 80.0, "branches": 66.0},
    "src/vcp/privacy.py": {"statements": 96.0, "branches": 88.0},
    "src/vcp/revocation.py": {"statements": 75.0, "branches": 70.0},
    "src/vcp/semantics/csm1.py": {"statements": 90.0, "branches": 82.0},
}


def _percentage(covered: int, total: int) -> float:
    return 100.0 if total == 0 else covered * 100.0 / total


def evaluate(report: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    files = report.get("files", {})
    results: list[dict[str, Any]] = []
    failures: list[str] = []
    for suffix, floors in THRESHOLDS.items():
        matches = [
            value
            for name, value in files.items()
            if name.replace("\\", "/").endswith(suffix)
        ]
        if len(matches) != 1:
            failures.append(
                f"{suffix}: expected one coverage record, found {len(matches)}"
            )
            continue
        summary = matches[0]["summary"]
        statement_percent = _percentage(
            summary["covered_lines"], summary["num_statements"]
        )
        branch_percent = _percentage(
            summary["covered_branches"], summary["num_branches"]
        )
        result = {
            "path": suffix,
            "statement_percent": round(statement_percent, 2),
            "statement_floor": floors["statements"],
            "branch_percent": round(branch_percent, 2),
            "branch_floor": floors["branches"],
        }
        results.append(result)
        if statement_percent < floors["statements"]:
            failures.append(
                f"{suffix}: statement coverage {statement_percent:.2f}% < {floors['statements']:.2f}%"
            )
        if branch_percent < floors["branches"]:
            failures.append(
                f"{suffix}: branch coverage {branch_percent:.2f}% < {floors['branches']:.2f}%"
            )
    return results, failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = json.loads(args.report.read_text(encoding="utf-8"))
    results, failures = evaluate(report)
    evidence = {
        "schema_version": 1,
        "source_report": str(args.report),
        "policy": "risk-based per-module statement and branch floors",
        "results": results,
        "failures": failures,
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    for result in results:
        print(
            f"{result['path']}: statements {result['statement_percent']:.2f}%/"
            f"{result['statement_floor']:.2f}%, branches {result['branch_percent']:.2f}%/"
            f"{result['branch_floor']:.2f}%"
        )
    if failures:
        print("Critical coverage failures:")
        for failure in failures:
            print(f"  {failure}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
