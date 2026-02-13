"""
VCP Canonicalization Module

Implements RFC 8785 (JCS) for manifest and content canonicalization.
"""

import hashlib
import json
import unicodedata
from typing import Any


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
    FORBIDDEN = {
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
        if char in FORBIDDEN:
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

    # JCS: sort keys, no whitespace, ensure_ascii=False for UTF-8
    canonical = json.dumps(to_sign, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    return canonical.encode("utf-8")


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
