"""Tests for VCP/I Namespace governance and validation."""

import pytest

from vcp.identity import NamespaceTier, Token, validate_namespace_access
from vcp.identity.namespace import (
    COMMUNITY_PREFIXES,
    CORE_DOMAINS,
    ORG_PREFIXES,
    PERSONAL_PREFIX,
    get_tier_config,
    infer_tier,
    is_core_domain,
    is_known_namespace,
)


class TestNamespaceTierInference:
    """Test automatic tier inference from tokens (VCP/I §4.2)."""

    def test_core_domain_family(self):
        """Core domains infer to CORE tier."""
        t = Token.parse("family.safe.guide")
        assert infer_tier(t) == NamespaceTier.CORE

    @pytest.mark.parametrize(
        "raw",
        [
            "family.safe.guide",
            "work.professional.assistant",
            "secure.privacy.guardian",
            "creative.artistic.muse",
            "reality.factual.anchor",
        ],
    )
    def test_all_core_prefixes(self, raw):
        assert infer_tier(Token.parse(raw)) == NamespaceTier.CORE

    @pytest.mark.parametrize(
        "raw",
        [
            "company.acme.legal.compliance",
            "school.mit.research",
            "ngo.redcross.humanitarian",
        ],
    )
    def test_organizational_prefixes(self, raw):
        """company, school and ngo infer to ORGANIZATIONAL."""
        assert infer_tier(Token.parse(raw)) == NamespaceTier.ORGANIZATIONAL

    @pytest.mark.parametrize(
        "raw",
        [
            "religion.buddhist.mindfulness",
            "culture.japanese.formal",
            "community.gaming.esports",
        ],
    )
    def test_community_prefixes(self, raw):
        """religion, culture and community infer to COMMUNITY."""
        assert infer_tier(Token.parse(raw)) == NamespaceTier.COMMUNITY

    def test_personal_user(self):
        """user prefix infers to PERSONAL."""
        t = Token.parse("user.john.creative.writer")
        assert infer_tier(t) == NamespaceTier.PERSONAL

    @pytest.mark.parametrize(
        "raw",
        [
            "health.privacy.hipaa",
            "education.k12.tutor",
            "finance.retail.advisor",
            "legal.contract.reviewer",
            "opensource.permissive.mit",
            "company-acme.legal.compliance",
            "user-john.creative.writer",
            "org.example.dept.team.policy",
        ],
    )
    def test_unknown_prefix_has_no_tier(self, raw):
        """Unknown prefixes are an invalid namespace (VCP/I §3.7.2, §4.2)."""
        with pytest.raises(ValueError, match="Unknown namespace prefix"):
            infer_tier(Token.parse(raw))


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
        t = Token.parse("company.acme.legal.compliance")
        assert validate_namespace_access(t, NamespaceTier.ORGANIZATIONAL) is True

    def test_personal_validates_for_personal(self):
        """Personal domain validates for PERSONAL tier."""
        t = Token.parse("user.john.creative.writer")
        assert validate_namespace_access(t, NamespaceTier.PERSONAL) is True

    @pytest.mark.parametrize("tier", list(NamespaceTier))
    def test_unknown_prefix_fails_closed_for_every_tier(self, tier):
        t = Token.parse("opensource.permissive.mit")
        assert validate_namespace_access(t, tier) is False


class TestCoreDomains:
    """Test namespace prefix definitions."""

    def test_all_core_domains_defined(self):
        """Core domains are exactly the five VCP/I §4.2.1 prefixes."""
        assert CORE_DOMAINS == {"family", "work", "secure", "creative", "reality"}

    def test_other_tier_prefixes(self):
        assert ORG_PREFIXES == {"company", "school", "ngo"}
        assert COMMUNITY_PREFIXES == {"religion", "culture", "community"}
        assert PERSONAL_PREFIX == "user"

    def test_is_known_namespace(self):
        assert is_known_namespace("family") is True
        assert is_known_namespace("user") is True
        assert is_known_namespace("health") is False

    def test_is_core_domain_true(self):
        """is_core_domain returns True for core domains."""
        assert is_core_domain("family") is True
        assert is_core_domain("reality") is True

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
