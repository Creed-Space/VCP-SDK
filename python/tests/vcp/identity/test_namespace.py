"""Tests for VCP/I Namespace governance and validation."""

from vcp.identity import NamespaceTier, Token, validate_namespace_access
from vcp.identity.namespace import (
    CORE_DOMAINS,
    get_tier_config,
    infer_tier,
    is_core_domain,
)


class TestNamespaceTierInference:
    """Test automatic tier inference from tokens."""

    def test_core_domain_family(self):
        """Core domains infer to CORE tier."""
        t = Token.parse("family.safe.guide")
        assert infer_tier(t) == NamespaceTier.CORE

    def test_core_domain_health(self):
        """Health is a core domain."""
        t = Token.parse("health.privacy.hipaa")
        assert infer_tier(t) == NamespaceTier.CORE

    def test_organizational_company(self):
        """company prefix infers to ORGANIZATIONAL."""
        t = Token.parse("company-acme.legal.compliance")
        assert infer_tier(t) == NamespaceTier.ORGANIZATIONAL

    def test_personal_user(self):
        """user prefix infers to PERSONAL."""
        t = Token.parse("user-john.creative.writer")
        assert infer_tier(t) == NamespaceTier.PERSONAL

    def test_community_default(self):
        """Non-matching domains infer to COMMUNITY."""
        t = Token.parse("opensource.permissive.mit")
        assert infer_tier(t) == NamespaceTier.COMMUNITY


class TestNamespaceValidation:
    """Test namespace access validation."""

    def test_core_validates_for_core(self):
        """Core domain validates for CORE tier."""
        t = Token.parse("family.safe.guide")
        assert validate_namespace_access(t, NamespaceTier.CORE) is True

    def test_core_fails_for_org(self):
        """Core domain fails for ORGANIZATIONAL tier."""
        t = Token.parse("family.safe.guide")
        assert validate_namespace_access(t, NamespaceTier.ORGANIZATIONAL) is False

    def test_org_validates_for_org(self):
        """Organizational domain validates for ORGANIZATIONAL tier."""
        t = Token.parse("company-acme.legal.compliance")
        assert validate_namespace_access(t, NamespaceTier.ORGANIZATIONAL) is True

    def test_personal_validates_for_personal(self):
        """Personal domain validates for PERSONAL tier."""
        t = Token.parse("user-john.creative.writer")
        assert validate_namespace_access(t, NamespaceTier.PERSONAL) is True


class TestCoreDomains:
    """Test core domain definitions."""

    def test_all_core_domains_defined(self):
        """All expected core domains are defined."""
        expected = {
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
        assert CORE_DOMAINS == expected

    def test_is_core_domain_true(self):
        """is_core_domain returns True for core domains."""
        assert is_core_domain("family") is True
        assert is_core_domain("health") is True

    def test_is_core_domain_false(self):
        """is_core_domain returns False for non-core domains."""
        assert is_core_domain("custom") is False
        assert is_core_domain("company") is False


class TestTierConfig:
    """Test tier configuration retrieval."""

    def test_core_config(self):
        """CORE tier config is correct."""
        config = get_tier_config(NamespaceTier.CORE)
        assert config.tier == NamespaceTier.CORE
        assert config.registration_required is False
        assert config.delegation_allowed is False
        assert config.proof_type is None

    def test_organizational_config(self):
        """ORGANIZATIONAL tier requires DNS proof."""
        config = get_tier_config(NamespaceTier.ORGANIZATIONAL)
        assert config.tier == NamespaceTier.ORGANIZATIONAL
        assert config.registration_required is True
        assert config.delegation_allowed is True
        assert config.proof_type == "dns"

    def test_personal_config(self):
        """PERSONAL tier requires email proof."""
        config = get_tier_config(NamespaceTier.PERSONAL)
        assert config.tier == NamespaceTier.PERSONAL
        assert config.registration_required is True
        assert config.delegation_allowed is False
        assert config.proof_type == "email"

    def test_community_config(self):
        """COMMUNITY tier requires consensus."""
        config = get_tier_config(NamespaceTier.COMMUNITY)
        assert config.tier == NamespaceTier.COMMUNITY
        assert config.registration_required is True
        assert config.delegation_allowed is True
        assert config.proof_type == "consensus"
