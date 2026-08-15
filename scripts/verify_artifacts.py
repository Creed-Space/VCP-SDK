#!/usr/bin/env python3
"""Build and smoke-test every distributable VCP-SDK artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import venv
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - exercised on Python 3.10 CI
    import tomli as tomllib

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifact-evidence" / "latest.json"
MAX_ARTIFACT_BYTES = 50 * 1024 * 1024
PROJECT_VERSION = tomllib.loads((ROOT / "python" / "pyproject.toml").read_text())[
    "project"
]["version"]
PUBLIC_PYTHON_EXAMPLES = tuple(sorted((ROOT / "examples" / "python").glob("*.py")))
PUBLIC_RUST_EXAMPLES = ("parse_token", "sign_and_verify", "verify_bundle")


def run(
    command: list[str],
    *,
    cwd: Path = ROOT,
    env: dict[str, str] | None = None,
    timeout: int = 900,
) -> dict[str, Any]:
    """Run one artifact check and retain bounded evidence."""
    started = time.monotonic()
    result = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    output = result.stdout + result.stderr
    return {
        "command": command,
        "status": "passed" if result.returncode == 0 else "failed",
        "exit_code": result.returncode,
        "duration_seconds": round(time.monotonic() - started, 3),
        "output_sha256": hashlib.sha256(output.encode("utf-8")).hexdigest(),
        "output_tail": output[-4000:],
    }


def executable(environment: Path, name: str) -> Path:
    """Return a virtual-environment executable on POSIX or Windows."""
    directory = "Scripts" if os.name == "nt" else "bin"
    suffix = ".exe" if os.name == "nt" else ""
    return environment / directory / f"{name}{suffix}"


def artifact_record(path: Path, kind: str) -> dict[str, Any]:
    """Hash and size one exact artifact, rejecting Git-hostile files."""
    size = path.stat().st_size
    if size > MAX_ARTIFACT_BYTES:
        raise ValueError(f"artifact exceeds 50 MiB: {path} ({size} bytes)")
    return {
        "kind": kind,
        "filename": path.name,
        "size_bytes": size,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def exported_artifact(
    path: Path,
    kind: str,
    artifact_dir: Path | None,
    family: str,
    *,
    filename: str | None = None,
) -> dict[str, Any]:
    """Copy one verified artifact into a release family and record its digest."""
    recorded = path
    relative_path = path.name
    if artifact_dir is not None:
        destination = artifact_dir / family / (filename or path.name)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)
        recorded = destination
        relative_path = destination.relative_to(artifact_dir).as_posix()
    record = artifact_record(recorded, kind)
    record["relative_path"] = relative_path
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        help="copy every verified publishable artifact into this initially empty directory",
    )
    parser.add_argument(
        "--require-clean",
        action="store_true",
        help="reject a dirty source candidate before building release artifacts",
    )
    parser.add_argument(
        "--allow-missing-wasm-target",
        action="store_true",
        help="Record a missing local wasm32 target as unsupported; CI must not use this.",
    )
    args = parser.parse_args()
    candidate_status = run(["git", "status", "--porcelain"])["output_tail"].strip()
    if args.require_clean and candidate_status:
        parser.error("--require-clean was requested but the source candidate is dirty")
    artifact_dir = args.artifact_dir.resolve() if args.artifact_dir else None
    if artifact_dir is not None:
        if artifact_dir.exists() and any(artifact_dir.iterdir()):
            parser.error(f"--artifact-dir must be empty: {artifact_dir}")
        artifact_dir.mkdir(parents=True, exist_ok=True)
    env = {
        **os.environ,
        "CARGO_PROFILE_DEV_DEBUG": "0",
        "CARGO_INCREMENTAL": "0",
        "CARGO_TARGET_DIR": str(ROOT / "rust" / "target"),
    }
    checks: list[dict[str, Any]] = []
    artifacts: list[dict[str, Any]] = []

    with tempfile.TemporaryDirectory(prefix="vcp-artifacts-") as temporary:
        temp = Path(temporary)
        python_dist = temp / "python-dist"
        python_dist.mkdir()
        build = run(
            [
                sys.executable,
                "-m",
                "build",
                "--outdir",
                str(python_dist),
                str(ROOT / "python"),
            ],
            env=env,
        )
        build["name"] = "python-build"
        checks.append(build)
        distributions = (
            sorted(python_dist.iterdir()) if build["status"] == "passed" else []
        )
        source_distributions = [
            distribution
            for distribution in distributions
            if distribution.name.endswith(".tar.gz")
        ]
        normalize = run(
            [
                sys.executable,
                str(ROOT / "scripts" / "normalize_python_sdist.py"),
                *map(str, source_distributions),
            ],
            env=env,
        )
        normalize["name"] = "python-sdist-normalize"
        checks.append(normalize)
        metadata = run(
            [sys.executable, "-m", "twine", "check", *map(str, distributions)],
            env=env,
        )
        metadata["name"] = "python-distribution-metadata"
        checks.append(metadata)
        for distribution in distributions:
            kind = "python-wheel" if distribution.suffix == ".whl" else "python-sdist"
            artifacts.append(
                exported_artifact(distribution, kind, artifact_dir, "python")
            )
            environment = temp / f"venv-{kind}"
            venv.EnvBuilder(with_pip=True, clear=True).create(environment)
            python = executable(environment, "python")
            install = run(
                [
                    str(python),
                    "-m",
                    "pip",
                    "install",
                    "--disable-pip-version-check",
                    str(distribution),
                ],
                env=env,
            )
            install["name"] = f"{kind}-install"
            checks.append(install)
            smoke = run(
                [
                    str(python),
                    "-c",
                    (
                        "import vcp; "
                        f"assert vcp.__version__ == {PROJECT_VERSION!r}; "
                        "assert vcp.Token.parse('family.safe.guide@1.2.0').full "
                        "== 'family.safe.guide@1.2.0'; "
                        "assert vcp.compute_content_hash('Be kind.').startswith('sha256:')"
                    ),
                ],
                env=env,
            )
            smoke["name"] = f"{kind}-installed-smoke"
            checks.append(smoke)
            mcp_extra = run(
                [
                    str(python),
                    "-m",
                    "pip",
                    "install",
                    "--disable-pip-version-check",
                    f"value-context-protocol[mcp] @ {distribution.resolve().as_uri()}",
                ],
                env=env,
            )
            mcp_extra["name"] = f"{kind}-mcp-extra-install"
            checks.append(mcp_extra)
            for example in PUBLIC_PYTHON_EXAMPLES:
                example_check = run([str(python), str(example)], env=env)
                example_check["name"] = f"{kind}-installed-example-{example.stem}"
                checks.append(example_check)

        for crate, config in (
            ("vcp-core", None),
            ("vcp-cli", 'patch.crates-io.vcp-core.path="vcp-core"'),
            ("vcp-wasm", 'patch.crates-io.vcp-core.path="vcp-core"'),
        ):
            command = ["cargo", "package", "-p", crate, "--allow-dirty", "--locked"]
            if config:
                command.extend(["--config", config])
            package = run(command, cwd=ROOT / "rust", env=env)
            package["name"] = f"{crate}-crate-package"
            checks.append(package)
            crate_path = (
                ROOT
                / "rust"
                / "target"
                / "package"
                / f"{crate}-{PROJECT_VERSION}.crate"
            )
            if package["status"] == "passed" and crate_path.is_file():
                artifacts.append(
                    exported_artifact(crate_path, "rust-crate", artifact_dir, "crates")
                )
                if crate == "vcp-core":
                    unpacked = temp / "vcp-core-crate"
                    unpacked.mkdir()
                    with tarfile.open(crate_path, "r:gz") as archive:
                        archive.extractall(unpacked, filter="data")
                    packaged_root = unpacked / f"vcp-core-{PROJECT_VERSION}"
                    packaged_tests = run(
                        [
                            "cargo",
                            "test",
                            "--quiet",
                            "--locked",
                            "--manifest-path",
                            str(packaged_root / "Cargo.toml"),
                        ],
                        env=env,
                    )
                    packaged_tests["name"] = "vcp-core-packaged-tests"
                    checks.append(packaged_tests)
                    for example in PUBLIC_RUST_EXAMPLES:
                        example_check = run(
                            [
                                "cargo",
                                "run",
                                "--quiet",
                                "--locked",
                                "--manifest-path",
                                str(packaged_root / "Cargo.toml"),
                                "--example",
                                example,
                            ],
                            env=env,
                        )
                        example_check["name"] = f"vcp-core-packaged-example-{example}"
                        checks.append(example_check)

        install_root = temp / "cargo-install"
        cli_install = run(
            [
                "cargo",
                "install",
                "--path",
                str(ROOT / "rust" / "vcp-cli"),
                "--root",
                str(install_root),
                "--locked",
                "--debug",
                "--force",
            ],
            env=env,
        )
        cli_install["name"] = "rust-cli-install"
        checks.append(cli_install)
        cli = install_root / "bin" / ("vcp-cli.exe" if os.name == "nt" else "vcp-cli")
        cli_smoke = run(
            [str(cli), "canonicalize-token", "Family.Safe.Guide@1.2.0"],
            env=env,
        )
        cli_smoke["name"] = "rust-cli-installed-smoke"
        checks.append(cli_smoke)
        if cli.is_file():
            cli_name = (
                f"vcp-cli-{platform.system().lower()}-"
                f"{platform.machine().lower()}{cli.suffix}"
            )
            artifacts.append(
                exported_artifact(
                    cli,
                    "rust-cli-binary",
                    artifact_dir,
                    "binaries",
                    filename=cli_name,
                )
            )

        wasm = run(
            [
                "cargo",
                "build",
                "-p",
                "vcp-wasm",
                "--target",
                "wasm32-unknown-unknown",
                "--locked",
            ],
            cwd=ROOT / "rust",
            env=env,
        )
        wasm["name"] = "rust-wasm-target"
        if (
            wasm["status"] == "failed"
            and args.allow_missing_wasm_target
            and "target may not be installed" in wasm["output_tail"]
        ):
            wasm["status"] = "unsupported"
            wasm["reason"] = "Local Rust installation lacks wasm32-unknown-unknown"
        checks.append(wasm)
        wasm_path = (
            ROOT
            / "rust"
            / "target"
            / "wasm32-unknown-unknown"
            / "debug"
            / "vcp_wasm.wasm"
        )
        if wasm["status"] == "passed" and wasm_path.is_file():
            artifacts.append(
                exported_artifact(
                    wasm_path, "rust-wasm-binary", artifact_dir, "binaries"
                )
            )

        packed_smoke = run(["npm", "run", "test:packed"], cwd=ROOT / "webmcp", env=env)
        packed_smoke["name"] = "webmcp-packed-smoke"
        checks.append(packed_smoke)
        npm_dist = temp / "npm-dist"
        npm_dist.mkdir()
        npm_pack = run(
            [
                "npm",
                "pack",
                "--ignore-scripts",
                "--json",
                "--pack-destination",
                str(npm_dist),
            ],
            cwd=ROOT / "webmcp",
            env=env,
        )
        npm_pack["name"] = "webmcp-pack"
        checks.append(npm_pack)
        tarballs = sorted(npm_dist.glob("*.tgz"))
        if npm_pack["status"] == "passed" and len(tarballs) == 1:
            artifacts.append(
                exported_artifact(tarballs[0], "npm-tarball", artifact_dir, "npm")
            )

    failed = [check["name"] for check in checks if check["status"] == "failed"]
    report = {
        "schema": "vcp-artifact-verification-report/1",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "candidate": {
            "git_head": run(["git", "rev-parse", "HEAD"])["output_tail"].strip(),
            "dirty": bool(candidate_status),
        },
        "environment": {
            "platform": platform.platform(),
            "python": platform.python_version(),
        },
        "artifacts": artifacts,
        "checks": checks,
        "summary": {
            "artifacts": len(artifacts),
            "checks": len(checks),
            "passed": sum(check["status"] == "passed" for check in checks),
            "unsupported": sum(check["status"] == "unsupported" for check in checks),
            "failed": len(failed),
        },
        "failures": failed,
        "attestation": "unsigned-local-result",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        f"Artifact verification: {report['summary']['artifacts']} artifacts, "
        f"{report['summary']['passed']} checks passed, "
        f"{report['summary']['unsupported']} unsupported, {len(failed)} failed."
    )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
