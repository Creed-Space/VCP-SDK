"""
VCP Canonicalization Module

Implements RFC 8785 (JCS) for manifest and content canonicalization.
"""

import hashlib
import json
import math
import re
import unicodedata
from datetime import datetime, timezone
from typing import Any

import rfc8785

_RFC3339_PATTERN = re.compile(
    r"\d{4}-\d{2}-\d{2}[Tt ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[Zz]|[+-]\d{2}:\d{2})"
)


def parse_rfc3339_utc(value: Any, field_name: str) -> datetime:
    """Parse a timezone-qualified RFC 3339 timestamp and normalize it to aware UTC.

    Fractions longer than six digits are truncated before parsing so that
    Python 3.10 (which rejects them) agrees with 3.11+ on otherwise valid
    nanosecond timestamps emitted by other runtimes.
    """
    if not isinstance(value, str) or _RFC3339_PATTERN.fullmatch(value) is None:
        raise ValueError(f"{field_name} must be an RFC 3339 string with timezone")
    normalized = f"{value[:-1]}+00:00" if value[-1] in "Zz" else value
    body, offset = normalized[:-6], normalized[-6:]
    if "." in body:
        seconds, fraction = body.split(".", 1)
        body = f"{seconds}.{fraction[:6].ljust(6, '0')}"
    try:
        parsed = datetime.fromisoformat(body + offset)
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a valid RFC 3339 datetime") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field_name} must include a timezone")
    return parsed.astimezone(timezone.utc)


def parse_json_strict(value: str | bytes | bytearray) -> Any:
    """Parse interoperable JSON without ambiguous object keys or numbers.

    Python's default decoder silently keeps the last occurrence of a duplicate
    object key and accepts the non-standard ``NaN`` and infinity constants.
    Both behaviours are unsafe for signed or security-sensitive documents,
    because different implementations can assign different meaning to the
    same bytes.
    """

    def _object_without_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, item in pairs:
            if key in result:
                raise ValueError(f"Duplicate JSON object key: {key!r}")
            result[key] = item
        return result

    def _reject_constant(constant: str) -> Any:
        raise ValueError(f"Non-finite JSON number is not permitted: {constant}")

    def _finite_float(text: str) -> float:
        # Overflowing literals such as ``1e400`` bypass parse_constant.
        number = float(text)
        if not math.isfinite(number):
            raise ValueError(f"Non-finite JSON number is not permitted: {text}")
        return number

    return json.loads(
        value,
        object_pairs_hook=_object_without_duplicates,
        parse_constant=_reject_constant,
        parse_float=_finite_float,
    )


def canonicalize_content(text: str) -> bytes:
    """
    Canonicalize constitution content for hash computation.

    Rules:
    1. Unicode NFC normalization
    2. Line ending normalization (CRLF/CR → LF)
    3. Strip trailing whitespace from each line
    4. Remove trailing empty lines, ensure single trailing newline
    5. Reject control characters (except \\n, \\t)
    6. UTF-8 encode without BOM

    Args:
        text: Raw constitution text

    Returns:
        Canonical UTF-8 bytes

    Raises:
        ValueError: If content contains illegal characters
    """
    # 1. Unicode NFC normalization
    text = unicodedata.normalize("NFC", text)

    # 2. Line ending normalization
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # 3. Strip trailing whitespace from each line
    lines = [line.rstrip(" \t") for line in text.split("\n")]

    # 4. Remove trailing empty lines, ensure single trailing newline
    while lines and lines[-1] == "":
        lines.pop()
    text = "\n".join(lines) + "\n"

    # 5. Reject control characters (except \n, \t)
    for i, char in enumerate(text):
        if unicodedata.category(char) == "Cc" and char not in "\n\t":
            raise ValueError(f"Illegal control character at position {i}: U+{ord(char):04X}")

    # Check for forbidden Unicode characters (direction overrides, etc.)
    forbidden = {
        "\u202a",
        "\u202b",
        "\u202c",
        "\u202d",
        "\u202e",  # direction overrides
        "\u2066",
        "\u2067",
        "\u2068",
        "\u2069",  # isolates
        "\u200b",
        "\u200c",
        "\u200d",
        "\ufeff",  # zero-width chars
    }
    for i, char in enumerate(text):
        if char in forbidden:
            raise ValueError(f"Forbidden Unicode character at position {i}: U+{ord(char):04X}")

    # 6. UTF-8 encode without BOM
    return text.encode("utf-8")


def canonicalize_manifest(manifest: dict[str, Any]) -> bytes:
    """
    Canonicalize manifest for signature computation.

    Implements RFC 8785 JSON Canonicalization Scheme (JCS):
    - UTF-8 encoding
    - No whitespace between tokens
    - Object keys sorted lexicographically
    - Numbers in shortest form

    Args:
        manifest: Manifest dict (signature field excluded)

    Returns:
        Canonical UTF-8 bytes
    """
    # Remove signature before canonicalizing
    to_sign = {k: v for k, v in manifest.items() if k != "signature"}

    return rfc8785.dumps(to_sign)


def compute_content_hash(content: str) -> str:
    """
    Compute SHA-256 hash of canonical content.

    Args:
        content: Raw constitution text

    Returns:
        Hash string in format "sha256:{hex}"
    """
    canonical = canonicalize_content(content)
    digest = hashlib.sha256(canonical).hexdigest()
    return f"sha256:{digest}"


def verify_content_hash(content: str, expected_hash: str) -> bool:
    """
    Verify content matches expected hash.

    Args:
        content: Constitution text to verify
        expected_hash: Expected hash string

    Returns:
        True if hash matches
    """
    computed = compute_content_hash(content)
    return computed == expected_hash
