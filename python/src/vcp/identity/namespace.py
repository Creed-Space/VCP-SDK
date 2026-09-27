"""
VCP/I Namespace governance and validation.

Namespace tiers control who can publish constitutions under which domains.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .token import Token


class NamespaceTier(Enum):
    """Namespace governance tiers (VCP/I §4.2)."""

    CORE = "core"  # Reserved by Creed Space (family, work, secure, creative, reality)
    ORGANIZATIONAL = "org"  # Verified organizations (company.*, school.*, ngo.*)
    COMMUNITY = "community"  # Multi-stakeholder consensus (religion.*, culture.*, community.*)
    PERSONAL = "personal"  # Individual users (user.*)


@dataclass
class NamespaceConfig:
    """Configuration for a namespace tier."""

    tier: NamespaceTier
    prefix_pattern: str
    registration_required: bool
    delegation_allowed: bool
    proof_type: str | None  # dns, email, consensus, none


# Namespace prefixes by tier, from the VCP/I §3.2 and §4.2 tables and the
# identity token schema (core_namespace, org_prefix, community_prefix).
# The first token segment selects the tier.

# Core domains (reserved by Creed Space)
CORE_DOMAINS = frozenset({"family", "work", "secure", "creative", "reality"})

# Organizational prefixes (delegated to verified organizations)
ORG_PREFIXES = frozenset({"company", "school", "ngo"})

# Community prefixes (multi-stakeholder consensus)
COMMUNITY_PREFIXES = frozenset({"religion", "culture", "community"})

# Personal prefix (individual control)
PERSONAL_PREFIX = "user"

# Reserved words that MUST NOT be used as segments (VCP/I §3.7.1). They are
# a validator and registry rule; the identity schema does not encode them.
RESERVED_WORDS = frozenset(
    {
        "system",
        "admin",
        "root",
        "null",
        "undefined",
        "true",
        "false",
        "none",
        "void",
        "default",
        "api",
        "internal",
        "private",
        "public",
        "test",
        "debug",
        "staging",
        "production",
        "vcp",
        "uvc",
        "csm",
        "bundle",
        "manifest",
        "creed",
        "official",
        "verified",
        "authentic",
        "real",
    }
)

# Number of segments a Core token must have (VCP/I §3.1.1, §3.4.1).
CORE_TOKEN_SEGMENTS = 3


class TokenValidationError(ValueError):
    """A syntactically valid token that fails VCP/I semantic validation.

    ``code`` is one of ``unknown_namespace_prefix``, ``core_segment_count``
    or ``reserved_word``.
    """

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


_PREFIX_TIERS: dict[str, NamespaceTier] = {
    **{prefix: NamespaceTier.CORE for prefix in CORE_DOMAINS},
    **{prefix: NamespaceTier.ORGANIZATIONAL for prefix in ORG_PREFIXES},
    **{prefix: NamespaceTier.COMMUNITY for prefix in COMMUNITY_PREFIXES},
    PERSONAL_PREFIX: NamespaceTier.PERSONAL,
}

# Tier configurations
TIER_CONFIGS = {
    NamespaceTier.CORE: NamespaceConfig(
        tier=NamespaceTier.CORE,
        prefix_pattern="",  # No prefix, just core domains
        registration_required=False,  # Pre-defined
        delegation_allowed=False,
        proof_type=None,
    ),
    NamespaceTier.ORGANIZATIONAL: NamespaceConfig(
        tier=NamespaceTier.ORGANIZATIONAL,
        prefix_pattern="company.",
        registration_required=True,
        delegation_allowed=True,
        proof_type="dns",  # DNS TXT record verification
    ),
    NamespaceTier.COMMUNITY: NamespaceConfig(
        tier=NamespaceTier.COMMUNITY,
        prefix_pattern="",  # Various prefixes
        registration_required=True,
        delegation_allowed=True,
        proof_type="consensus",  # Multi-stakeholder approval
    ),
    NamespaceTier.PERSONAL: NamespaceConfig(
        tier=NamespaceTier.PERSONAL,
        prefix_pattern="user.",
        registration_required=True,
        delegation_allowed=False,
        proof_type="email",  # Email verification
    ),
}


def infer_tier(token: Token) -> NamespaceTier:
    """Infer the namespace tier from a token's first segment.

    Args:
        token: VCP/I Token

    Returns:
        Inferred namespace tier

    Raises:
        ValueError: If the first segment is not a namespace prefix listed in
            VCP/I §4.2. The specification treats an unknown prefix as an
            invalid namespace, so no tier is assumed for it.
    """
    tier = _PREFIX_TIERS.get(token.domain)
    if tier is None:
        raise ValueError(f"Unknown namespace prefix: {token.domain!r}")
    return tier


def validate_namespace_access(token: Token, tier: NamespaceTier) -> bool:
    """Check if token is valid for the given namespace tier.

    Fails closed: a token whose first segment is not a known namespace
    prefix is valid for no tier.

    Args:
        token: VCP/I Token to validate
        tier: Required namespace tier

    Returns:
        True if token is valid for the tier
    """
    try:
        inferred = infer_tier(token)
    except ValueError:
        return False
    return inferred == tier


def get_tier_config(tier: NamespaceTier) -> NamespaceConfig:
    """Get configuration for a namespace tier.

    Args:
        tier: Namespace tier

    Returns:
        Configuration for the tier
    """
    return TIER_CONFIGS[tier]


def validate_token_semantics(token: Token) -> NamespaceTier:
    """Apply the VCP/I §3.4.1 semantic rules to a parsed token.

    ``Token.parse`` checks syntax only (the §3.4 ABNF and the schema
    ``pattern``). A conforming validator also requires a listed namespace
    prefix, exactly three segments for a Core token, and no reserved word
    (§3.7.1) in any segment.

    Args:
        token: Syntactically valid token

    Returns:
        The token's namespace tier

    Raises:
        TokenValidationError: If a semantic rule fails
    """
    tier = _PREFIX_TIERS.get(token.domain)
    if tier is None:
        raise TokenValidationError(
            "unknown_namespace_prefix",
            f"Unknown namespace prefix: {token.domain!r} (VCP/I §4.2 lists "
            "family, work, secure, creative, reality, company, school, ngo, "
            "religion, culture, community and user)",
        )
    if tier is NamespaceTier.CORE and len(token.segments) != CORE_TOKEN_SEGMENTS:
        raise TokenValidationError(
            "core_segment_count",
            f"Core namespace {token.domain!r} requires exactly "
            f"{CORE_TOKEN_SEGMENTS} segments, got {len(token.segments)}",
        )
    for index, segment in enumerate(token.segments, start=1):
        if segment in RESERVED_WORDS:
            raise TokenValidationError(
                "reserved_word", f"Segment {index} is a reserved word: {segment!r}"
            )
    return tier


def is_known_namespace(domain: str) -> bool:
    """Check if a domain is a namespace prefix listed in VCP/I §4.2.

    Args:
        domain: First segment of a token

    Returns:
        True if the prefix belongs to one of the four tiers
    """
    return domain in _PREFIX_TIERS


def is_core_domain(domain: str) -> bool:
    """Check if a domain is a reserved core domain.

    Args:
        domain: Domain segment from token

    Returns:
        True if domain is reserved
    """
    return domain in CORE_DOMAINS
