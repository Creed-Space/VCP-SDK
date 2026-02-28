"""Tests for VCP 3.1 Personal Context Extensions."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from vcp.extensions.personal import (
    ALL_VALID_CATEGORIES,
    DECAY_CONFIGS,
    DecayConfig,
    LifecycleState,
    PersonalContext,
    PersonalDimension,
    PersonalSignal,
    compute_decayed_intensity,
)


class TestPersonalDimension:
    """Tests for PersonalDimension enum."""

    def test_all_five_dimensions(self) -> None:
        assert len(PersonalDimension) == 5
        assert PersonalDimension.COGNITIVE_STATE == "cognitive_state"
        assert PersonalDimension.EMOTIONAL_TONE == "emotional_tone"
        assert PersonalDimension.ENERGY_LEVEL == "energy_level"
        assert PersonalDimension.PERCEIVED_URGENCY == "perceived_urgency"
        assert PersonalDimension.BODY_SIGNALS == "body_signals"


class TestPersonalSignal:
    """Tests for PersonalSignal dataclass."""

    def test_valid_signal(self) -> None:
        signal = PersonalSignal(category="focused", intensity=4)
        assert signal.category == "focused"
        assert signal.intensity == 4
        assert signal.source == "declared"
        assert signal.confidence == 1.0
        assert signal.declared_at is None

    def test_default_intensity(self) -> None:
        signal = PersonalSignal(category="calm")
        assert signal.intensity == 3

    def test_invalid_category(self) -> None:
        with pytest.raises(ValueError, match="Invalid category"):
            PersonalSignal(category="invalid_category")

    def test_intensity_too_low(self) -> None:
        with pytest.raises(ValueError, match="Intensity must be 1-5"):
            PersonalSignal(category="focused", intensity=0)

    def test_intensity_too_high(self) -> None:
        with pytest.raises(ValueError, match="Intensity must be 1-5"):
            PersonalSignal(category="focused", intensity=6)

    def test_invalid_confidence(self) -> None:
        with pytest.raises(ValueError, match="Confidence must be 0.0-1.0"):
            PersonalSignal(category="focused", confidence=1.5)

    def test_to_dict(self) -> None:
        signal = PersonalSignal(
            category="tense",
            intensity=4,
            source="inferred",
            confidence=0.8,
            declared_at="2025-01-01T00:00:00Z",
        )
        d = signal.to_dict()
        assert d["category"] == "tense"
        assert d["intensity"] == 4
        assert d["source"] == "inferred"
        assert d["confidence"] == 0.8
        assert d["declared_at"] == "2025-01-01T00:00:00Z"

    def test_to_dict_no_declared_at(self) -> None:
        signal = PersonalSignal(category="calm")
        d = signal.to_dict()
        assert "declared_at" not in d

    def test_from_dict(self) -> None:
        data = {"category": "rested", "intensity": 5, "source": "preset"}
        signal = PersonalSignal.from_dict(data)
        assert signal.category == "rested"
        assert signal.intensity == 5
        assert signal.source == "preset"

    def test_from_dict_defaults(self) -> None:
        signal = PersonalSignal.from_dict({"category": "neutral"})
        assert signal.intensity == 3
        assert signal.source == "declared"
        assert signal.confidence == 1.0

    def test_all_valid_categories_covered(self) -> None:
        # Every category in every dimension should be in ALL_VALID_CATEGORIES
        for cat in ALL_VALID_CATEGORIES:
            signal = PersonalSignal(category=cat)
            assert signal.category == cat


class TestPersonalContext:
    """Tests for PersonalContext dataclass."""

    def test_empty_context(self) -> None:
        ctx = PersonalContext()
        assert not ctx.has_any_signal()

    def test_single_signal(self) -> None:
        ctx = PersonalContext(cognitive_state=PersonalSignal(category="focused", intensity=5))
        assert ctx.has_any_signal()

    def test_all_signals(self) -> None:
        ctx = PersonalContext(
            cognitive_state=PersonalSignal(category="focused"),
            emotional_tone=PersonalSignal(category="calm"),
            energy_level=PersonalSignal(category="rested"),
            perceived_urgency=PersonalSignal(category="unhurried"),
            body_signals=PersonalSignal(category="neutral"),
        )
        assert ctx.has_any_signal()

    def test_to_dict(self) -> None:
        ctx = PersonalContext(
            cognitive_state=PersonalSignal(category="foggy", intensity=2),
        )
        d = ctx.to_dict()
        assert d["cognitive_state"]["category"] == "foggy"
        assert d["emotional_tone"] is None

    def test_from_dict(self) -> None:
        data = {
            "cognitive_state": {"category": "focused", "intensity": 4},
            "energy_level": {"category": "fatigued", "intensity": 3},
        }
        ctx = PersonalContext.from_dict(data)
        assert ctx.cognitive_state is not None
        assert ctx.cognitive_state.category == "focused"
        assert ctx.energy_level is not None
        assert ctx.energy_level.category == "fatigued"
        assert ctx.emotional_tone is None

    def test_roundtrip(self) -> None:
        original = PersonalContext(
            cognitive_state=PersonalSignal(category="reflective", intensity=2),
            body_signals=PersonalSignal(category="discomfort", intensity=4),
        )
        restored = PersonalContext.from_dict(original.to_dict())
        assert restored.cognitive_state is not None
        assert restored.cognitive_state.category == "reflective"
        assert restored.body_signals is not None
        assert restored.body_signals.intensity == 4
        assert restored.emotional_tone is None


class TestDecayConfig:
    """Tests for DecayConfig and DECAY_CONFIGS."""

    def test_defaults(self) -> None:
        cfg = DecayConfig(half_life_seconds=600.0)
        assert cfg.baseline == 1
        assert cfg.pinned is False
        assert cfg.reset_on_engagement is False

    def test_all_dimensions_have_configs(self) -> None:
        for dim in PersonalDimension:
            assert dim.value in DECAY_CONFIGS

    def test_urgency_config(self) -> None:
        cfg = DECAY_CONFIGS["perceived_urgency"]
        assert cfg.half_life_seconds == 900.0
        assert cfg.reset_on_engagement is False

    def test_cognitive_config(self) -> None:
        cfg = DECAY_CONFIGS["cognitive_state"]
        assert cfg.reset_on_engagement is True


class TestComputeDecayedIntensity:
    """Tests for compute_decayed_intensity function."""

    def test_no_decay_at_t0(self) -> None:
        now = datetime.now(timezone.utc)
        config = DecayConfig(half_life_seconds=600.0)
        result = compute_decayed_intensity(5, now, config, now)
        assert result == 5

    def test_decay_at_half_life(self) -> None:
        now = datetime.now(timezone.utc)
        declared_at = now - timedelta(seconds=600)
        config = DecayConfig(half_life_seconds=600.0, baseline=1)
        result = compute_decayed_intensity(5, declared_at, config, now)
        # After 1 half-life: 1 + (5-1) * 0.5 = 3.0 -> floor = 3
        assert result == 3

    def test_decay_at_two_half_lives(self) -> None:
        now = datetime.now(timezone.utc)
        declared_at = now - timedelta(seconds=1200)
        config = DecayConfig(half_life_seconds=600.0, baseline=1)
        result = compute_decayed_intensity(5, declared_at, config, now)
        # After 2 half-lives: 1 + (5-1) * 0.25 = 2.0 -> floor = 2
        assert result == 2

    def test_never_below_baseline(self) -> None:
        now = datetime.now(timezone.utc)
        declared_at = now - timedelta(hours=24)
        config = DecayConfig(half_life_seconds=600.0, baseline=1)
        result = compute_decayed_intensity(5, declared_at, config, now)
        assert result >= 1

    def test_pinned_no_decay(self) -> None:
        now = datetime.now(timezone.utc)
        declared_at = now - timedelta(hours=24)
        config = DecayConfig(half_life_seconds=600.0, pinned=True)
        result = compute_decayed_intensity(5, declared_at, config, now)
        assert result == 5

    def test_negative_elapsed(self) -> None:
        now = datetime.now(timezone.utc)
        declared_at = now + timedelta(seconds=100)  # future
        config = DecayConfig(half_life_seconds=600.0)
        result = compute_decayed_intensity(5, declared_at, config, now)
        assert result == 5

    def test_naive_datetime_treated_as_utc(self) -> None:
        now = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        declared_at = datetime(2025, 1, 1, 11, 50, 0)  # naive
        config = DecayConfig(half_life_seconds=600.0, baseline=1)
        result = compute_decayed_intensity(5, declared_at, config, now)
        # 10 minutes = 600 seconds = 1 half-life -> expect 3
        assert result == 3

    def test_baseline_intensity_stays_at_baseline(self) -> None:
        now = datetime.now(timezone.utc)
        declared_at = now - timedelta(seconds=300)
        config = DecayConfig(half_life_seconds=600.0, baseline=1)
        result = compute_decayed_intensity(1, declared_at, config, now)
        assert result == 1


class TestLifecycleState:
    """Tests for LifecycleState enum."""

    def test_all_states(self) -> None:
        assert len(LifecycleState) == 5
        assert LifecycleState.SET == "set"
        assert LifecycleState.ACTIVE == "active"
        assert LifecycleState.DECAYING == "decaying"
        assert LifecycleState.STALE == "stale"
        assert LifecycleState.EXPIRED == "expired"
