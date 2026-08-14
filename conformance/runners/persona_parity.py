#!/usr/bin/env python3
"""Run persona resolution vectors against Python and Rust."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_SRC = ROOT / "python" / "src"
RUST_BINARY = ROOT / "rust" / "target" / "debug" / "vcp-cli"
FIXTURE = ROOT / "conformance" / "semantics" / "persona_resolution.json"
VALID_CODES = "NZGAMDC"


def python_resolve(code: str) -> dict[str, Any]:
    if str(PYTHON_SRC) not in sys.path:
        sys.path.insert(0, str(PYTHON_SRC))
    from vcp.semantics.csm1 import Persona

    try:
        persona = Persona.from_wire_char(code)
    except ValueError:
        return {"valid": False}
    return {
        "valid": True,
        "persona_code": persona.value,
        "persona_name": persona.name.lower(),
        "focus": persona.focus,
        "default_adherence": persona.default_adherence,
        "requires_namespace": persona is Persona.CUSTOM,
    }


def rust_resolve(code: str) -> dict[str, Any]:
    result = subprocess.run(
        [str(RUST_BINARY), "resolve-persona", code],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=10,
        check=False,
    )
    if result.returncode:
        return {"valid": False}
    return {"valid": True, **json.loads(result.stdout)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-build", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if not args.skip_build:
        subprocess.run(
            ["cargo", "build", "--quiet", "-p", "vcp-cli"],
            cwd=ROOT / "rust",
            check=True,
        )
    document = json.loads(FIXTURE.read_text(encoding="utf-8"))
    failures: list[str] = []
    results: list[dict[str, Any]] = []
    for case in document["vectors"]:
        if "input_name" in case:
            py_matches = [code for code in VALID_CODES if python_resolve(code).get("persona_name") == case["input_name"]]
            rs_matches = [code for code in VALID_CODES if rust_resolve(code).get("persona_name") == case["input_name"]]
            py = {"persona_code": py_matches[0] if len(py_matches) == 1 else None}
            rs = {"persona_code": rs_matches[0] if len(rs_matches) == 1 else None}
        else:
            py = python_resolve(case["input"])
            rs = rust_resolve(case["input"])
        for implementation, actual in (("Python", py), ("Rust", rs)):
            for key, value in case["expected"].items():
                if key == "note":
                    continue
                if actual.get(key) != value:
                    failures.append(
                        f"{case['id']}: {implementation} {key}={actual.get(key)!r}, expected={value!r}"
                    )
        if py != rs:
            failures.append(f"{case['id']}: Python and Rust differ")
        results.append({"id": case["id"], "python": py, "rust": rs})
    report = {
        "schema": "vcp-conformance-report/1",
        "profile": "persona-resolution",
        "implementations": ["python", "rust"],
        "fixture_sha256": hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
        "summary": {"cases": len(results), "failures": len(failures)},
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
    print(f"Persona parity passed: {len(results)} cases across Python and Rust.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
