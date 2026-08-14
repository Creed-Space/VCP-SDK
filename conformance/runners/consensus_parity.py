#!/usr/bin/env python3
"""Run Schulze consensus vectors against the Python and Rust SDKs."""

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
FIXTURE = ROOT / "conformance" / "extensions" / "consensus_voting.json"
CHECKED_KEYS = {
    "winner",
    "has_condorcet_winner",
    "ballot_count",
    "pairwise_matrix",
    "strongest_paths",
    "ranking",
    "ties",
}


def python_result(value: dict[str, Any]) -> dict[str, Any]:
    if str(PYTHON_SRC) not in sys.path:
        sys.path.insert(0, str(PYTHON_SRC))
    from vcp.extensions.consensus import Ballot, SchulzeElection

    candidates = value["candidates"]
    election = SchulzeElection(candidates)
    for ballot in value.get("ballots", []):
        election.add_ballot(Ballot.from_dict(ballot))
    result = election.compute()
    winner = result.winner
    has_condorcet = False
    if winner is not None:
        winner_index = candidates.index(winner)
        has_condorcet = all(
            index == winner_index
            or result.pairwise_matrix[winner_index][index]
            > result.pairwise_matrix[index][winner_index]
            for index in range(len(candidates))
        )
    ties: list[list[str]] = []
    if value.get("ballots"):
        for left in range(len(candidates)):
            for right in range(left + 1, len(candidates)):
                if (
                    result.strongest_paths[left][right]
                    == result.strongest_paths[right][left]
                ):
                    ties.append([candidates[left], candidates[right]])
    return {
        "winner": winner,
        "ranking": [
            {
                "candidate": item.candidate,
                "rank": item.rank,
                "wins": item.wins,
                "losses": item.losses,
            }
            for item in result.ranking
        ],
        "pairwise_matrix": result.pairwise_matrix,
        "strongest_paths": result.strongest_paths,
        "candidates": candidates,
        "ballot_count": len(value.get("ballots", [])),
        "has_condorcet_winner": has_condorcet,
        "ties": ties,
    }


def rust_result(value: dict[str, Any]) -> dict[str, Any]:
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8", delete=False) as handle:
        path = Path(handle.name)
        json.dump(value, handle)
    try:
        result = subprocess.run(
            [str(RUST_BINARY), "run-consensus", str(path)],
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


def compare(case_id: str, implementation: str, actual: dict[str, Any], expected: dict[str, Any]) -> list[str]:
    return [
        f"{case_id}: {implementation} {key}={actual.get(key)!r}, expected={value!r}"
        for key, value in expected.items()
        if key in CHECKED_KEYS and actual.get(key) != value
    ]


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
    document = json.loads(FIXTURE.read_text(encoding="utf-8"))
    failures: list[str] = []
    results: list[dict[str, Any]] = []
    not_applicable = 0
    for case in document["test_cases"]:
        if "candidates" not in case["input"]:
            not_applicable += 1
            results.append({"id": case["id"], "status": "not_applicable", "reason": "model-shape documentation vector"})
            continue
        py = python_result(case["input"])
        rs = rust_result(case["input"])
        failures.extend(compare(case["id"], "Python", py, case["expected"]))
        failures.extend(compare(case["id"], "Rust", rs, case["expected"]))
        for key in CHECKED_KEYS:
            if key in case["expected"] and py.get(key) != rs.get(key):
                failures.append(f"{case['id']}: Python and Rust {key} differ")
        results.append({"id": case["id"], "python": py, "rust": rs})
    report = {
        "schema": "vcp-conformance-report/1",
        "profile": "schulze-consensus",
        "implementations": ["python", "rust"],
        "fixture_sha256": hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
        "summary": {
            "cases": len(results) - not_applicable,
            "not_applicable": not_applicable,
            "failures": len(failures),
        },
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
        f"Consensus parity passed: {len(results) - not_applicable} cases across Python and Rust; "
        f"{not_applicable} documentation vectors not applicable."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
