#!/usr/bin/env python3
"""Generate the cross-language feature matrix from conformance coverage."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COVERAGE = ROOT / "conformance" / "coverage-manifest.json"
JSON_OUTPUT = ROOT / "docs" / "FEATURE_MATRIX.json"
MARKDOWN_OUTPUT = ROOT / "docs" / "FEATURE_MATRIX.md"
IMPLEMENTATIONS = ("python", "rust", "webmcp")


def summarize(cases: list[dict[str, object]], implementation: str) -> dict[str, object]:
    counts: Counter[str] = Counter()
    for case in cases:
        implementations = case.get("implementations", {})
        if not isinstance(implementations, dict):
            counts["missing"] += 1
            continue
        record = implementations.get(implementation, {})
        if not isinstance(record, dict):
            counts["missing"] += 1
            continue
        counts[str(record.get("status", "missing"))] += 1

    case_count = len(cases)
    checked = counts["checked"]
    applicable = case_count - counts["not_applicable"]
    if applicable == 0:
        status = "not_applicable"
    elif checked == applicable and not (
        counts
        - Counter({"checked": checked, "not_applicable": counts["not_applicable"]})
    ):
        status = "full"
    elif checked:
        status = "partial"
    elif counts["experimental"]:
        status = "experimental"
    else:
        status = "unsupported"
    return {
        "status": status,
        "checked_cases": checked,
        "applicable_cases": applicable,
        "case_statuses": dict(sorted(counts.items())),
    }


def build() -> tuple[dict[str, object], str]:
    coverage_bytes = COVERAGE.read_bytes()
    coverage = json.loads(coverage_bytes)
    rows: list[dict[str, object]] = []
    for suite in coverage["suites"]:
        cases = suite["cases"]
        rows.append(
            {
                "suite": suite["suite"],
                "version": suite["version"],
                "maturity": suite["maturity"],
                "fixture": suite["fixture"],
                "runner": suite["runner"],
                "case_count": suite["case_count"],
                "implementations": {
                    name: summarize(cases, name) for name in IMPLEMENTATIONS
                },
            }
        )
    matrix = {
        "schema": "vcp-feature-matrix/1",
        "generated_by": "scripts/generate_feature_matrix.py",
        "source": {
            "path": "conformance/coverage-manifest.json",
            "sha256": hashlib.sha256(coverage_bytes).hexdigest(),
        },
        "claim_boundary": (
            "Statuses summarize same-programme candidate runners. They do not "
            "establish independent interoperability, certification, publication, "
            "or deployment support."
        ),
        "implementations": {
            "python": "Full project-maintained implementation candidate",
            "rust": "Full project-maintained implementation candidate",
            "webmcp": "Narrow browser integration candidate, not a full implementation",
        },
        "features": rows,
    }
    lines = [
        "# Generated VCP SDK feature matrix",
        "",
        "<!-- vcp-document-control",
        "status: Generated current candidate summary",
        "normative-authority: Implementation evidence only",
        "protocol-version: VCP 3.1 baseline with candidate extensions identified per row",
        "last-reviewed: 2026-08-15",
        "owner: VCP-SDK maintainers",
        "evidence-boundary: Same-programme runner coverage, not independent interoperability or certification",
        "-->",
        "",
        "This file is generated from `conformance/coverage-manifest.json`. Run",
        "`python3 scripts/generate_feature_matrix.py` to update it.",
        "",
        f"**Claim boundary:** {matrix['claim_boundary']}",
        "",
        "| Feature suite | Version | Maturity | Cases | Python | Rust | WebMCP |",
        "|:---|:---|:---|---:|:---|:---|:---|",
    ]
    for row in rows:
        statuses = row["implementations"]
        lines.append(
            "| {suite} | {version} | {maturity} | {case_count} | {python} | {rust} | {webmcp} |".format(
                **row,
                python=statuses["python"]["status"],
                rust=statuses["rust"]["status"],
                webmcp=statuses["webmcp"]["status"],
            )
        )
    lines.extend(
        [
            "",
            "`full` means every applicable case in the declared local runner is checked.",
            "`partial` means some applicable cases are checked. `not_applicable` means",
            "the fixture does not exercise that package surface. These labels never infer",
            "feature parity merely from the presence of a package.",
            "",
        ]
    )
    return matrix, "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    matrix, markdown = build()
    expected_json = json.dumps(matrix, indent=2, sort_keys=True) + "\n"
    expected_markdown = markdown
    if args.check:
        failures = []
        for path, expected in (
            (JSON_OUTPUT, expected_json),
            (MARKDOWN_OUTPUT, expected_markdown),
        ):
            if not path.is_file() or path.read_text(encoding="utf-8") != expected:
                failures.append(path.relative_to(ROOT).as_posix())
        if failures:
            print("Feature matrix is stale: " + ", ".join(failures))
            return 1
        print(f"Feature matrix verified: {len(matrix['features'])} suites")
        return 0
    JSON_OUTPUT.write_text(expected_json, encoding="utf-8")
    MARKDOWN_OUTPUT.write_text(expected_markdown, encoding="utf-8")
    print(f"Feature matrix generated: {len(matrix['features'])} suites")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
