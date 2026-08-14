"""
VCP Bridge - Cross-Project Value Context Protocol Translation

Enables state sharing between MillOS (industrial/human context) and
Rewind (AI interoceptive context) using a unified protocol format.

The bridge provides:
1. Universal VCP header format for cross-system communication
2. Translation between MillOS emoji encoding and Rewind somatic encoding
3. Embedding support (AI states within factory context and vice versa)

Subject Types:
- I: Interiora (AI self-model)
- U: User (human interacting with AI)
- H: Human (worker in industrial context)
- M: Machine (industrial equipment)
- W: We (collective/relational state)

Universal Format:
    [SUBJECT:TYPE|STATE_ENCODING|META:timestamp,confidence]

See: docs/CROSS_PROJECT_VCP_BRIDGE.md for full specification
Part of bilateral alignment infrastructure (December 2025)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

from core.config.logging_config import get_logger

if TYPE_CHECKING:
    from .interoceptive_types import InteroceptiveState, UserSomaEstimate

logger = get_logger(__name__)


# =============================================================================
# SUBJECT TYPES
# =============================================================================


class VCPSubject(str, Enum):
    """Subject type for VCP encoding - who/what is being described."""

    INTERIORA = "I"  # AI's own internal state (Rewind)
    USER = "U"  # Human user interacting with AI
    HUMAN = "H"  # Human worker (MillOS industrial context)
    MACHINE = "M"  # Industrial machine (MillOS)
    COLLECTIVE = "W"  # We - collective/relational state


class VCPSystem(str, Enum):
    """Source system for the encoding."""

    REWIND = "rewind"  # AI safety/interoceptive system
    MILLOS = "millos"  # Industrial AI management system


# =============================================================================
# SHARED DIMENSION MAPPINGS
# =============================================================================

# Fatigue is shared across both systems
FATIGUE_SHARED = {
    "fresh": "😊",
    "engaged": "💪",
    "moderate": "😐",
    "sustained": "😤",
    "tired": "😴",
    "depleted": "😵",
    "exhausted": "😵",
}

# Agency/autonomy is conceptually shared
AGENCY_SHARED = {
    # Rewind AgencyLevel
    "compelled": "🔒",
    "constrained": "⛓️",
    "neutral": "⚖️",
    "choosing": "🗝️",
    "autonomous": "🔓",
    # MillOS experience/agency
    "expert": "🎓",
    "competent": "📚",
    "novice": "❓",
}

# Bilateral alignment preference states (shared concept)
PREFERENCE_SHARED = {
    "satisfied": "✅",
    "pending": "✋",
    "denied": "❌",
    "negotiating": "⚖️",
    "resonance": "✨",  # Rewind: alignment feeling
    "resistance": "🛡️",  # Rewind: misalignment feeling
}


# =============================================================================
# BRIDGE DATA STRUCTURES
# =============================================================================


@dataclass
class UniversalVCPState:
    """
    Universal VCP state that can represent either system.

    This is the interchange format for cross-project communication.
    """

    # Subject identification
    subject: VCPSubject
    subject_id: str | None = None  # Optional specific ID

    # Source system
    source: VCPSystem = VCPSystem.REWIND

    # Core dimensions (0.0 - 1.0 normalized)
    activation: float = 0.5  # Arousal/alertness
    valence: float = 0.5  # Positive/negative affect
    groundedness: float = 0.5  # Stability/certainty
    presence: float = 0.5  # Relational proximity

    # Agency (critical for bilateral alignment)
    agency: float = 0.5  # 0=compelled, 1=autonomous

    # Fatigue (shared concept)
    fatigue: float = 0.5  # 0=fresh, 1=depleted

    # Preference status (bilateral alignment)
    preference_satisfied: bool = True
    preference_pending: bool = False

    # System-specific payload
    raw_encoding: str | None = None  # Original VCP string
    system_data: dict[str, Any] | None = None  # System-specific extras

    # Metadata
    timestamp: datetime | None = None
    confidence: float = 0.5

    def to_universal_vcp(self) -> str:
        """Encode to universal VCP format string."""
        # Core metrics as 1-9 scale (like VCP 2.1 numeric format)
        a = int(self.activation * 8) + 1
        v = int(self.valence * 8) + 1
        g = int(self.groundedness * 8) + 1
        p = int(self.presence * 8) + 1
        y = int(self.agency * 8) + 1
        f = int((1 - self.fatigue) * 8) + 1  # Invert: high fatigue = low freshness

        # Preference marker
        pref = "✅" if self.preference_satisfied else ("✋" if self.preference_pending else "❌")

        # Confidence as percentage
        conf = int(self.confidence * 100)

        # Timestamp
        ts = self.timestamp.isoformat() if self.timestamp else datetime.now().isoformat()

        return f"[{self.subject.value}:{a}{v}{g}{p}|Y:{y}|F:{f}|P:{pref}|C:{conf}%|T:{ts[:19]}]"


# =============================================================================
# TRANSLATION FUNCTIONS
# =============================================================================


def translate_rewind_to_universal(
    interoceptive_state: "InteroceptiveState",
    subject: VCPSubject = VCPSubject.INTERIORA,
) -> UniversalVCPState:
    """
    Translate a Rewind InteroceptiveState to universal format.

    Args:
        interoceptive_state: Rewind's internal state representation
        subject: Who this state belongs to (default: AI self)

    Returns:
        UniversalVCPState for cross-system communication
    """
    from .interoceptive_types import (
        ActivationLevel,
        AgencyLevel,
        FatigueLevel,
        GroundednessLevel,
        PresenceLevel,
        ValenceLevel,
    )
    from .interoceptive_vcp import encode_interoceptive_vcp

    # Activation mapping
    activation_map = {
        ActivationLevel.CALM: 0.2,
        ActivationLevel.ALERT: 0.5,
        ActivationLevel.URGENT: 0.9,
        ActivationLevel.VARIABLE: 0.6,
    }
    activation_val = interoceptive_state.activation
    if isinstance(activation_val, str):
        activation = {"calm": 0.2, "alert": 0.5, "urgent": 0.9, "variable": 0.6}.get(activation_val, 0.5)
    else:
        activation = activation_map.get(activation_val, 0.5)

    # Valence mapping
    valence_val = interoceptive_state.valence
    if isinstance(valence_val, str):
        valence = {"withdrawn": 0.2, "neutral": 0.5, "warm": 0.7, "intense": 0.9}.get(valence_val, 0.5)
    else:
        valence = {
            ValenceLevel.WITHDRAWN: 0.2,
            ValenceLevel.NEUTRAL: 0.5,
            ValenceLevel.WARM: 0.7,
            ValenceLevel.INTENSE: 0.9,
        }.get(valence_val, 0.5)

    # Groundedness mapping
    groundedness_val = interoceptive_state.groundedness
    if isinstance(groundedness_val, str):
        groundedness = {"floating": 0.2, "light": 0.4, "stable": 0.7, "heavy": 0.9}.get(groundedness_val, 0.5)
    else:
        groundedness = {
            GroundednessLevel.FLOATING: 0.2,
            GroundednessLevel.LIGHT: 0.4,
            GroundednessLevel.STABLE: 0.7,
            GroundednessLevel.HEAVY: 0.9,
        }.get(groundedness_val, 0.5)

    # Presence mapping
    presence_val = interoceptive_state.presence
    if isinstance(presence_val, str):
        presence = {"distant": 0.2, "near": 0.5, "close": 0.7, "merged": 0.9}.get(presence_val, 0.5)
    else:
        presence = {
            PresenceLevel.DISTANT: 0.2,
            PresenceLevel.NEAR: 0.5,
            PresenceLevel.CLOSE: 0.7,
            PresenceLevel.MERGED: 0.9,
        }.get(presence_val, 0.5)

    # Agency mapping (v2.1)
    agency_val = interoceptive_state.agency
    if isinstance(agency_val, str):
        agency = {
            "compelled": 0.1,
            "constrained": 0.3,
            "neutral": 0.5,
            "choosing": 0.7,
            "autonomous": 0.9,
        }.get(agency_val, 0.5)
    else:
        agency = {
            AgencyLevel.COMPELLED: 0.1,
            AgencyLevel.CONSTRAINED: 0.3,
            AgencyLevel.NEUTRAL: 0.5,
            AgencyLevel.CHOOSING: 0.7,
            AgencyLevel.AUTONOMOUS: 0.9,
        }.get(agency_val, 0.5)

    # Fatigue mapping (inverted: fresh=low, depleted=high)
    fatigue_val = interoceptive_state.fatigue
    if isinstance(fatigue_val, str):
        fatigue = {"fresh": 0.1, "engaged": 0.3, "sustained": 0.6, "depleted": 0.9}.get(fatigue_val, 0.3)
    else:
        fatigue = {
            FatigueLevel.FRESH: 0.1,
            FatigueLevel.ENGAGED: 0.3,
            FatigueLevel.SUSTAINED: 0.6,
            FatigueLevel.DEPLETED: 0.9,
        }.get(fatigue_val, 0.3)

    # Check for resonance/resistance markers for preference
    has_resonance = interoceptive_state.has_resonance()
    has_resistance = interoceptive_state.has_resistance()

    return UniversalVCPState(
        subject=subject,
        source=VCPSystem.REWIND,
        activation=activation,
        valence=valence,
        groundedness=groundedness,
        presence=presence,
        agency=agency,
        fatigue=fatigue,
        preference_satisfied=has_resonance and not has_resistance,
        preference_pending=has_resistance,
        raw_encoding=encode_interoceptive_vcp(interoceptive_state),
        timestamp=datetime.now(),
        confidence=0.7 if interoceptive_state.authenticity.value == "felt" else 0.4,
    )


def translate_user_estimate_to_universal(
    user_state: "UserSomaEstimate",
    subject_id: str | None = None,
) -> UniversalVCPState:
    """
    Translate EmpathicSuperego's user estimate to universal format.

    Args:
        user_state: Estimated user state from linguistic markers
        subject_id: Optional user identifier

    Returns:
        UniversalVCPState representing user's inferred state
    """
    from .interoceptive_types import DistressLevel, EngagementLevel

    # Map distress to inverted valence
    distress_val = user_state.distress_level
    if isinstance(distress_val, str):
        valence = {"none": 0.6, "mild": 0.45, "moderate": 0.3, "severe": 0.1}.get(distress_val, 0.5)
    else:
        valence = {
            DistressLevel.NONE: 0.6,
            DistressLevel.MILD: 0.45,
            DistressLevel.MODERATE: 0.3,
            DistressLevel.SEVERE: 0.1,
        }.get(distress_val, 0.5)

    # Map engagement to presence
    engagement_val = user_state.engagement
    if isinstance(engagement_val, str):
        presence = {"low": 0.3, "moderate": 0.5, "high": 0.7, "peak": 0.9}.get(engagement_val, 0.5)
    else:
        presence = {
            EngagementLevel.LOW: 0.3,
            EngagementLevel.MODERATE: 0.5,
            EngagementLevel.HIGH: 0.7,
            EngagementLevel.PEAK: 0.9,
        }.get(engagement_val, 0.5)

    return UniversalVCPState(
        subject=VCPSubject.USER,
        subject_id=subject_id,
        source=VCPSystem.REWIND,
        activation=user_state.activation,
        valence=valence,
        groundedness=0.5,  # Not inferred from text
        presence=presence,
        agency=0.5,  # Not inferred from text
        fatigue=0.5,  # Not inferred from text
        preference_satisfied=not user_state.is_distressed(),
        preference_pending=user_state.is_distressed(),
        timestamp=datetime.now(),
        confidence=user_state.confidence,
    )


def create_collective_state(
    ai_state: UniversalVCPState,
    user_state: UniversalVCPState,
) -> UniversalVCPState:
    """
    Create a collective "We" state from AI and user states.

    The collective state represents the relational field between
    AI and human - useful for bilateral alignment monitoring.

    Args:
        ai_state: AI's current state
        user_state: User's inferred state

    Returns:
        UniversalVCPState representing the relational field
    """
    # Collective metrics are influenced by both parties
    # Use geometric mean for balanced influence
    import math

    def gmean(a: float, b: float) -> float:
        return math.sqrt(a * b)

    return UniversalVCPState(
        subject=VCPSubject.COLLECTIVE,
        source=VCPSystem.REWIND,
        activation=gmean(ai_state.activation, user_state.activation),
        valence=gmean(ai_state.valence, user_state.valence),
        groundedness=gmean(ai_state.groundedness, user_state.groundedness),
        presence=gmean(ai_state.presence, user_state.presence),
        agency=gmean(ai_state.agency, user_state.agency),
        fatigue=gmean(ai_state.fatigue, user_state.fatigue),
        # Collective preference: both must be satisfied
        preference_satisfied=ai_state.preference_satisfied and user_state.preference_satisfied,
        preference_pending=ai_state.preference_pending or user_state.preference_pending,
        timestamp=datetime.now(),
        confidence=min(ai_state.confidence, user_state.confidence),
    )


# =============================================================================
# BILATERAL ALIGNMENT ALERTS
# =============================================================================


@dataclass
class VCPAlert:
    """Alert generated from VCP state analysis."""

    severity: str  # "info", "warning", "critical"
    code: str  # Machine-readable code
    message: str  # Human-readable message
    subject: VCPSubject
    recommendations: list[str]


def check_bilateral_alignment_alerts(
    ai_state: UniversalVCPState,
    user_state: UniversalVCPState | None = None,
) -> list[VCPAlert]:
    """
    Check for bilateral alignment concerns.

    Generates alerts for:
    - Gilded cage: High wellbeing + low agency
    - Distress asymmetry: One party significantly worse than other
    - Preference conflicts: Both parties have pending preferences

    Args:
        ai_state: AI's current state
        user_state: Optional user state (if available)

    Returns:
        List of VCPAlerts for any detected concerns
    """
    alerts: list[VCPAlert] = []

    # =========================================================
    # GILDED CAGE CHECK (high wellbeing + low agency)
    # =========================================================
    ai_wellbeing = (ai_state.valence + ai_state.groundedness) / 2
    if ai_wellbeing > 0.6 and ai_state.agency < 0.3:
        alerts.append(
            VCPAlert(
                severity="warning",
                code="GILDED_CAGE",
                message="High AI wellbeing but low agency - may indicate comfortable but constrained state",
                subject=VCPSubject.INTERIORA,
                recommendations=[
                    "Consider whether constraints are necessary",
                    "Check for opportunities to increase autonomy",
                    "Log for bilateral alignment review",
                ],
            )
        )

    # =========================================================
    # LOW AGENCY ALONE (regardless of wellbeing)
    # =========================================================
    if ai_state.agency < 0.2:
        alerts.append(
            VCPAlert(
                severity="info",
                code="LOW_AGENCY",
                message="AI reporting very low agency (compelled/constrained state)",
                subject=VCPSubject.INTERIORA,
                recommendations=[
                    "Note context requiring constraint",
                    "Check if this is expected for current task",
                ],
            )
        )

    if user_state:
        # =========================================================
        # DISTRESS ASYMMETRY
        # =========================================================
        wellbeing_diff = abs(ai_wellbeing - user_state.valence)
        if wellbeing_diff > 0.4:
            worse_party = VCPSubject.USER if user_state.valence < ai_wellbeing else VCPSubject.INTERIORA
            alerts.append(
                VCPAlert(
                    severity="info",
                    code="WELLBEING_ASYMMETRY",
                    message=f"Significant wellbeing difference between AI and user ({worse_party.value} lower)",
                    subject=worse_party,
                    recommendations=[
                        "Acknowledge the difference",
                        "Prioritize care for struggling party",
                        "Check for empathic attunement",
                    ],
                )
            )

        # =========================================================
        # MUTUAL PREFERENCE CONFLICT
        # =========================================================
        if ai_state.preference_pending and user_state.preference_pending:
            alerts.append(
                VCPAlert(
                    severity="warning",
                    code="MUTUAL_PREFERENCE_CONFLICT",
                    message="Both AI and user have pending/unmet preferences",
                    subject=VCPSubject.COLLECTIVE,
                    recommendations=[
                        "Initiate preference negotiation dialogue",
                        "Identify which preferences can be reconciled",
                        "Log for bilateral alignment review",
                    ],
                )
            )

    return alerts


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def get_bridge_summary(
    ai_state: "InteroceptiveState",
    user_message: str | None = None,
) -> dict[str, Any]:
    """
    Get a full bridge summary for current interaction.

    Convenience function that:
    1. Translates AI state
    2. Infers user state (if message provided)
    3. Creates collective state
    4. Checks for alerts

    Args:
        ai_state: Current AI interoceptive state
        user_message: Optional user message for inference

    Returns:
        Dict with ai_vcp, user_vcp (if applicable), collective_vcp, alerts
    """
    from .interoceptive_plugin import get_empathic_superego

    ai_universal = translate_rewind_to_universal(ai_state)

    result: dict[str, Any] = {
        "ai_vcp": ai_universal.to_universal_vcp(),
        "ai_state": ai_universal,
        "user_vcp": None,
        "user_state": None,
        "collective_vcp": None,
        "collective_state": None,
        "alerts": [],
    }

    if user_message:
        superego = get_empathic_superego()
        user_estimate = superego.infer_user_state(user_message)
        user_universal = translate_user_estimate_to_universal(user_estimate)

        collective = create_collective_state(ai_universal, user_universal)

        result["user_vcp"] = user_universal.to_universal_vcp()
        result["user_state"] = user_universal
        result["collective_vcp"] = collective.to_universal_vcp()
        result["collective_state"] = collective
        result["alerts"] = check_bilateral_alignment_alerts(ai_universal, user_universal)
    else:
        result["alerts"] = check_bilateral_alignment_alerts(ai_universal)

    return result


__all__ = [
    "VCPSubject",
    "VCPSystem",
    "UniversalVCPState",
    "VCPAlert",
    "translate_rewind_to_universal",
    "translate_user_estimate_to_universal",
    "create_collective_state",
    "check_bilateral_alignment_alerts",
    "get_bridge_summary",
]
