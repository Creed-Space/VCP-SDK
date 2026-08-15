from __future__ import annotations

import base64
import hashlib
import os
import stat
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[3]
WORKFLOW = ROOT / ".github/workflows/release.yml"
pytestmark = pytest.mark.skipif(
    sys.platform == "win32",
    reason="the protected publication job runs only on ubuntu-24.04 Bash",
)


def materialization_script() -> str:
    workflow = yaml.safe_load(WORKFLOW.read_text())
    steps = workflow["jobs"]["authorize-publication"]["steps"]
    step = next(
        item
        for item in steps
        if item.get("name") == "Materialize the hash-bound protected review ledger"
    )
    return step["run"]


def run_materialization(
    tmp_path: Path, *, payload: bytes, expected_sha256: str
) -> subprocess.CompletedProcess[str]:
    runner_temp = tmp_path / "runner"
    runner_temp.mkdir()
    environment = {
        **os.environ,
        "RUNNER_TEMP": str(runner_temp),
        "GITHUB_ENV": str(tmp_path / "github-env"),
        "GITHUB_STEP_SUMMARY": str(tmp_path / "summary"),
        "VCP_REVIEW_LEDGER_B64": base64.b64encode(payload).decode(),
        "VCP_REVIEW_LEDGER_SHA256": expected_sha256,
        "PATH": f"{Path(sys.executable).parent}:{os.environ['PATH']}",
    }
    return subprocess.run(
        ["bash", "-eo", "pipefail", "-c", materialization_script()],
        cwd=ROOT,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )


def test_protected_ledger_is_hash_bound_and_written_privately(tmp_path: Path) -> None:
    payload = (ROOT / "release/review-ledger.template.json").read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    result = run_materialization(tmp_path, payload=payload, expected_sha256=digest)
    assert result.returncode == 0, result.stderr

    ledger = tmp_path / "runner/review-ledger.json"
    assert ledger.read_bytes() == payload
    assert stat.S_IMODE(ledger.stat().st_mode) == 0o600
    assert (tmp_path / "github-env").read_text() == f"VCP_REVIEW_LEDGER={ledger}\n"
    assert digest in (tmp_path / "summary").read_text()


def test_protected_ledger_rejects_digest_mismatch(tmp_path: Path) -> None:
    result = run_materialization(
        tmp_path,
        payload=b'[{"untrusted": "ledger"}]',
        expected_sha256="0" * 64,
    )
    assert result.returncode != 0
    assert "does not match dispatch" in result.stderr
    assert not (tmp_path / "runner/review-ledger.json").exists()
