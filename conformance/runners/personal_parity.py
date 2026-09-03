#!/usr/bin/env python3
"""Run personal-state decay and lifecycle vectors against Python, Rust, and WebMCP."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_SRC = ROOT / "python" / "src"
RUST_BINARY = ROOT / "rust" / "target" / "debug" / "vcp-cli"
FIXTURE = ROOT / "conformance" / "extensions" / "personal_state.json"
WEBMCP_RUNNER = ROOT / "webmcp" / "scripts" / "run-personal.mjs"


def _load_python() -> tuple[Any, Any, Any, Any]:
    if str(PYTHON_SRC) not in sys.path:
        sys.path.insert(0, str(PYTHON_SRC))
    from vcp.extensions.personal import (
        DECAY_CONFIGS,
        DecayConfig,
        compute_decayed_intensity,
        compute_lifecycle_state,
    )

    return (
        DECAY_CONFIGS,
        DecayConfig,
        compute_decayed_intensity,
        compute_lifecycle_state,
    )


def _python_configs() -> dict[str, dict[str, Any]]:
    configs, _, _, _ = _load_python()
    return {
        name: {
            "half_life_seconds": config.half_life_seconds,
            "baseline": config.baseline,
            "reset_on_engagement": config.reset_on_engagement,
            "stale_threshold": config.stale_threshold,
            "fresh_window_seconds": config.fresh_window_seconds,
        }
        for name, config in configs.items()
    }


def _rust(*args: str) -> str:
    result = subprocess.run(
        [str(RUST_BINARY), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=10,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(
            result.stderr.strip() or f"Rust CLI exited {result.returncode}"
        )
    return result.stdout.strip()


def _config_from_input(value: dict[str, Any]) -> dict[str, Any]:
    config = value.get("config", value)
    return {
        "half_life_seconds": float(config.get("half_life_seconds", 1800)),
        "baseline": int(config.get("baseline", 1)),
        "fresh_window_seconds": float(config.get("fresh_window_seconds", 60)),
        "stale_threshold": float(config.get("stale_threshold", 0.3)),
        "pinned": bool(config.get("pinned", value.get("pinned", False))),
    }


def _python_case(value: dict[str, Any], *, lifecycle: bool) -> dict[str, Any]:
    _, config_type, decay, classify = _load_python()
    config_values = _config_from_input(value)
    config = config_type(**config_values)
    declared_at = datetime(1970, 1, 1, tzinfo=timezone.utc)
    now = declared_at + timedelta(seconds=float(value["elapsed_seconds"]))
    effective = decay(int(value["declared_intensity"]), declared_at, config, now)
    if lifecycle:
        return {
            "lifecycle_state": classify(
                int(value["declared_intensity"]), declared_at, config, now
            ).value,
            "effective_intensity": effective,
        }
    return {"decayed_intensity": effective}


def _rust_case(value: dict[str, Any], *, lifecycle: bool) -> dict[str, Any]:
    config = _config_from_input(value)
    common = [
        str(value["declared_intensity"]),
        str(config["half_life_seconds"]),
        str(config["baseline"]),
        str(value["elapsed_seconds"]),
    ]
    pinned = ["--pinned"] if config["pinned"] else []
    if lifecycle:
        raw = _rust(
            "personal-lifecycle",
            *common,
            str(config["fresh_window_seconds"]),
            str(config["stale_threshold"]),
            *pinned,
        )
        return json.loads(raw)
    return {"decayed_intensity": int(_rust("personal-decay", *common, *pinned))}


def _webmcp(payload: dict[str, Any]) -> dict[str, Any]:
    """Run one fixture case through the built WebMCP personal module."""
    with tempfile.NamedTemporaryFile(
        "w", suffix=".json", encoding="utf-8", delete=False
    ) as handle:
        path = Path(handle.name)
        json.dump(payload, handle, ensure_ascii=False)
    try:
        result = subprocess.run(
            ["node", str(WEBMCP_RUNNER), str(path)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=10,
            check=False,
        )
    finally:
        path.unlink(missing_ok=True)
    if result.returncode:
        raise RuntimeError(
            result.stderr.strip() or f"WebMCP runner exited {result.returncode}"
        )
    return json.loads(result.stdout)


def _webmcp_case(value: dict[str, Any], *, lifecycle: bool) -> dict[str, Any]:
    config = _config_from_input(value)
    return _webmcp(
        {
            "mode": "lifecycle" if lifecycle else "decay",
            "declared_intensity": int(value["declared_intensity"]),
            "elapsed_seconds": float(value["elapsed_seconds"]),
            "config": config,
        }
    )


def _expected_subset(actual: dict[str, Any], expected: dict[str, Any]) -> list[str]:
    return [
        f"{key}={actual.get(key)!r}, expected={value!r}"
        for key, value in expected.items()
        if key
        in {
            "decayed_intensity",
            "effective_intensity",
            "lifecycle_state",
            "decay_configs",
        }
        and actual.get(key) != value
    ]


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
        subprocess.run(
            ["npm", "run", "build", "--silent"],
            cwd=ROOT / "webmcp",
            check=True,
            timeout=120,
        )

    document = json.loads(FIXTURE.read_text(encoding="utf-8"))
    failures: list[str] = []
    results: list[dict[str, Any]] = []
    for case in document["test_cases"]:
        case_id = case["id"]
        if case_id == "decay-configs-reference":
            py = {"decay_configs": _python_configs()}
            rs = {"decay_configs": json.loads(_rust("personal-configs"))}
            web = _webmcp({"mode": "configs"})
        else:
            lifecycle = case_id.startswith("lifecycle-")
            py = _python_case(case["input"], lifecycle=lifecycle)
            rs = _rust_case(case["input"], lifecycle=lifecycle)
            web = _webmcp_case(case["input"], lifecycle=lifecycle)
        for implementation, actual in (("Python", py), ("Rust", rs), ("WebMCP", web)):
            failures.extend(
                f"{case_id}: {implementation} {failure}"
                for failure in _expected_subset(actual, case["expected"])
            )
        if py != rs:
            failures.append(f"{case_id}: Python and Rust differ: {py!r} != {rs!r}")
        if py != web:
            failures.append(f"{case_id}: Python and WebMCP differ: {py!r} != {web!r}")
        results.append({"id": case_id, "python": py, "rust": rs, "webmcp": web})

    report = {
        "schema": "vcp-conformance-report/1",
        "profile": "personal-state-parity",
        "implementations": ["python", "rust", "webmcp"],
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
    print(
        f"Personal-state parity passed: {len(results)} cases across Python, Rust, and WebMCP."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
