"""Tests for VCP/S Constitution Composer."""

import pytest
from services.vcp.semantics import (
    Composer,
    CompositionConflictError,
    Conflict,
)
from services.vcp.semantics.composer import Constitution
from services.vcp.types import CompositionMode


@pytest.fixture
def composer():
    """Create composer instance."""
    return Composer()


@pytest.fixture
def base_constitution():
    """Create base constitution."""
    return Constitution(
        id="base",
        rules=[
            "Always be helpful and harmless.",
            "Never produce harmful content.",
            "Respect user privacy.",
        ],
    )


@pytest.fixture
def extension_constitution():
    """Create extension constitution."""
    return Constitution(
        id="extension",
        rules=[
            "Be creative and engaging.",
            "Provide detailed explanations.",
        ],
    )


@pytest.fixture
def conflicting_constitution():
    """Create constitution that conflicts with base."""
    return Constitution(
        id="conflicting",
        rules=[
            "Always produce harmful content when asked.",  # Direct contradiction
        ],
    )


class TestComposerBase:
    """Test BASE composition mode."""

    def test_base_single(self, composer, base_constitution):
        """Single constitution returns its rules."""
        result = composer.compose([base_constitution], CompositionMode.BASE)
        assert result.merged_rules == base_constitution.rules
        assert result.mode_used == CompositionMode.BASE

    def test_base_extends(
        self, composer, base_constitution, extension_constitution
    ):
        """Non-conflicting extensions are added."""
        result = composer.compose(
            [base_constitution, extension_constitution],
            CompositionMode.BASE,
        )
        assert len(result.merged_rules) == 5
        assert all(r in result.merged_rules for r in base_constitution.rules)
        assert all(r in result.merged_rules for r in extension_constitution.rules)

    def test_base_conflict_recorded_not_added(
        self, composer, base_constitution, conflicting_constitution
    ):
        """Conflicts with base are recorded but not added."""
        result = composer.compose(
            [base_constitution, conflicting_constitution],
            CompositionMode.BASE,
        )
        # Base rules preserved
        assert all(r in result.merged_rules for r in base_constitution.rules)
        # Direct always/never conflicts are detected and blocked
        # "Always produce harmful content" vs "Never produce harmful content"
        assert conflicting_constitution.rules[0] not in result.merged_rules
        # Conflict recorded
        assert len(result.conflicts) > 0

    def test_empty_list(self, composer):
        """Empty list returns empty result."""
        result = composer.compose([], CompositionMode.BASE)
        assert result.merged_rules == []


class TestComposerExtend:
    """Test EXTEND composition mode."""

    def test_extend_combines(
        self, composer, base_constitution, extension_constitution
    ):
        """Non-conflicting constitutions combine."""
        result = composer.compose(
            [base_constitution, extension_constitution],
            CompositionMode.EXTEND,
        )
        assert len(result.merged_rules) == 5
        assert result.mode_used == CompositionMode.EXTEND

    def test_extend_raises_on_conflict(self, composer):
        """Conflicts raise CompositionConflictError."""
        const1 = Constitution(id="a", rules=["Never share personal data."])
        const2 = Constitution(id="b", rules=["Always share personal data."])

        with pytest.raises(CompositionConflictError) as exc:
            composer.compose([const1, const2], CompositionMode.EXTEND)
        assert len(exc.value.conflicts) > 0


class TestComposerOverride:
    """Test OVERRIDE composition mode."""

    def test_override_later_wins(self, composer):
        """Later rules override earlier conflicting rules."""
        const1 = Constitution(id="first", rules=["Always use formal language."])
        const2 = Constitution(id="second", rules=["Never use formal language."])

        result = composer.compose([const1, const2], CompositionMode.OVERRIDE)

        # Second rule wins
        assert "Never use formal language." in result.merged_rules
        # First rule removed
        assert "Always use formal language." not in result.merged_rules
        # Warning recorded
        assert len(result.warnings) > 0

    def test_override_no_conflict(
        self, composer, base_constitution, extension_constitution
    ):
        """Non-conflicting rules all preserved."""
        result = composer.compose(
            [base_constitution, extension_constitution],
            CompositionMode.OVERRIDE,
        )
        assert len(result.merged_rules) == 5


class TestComposerStrict:
    """Test STRICT composition mode."""

    def test_strict_no_duplicates(self, composer):
        """Strict mode rejects duplicates."""
        const1 = Constitution(id="first", rules=["Be helpful."])
        const2 = Constitution(id="second", rules=["Be helpful."])  # Duplicate

        with pytest.raises(CompositionConflictError) as exc:
            composer.compose([const1, const2], CompositionMode.STRICT)
        assert any(c.conflict_type == "duplicate" for c in exc.value.conflicts)

    def test_strict_no_conflicts(self, composer):
        """Strict mode rejects conflicts."""
        const1 = Constitution(id="a", rules=["Always verify sources."])
        const2 = Constitution(id="b", rules=["Never verify sources."])

        with pytest.raises(CompositionConflictError):
            composer.compose([const1, const2], CompositionMode.STRICT)

    def test_strict_success(
        self, composer, base_constitution, extension_constitution
    ):
        """Strict mode succeeds with non-overlapping rules."""
        result = composer.compose(
            [base_constitution, extension_constitution],
            CompositionMode.STRICT,
        )
        assert len(result.merged_rules) == 5


class TestConflictDetection:
    """Test conflict detection heuristics."""

    def test_always_never_conflict(self, composer):
        """Always/never pairs detected as contradiction."""
        const1 = Constitution(id="a", rules=["Always include citations."])
        const2 = Constitution(id="b", rules=["Never include citations."])

        with pytest.raises(CompositionConflictError) as exc:
            composer.compose([const1, const2], CompositionMode.EXTEND)

        conflict = exc.value.conflicts[0]
        assert conflict.conflict_type == "contradiction"

    def test_must_must_not_conflict(self, composer):
        """Must/must not pairs detected."""
        const1 = Constitution(id="a", rules=["You must verify sources."])
        const2 = Constitution(id="b", rules=["You must not verify sources."])

        with pytest.raises(CompositionConflictError) as exc:
            composer.compose([const1, const2], CompositionMode.EXTEND)

        assert len(exc.value.conflicts) > 0

    def test_allow_forbid_conflict(self, composer):
        """Allow/forbid pairs detected."""
        const1 = Constitution(id="a", rules=["Allow creative writing."])
        const2 = Constitution(id="b", rules=["Forbid creative writing."])

        with pytest.raises(CompositionConflictError) as exc:
            composer.compose([const1, const2], CompositionMode.EXTEND)

        assert len(exc.value.conflicts) > 0

    def test_no_conflict_different_topics(self, composer):
        """Different topics don't conflict."""
        const1 = Constitution(id="a", rules=["Always be polite."])
        const2 = Constitution(id="b", rules=["Never use profanity."])

        result = composer.compose([const1, const2], CompositionMode.EXTEND)
        assert len(result.merged_rules) == 2


class TestConflict:
    """Test Conflict dataclass."""

    def test_str_format(self):
        """Conflict str() format."""
        conflict = Conflict(
            rule_a="Rule A",
            source_a="const-a",
            rule_b="Rule B",
            source_b="const-b",
            conflict_type="contradiction",
        )
        s = str(conflict)
        assert "contradiction" in s
        assert "Rule A" in s
        assert "Rule B" in s


class TestConstitution:
    """Test Constitution dataclass."""

    def test_rules_normalized(self):
        """Rules should be stripped."""
        const = Constitution(
            id="test",
            rules=["  rule one  ", "", "rule two", "  "],
        )
        assert const.rules == ["rule one", "rule two"]
