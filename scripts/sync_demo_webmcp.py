#!/usr/bin/env python3
"""Generate and verify the Demo's vendored WebMCP adapter from VCP-SDK."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

SDK_ROOT = Path(__file__).resolve().parents[1]

MAPPINGS = {
    SDK_ROOT / "webmcp/src/types.ts": "src/lib/vcp-webmcp-sdk/types.ts",
    SDK_ROOT / "webmcp/src/tools.ts": "src/lib/vcp-webmcp-sdk/tools.ts",
    SDK_ROOT / "webmcp/src/registration.ts": "src/lib/vcp-webmcp-sdk/registration.ts",
    SDK_ROOT / "webmcp/src/polyfill.ts": "src/lib/webmcp/polyfill.ts",
    SDK_ROOT / "webmcp/tests/registration.test.ts": (
        "src/lib/vcp-webmcp-sdk/registration.test.ts"
    ),
    SDK_ROOT / "webmcp/tests/polyfill.test.ts": "src/lib/webmcp/polyfill.test.ts",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def transformed(source: Path) -> bytes:
    text = source.read_text(encoding="utf-8")
    text = text.replace("'./types.js'", "'./types'")
    text = text.replace("'./tools.js'", "'./tools'")
    text = text.replace("'../src/registration.js'", "'./registration'")
    text = text.replace("'../src/types.js'", "'./types'")
    text = text.replace("'../src/polyfill.js'", "'./polyfill'")
    return text.encode("utf-8")


def expected_manifest(demo: Path) -> dict[str, object]:
    files = []
    for source, relative_target in MAPPINGS.items():
        source_bytes = source.read_bytes()
        target_bytes = transformed(source)
        files.append(
            {
                "sdk_path": source.relative_to(SDK_ROOT).as_posix(),
                "demo_path": relative_target,
                "sdk_sha256": sha256(source_bytes),
                "demo_sha256": sha256(target_bytes),
            }
        )
    return {
        "schema": "vcp-webmcp-source-sync/1",
        "authority": "VCP-SDK/webmcp",
        "generated": True,
        "files": files,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", type=Path, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()

    demo = args.demo.expanduser().resolve()
    if not (demo / ".git").exists():
        parser.error(f"Demo must be a Git worktree root: {demo}")

    manifest = expected_manifest(demo)
    manifest_path = demo / "src/lib/vcp-webmcp-sdk/upstream-sync.json"
    expected_manifest_bytes = (
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")

    failures: list[str] = []
    for source, relative_target in MAPPINGS.items():
        target = demo / relative_target
        expected = transformed(source)
        if args.write:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(expected)
        elif not target.is_file() or target.read_bytes() != expected:
            failures.append(relative_target)

    if args.write:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_bytes(expected_manifest_bytes)
    elif (
        not manifest_path.is_file()
        or manifest_path.read_bytes() != expected_manifest_bytes
    ):
        failures.append(manifest_path.relative_to(demo).as_posix())

    if failures:
        print("WebMCP source drift:")
        for failure in failures:
            print(f"  {failure}")
        return 1

    verb = "generated" if args.write else "verified"
    print(f"Demo WebMCP adapter {verb}: {len(MAPPINGS)} synchronized files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
