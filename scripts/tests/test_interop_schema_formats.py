"""Regression tests for semantic formats in the interoperability runner."""

from __future__ import annotations

import json
from copy import deepcopy

from conformance.runners.interop_parity import COMPLETE, manifest_validator


def test_interop_manifest_rejects_impossible_calendar_timestamp() -> None:
    fixture = json.loads(COMPLETE.read_text(encoding="utf-8"))
    manifest = deepcopy(fixture["vectors"][0]["manifest"])
    manifest["timestamps"]["iat"] = "2026-02-29T00:00:00Z"

    errors = list(manifest_validator().iter_errors(manifest))

    assert any(list(error.path) == ["timestamps", "iat"] for error in errors)
