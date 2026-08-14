#!/usr/bin/env python3
"""Emit exact direct lower bounds from Python package metadata."""

from __future__ import annotations

import re
from pathlib import Path

import tomllib

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "python" / "pyproject.toml"
NAME = re.compile(r"^([A-Za-z0-9_.-]+)")
LOWER = re.compile(r">=\s*([0-9][0-9A-Za-z.!+_-]*)")


def main() -> int:
    document = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    project = document["project"]
    requirements = list(project["dependencies"])
    extras = project["optional-dependencies"]
    for name in ("server", "mcp", "redis", "metrics"):
        requirements.extend(extras[name])
    lower_by_name: dict[str, tuple[str, str]] = {}
    for requirement in requirements:
        name_match = NAME.match(requirement)
        lower_match = LOWER.search(requirement)
        if not name_match or not lower_match:
            raise ValueError(
                f"Runtime requirement needs an explicit lower bound: {requirement}"
            )
        name = name_match.group(1)
        normalized = name.lower().replace("_", "-")
        version = lower_match.group(1)
        existing = lower_by_name.get(normalized)
        if existing is None or tuple(
            int(part) for part in version.split(".") if part.isdigit()
        ) > tuple(int(part) for part in existing[1].split(".") if part.isdigit()):
            upper = requirement[lower_match.end() :]
            lower_by_name[normalized] = (name, f"{name}=={version}{upper}")
    for _, requirement in sorted(lower_by_name.values()):
        print(requirement)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
