#!/usr/bin/env python3
"""Require two independently built release directories to match byte for byte."""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path


def inventory(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("first", type=Path)
    parser.add_argument("second", type=Path)
    args = parser.parse_args()
    first = inventory(args.first)
    second = inventory(args.second)
    missing = sorted(set(first) - set(second))
    unexpected = sorted(set(second) - set(first))
    changed = sorted(
        name for name in first.keys() & second if first[name] != second[name]
    )
    if missing or unexpected or changed:
        print(f"missing from second: {missing}", file=sys.stderr)
        print(f"unexpected in second: {unexpected}", file=sys.stderr)
        print(f"digest mismatches: {changed}", file=sys.stderr)
        return 1
    print(f"Reproducibility comparison passed for {len(first)} files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
