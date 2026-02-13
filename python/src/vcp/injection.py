"""
VCP Injection Module

Formats verified bundles for LLM injection.
"""

from dataclasses import dataclass
from datetime import datetime
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
    options = options or InjectionOptions()
    verified_at = verified_at or datetime.utcnow()

    if options.format == InjectionFormat.HEADER_DELIMITED:
        return _format_header_delimited(bundle, options, verified_at)
    elif options.format == InjectionFormat.XML_TAGGED:
        return _format_xml_tagged(bundle, options, verified_at)
    else:
        return _format_minimal(bundle, options, verified_at)


def _format_header_delimited(
    bundle: Bundle,
    options: InjectionOptions,
    verified_at: datetime,
) -> str:
    """Format with VCP header and delimiters."""
    manifest = bundle.manifest

    # Extract hash prefix and suffix
    content_hash = manifest.bundle.content_hash
    hash_value = content_hash.split(":")[1]
    hash_display = f"{hash_value[: options.hash_prefix_length]}...{hash_value[-options.hash_suffix_length :]}"

    lines = [
        f"[VCP:{manifest.vcp_version}]",
        f"[ID:{manifest.bundle.id}@{manifest.bundle.version}]",
        f"[HASH:{hash_display}]",
    ]

    if options.include_tokens:
        lines.append(f"[TOKENS:{manifest.budget.token_count}]")

    if options.include_attestation:
        attestation = manifest.safety_attestation
        lines.append(f"[ATTESTED:{attestation.attestation_type.value}:{attestation.auditor}]")

    lines.append(f"[VERIFIED:{verified_at.isoformat()}Z]")
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

    content_hash = manifest.bundle.content_hash
    hash_value = content_hash.split(":")[1]
    hash_display = f"{hash_value[: options.hash_prefix_length]}...{hash_value[-options.hash_suffix_length :]}"

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
        attrs.append(f'attestation="{attestation.attestation_type.value}"')
        attrs.append(f'auditor="{attestation.auditor}"')

    attrs.append(f'verified="{verified_at.isoformat()}Z"')

    attrs_str = " ".join(attrs)

    return f"<vcp-constitution {attrs_str}>\n{bundle.content.rstrip()}\n</vcp-constitution>"


def _format_minimal(
    bundle: Bundle,
    options: InjectionOptions,
    verified_at: datetime,
) -> str:
    """Minimal format - just the content with a brief header."""
    manifest = bundle.manifest

    content_hash = manifest.bundle.content_hash
    hash_value = content_hash.split(":")[1][:8]

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
    options = options or InjectionOptions()
    verified_at = verified_at or datetime.utcnow()

    if not bundles:
        raise ValueError("At least one bundle required")

    if len(bundles) == 1:
        return format_injection(bundles[0], options, verified_at)

    # Sort by layer
    sorted_bundles = sorted(
        bundles,
        key=lambda b: b.manifest.composition.layer if b.manifest.composition else 2,
    )

    lines = [
        "[VCP:1.0]",
        "[COMPOSITION:layered]",
        f"[LAYERS:{len(bundles)}]",
    ]

    # Add layer entries
    for i, bundle in enumerate(sorted_bundles, 1):
        manifest = bundle.manifest
        layer = manifest.composition.layer if manifest.composition else i
        hash_value = manifest.bundle.content_hash.split(":")[1]
        hash_short = f"{hash_value[:8]}...{hash_value[-4:]}"
        lines.append(f"[LAYER:{layer}:{manifest.bundle.id}@{manifest.bundle.version}:{hash_short}]")

    # Precedence (higher layer overrides lower)
    layers = [b.manifest.composition.layer if b.manifest.composition else i for i, b in enumerate(sorted_bundles, 1)]
    precedence = ">".join(str(layer) for layer in sorted(set(layers)))
    lines.append(f"[PRECEDENCE:{precedence}]")

    lines.append(f"[VERIFIED:{verified_at.isoformat()}Z]")
    lines.append("---BEGIN-CONSTITUTION---")

    # Add each constitution with layer marker
    for i, bundle in enumerate(sorted_bundles, 1):
        manifest = bundle.manifest
        layer = manifest.composition.layer if manifest.composition else i
        mode = manifest.composition.mode.value if manifest.composition else "extend"

        lines.append(f"\n## Layer {layer}: {manifest.metadata.get('title', manifest.bundle.id)} ({mode.upper()})")
        lines.append(bundle.content.rstrip())

    lines.append("\n---END-CONSTITUTION---")

    return "\n".join(lines)
