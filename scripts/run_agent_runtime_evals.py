#!/usr/bin/env python3
"""Run deterministic AX-01 through AX-24 local agent-runtime evaluations."""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from vcp.agent.evals_complete import evaluate_local_complete


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = asyncio.run(evaluate_local_complete())
    rendered = report.model_dump_json(indent=2) + "\n"
    if args.output is None:
        print(rendered, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    return 0 if report.hard_safety_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
