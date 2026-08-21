"""Adversarial trust-store parsing and authorization tests."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from vcp.trust import TrustAnchor, TrustConfig


def _anchor(
    *,
    entity_id: str = "issuer",
    key_id: str = "key-1",
    anchor_type: str = "issuer",
) -> TrustAnchor:
    now = datetime.now(timezone.utc)
    return TrustAnchor(
        id=entity_id,
        key_id=key_id,
        algorithm="ed25519",
        public_key="base64:AAAA",
        anchor_type=anchor_type,
        valid_from=now - timedelta(days=1),
        valid_until=now + timedelta(days=1),
    )


def test_duplicate_json_keys_are_rejected() -> None:
    with pytest.raises(ValueError, match="Duplicate JSON object key"):
        TrustConfig.from_json('{"trust_anchors":{},"trust_anchors":{"shadow":{}}}')


def test_from_dict_does_not_mutate_caller_owned_key_records() -> None:
    now = datetime.now(timezone.utc)
    key = {
        "id": "key-1",
        "algorithm": "ed25519",
        "public_key": "base64:AAAA",
        "valid_from": (now - timedelta(days=1)).isoformat(),
        "valid_until": (now + timedelta(days=1)).isoformat(),
    }
    data = {"trust_anchors": {"issuer": {"type": "issuer", "keys": [key]}}}
    TrustConfig.from_dict(data)
    assert "type" not in key


def test_unknown_entity_type_is_rejected_instead_of_becoming_an_issuer() -> None:
    with pytest.raises(ValueError, match="Unknown trust anchor type"):
        TrustConfig.from_dict(
            {"trust_anchors": {"issuer": {"type": "mystery", "keys": []}}}
        )


def test_empty_requested_key_id_does_not_authorize_an_arbitrary_key() -> None:
    config = TrustConfig()
    config.add_issuer("issuer", _anchor())
    assert config.get_issuer_key("issuer", "") is None


def test_anchor_type_and_entity_id_must_match_destination() -> None:
    config = TrustConfig()
    with pytest.raises(ValueError, match="as an issuer"):
        config.add_issuer("issuer", _anchor(anchor_type="auditor"))
    with pytest.raises(ValueError, match="id must match"):
        config.add_issuer("different", _anchor())


def test_duplicate_key_ids_are_rejected_as_ambiguous() -> None:
    config = TrustConfig()
    config.add_issuer("issuer", _anchor())
    with pytest.raises(ValueError, match="Duplicate"):
        config.add_issuer("issuer", _anchor())


@pytest.mark.parametrize(
    "changes",
    [
        {"anchor_type": "unknown"},
        {"state": "unknown"},
        {"key_id": ""},
        {
            "valid_from": datetime(2026, 1, 2, tzinfo=timezone.utc),
            "valid_until": datetime(2026, 1, 1, tzinfo=timezone.utc),
        },
        {"valid_from": datetime(2026, 1, 1)},
    ],
)
def test_malformed_anchor_invariants_are_rejected(changes: dict[str, object]) -> None:
    now = datetime.now(timezone.utc)
    kwargs: dict[str, object] = {
        "id": "issuer",
        "key_id": "key-1",
        "algorithm": "ed25519",
        "public_key": "base64:AAAA",
        "anchor_type": "issuer",
        "valid_from": now - timedelta(days=1),
        "valid_until": now + timedelta(days=1),
        "state": "active",
    }
    kwargs.update(changes)
    with pytest.raises(ValueError):
        TrustAnchor(**kwargs)  # type: ignore[arg-type]
