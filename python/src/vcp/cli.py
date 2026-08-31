"""Command line entry point for VCP runtime diagnostics."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence

from .agent import runtime_identity


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="vcp")
    commands = parser.add_subparsers(dest="command", required=True)
    doctor = commands.add_parser("doctor", help="diagnose VCP runtime identity")
    doctor.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)

    identity = runtime_identity()
    payload = identity.model_dump(mode="json")
    if args.as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"distribution: {identity.distribution} {identity.version}")
        print(f"implementation: {identity.implementation}")
        print(f"module: {identity.module_path}")
        print(f"profiles: {', '.join(identity.supported_profiles)}")
        print(f"schema: {identity.schema_digest}")
        print(
            "discovered distributions: "
            + (", ".join(identity.discovered_distributions) or "source tree only")
        )
        print(f"collision: {'yes' if identity.collision else 'no'}")
        for transition in identity.safe_next:
            print(f"safe next: {transition}")
    return 2 if identity.collision else 0
