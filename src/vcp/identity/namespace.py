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
    """Namespace governance tiers."""

    CORE = "core"  # Reserved by Creed Space (family, work, health, etc.)
    ORGANIZATIONAL = "org"  # Verified organizations (company.acme.*)
    COMMUNITY = "community"  # Multi-stakeholder consensus
    PERSONAL = "personal"  # Individual users (user.*)


@dataclass
class NamespaceConfig:
    """Configuration for a namespace tier."""

    tier: NamespaceTier
    prefix_pattern: str
    registration_required: bool
    delegation_allowed: bool
    proof_type: str | None  # dns, email, consensus, none


# Core domains (reserved by Creed Space)
CORE_DOMAINS = frozenset(
    {
        "family",
        "work",
        "education",
        "health",
        "finance",
        "legal",
        "safety",
        "privacy",
        "accessibility",
        "environment",
    }
)

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
    """Infer the namespace tier from a token.

    Args:
        token: VCP/I Token

    Returns:
        Inferred namespace tier
    """
    if token.domain in CORE_DOMAINS:
        return NamespaceTier.CORE

    if token.domain.startswith("company-") or token.domain == "company":
        return NamespaceTier.ORGANIZATIONAL

    if token.domain.startswith("user-") or token.domain == "user":
        return NamespaceTier.PERSONAL

    return NamespaceTier.COMMUNITY


def validate_namespace_access(token: Token, tier: NamespaceTier) -> bool:
    """Check if token is valid for the given namespace tier.

    Args:
        token: VCP/I Token to validate
        tier: Required namespace tier

    Returns:
        True if token is valid for the tier
    """
    inferred = infer_tier(token)
    return inferred == tier


def get_tier_config(tier: NamespaceTier) -> NamespaceConfig:
    """Get configuration for a namespace tier.

    Args:
        tier: Namespace tier

    Returns:
        Configuration for the tier
    """
    return TIER_CONFIGS[tier]


def is_core_domain(domain: str) -> bool:
    """Check if a domain is a reserved core domain.

    Args:
        domain: Domain segment from token

    Returns:
        True if domain is reserved
    """
    return domain in CORE_DOMAINS
