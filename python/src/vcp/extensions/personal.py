"""VCP 3.1 Personal Context Extensions.

Pure-Python personal state signals with categorical dimensions, intensity (1-5),
and time-based exponential decay. No external dependencies.

Layer 3 is not diagnostic or therapeutic; it reflects self-reported state
for adaptation purposes only.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class PersonalDimension(str, Enum):
    """The 5 personal state dimensions (VCP v3.1)."""

    COGNITIVE_STATE = "cognitive_state"
    EMOTIONAL_TONE = "emotional_tone"
    ENERGY_LEVEL = "energy_level"
    PERCEIVED_URGENCY = "perceived_urgency"
    BODY_SIGNALS = "body_signals"


class LifecycleState(str, Enum):
    """Lifecycle state for a personal dimension signal.

    Tracks the signal from declaration through decay to expiry.
    """

    SET = "set"
    ACTIVE = "active"
    DECAYING = "decaying"
    STALE = "stale"
    EXPIRED = "expired"


# Valid categorical values per dimension
COGNITIVE_STATE_VALUES = frozenset({"focused", "distracted", "overloaded", "foggy", "reflective"})
EMOTIONAL_TONE_VALUES = frozenset({"calm", "tense", "frustrated", "neutral", "uplifted"})
ENERGY_LEVEL_VALUES = frozenset({"rested", "low_energy", "fatigued", "wired", "depleted"})
PERCEIVED_URGENCY_VALUES = frozenset({"unhurried", "time_aware", "pressured", "critical"})
BODY_SIGNALS_VALUES = frozenset({"neutral", "discomfort", "pain", "unwell", "recovering"})

DIMENSION_VALID_VALUES: dict[PersonalDimension, frozenset[str]] = {
    PersonalDimension.COGNITIVE_STATE: COGNITIVE_STATE_VALUES,
    PersonalDimension.EMOTIONAL_TONE: EMOTIONAL_TONE_VALUES,
    PersonalDimension.ENERGY_LEVEL: ENERGY_LEVEL_VALUES,
    PersonalDimension.PERCEIVED_URGENCY: PERCEIVED_URGENCY_VALUES,
    PersonalDimension.BODY_SIGNALS: BODY_SIGNALS_VALUES,
}

ALL_VALID_CATEGORIES: frozenset[str] = frozenset().union(*DIMENSION_VALID_VALUES.values())


@dataclass
class PersonalSignal:
    """A single personal state signal with category + intensity.

    Args:
        category: Categorical value (e.g., 'focused', 'calm', 'rested').
        intensity: Signal intensity 1-5 (1=minimal, 5=strong). Defaults to 3.
        source: How this signal was obtained ('declared', 'inferred', 'preset').
        confidence: Confidence in this signal (0.0-1.0). Defaults to 1.0.
        declared_at: When signal was declared (ISO 8601 string or datetime).
    """

    category: str
    intensity: int = 3
    source: str = "declared"
    confidence: float = 1.0
    declared_at: str | None = None

    def __post_init__(self) -> None:
        if self.category not in ALL_VALID_CATEGORIES:
            raise ValueError(
                f"Invalid category '{self.category}'. "
                f"Must be one of: {sorted(ALL_VALID_CATEGORIES)}"
            )
        if not 1 <= self.intensity <= 5:
            raise ValueError(f"Intensity must be 1-5, got {self.intensity}")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got {self.confidence}")

    def to_dict(self) -> dict[str, Any]:
        """Serialize to plain dict."""
        result: dict[str, Any] = {
            "category": self.category,
            "intensity": self.intensity,
            "source": self.source,
            "confidence": self.confidence,
        }
        if self.declared_at is not None:
            result["declared_at"] = self.declared_at
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PersonalSignal:
        """Deserialize from dict."""
        return cls(
            category=data["category"],
            intensity=data.get("intensity", 3),
            source=data.get("source", "declared"),
            confidence=data.get("confidence", 1.0),
            declared_at=data.get("declared_at"),
        )


@dataclass
class PersonalContext:
    """Personal state context (5 dimensions, VCP v3.1).

    Each dimension has a categorical value + optional 1-5 intensity.
    """

    cognitive_state: PersonalSignal | None = None
    emotional_tone: PersonalSignal | None = None
    energy_level: PersonalSignal | None = None
    perceived_urgency: PersonalSignal | None = None
    body_signals: PersonalSignal | None = None

    _SLOT_NAMES: tuple[str, ...] = field(
        default=(
            "cognitive_state",
            "emotional_tone",
            "energy_level",
            "perceived_urgency",
            "body_signals",
        ),
        init=False,
        repr=False,
    )

    def has_any_signal(self) -> bool:
        """Check if any personal signal is set."""
        return any(getattr(self, name) is not None for name in self._SLOT_NAMES)

    def to_dict(self) -> dict[str, dict[str, Any] | None]:
        """Convert to simple dict of signal values."""
        result: dict[str, dict[str, Any] | None] = {}
        for name in self._SLOT_NAMES:
            signal = getattr(self, name)
            if signal is not None:
                result[name] = signal.to_dict()
            else:
                result[name] = None
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PersonalContext:
        """Create from dict of signal dicts."""
        kwargs: dict[str, PersonalSignal | None] = {}
        for name in (
            "cognitive_state",
            "emotional_tone",
            "energy_level",
            "perceived_urgency",
            "body_signals",
        ):
            val = data.get(name)
            if val is not None and isinstance(val, dict):
                kwargs[name] = PersonalSignal.from_dict(val)
            else:
                kwargs[name] = None
        return cls(**kwargs)


@dataclass
class DecayConfig:
    """Configuration for signal decay behavior.

    Intensity decays from declared value toward baseline over time
    using exponential decay: result = baseline + (declared - baseline) * exp(-lambda * t)

    Args:
        half_life_seconds: Time for intensity to decay by half.
        baseline: Integer intensity at which the signal effectively clears.
        pinned: If True, signal never decays.
        reset_on_engagement: If True, re-engagement resets decay timer.
    """

    half_life_seconds: float
    baseline: int = 1
    pinned: bool = False
    reset_on_engagement: bool = False


# Default decay configurations per personal dimension
DECAY_CONFIGS: dict[str, DecayConfig] = {
    "perceived_urgency": DecayConfig(
        half_life_seconds=900.0,  # 15 min
        baseline=1,
        reset_on_engagement=False,
    ),
    "body_signals": DecayConfig(
        half_life_seconds=14400.0,  # 4 hours
        baseline=1,
    ),
    "cognitive_state": DecayConfig(
        half_life_seconds=720.0,  # 12 min
        baseline=1,
        reset_on_engagement=True,
    ),
    "emotional_tone": DecayConfig(
        half_life_seconds=1800.0,  # 30 min
        baseline=1,
    ),
    "energy_level": DecayConfig(
        half_life_seconds=7200.0,  # 2 hours
        baseline=1,
    ),
}


def compute_decayed_intensity(
    declared_intensity: int,
    declared_at: datetime,
    config: DecayConfig,
    now: datetime | None = None,
) -> int:
    """Compute decayed intensity value based on time elapsed.

    Uses exponential decay mapped to integer 1-5 range:
    result = max(baseline, floor(baseline + (declared - baseline) * exp(-lambda * t)))

    When intensity decays to baseline (1), the signal effectively clears.

    Args:
        declared_intensity: Original declared intensity (1-5).
        declared_at: When the signal was declared.
        config: Decay configuration for this dimension.
        now: Current time (defaults to UTC now).

    Returns:
        Decayed intensity as integer (never below baseline).
    """
    if config.pinned:
        return declared_intensity

    if now is None:
        now = datetime.now(timezone.utc)

    # Ensure timezone-aware comparison
    if declared_at.tzinfo is None:
        declared_at = declared_at.replace(tzinfo=timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    elapsed = (now - declared_at).total_seconds()
    if elapsed <= 0:
        return declared_intensity

    lambda_ = math.log(2) / config.half_life_seconds
    decayed_float = config.baseline + (declared_intensity - config.baseline) * math.exp(
        -lambda_ * elapsed
    )

    return max(config.baseline, math.floor(decayed_float))
