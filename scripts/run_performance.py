#!/usr/bin/env python3
"""Run cross-language performance probes and enforce coarse safety envelopes."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import resource
import subprocess
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python" / "src"))


def command(*parts: str, cwd: Path = ROOT) -> str:
    result = subprocess.run(
        parts,
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def source_digest() -> str:
    digest = hashlib.sha256()
    tracked = command(
        "git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"
    ).split("\0")
    for relative in sorted(path for path in tracked if path):
        path = ROOT / relative
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        if not path.exists():
            digest.update(b"<deleted>\0")
            continue
        if not path.is_file():
            digest.update(b"<non-file>\0")
            continue
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def summarize(name: str, samples_ns: list[int]) -> dict[str, int | float | str]:
    samples_ns.sort()
    count = len(samples_ns)
    total_ns = sum(samples_ns)
    p95_index = max(int(count * 0.95 + 0.999_999) - 1, 0)
    return {
        "name": name,
        "iterations": count,
        "ops_per_second": count / (total_ns / 1_000_000_000),
        "p50_us": samples_ns[count // 2] / 1_000,
        "p95_us": samples_ns[p95_index] / 1_000,
    }


def measure(
    name: str, operation: Callable[[], object], iterations: int
) -> dict[str, Any]:
    for _ in range(min(iterations, 1_000)):
        operation()
    samples: list[int] = []
    for _ in range(iterations):
        started = time.perf_counter_ns()
        operation()
        samples.append(time.perf_counter_ns() - started)
    return summarize(name, samples)


def python_metrics(iterations: int, hash_iterations: int) -> list[dict[str, Any]]:
    from vcp.canonicalize import canonicalize_manifest, compute_content_hash
    from vcp.identity import Token
    from vcp.orchestrator import _verify_ed25519_signature
    from vcp.semantics.csm1 import CSM1Code

    payload = "vcp-performance-payload\n" * 2_800
    token = Token.parse("company.product.safety.review.workflow.agent")
    large_manifest = {
        "bundle": {f"field_{index:04d}": "v" * 80 for index in range(512)},
        "signature": {"value": "excluded"},
    }
    private_key = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
    public_key = private_key.public_key().public_bytes_raw()
    message = canonicalize_manifest({"bundle": {"id": "verification-probe"}})
    signature = private_key.sign(message)
    verify_iterations = max(iterations // 20, 100)
    return [
        measure(
            "python_csm1_roundtrip",
            lambda: CSM1Code.parse("Z5+P+T:SEC@4.2.0").encode(),
            iterations,
        ),
        measure(
            "python_content_hash_64k",
            lambda: compute_content_hash(payload),
            hash_iterations,
        ),
        measure(
            "python_scope_glob_6",
            lambda: token.matches_pattern("company.*.safety.**"),
            iterations,
        ),
        measure(
            "python_manifest_canonicalization_48k",
            lambda: canonicalize_manifest(large_manifest),
            hash_iterations,
        ),
        measure(
            "python_ed25519_verification",
            lambda: _verify_ed25519_signature(public_key, message, signature),
            verify_iterations,
        ),
    ]


def peak_rss_mb() -> float:
    usage = max(
        resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
    )
    divisor = 1024 * 1024 if sys.platform == "darwin" else 1024
    return usage / divisor


def run_probe(command_parts: list[str], cwd: Path) -> list[dict[str, Any]]:
    output = command(*command_parts, cwd=cwd)
    return list(json.loads(output.splitlines()[-1])["metrics"])


def enforce(result: dict[str, Any], envelope: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if result["wall_seconds"] > envelope["max_wall_seconds"]:
        failures.append(
            f"wall_seconds {result['wall_seconds']:.3f} exceeds {envelope['max_wall_seconds']}"
        )
    if result["peak_rss_mb"] > envelope["max_peak_rss_mb"]:
        failures.append(
            f"peak_rss_mb {result['peak_rss_mb']:.1f} exceeds {envelope['max_peak_rss_mb']}"
        )
    by_name = {metric["name"]: metric for metric in result["metrics"]}
    for name, limits in envelope["metrics"].items():
        metric = by_name.get(name)
        if metric is None:
            failures.append(f"missing metric {name}")
            continue
        if metric["ops_per_second"] < limits["min_ops_per_second"]:
            failures.append(
                f"{name} ops_per_second {metric['ops_per_second']:.1f} is below "
                f"{limits['min_ops_per_second']}"
            )
        if metric["p95_us"] > limits["max_p95_us"]:
            failures.append(
                f"{name} p95_us {metric['p95_us']:.1f} exceeds {limits['max_p95_us']}"
            )
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=("smoke", "full"), default="smoke")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--skip-build", action="store_true")
    args = parser.parse_args()

    iterations = 20_000 if args.profile == "smoke" else 100_000
    hash_iterations = 25 if args.profile == "smoke" else 100
    if not args.skip_build:
        command(
            "cargo",
            "build",
            "--release",
            "-p",
            "vcp-core",
            "--example",
            "performance_probe",
            cwd=ROOT / "rust",
        )
        command("npm", "run", "build", cwd=ROOT / "webmcp")

    started = time.perf_counter()
    metrics = python_metrics(iterations, hash_iterations)
    metrics.extend(
        run_probe(
            [
                str(
                    ROOT
                    / "rust"
                    / "target"
                    / "release"
                    / "examples"
                    / "performance_probe"
                ),
                "--iterations",
                str(iterations),
                "--hash-iterations",
                str(hash_iterations),
            ],
            ROOT,
        )
    )
    metrics.extend(
        run_probe(
            [
                "node",
                "scripts/performance-probe.mjs",
                "--iterations",
                str(iterations),
            ],
            ROOT / "webmcp",
        )
    )
    wall_seconds = time.perf_counter() - started
    commit = command("git", "rev-parse", "HEAD")
    dirty = bool(command("git", "status", "--porcelain"))
    result: dict[str, Any] = {
        "schema_version": 1,
        "candidate": {
            "commit": commit,
            "source_sha256": source_digest(),
            "dirty": dirty,
        },
        "profile": args.profile,
        "environment": {
            "os": platform.platform(),
            "machine": platform.machine(),
            "python": platform.python_version(),
            "node": command("node", "--version"),
            "rustc": command("rustc", "--version"),
        },
        "wall_seconds": wall_seconds,
        "peak_rss_mb": peak_rss_mb(),
        "metrics": metrics,
    }
    envelopes = json.loads((ROOT / "performance" / "envelopes.json").read_text())
    failures = enforce(result, envelopes["profiles"][args.profile])
    result["passed"] = not failures
    result["failures"] = failures

    output = args.output if args.output.is_absolute() else ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
