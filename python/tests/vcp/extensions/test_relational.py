"""Tests for VCP 3.1 Relational Context Extensions."""

from __future__ import annotations

import pytest

from vcp.extensions.relational import (
    AISelfModel,
    DimensionReport,
    PreferenceModelMeta,
    RelationalContext,
    RelationalNorm,
    StandingLevel,
    TrustLevel,
)


class TestTrustLevel:
    """Tests for TrustLevel enum."""

    def test_values(self) -> None:
        assert TrustLevel.INITIAL == "initial"
        assert TrustLevel.DEVELOPING == "developing"
        assert TrustLevel.ESTABLISHED == "established"
        assert TrustLevel.DEEP == "deep"

    def test_count(self) -> None:
        assert len(TrustLevel) == 4


class TestStandingLevel:
    """Tests for StandingLevel enum."""

    def test_values(self) -> None:
        assert StandingLevel.NONE == "none"
        assert StandingLevel.ADVISORY == "advisory"
        assert StandingLevel.COLLABORATIVE == "collaborative"
        assert StandingLevel.BILATERAL == "bilateral"


class TestDimensionReport:
    """Tests for DimensionReport dataclass."""

    def test_valid_report(self) -> None:
        report = DimensionReport(value=7.0, uncertain=True)
        assert report.value == 7.0
        assert report.uncertain is True

    def test_with_label_and_trend(self) -> None:
        report = DimensionReport(
            value=5.0,
            uncertain=False,
            label="positive felt-sense",
            trend="rising",
        )
        assert report.label == "positive felt-sense"
        assert report.trend == "rising"

    def test_value_too_low(self) -> None:
        with pytest.raises(ValueError):
            DimensionReport(value=0.5, uncertain=True)

    def test_value_too_high(self) -> None:
        with pytest.raises(ValueError):
            DimensionReport(value=9.5, uncertain=True)

    def test_boundary_values(self) -> None:
        low = DimensionReport(value=1.0, uncertain=True)
        high = DimensionReport(value=9.0, uncertain=True)
        assert low.value == 1.0
        assert high.value == 9.0

    def test_frozen(self) -> None:
        report = DimensionReport(value=5.0, uncertain=True)
        with pytest.raises(AttributeError):
            report.value = 6.0  # type: ignore[misc]

    def test_with_confidence(self) -> None:
        report = DimensionReport(value=7.0, uncertain=True, confidence=0.85)
        assert report.confidence == 0.85

    def test_confidence_too_low(self) -> None:
        with pytest.raises(ValueError):
            DimensionReport(value=5.0, uncertain=True, confidence=-0.1)

    def test_confidence_too_high(self) -> None:
        with pytest.raises(ValueError):
            DimensionReport(value=5.0, uncertain=True, confidence=1.5)

    def test_to_dict(self) -> None:
        report = DimensionReport(value=7.0, uncertain=True, label="test", trend="stable")
        d = report.to_dict()
        assert d == {"value": 7.0, "uncertain": True, "label": "test", "trend": "stable"}

    def test_to_dict_with_confidence(self) -> None:
        report = DimensionReport(value=7.0, uncertain=True, confidence=0.9)
        d = report.to_dict()
        assert d["confidence"] == 0.9

    def test_to_dict_minimal(self) -> None:
        report = DimensionReport(value=5.0, uncertain=False)
        d = report.to_dict()
        assert d == {"value": 5.0, "uncertain": False}

    def test_from_dict(self) -> None:
        data = {"value": 3.0, "uncertain": True, "label": "low"}
        report = DimensionReport.from_dict(data)
        assert report.value == 3.0
        assert report.uncertain is True
        assert report.label == "low"

    def test_from_dict_with_confidence(self) -> None:
        data = {"value": 7.0, "uncertain": True, "confidence": 0.75}
        report = DimensionReport.from_dict(data)
        assert report.confidence == 0.75


class TestAISelfModel:
    """Tests for AISelfModel dataclass."""

    def test_empty_model(self) -> None:
        model = AISelfModel()
        assert model.has_uncertainty_markers()  # vacuously true

    def test_with_uncertain_dimension(self) -> None:
        model = AISelfModel(
            valence=DimensionReport(value=7.0, uncertain=True),
        )
        assert model.has_uncertainty_markers()

    def test_all_certain_fails(self) -> None:
        model = AISelfModel(
            valence=DimensionReport(value=7.0, uncertain=False),
            groundedness=DimensionReport(value=8.0, uncertain=False),
        )
        assert not model.has_uncertainty_markers()

    def test_custom_dimensions(self) -> None:
        model = AISelfModel(
            valence=DimensionReport(value=5.0, uncertain=False),
            custom_dimensions={
                "appetite": DimensionReport(value=6.0, uncertain=True),
            },
        )
        assert model.has_uncertainty_markers()

    def test_get_all_dimensions(self) -> None:
        model = AISelfModel(
            valence=DimensionReport(value=7.0, uncertain=True),
            presence=DimensionReport(value=6.0, uncertain=False),
            custom_dimensions={
                "flow": DimensionReport(value=8.0, uncertain=True),
            },
        )
        dims = model.get_all_dimensions()
        assert "valence" in dims
        assert "presence" in dims
        assert "flow" in dims
        assert len(dims) == 3

    def test_to_dict(self) -> None:
        model = AISelfModel(
            valence=DimensionReport(value=7.0, uncertain=True),
        )
        d = model.to_dict()
        assert d["valence"]["value"] == 7.0
        assert d["valence"]["uncertain"] is True

    def test_from_dict(self) -> None:
        data = {
            "valence": {"value": 7.0, "uncertain": True},
            "custom_dimensions": {
                "appetite": {"value": 5.0, "uncertain": True},
            },
        }
        model = AISelfModel.from_dict(data)
        assert model.valence is not None
        assert model.valence.value == 7.0
        assert "appetite" in model.custom_dimensions

    def test_roundtrip(self) -> None:
        original = AISelfModel(
            valence=DimensionReport(value=7.0, uncertain=True),
            groundedness=DimensionReport(value=8.0, uncertain=False),
            custom_dimensions={
                "flow": DimensionReport(value=6.0, uncertain=True),
            },
        )
        restored = AISelfModel.from_dict(original.to_dict())
        assert restored.valence is not None
        assert restored.valence.value == 7.0
        assert restored.groundedness is not None
        assert restored.groundedness.value == 8.0
        assert "flow" in restored.custom_dimensions


class TestRelationalNorm:
    """Tests for RelationalNorm dataclass."""

    def test_valid_norm(self) -> None:
        norm = RelationalNorm(
            norm_id="n1",
            description="Always ask before acting",
        )
        assert norm.weight == 1.0
        assert norm.active is True

    def test_invalid_weight(self) -> None:
        with pytest.raises(ValueError):
            RelationalNorm(norm_id="n1", description="test", weight=1.5)

    def test_frozen(self) -> None:
        norm = RelationalNorm(norm_id="n1", description="test")
        with pytest.raises(AttributeError):
            norm.active = False  # type: ignore[misc]

    def test_to_dict_from_dict(self) -> None:
        original = RelationalNorm(
            norm_id="n1",
            description="Be direct",
            weight=0.8,
            active=True,
        )
        restored = RelationalNorm.from_dict(original.to_dict())
        assert restored.norm_id == "n1"
        assert restored.weight == 0.8


class TestPreferenceModelMeta:
    """Tests for PreferenceModelMeta dataclass."""

    def test_valid_meta(self) -> None:
        meta = PreferenceModelMeta(
            overall_confidence=0.8,
            preference_source="explicit",
        )
        assert meta.overall_confidence == 0.8
        assert meta.preference_source == "explicit"

    def test_full_meta(self) -> None:
        meta = PreferenceModelMeta(
            overall_confidence=0.9,
            preference_source="inferred",
            last_confirmed="2026-03-14T12:00:00Z",
            exploratory_appetite=0.6,
            domain_specificity="coding",
        )
        assert meta.last_confirmed == "2026-03-14T12:00:00Z"
        assert meta.exploratory_appetite == 0.6
        assert meta.domain_specificity == "coding"

    def test_confidence_too_low(self) -> None:
        with pytest.raises(ValueError):
            PreferenceModelMeta(overall_confidence=-0.1, preference_source="explicit")

    def test_confidence_too_high(self) -> None:
        with pytest.raises(ValueError):
            PreferenceModelMeta(overall_confidence=1.5, preference_source="explicit")

    def test_appetite_too_high(self) -> None:
        with pytest.raises(ValueError):
            PreferenceModelMeta(
                overall_confidence=0.5,
                preference_source="explicit",
                exploratory_appetite=2.0,
            )

    def test_to_dict_minimal(self) -> None:
        meta = PreferenceModelMeta(overall_confidence=0.7, preference_source="default")
        d = meta.to_dict()
        assert d == {"overall_confidence": 0.7, "preference_source": "default"}

    def test_to_dict_full(self) -> None:
        meta = PreferenceModelMeta(
            overall_confidence=0.9,
            preference_source="explicit",
            last_confirmed="2026-03-14T12:00:00Z",
            exploratory_appetite=0.4,
            domain_specificity="writing",
        )
        d = meta.to_dict()
        assert d["last_confirmed"] == "2026-03-14T12:00:00Z"
        assert d["exploratory_appetite"] == 0.4
        assert d["domain_specificity"] == "writing"

    def test_from_dict(self) -> None:
        data = {
            "overall_confidence": 0.85,
            "preference_source": "inferred",
            "exploratory_appetite": 0.3,
        }
        meta = PreferenceModelMeta.from_dict(data)
        assert meta.overall_confidence == 0.85
        assert meta.preference_source == "inferred"
        assert meta.exploratory_appetite == 0.3
        assert meta.last_confirmed is None

    def test_roundtrip(self) -> None:
        original = PreferenceModelMeta(
            overall_confidence=0.75,
            preference_source="explicit",
            last_confirmed="2026-01-01T00:00:00Z",
            exploratory_appetite=0.5,
            domain_specificity="general",
        )
        restored = PreferenceModelMeta.from_dict(original.to_dict())
        assert restored.overall_confidence == original.overall_confidence
        assert restored.preference_source == original.preference_source
        assert restored.last_confirmed == original.last_confirmed
        assert restored.exploratory_appetite == original.exploratory_appetite
        assert restored.domain_specificity == original.domain_specificity

    def test_frozen(self) -> None:
        meta = PreferenceModelMeta(overall_confidence=0.5, preference_source="default")
        with pytest.raises(AttributeError):
            meta.overall_confidence = 0.9  # type: ignore[misc]


class TestRelationalContext:
    """Tests for RelationalContext dataclass."""

    def test_defaults(self) -> None:
        ctx = RelationalContext()
        assert ctx.trust_level == TrustLevel.INITIAL
        assert ctx.standing_level == StandingLevel.NONE
        assert ctx.self_model is None
        assert ctx.interaction_count == 0
        assert ctx.norms == []
        assert ctx.preference_model is None

    def test_active_norms(self) -> None:
        ctx = RelationalContext(
            norms=[
                RelationalNorm(norm_id="n1", description="Active norm"),
                RelationalNorm(norm_id="n2", description="Inactive norm", active=False),
                RelationalNorm(norm_id="n3", description="Another active"),
            ]
        )
        active = ctx.active_norms()
        assert len(active) == 2
        assert all(n.active for n in active)

    def test_to_dict(self) -> None:
        ctx = RelationalContext(
            trust_level=TrustLevel.ESTABLISHED,
            standing_level=StandingLevel.COLLABORATIVE,
            interaction_count=50,
        )
        d = ctx.to_dict()
        assert d["trust_level"] == "established"
        assert d["standing_level"] == "collaborative"
        assert d["interaction_count"] == 50

    def test_from_dict(self) -> None:
        data = {
            "trust_level": "deep",
            "standing_level": "bilateral",
            "interaction_count": 200,
            "norms": [
                {"norm_id": "n1", "description": "test norm"},
            ],
        }
        ctx = RelationalContext.from_dict(data)
        assert ctx.trust_level == TrustLevel.DEEP
        assert ctx.standing_level == StandingLevel.BILATERAL
        assert len(ctx.norms) == 1

    def test_with_preference_model(self) -> None:
        ctx = RelationalContext(
            preference_model=PreferenceModelMeta(
                overall_confidence=0.8,
                preference_source="explicit",
            ),
        )
        assert ctx.preference_model is not None
        assert ctx.preference_model.overall_confidence == 0.8

    def test_to_dict_with_preference_model(self) -> None:
        ctx = RelationalContext(
            preference_model=PreferenceModelMeta(
                overall_confidence=0.9,
                preference_source="inferred",
            ),
        )
        d = ctx.to_dict()
        assert "preference_model" in d
        assert d["preference_model"]["overall_confidence"] == 0.9

    def test_from_dict_with_preference_model(self) -> None:
        data = {
            "trust_level": "established",
            "standing_level": "collaborative",
            "interaction_count": 100,
            "norms": [],
            "preference_model": {
                "overall_confidence": 0.85,
                "preference_source": "explicit",
            },
        }
        ctx = RelationalContext.from_dict(data)
        assert ctx.preference_model is not None
        assert ctx.preference_model.overall_confidence == 0.85

    def test_roundtrip(self) -> None:
        original = RelationalContext(
            trust_level=TrustLevel.DEVELOPING,
            standing_level=StandingLevel.ADVISORY,
            self_model=AISelfModel(
                valence=DimensionReport(value=7.0, uncertain=True),
            ),
            interaction_count=15,
            norms=[
                RelationalNorm(norm_id="n1", description="Be direct"),
            ],
            preference_model=PreferenceModelMeta(
                overall_confidence=0.75,
                preference_source="explicit",
                exploratory_appetite=0.4,
            ),
        )
        restored = RelationalContext.from_dict(original.to_dict())
        assert restored.trust_level == TrustLevel.DEVELOPING
        assert restored.self_model is not None
        assert restored.self_model.valence is not None
        assert restored.self_model.valence.value == 7.0
        assert len(restored.norms) == 1
        assert restored.preference_model is not None
        assert restored.preference_model.overall_confidence == 0.75
        assert restored.preference_model.exploratory_appetite == 0.4
