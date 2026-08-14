#!/usr/bin/env python3
"""Run layered constitution-composition vectors against Python and Rust."""

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
FIXTURE = ROOT / "conformance" / "semantics" / "composition.json"


def python_result(case: dict[str, Any]) -> dict[str, Any]:
    if str(PYTHON_SRC) not in sys.path:
        sys.path.insert(0, str(PYTHON_SRC))
    from vcp.semantics.composer import compose_layered

    return compose_layered(case["bundles"], case.get("available_constitutions"))


def rust_result(case: dict[str, Any]) -> dict[str, Any]:
    value = {
        "bundles": case["bundles"],
        "available_constitutions": case.get("available_constitutions"),
    }
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8", delete=False) as handle:
        path = Path(handle.name)
        json.dump(value, handle)
    try:
        result = subprocess.run(
            [str(RUST_BINARY), "run-layered-composition", str(path)],
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
    not_applicable = 0
    for case in document["vectors"]:
        if "bundles" not in case:
            not_applicable += 1
            results.append({"id": case["id"], "status": "not_applicable", "reason": "vocabulary vector"})
            continue
        py = python_result(case)
        rs = rust_result(case)
        expected = {key: value for key, value in case["expected"].items() if key != "note"}
        for implementation, actual in (("Python", py), ("Rust", rs)):
            for key, value in expected.items():
                if actual.get(key) != value:
                    failures.append(
                        f"{case['id']}: {implementation} {key}={actual.get(key)!r}, expected={value!r}"
                    )
        if py != rs:
            failures.append(f"{case['id']}: Python and Rust differ")
        results.append({"id": case["id"], "python": py, "rust": rs})
    report = {
        "schema": "vcp-conformance-report/1",
        "profile": "layered-composition",
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
        f"Composition parity passed: {len(results) - not_applicable} cases across Python and Rust; "
        f"{not_applicable} vocabulary vectors not applicable."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
