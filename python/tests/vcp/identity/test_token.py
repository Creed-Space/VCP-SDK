"""Tests for VCP/I Token parsing and validation."""

import pytest

from vcp.identity import Token


class TestTokenParsing:
    """Test token parsing from strings."""

    def test_simple_token(self):
        """Parse basic domain.approach.role token."""
        t = Token.parse("family.safe.guide")
        assert t.domain == "family"
        assert t.approach == "safe"
        assert t.role == "guide"
        assert t.version is None
        assert t.namespace is None

    def test_versioned_token(self):
        """Parse token with version."""
        t = Token.parse("family.safe.guide@1.2.0")
        assert t.version == "1.2.0"
        assert t.canonical == "family.safe.guide"
        assert t.full == "family.safe.guide@1.2.0"

    def test_namespaced_token(self):
        """Parse token with namespace."""
        t = Token.parse("company.acme.legal:SEC")
        assert t.namespace == "SEC"
        assert t.canonical == "company.acme.legal"
        assert t.full == "company.acme.legal:SEC"

    def test_full_token(self):
        """Parse token with both version and namespace."""
        t = Token.parse("family.safe.guide@1.2.0:ELEM")
        assert t.domain == "family"
        assert t.approach == "safe"
        assert t.role == "guide"
        assert t.version == "1.2.0"
        assert t.namespace == "ELEM"
        assert t.full == "family.safe.guide@1.2.0:ELEM"

    def test_hyphenated_segments(self):
        """Parse token with hyphenated segments."""
        t = Token.parse("work-life.balanced-approach.team-lead")
        assert t.domain == "work-life"
        assert t.approach == "balanced-approach"
        assert t.role == "team-lead"


class TestTokenValidation:
    """Test token validation rules."""

    def test_empty_token_raises(self):
        """Empty string should raise ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            Token.parse("")

    def test_invalid_format_raises(self):
        """Invalid format should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid VCP/I token"):
            Token.parse("invalid")

    def test_missing_segments_raises(self):
        """Missing segments should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid VCP/I token"):
            Token.parse("family.safe")  # Missing role

    def test_too_long_raises(self):
        """Token exceeding max length should raise."""
        # 256+ chars, but valid format (many segments)
        long_token = ".".join(["seg"] * 100)  # Way over max length
        with pytest.raises(ValueError, match="(exceeds max length|Invalid VCP/I token)"):
            Token.parse(long_token)

    def test_segment_too_long_raises(self):
        """Segment exceeding max length should raise."""
        long_segment = "a" * 40
        with pytest.raises(ValueError, match="Segment.*exceeds max length"):
            Token.parse(f"{long_segment}.safe.guide")

    def test_invalid_version_format(self):
        """Invalid version format should fail parsing."""
        with pytest.raises(ValueError, match="Invalid VCP/I token"):
            Token.parse("family.safe.guide@1.2")  # Missing patch

    def test_invalid_namespace_format(self):
        """Invalid namespace format should fail parsing."""
        with pytest.raises(ValueError, match="Invalid VCP/I token"):
            Token.parse("family.safe.guide:lowercase")  # Lowercase

    def test_uppercase_domain_fails(self):
        """Uppercase in domain should fail."""
        with pytest.raises(ValueError, match="Invalid VCP/I token"):
            Token.parse("Family.safe.guide")


class TestTokenImmutability:
    """Test that tokens are immutable."""

    def test_frozen_dataclass(self):
        """Token attributes cannot be modified."""
        t = Token.parse("family.safe.guide")
        with pytest.raises(AttributeError):
            t.domain = "other"  # type: ignore

    def test_with_version_returns_new(self):
        """with_version returns a new token."""
        t1 = Token.parse("family.safe.guide")
        t2 = t1.with_version("2.0.0")
        assert t1.version is None
        assert t2.version == "2.0.0"
        assert t1 is not t2

    def test_with_namespace_returns_new(self):
        """with_namespace returns a new token."""
        t1 = Token.parse("family.safe.guide")
        t2 = t1.with_namespace("ELEM")
        assert t1.namespace is None
        assert t2.namespace == "ELEM"
        assert t1 is not t2


class TestTokenMethods:
    """Test token utility methods."""

    def test_canonical_strips_version_namespace(self):
        """canonical property strips version and namespace."""
        t = Token.parse("family.safe.guide@1.2.0:ELEM")
        assert t.canonical == "family.safe.guide"

    def test_to_uri_default_registry(self):
        """to_uri uses default registry."""
        t = Token.parse("family.safe.guide@1.2.0")
        assert t.to_uri() == "creed://creed.space/family.safe.guide@1.2.0"

    def test_to_uri_custom_registry(self):
        """to_uri accepts custom registry."""
        t = Token.parse("family.safe.guide")
        assert t.to_uri("custom.registry") == "creed://custom.registry/family.safe.guide"

    def test_str_returns_full(self):
        """str() returns full token."""
        t = Token.parse("family.safe.guide@1.2.0:ELEM")
        assert str(t) == "family.safe.guide@1.2.0:ELEM"

    def test_repr_includes_type(self):
        """repr() includes type name."""
        t = Token.parse("family.safe.guide")
        assert repr(t) == "Token('family.safe.guide')"


class TestTokenPatternMatching:
    """Test glob-like pattern matching."""

    def test_exact_match(self):
        """Exact pattern matches."""
        t = Token.parse("family.safe.guide")
        assert t.matches_pattern("family.safe.guide") is True

    def test_wildcard_domain(self):
        """Wildcard in domain position."""
        t = Token.parse("family.safe.guide")
        assert t.matches_pattern("*.safe.guide") is True

    def test_wildcard_approach(self):
        """Wildcard in approach position."""
        t = Token.parse("family.safe.guide")
        assert t.matches_pattern("family.*.guide") is True

    def test_wildcard_role(self):
        """Wildcard in role position."""
        t = Token.parse("family.safe.guide")
        assert t.matches_pattern("family.safe.*") is True

    def test_all_wildcards(self):
        """All wildcards match any token."""
        t = Token.parse("work.strict.admin")
        assert t.matches_pattern("*.*.*") is True

    def test_no_match(self):
        """Non-matching pattern returns False."""
        t = Token.parse("family.safe.guide")
        assert t.matches_pattern("work.safe.guide") is False

    def test_invalid_pattern_segments(self):
        """Pattern with wrong number of segments fails."""
        t = Token.parse("family.safe.guide")
        assert t.matches_pattern("family.safe") is False
        assert t.matches_pattern("family.safe.guide.extra") is False

    def test_double_star_wildcard(self):
        """Double-star matches any number of segments."""
        t = Token.parse("company.acme.legal.compliance")
        assert t.matches_pattern("company.**") is True
        assert t.matches_pattern("**.compliance") is True
        assert t.matches_pattern("company.**.compliance") is True

    def test_four_segment_exact(self):
        """Four segment tokens match four segment patterns."""
        t = Token.parse("company.acme.legal.compliance")
        assert t.matches_pattern("company.acme.legal.compliance") is True
        assert t.matches_pattern("*.acme.legal.*") is True


class TestMultiSegmentTokens:
    """Test variable-depth token support."""

    def test_four_segment_token(self):
        """Parse 4-segment token."""
        t = Token.parse("company.acme.legal.compliance")
        assert t.domain == "company"
        assert t.approach == "legal"
        assert t.role == "compliance"
        assert t.depth == 4
        assert t.path == ("acme",)
        assert t.canonical == "company.acme.legal.compliance"

    def test_five_segment_token(self):
        """Parse 5-segment token."""
        t = Token.parse("org.example.dept.team.policy@1.0.0")
        assert t.domain == "org"
        assert t.approach == "team"
        assert t.role == "policy"
        assert t.depth == 5
        assert t.path == ("example", "dept")
        assert t.version == "1.0.0"

    def test_parent_returns_shorter(self):
        """Parent method returns token with one less segment."""
        t = Token.parse("company.acme.legal.compliance")
        parent = t.parent()
        assert parent is not None
        assert parent.canonical == "company.acme.legal"
        assert parent.depth == 3

    def test_parent_at_min_depth_returns_none(self):
        """Parent at minimum depth returns None."""
        t = Token.parse("family.safe.guide")
        assert t.parent() is None

    def test_child_adds_segment(self):
        """Child method adds a segment."""
        t = Token.parse("family.safe.guide")
        child = t.child("extra")
        assert child.canonical == "family.safe.guide.extra"
        assert child.depth == 4

    def test_is_ancestor_of(self):
        """Check ancestor relationship."""
        ancestor = Token.parse("company.acme.legal")
        descendant = Token.parse("company.acme.legal.compliance")
        assert ancestor.is_ancestor_of(descendant) is True
        assert descendant.is_ancestor_of(ancestor) is False

    def test_is_descendant_of(self):
        """Check descendant relationship."""
        ancestor = Token.parse("company.acme.legal")
        descendant = Token.parse("company.acme.legal.compliance")
        assert descendant.is_descendant_of(ancestor) is True
        assert ancestor.is_descendant_of(descendant) is False

    def test_segments_property(self):
        """Segments property returns all segments."""
        t = Token.parse("a.b.c.d.e")
        assert t.segments == ("a", "b", "c", "d", "e")


class TestWithVersionValidation:
    """Test version validation in with_version."""

    def test_valid_version(self):
        """Valid semver format succeeds."""
        t = Token.parse("family.safe.guide")
        t2 = t.with_version("1.0.0")
        assert t2.version == "1.0.0"

    def test_invalid_version_raises(self):
        """Invalid version format raises."""
        t = Token.parse("family.safe.guide")
        with pytest.raises(ValueError, match="Invalid version format"):
            t.with_version("1.0")


class TestWithNamespaceValidation:
    """Test namespace validation in with_namespace."""

    def test_valid_namespace(self):
        """Valid namespace format succeeds."""
        t = Token.parse("family.safe.guide")
        t2 = t.with_namespace("ELEM")
        assert t2.namespace == "ELEM"

    def test_invalid_namespace_raises(self):
        """Invalid namespace format raises."""
        t = Token.parse("family.safe.guide")
        with pytest.raises(ValueError, match="Invalid namespace format"):
            t.with_namespace("lowercase")
