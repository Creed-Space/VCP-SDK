"""Tests for VCP/A State Tracker."""

import pytest
from services.vcp.adaptation import (
    ContextEncoder,
    Dimension,
    StateTracker,
    Transition,
    TransitionSeverity,
    VCPContext,
)


@pytest.fixture
def tracker():
    """Create state tracker."""
    return StateTracker()


@pytest.fixture
def encoder():
    """Create context encoder."""
    return ContextEncoder()


class TestTransitionSeverity:
    """Test TransitionSeverity enum."""

    def test_all_severities(self):
        """All severities should be defined."""
        assert TransitionSeverity.NONE
        assert TransitionSeverity.MINOR
        assert TransitionSeverity.MAJOR
        assert TransitionSeverity.EMERGENCY


class TestTransition:
    """Test Transition class."""

    def test_is_significant(self):
        """is_significant should check MAJOR or EMERGENCY."""
        ctx = VCPContext()
        minor = Transition(
            severity=TransitionSeverity.MINOR,
            changed_dimensions=[],
            previous=ctx,
            current=ctx,
            timestamp=None,
        )
        major = Transition(
            severity=TransitionSeverity.MAJOR,
            changed_dimensions=[],
            previous=ctx,
            current=ctx,
            timestamp=None,
        )
        emergency = Transition(
            severity=TransitionSeverity.EMERGENCY,
            changed_dimensions=[],
            previous=ctx,
            current=ctx,
            timestamp=None,
        )

        assert not minor.is_significant
        assert major.is_significant
        assert emergency.is_significant

    def test_is_emergency(self):
        """is_emergency should check EMERGENCY only."""
        ctx = VCPContext()
        major = Transition(
            severity=TransitionSeverity.MAJOR,
            changed_dimensions=[],
            previous=ctx,
            current=ctx,
            timestamp=None,
        )
        emergency = Transition(
            severity=TransitionSeverity.EMERGENCY,
            changed_dimensions=[],
            previous=ctx,
            current=ctx,
            timestamp=None,
        )

        assert not major.is_emergency
        assert emergency.is_emergency

    def test_str_format(self):
        """Transition string representation."""
        ctx = VCPContext()
        t = Transition(
            severity=TransitionSeverity.MINOR,
            changed_dimensions=[Dimension.TIME],
            previous=ctx,
            current=ctx,
            timestamp=None,
        )
        s = str(t)
        assert "minor" in s
        assert "time" in s


class TestStateTracker:
    """Test StateTracker class."""

    def test_first_record_returns_none(self, tracker, encoder):
        """First record should return None (no transition)."""
        ctx = encoder.encode(time="morning")
        result = tracker.record(ctx)
        assert result is None

    def test_no_change_returns_none_severity(self, tracker, encoder):
        """Recording same context should return NONE severity."""
        ctx = encoder.encode(time="morning")
        tracker.record(ctx)
        transition = tracker.record(ctx)
        assert transition.severity == TransitionSeverity.NONE

    def test_single_change_is_minor(self, tracker, encoder):
        """Single dimension change should be MINOR."""
        ctx1 = encoder.encode(time="morning")
        ctx2 = encoder.encode(time="evening")
        tracker.record(ctx1)
        transition = tracker.record(ctx2)
        assert transition.severity == TransitionSeverity.MINOR
        assert Dimension.TIME in transition.changed_dimensions

    def test_multiple_changes_is_major(self, tracker, encoder):
        """Three or more dimension changes should be MAJOR."""
        ctx1 = encoder.encode(time="morning", space="home", state="happy")
        ctx2 = encoder.encode(time="evening", space="office", state="anxious")
        tracker.record(ctx1)
        transition = tracker.record(ctx2)
        assert transition.severity == TransitionSeverity.MAJOR

    def test_major_dimension_change_is_major(self, tracker, encoder):
        """AGENCY change should be MAJOR."""
        ctx1 = encoder.encode(agency="peer")
        ctx2 = encoder.encode(agency="leader")
        tracker.record(ctx1)
        transition = tracker.record(ctx2)
        assert transition.severity == TransitionSeverity.MAJOR

    def test_emergency_value_is_emergency(self, tracker):
        """Emergency emoji should trigger EMERGENCY."""
        ctx1 = VCPContext(dimensions={Dimension.OCCASION: ["➖"]})
        ctx2 = VCPContext(dimensions={Dimension.OCCASION: ["🚨"]})
        tracker.record(ctx1)
        transition = tracker.record(ctx2)
        assert transition.severity == TransitionSeverity.EMERGENCY

    def test_current_property(self, tracker, encoder):
        """current should return latest context."""
        assert tracker.current is None
        ctx = encoder.encode(time="morning")
        tracker.record(ctx)
        assert tracker.current == ctx

    def test_history_property(self, tracker, encoder):
        """history should return all recorded contexts."""
        ctx1 = encoder.encode(time="morning")
        ctx2 = encoder.encode(time="evening")
        tracker.record(ctx1)
        tracker.record(ctx2)
        assert tracker.history_count == 2

    def test_history_trimming(self, encoder):
        """History should be trimmed to max_history."""
        tracker = StateTracker(max_history=5)
        for i in range(10):
            tracker.record(encoder.encode(time="morning" if i % 2 == 0 else "evening"))
        assert tracker.history_count == 5

    def test_get_recent(self, tracker, encoder):
        """get_recent should return limited history."""
        for _ in range(10):
            tracker.record(encoder.encode(time="morning"))
        recent = tracker.get_recent(3)
        assert len(recent) == 3

    def test_clear(self, tracker, encoder):
        """clear should remove all history."""
        tracker.record(encoder.encode(time="morning"))
        tracker.record(encoder.encode(time="evening"))
        tracker.clear()
        assert tracker.history_count == 0
        assert tracker.current is None


class TestStateTrackerHandlers:
    """Test StateTracker transition handlers."""

    def test_register_handler(self, tracker, encoder):
        """Handler should be called on transition."""
        calls = []

        def handler(t: Transition):
            calls.append(t)

        tracker.register_handler(TransitionSeverity.MINOR, handler)
        tracker.record(encoder.encode(time="morning"))
        tracker.record(encoder.encode(time="evening"))

        assert len(calls) == 1
        assert calls[0].severity == TransitionSeverity.MINOR

    def test_unregister_handler(self, tracker, encoder):
        """Unregistered handler should not be called."""
        calls = []

        def handler(t: Transition):
            calls.append(t)

        tracker.register_handler(TransitionSeverity.MINOR, handler)
        tracker.record(encoder.encode(time="morning"))
        tracker.unregister_handler(TransitionSeverity.MINOR, handler)
        tracker.record(encoder.encode(time="evening"))

        assert len(calls) == 0  # First record doesn't trigger, unregistered before second

    def test_unregister_missing_handler(self, tracker):
        """Unregistering missing handler should return False."""

        def handler(t: Transition):
            pass

        result = tracker.unregister_handler(TransitionSeverity.MINOR, handler)
        assert result is False

    def test_multiple_handlers(self, tracker, encoder):
        """Multiple handlers should all be called."""
        calls1 = []
        calls2 = []

        tracker.register_handler(TransitionSeverity.MINOR, lambda t: calls1.append(t))
        tracker.register_handler(TransitionSeverity.MINOR, lambda t: calls2.append(t))

        tracker.record(encoder.encode(time="morning"))
        tracker.record(encoder.encode(time="evening"))

        assert len(calls1) == 1
        assert len(calls2) == 1

    def test_handler_only_for_severity(self, tracker, encoder):
        """Handler should only be called for matching severity."""
        minor_calls = []
        major_calls = []

        tracker.register_handler(TransitionSeverity.MINOR, lambda t: minor_calls.append(t))
        tracker.register_handler(TransitionSeverity.MAJOR, lambda t: major_calls.append(t))

        tracker.record(encoder.encode(time="morning"))
        tracker.record(encoder.encode(time="evening"))  # MINOR change

        assert len(minor_calls) == 1
        assert len(major_calls) == 0


class TestFindTransitions:
    """Test finding transitions in history."""

    def test_find_transitions_empty(self, tracker):
        """Empty history should return no transitions."""
        assert tracker.find_transitions() == []

    def test_find_transitions_single(self, tracker, encoder):
        """Single record should return no transitions."""
        tracker.record(encoder.encode(time="morning"))
        assert tracker.find_transitions() == []

    def test_find_transitions_with_changes(self, tracker, encoder):
        """Should find transitions above minimum severity."""
        tracker.record(encoder.encode(time="morning"))
        tracker.record(encoder.encode(time="evening"))
        tracker.record(encoder.encode(time="night"))

        transitions = tracker.find_transitions(TransitionSeverity.MINOR)
        assert len(transitions) == 2

    def test_find_transitions_filter_severity(self, tracker, encoder):
        """Should filter by minimum severity."""
        # Record some minor changes
        tracker.record(encoder.encode(time="morning"))
        tracker.record(encoder.encode(time="evening"))

        # Record a major change (3+ dimensions)
        tracker.record(encoder.encode(time="night", space="office", state="tired"))

        minor = tracker.find_transitions(TransitionSeverity.MINOR)
        major = tracker.find_transitions(TransitionSeverity.MAJOR)

        assert len(minor) > len(major)
