#!/usr/bin/env python3
"""Run one evidence-producing validation pass across the VCP repositories."""

from __future__ import annotations

import argparse
import shlex
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Check:
    repository: str
    command: tuple[str, ...]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate one exact VCP Demo, Spec, and SDK candidate set."
    )
    parser.add_argument("--demo", type=Path, required=True)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--sdk", type=Path, required=True)
    parser.add_argument(
        "--python",
        default=sys.executable,
        help="Python executable with the Spec and SDK validation dependencies installed.",
    )
    parser.add_argument(
        "--mode",
        choices=("core", "full"),
        default="full",
        help="core runs integrated behavior checks; full also builds packages and runs audits.",
    )
    return parser.parse_args()


def git_output(repository: Path, *arguments: str) -> str:
    result = subprocess.run(
        ("git", *arguments),
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def validate_repository_path(label: str, path: Path) -> Path:
    resolved = path.expanduser().resolve()
    if not resolved.is_dir():
        raise ValueError(f"{label} repository is not a directory: {resolved}")
    top = Path(git_output(resolved, "rev-parse", "--show-toplevel")).resolve()
    if top != resolved:
        raise ValueError(
            f"{label} path is not its Git root: {resolved} (root is {top})"
        )
    return resolved


def checks_for(mode: str, python: str) -> list[Check]:
    spec_checks = [
        Check("spec", ("make", "check", f"PYTHON={python}")),
    ]
    sdk_checks = [
        Check(
            "sdk",
            (
                "make",
                "all" if mode == "full" else "validate",
                f"PYTHON={python}",
            ),
        ),
        Check(
            "sdk",
            (
                "make",
                "schema-sync",
                "SPEC={spec}",
                f"PYTHON={python}",
            ),
        ),
        Check(
            "sdk",
            (
                python,
                "scripts/validate_public_contract.py",
                "--demo",
                "{demo}",
                "--spec",
                "{spec}",
                "--sdk",
                "{sdk}",
            ),
        ),
    ]
    if mode == "full":
        sdk_checks[1:1] = [
            Check("sdk", ("make", "property", f"PYTHON={python}")),
            Check("sdk", ("make", "performance-smoke", f"PYTHON={python}")),
            Check(
                "sdk",
                (
                    "cargo",
                    "check",
                    "--locked",
                    "--manifest-path",
                    "rust/fuzz/Cargo.toml",
                ),
            ),
        ]
    demo_checks = [
        Check("demo", ("npm", "run", "check:repo")),
        Check("demo", ("npm", "run", "test:hook")),
        Check("demo", ("npm", "run", "lint")),
        Check("demo", ("npm", "run", "check")),
        Check("demo", ("npm", "test")),
        Check("demo", ("npm", "run", "check:links")),
        Check("demo", ("npm", "run", "build")),
        Check("demo", ("npm", "run", "check:budget")),
    ]
    checks = [*spec_checks, *sdk_checks, *demo_checks]
    if mode == "full":
        checks.extend(
            [
                Check("demo", ("npm", "run", "test:e2e")),
                Check("demo", ("actionlint", "-no-color")),
                Check("spec", ("actionlint", "-no-color")),
                Check("sdk", ("actionlint", "-no-color")),
                Check("spec", ("make", "audits", f"PYTHON={python}")),
                Check("demo", ("npm", "audit", "--audit-level=high")),
                Check(
                    "spec",
                    (
                        "gitleaks",
                        "detect",
                        "--source",
                        ".",
                        "--no-git",
                        "--redact",
                        "--config",
                        ".gitleaks.toml",
                    ),
                ),
                Check(
                    "sdk",
                    (
                        "gitleaks",
                        "detect",
                        "--source",
                        ".",
                        "--no-git",
                        "--redact",
                        "--config",
                        ".gitleaks.toml",
                    ),
                ),
                Check(
                    "demo",
                    (
                        "gitleaks",
                        "detect",
                        "--source",
                        ".",
                        "--no-git",
                        "--redact",
                        "--config",
                        ".gitleaks.toml",
                    ),
                ),
            ]
        )
    checks.extend(
        Check(name, ("git", "diff", "--check")) for name in ("spec", "sdk", "demo")
    )
    return checks


def main() -> int:
    args = parse_args()
    try:
        repositories = {
            "demo": validate_repository_path("Demo", args.demo),
            "spec": validate_repository_path("Spec", args.spec),
            "sdk": validate_repository_path("SDK", args.sdk),
        }
    except (ValueError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print("VCP ecosystem candidate identity")
    for label in ("demo", "spec", "sdk"):
        repository = repositories[label]
        head = git_output(repository, "rev-parse", "HEAD")
        dirty = bool(git_output(repository, "status", "--porcelain"))
        print(f"  {label}: {head} dirty={str(dirty).lower()} path={repository}")

    if args.mode == "full":
        missing = [
            tool
            for tool in ("cargo-audit", "actionlint", "gitleaks")
            if shutil.which(tool) is None
        ]
        if missing:
            print(
                "ERROR: full mode requires these validation tools on PATH: "
                + ", ".join(missing),
                file=sys.stderr,
            )
            return 2

    started = time.monotonic()
    checks = checks_for(args.mode, args.python)
    for index, check in enumerate(checks, start=1):
        repository = repositories[check.repository]
        substitutions = {
            "SPEC={spec}": f"SPEC={repositories['spec']}",
            "{demo}": str(repositories["demo"]),
            "{spec}": str(repositories["spec"]),
            "{sdk}": str(repositories["sdk"]),
        }
        command = tuple(
            substitutions.get(argument, argument) for argument in check.command
        )
        print(
            f"[{index}/{len(checks)}] {check.repository}: {shlex.join(command)}",
            flush=True,
        )
        result = subprocess.run(command, cwd=repository, check=False)
        if result.returncode:
            print(
                f"FAILED: {check.repository} command exited {result.returncode}",
                file=sys.stderr,
            )
            return result.returncode

    elapsed = time.monotonic() - started
    print(
        f"VCP ecosystem {args.mode} validation passed: "
        f"{len(checks)} commands in {elapsed:.1f}s."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
