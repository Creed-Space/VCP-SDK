from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "check_release_authority.py"
TEMPLATE = ROOT / "release" / "review-ledger.template.json"


def run_publish(*, ledger: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--version",
            "4.2.0",
            "--publish",
            "--ledger",
            str(ledger),
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def test_publish_uses_external_ledger_path(tmp_path: Path) -> None:
    ledger = tmp_path / "review-ledger.json"
    ledger.write_bytes(TEMPLATE.read_bytes())
    result = run_publish(ledger=ledger)
    assert result.returncode == 1
    assert "review ledger is missing" not in result.stderr
    assert "has not passed prepublication validation" in result.stderr


def test_publish_fails_closed_when_external_ledger_is_missing(
    tmp_path: Path,
) -> None:
    result = run_publish(ledger=tmp_path / "missing.json")
    assert result.returncode == 1
    assert "review ledger is missing" in result.stderr
