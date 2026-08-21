"""
VCP Injection Module

Formats verified bundles for LLM injection.
"""

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

from .bundle import Bundle


class InjectionFormat(Enum):
    """Supported injection formats."""

    HEADER_DELIMITED = "header-delimited"
    XML_TAGGED = "xml-tagged"
    MINIMAL = "minimal"


@dataclass
class InjectionOptions:
    """Options for formatting injection."""

    format: InjectionFormat = InjectionFormat.HEADER_DELIMITED
    include_tokens: bool = True
    include_attestation: bool = True
    hash_prefix_length: int = 8
    hash_suffix_length: int = 4


_CONTENT_HASH_RE = re.compile(r"^sha256:([0-9a-f]{64})$")


def _validated_inputs(
    options: InjectionOptions | None,
    verified_at: datetime | None,
) -> tuple[InjectionOptions, datetime]:
    """Validate formatter controls and normalize the verification time."""
    resolved_options = options if options is not None else InjectionOptions()
    if not isinstance(resolved_options, InjectionOptions):
        raise TypeError("options must be an InjectionOptions instance")
    if not isinstance(resolved_options.format, InjectionFormat):
        raise ValueError("options.format must be a supported InjectionFormat")
    for name, value in (
        ("hash_prefix_length", resolved_options.hash_prefix_length),
        ("hash_suffix_length", resolved_options.hash_suffix_length),
    ):
        if not isinstance(value, int) or isinstance(value, bool) or not 1 <= value <= 64:
            raise ValueError(f"{name} must be an integer between 1 and 64")
    for name, value in (
        ("include_tokens", resolved_options.include_tokens),
        ("include_attestation", resolved_options.include_attestation),
    ):
        if not isinstance(value, bool):
            raise ValueError(f"{name} must be a boolean")

    resolved_time = verified_at if verified_at is not None else datetime.now(timezone.utc)
    if (
        not isinstance(resolved_time, datetime)
        or resolved_time.tzinfo is None
        or resolved_time.utcoffset() is None
    ):
        raise ValueError("verified_at must be a timezone-aware datetime")
    return resolved_options, resolved_time.astimezone(timezone.utc)


def _verified_timestamp(value: datetime) -> str:
    """Render an aware timestamp as RFC 3339 UTC with exactly one ``Z``."""
    return value.isoformat().replace("+00:00", "Z")


def _content_hash_value(bundle: Bundle) -> str:
    """Return a validated SHA-256 digest from a verified bundle manifest."""
    content_hash = bundle.manifest.bundle.content_hash
    if not isinstance(content_hash, str):
        raise ValueError("bundle content_hash must be a sha256 digest")
    match = _CONTENT_HASH_RE.fullmatch(content_hash)
    if match is None:
        raise ValueError(
            "bundle content_hash must be 'sha256:' followed by 64 lowercase hex digits"
        )
    return match.group(1)


def format_injection(
    bundle: Bundle,
    options: InjectionOptions | None = None,
    verified_at: datetime | None = None,
) -> str:
    """
    Format a verified bundle for LLM injection.

    Args:
        bundle: Verified bundle to format
        options: Formatting options
        verified_at: Verification timestamp (defaults to now)

    Returns:
        Formatted string for system prompt injection
    """
    if not isinstance(bundle, Bundle):
        raise TypeError("bundle must be a Bundle")
    options, verified_at = _validated_inputs(options, verified_at)

    if options.format == InjectionFormat.HEADER_DELIMITED:
        return _format_header_delimited(bundle, options, verified_at)
    elif options.format == InjectionFormat.XML_TAGGED:
        return _format_xml_tagged(bundle, options, verified_at)
    elif options.format == InjectionFormat.MINIMAL:
        return _format_minimal(bundle, options, verified_at)
    raise AssertionError("unreachable injection format")


def _format_header_delimited(
    bundle: Bundle,
    options: InjectionOptions,
    verified_at: datetime,
) -> str:
    """Format with VCP header and delimiters."""
    manifest = bundle.manifest

    # Extract hash prefix and suffix
    hash_value = _content_hash_value(bundle)
    hash_display = (
        f"{hash_value[: options.hash_prefix_length]}...{hash_value[-options.hash_suffix_length :]}"
    )

    lines = [
        f"[VCP:{manifest.vcp_version}]",
        f"[ID:{manifest.bundle.id}@{manifest.bundle.version}]",
        f"[HASH:{hash_display}]",
    ]

    if options.include_tokens:
        lines.append(f"[TOKENS:{manifest.budget.token_count}]")

    if options.include_attestation:
        attestation = manifest.safety_attestation
        att_type = attestation.attestation_type.value
        lines.append(f"[ATTESTED:{att_type}:{attestation.auditor}]")

    lines.append(f"[VERIFIED:{_verified_timestamp(verified_at)}]")
    lines.append("---BEGIN-CONSTITUTION---")
    lines.append(bundle.content.rstrip())
    lines.append("---END-CONSTITUTION---")

    return "\n".join(lines)


def _format_xml_tagged(
    bundle: Bundle,
    options: InjectionOptions,
    verified_at: datetime,
) -> str:
    """Format with XML-style tags."""
    manifest = bundle.manifest

    hash_value = _content_hash_value(bundle)
    hash_display = (
        f"{hash_value[: options.hash_prefix_length]}...{hash_value[-options.hash_suffix_length :]}"
    )

    attrs = [
        f'version="{manifest.vcp_version}"',
        f'id="{manifest.bundle.id}"',
        f'bundle_version="{manifest.bundle.version}"',
        f'hash="{hash_display}"',
    ]

    if options.include_tokens:
        attrs.append(f'tokens="{manifest.budget.token_count}"')

    if options.include_attestation:
        attestation = manifest.safety_attestation
        att_type = attestation.attestation_type.value
        attrs.append(f'attestation="{att_type}"')
        attrs.append(f'auditor="{attestation.auditor}"')

    attrs.append(f'verified="{_verified_timestamp(verified_at)}"')

    attrs_str = " ".join(attrs)

    return f"<vcp-constitution {attrs_str}>\n{bundle.content.rstrip()}\n</vcp-constitution>"


def _format_minimal(
    bundle: Bundle,
    options: InjectionOptions,
    verified_at: datetime,
) -> str:
    """Minimal format - just the content with a brief header."""
    manifest = bundle.manifest

    hash_value = _content_hash_value(bundle)[:8]

    header = f"# Constitution: {manifest.bundle.id}@{manifest.bundle.version} [{hash_value}]"

    return f"{header}\n\n{bundle.content.rstrip()}"


def format_multi_constitution_injection(
    bundles: list[Bundle],
    options: InjectionOptions | None = None,
    verified_at: datetime | None = None,
) -> str:
    """
    Format multiple bundles for injection with composition.

    Args:
        bundles: List of verified bundles (in layer order)
        options: Formatting options
        verified_at: Verification timestamp

    Returns:
        Formatted string with all constitutions
    """
    options, verified_at = _validated_inputs(options, verified_at)
    if options.format is not InjectionFormat.HEADER_DELIMITED:
        raise ValueError("multi-constitution injection supports only header-delimited format")

    if not bundles:
        raise ValueError("At least one bundle required")
    if any(not isinstance(bundle, Bundle) for bundle in bundles):
        raise TypeError("bundles must contain only Bundle instances")

    if len(bundles) == 1:
        return format_injection(bundles[0], options, verified_at)

    # Sort by layer
    sorted_bundles = sorted(
        bundles,
        key=lambda b: b.manifest.composition.layer if b.manifest.composition else 2,
    )

    versions = {bundle.manifest.vcp_version for bundle in bundles}
    if len(versions) != 1:
        raise ValueError("all bundles in a composition must use the same VCP version")
    protocol_version = versions.pop()

    lines = [
        f"[VCP:{protocol_version}]",
        "[COMPOSITION:layered]",
        f"[LAYERS:{len(bundles)}]",
    ]

    # Add layer entries
    for i, bundle in enumerate(sorted_bundles, 1):
        manifest = bundle.manifest
        layer = manifest.composition.layer if manifest.composition else i
        hash_value = _content_hash_value(bundle)
        hash_short = f"{hash_value[:8]}...{hash_value[-4:]}"
        lines.append(f"[LAYER:{layer}:{manifest.bundle.id}@{manifest.bundle.version}:{hash_short}]")

    # Precedence (higher layer overrides lower)
    layers = [
        b.manifest.composition.layer if b.manifest.composition else i
        for i, b in enumerate(sorted_bundles, 1)
    ]
    precedence = ">".join(str(layer) for layer in sorted(set(layers)))
    lines.append(f"[PRECEDENCE:{precedence}]")

    lines.append(f"[VERIFIED:{_verified_timestamp(verified_at)}]")
    lines.append("---BEGIN-CONSTITUTION---")

    # Add each constitution with layer marker
    for i, bundle in enumerate(sorted_bundles, 1):
        manifest = bundle.manifest
        layer = manifest.composition.layer if manifest.composition else i
        mode = manifest.composition.mode.value if manifest.composition else "extend"

        title = manifest.metadata.get("title", manifest.bundle.id)
        lines.append(f"\n## Layer {layer}: {title} ({mode.upper()})")
        lines.append(bundle.content.rstrip())

    lines.append("\n---END-CONSTITUTION---")

    return "\n".join(lines)
