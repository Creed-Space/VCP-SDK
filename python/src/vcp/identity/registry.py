"""
VCP/I Registry with Privacy-Preserving Wildcard Queries.

Design Principles:
1. PRIVATE BY DEFAULT - Personal/org tokens not enumerable without authorization
2. PSEUDONYMOUS SUPPORT - Hash-based lookups, optional identity
3. WILDCARD QUERIES - Efficient pattern matching within authorized scope
4. ZERO-KNOWLEDGE PROOFS - Prove existence without revealing siblings

Privacy Model:
┌─────────────────────────────────────────────────────────────────────────┐
│                        REGISTRY PRIVACY TIERS                           │
├─────────────────────────────────────────────────────────────────────────┤
│  PUBLIC        │ Core namespaces (family.*, work.*, etc.)               │
│                │ Anyone can discover, enumerate, query                  │
├─────────────────────────────────────────────────────────────────────────┤
│  ORGANIZATIONAL│ company.acme.*, school.mit.*, etc.                     │
│                │ Existence public, details require org membership       │
│                │ Wildcard queries require org authorization             │
├─────────────────────────────────────────────────────────────────────────┤
│  COMMUNITY     │ religion.*, culture.*, community.*                     │
│                │ Existence public, moderation by community              │
│                │ Wildcard queries open to community members             │
├─────────────────────────────────────────────────────────────────────────┤
│  PERSONAL      │ user.alice.*, user.bob.*                               │
│                │ Existence hidden, only owner can enumerate             │
│                │ Others need exact token to resolve                     │
├─────────────────────────────────────────────────────────────────────────┤
│  PSEUDONYMOUS  │ anon.<hash>.*, pseudo.<hash>.*                         │
│                │ Hash-based identity, unlinkable to real identity       │
│                │ Encrypted metadata, ZK proofs for ownership            │
└─────────────────────────────────────────────────────────────────────────┘

Query Privacy:
- Exact lookup: Always allowed, reveals nothing about siblings
- Prefix query: Requires authorization for that prefix
- Pattern query: Scoped to authorized prefixes only
- Existence proof: Bloom filter, no enumeration possible
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .token import Token


class PrivacyTier(Enum):
    """Privacy tier for registry entries."""

    PUBLIC = "public"  # Anyone can discover and enumerate
    ORGANIZATIONAL = "organizational"  # Existence public, details restricted
    COMMUNITY = "community"  # Community-moderated access
    PERSONAL = "personal"  # Owner-only enumeration
    PSEUDONYMOUS = "pseudonymous"  # Hash-based, unlinkable


class QueryScope(Enum):
    """Scope of a wildcard query."""

    EXACT = "exact"  # Single token lookup
    PREFIX = "prefix"  # company.acme.** (everything under prefix)
    SUFFIX = "suffix"  # **.compliance (everything ending with)
    PATTERN = "pattern"  # *.*.legal.* (pattern with wildcards)


@dataclass
class RegistryEntry:
    """A registered token with metadata."""

    token: Token
    privacy_tier: PrivacyTier
    owner_id: str | None = None  # None for public/pseudonymous
    owner_pubkey: bytes | None = None  # For encrypted metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata_encrypted: bytes | None = None  # E(pubkey, metadata)
    metadata_public: dict = field(default_factory=dict)

    # Pseudonymous support
    pseudonym_salt: bytes | None = None  # For hash-based lookups
    pseudonym_proof: bytes | None = None  # ZK proof of ownership


@dataclass
class QueryResult:
    """Result of a registry query."""

    tokens: list[Token]
    total_count: int  # May be > len(tokens) if paginated
    has_more: bool
    scope_authorized: bool  # Whether requester had full scope access
    redacted_count: int = 0  # Tokens hidden due to privacy


@dataclass
class AuthorizationContext:
    """Authorization context for registry queries."""

    requester_id: str | None = None
    requester_pubkey: bytes | None = None
    org_memberships: set[str] = field(
        default_factory=set
    )  # e.g., {"acme", "mit"}
    community_memberships: set[str] = field(
        default_factory=set
    )
    owned_prefixes: set[str] = field(
        default_factory=set
    )  # e.g., {"user.alice"}
    is_admin: bool = False


class BloomFilter:
    """
    Space-efficient probabilistic set membership.

    Properties:
    - Can prove "definitely not in set" (no false negatives)
    - May say "possibly in set" (small false positive rate)
    - Cannot enumerate members (privacy-preserving)
    """

    def __init__(
        self,
        expected_items: int = 10000,
        false_positive_rate: float = 0.01,
    ):
        import math

        self.size = int(
            -expected_items
            * math.log(false_positive_rate)
            / (math.log(2) ** 2)
        )
        self.num_hashes = int(
            self.size / expected_items * math.log(2)
        )
        self.bit_array = bytearray(self.size // 8 + 1)
        self._count = 0

    def _hashes(self, item: str) -> Iterator[int]:
        """Generate hash positions for an item."""
        h1 = int(hashlib.sha256(item.encode()).hexdigest(), 16)
        h2 = int(hashlib.md5(item.encode()).hexdigest(), 16)
        for i in range(self.num_hashes):
            yield (h1 + i * h2) % self.size

    def add(self, item: str) -> None:
        """Add item to the filter."""
        for pos in self._hashes(item):
            self.bit_array[pos // 8] |= 1 << (pos % 8)
        self._count += 1

    def might_contain(self, item: str) -> bool:
        """Check if item might be in the filter."""
        return all(
            self.bit_array[pos // 8] & (1 << (pos % 8))
            for pos in self._hashes(item)
        )

    def __len__(self) -> int:
        return self._count


class PrefixTree:
    """
    Prefix tree (trie) for efficient wildcard queries.

    Each node has:
    - Children (next segments)
    - Entries (tokens ending at this node)
    - ACL (who can enumerate children)
    """

    @dataclass
    class Node:
        segment: str
        children: dict[str, PrefixTree.Node] = field(default_factory=dict)
        entries: list[RegistryEntry] = field(default_factory=list)
        privacy_tier: PrivacyTier = PrivacyTier.PUBLIC

    def __init__(self):
        self.root = self.Node(segment="")

    def insert(self, entry: RegistryEntry) -> None:
        """Insert an entry into the tree."""
        node = self.root
        for segment in entry.token.segments:
            if segment not in node.children:
                node.children[segment] = self.Node(segment=segment)
            node = node.children[segment]
            # Inherit strictest privacy tier
            if entry.privacy_tier.value > node.privacy_tier.value:
                node.privacy_tier = entry.privacy_tier
        node.entries.append(entry)

    def find_exact(self, token: Token) -> RegistryEntry | None:
        """Find exact token match."""
        node = self.root
        for segment in token.segments:
            if segment not in node.children:
                return None
            node = node.children[segment]
        # Find matching version/namespace
        for entry in node.entries:
            if entry.token.version == token.version:
                return entry
        return node.entries[0] if node.entries else None

    def find_prefix(
        self,
        prefix_segments: tuple[str, ...],
        auth: AuthorizationContext,
        max_results: int = 100,
    ) -> tuple[list[RegistryEntry], int]:
        """Find all entries under a prefix.

        Returns:
            Tuple of (entries, redacted_count)
        """
        # Navigate to prefix node
        node = self.root
        for segment in prefix_segments:
            if segment not in node.children:
                return [], 0
            node = node.children[segment]

        # Check authorization
        prefix_str = ".".join(prefix_segments)
        if not self._can_enumerate(node, prefix_str, auth):
            # Count all entries under this prefix as redacted
            redacted = self._count_entries(node)
            return [], redacted

        # Collect entries with redaction tracking
        return self._collect_entries(node, auth, max_results)

    def _count_entries(self, node: PrefixTree.Node) -> int:
        """Count all entries under a node (for redaction tracking)."""
        count = len(node.entries)
        for child in node.children.values():
            count += self._count_entries(child)
        return count

    def _can_enumerate(
        self,
        node: PrefixTree.Node,
        prefix: str,
        auth: AuthorizationContext,
    ) -> bool:
        """Check if requester can enumerate children of this node."""
        if auth.is_admin:
            return True

        if node.privacy_tier == PrivacyTier.PUBLIC:
            return True

        if node.privacy_tier == PrivacyTier.ORGANIZATIONAL:
            # Check org membership
            parts = prefix.split(".")
            if len(parts) >= 2 and parts[0] in ("company", "school", "ngo"):
                org_name = parts[1]
                return org_name in auth.org_memberships
            return False

        if node.privacy_tier == PrivacyTier.COMMUNITY:
            parts = prefix.split(".")
            if len(parts) >= 2 and parts[0] in ("religion", "culture", "community"):
                community_name = parts[1]
                return community_name in auth.community_memberships
            return False

        if node.privacy_tier == PrivacyTier.PERSONAL:
            return prefix in auth.owned_prefixes

        if node.privacy_tier == PrivacyTier.PSEUDONYMOUS:
            # Pseudonymous requires proof of ownership
            return prefix in auth.owned_prefixes

        return False

    def _collect_entries(
        self,
        node: PrefixTree.Node,
        auth: AuthorizationContext,
        max_results: int,
    ) -> tuple[list[RegistryEntry], int]:
        """Recursively collect entries from node and children.

        Returns:
            Tuple of (entries, redacted_count)
        """
        entries: list[RegistryEntry] = []
        redacted_holder = [0]

        self._collect_entries_recursive(node, auth, max_results, entries, redacted_holder)
        return entries, redacted_holder[0]

    def _collect_entries_recursive(
        self,
        node: PrefixTree.Node,
        auth: AuthorizationContext,
        max_results: int,
        entries: list[RegistryEntry],
        redacted_holder: list[int],
    ) -> None:
        """Recursively collect entries, mutating the lists."""
        for entry in node.entries:
            if len(entries) >= max_results:
                return
            if self._can_access_entry(entry, auth):
                entries.append(entry)
            else:
                redacted_holder[0] += 1

        for child in node.children.values():
            if len(entries) >= max_results:
                return
            self._collect_entries_recursive(child, auth, max_results, entries, redacted_holder)

    def _can_access_entry(
        self, entry: RegistryEntry, auth: AuthorizationContext
    ) -> bool:
        """Check if requester can access this entry."""
        if entry.privacy_tier == PrivacyTier.PUBLIC:
            return True
        if auth.is_admin:
            return True
        if entry.owner_id and entry.owner_id == auth.requester_id:
            return True

        # Check organizational membership
        if entry.privacy_tier == PrivacyTier.ORGANIZATIONAL:
            # Extract org name from token (second segment for company.acme.*)
            segments = entry.token.segments
            if len(segments) >= 2 and segments[0] in (
                "company", "school", "ngo", "org"
            ):
                org_name = segments[1]
                if org_name in auth.org_memberships:
                    return True

        # Check community membership
        if entry.privacy_tier == PrivacyTier.COMMUNITY:
            segments = entry.token.segments
            if len(segments) >= 2 and segments[0] in (
                "religion", "culture", "community"
            ):
                community_name = segments[1]
                if community_name in auth.community_memberships:
                    return True

        # Check owned prefixes for personal/pseudonymous
        if entry.privacy_tier in (
            PrivacyTier.PERSONAL, PrivacyTier.PSEUDONYMOUS
        ):
            canonical = entry.token.canonical
            for prefix in auth.owned_prefixes:
                if canonical.startswith(prefix):
                    return True

        return False


class Registry(ABC):
    """Abstract registry interface."""

    @abstractmethod
    def register(
        self,
        token: Token,
        privacy_tier: PrivacyTier = PrivacyTier.PUBLIC,
        owner_id: str | None = None,
        metadata: dict | None = None,
    ) -> RegistryEntry:
        """Register a new token."""
        ...

    @abstractmethod
    def resolve(self, token: Token) -> RegistryEntry | None:
        """Resolve a token to its entry (exact lookup, always allowed)."""
        ...

    @abstractmethod
    def exists(self, token: Token) -> bool:
        """Check if token exists (uses bloom filter, no enumeration)."""
        ...

    @abstractmethod
    def find(
        self,
        pattern: str,
        auth: AuthorizationContext,
        max_results: int = 100,
    ) -> QueryResult:
        """
        Find tokens matching pattern.

        Patterns:
        - "company.acme.**" - prefix query
        - "**.compliance" - suffix query
        - "*.*.legal.*" - pattern query

        Authorization required for non-public scopes.
        """
        ...

    @abstractmethod
    def subscribe(
        self,
        pattern: str,
        auth: AuthorizationContext,
        callback: callable,
    ) -> str:
        """Subscribe to changes matching pattern. Returns subscription ID."""
        ...


class LocalRegistry(Registry):
    """
    In-memory registry for development and testing.

    Production would use distributed registry with:
    - PostgreSQL for persistence
    - Redis for bloom filter caching
    - Kafka for change subscriptions
    """

    def __init__(self):
        self._tree = PrefixTree()
        self._bloom = BloomFilter()
        self._entries: dict[str, RegistryEntry] = {}
        self._subscriptions: dict[
            str, tuple[str, AuthorizationContext, callable]
        ] = {}

    def register(
        self,
        token: Token,
        privacy_tier: PrivacyTier = PrivacyTier.PUBLIC,
        owner_id: str | None = None,
        metadata: dict | None = None,
    ) -> RegistryEntry:
        """Register a new token."""
        entry = RegistryEntry(
            token=token,
            privacy_tier=privacy_tier,
            owner_id=owner_id,
            metadata_public=metadata or {},
        )

        # Add to structures
        self._tree.insert(entry)
        self._bloom.add(token.canonical)
        self._entries[token.canonical] = entry

        # Notify subscribers
        self._notify_subscribers(token, "created")

        return entry

    def resolve(self, token: Token) -> RegistryEntry | None:
        """Resolve exact token (always allowed, reveals nothing about siblings)."""
        return self._entries.get(token.canonical)

    def exists(self, token: Token) -> bool:
        """Check existence via bloom filter (no enumeration possible)."""
        if not self._bloom.might_contain(token.canonical):
            return False  # Definitely not present
        # Bloom says maybe - verify
        return token.canonical in self._entries

    def find(
        self,
        pattern: str,
        auth: AuthorizationContext,
        max_results: int = 100,
    ) -> QueryResult:
        """Find tokens matching pattern within authorized scope."""
        from .token import Token

        tokens = []
        redacted = 0

        if "**" in pattern:
            # Multi-segment wildcard
            if pattern.endswith(".**"):
                # Prefix query: company.acme.**
                prefix = pattern[:-3]
                prefix_segments = tuple(prefix.split("."))

                entries, prefix_redacted = self._tree.find_prefix(
                    prefix_segments, auth, max_results
                )
                tokens = [entry.token for entry in entries]
                redacted += prefix_redacted

            elif pattern.startswith("**."):
                # Suffix query: **.compliance
                suffix = pattern[3:]
                # Must scan all entries (expensive, but privacy-preserving)
                for canonical, entry in self._entries.items():
                    if not self._tree._can_access_entry(entry, auth):
                        redacted += 1
                        continue
                    if canonical.endswith(suffix):
                        tokens.append(entry.token)
                        if len(tokens) >= max_results:
                            break

            else:
                # Mixed pattern: company.**.compliance
                parts = pattern.split("**")
                prefix = parts[0].rstrip(".")
                suffix = parts[1].lstrip(".") if len(parts) > 1 else ""

                prefix_segments = tuple(prefix.split(".")) if prefix else ()

                entries, prefix_redacted = self._tree.find_prefix(
                    prefix_segments, auth, max_results * 2
                )
                redacted += prefix_redacted
                for entry in entries:
                    if suffix and not entry.token.canonical.endswith(suffix):
                        continue
                    tokens.append(entry.token)
                    if len(tokens) >= max_results:
                        break

        elif "*" in pattern:
            # Single-segment wildcards
            for canonical, entry in self._entries.items():
                if not self._tree._can_access_entry(entry, auth):
                    redacted += 1
                    continue
                if entry.token.matches_pattern(pattern):
                    tokens.append(entry.token)
                    if len(tokens) >= max_results:
                        break

        else:
            # Exact match
            entry = self.resolve(Token.parse(pattern))
            if entry:
                tokens.append(entry.token)

        return QueryResult(
            tokens=tokens,
            total_count=len(tokens) + redacted,
            has_more=len(tokens) >= max_results,
            scope_authorized=redacted == 0,
            redacted_count=redacted,
        )

    def subscribe(
        self,
        pattern: str,
        auth: AuthorizationContext,
        callback: callable,
    ) -> str:
        """Subscribe to changes matching pattern."""
        sub_id = secrets.token_hex(16)
        self._subscriptions[sub_id] = (pattern, auth, callback)
        return sub_id

    def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from changes."""
        if subscription_id in self._subscriptions:
            del self._subscriptions[subscription_id]
            return True
        return False

    def _notify_subscribers(
        self, token: Token, event: str
    ) -> None:
        """Notify subscribers of a change."""
        for sub_id, (pattern, auth, callback) in list(
            self._subscriptions.items()
        ):
            # Check if token matches the subscription pattern
            if not token.matches_pattern(pattern):
                continue

            # Check authorization - navigate to prefix node
            if "**" in pattern:
                prefix = pattern.split("**")[0].rstrip(".")
            elif "*" in pattern:
                prefix = pattern.split("*")[0].rstrip(".")
            else:
                prefix = pattern

            prefix_segments = (
                tuple(prefix.split(".")) if prefix else ()
            )

            # Navigate to the prefix node for authorization check
            node = self._tree.root
            for segment in prefix_segments:
                if segment in node.children:
                    node = node.children[segment]
                else:
                    break

            prefix_str = (
                ".".join(prefix_segments)
                if prefix_segments
                else ""
            )
            if self._tree._can_enumerate(
                node, prefix_str, auth
            ):
                try:
                    callback(token, event)
                except Exception as callback_err:
                    # Don't let callback errors break registry, but log for debugging
                    import logging

                    logging.getLogger(__name__).warning(
                        "Registry callback error "
                        f"(token={token}, event={event}): "
                        f"{type(callback_err).__name__}: "
                        f"{callback_err}"
                    )


class PseudonymousRegistry:
    """
    Registry extension for pseudonymous tokens.

    Features:
    - Hash-based token IDs (unlinkable to real identity)
    - Encrypted metadata (only owner can decrypt)
    - Zero-knowledge proofs of ownership
    - Onion routing for query privacy
    """

    def __init__(self, base_registry: Registry):
        self._base = base_registry
        self._pseudonym_salts: dict[str, bytes] = {}

    def generate_pseudonym(self, real_identity: str, secret: bytes) -> str:
        """Generate a pseudonymous identity hash."""
        salt = secrets.token_bytes(32)
        pseudonym = hmac.new(
            secret,
            f"{real_identity}:{salt.hex()}".encode(),
            hashlib.sha256,
        ).hexdigest()[:32]
        self._pseudonym_salts[pseudonym] = salt
        return pseudonym

    def register_pseudonymous(
        self,
        token: Token,
        pseudonym: str,
        encrypted_metadata: bytes,
    ) -> RegistryEntry:
        """Register a token under a pseudonymous identity."""
        return self._base.register(
            token=token,
            privacy_tier=PrivacyTier.PSEUDONYMOUS,
            owner_id=f"pseudo:{pseudonym}",
            metadata={"encrypted": encrypted_metadata.hex()},
        )

    def prove_ownership(
        self,
        token: Token,
        pseudonym: str,
        secret: bytes,
    ) -> bytes:
        """Generate zero-knowledge proof of ownership."""
        # Simplified: In production, use proper ZK-SNARK/STARK
        salt = self._pseudonym_salts.get(pseudonym, b"")
        proof = hmac.new(
            secret,
            f"{token.canonical}:{pseudonym}:{salt.hex()}".encode(),
            hashlib.sha256,
        ).digest()
        return proof

    def verify_ownership(
        self,
        token: Token,
        pseudonym: str,
        proof: bytes,
        secret: bytes,
    ) -> bool:
        """Verify a zero-knowledge ownership proof."""
        expected = self.prove_ownership(token, pseudonym, secret)
        return hmac.compare_digest(proof, expected)


# Convenience functions


def infer_privacy_tier(token: Token) -> PrivacyTier:
    """Infer privacy tier from token's first segment."""
    domain = token.domain

    # Core namespaces are public
    if domain in ("family", "work", "secure", "creative", "reality", "education", "health"):
        return PrivacyTier.PUBLIC

    # Organizational namespaces
    if domain in ("company", "school", "ngo", "org"):
        return PrivacyTier.ORGANIZATIONAL

    # Community namespaces
    if domain in ("religion", "culture", "community"):
        return PrivacyTier.COMMUNITY

    # Personal namespaces
    if domain == "user":
        return PrivacyTier.PERSONAL

    # Pseudonymous namespaces
    if domain in ("anon", "pseudo"):
        return PrivacyTier.PSEUDONYMOUS

    # Default to organizational (restrictive)
    return PrivacyTier.ORGANIZATIONAL


def create_authorization(
    requester_id: str | None = None,
    org_memberships: list[str] | None = None,
    community_memberships: list[str] | None = None,
    owned_prefixes: list[str] | None = None,
    is_admin: bool = False,
) -> AuthorizationContext:
    """Create an authorization context."""
    return AuthorizationContext(
        requester_id=requester_id,
        org_memberships=set(org_memberships or []),
        community_memberships=set(community_memberships or []),
        owned_prefixes=set(owned_prefixes or []),
        is_admin=is_admin,
    )
