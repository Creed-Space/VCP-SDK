#!/usr/bin/env python3
"""Check VCP-SDK verification codes against the selected Spec registry."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def python_codes() -> list[dict[str, object]]:
    path = ROOT / "python" / "src" / "vcp" / "types.py"
    spec = importlib.util.spec_from_file_location("_vcp_types_status_check", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load Python status definitions: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(spec.name, None)
    verification_result = module.VerificationResult

    return [
        {
            "code": item.value,
            "symbol": item.name,
            "wire_label": item.name.lower(),
            "category": item.category,
        }
        for item in verification_result
    ]


def rust_codes() -> list[tuple[int, str]]:
    path = ROOT / "rust" / "vcp-core" / "src" / "error.rs"
    text = path.read_text(encoding="utf-8")
    match = re.search(
        r"pub enum VerificationCode\s*\{(?P<body>.*?)\n\}", text, re.DOTALL
    )
    if match is None:
        raise RuntimeError("could not locate Rust VerificationCode enum")
    entries = re.findall(
        r"^\s*([A-Z][A-Za-z0-9]+)\s*=\s*(\d+),",
        match.group("body"),
        re.MULTILINE,
    )
    return sorted((int(code), symbol) for symbol, code in entries)


def snake_to_pascal(value: str) -> str:
    return "".join(part.title() for part in value.lower().split("_"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", required=True, type=Path)
    args = parser.parse_args()
    path = args.spec.resolve() / "registries" / "verification-status-codes.json"
    if not path.is_file():
        print(f"ERROR: Spec status registry is missing: {path}", file=sys.stderr)
        return 1
    registry = json.loads(path.read_text(encoding="utf-8"))
    expected = [
        {
            "code": entry["code"],
            "symbol": entry["symbol"],
            "wire_label": entry["wire_label"],
            "category": entry["category"],
        }
        for entry in registry["codes"]
    ]
    failures = []
    if python_codes() != expected:
        failures.append("Python VerificationResult differs from the Spec registry")
    expected_rust = sorted(
        (entry["code"], snake_to_pascal(entry["symbol"])) for entry in expected
    )
    if rust_codes() != expected_rust:
        failures.append("Rust VerificationCode differs from the Spec registry")
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}", file=sys.stderr)
        return 1
    print(f"Status registry sync passed: {len(expected)} verification codes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
