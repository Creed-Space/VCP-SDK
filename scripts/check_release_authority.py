#!/usr/bin/env python3
"""Validate SDK version coherence and fail closed on absent publication authority."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - exercised on Python 3.10 CI
    import tomli as tomllib

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True)
    parser.add_argument("--publish", action="store_true")
    parser.add_argument(
        "--ledger",
        type=Path,
        help="external coordinated review ledger used for publication authority",
    )
    args = parser.parse_args()
    problems: list[str] = []
    python = tomllib.loads((ROOT / "python" / "pyproject.toml").read_text())["project"][
        "version"
    ]
    rust = tomllib.loads((ROOT / "rust" / "Cargo.toml").read_text())["workspace"][
        "package"
    ]["version"]
    npm = json.loads((ROOT / "webmcp" / "package.json").read_text())["version"]
    for ecosystem, value in (("python", python), ("rust", rust), ("npm", npm)):
        if value != args.version:
            problems.append(
                f"{ecosystem} version {value!r} does not match {args.version!r}"
            )

    state = json.loads((ROOT / "release" / "publication-state.json").read_text())
    for artifact in state["artifacts"]:
        if artifact["candidate_version"] != args.version:
            problems.append(
                f"publication state {artifact['id']} version "
                f"{artifact['candidate_version']!r} does not match {args.version!r}"
            )

    if args.publish:
        if not state["candidate_names_ratified"]:
            problems.append("candidate artifact names have not been ratified")
        if state["overall_state"] not in {"candidate", "published"}:
            problems.append(
                "publication state must be candidate or published before registry upload"
            )
        ledger = args.ledger
        if ledger is None:
            problems.append("publication requires an external review ledger")
        elif not ledger.is_file():
            problems.append(f"review ledger is missing: {ledger}")
        else:
            validation = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "validate_review_ledger.py"),
                    str(ledger),
                    "--require-prepublication",
                ],
                cwd=ROOT,
                check=False,
            )
            if validation.returncode:
                problems.append(
                    "the coordinated review ledger has not passed "
                    "prepublication validation"
                )

    if problems:
        for problem in problems:
            print(f"ERROR: {problem}", file=sys.stderr)
        return 1
    scope = "publication" if args.publish else "candidate build"
    print(f"Release authority preflight passed for {scope} version {args.version}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
