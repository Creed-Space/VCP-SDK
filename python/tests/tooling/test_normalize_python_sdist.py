from __future__ import annotations

import gzip
import io
import subprocess
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NORMALIZER = ROOT / "scripts" / "normalize_python_sdist.py"


def make_sdist(path: Path, archive_mtime: int, member_mtime: int, uid: int) -> None:
    with (
        path.open("wb") as raw,
        gzip.GzipFile(
            filename=path.name,
            fileobj=raw,
            mode="wb",
            mtime=archive_mtime,
        ) as zipped,
        tarfile.open(fileobj=zipped, mode="w") as archive,
    ):
        directory = tarfile.TarInfo("example-1.0")
        directory.type = tarfile.DIRTYPE
        directory.mode = 0o775
        directory.uid = uid
        directory.gid = uid
        directory.mtime = member_mtime
        archive.addfile(directory)
        content = b"Name: example\n"
        metadata = tarfile.TarInfo("example-1.0/PKG-INFO")
        metadata.size = len(content)
        metadata.mode = 0o664
        metadata.uid = uid
        metadata.gid = uid
        metadata.mtime = member_mtime
        archive.addfile(metadata, io.BytesIO(content))


def test_normalizer_eliminates_time_and_owner_variance(tmp_path: Path) -> None:
    first = tmp_path / "first.tar.gz"
    second = tmp_path / "second.tar.gz"
    make_sdist(first, 100, 200, 501)
    make_sdist(second, 300, 400, 1000)

    subprocess.run(
        [sys.executable, str(NORMALIZER), "--epoch", "1234567890", str(first), str(second)],
        check=True,
    )

    assert first.read_bytes() == second.read_bytes()
    with tarfile.open(first, mode="r:gz") as archive:
        for member in archive.getmembers():
            assert member.mtime == 1234567890
            assert member.uid == 0
            assert member.gid == 0
            assert member.uname == "root"
            assert member.gname == "root"


def test_normalizer_rejects_parent_traversal(tmp_path: Path) -> None:
    unsafe = tmp_path / "unsafe.tar.gz"
    with tarfile.open(unsafe, mode="w:gz") as archive:
        member = tarfile.TarInfo("../outside")
        member.size = 0
        archive.addfile(member)

    result = subprocess.run(
        [sys.executable, str(NORMALIZER), "--epoch", "1234567890", str(unsafe)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "unsafe source-distribution member" in result.stderr
