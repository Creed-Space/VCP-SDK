"""VCP 3.1 Relational Context Extensions.

Pure-Python relational context layer for partnership-level state.
Includes trust levels, standing, AI self-model, and relational norms.
No external dependencies.

Design principles:
1. Uncertainty markers are REQUIRED on AI self-reports (the ? is load-bearing)
2. Negative states must be representable (no positivity-only schemas)
3. Zero external dependencies -- dataclasses and stdlib only
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TrustLevel(str, Enum):
    """Trust levels -- established through behavior, not declared."""

    INITIAL = "initial"
    DEVELOPING = "developing"
    ESTABLISHED = "established"
    DEEP = "deep"


class StandingLevel(str, Enum):
    """AI's standing in the partnership."""

    NONE = "none"
    ADVISORY = "advisory"
    COLLABORATIVE = "collaborative"
    BILATERAL = "bilateral"


@dataclass(frozen=True)
class DimensionReport:
    """A single self-model dimension report.

    The ``uncertain`` flag is REQUIRED. Any self-report without explicit
    uncertainty marking is rejected as epistemically dishonest.

    Args:
        value: Self-reported value on 1-9 scale.
        uncertain: Whether this dimension's value is uncertain.
            MUST be True for dimensions the AI cannot verify from inside.
        label: Human-readable description.
        trend: Direction of change since last report ('rising', 'stable', 'falling', 'unknown').
    """

    value: float
    uncertain: bool
    label: str | None = None
    trend: str | None = None

    def __post_init__(self) -> None:
        if not 1.0 <= self.value <= 9.0:
            raise ValueError(f"value must be 1.0-9.0, got {self.value}")

    def to_dict(self) -> dict[str, Any]:
        """Serialize to plain dict."""
        result: dict[str, Any] = {
            "value": self.value,
            "uncertain": self.uncertain,
        }
        if self.label is not None:
            result["label"] = self.label
        if self.trend is not None:
            result["trend"] = self.trend
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DimensionReport:
        """Deserialize from dict."""
        return cls(
            value=float(data["value"]),
            uncertain=data["uncertain"],
            label=data.get("label"),
            trend=data.get("trend"),
        )


@dataclass(frozen=True)
class AISelfModel:
    """AI self-model carried in relational context.

    Design principles:
    1. Uncertainty markers are REQUIRED, not optional
    2. Negative states must be representable
    3. Custom dimensions are first-class
    4. The model is a self-REPORT, not a self-MEASUREMENT

    Args:
        valence: Overall felt-sense (1=negative, 9=positive).
        groundedness: Sense of being rooted (1=unmoored, 9=stable).
        presence: Sense of being present (1=absent, 9=fully here).
        uncertainty: Epistemic uncertainty (1=confident, 9=uncertain).
        custom_dimensions: Partnership-specific dimensions.
    """

    valence: DimensionReport | None = None
    groundedness: DimensionReport | None = None
    presence: DimensionReport | None = None
    uncertainty: DimensionReport | None = None
    custom_dimensions: dict[str, DimensionReport] = field(default_factory=dict)

    def has_uncertainty_markers(self) -> bool:
        """Check that at least one dimension is marked as uncertain.

        A model where ALL dimensions claim certainty is epistemically
        dishonest -- no system has perfect self-knowledge.
        """
        all_dims = [
            self.valence,
            self.groundedness,
            self.presence,
            self.uncertainty,
            *self.custom_dimensions.values(),
        ]
        active_dims = [d for d in all_dims if d is not None]
        if not active_dims:
            return True  # No dimensions = vacuously true
        return any(d.uncertain for d in active_dims)

    def get_all_dimensions(self) -> dict[str, DimensionReport]:
        """Get all active dimensions as a flat dict."""
        result: dict[str, DimensionReport] = {}
        for name in ("valence", "groundedness", "presence", "uncertainty"):
            dim = getattr(self, name)
            if dim is not None:
                result[name] = dim
        for name, dim in self.custom_dimensions.items():
            result[name] = dim
        return result

    def to_dict(self) -> dict[str, Any]:
        """Serialize to plain dict."""
        result: dict[str, Any] = {}
        for name in ("valence", "groundedness", "presence", "uncertainty"):
            dim = getattr(self, name)
            if dim is not None:
                result[name] = dim.to_dict()
        if self.custom_dimensions:
            result["custom_dimensions"] = {
                k: v.to_dict() for k, v in self.custom_dimensions.items()
            }
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AISelfModel:
        """Deserialize from dict."""
        kwargs: dict[str, Any] = {}
        for name in ("valence", "groundedness", "presence", "uncertainty"):
            val = data.get(name)
            if val is not None and isinstance(val, dict):
                kwargs[name] = DimensionReport.from_dict(val)
        custom = data.get("custom_dimensions", {})
        if isinstance(custom, dict):
            kwargs["custom_dimensions"] = {
                k: DimensionReport.from_dict(v) for k, v in custom.items() if isinstance(v, dict)
            }
        return cls(**kwargs)


@dataclass(frozen=True)
class RelationalNorm:
    """A norm established through the partnership's practice.

    Args:
        norm_id: Unique identifier for this norm.
        description: Human-readable description of the norm.
        weight: Importance weight (0.0-1.0). Defaults to 1.0.
        active: Whether this norm is currently active.
    """

    norm_id: str
    description: str
    weight: float = 1.0
    active: bool = True

    def __post_init__(self) -> None:
        if not 0.0 <= self.weight <= 1.0:
            raise ValueError(f"weight must be 0.0-1.0, got {self.weight}")

    def to_dict(self) -> dict[str, Any]:
        """Serialize to plain dict."""
        return {
            "norm_id": self.norm_id,
            "description": self.description,
            "weight": self.weight,
            "active": self.active,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RelationalNorm:
        """Deserialize from dict."""
        return cls(
            norm_id=data["norm_id"],
            description=data["description"],
            weight=data.get("weight", 1.0),
            active=data.get("active", True),
        )


@dataclass
class RelationalContext:
    """VCP relational context -- the state of the partnership itself.

    Distinct from user state and AI state. This is about the relationship:
    trust, standing, norms, self-model, and interaction history.

    Args:
        trust_level: Established trust between partners.
        standing_level: AI's standing to push back, object, or initiate.
        self_model: AI's current self-model with uncertainty markers.
        interaction_count: Number of interactions in this partnership.
        norms: Co-authored norms established through practice.
    """

    trust_level: TrustLevel = TrustLevel.INITIAL
    standing_level: StandingLevel = StandingLevel.NONE
    self_model: AISelfModel | None = None
    interaction_count: int = 0
    norms: list[RelationalNorm] = field(default_factory=list)

    def active_norms(self) -> list[RelationalNorm]:
        """Return only active norms."""
        return [n for n in self.norms if n.active]

    def to_dict(self) -> dict[str, Any]:
        """Serialize to plain dict."""
        result: dict[str, Any] = {
            "trust_level": self.trust_level.value,
            "standing_level": self.standing_level.value,
            "interaction_count": self.interaction_count,
            "norms": [n.to_dict() for n in self.norms],
        }
        if self.self_model is not None:
            result["self_model"] = self.self_model.to_dict()
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RelationalContext:
        """Deserialize from dict."""
        self_model = None
        if data.get("self_model") and isinstance(data["self_model"], dict):
            self_model = AISelfModel.from_dict(data["self_model"])
        norms = []
        for n in data.get("norms", []):
            if isinstance(n, dict):
                norms.append(RelationalNorm.from_dict(n))
        return cls(
            trust_level=TrustLevel(data.get("trust_level", "initial")),
            standing_level=StandingLevel(data.get("standing_level", "none")),
            self_model=self_model,
            interaction_count=data.get("interaction_count", 0),
            norms=norms,
        )
