#!/usr/bin/env python3
"""Check Python and Rust context encoding against core and extended fixtures."""

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
FIXTURES = (
    ROOT / "conformance" / "adaptation" / "context_encoding.json",
    ROOT / "conformance" / "adaptation" / "context_encoding_extended.json",
)


def python_context(value: dict[str, Any]) -> tuple[Any, dict[str, Any]]:
    if str(PYTHON_SRC) not in sys.path:
        sys.path.insert(0, str(PYTHON_SRC))
    from vcp.adaptation.context import (
        PersonalState,
        PersonalStateDimension,
        SituationalDimension,
        VCPContext,
    )

    context = VCPContext(
        situational={
            SituationalDimension.from_name(name): list(tags)
            for name, tags in value.get("situational", {}).items()
        },
        personal={
            PersonalStateDimension.from_name(name): PersonalState(
                state["value"], state.get("intensity")
            )
            for name, state in value.get("personal", {}).items()
        },
    )
    wire = context.encode()
    decoded = VCPContext.decode(wire)
    return context, {
        "wire": wire,
        "has_any": bool(context.situational or context.personal),
        "has_situational": bool(context.situational),
        "has_personal": bool(context.personal),
        "has_vep_0004": any(dimension.is_vep_0004 for dimension in context.situational),
        "conformance_level": context.conformance_level(),
        "roundtrip": decoded.to_json(),
    }


def rust_context(value: dict[str, Any]) -> dict[str, Any]:
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8", delete=False) as handle:
        path = Path(handle.name)
        json.dump(value, handle, ensure_ascii=False)
    try:
        result = subprocess.run(
            [str(RUST_BINARY), "encode-context", str(path)],
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


def assert_expected(case_id: str, actual: dict[str, Any], expected: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    checks = {
        "wire": actual["wire"],
        "has_any": actual["has_any"],
        "has_situational": actual["has_situational"],
        "has_personal": actual["has_personal"],
        "has_vep_0004": actual["has_vep_0004"],
        "conformance_level": actual["conformance_level"],
    }
    for key, value in checks.items():
        if key in expected and value != expected[key]:
            failures.append(f"{case_id}: {key}={value!r}, expected={expected[key]!r}")
    if "wire_contains" in expected and expected["wire_contains"] not in actual["wire"]:
        failures.append(f"{case_id}: wire lacks {expected['wire_contains']!r}")
    if "wire_does_not_contain" in expected and expected["wire_does_not_contain"] in actual["wire"]:
        failures.append(f"{case_id}: wire contains forbidden {expected['wire_does_not_contain']!r}")
    if "wire_starts_with" in expected and not actual["wire"].startswith(expected["wire_starts_with"]):
        failures.append(f"{case_id}: wire prefix mismatch")
    if expected.get("separator_u2016_present") and "‖" not in actual["wire"]:
        failures.append(f"{case_id}: personal separator missing")
    if expected.get("wire_contains_separator_u2016") and "‖" not in actual["wire"]:
        failures.append(f"{case_id}: expected personal separator missing")
    return failures


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

    failures: list[str] = []
    results: list[dict[str, Any]] = []
    for fixture in FIXTURES:
        document = json.loads(fixture.read_text(encoding="utf-8"))
        for vector in document["vectors"]:
            case_id = vector["id"]
            if "wire_input" in vector:
                if str(PYTHON_SRC) not in sys.path:
                    sys.path.insert(0, str(PYTHON_SRC))
                from vcp.adaptation.context import VCPContext

                decoded = VCPContext.decode(vector["wire_input"])
                py = {
                    "wire": decoded.encode(),
                    "has_any": bool(decoded.situational or decoded.personal),
                    "has_situational": bool(decoded.situational),
                    "has_personal": bool(decoded.personal),
                    "has_vep_0004": any(d.is_vep_0004 for d in decoded.situational),
                    "conformance_level": decoded.conformance_level(),
                }
                parsed = subprocess.run(
                    [str(RUST_BINARY), "parse-context", vector["wire_input"]],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if parsed.returncode:
                    failures.append(f"{case_id}: Rust rejected wire input")
                    continue
                rust_decoded = json.loads(parsed.stdout)
                rs = rust_context(rust_decoded)
            else:
                _, py = python_context(vector["input"])
                rs = rust_context(vector["input"])
            failures.extend(f"Python {failure}" for failure in assert_expected(case_id, py, vector["expected"]))
            failures.extend(f"Rust {failure}" for failure in assert_expected(case_id, rs, vector["expected"]))
            for key in (
                "wire",
                "has_any",
                "has_situational",
                "has_personal",
                "has_vep_0004",
                "conformance_level",
            ):
                if py.get(key) != rs.get(key):
                    failures.append(f"{case_id}: Python and Rust {key} differ")
            results.append({"id": case_id, "python": py, "rust": rs})

    report = {
        "schema": "vcp-conformance-report/1",
        "profile": "context-parity",
        "implementations": ["python", "rust"],
        "fixture_sha256": {
            path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in FIXTURES
        },
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
    print(f"Context parity passed: {len(results)} cases across Python and Rust.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
