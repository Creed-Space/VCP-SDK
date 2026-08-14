"""Tests for the bounded WebMCP upstream watcher."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "check_webmcp_upstream.py"
SPEC = importlib.util.spec_from_file_location("check_webmcp_upstream", SCRIPT)
assert SPEC and SPEC.loader
watcher = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(watcher)


def contract_for(source: bytes) -> dict[str, object]:
    return {
        "schema": "vcp-webmcp-upstream-contract/1",
        "reviewed_at": "2026-08-14",
        "upstream_commit": "a" * 40,
        "source_url": "https://raw.githubusercontent.com/example/project/main/spec.bs",
        "sha256": hashlib.sha256(source).hexdigest(),
        "maximum_bytes": 1024,
        "required_fragments": ["Document", "registerTool"],
        "forbidden_fragments": ["unregister()"],
    }


def test_evaluate_accepts_exact_reviewed_contract() -> None:
    source = b"partial interface Document { registerTool(); };"
    result = watcher.evaluate(source, contract_for(source))
    assert result["status"] == "matched"
    assert result["claim_update_performed"] is False


def test_evaluate_reports_hash_and_semantic_drift_without_source_copy() -> None:
    source = b"partial interface Document { unregister(); };"
    contract = contract_for(b"partial interface Document { registerTool(); };")
    result = watcher.evaluate(source, contract)
    assert result["status"] == "drift"
    assert result["missing_required_fragments"] == ["registerTool"]
    assert result["present_forbidden_fragments"] == ["unregister()"]
    assert "source" not in result


def test_load_contract_rejects_unapproved_host(tmp_path: Path) -> None:
    source = b"Document registerTool"
    contract = contract_for(source)
    contract["source_url"] = "https://example.invalid/spec.bs"
    path = tmp_path / "contract.json"
    path.write_text(json.dumps(contract), encoding="utf-8")
    with pytest.raises(ValueError, match="raw.githubusercontent.com"):
        watcher.load_contract(path)
