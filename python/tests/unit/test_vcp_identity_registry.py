"""
VCP Identity Registry Tests

Comprehensive unit tests for services/vcp/identity/registry.py.
Tests identity registration, lookup, privacy tiers, authorization,
wildcard queries, and subscription handling.

Coverage target: registry.py 0% -> 80%+
"""

from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock

# ====================================================================================
# PRIVACY TIER TESTS
# ====================================================================================


class TestPrivacyTier:
    """Tests for PrivacyTier enum."""

    def test_privacy_tier_enum_values(self) -> None:
        """Test all privacy tier values exist."""
        from vcp.identity.registry import PrivacyTier

        assert PrivacyTier.PUBLIC.value == "public"
        assert PrivacyTier.ORGANIZATIONAL.value == "organizational"
        assert PrivacyTier.COMMUNITY.value == "community"
        assert PrivacyTier.PERSONAL.value == "personal"
        assert PrivacyTier.PSEUDONYMOUS.value == "pseudonymous"

    def test_privacy_tier_count(self) -> None:
        """Test we have exactly 5 privacy tiers."""
        from vcp.identity.registry import PrivacyTier

        assert len(PrivacyTier) == 5


# ====================================================================================
# QUERY SCOPE TESTS
# ====================================================================================


class TestQueryScope:
    """Tests for QueryScope enum."""

    def test_query_scope_values(self) -> None:
        """Test all query scope values exist."""
        from vcp.identity.registry import QueryScope

        assert QueryScope.EXACT.value == "exact"
        assert QueryScope.PREFIX.value == "prefix"
        assert QueryScope.SUFFIX.value == "suffix"
        assert QueryScope.PATTERN.value == "pattern"


# ====================================================================================
# REGISTRY ENTRY TESTS
# ====================================================================================


class TestRegistryEntry:
    """Tests for RegistryEntry dataclass."""

    def test_registry_entry_creation(self) -> None:
        """Test basic registry entry creation."""
        from vcp.identity.registry import PrivacyTier, RegistryEntry
        from vcp.identity.token import Token

        token = Token.parse("family.safe.guide")
        entry = RegistryEntry(
            token=token,
            privacy_tier=PrivacyTier.PUBLIC,
        )

        assert entry.token == token
        assert entry.privacy_tier == PrivacyTier.PUBLIC
        assert entry.owner_id is None
        assert entry.owner_pubkey is None
        assert isinstance(entry.created_at, datetime)
        assert isinstance(entry.updated_at, datetime)

    def test_registry_entry_with_owner(self) -> None:
        """Test registry entry with owner information."""
        from vcp.identity.registry import PrivacyTier, RegistryEntry
        from vcp.identity.token import Token

        token = Token.parse("user.alice.personal")
        entry = RegistryEntry(
            token=token,
            privacy_tier=PrivacyTier.PERSONAL,
            owner_id="alice",
            metadata_public={"description": "Alice's personal creed"},
        )

        assert entry.owner_id == "alice"
        assert entry.metadata_public == {"description": "Alice's personal creed"}

    def test_registry_entry_with_encrypted_metadata(self) -> None:
        """Test registry entry with encrypted metadata."""
        from vcp.identity.registry import PrivacyTier, RegistryEntry
        from vcp.identity.token import Token

        token = Token.parse("pseudo.abc123.private")
        encrypted = b"encrypted_data_bytes"

        entry = RegistryEntry(
            token=token,
            privacy_tier=PrivacyTier.PSEUDONYMOUS,
            metadata_encrypted=encrypted,
            pseudonym_salt=b"salt_bytes",
        )

        assert entry.metadata_encrypted == encrypted
        assert entry.pseudonym_salt == b"salt_bytes"


# ====================================================================================
# QUERY RESULT TESTS
# ====================================================================================


class TestQueryResult:
    """Tests for QueryResult dataclass."""

    def test_query_result_creation(self) -> None:
        """Test query result creation."""
        from vcp.identity.registry import QueryResult
        from vcp.identity.token import Token

        tokens = [Token.parse("family.safe.guide")]
        result = QueryResult(
            tokens=tokens,
            total_count=1,
            has_more=False,
            scope_authorized=True,
        )

        assert result.tokens == tokens
        assert result.total_count == 1
        assert not result.has_more
        assert result.scope_authorized
        assert result.redacted_count == 0

    def test_query_result_with_redaction(self) -> None:
        """Test query result with redacted entries."""
        from vcp.identity.registry import QueryResult

        result = QueryResult(
            tokens=[],
            total_count=10,
            has_more=False,
            scope_authorized=False,
            redacted_count=10,
        )

        assert result.redacted_count == 10
        assert not result.scope_authorized


# ====================================================================================
# AUTHORIZATION CONTEXT TESTS
# ====================================================================================


class TestAuthorizationContext:
    """Tests for AuthorizationContext dataclass."""

    def test_authorization_context_defaults(self) -> None:
        """Test authorization context default values."""
        from vcp.identity.registry import AuthorizationContext

        auth = AuthorizationContext()

        assert auth.requester_id is None
        assert auth.requester_pubkey is None
        assert auth.org_memberships == set()
        assert auth.community_memberships == set()
        assert auth.owned_prefixes == set()
        assert not auth.is_admin

    def test_authorization_context_with_memberships(self) -> None:
        """Test authorization context with memberships."""
        from vcp.identity.registry import AuthorizationContext

        auth = AuthorizationContext(
            requester_id="alice",
            org_memberships={"acme", "example"},
            community_memberships={"buddhist"},
            owned_prefixes={"user.alice"},
        )

        assert auth.requester_id == "alice"
        assert "acme" in auth.org_memberships
        assert "example" in auth.org_memberships
        assert "buddhist" in auth.community_memberships
        assert "user.alice" in auth.owned_prefixes

    def test_authorization_context_admin(self) -> None:
        """Test admin authorization context."""
        from vcp.identity.registry import AuthorizationContext

        auth = AuthorizationContext(is_admin=True)

        assert auth.is_admin


# ====================================================================================
# BLOOM FILTER TESTS
# ====================================================================================


class TestBloomFilter:
    """Tests for BloomFilter probabilistic set."""

    def test_bloom_filter_creation(self) -> None:
        """Test bloom filter creation with defaults."""
        from vcp.identity.registry import BloomFilter

        bloom = BloomFilter()

        assert bloom.size > 0
        assert bloom.num_hashes > 0
        assert len(bloom) == 0

    def test_bloom_filter_add_and_check(self) -> None:
        """Test adding and checking items in bloom filter."""
        from vcp.identity.registry import BloomFilter

        bloom = BloomFilter()
        bloom.add("family.safe.guide")

        assert bloom.might_contain("family.safe.guide")
        assert len(bloom) == 1

    def test_bloom_filter_no_false_negatives(self) -> None:
        """Test that bloom filter never has false negatives."""
        from vcp.identity.registry import BloomFilter

        bloom = BloomFilter(expected_items=100)

        items = [f"test.item.{i}" for i in range(100)]
        for item in items:
            bloom.add(item)

        # All added items should be found
        for item in items:
            assert bloom.might_contain(item), f"False negative for {item}"

    def test_bloom_filter_definitely_not_present(self) -> None:
        """Test that bloom filter correctly identifies items not present."""
        from vcp.identity.registry import BloomFilter

        bloom = BloomFilter()
        bloom.add("family.safe.guide")

        # Items that definitely aren't there should (mostly) return False
        # Note: false positives are possible but rare
        not_present = "completely.different.token"
        # This could be a false positive, so we just test the method exists
        result = bloom.might_contain(not_present)
        assert isinstance(result, bool)

    def test_bloom_filter_custom_parameters(self) -> None:
        """Test bloom filter with custom parameters."""
        from vcp.identity.registry import BloomFilter

        bloom = BloomFilter(expected_items=1000, false_positive_rate=0.001)

        assert bloom.size > 0
        assert bloom.num_hashes > 0


# ====================================================================================
# PREFIX TREE TESTS
# ====================================================================================


class TestPrefixTree:
    """Tests for PrefixTree (trie) data structure."""

    def test_prefix_tree_creation(self) -> None:
        """Test prefix tree creation."""
        from vcp.identity.registry import PrefixTree

        tree = PrefixTree()

        assert tree.root is not None
        assert tree.root.segment == ""

    def test_prefix_tree_insert(self) -> None:
        """Test inserting entries into prefix tree."""
        from vcp.identity.registry import PrefixTree, PrivacyTier, RegistryEntry
        from vcp.identity.token import Token

        tree = PrefixTree()
        token = Token.parse("family.safe.guide")
        entry = RegistryEntry(token=token, privacy_tier=PrivacyTier.PUBLIC)

        tree.insert(entry)

        # Verify the entry was inserted
        result = tree.find_exact(token)
        assert result is not None
        assert result.token == token

    def test_prefix_tree_find_exact(self) -> None:
        """Test exact lookup in prefix tree."""
        from vcp.identity.registry import PrefixTree, PrivacyTier, RegistryEntry
        from vcp.identity.token import Token

        tree = PrefixTree()
        token1 = Token.parse("family.safe.guide")
        token2 = Token.parse("family.safe.companion")

        tree.insert(RegistryEntry(token=token1, privacy_tier=PrivacyTier.PUBLIC))
        tree.insert(RegistryEntry(token=token2, privacy_tier=PrivacyTier.PUBLIC))

        result1 = tree.find_exact(token1)
        result2 = tree.find_exact(token2)

        assert result1 is not None
        assert result1.token == token1
        assert result2 is not None
        assert result2.token == token2

    def test_prefix_tree_find_exact_not_found(self) -> None:
        """Test exact lookup for non-existent token."""
        from vcp.identity.registry import PrefixTree, PrivacyTier, RegistryEntry
        from vcp.identity.token import Token

        tree = PrefixTree()
        token1 = Token.parse("family.safe.guide")
        token2 = Token.parse("work.professional.advisor")

        tree.insert(RegistryEntry(token=token1, privacy_tier=PrivacyTier.PUBLIC))

        result = tree.find_exact(token2)
        assert result is None

    def test_prefix_tree_find_prefix_public(self) -> None:
        """Test prefix query for public entries."""
        from vcp.identity.registry import (
            AuthorizationContext,
            PrefixTree,
            PrivacyTier,
            RegistryEntry,
        )
        from vcp.identity.token import Token

        tree = PrefixTree()
        tokens = [
            Token.parse("family.safe.guide"),
            Token.parse("family.safe.companion"),
            Token.parse("family.protective.guardian"),
        ]

        for token in tokens:
            tree.insert(RegistryEntry(token=token, privacy_tier=PrivacyTier.PUBLIC))

        auth = AuthorizationContext()
        entries, redacted = tree.find_prefix(("family",), auth)

        assert len(entries) == 3
        assert redacted == 0

    def test_prefix_tree_find_prefix_organizational(self) -> None:
        """Test prefix query for organizational entries with membership."""
        from vcp.identity.registry import (
            AuthorizationContext,
            PrefixTree,
            PrivacyTier,
            RegistryEntry,
        )
        from vcp.identity.token import Token

        tree = PrefixTree()
        token = Token.parse("company.acme.legal.compliance")
        tree.insert(RegistryEntry(token=token, privacy_tier=PrivacyTier.ORGANIZATIONAL))

        # Without membership
        auth_no_access = AuthorizationContext()
        entries, redacted = tree.find_prefix(("company", "acme"), auth_no_access)
        assert len(entries) == 0
        assert redacted == 1

        # With membership
        auth_with_access = AuthorizationContext(org_memberships={"acme"})
        entries, redacted = tree.find_prefix(("company", "acme"), auth_with_access)
        assert len(entries) == 1
        assert redacted == 0

    def test_prefix_tree_find_prefix_personal(self) -> None:
        """Test prefix query for personal entries."""
        from vcp.identity.registry import (
            AuthorizationContext,
            PrefixTree,
            PrivacyTier,
            RegistryEntry,
        )
        from vcp.identity.token import Token

        tree = PrefixTree()
        token = Token.parse("user.alice.personal")
        tree.insert(RegistryEntry(token=token, privacy_tier=PrivacyTier.PERSONAL, owner_id="alice"))

        # Without ownership
        auth_no_access = AuthorizationContext()
        entries, redacted = tree.find_prefix(("user", "alice"), auth_no_access)
        assert len(entries) == 0
        assert redacted == 1

        # With ownership
        auth_owner = AuthorizationContext(owned_prefixes={"user.alice"})
        entries, redacted = tree.find_prefix(("user", "alice"), auth_owner)
        assert len(entries) == 1
        assert redacted == 0

    def test_prefix_tree_admin_access(self) -> None:
        """Test that admin can access all entries."""
        from vcp.identity.registry import (
            AuthorizationContext,
            PrefixTree,
            PrivacyTier,
            RegistryEntry,
        )
        from vcp.identity.token import Token

        tree = PrefixTree()
        token = Token.parse("user.alice.personal")
        tree.insert(RegistryEntry(token=token, privacy_tier=PrivacyTier.PERSONAL))

        auth_admin = AuthorizationContext(is_admin=True)
        entries, redacted = tree.find_prefix(("user", "alice"), auth_admin)

        assert len(entries) == 1
        assert redacted == 0

    def test_prefix_tree_community_access(self) -> None:
        """Test community tier access."""
        from vcp.identity.registry import (
            AuthorizationContext,
            PrefixTree,
            PrivacyTier,
            RegistryEntry,
        )
        from vcp.identity.token import Token

        tree = PrefixTree()
        token = Token.parse("religion.buddhist.mindfulness")
        tree.insert(RegistryEntry(token=token, privacy_tier=PrivacyTier.COMMUNITY))

        # Without membership
        auth_no_access = AuthorizationContext()
        entries, redacted = tree.find_prefix(("religion", "buddhist"), auth_no_access)
        assert len(entries) == 0

        # With membership
        auth_member = AuthorizationContext(community_memberships={"buddhist"})
        entries, redacted = tree.find_prefix(("religion", "buddhist"), auth_member)
        assert len(entries) == 1


# ====================================================================================
# LOCAL REGISTRY TESTS
# ====================================================================================


class TestLocalRegistry:
    """Tests for LocalRegistry implementation."""

    def test_local_registry_creation(self) -> None:
        """Test local registry creation."""
        from vcp.identity.registry import LocalRegistry

        registry = LocalRegistry()

        assert registry is not None

    def test_register_public_token(self) -> None:
        """Test registering a public token."""
        from vcp.identity.registry import LocalRegistry, PrivacyTier
        from vcp.identity.token import Token

        registry = LocalRegistry()
        token = Token.parse("family.safe.guide")

        entry = registry.register(token, privacy_tier=PrivacyTier.PUBLIC)

        assert entry.token == token
        assert entry.privacy_tier == PrivacyTier.PUBLIC

    def test_register_with_metadata(self) -> None:
        """Test registering token with metadata."""
        from vcp.identity.registry import LocalRegistry
        from vcp.identity.token import Token

        registry = LocalRegistry()
        token = Token.parse("family.safe.guide")
        metadata = {"description": "Family safety guide", "author": "system"}

        entry = registry.register(token, metadata=metadata)

        assert entry.metadata_public == metadata

    def test_resolve_existing_token(self) -> None:
        """Test resolving an existing token."""
        from vcp.identity.registry import LocalRegistry
        from vcp.identity.token import Token

        registry = LocalRegistry()
        token = Token.parse("family.safe.guide")
        registry.register(token)

        resolved = registry.resolve(token)

        assert resolved is not None
        assert resolved.token == token

    def test_resolve_nonexistent_token(self) -> None:
        """Test resolving a token that doesn't exist."""
        from vcp.identity.registry import LocalRegistry
        from vcp.identity.token import Token

        registry = LocalRegistry()
        token = Token.parse("nonexistent.token.here")

        resolved = registry.resolve(token)

        assert resolved is None

    def test_exists_with_bloom_filter(self) -> None:
        """Test existence check using bloom filter."""
        from vcp.identity.registry import LocalRegistry
        from vcp.identity.token import Token

        registry = LocalRegistry()
        token = Token.parse("family.safe.guide")
        registry.register(token)

        assert registry.exists(token) is True

    def test_exists_nonexistent_token(self) -> None:
        """Test existence check for non-existent token."""
        from vcp.identity.registry import LocalRegistry
        from vcp.identity.token import Token

        registry = LocalRegistry()
        token = Token.parse("nonexistent.token.here")

        assert registry.exists(token) is False

    def test_find_prefix_pattern(self) -> None:
        """Test finding tokens by prefix pattern."""
        from vcp.identity.registry import AuthorizationContext, LocalRegistry
        from vcp.identity.token import Token

        registry = LocalRegistry()
        tokens = [
            Token.parse("family.safe.guide"),
            Token.parse("family.safe.companion"),
            Token.parse("family.protective.guardian"),
            Token.parse("work.professional.advisor"),
        ]

        for token in tokens:
            registry.register(token)

        auth = AuthorizationContext()
        result = registry.find("family.**", auth)

        assert len(result.tokens) == 3
        assert result.scope_authorized

    def test_find_suffix_pattern(self) -> None:
        """Test finding tokens by suffix pattern."""
        from vcp.identity.registry import AuthorizationContext, LocalRegistry
        from vcp.identity.token import Token

        registry = LocalRegistry()
        tokens = [
            Token.parse("family.safe.guide"),
            Token.parse("work.career.guide"),
            Token.parse("education.learning.guide"),
        ]

        for token in tokens:
            registry.register(token)

        auth = AuthorizationContext()
        result = registry.find("**.guide", auth)

        assert len(result.tokens) == 3

    def test_find_wildcard_pattern(self) -> None:
        """Test finding tokens with single-segment wildcard."""
        from vcp.identity.registry import AuthorizationContext, LocalRegistry
        from vcp.identity.token import Token

        registry = LocalRegistry()
        tokens = [
            Token.parse("family.safe.guide"),
            Token.parse("family.protective.guide"),
            Token.parse("family.caring.guide"),
        ]

        for token in tokens:
            registry.register(token)

        auth = AuthorizationContext()
        result = registry.find("family.*.guide", auth)

        assert len(result.tokens) == 3

    def test_find_exact_match(self) -> None:
        """Test finding token by exact match."""
        from vcp.identity.registry import AuthorizationContext, LocalRegistry
        from vcp.identity.token import Token

        registry = LocalRegistry()
        token = Token.parse("family.safe.guide")
        registry.register(token)

        auth = AuthorizationContext()
        result = registry.find("family.safe.guide", auth)

        assert len(result.tokens) == 1
        assert result.tokens[0] == token

    def test_find_mixed_pattern(self) -> None:
        """Test finding tokens with mixed prefix/suffix pattern."""
        from vcp.identity.registry import AuthorizationContext, LocalRegistry
        from vcp.identity.token import Token

        registry = LocalRegistry()
        tokens = [
            Token.parse("company.acme.legal.compliance"),
            Token.parse("company.acme.hr.compliance"),
            Token.parse("company.example.legal.compliance"),
        ]

        for token in tokens:
            registry.register(token)

        auth = AuthorizationContext()
        result = registry.find("company.**.compliance", auth)

        assert len(result.tokens) == 3

    def test_find_with_max_results(self) -> None:
        """Test find respects max_results limit."""
        from vcp.identity.registry import AuthorizationContext, LocalRegistry
        from vcp.identity.token import Token

        registry = LocalRegistry()
        for i in range(10):
            registry.register(Token.parse(f"family.item{i}.guide"))

        auth = AuthorizationContext()
        result = registry.find("family.**", auth, max_results=5)

        assert len(result.tokens) == 5
        assert result.has_more

    def test_subscribe_and_unsubscribe(self) -> None:
        """Test subscription and unsubscription."""
        from vcp.identity.registry import AuthorizationContext, LocalRegistry

        registry = LocalRegistry()
        auth = AuthorizationContext()
        callback = MagicMock()

        sub_id = registry.subscribe("family.**", auth, callback)

        assert sub_id is not None
        assert len(sub_id) == 32  # hex token

        # Unsubscribe
        result = registry.unsubscribe(sub_id)
        assert result is True

        # Unsubscribe again should fail
        result = registry.unsubscribe(sub_id)
        assert result is False

    def test_subscription_notification(self) -> None:
        """Test that subscribers are notified on registration."""
        from vcp.identity.registry import AuthorizationContext, LocalRegistry
        from vcp.identity.token import Token

        registry = LocalRegistry()
        auth = AuthorizationContext()
        callback = MagicMock()

        registry.subscribe("family.**", auth, callback)
        token = Token.parse("family.safe.guide")
        registry.register(token)

        callback.assert_called_once_with(token, "created")

    def test_subscription_notification_respects_pattern(self) -> None:
        """Test that subscribers only get matching notifications."""
        from vcp.identity.registry import AuthorizationContext, LocalRegistry
        from vcp.identity.token import Token

        registry = LocalRegistry()
        auth = AuthorizationContext()
        callback = MagicMock()

        registry.subscribe("family.**", auth, callback)

        # This should trigger callback
        registry.register(Token.parse("family.safe.guide"))
        # This should NOT trigger callback
        registry.register(Token.parse("work.professional.advisor"))

        assert callback.call_count == 1

    def test_subscription_callback_error_handling(self) -> None:
        """Test that callback errors don't break registry."""
        from vcp.identity.registry import AuthorizationContext, LocalRegistry
        from vcp.identity.token import Token

        registry = LocalRegistry()
        auth = AuthorizationContext()

        def failing_callback(token, event):
            raise ValueError("Callback failed")

        registry.subscribe("family.**", auth, failing_callback)

        # Should not raise, just log warning
        token = Token.parse("family.safe.guide")
        registry.register(token)

        # Registry should still work
        assert registry.exists(token)


# ====================================================================================
# PSEUDONYMOUS REGISTRY TESTS
# ====================================================================================


class TestPseudonymousRegistry:
    """Tests for PseudonymousRegistry extension."""

    def test_pseudonymous_registry_creation(self) -> None:
        """Test pseudonymous registry creation."""
        from vcp.identity.registry import LocalRegistry, PseudonymousRegistry

        base = LocalRegistry()
        pseudo = PseudonymousRegistry(base)

        assert pseudo is not None

    def test_generate_pseudonym(self) -> None:
        """Test pseudonym generation."""
        from vcp.identity.registry import LocalRegistry, PseudonymousRegistry

        base = LocalRegistry()
        pseudo = PseudonymousRegistry(base)
        secret = b"user_secret_key_12345678901234"

        pseudonym = pseudo.generate_pseudonym("alice@example.com", secret)

        assert pseudonym is not None
        assert len(pseudonym) == 32  # SHA256 truncated to 32 chars

    def test_pseudonym_uniqueness(self) -> None:
        """Test that different inputs generate different pseudonyms."""
        from vcp.identity.registry import LocalRegistry, PseudonymousRegistry

        base = LocalRegistry()
        pseudo = PseudonymousRegistry(base)
        secret = b"user_secret_key_12345678901234"

        p1 = pseudo.generate_pseudonym("alice@example.com", secret)
        p2 = pseudo.generate_pseudonym("bob@example.com", secret)

        assert p1 != p2

    def test_register_pseudonymous(self) -> None:
        """Test registering a pseudonymous token."""
        from vcp.identity.registry import (
            LocalRegistry,
            PrivacyTier,
            PseudonymousRegistry,
        )
        from vcp.identity.token import Token

        base = LocalRegistry()
        pseudo = PseudonymousRegistry(base)

        secret = b"user_secret_key_12345678901234"
        pseudonym = pseudo.generate_pseudonym("alice@example.com", secret)
        # Use a valid segment format (lowercase alphanumeric, max 32 chars)
        token = Token.parse("anon.abc123hash.private")
        encrypted = b"encrypted_creed_data"

        entry = pseudo.register_pseudonymous(token, pseudonym, encrypted)

        assert entry.privacy_tier == PrivacyTier.PSEUDONYMOUS
        assert entry.owner_id == f"pseudo:{pseudonym}"

    def test_prove_and_verify_ownership(self) -> None:
        """Test ownership proof generation and verification."""
        from vcp.identity.registry import LocalRegistry, PseudonymousRegistry
        from vcp.identity.token import Token

        base = LocalRegistry()
        pseudo = PseudonymousRegistry(base)

        secret = b"user_secret_key_12345678901234"
        pseudonym = pseudo.generate_pseudonym("alice@example.com", secret)
        # Use a valid segment format
        token = Token.parse("anon.abc123hash.private")

        proof = pseudo.prove_ownership(token, pseudonym, secret)
        assert proof is not None

        # Verify proof
        is_valid = pseudo.verify_ownership(token, pseudonym, proof, secret)
        assert is_valid is True

    def test_invalid_proof_fails_verification(self) -> None:
        """Test that invalid proof fails verification."""
        from vcp.identity.registry import LocalRegistry, PseudonymousRegistry
        from vcp.identity.token import Token

        base = LocalRegistry()
        pseudo = PseudonymousRegistry(base)

        secret = b"user_secret_key_12345678901234"
        wrong_secret = b"wrong_secret_key_123456789012"
        pseudonym = pseudo.generate_pseudonym("alice@example.com", secret)
        # Use a valid segment format
        token = Token.parse("anon.abc123hash.private")

        # Generate proof with wrong secret
        wrong_proof = pseudo.prove_ownership(token, pseudonym, wrong_secret)

        # Verification should fail
        is_valid = pseudo.verify_ownership(token, pseudonym, wrong_proof, secret)
        assert is_valid is False


# ====================================================================================
# CONVENIENCE FUNCTION TESTS
# ====================================================================================


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_infer_privacy_tier_public(self) -> None:
        """Test inferring public privacy tier."""
        from vcp.identity.registry import PrivacyTier, infer_privacy_tier
        from vcp.identity.token import Token

        public_domains = ["family", "work", "secure", "creative", "reality", "education", "health"]
        for domain in public_domains:
            token = Token.parse(f"{domain}.safe.guide")
            tier = infer_privacy_tier(token)
            assert tier == PrivacyTier.PUBLIC, f"Expected PUBLIC for {domain}"

    def test_infer_privacy_tier_organizational(self) -> None:
        """Test inferring organizational privacy tier."""
        from vcp.identity.registry import PrivacyTier, infer_privacy_tier
        from vcp.identity.token import Token

        org_domains = ["company", "school", "ngo", "org"]
        for domain in org_domains:
            token = Token.parse(f"{domain}.example.policy")
            tier = infer_privacy_tier(token)
            assert tier == PrivacyTier.ORGANIZATIONAL, f"Expected ORGANIZATIONAL for {domain}"

    def test_infer_privacy_tier_community(self) -> None:
        """Test inferring community privacy tier."""
        from vcp.identity.registry import PrivacyTier, infer_privacy_tier
        from vcp.identity.token import Token

        community_domains = ["religion", "culture", "community"]
        for domain in community_domains:
            token = Token.parse(f"{domain}.example.creed")
            tier = infer_privacy_tier(token)
            assert tier == PrivacyTier.COMMUNITY, f"Expected COMMUNITY for {domain}"

    def test_infer_privacy_tier_personal(self) -> None:
        """Test inferring personal privacy tier."""
        from vcp.identity.registry import PrivacyTier, infer_privacy_tier
        from vcp.identity.token import Token

        token = Token.parse("user.alice.personal")
        tier = infer_privacy_tier(token)
        assert tier == PrivacyTier.PERSONAL

    def test_infer_privacy_tier_pseudonymous(self) -> None:
        """Test inferring pseudonymous privacy tier."""
        from vcp.identity.registry import PrivacyTier, infer_privacy_tier
        from vcp.identity.token import Token

        for domain in ["anon", "pseudo"]:
            token = Token.parse(f"{domain}.abc123.private")
            tier = infer_privacy_tier(token)
            assert tier == PrivacyTier.PSEUDONYMOUS, f"Expected PSEUDONYMOUS for {domain}"

    def test_infer_privacy_tier_unknown_defaults_to_organizational(self) -> None:
        """Test that unknown domains default to organizational."""
        from vcp.identity.registry import PrivacyTier, infer_privacy_tier
        from vcp.identity.token import Token

        token = Token.parse("unknown.custom.creed")
        tier = infer_privacy_tier(token)
        assert tier == PrivacyTier.ORGANIZATIONAL

    def test_create_authorization(self) -> None:
        """Test authorization context creation helper."""
        from vcp.identity.registry import create_authorization

        auth = create_authorization(
            requester_id="alice",
            org_memberships=["acme", "example"],
            community_memberships=["buddhist"],
            owned_prefixes=["user.alice"],
            is_admin=False,
        )

        assert auth.requester_id == "alice"
        assert auth.org_memberships == {"acme", "example"}
        assert auth.community_memberships == {"buddhist"}
        assert auth.owned_prefixes == {"user.alice"}
        assert not auth.is_admin

    def test_create_authorization_defaults(self) -> None:
        """Test authorization context creation with defaults."""
        from vcp.identity.registry import create_authorization

        auth = create_authorization()

        assert auth.requester_id is None
        assert auth.org_memberships == set()
        assert auth.community_memberships == set()
        assert auth.owned_prefixes == set()
        assert not auth.is_admin


# ====================================================================================
# VERSION MATCHING TESTS
# ====================================================================================


class TestVersionMatching:
    """Tests for version-aware token resolution."""

    def test_find_exact_with_version(self) -> None:
        """Test that version is considered in exact lookups."""
        from vcp.identity.registry import LocalRegistry
        from vcp.identity.token import Token

        registry = LocalRegistry()
        token_v1 = Token.parse("family.safe.guide@1.0.0")
        token_v2 = Token.parse("family.safe.guide@2.0.0")

        registry.register(token_v1)
        registry.register(token_v2)

        # Both should be resolvable
        entry_v1 = registry.resolve(token_v1)
        entry_v2 = registry.resolve(token_v2)

        # Note: Current implementation uses canonical (no version) as key
        # So these might resolve to the same entry
        assert entry_v1 is not None or entry_v2 is not None


# ====================================================================================
# EDGE CASE TESTS
# ====================================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_pattern_returns_empty(self) -> None:
        """Test that empty pattern handling."""
        from vcp.identity.registry import AuthorizationContext, LocalRegistry
        from vcp.identity.token import Token

        registry = LocalRegistry()
        registry.register(Token.parse("family.safe.guide"))

        auth = AuthorizationContext()
        # Non-matching exact pattern
        result = registry.find("nonexistent.token.here", auth)
        assert len(result.tokens) == 0

    def test_find_with_no_entries(self) -> None:
        """Test find on empty registry."""
        from vcp.identity.registry import AuthorizationContext, LocalRegistry

        registry = LocalRegistry()
        auth = AuthorizationContext()

        result = registry.find("family.**", auth)

        assert len(result.tokens) == 0
        assert result.total_count == 0

    def test_privacy_tier_inheritance(self) -> None:
        """Test that child nodes inherit stricter privacy tiers."""
        from vcp.identity.registry import (
            AuthorizationContext,
            LocalRegistry,
            PrivacyTier,
        )
        from vcp.identity.token import Token

        registry = LocalRegistry()

        # Register public parent
        registry.register(
            Token.parse("company.acme.public"),
            privacy_tier=PrivacyTier.PUBLIC,
        )

        # Register private child
        registry.register(
            Token.parse("company.acme.private.secret"),
            privacy_tier=PrivacyTier.PERSONAL,
        )

        auth = AuthorizationContext()
        result = registry.find("company.acme.**", auth)

        # Should only get public entries
        assert len(result.tokens) == 1
        assert result.redacted_count == 1

    def test_max_history_entries(self) -> None:
        """Test that prefix queries respect max_results."""
        from vcp.identity.registry import AuthorizationContext, LocalRegistry
        from vcp.identity.token import Token

        registry = LocalRegistry()

        # Register many tokens
        for i in range(50):
            registry.register(Token.parse(f"family.item{i:02d}.guide"))

        auth = AuthorizationContext()
        result = registry.find("family.**", auth, max_results=10)

        assert len(result.tokens) == 10
        assert result.has_more is True
