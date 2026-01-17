"""
VCP/I (Identity Layer) - Token naming, namespace governance, and registry.

The foundational layer providing:
- Canonical naming (Token)
- Namespace governance (NamespaceTier)
- Privacy-preserving registry (Registry, LocalRegistry)
- Pseudonymous identity (PseudonymousRegistry)
"""

from .namespace import NamespaceConfig, NamespaceTier, validate_namespace_access
from .registry import (
    AuthorizationContext,
    BloomFilter,
    LocalRegistry,
    PrivacyTier,
    PseudonymousRegistry,
    QueryResult,
    QueryScope,
    Registry,
    RegistryEntry,
    create_authorization,
    infer_privacy_tier,
)
from .token import Token

__all__ = [
    # Token
    "Token",
    # Namespace
    "NamespaceTier",
    "NamespaceConfig",
    "validate_namespace_access",
    # Registry
    "Registry",
    "LocalRegistry",
    "PseudonymousRegistry",
    "RegistryEntry",
    "QueryResult",
    "QueryScope",
    "PrivacyTier",
    "AuthorizationContext",
    "BloomFilter",
    "create_authorization",
    "infer_privacy_tier",
]
