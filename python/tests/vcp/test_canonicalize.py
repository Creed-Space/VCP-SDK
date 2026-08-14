"""Direct contract tests for VCP content and manifest canonicalization."""

from __future__ import annotations

import hashlib
import unicodedata

import pytest
from rfc8785 import FloatDomainError

from vcp.canonicalize import (
    canonicalize_content,
    canonicalize_manifest,
    compute_content_hash,
    verify_content_hash,
)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Hello\r\nWorld\r\n", b"Hello\nWorld\n"),
        ("Hello\rWorld\r", b"Hello\nWorld\n"),
        ("  leading and trailing  \t\n", b"  leading and trailing\n"),
        ("No trailing newline", b"No trailing newline\n"),
        ("Multiple\n\ninternal\n\n\n", b"Multiple\n\ninternal\n"),
        ("Tab\there\t\n", b"Tab\there\n"),
        ("", b"\n"),
        ("\n\n\n", b"\n"),
    ],
)
def test_content_canonicalization_contract(raw: str, expected: bytes) -> None:
    assert canonicalize_content(raw) == expected


def test_content_is_nfc_normalized_and_utf8_encoded_without_bom() -> None:
    decomposed = "Cafe\N{COMBINING ACUTE ACCENT}"
    expected_text = unicodedata.normalize("NFC", decomposed) + "\n"

    canonical = canonicalize_content(decomposed)

    assert canonical == expected_text.encode("utf-8")
    assert not canonical.startswith(b"\xef\xbb\xbf")


@pytest.mark.parametrize(
    "character",
    [
        chr(codepoint)
        for codepoint in (*range(0x00, 0x20), *range(0x7F, 0xA0))
        if codepoint not in {0x09, 0x0A, 0x0D}
    ],
)
def test_rejects_control_characters_with_exact_position(character: str) -> None:
    with pytest.raises(
        ValueError,
        match=rf"^Illegal control character at position 1: U\+{ord(character):04X}$",
    ):
        canonicalize_content(f"A{character}B")


@pytest.mark.parametrize(
    "character",
    [
        "\u202a",
        "\u202b",
        "\u202c",
        "\u202d",
        "\u202e",
        "\u2066",
        "\u2067",
        "\u2068",
        "\u2069",
        "\u200b",
        "\u200c",
        "\u200d",
        "\ufeff",
    ],
)
def test_rejects_directional_and_zero_width_characters(character: str) -> None:
    with pytest.raises(
        ValueError,
        match=rf"^Forbidden Unicode character at position 1: U\+{ord(character):04X}$",
    ):
        canonicalize_content(f"A{character}B")


def test_manifest_uses_jcs_and_removes_only_top_level_signature() -> None:
    manifest = {
        "z": 1.0,
        "signature": {"algorithm": "ed25519", "value": "ignored"},
        "a": {"signature": "retained", "value": True},
    }

    assert canonicalize_manifest(manifest) == (b'{"a":{"signature":"retained","value":true},"z":1}')
    assert "signature" in manifest


def test_manifest_rejects_values_outside_jcs() -> None:
    with pytest.raises((FloatDomainError, ValueError)):
        canonicalize_manifest({"value": float("nan")})


def test_content_hash_uses_sha256_of_canonical_bytes() -> None:
    canonical = b"Hello\n"
    expected = f"sha256:{hashlib.sha256(canonical).hexdigest()}"

    assert compute_content_hash("Hello\r\n") == expected
    assert verify_content_hash("Hello", expected)
    assert not verify_content_hash("Hello!", expected)
    assert not verify_content_hash("Hello", expected.upper())
