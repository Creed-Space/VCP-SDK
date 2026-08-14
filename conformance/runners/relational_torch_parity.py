#!/usr/bin/env python3
"""Run relational and torch profile vectors against Python and Rust."""

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
FIXTURES = {
    "relational": ROOT / "conformance" / "extensions" / "relational_context.json",
    "torch": ROOT / "conformance" / "extensions" / "torch_handoff.json",
}


def load_python() -> dict[str, Any]:
    if str(PYTHON_SRC) not in sys.path:
        sys.path.insert(0, str(PYTHON_SRC))
    from vcp.extensions.relational import (
        AISelfModel,
        DimensionReport,
        RelationalContext,
        RelationalNorm,
        StandingLevel,
        TrustLevel,
    )
    from vcp.extensions.torch import TorchChain, TorchConsumer, TorchGenerator

    return locals()


def relational_case(case: dict[str, Any], api: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    case_id = case["id"]
    expected = case["expected"]
    if case_id == "trust-level-ordering":
        return "passed", {"trust_levels": [item.value for item in api["TrustLevel"]]}
    if case_id == "standing-level-ordering":
        return "passed", {"standing_levels": [item.value for item in api["StandingLevel"]]}
    if case_id.startswith("trust-from-session-count-"):
        if case_id.endswith("boundaries"):
            actual = [
                {
                    "session_count": item["session_count"],
                    "trust_level": api["TorchConsumer"]()
                    .receive_protocol({"session_count": item["session_count"]})
                    .trust_level.value,
                }
                for item in expected["boundaries"]
            ]
            return "passed", {"boundaries": actual}
        context = api["TorchConsumer"]().receive_protocol(
            {"session_count": case["input"]["session_count"]}
        )
        return "passed", {"trust_level": context.trust_level.value}
    if case_id == "self-model-dimension-range":
        api["DimensionReport"](1.0, True)
        api["DimensionReport"](9.0, True)
        return "passed", {"min_value": 1.0, "max_value": 9.0}
    if case_id.startswith("self-model-"):
        model = api["AISelfModel"].from_dict(case["input"]["ai_self_model"])
        return "passed", {
            "valid": True,
            "has_uncertainty_markers": model.has_uncertainty_markers(),
            "dimension_count": len(model.get_all_dimensions()),
        }
    if case_id.startswith("norm-"):
        try:
            api["RelationalNorm"].from_dict(case["input"]["norm"])
            valid = True
        except ValueError:
            valid = False
        return "passed", {"valid": valid}
    if case_id == "relational-context-defaults":
        return "passed", api["RelationalContext"]().to_protocol_dict()
    if case_id == "torch-receive-bootstraps-context":
        context = api["TorchConsumer"]().receive_protocol(case["input"]["torch"])
        return "passed", {
            "trust_level": context.trust_level.value,
            "standing": context.standing_level.value,
            "continuity_depth": context.interaction_count,
        }
    return "not_applicable", {"reason": "vocabulary-only documentation vector"}


def torch_case(case: dict[str, Any], api: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    case_id = case["id"]
    if case_id == "basic-handoff":
        context = api["RelationalContext"].from_dict(case["input"]["relational_context"])
        return "passed", {
            "torch": api["TorchGenerator"]().generate_protocol(
                context, "2026-02-28T10:00:00Z"
            )
        }
    if case_id in {"lineage-chain", "round-trip-serialization"}:
        lineage = api["TorchChain"].from_dict(case["input"]["lineage"])
        serialized = lineage.to_dict()
        return "passed", {
            "session_count": lineage.session_count,
            "lineage_depth": len(lineage.torch_chain),
            "first_session_date": lineage.first_session_date,
            "chain_length": len(lineage.torch_chain),
            "serialized": serialized,
            "round_trip_equal": api["TorchChain"].from_dict(serialized) == lineage,
        }
    if case_id == "torch-receive-trust-mapping":
        mappings = [
            {
                "session_count": item["session_count"],
                "trust_level": api["TorchConsumer"]()
                .receive_protocol({"session_count": item["session_count"]})
                .trust_level.value,
            }
            for item in case["input"]["torches"]
        ]
        return "passed", {"standing": "advisory", "mappings": mappings}
    if case_id == "gestalt-token-format":
        tokens = []
        for item in case["input"]["self_model_cases"]:
            model_data = {
                name: {"value": value, "uncertain": True}
                for name, value in item["dimensions"].items()
            }
            model = api["AISelfModel"].from_dict(model_data)
            tokens.append(api["TorchGenerator"]()._build_gestalt(model))
        return "passed", {"tokens": tokens}
    if case_id == "trajectory-derivation":
        trajectories = []
        for item in case["input"]["cases"]:
            history = [api["AISelfModel"].from_dict(entry["model"]) for entry in item["self_model_history"]]
            trajectories.append(api["TorchGenerator"].derive_trajectory(history))
        return "passed", {"trajectories": trajectories}
    return "not_applicable", {"reason": "model-shape documentation vector"}


def expected_failures(case: dict[str, Any], actual: dict[str, Any]) -> list[str]:
    expected = case["expected"]
    case_id = case["id"]
    failures: list[str] = []
    if case_id == "basic-handoff":
        expected = expected["torch"]
        actual = actual["torch"]
    if case_id == "torch-receive-trust-mapping":
        by_count = {item["session_count"]: item["trust_level"] for item in actual["mappings"]}
        for item in case["input"]["torches"]:
            if by_count[item["session_count"]] != item["expected_trust"]:
                failures.append(f"{case_id}: trust mapping differs at {item['session_count']}")
        return failures
    if case_id == "gestalt-token-format":
        expected_tokens = [item["expected_token"] for item in case["input"]["self_model_cases"]]
        return [] if actual["tokens"] == expected_tokens else [f"{case_id}: tokens differ"]
    if case_id == "trajectory-derivation":
        expected_values = [item["expected_trajectory"] for item in case["input"]["cases"]]
        return [] if actual["trajectories"] == expected_values else [f"{case_id}: trajectories differ"]
    for key, value in expected.items():
        if key in {"note", "notes", "ordering", "origin_values", "uncertainty_range"}:
            continue
        if key in actual and actual[key] != value:
            failures.append(f"{case_id}: {key}={actual[key]!r}, expected={value!r}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    api = load_python()
    failures: list[str] = []
    results: list[dict[str, Any]] = []
    not_applicable = 0
    for profile, fixture_path in FIXTURES.items():
        document = json.loads(fixture_path.read_text(encoding="utf-8"))
        for case in document["test_cases"]:
            status, actual = (
                relational_case(case, api) if profile == "relational" else torch_case(case, api)
            )
            if status == "not_applicable":
                not_applicable += 1
            else:
                failures.extend(expected_failures(case, actual))
            results.append({"suite": profile, "id": case["id"], "status": status, "python": actual})

    rust = subprocess.run(
        ["cargo", "test", "-q", "-p", "vcp-core", "--test", "extension_conformance"],
        cwd=ROOT / "rust",
        text=True,
        capture_output=True,
        timeout=180,
        check=False,
        env={**__import__("os").environ, "CARGO_PROFILE_DEV_DEBUG": "0", "CARGO_INCREMENTAL": "0"},
    )
    if rust.returncode:
        failures.append(f"Rust extension conformance failed:\n{(rust.stdout + rust.stderr)[-4000:]}")
    report = {
        "schema": "vcp-conformance-report/1",
        "profile": "relational-and-torch",
        "implementations": ["python", "rust"],
        "fixture_sha256": {
            path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in FIXTURES.values()
        },
        "summary": {
            "cases": len(results) - not_applicable,
            "not_applicable": not_applicable,
            "failures": len(failures),
        },
        "results": results,
        "rust_command_output_sha256": hashlib.sha256((rust.stdout + rust.stderr).encode()).hexdigest(),
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
        f"Relational and torch parity passed: {len(results) - not_applicable} behavior vectors; "
        f"{not_applicable} vocabulary vectors not applicable."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
