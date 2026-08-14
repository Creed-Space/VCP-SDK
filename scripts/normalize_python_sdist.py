#!/usr/bin/env python3
"""Rewrite Python source distributions with deterministic archive metadata."""

from __future__ import annotations

import argparse
import gzip
import io
import os
import stat
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
MAX_MEMBER_BYTES = 50 * 1024 * 1024
MAX_ARCHIVE_BYTES = 100 * 1024 * 1024


def source_epoch(explicit: int | None) -> int:
    """Return an explicit, environmental, or source-commit epoch."""
    value = explicit
    if value is None and os.environ.get("SOURCE_DATE_EPOCH"):
        value = int(os.environ["SOURCE_DATE_EPOCH"])
    if value is None:
        value = int(
            subprocess.run(
                ("git", "show", "-s", "--format=%ct", "HEAD"),
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
        )
    if not 0 <= value <= 0xFFFF_FFFF:
        raise ValueError("epoch must fit the unsigned 32-bit gzip timestamp field")
    return value


def safe_name(name: str) -> str:
    """Validate and return one portable archive member name."""
    candidate = PurePosixPath(name)
    if (
        candidate.is_absolute()
        or ".." in candidate.parts
        or not candidate.parts
        or "\\" in name
    ):
        raise ValueError(f"unsafe source-distribution member: {name!r}")
    return candidate.as_posix()


def normalized_members(path: Path, epoch: int) -> list[tuple[tarfile.TarInfo, bytes]]:
    """Read and normalize a bounded source distribution."""
    if not path.is_file() or not path.name.endswith(".tar.gz"):
        raise ValueError(f"expected an existing .tar.gz source distribution: {path}")
    if path.stat().st_size > MAX_ARCHIVE_BYTES:
        raise ValueError(f"source distribution exceeds 100 MiB: {path}")
    records: list[tuple[tarfile.TarInfo, bytes]] = []
    seen: set[str] = set()
    total_size = 0
    with tarfile.open(path, mode="r:gz") as archive:
        for original in archive.getmembers():
            name = safe_name(original.name)
            if name in seen:
                raise ValueError(f"duplicate source-distribution member: {name}")
            seen.add(name)
            if not (original.isdir() or original.isfile()):
                raise ValueError(f"unsupported source-distribution member type: {name}")
            if original.size > MAX_MEMBER_BYTES:
                raise ValueError(f"source-distribution member exceeds 50 MiB: {name}")
            data = b""
            if original.isfile():
                stream = archive.extractfile(original)
                if stream is None:
                    raise ValueError(
                        f"could not read source-distribution member: {name}"
                    )
                data = stream.read(MAX_MEMBER_BYTES + 1)
                if len(data) != original.size:
                    raise ValueError(
                        f"source-distribution member size mismatch: {name}"
                    )
                total_size += len(data)
                if total_size > MAX_ARCHIVE_BYTES:
                    raise ValueError("expanded source distribution exceeds 100 MiB")
            info = tarfile.TarInfo(name)
            info.type = tarfile.DIRTYPE if original.isdir() else tarfile.REGTYPE
            info.size = len(data)
            info.mode = 0o755 if original.isdir() or original.mode & 0o111 else 0o644
            info.uid = 0
            info.gid = 0
            info.uname = "root"
            info.gname = "root"
            info.mtime = epoch
            records.append((info, data))
    if not records:
        raise ValueError("source distribution is empty")
    return sorted(records, key=lambda item: item[0].name)


def normalize(path: Path, epoch: int) -> None:
    """Atomically replace one sdist with a deterministic gzip and tar stream."""
    records = normalized_members(path, epoch)
    original_mode = stat.S_IMODE(path.stat().st_mode)
    with tempfile.NamedTemporaryFile(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent, delete=False
    ) as temporary:
        temporary_path = Path(temporary.name)
        with (
            gzip.GzipFile(
                filename="",
                mode="wb",
                compresslevel=9,
                fileobj=temporary,
                mtime=epoch,
            ) as zipped,
            tarfile.open(
                fileobj=zipped, mode="w", format=tarfile.PAX_FORMAT
            ) as archive,
        ):
            for info, data in records:
                archive.addfile(info, io.BytesIO(data) if info.isfile() else None)
    try:
        temporary_path.chmod(original_mode)
        os.replace(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archives", nargs="+", type=Path)
    parser.add_argument("--epoch", type=int)
    args = parser.parse_args()
    try:
        epoch = source_epoch(args.epoch)
        for archive in args.archives:
            normalize(archive.resolve(), epoch)
    except (
        OSError,
        ValueError,
        tarfile.TarError,
        subprocess.CalledProcessError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Normalized {len(args.archives)} Python sdist(s) at epoch {epoch}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
