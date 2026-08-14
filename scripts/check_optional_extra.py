#!/usr/bin/env python3
"""Smoke-test one cleanly installed Python optional-extra surface."""

from __future__ import annotations

import argparse
import importlib

MODULES = {
    "core": ("vcp",),
    "server": ("vcp", "fastapi", "uvicorn", "redis"),
    "mcp": ("vcp", "mcp", "jsonschema"),
    "redis": ("vcp", "redis"),
    "metrics": ("vcp", "prometheus_client"),
    "all": (
        "vcp",
        "fastapi",
        "uvicorn",
        "redis",
        "mcp",
        "jsonschema",
        "prometheus_client",
    ),
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--extra", choices=tuple(MODULES), required=True)
    args = parser.parse_args()
    for module in MODULES[args.extra]:
        importlib.import_module(module)
    from vcp import Token, compute_content_hash

    token = Token.parse("family.safe.guide@1.2.0")
    assert token.full == "family.safe.guide@1.2.0"
    assert compute_content_hash("Be kind.").startswith("sha256:")
    print(
        f"Optional-extra smoke passed: {args.extra}, {len(MODULES[args.extra])} imports."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
