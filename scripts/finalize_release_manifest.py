#!/usr/bin/env python3
"""Hash a release directory and generate its final manifest and checksum list."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_FILE_BYTES = 50 * 1024 * 1024
OUTPUT_NAMES = {"release-manifest.json", "SHA256SUMS"}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--version", required=True)
    args = parser.parse_args()
    root = args.directory.resolve()
    try:
        if not root.is_dir():
            raise ValueError(f"release directory does not exist: {root}")
        for name in OUTPUT_NAMES:
            path = root / name
            if path.exists():
                path.unlink()
        records: list[dict[str, object]] = []
        for path in sorted(root.rglob("*")):
            if path.is_dir():
                continue
            metadata = os.lstat(path)
            relative = path.relative_to(root).as_posix()
            if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
                raise ValueError(f"release contains a non-regular file: {relative}")
            if metadata.st_size > MAX_FILE_BYTES:
                raise ValueError(f"release file exceeds 50 MiB: {relative}")
            records.append(
                {
                    "path": relative,
                    "size_bytes": metadata.st_size,
                    "sha256": digest(path),
                }
            )
        if not records:
            raise ValueError("release directory contains no artifacts")
        checksums = "".join(
            f"{record['sha256']}  {record['path']}\n" for record in records
        )
        checksum_path = root / "SHA256SUMS"
        checksum_path.write_text(checksums, encoding="utf-8")
        records.append(
            {
                "path": "SHA256SUMS",
                "size_bytes": checksum_path.stat().st_size,
                "sha256": digest(checksum_path),
            }
        )
        git_head = subprocess.run(
            ("git", "rev-parse", "HEAD"),
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        timestamp = (
            datetime.fromisoformat(
                subprocess.run(
                    ("git", "show", "-s", "--format=%cI", "HEAD"),
                    cwd=ROOT,
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout.strip()
            )
            .isoformat()
            .replace("+00:00", "Z")
        )
        manifest = {
            "schema": "vcp-sdk-release-manifest/1",
            "version": args.version,
            "source_commit": git_head,
            "source_commit_time": timestamp,
            "manifest_scope": "all delivered files except this self-referential manifest",
            "files": records,
        }
        manifest_path = root / "release-manifest.json"
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(
        f"Finalized {len(records)} delivered files; "
        f"manifest sha256={digest(manifest_path)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
