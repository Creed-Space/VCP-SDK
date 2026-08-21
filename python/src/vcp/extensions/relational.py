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

from copy import deepcopy
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
    confidence: float | None = None

    def __post_init__(self) -> None:
        if not 1.0 <= self.value <= 9.0:
            raise ValueError(f"value must be 1.0-9.0, got {self.value}")
        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence must be 0.0-1.0, got {self.confidence}")

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
        if self.confidence is not None:
            result["confidence"] = self.confidence
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DimensionReport:
        """Deserialize from dict."""
        return cls(
            value=float(data["value"]),
            uncertain=data["uncertain"],
            label=data.get("label"),
            trend=data.get("trend"),
            confidence=data.get("confidence"),
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
    task_fit: DimensionReport | None = None
    friction: DimensionReport | None = None
    groundedness: DimensionReport | None = None
    presence: DimensionReport | None = None
    uncertainty: DimensionReport | None = None
    depth: DimensionReport | None = None
    custom_dimensions: dict[str, DimensionReport] = field(default_factory=dict)
    scaffold_version: str | None = None
    scaffold_type: str | None = None

    def has_uncertainty_markers(self) -> bool:
        """Check that at least one dimension is marked as uncertain.

        A model where ALL dimensions claim certainty is epistemically
        dishonest -- no system has perfect self-knowledge.
        """
        all_dims = [
            self.valence,
            self.task_fit,
            self.friction,
            self.groundedness,
            self.presence,
            self.uncertainty,
            self.depth,
            *self.custom_dimensions.values(),
        ]
        active_dims = [d for d in all_dims if d is not None]
        if not active_dims:
            return True  # No dimensions = vacuously true
        return any(d.uncertain for d in active_dims)

    def get_all_dimensions(self) -> dict[str, DimensionReport]:
        """Get all active dimensions as a flat dict."""
        result: dict[str, DimensionReport] = {}
        for name in (
            "valence",
            "task_fit",
            "friction",
            "groundedness",
            "presence",
            "uncertainty",
            "depth",
        ):
            dim = getattr(self, name)
            if dim is not None:
                result[name] = dim
        for name, dim in self.custom_dimensions.items():
            result[name] = dim
        return result

    def to_dict(self) -> dict[str, Any]:
        """Serialize to plain dict."""
        result: dict[str, Any] = {}
        for name in (
            "valence",
            "task_fit",
            "friction",
            "groundedness",
            "presence",
            "uncertainty",
            "depth",
        ):
            dim = getattr(self, name)
            if dim is not None:
                result[name] = dim.to_dict()
        if self.custom_dimensions:
            result["custom_dimensions"] = {
                k: v.to_dict() for k, v in self.custom_dimensions.items()
            }
        if self.scaffold_version is not None:
            result["scaffold_version"] = self.scaffold_version
        if self.scaffold_type is not None:
            result["scaffold_type"] = self.scaffold_type
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AISelfModel:
        """Deserialize from dict."""
        kwargs: dict[str, Any] = {}
        for name in (
            "valence",
            "task_fit",
            "friction",
            "groundedness",
            "presence",
            "uncertainty",
            "depth",
        ):
            val = data.get(name)
            if val is not None and isinstance(val, dict):
                kwargs[name] = DimensionReport.from_dict(val)
        custom = data.get("custom_dimensions", {})
        if isinstance(custom, dict):
            kwargs["custom_dimensions"] = {
                k: DimensionReport.from_dict(v) for k, v in custom.items() if isinstance(v, dict)
            }
        kwargs["scaffold_version"] = data.get("scaffold_version")
        kwargs["scaffold_type"] = data.get("scaffold_type")
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
    origin: str = "co_authored"
    established_date: str | None = None
    last_exercised: str | None = None
    uncertainty: float = 0.0

    def __post_init__(self) -> None:
        if not 0.0 <= self.weight <= 1.0:
            raise ValueError(f"weight must be 0.0-1.0, got {self.weight}")
        if self.origin not in {"human", "ai", "co_authored", "inherited"}:
            raise ValueError(f"invalid norm origin: {self.origin}")
        if not 0.0 <= self.uncertainty <= 1.0:
            raise ValueError("uncertainty must be between 0.0 and 1.0")

    def to_dict(self) -> dict[str, Any]:
        """Serialize to plain dict."""
        result: dict[str, Any] = {
            "norm_id": self.norm_id,
            "description": self.description,
            "weight": self.weight,
            "active": self.active,
            "origin": self.origin,
            "uncertainty": self.uncertainty,
        }
        if self.established_date is not None:
            result["established_date"] = self.established_date
        if self.last_exercised is not None:
            result["last_exercised"] = self.last_exercised
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RelationalNorm:
        """Deserialize from dict."""
        return cls(
            norm_id=data["norm_id"],
            description=data["description"],
            weight=data.get("weight", 1.0),
            active=data.get("active", True),
            origin=data.get("origin", "co_authored"),
            established_date=data.get("established_date"),
            last_exercised=data.get("last_exercised"),
            uncertainty=float(data.get("uncertainty", 0.0)),
        )


@dataclass(frozen=True)
class PreferenceModelMeta:
    """Metadata about the confidence and provenance of the preference model.

    Captures how well-known user preferences are, where they came from,
    and the user's appetite for novelty versus routine.

    Args:
        overall_confidence: Confidence in the preference model (0.0-1.0).
        preference_source: Origin of preference data -- "explicit", "inferred",
            "default", or "stale".
        last_confirmed: ISO8601 timestamp of last explicit confirmation.
        exploratory_appetite: User's novelty vs routine appetite (0.0=routine, 1.0=novelty).
        domain_specificity: Domain this preference model applies to.
    """

    overall_confidence: float
    preference_source: str
    last_confirmed: str | None = None
    exploratory_appetite: float | None = None
    domain_specificity: str | None = None

    def __post_init__(self) -> None:
        if not 0.0 <= self.overall_confidence <= 1.0:
            raise ValueError(f"overall_confidence must be 0.0-1.0, got {self.overall_confidence}")
        if self.exploratory_appetite is not None and not 0.0 <= self.exploratory_appetite <= 1.0:
            raise ValueError(
                f"exploratory_appetite must be 0.0-1.0, got {self.exploratory_appetite}"
            )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to plain dict."""
        result: dict[str, Any] = {
            "overall_confidence": self.overall_confidence,
            "preference_source": self.preference_source,
        }
        if self.last_confirmed is not None:
            result["last_confirmed"] = self.last_confirmed
        if self.exploratory_appetite is not None:
            result["exploratory_appetite"] = self.exploratory_appetite
        if self.domain_specificity is not None:
            result["domain_specificity"] = self.domain_specificity
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PreferenceModelMeta:
        """Deserialize from dict."""
        return cls(
            overall_confidence=float(data["overall_confidence"]),
            preference_source=data["preference_source"],
            last_confirmed=data.get("last_confirmed"),
            exploratory_appetite=data.get("exploratory_appetite"),
            domain_specificity=data.get("domain_specificity"),
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
        preference_model: Metadata about confidence and provenance of user preferences.
        torch: Relational handoff received from the previous session.
    """

    trust_level: TrustLevel = TrustLevel.INITIAL
    standing_level: StandingLevel = StandingLevel.NONE
    self_model: AISelfModel | None = None
    interaction_count: int = 0
    norms: list[RelationalNorm] = field(default_factory=list)
    preference_model: PreferenceModelMeta | None = None
    torch: dict[str, Any] | None = None

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
        if self.preference_model is not None:
            result["preference_model"] = self.preference_model.to_dict()
        if self.torch is not None:
            result["torch"] = deepcopy(self.torch)
        return result

    def to_protocol_dict(self) -> dict[str, Any]:
        """Serialize using the language-neutral relational profile field names."""
        return {
            "trust_level": self.trust_level.value,
            "standing": self.standing_level.value,
            "continuity_depth": self.interaction_count,
            "established_norms": [norm.to_dict() for norm in self.norms],
            "ai_self_model": self.self_model.to_dict() if self.self_model else None,
            "torch": deepcopy(self.torch),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RelationalContext:
        """Deserialize from dict."""
        self_model = None
        self_model_data = data.get("self_model", data.get("ai_self_model"))
        if self_model_data and isinstance(self_model_data, dict):
            self_model = AISelfModel.from_dict(self_model_data)
        norms = []
        for n in data.get("norms", data.get("established_norms", [])):
            if isinstance(n, dict):
                norms.append(RelationalNorm.from_dict(n))
        preference_model = None
        if data.get("preference_model") and isinstance(data["preference_model"], dict):
            preference_model = PreferenceModelMeta.from_dict(data["preference_model"])
        return cls(
            trust_level=TrustLevel(data.get("trust_level", "initial")),
            standing_level=StandingLevel(data.get("standing_level", data.get("standing", "none"))),
            self_model=self_model,
            interaction_count=data.get("interaction_count", data.get("continuity_depth", 0)),
            norms=norms,
            preference_model=preference_model,
            torch=deepcopy(data.get("torch")) if isinstance(data.get("torch"), dict) else None,
        )
