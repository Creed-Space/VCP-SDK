#!/usr/bin/env python3
"""Run every checked VCP conformance profile and emit one aggregate report."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.jsonschema_formats import strict_format_checker

REPORT_DIR = ROOT / "conformance" / "reports"
DEFAULT_REPORT = REPORT_DIR / "latest.json"
SCHEMA = ROOT / "schemas" / "vcp-conformance-aggregate-report.schema.json"
COVERAGE = ROOT / "conformance" / "coverage-manifest.json"

RUNNERS: tuple[tuple[str, str, bool], ...] = (
    ("agent-runtime-profile", "agent_runtime_profile.py", False),
    ("csm1", "csm1_parity.py", True),
    ("identity", "identity_parity.py", True),
    ("transport", "transport_parity.py", True),
    ("context", "context_parity.py", True),
    ("personal", "personal_parity.py", True),
    ("capability-negotiation", "negotiation_parity.py", True),
    ("consensus", "consensus_parity.py", True),
    ("persona", "persona_parity.py", True),
    ("composition", "composition_parity.py", True),
    ("interoperability", "interop_parity.py", True),
    ("messaging", "messaging_conformance.py", False),
    ("state-machine", "state_machine_conformance.py", False),
    ("competence", "competence_conformance.py", False),
    ("relational-and-torch", "relational_torch_parity.py", False),
    ("security-policy", "security_parity.py", False),
)


def command_version(command: list[str]) -> str:
    """Return one stable first-line tool version or an explicit absence."""
    try:
        result = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=15,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as error:
        return f"unavailable: {type(error).__name__}"
    return (result.stdout or result.stderr).strip().splitlines()[0]


def source_fingerprint() -> str:
    """Hash all candidate source files without including build or report outputs."""
    listed = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        capture_output=True,
        check=True,
    ).stdout.split(b"\0")
    excluded_parts = {
        ".git",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        "node_modules",
        "target",
        "__pycache__",
        "reports",
    }
    digest = hashlib.sha256()
    for raw_path in sorted(item for item in listed if item):
        relative = Path(os.fsdecode(raw_path))
        if excluded_parts.intersection(relative.parts):
            continue
        path = ROOT / relative
        if not path.is_file():
            continue
        digest.update(relative.as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
        digest.update(b"\0")
    return digest.hexdigest()


def run_profile(
    name: str,
    script: str,
    skip_build: bool,
    env: dict[str, str],
) -> dict[str, Any]:
    """Run one profile, retaining bounded diagnostics and its structured report."""
    report_path = REPORT_DIR / "profiles" / f"{name}.json"
    report_path.unlink(missing_ok=True)
    command = [
        sys.executable,
        str(ROOT / "conformance" / "runners" / script),
    ]
    if skip_build:
        command.append("--skip-build")
    command.extend(["--report", str(report_path)])
    started = time.monotonic()
    result = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=600,
        check=False,
        env=env,
    )
    duration = time.monotonic() - started
    output = result.stdout + result.stderr
    structured = None
    if report_path.is_file():
        try:
            structured = json.loads(report_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            structured = None
    valid_structured = (
        isinstance(structured, dict)
        and structured.get("schema") == "vcp-conformance-report/1"
        and not structured.get("failures")
    )
    passed = result.returncode == 0 and valid_structured
    return {
        "name": name,
        "status": "passed" if passed else "failed",
        "command": [str(item) for item in command],
        "duration_seconds": round(duration, 3),
        "output_sha256": hashlib.sha256(output.encode("utf-8")).hexdigest(),
        "output_tail": output[-4000:],
        "report": structured,
    }


def run_webmcp(env: dict[str, str]) -> dict[str, Any]:
    """Run the installed npm tarball surface check."""
    command = ["npm", "run", "test:packed"]
    started = time.monotonic()
    result = subprocess.run(
        command,
        cwd=ROOT / "webmcp",
        text=True,
        capture_output=True,
        timeout=300,
        check=False,
        env=env,
    )
    output = result.stdout + result.stderr
    passed = result.returncode == 0 and "Packed WebMCP artifact passed:" in output
    report = {
        "schema": "vcp-conformance-report/1",
        "profile": "webmcp-packed-artifact",
        "implementations": {"webmcp": "passed" if passed else "failed"},
        "fixture_sha256": {
            path.relative_to(ROOT).as_posix(): hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
            for path in (
                ROOT / "webmcp" / "package.json",
                ROOT / "webmcp" / "package-lock.json",
                ROOT / "webmcp" / "scripts" / "test-packed.mjs",
            )
        },
        "summary": {"cases": 1, "failures": 0 if passed else 1},
        "failures": [] if passed else ["packed npm artifact check failed"],
        "attestation": "unsigned-local-result",
    }
    return {
        "name": "webmcp-packed-artifact",
        "status": "passed" if passed else "failed",
        "command": command,
        "duration_seconds": round(time.monotonic() - started, 3),
        "output_sha256": hashlib.sha256(output.encode("utf-8")).hexdigest(),
        "output_tail": output[-4000:],
        "report": report,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--skip-webmcp", action="store_true")
    parser.add_argument("--skip-build", action="store_true")
    args = parser.parse_args()
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    (REPORT_DIR / "profiles").mkdir(parents=True, exist_ok=True)

    coverage_check = subprocess.run(
        [sys.executable, "scripts/generate_conformance_coverage.py", "--check"],
        cwd=ROOT,
        check=False,
    )
    if coverage_check.returncode:
        return coverage_check.returncode

    env = {
        **os.environ,
        "CARGO_PROFILE_DEV_DEBUG": "0",
        "CARGO_INCREMENTAL": "0",
        "PYTHONHASHSEED": "0",
    }
    profiles: list[dict[str, Any]] = []
    if not args.skip_build:
        build = subprocess.run(
            ["cargo", "build", "--quiet", "-p", "vcp-cli"],
            cwd=ROOT / "rust",
            text=True,
            capture_output=True,
            timeout=600,
            check=False,
            env=env,
        )
        if build.returncode:
            output = build.stdout + build.stderr
            profiles.append(
                {
                    "name": "rust-cli-build",
                    "status": "failed",
                    "command": ["cargo", "build", "--quiet", "-p", "vcp-cli"],
                    "duration_seconds": 0.0,
                    "output_sha256": hashlib.sha256(output.encode()).hexdigest(),
                    "output_tail": output[-4000:],
                    "report": None,
                }
            )
    if not profiles and not args.skip_build and not args.skip_webmcp:
        # The context, personal, negotiation and relational profiles execute the
        # built WebMCP modules under webmcp/dist; build once here because every
        # profile runner is invoked with --skip-build.
        build = subprocess.run(
            ["npm", "run", "build", "--silent"],
            cwd=ROOT / "webmcp",
            text=True,
            capture_output=True,
            timeout=600,
            check=False,
            env=env,
        )
        if build.returncode:
            output = build.stdout + build.stderr
            profiles.append(
                {
                    "name": "webmcp-build",
                    "status": "failed",
                    "command": ["npm", "run", "build", "--silent"],
                    "duration_seconds": 0.0,
                    "output_sha256": hashlib.sha256(output.encode()).hexdigest(),
                    "output_tail": output[-4000:],
                    "report": None,
                }
            )
    if not profiles:
        for name, script, skip_build in RUNNERS:
            record = run_profile(name, script, skip_build, env)
            profiles.append(record)
            print(f"{record['status'].upper()}: {name}")
        if not args.skip_webmcp:
            record = run_webmcp(env)
            profiles.append(record)
            print(f"{record['status'].upper()}: {record['name']}")

    coverage = json.loads(COVERAGE.read_text(encoding="utf-8"))
    git_head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()
    dirty = bool(
        subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        ).stdout
    )
    failed = sum(item["status"] == "failed" for item in profiles)
    generated_at = datetime.now(timezone.utc)
    source_sha256 = source_fingerprint()
    claim = {
        "status": "local-source-evidence",
        "publishable": False,
        "protocol": "VCP 3.1 source baseline with labelled candidates",
        "profile": "project-controlled aggregate runner",
        "implementation_version": "4.2.0 source candidate",
        "source_sha256": source_sha256,
        "issued_at": generated_at.isoformat().replace("+00:00", "Z"),
        "expires_at": (generated_at + timedelta(days=30))
        .isoformat()
        .replace("+00:00", "Z"),
        "revocation_status_url": (
            "https://github.com/Creed-Space/VCP-SDK/blob/main/"
            "release/publication-state.json"
        ),
        "superseded_by": None,
        "revoked_at": None,
    }
    report = {
        "schema": "vcp-conformance-aggregate-report/1",
        "generated_at": generated_at.isoformat().replace("+00:00", "Z"),
        "candidate": {
            "git_head": git_head,
            "dirty": dirty,
            "source_sha256": source_sha256,
        },
        "environment": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "rustc": command_version(["rustc", "--version"]),
            "node": command_version(["node", "--version"]),
        },
        "coverage_manifest": {
            "path": COVERAGE.relative_to(ROOT).as_posix(),
            "sha256": hashlib.sha256(COVERAGE.read_bytes()).hexdigest(),
            "fixture_count": coverage["summary"]["fixture_count"],
            "vector_count": coverage["summary"]["vector_count"],
        },
        "profiles": profiles,
        "summary": {
            "profiles": len(profiles),
            "passed": len(profiles) - failed,
            "failed": failed,
        },
        "claim": claim,
        "attestation": "unsigned-local-result",
    }
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    errors = sorted(
        Draft202012Validator(
            schema, format_checker=strict_format_checker()
        ).iter_errors(report),
        key=lambda error: list(error.path),
    )
    if errors:
        print(f"Aggregate report schema failure: {errors[0].message}", file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    badge = {
        "schemaVersion": 1,
        "label": "VCP local suite",
        "message": (
            f"{report['summary']['passed']}/{report['summary']['profiles']} "
            "project-controlled profiles"
        ),
        "color": "lightgrey" if not failed else "critical",
        "cacheSeconds": 300,
        "claim": claim,
    }
    (args.output.parent / "badge.json").write_text(
        json.dumps(badge, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        f"Aggregate conformance: {report['summary']['passed']} passed, "
        f"{failed} failed; report={args.output}"
    )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
