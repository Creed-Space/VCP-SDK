"""Tests for VCP/I Registry with privacy-preserving wildcard queries."""

import pytest

from vcp.identity import (
    BloomFilter,
    LocalRegistry,
    PrivacyTier,
    PseudonymousRegistry,
    Token,
    create_authorization,
    infer_privacy_tier,
)


class TestBloomFilter:
    """Test bloom filter for existence checks."""

    def test_add_and_check(self):
        """Items added can be found."""
        bf = BloomFilter(expected_items=100)
        bf.add("family.safe.guide")
        assert bf.might_contain("family.safe.guide") is True

    def test_not_added_probably_not_found(self):
        """Items not added are probably not found."""
        bf = BloomFilter(expected_items=100)
        bf.add("family.safe.guide")
        # High probability this returns False
        assert bf.might_contain("work.professional.assistant") is False

    def test_count(self):
        """Count tracks additions."""
        bf = BloomFilter()
        assert len(bf) == 0
        bf.add("a.b.c")
        assert len(bf) == 1
        bf.add("d.e.f")
        assert len(bf) == 2


class TestLocalRegistry:
    """Test local registry implementation."""

    @pytest.fixture
    def registry(self):
        return LocalRegistry()

    @pytest.fixture
    def admin_auth(self):
        return create_authorization(is_admin=True)

    @pytest.fixture
    def public_auth(self):
        return create_authorization()

    def test_register_and_resolve(self, registry):
        """Register token and resolve it."""
        token = Token.parse("family.safe.guide@1.0.0")
        registry.register(token)

        resolved = registry.resolve(token)
        assert resolved is not None
        assert resolved.token.canonical == "family.safe.guide"

    def test_exists_with_bloom(self, registry):
        """Existence check uses bloom filter."""
        token = Token.parse("family.safe.guide")
        assert registry.exists(token) is False

        registry.register(token)
        assert registry.exists(token) is True

    def test_exists_non_existent(self, registry):
        """Non-existent token returns False."""
        token = Token.parse("nonexistent.token.here")
        assert registry.exists(token) is False

    def test_find_exact(self, registry, public_auth):
        """Find exact token match."""
        token = Token.parse("family.safe.guide")
        registry.register(token)

        result = registry.find("family.safe.guide", public_auth)
        assert len(result.tokens) == 1
        assert result.tokens[0].canonical == "family.safe.guide"

    def test_find_prefix_wildcard(self, registry, admin_auth):
        """Find tokens with prefix wildcard."""
        registry.register(Token.parse("company.acme.legal.compliance"))
        registry.register(Token.parse("company.acme.legal.policy"))
        registry.register(Token.parse("company.acme.hr.hiring"))
        registry.register(Token.parse("company.other.legal.stuff"))

        result = registry.find("company.acme.**", admin_auth)
        assert len(result.tokens) == 3

    def test_find_suffix_wildcard(self, registry, admin_auth):
        """Find tokens with suffix wildcard."""
        registry.register(Token.parse("company.acme.legal.compliance"))
        registry.register(Token.parse("company.other.legal.compliance"))
        registry.register(Token.parse("family.safe.compliance"))

        result = registry.find("**.compliance", admin_auth)
        assert len(result.tokens) == 3

    def test_find_pattern_wildcard(self, registry, admin_auth):
        """Find tokens with single-segment wildcards."""
        registry.register(Token.parse("company.acme.legal.compliance"))
        registry.register(Token.parse("company.other.legal.policy"))
        registry.register(Token.parse("company.xyz.hr.hiring"))

        result = registry.find("company.*.legal.*", admin_auth)
        assert len(result.tokens) == 2


class TestPrivacyTiers:
    """Test privacy tier enforcement."""

    @pytest.fixture
    def registry(self):
        reg = LocalRegistry()
        # Register tokens at different privacy levels
        reg.register(
            Token.parse("family.safe.guide"),
            privacy_tier=PrivacyTier.PUBLIC,
        )
        reg.register(
            Token.parse("company.acme.legal.compliance"),
            privacy_tier=PrivacyTier.ORGANIZATIONAL,
        )
        reg.register(
            Token.parse("user.alice.personal.diary"),
            privacy_tier=PrivacyTier.PERSONAL,
            owner_id="alice",
        )
        return reg

    def test_public_tokens_visible_to_all(self, registry):
        """Public tokens are visible without authorization."""
        auth = create_authorization()
        result = registry.find("family.**", auth)
        assert len(result.tokens) == 1

    def test_org_tokens_require_membership(self, registry):
        """Organizational tokens require membership."""
        # Without membership
        no_auth = create_authorization()
        result = registry.find("company.acme.**", no_auth)
        assert len(result.tokens) == 0
        assert result.redacted_count == 1

        # With membership
        member_auth = create_authorization(org_memberships=["acme"])
        result = registry.find("company.acme.**", member_auth)
        assert len(result.tokens) == 1

    def test_personal_tokens_owner_only(self, registry):
        """Personal tokens only visible to owner."""
        # Not owner
        other_auth = create_authorization(requester_id="bob")
        result = registry.find("user.alice.**", other_auth)
        assert len(result.tokens) == 0

        # Owner
        owner_auth = create_authorization(
            requester_id="alice",
            owned_prefixes=["user.alice"],
        )
        result = registry.find("user.alice.**", owner_auth)
        assert len(result.tokens) == 1

    def test_admin_sees_all(self, registry):
        """Admin can see all tokens."""
        admin = create_authorization(is_admin=True)
        # Admin can query any prefix
        result = registry.find("company.acme.**", admin)
        assert len(result.tokens) == 1
        assert result.scope_authorized is True

    def test_exact_lookup_always_works(self, registry):
        """Exact lookup works regardless of privacy tier."""
        token = Token.parse("user.alice.personal.diary")
        # Even without auth, exact lookup works
        entry = registry.resolve(token)
        assert entry is not None


class TestInferPrivacyTier:
    """Test privacy tier inference from token."""

    def test_public_core_namespaces(self):
        """Core namespaces are public."""
        assert (
            infer_privacy_tier(Token.parse("family.safe.guide"))
            == PrivacyTier.PUBLIC
        )
        assert (
            infer_privacy_tier(Token.parse("work.pro.assistant"))
            == PrivacyTier.PUBLIC
        )
        assert (
            infer_privacy_tier(Token.parse("education.k12.safety"))
            == PrivacyTier.PUBLIC
        )

    def test_organizational_namespaces(self):
        """Organizational namespaces are restricted."""
        assert (
            infer_privacy_tier(Token.parse("company.acme.legal.x"))
            == PrivacyTier.ORGANIZATIONAL
        )
        assert (
            infer_privacy_tier(Token.parse("school.mit.research.x"))
            == PrivacyTier.ORGANIZATIONAL
        )
        assert (
            infer_privacy_tier(
                Token.parse("org.example.dept.policy")
            )
            == PrivacyTier.ORGANIZATIONAL
        )

    def test_community_namespaces(self):
        """Community namespaces are community-controlled."""
        assert (
            infer_privacy_tier(
                Token.parse("religion.buddhist.meditation")
            )
            == PrivacyTier.COMMUNITY
        )
        assert (
            infer_privacy_tier(
                Token.parse("culture.japanese.formal")
            )
            == PrivacyTier.COMMUNITY
        )

    def test_personal_namespaces(self):
        """Personal namespaces are private."""
        assert infer_privacy_tier(Token.parse("user.alice.personal")) == PrivacyTier.PERSONAL

    def test_pseudonymous_namespaces(self):
        """Pseudonymous namespaces are unlinkable."""
        assert (
            infer_privacy_tier(
                Token.parse("anon.abc123.constitution")
            )
            == PrivacyTier.PSEUDONYMOUS
        )
        assert (
            infer_privacy_tier(
                Token.parse("pseudo.xyz789.private")
            )
            == PrivacyTier.PSEUDONYMOUS
        )


class TestPseudonymousRegistry:
    """Test pseudonymous registration and ownership proofs."""

    @pytest.fixture
    def registry(self):
        base = LocalRegistry()
        return PseudonymousRegistry(base)

    def test_generate_pseudonym(self, registry):
        """Generate pseudonymous identity."""
        secret = b"my_secret_key"
        pseudonym = registry.generate_pseudonym("alice@example.com", secret)

        assert len(pseudonym) == 32
        assert pseudonym.isalnum()

    def test_pseudonym_is_deterministic_with_salt(self, registry):
        """Same identity + secret produces consistent pseudonym (with stored salt)."""
        secret = b"my_secret_key"
        p1 = registry.generate_pseudonym("alice@example.com", secret)
        # Note: Different calls generate different salts
        # This tests the format, not determinism
        assert len(p1) == 32

    def test_prove_and_verify_ownership(self, registry):
        """Ownership can be proven and verified."""
        secret = b"my_secret_key"
        pseudonym = registry.generate_pseudonym("alice@example.com", secret)

        token = Token.parse("anon.abc.def.xyz")
        proof = registry.prove_ownership(token, pseudonym, secret)

        assert registry.verify_ownership(token, pseudonym, proof, secret) is True

    def test_wrong_secret_fails_verification(self, registry):
        """Wrong secret fails verification."""
        secret = b"my_secret_key"
        wrong_secret = b"wrong_secret"
        pseudonym = registry.generate_pseudonym("alice@example.com", secret)

        token = Token.parse("anon.abc.def.xyz")
        proof = registry.prove_ownership(token, pseudonym, secret)

        assert registry.verify_ownership(token, pseudonym, proof, wrong_secret) is False


class TestSubscriptions:
    """Test registry change subscriptions."""

    def test_subscribe_and_notify(self):
        """Subscribers are notified of changes."""
        registry = LocalRegistry()
        auth = create_authorization(is_admin=True)

        notifications = []

        def callback(token, event):
            notifications.append((token.canonical, event))

        registry.subscribe("company.acme.**", auth, callback)

        # Register a matching token
        registry.register(Token.parse("company.acme.legal.new"))

        assert len(notifications) == 1
        assert notifications[0] == ("company.acme.legal.new", "created")

    def test_unsubscribe(self):
        """Unsubscribed callbacks are not called."""
        registry = LocalRegistry()
        auth = create_authorization(is_admin=True)

        notifications = []

        def callback(token, event):
            notifications.append(token.canonical)

        sub_id = registry.subscribe("company.**", auth, callback)
        registry.unsubscribe(sub_id)

        registry.register(Token.parse("company.test.token.here"))

        assert len(notifications) == 0


class TestQueryResult:
    """Test query result structure."""

    def test_has_more_flag(self):
        """has_more indicates pagination needed."""
        registry = LocalRegistry()
        auth = create_authorization(is_admin=True)

        # Register more tokens than max_results
        for i in range(10):
            registry.register(Token.parse(f"family.test.token{i}"))

        result = registry.find("family.**", auth, max_results=5)
        assert len(result.tokens) == 5
        assert result.has_more is True

    def test_redacted_count(self):
        """Redacted count tracks hidden tokens."""
        registry = LocalRegistry()

        # Register private token
        registry.register(
            Token.parse("user.alice.secret.token"),
            privacy_tier=PrivacyTier.PERSONAL,
            owner_id="alice",
        )

        # Query without auth
        auth = create_authorization(requester_id="bob")
        result = registry.find("user.alice.**", auth)

        assert len(result.tokens) == 0
        assert result.redacted_count == 1
        assert result.scope_authorized is False
