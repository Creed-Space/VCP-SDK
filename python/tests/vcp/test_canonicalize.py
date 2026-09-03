"""Direct contract tests for VCP content and manifest canonicalization."""

from __future__ import annotations

import hashlib
import unicodedata
from datetime import datetime, timezone

import pytest
from rfc8785 import FloatDomainError

from vcp.canonicalize import (
    canonicalize_content,
    canonicalize_manifest,
    compute_content_hash,
    parse_json_strict,
    parse_rfc3339_utc,
    verify_content_hash,
)


@pytest.mark.parametrize(
    "payload",
    [
        '{"outer":{"answer":42},"items":[true,null]}',
        b'{"outer":{"answer":42},"items":[true,null]}',
        bytearray(b'{"outer":{"answer":42},"items":[true,null]}'),
    ],
)
def test_strict_json_parser_preserves_supported_input_types(
    payload: str | bytes | bytearray,
) -> None:
    assert parse_json_strict(payload) == {
        "outer": {"answer": 42},
        "items": [True, None],
    }


def test_strict_json_parser_accepts_finite_floats() -> None:
    assert parse_json_strict('{"value":1.5,"neg":-2.25e3}') == {"value": 1.5, "neg": -2250.0}


def test_strict_json_parser_rejects_overflowing_numeric_literals() -> None:
    # 1e999 is a syntactically valid JSON number that overflows to infinity;
    # it never reaches parse_constant, so parse_float has to catch it.
    with pytest.raises(
        ValueError,
        match=r"^Non-finite JSON number is not permitted: 1e999$",
    ):
        parse_json_strict('{"value":1e999}')


def test_strict_json_parser_rejects_duplicate_nested_keys() -> None:
    with pytest.raises(
        ValueError,
        match=r"^Duplicate JSON object key: 'role'$",
    ):
        parse_json_strict('{"identity":{"role":"guide","role":"admin"}}')


@pytest.mark.parametrize("constant", ["NaN", "Infinity", "-Infinity"])
def test_strict_json_parser_rejects_non_finite_constants(constant: str) -> None:
    with pytest.raises(
        ValueError,
        match=rf"^Non-finite JSON number is not permitted: {constant}$",
    ):
        parse_json_strict(f'{{"value":{constant}}}')


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


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("A\u00a0", "A\u00a0\n"),
        ("AXX\n", "AXX\n"),
    ],
)
def test_content_strips_only_spaces_and_tabs_from_line_ends(raw: str, expected: str) -> None:
    assert canonicalize_content(raw) == expected.encode("utf-8")


class TestParseRfc3339Utc:
    def test_lowercase_zulu_suffix_is_utc(self) -> None:
        assert parse_rfc3339_utc("2026-01-01T00:00:00z", "ts") == datetime(
            2026, 1, 1, tzinfo=timezone.utc
        )

    def test_negative_offset_is_normalised_to_utc(self) -> None:
        parsed = parse_rfc3339_utc("2026-01-01T02:00:00-05:00", "ts")
        assert parsed == datetime(2026, 1, 1, 7, tzinfo=timezone.utc)
        assert parsed.tzinfo is timezone.utc

    def test_short_fraction_is_right_padded_with_zeros(self) -> None:
        parsed = parse_rfc3339_utc("2026-01-01T00:00:00.5Z", "ts")
        assert parsed == datetime(2026, 1, 1, 0, 0, 0, 500000, tzinfo=timezone.utc)

    def test_long_fraction_is_truncated_to_microseconds(self) -> None:
        parsed = parse_rfc3339_utc("2026-01-01T00:00:00.123456789+00:00", "ts")
        assert parsed == datetime(2026, 1, 1, 0, 0, 0, 123456, tzinfo=timezone.utc)

    @pytest.mark.parametrize("value", [7, None, "", "2026-01-01T00:00:00", "2026-01-01"])
    def test_untimed_or_non_string_values_are_rejected(self, value: object) -> None:
        with pytest.raises(ValueError, match=r"^ts must be an RFC 3339 string with timezone$"):
            parse_rfc3339_utc(value, "ts")

    def test_well_formed_but_impossible_datetime_is_rejected(self) -> None:
        with pytest.raises(ValueError, match=r"^ts must be a valid RFC 3339 datetime$"):
            parse_rfc3339_utc("2026-13-01T00:00:00Z", "ts")
