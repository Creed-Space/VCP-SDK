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
