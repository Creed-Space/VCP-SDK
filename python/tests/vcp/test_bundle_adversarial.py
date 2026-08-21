"""Regression tests for bundle serialization ambiguity and field preservation."""

from __future__ import annotations

import pytest

from vcp.bundle import Bundle, BundleBuilder, Manifest
from vcp.types import Scope


def _bundle() -> Bundle:
    return (
        BundleBuilder("test", "1.0.0")
        .with_content("Be helpful.")
        .with_issuer("issuer", "ed25519:public", "key-1")
        .with_auditor("auditor", "audit-key")
        .build(lambda _payload: "manifest", lambda _payload: "attestation")
    )


def test_manifest_roundtrip_preserves_competence_requirements() -> None:
    bundle = _bundle()
    bundle.manifest.scope = Scope(competence_requirements={"medical": 0.8, "legal": 1.0})
    restored = Manifest.from_dict(bundle.manifest.to_dict())
    assert restored.scope == Scope(competence_requirements={"medical": 0.8, "legal": 1.0})
    assert restored.to_dict()["scope"]["competence_requirements"] == {
        "medical": 0.8,
        "legal": 1.0,
    }


@pytest.mark.parametrize(
    "payload",
    [
        "[]",
        "NaN",
        '{"manifest":{},"manifest":{"shadow":true},"content":"x"}',
    ],
)
def test_bundle_json_rejects_non_object_nonfinite_and_duplicate_keys(payload: str) -> None:
    with pytest.raises((TypeError, ValueError)):
        Bundle.from_json(payload)


def test_bundle_from_json_preserves_valid_bundle() -> None:
    bundle = _bundle()
    assert Bundle.from_json(bundle.to_json()).to_dict() == bundle.to_dict()
