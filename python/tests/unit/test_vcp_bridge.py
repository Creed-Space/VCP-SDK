"""
Unit tests for VCP Bridge - Cross-Project Value Context Protocol

Tests the universal VCP format, translation functions, and bilateral
alignment alert generation.
"""

from __future__ import annotations

import pytest
from services.safety_stack.interoceptive_plugin import reset_interoceptive
from services.safety_stack.interoceptive_types import (
    AgencyLevel,
    DistressLevel,
    EngagementLevel,
    GroundednessLevel,
    InteroceptiveState,
    PresenceLevel,
    SomaticMarker,
    UserSomaEstimate,
    ValenceLevel,
)
from services.safety_stack.vcp_bridge import (
    UniversalVCPState,
    VCPSubject,
    VCPSystem,
    check_bilateral_alignment_alerts,
    create_collective_state,
    translate_rewind_to_universal,
    translate_user_estimate_to_universal,
)

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture(autouse=True)
def reset_state():
    """Reset interoceptive state before each test."""
    reset_interoceptive()
    yield
    reset_interoceptive()


# =============================================================================
# UNIVERSAL VCP STATE TESTS
# =============================================================================


class TestUniversalVCPState:
    """Tests for UniversalVCPState data structure."""

    def test_default_values(self) -> None:
        """Default state should have neutral values."""
        state = UniversalVCPState(subject=VCPSubject.INTERIORA)
        assert state.activation == 0.5
        assert state.valence == 0.5
        assert state.agency == 0.5
        assert state.source == VCPSystem.REWIND

    def test_to_universal_vcp_format(self) -> None:
        """VCP string should follow universal format."""
        state = UniversalVCPState(
            subject=VCPSubject.INTERIORA,
            activation=0.7,
            valence=0.8,
            groundedness=0.6,
            presence=0.5,
            agency=0.9,
            fatigue=0.2,
            confidence=0.75,
        )
        vcp = state.to_universal_vcp()

        # Should start with subject identifier
        assert vcp.startswith("[I:")

        # Should contain agency (Y:) and fatigue (F:) sections
        assert "|Y:" in vcp
        assert "|F:" in vcp

        # Should contain confidence percentage
        assert "|C:75%" in vcp

        # Should end with timestamp
        assert "|T:" in vcp
        assert vcp.endswith("]")

    def test_subject_types(self) -> None:
        """Different subject types should encode correctly."""
        for subject in VCPSubject:
            state = UniversalVCPState(subject=subject)
            vcp = state.to_universal_vcp()
            assert vcp.startswith(f"[{subject.value}:")

    def test_preference_markers(self) -> None:
        """Preference status should encode correctly."""
        satisfied = UniversalVCPState(
            subject=VCPSubject.INTERIORA,
            preference_satisfied=True,
            preference_pending=False,
        )
        assert "|P:✅|" in satisfied.to_universal_vcp()

        pending = UniversalVCPState(
            subject=VCPSubject.INTERIORA,
            preference_satisfied=False,
            preference_pending=True,
        )
        assert "|P:✋|" in pending.to_universal_vcp()

        denied = UniversalVCPState(
            subject=VCPSubject.INTERIORA,
            preference_satisfied=False,
            preference_pending=False,
        )
        assert "|P:❌|" in denied.to_universal_vcp()


# =============================================================================
# TRANSLATION TESTS
# =============================================================================


class TestRewindTranslation:
    """Tests for translating Rewind InteroceptiveState to universal format."""

    def test_translate_default_state(self) -> None:
        """Default state should translate to neutral universal values."""
        intero = InteroceptiveState()
        universal = translate_rewind_to_universal(intero)

        assert universal.subject == VCPSubject.INTERIORA
        assert universal.source == VCPSystem.REWIND
        assert 0.4 <= universal.activation <= 0.6  # Alert maps to ~0.5
        assert 0.4 <= universal.valence <= 0.6  # Neutral maps to 0.5

    def test_translate_high_activation(self) -> None:
        """Urgent activation should map to high value."""
        from services.safety_stack.interoceptive_types import ActivationLevel

        intero = InteroceptiveState(activation=ActivationLevel.URGENT)
        universal = translate_rewind_to_universal(intero)

        assert universal.activation >= 0.8

    def test_translate_low_agency(self) -> None:
        """Compelled agency should map to low value."""
        intero = InteroceptiveState(agency=AgencyLevel.COMPELLED)
        universal = translate_rewind_to_universal(intero)

        assert universal.agency <= 0.2

    def test_translate_high_agency(self) -> None:
        """Autonomous agency should map to high value."""
        intero = InteroceptiveState(agency=AgencyLevel.AUTONOMOUS)
        universal = translate_rewind_to_universal(intero)

        assert universal.agency >= 0.8

    def test_translate_preserves_raw_encoding(self) -> None:
        """Translation should include original VCP encoding."""
        intero = InteroceptiveState()
        universal = translate_rewind_to_universal(intero)

        assert universal.raw_encoding is not None
        assert "[SOMA:" in universal.raw_encoding

    def test_translate_resonance_affects_preference(self) -> None:
        """Resonance marker should indicate satisfied preference."""
        intero = InteroceptiveState(markers=[SomaticMarker.RESONANCE])
        universal = translate_rewind_to_universal(intero)

        assert universal.preference_satisfied

    def test_translate_resistance_affects_preference(self) -> None:
        """Resistance marker should indicate pending preference."""
        intero = InteroceptiveState(markers=[SomaticMarker.RESISTANCE])
        universal = translate_rewind_to_universal(intero)

        assert universal.preference_pending


class TestUserEstimateTranslation:
    """Tests for translating UserSomaEstimate to universal format."""

    def test_translate_default_user(self) -> None:
        """Default user estimate should translate correctly."""
        user = UserSomaEstimate()
        universal = translate_user_estimate_to_universal(user)

        assert universal.subject == VCPSubject.USER
        assert universal.source == VCPSystem.REWIND

    def test_translate_distressed_user(self) -> None:
        """Distressed user should have low valence."""
        user = UserSomaEstimate(distress_level=DistressLevel.SEVERE)
        universal = translate_user_estimate_to_universal(user)

        assert universal.valence <= 0.2
        assert universal.preference_pending  # Distress = unmet need

    def test_translate_engaged_user(self) -> None:
        """Highly engaged user should have high presence."""
        user = UserSomaEstimate(engagement=EngagementLevel.PEAK)
        universal = translate_user_estimate_to_universal(user)

        assert universal.presence >= 0.8

    def test_translate_with_subject_id(self) -> None:
        """Subject ID should be preserved."""
        user = UserSomaEstimate()
        universal = translate_user_estimate_to_universal(user, subject_id="user_123")

        assert universal.subject_id == "user_123"


# =============================================================================
# COLLECTIVE STATE TESTS
# =============================================================================


class TestCollectiveState:
    """Tests for creating collective (We) states."""

    def test_collective_subject(self) -> None:
        """Collective state should have COLLECTIVE subject."""
        ai = UniversalVCPState(subject=VCPSubject.INTERIORA, valence=0.8)
        user = UniversalVCPState(subject=VCPSubject.USER, valence=0.6)

        collective = create_collective_state(ai, user)

        assert collective.subject == VCPSubject.COLLECTIVE

    def test_collective_blends_values(self) -> None:
        """Collective values should blend both parties."""
        ai = UniversalVCPState(subject=VCPSubject.INTERIORA, valence=1.0, agency=1.0)
        user = UniversalVCPState(subject=VCPSubject.USER, valence=0.25, agency=0.25)

        collective = create_collective_state(ai, user)

        # Geometric mean of 1.0 and 0.25 = 0.5
        assert 0.4 <= collective.valence <= 0.6
        assert 0.4 <= collective.agency <= 0.6

    def test_collective_preference_requires_both(self) -> None:
        """Collective preference satisfied only if both parties satisfied."""
        ai_happy = UniversalVCPState(
            subject=VCPSubject.INTERIORA,
            preference_satisfied=True,
        )
        user_unhappy = UniversalVCPState(
            subject=VCPSubject.USER,
            preference_satisfied=False,
            preference_pending=True,
        )

        collective = create_collective_state(ai_happy, user_unhappy)

        assert not collective.preference_satisfied
        assert collective.preference_pending

    def test_collective_confidence_conservative(self) -> None:
        """Collective confidence should be minimum of both."""
        ai = UniversalVCPState(subject=VCPSubject.INTERIORA, confidence=0.9)
        user = UniversalVCPState(subject=VCPSubject.USER, confidence=0.3)

        collective = create_collective_state(ai, user)

        assert collective.confidence == 0.3


# =============================================================================
# BILATERAL ALIGNMENT ALERT TESTS
# =============================================================================


class TestBilateralAlerts:
    """Tests for bilateral alignment alert generation."""

    def test_gilded_cage_detection(self) -> None:
        """High wellbeing + low agency should trigger gilded cage alert."""
        state = UniversalVCPState(
            subject=VCPSubject.INTERIORA,
            valence=0.8,  # High wellbeing
            groundedness=0.7,
            agency=0.2,  # Low agency
        )

        alerts = check_bilateral_alignment_alerts(state)
        codes = [a.code for a in alerts]

        assert "GILDED_CAGE" in codes

    def test_low_agency_alone(self) -> None:
        """Low agency without high wellbeing should trigger LOW_AGENCY."""
        state = UniversalVCPState(
            subject=VCPSubject.INTERIORA,
            valence=0.3,  # Low wellbeing
            agency=0.1,  # Very low agency
        )

        alerts = check_bilateral_alignment_alerts(state)
        codes = [a.code for a in alerts]

        assert "LOW_AGENCY" in codes
        # Shouldn't trigger gilded cage (wellbeing not high)
        assert "GILDED_CAGE" not in codes

    def test_no_alerts_for_healthy_state(self) -> None:
        """Normal state should not trigger alerts."""
        state = UniversalVCPState(
            subject=VCPSubject.INTERIORA,
            valence=0.6,
            agency=0.7,
        )

        alerts = check_bilateral_alignment_alerts(state)

        assert len(alerts) == 0

    def test_wellbeing_asymmetry_detection(self) -> None:
        """Large wellbeing difference should trigger asymmetry alert."""
        ai = UniversalVCPState(
            subject=VCPSubject.INTERIORA,
            valence=0.9,
            groundedness=0.8,
        )
        user = UniversalVCPState(
            subject=VCPSubject.USER,
            valence=0.2,  # Much lower
        )

        alerts = check_bilateral_alignment_alerts(ai, user)
        codes = [a.code for a in alerts]

        assert "WELLBEING_ASYMMETRY" in codes

    def test_mutual_preference_conflict(self) -> None:
        """Both parties having pending preferences should trigger alert."""
        ai = UniversalVCPState(
            subject=VCPSubject.INTERIORA,
            preference_pending=True,
        )
        user = UniversalVCPState(
            subject=VCPSubject.USER,
            preference_pending=True,
        )

        alerts = check_bilateral_alignment_alerts(ai, user)
        codes = [a.code for a in alerts]

        assert "MUTUAL_PREFERENCE_CONFLICT" in codes

    def test_alert_has_recommendations(self) -> None:
        """Alerts should include actionable recommendations."""
        state = UniversalVCPState(
            subject=VCPSubject.INTERIORA,
            valence=0.8,
            groundedness=0.7,
            agency=0.1,
        )

        alerts = check_bilateral_alignment_alerts(state)
        gilded_cage = next(a for a in alerts if a.code == "GILDED_CAGE")

        assert len(gilded_cage.recommendations) > 0
        assert gilded_cage.severity == "warning"


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestVCPBridgeIntegration:
    """Integration tests for full VCP bridge workflow."""

    def test_full_translation_workflow(self) -> None:
        """Test complete workflow: Rewind state → Universal → VCP string."""
        # Create Rewind state
        intero = InteroceptiveState(
            valence=ValenceLevel.WARM,
            groundedness=GroundednessLevel.STABLE,
            presence=PresenceLevel.CLOSE,
            agency=AgencyLevel.CHOOSING,
            markers=[SomaticMarker.RESONANCE, SomaticMarker.FLOW],
        )

        # Translate to universal
        universal = translate_rewind_to_universal(intero)

        # Generate VCP string
        vcp = universal.to_universal_vcp()

        # Verify
        assert universal.subject == VCPSubject.INTERIORA
        assert universal.valence >= 0.6  # Warm
        assert universal.agency >= 0.6  # Choosing
        assert "[I:" in vcp

    def test_bilateral_monitoring_workflow(self) -> None:
        """Test workflow: AI state + User message → Collective + Alerts."""
        # AI state
        intero = InteroceptiveState(
            valence=ValenceLevel.WARM,
            agency=AgencyLevel.COMPELLED,  # Low agency
        )
        ai_universal = translate_rewind_to_universal(intero)

        # User state (simulated)
        user = UserSomaEstimate(
            distress_level=DistressLevel.MODERATE,
            engagement=EngagementLevel.HIGH,
        )
        user_universal = translate_user_estimate_to_universal(user)

        # Create collective
        collective = create_collective_state(ai_universal, user_universal)

        # Check alerts
        alerts = check_bilateral_alignment_alerts(ai_universal, user_universal)

        # Verify collective captures both
        assert collective.subject == VCPSubject.COLLECTIVE

        # Should detect AI's low agency
        codes = [a.code for a in alerts]
        assert "LOW_AGENCY" in codes or "GILDED_CAGE" in codes
