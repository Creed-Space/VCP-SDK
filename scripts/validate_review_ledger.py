#!/usr/bin/env python3
"""Validate the coordinated VCP human review ledger without closing its gates."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = ROOT / "release/review-ledger.schema.json"
DEFAULT_LEDGER = ROOT / "release/review-ledger.template.json"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")

EXPECTED_REVIEWS: dict[str, tuple[str, tuple[str, ...]]] = {
    "X015": ("release", ("VCP-Demo-Site", "VCP-Spec", "VCP-SDK")),
    "X016": ("legal", ("VCP-Demo-Site", "VCP-Spec", "VCP-SDK")),
    "X017": ("independent_security", ("VCP-Spec", "VCP-SDK")),
    "X018": ("production", ("VCP-Demo-Site", "VCP-SDK")),
    "D042": ("accessibility", ("VCP-Demo-Site",)),
    "D043": ("privacy", ("VCP-Demo-Site",)),
    "S030": ("governance", ("VCP-Spec",)),
    "S031": ("editorial", ("VCP-Spec",)),
    "S032": ("governance", ("VCP-Spec",)),
    "S033": ("independent_review", ("VCP-Spec",)),
    "K044": ("publication", ("VCP-SDK",)),
    "K045": ("independent_security", ("VCP-SDK",)),
    "K046": ("semver", ("VCP-SDK",)),
}

REQUIRED_EVIDENCE: dict[str, set[str]] = {
    "X015": {"release-approval"},
    "X016": {"legal-opinion"},
    "X017": {"independent-security-report"},
    "X018": {"production-smoke-report"},
    "D042": {"accessibility-report"},
    "D043": {"privacy-report", "network-capture"},
    "S030": {"governance-record"},
    "S031": {"artifact-hash-selection"},
    "S032": {"governance-record"},
    "S033": {"independent-review-report"},
    "K044": {"artifact-signature", "registry-receipt"},
    "K045": {"independent-security-report"},
    "K046": {"semver-decision"},
}

INDEPENDENT_GATES = {"X017", "S033", "K045"}


class Problems:
    def __init__(self) -> None:
        self.items: list[str] = []

    def add(self, message: str) -> None:
        self.items.append(message)

    def finish(self) -> int:
        if not self.items:
            print("VCP coordinated review ledger validation passed.")
            return 0
        for item in sorted(set(self.items)):
            print(f"ERROR: {item}", file=sys.stderr)
        print(
            f"Review ledger validation failed with {len(set(self.items))} problem(s).",
            file=sys.stderr,
        )
        return 1


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read {path}: {exc}") from exc


def candidate_is_locked(candidate: dict[str, Any], problems: Problems) -> bool:
    locked = True
    repositories = candidate.get("repositories", [])
    names = [item.get("name") for item in repositories if isinstance(item, dict)]
    if names != ["VCP-Demo-Site", "VCP-Spec", "VCP-SDK"]:
        problems.add(
            "candidate repositories must use the canonical three-repository order"
        )
        locked = False
    for repository in repositories:
        if not isinstance(repository, dict):
            locked = False
            continue
        name = repository.get("name", "unknown")
        if not isinstance(repository.get("commit"), str) or not COMMIT_RE.fullmatch(
            repository["commit"]
        ):
            problems.add(f"{name} needs an exact 40-character commit")
            locked = False
        for field in ("working_tree_sha256",):
            value = repository.get(field)
            if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
                problems.add(f"{name} needs an exact {field}")
                locked = False
    combined = candidate.get("combined_candidate_sha256")
    if not isinstance(combined, str) or not SHA256_RE.fullmatch(combined):
        problems.add("candidate needs an exact combined_candidate_sha256")
        locked = False
    source_manifest = candidate.get("source_manifest_sha256")
    if not isinstance(source_manifest, str) or not SHA256_RE.fullmatch(source_manifest):
        problems.add("candidate needs an exact source_manifest_sha256")
        locked = False
    return locked


def validate_review_shape(ledger: dict[str, Any], problems: Problems) -> None:
    reviews = ledger.get("reviews", [])
    by_id = {review.get("id"): review for review in reviews if isinstance(review, dict)}
    if set(by_id) != set(EXPECTED_REVIEWS) or len(reviews) != len(EXPECTED_REVIEWS):
        problems.add(
            "review ledger must contain each of the 13 canonical gates exactly once"
        )
        return

    for gate_id, (category, scope) in EXPECTED_REVIEWS.items():
        review = by_id[gate_id]
        if review.get("category") != category:
            problems.add(f"{gate_id} category must be {category}")
        if tuple(review.get("scope", [])) != scope:
            problems.add(f"{gate_id} scope must be {list(scope)}")
        status = review.get("status")
        if status == "pending":
            for field in ("reviewer", "reviewed_at", "decision_summary", "attestation"):
                if review.get(field) is not None:
                    problems.add(f"{gate_id} pending review must leave {field} null")
            for field in ("conditions", "findings", "evidence"):
                if review.get(field) != []:
                    problems.add(f"{gate_id} pending review must leave {field} empty")
            continue

        reviewer = review.get("reviewer")
        if not isinstance(reviewer, dict):
            problems.add(f"{gate_id} completed review needs a named reviewer")
        elif gate_id in INDEPENDENT_GATES:
            statement = reviewer.get("independence_statement", "").strip().lower()
            if len(statement) < 20 or statement in {"n/a", "none", "not independent"}:
                problems.add(
                    f"{gate_id} needs a substantive reviewer independence statement"
                )
        if not review.get("reviewed_at"):
            problems.add(f"{gate_id} completed review needs reviewed_at")
        summary = review.get("decision_summary")
        if not isinstance(summary, str) or len(summary.strip()) < 20:
            problems.add(
                f"{gate_id} completed review needs a substantive decision summary"
            )
        if status == "approved_with_conditions" and not review.get("conditions"):
            problems.add(f"{gate_id} approved_with_conditions needs conditions")
        if not isinstance(review.get("attestation"), dict):
            problems.add(f"{gate_id} completed review needs an attestation")

        evidence = review.get("evidence", [])
        evidence_kinds = {
            item.get("kind") for item in evidence if isinstance(item, dict)
        }
        missing = REQUIRED_EVIDENCE[gate_id] - evidence_kinds
        if missing:
            problems.add(f"{gate_id} is missing evidence kinds {sorted(missing)}")


def validate_candidate_semantics(
    ledger: dict[str, Any], problems: Problems, require_complete: bool
) -> None:
    candidate = ledger.get("candidate", {})
    reviews = ledger.get("reviews", [])
    has_completed_review = any(
        isinstance(review, dict) and review.get("status") != "pending"
        for review in reviews
    )
    if has_completed_review or require_complete:
        candidate_is_locked(candidate, problems)

    if require_complete:
        pending = [
            review.get("id")
            for review in reviews
            if isinstance(review, dict) and review.get("status") == "pending"
        ]
        if pending:
            problems.add(f"require-complete found pending gates: {', '.join(pending)}")

        protocol = candidate.get("protocol", {})
        if not protocol.get("amendment_maturity"):
            problems.add("completed ledger needs the v3.2 amendment maturity decision")
        versions = candidate.get("versions", {})
        for name in ("python", "rust", "webmcp", "demo"):
            version = versions.get(name)
            if not isinstance(version, str) or not SEMVER_RE.fullmatch(version):
                problems.add(f"completed ledger needs a semantic {name} version")
        deployment = candidate.get("deployment", {})
        for name in ("environment", "url", "release_id", "deployed_at"):
            if not deployment.get(name):
                problems.add(f"completed ledger needs deployment.{name}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", nargs="?", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument(
        "--require-complete",
        action="store_true",
        help="require exact candidate identity, deployment identity, and no pending gates",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    problems = Problems()
    try:
        schema = load_json(args.schema)
        ledger = load_json(args.ledger)
        Draft202012Validator.check_schema(schema)
    except (ValueError, SchemaError) as exc:
        problems.add(str(exc))
        return problems.finish()

    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    for error in sorted(
        validator.iter_errors(ledger), key=lambda item: list(item.path)
    ):
        location = ".".join(str(part) for part in error.absolute_path) or "root"
        problems.add(f"schema {location}: {error.message}")

    if isinstance(ledger, dict):
        validate_review_shape(ledger, problems)
        validate_candidate_semantics(ledger, problems, args.require_complete)
    else:
        problems.add("ledger root must be an object")
    return problems.finish()


if __name__ == "__main__":
    raise SystemExit(main())
