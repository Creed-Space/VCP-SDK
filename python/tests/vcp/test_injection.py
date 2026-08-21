"""Adversarial tests for verified-bundle prompt injection formatting."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from vcp.bundle import Bundle, BundleBuilder
from vcp.injection import (
    InjectionFormat,
    InjectionOptions,
    format_injection,
    format_multi_constitution_injection,
)
from vcp.types import Composition, CompositionMode


def _bundle(
    bundle_id: str = "test",
    *,
    layer: int | None = None,
    content: str = "Be helpful.",
) -> Bundle:
    builder = (
        BundleBuilder(bundle_id, "1.0.0")
        .with_content(content)
        .with_issuer("issuer", "ed25519:public", "key-1")
        .with_auditor("auditor", "audit-key")
    )
    if layer is not None:
        builder.with_composition(Composition(layer=layer, mode=CompositionMode.EXTEND))
    return builder.build(lambda _payload: "manifest", lambda _payload: "attestation")


@pytest.mark.parametrize(
    ("injection_format", "marker"),
    [
        (InjectionFormat.HEADER_DELIMITED, "---BEGIN-CONSTITUTION---"),
        (InjectionFormat.XML_TAGGED, "<vcp-constitution "),
        (InjectionFormat.MINIMAL, "# Constitution: test@1.0.0"),
    ],
)
def test_every_injection_format_preserves_content(
    injection_format: InjectionFormat,
    marker: str,
) -> None:
    rendered = format_injection(_bundle(), InjectionOptions(format=injection_format))
    assert marker in rendered
    assert "Be helpful." in rendered


def test_verified_timestamp_is_valid_rfc3339_with_one_utc_suffix() -> None:
    verified_at = datetime(2026, 1, 1, 1, 0, tzinfo=timezone(timedelta(hours=1)))
    rendered = format_injection(_bundle(), verified_at=verified_at)
    assert "[VERIFIED:2026-01-01T00:00:00Z]" in rendered
    assert "+00:00Z" not in rendered


def test_naive_verification_timestamp_is_rejected() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        format_injection(_bundle(), verified_at=datetime(2026, 1, 1))


@pytest.mark.parametrize(
    "options",
    [
        InjectionOptions(format="unknown"),  # type: ignore[arg-type]
        InjectionOptions(hash_prefix_length=0),
        InjectionOptions(hash_suffix_length=True),
        InjectionOptions(include_tokens=1),  # type: ignore[arg-type]
    ],
)
def test_malformed_options_are_rejected_instead_of_changing_format(
    options: InjectionOptions,
) -> None:
    with pytest.raises(ValueError):
        format_injection(_bundle(), options)


def test_malformed_content_hash_is_rejected_without_index_error() -> None:
    bundle = _bundle()
    bundle.manifest.bundle.content_hash = "not-a-digest"
    with pytest.raises(ValueError, match="content_hash"):
        format_injection(bundle)


def test_include_flags_remove_only_their_metadata() -> None:
    rendered = format_injection(
        _bundle(),
        InjectionOptions(include_tokens=False, include_attestation=False),
    )
    assert "[TOKENS:" not in rendered
    assert "[ATTESTED:" not in rendered
    assert "[HASH:" in rendered


def test_multi_injection_sorts_layers_and_uses_actual_protocol_version() -> None:
    rendered = format_multi_constitution_injection(
        [_bundle("upper", layer=3), _bundle("base", layer=1)],
        verified_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    assert rendered.startswith("[VCP:2.0]\n")
    assert rendered.index("[LAYER:1:base@1.0.0") < rendered.index("[LAYER:3:upper@1.0.0")
    assert "[PRECEDENCE:1>3]" in rendered
    assert "[VERIFIED:2026-01-01T00:00:00Z]" in rendered


def test_multi_injection_rejects_empty_and_silently_ignored_formats() -> None:
    with pytest.raises(ValueError, match="At least one"):
        format_multi_constitution_injection([])
    with pytest.raises(ValueError, match="header-delimited"):
        format_multi_constitution_injection(
            [_bundle()],
            InjectionOptions(format=InjectionFormat.XML_TAGGED),
        )
