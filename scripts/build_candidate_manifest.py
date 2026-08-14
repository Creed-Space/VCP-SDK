#!/usr/bin/env python3
"""Build a deterministic source inventory for one VCP ecosystem candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

MAX_FILE_BYTES = 50 * 1024 * 1024


def git_bytes(repository: Path, *arguments: str) -> bytes:
    return subprocess.run(
        ("git", *arguments),
        cwd=repository,
        check=True,
        capture_output=True,
    ).stdout


def git_text(repository: Path, *arguments: str) -> str:
    return git_bytes(repository, *arguments).decode("utf-8").strip()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def validate_repository(label: str, path: Path) -> Path:
    repository = path.expanduser().resolve()
    if not repository.is_dir():
        raise ValueError(f"{label} is not a directory: {repository}")
    root = Path(git_text(repository, "rev-parse", "--show-toplevel")).resolve()
    if root != repository:
        raise ValueError(f"{label} is not its Git root: {repository}")
    return repository


def candidate_paths(repository: Path) -> list[str]:
    raw = git_bytes(
        repository,
        "ls-files",
        "-z",
        "--cached",
        "--others",
        "--exclude-standard",
    )
    return sorted(item.decode("utf-8") for item in raw.split(b"\0") if item)


def inventory_repository(
    name: str, repository: Path, require_clean: bool
) -> dict[str, Any]:
    status = git_text(repository, "status", "--porcelain=v1", "--untracked-files=all")
    if require_clean and status:
        raise ValueError(f"{name} is dirty but --require-clean was requested")

    records: list[dict[str, Any]] = []
    total_bytes = 0
    for relative in candidate_paths(repository):
        path = repository / relative
        if not path.exists() and not path.is_symlink():
            continue
        metadata = os.lstat(path)
        if stat.S_ISLNK(metadata.st_mode):
            raise ValueError(f"{name} candidate contains a source symlink: {relative}")
        if not stat.S_ISREG(metadata.st_mode):
            raise ValueError(f"{name} candidate contains a special file: {relative}")
        if metadata.st_size > MAX_FILE_BYTES:
            raise ValueError(f"{name} candidate file exceeds 50 MiB: {relative}")
        record = {
            "path": relative,
            "mode": f"{stat.S_IMODE(metadata.st_mode):04o}",
            "size": metadata.st_size,
            "sha256": sha256_file(path),
        }
        total_bytes += metadata.st_size
        records.append(record)

    deleted = sorted(
        item.decode("utf-8")
        for item in git_bytes(repository, "ls-files", "-z", "--deleted").split(b"\0")
        if item
    )
    digest = hashlib.sha256()
    for record in records:
        digest.update(canonical_bytes(record) + b"\n")
    for relative in deleted:
        digest.update(canonical_bytes({"deleted": relative}) + b"\n")

    return {
        "repository": name,
        "path": str(repository),
        "branch": git_text(repository, "branch", "--show-current"),
        "commit": git_text(repository, "rev-parse", "HEAD"),
        "dirty": bool(status),
        "status": status.splitlines(),
        "working_tree_sha256": digest.hexdigest(),
        "source_file_count": len(records),
        "source_bytes": total_bytes,
        "deleted_tracked_paths": deleted,
        "files": records,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", type=Path, required=True)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--sdk", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--require-clean",
        action="store_true",
        help="reject repositories with tracked or untracked candidate changes",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        repositories = {
            "VCP-Demo-Site": validate_repository("Demo", args.demo),
            "VCP-Spec": validate_repository("Spec", args.spec),
            "VCP-SDK": validate_repository("SDK", args.sdk),
        }
        output = args.output.expanduser().resolve()
        for name, repository in repositories.items():
            if output == repository or repository in output.parents:
                raise ValueError(
                    f"manifest output must be outside candidate repositories ({name})"
                )

        inventories = [
            inventory_repository(name, repository, args.require_clean)
            for name, repository in repositories.items()
        ]
        combined = hashlib.sha256()
        for inventory in inventories:
            combined.update(inventory["repository"].encode("utf-8"))
            combined.update(b"\0")
            combined.update(inventory["working_tree_sha256"].encode("ascii"))
            combined.update(b"\n")

        document = {
            "schema": "vcp-candidate-manifest/1.0.0",
            "generated_at": datetime.now(UTC).isoformat(),
            "combined_candidate_sha256": combined.hexdigest(),
            "repositories": inventories,
        }
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    except (OSError, UnicodeError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(f"candidate manifest: {output}")
    print(f"combined candidate SHA-256: {document['combined_candidate_sha256']}")
    print(f"manifest SHA-256: {sha256_file(output)}")
    for inventory in inventories:
        print(
            f"{inventory['repository']}: commit={inventory['commit']} "
            f"tree={inventory['working_tree_sha256']} dirty={inventory['dirty']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
