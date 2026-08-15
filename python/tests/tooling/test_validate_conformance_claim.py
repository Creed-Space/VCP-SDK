from __future__ import annotations

import importlib.util
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "validate_conformance_claim.py"
SPEC = importlib.util.spec_from_file_location("validate_conformance_claim", SCRIPT)
assert SPEC and SPEC.loader
claim_validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(claim_validator)
validate_claim = claim_validator.validate_claim


def claim(**overrides: object) -> dict[str, object]:
    value: dict[str, object] = {
        "status": "local-source-evidence",
        "publishable": False,
        "issued_at": "2026-08-15T00:00:00Z",
        "expires_at": "2026-09-14T00:00:00Z",
        "revoked_at": None,
        "superseded_by": None,
    }
    value.update(overrides)
    return value


PUBLICATION_STATE = {"public_copy_policy": {"published_badges_allowed": False}}


def test_accepts_current_local_only_claim() -> None:
    assert not validate_claim(claim(), PUBLICATION_STATE, datetime(2026, 8, 20, tzinfo=UTC))


def test_rejects_expired_claim() -> None:
    assert "claim is expired" in validate_claim(
        claim(), PUBLICATION_STATE, datetime(2026, 9, 14, tzinfo=UTC)
    )


def test_rejects_superseded_claim() -> None:
    assert "claim is superseded" in validate_claim(
        claim(superseded_by="claim-2"),
        PUBLICATION_STATE,
        datetime(2026, 8, 20, tzinfo=UTC),
    )


def test_rejects_revoked_claim() -> None:
    assert "claim is revoked" in validate_claim(
        claim(revoked_at="2026-08-18T00:00:00Z"),
        PUBLICATION_STATE,
        datetime(2026, 8, 20, tzinfo=UTC),
    )
