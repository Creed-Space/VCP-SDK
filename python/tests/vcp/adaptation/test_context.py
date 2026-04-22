"""Tests for VCP/A Context Encoder (VCP v3.2 / VEP-0004)."""

import pytest

from vcp.adaptation import (
    ContextEncoder,
    Dimension,
    PersonalStateDimension,
    PersonalState,
    SituationalDimension,
    VCPContext,
)


# ────────────────────────────────────────────────────────────────────────────
# SituationalDimension
# ────────────────────────────────────────────────────────────────────────────

class TestSituationalDimension:
    """Test SituationalDimension enum."""

    def test_all_dimensions_have_symbol(self):
        for dim in SituationalDimension:
            assert dim.symbol
            assert isinstance(dim.symbol, str)

    def test_positions_are_unique_1_through_13(self):
        """v3.2 defines 13 situational dimensions with unique positions 1-13."""
        positions = [dim.position for dim in SituationalDimension]
        assert sorted(positions) == list(range(1, 14))

    def test_vep_0004_dims_are_10_through_13(self):
        expected = {
            SituationalDimension.EMBODIMENT,
            SituationalDimension.PROXIMITY,
            SituationalDimension.RELATIONSHIP,
            SituationalDimension.FORMALITY,
        }
        vep = {d for d in SituationalDimension if d.is_vep_0004}
        assert vep == expected
        assert all(10 <= d.position <= 13 for d in vep)

    def test_system_context_is_position_9(self):
        """SYSTEM_CONTEXT replaces the deprecated STATE at position 9."""
        assert SituationalDimension.SYSTEM_CONTEXT.position == 9

    def test_state_is_removed(self):
        """STATE was removed in v3.1 — it must not exist as a SituationalDimension."""
        names = {d.name for d in SituationalDimension}
        assert "STATE" not in names

    def test_relationship_is_free_form(self):
        assert SituationalDimension.RELATIONSHIP.is_free_form
        assert not SituationalDimension.TIME.is_free_form

    def test_culture_values_are_communication_styles(self):
        """CULTURE must encode communication styles, not nationalities (per CSM1 v3.2)."""
        names = set(SituationalDimension.CULTURE.values.values())
        # Any nationality leak is a regression.
        forbidden = {"american", "european", "japanese", "global"}
        assert not (names & forbidden)
        # Must include at least the core communication styles.
        assert {"high_context", "low_context", "formal"} <= names

    def test_from_name(self):
        assert SituationalDimension.from_name("time") == SituationalDimension.TIME
        assert SituationalDimension.from_name("TIME") == SituationalDimension.TIME
        assert (
            SituationalDimension.from_name("system_context")
            == SituationalDimension.SYSTEM_CONTEXT
        )
        assert SituationalDimension.from_name("embodiment") == SituationalDimension.EMBODIMENT

    def test_from_name_invalid(self):
        with pytest.raises(ValueError, match="Unknown situational dimension"):
            SituationalDimension.from_name("invalid")


class TestDimensionAlias:
    """`Dimension` stays around as a backwards-compat alias."""

    def test_dimension_is_situational_alias(self):
        assert Dimension is SituationalDimension

    def test_dimension_state_attribute_gone(self):
        """The deprecated STATE dim must not resurface under the alias."""
        assert not hasattr(Dimension, "STATE")


# ────────────────────────────────────────────────────────────────────────────
# PersonalStateDimension
# ────────────────────────────────────────────────────────────────────────────

class TestPersonalDimension:
    """Test PersonalStateDimension enum (R-line)."""

    def test_five_personal_dimensions(self):
        assert len(list(PersonalStateDimension)) == 5

    def test_positions_are_unique_1_through_5(self):
        positions = [dim.position for dim in PersonalStateDimension]
        assert sorted(positions) == [1, 2, 3, 4, 5]

    def test_all_have_symbol(self):
        for dim in PersonalStateDimension:
            assert dim.symbol

    def test_from_symbol(self):
        assert PersonalStateDimension.from_symbol("🧠") == PersonalStateDimension.COGNITIVE_STATE
        assert PersonalStateDimension.from_symbol("🩺") == PersonalStateDimension.BODY_SIGNALS
        assert PersonalStateDimension.from_symbol("not-a-symbol") is None


class TestPersonalState:
    """Test PersonalState value type."""

    def test_bare_value(self):
        ps = PersonalState(value="focused")
        assert ps.value == "focused"
        assert ps.intensity is None
        assert ps.encode() == "focused"

    def test_with_intensity(self):
        ps = PersonalState(value="calm", intensity=5)
        assert ps.encode() == "calm:5"

    def test_intensity_must_be_1_through_5(self):
        with pytest.raises(ValueError):
            PersonalState(value="x", intensity=0)
        with pytest.raises(ValueError):
            PersonalState(value="x", intensity=6)

    def test_decode_with_intensity(self):
        assert PersonalState.decode("focused:4") == PersonalState("focused", 4)

    def test_decode_without_intensity(self):
        assert PersonalState.decode("calm") == PersonalState("calm")


# ────────────────────────────────────────────────────────────────────────────
# VCPContext basic shape
# ────────────────────────────────────────────────────────────────────────────

class TestVCPContext:
    """Test VCPContext class."""

    def test_empty_context(self):
        ctx = VCPContext()
        assert not ctx
        assert ctx.encode() == ""

    def test_single_dimension(self):
        ctx = VCPContext(situational={SituationalDimension.TIME: ["🌅"]})
        assert ctx
        assert ctx.has(SituationalDimension.TIME)
        assert not ctx.has(SituationalDimension.SPACE)

    def test_multiple_dimensions(self):
        ctx = VCPContext(
            situational={
                SituationalDimension.TIME: ["🌅"],
                SituationalDimension.SPACE: ["🏡"],
                SituationalDimension.COMPANY: ["👶", "👨‍👩‍👧"],
            }
        )
        assert ctx.get(SituationalDimension.TIME) == ["🌅"]
        assert ctx.get(SituationalDimension.COMPANY) == ["👶", "👨‍👩‍👧"]

    def test_get_missing_dimension(self):
        ctx = VCPContext()
        assert ctx.get(SituationalDimension.TIME) == []

    def test_set_returns_new_context(self):
        ctx1 = VCPContext()
        ctx2 = ctx1.set(SituationalDimension.TIME, ["🌅"])
        assert ctx1.get(SituationalDimension.TIME) == []
        assert ctx2.get(SituationalDimension.TIME) == ["🌅"]

    def test_set_personal_returns_new_context(self):
        ctx1 = VCPContext()
        ctx2 = ctx1.set_personal(PersonalStateDimension.COGNITIVE_STATE, "focused", 4)
        assert ctx1.get_personal(PersonalStateDimension.COGNITIVE_STATE) is None
        ps = ctx2.get_personal(PersonalStateDimension.COGNITIVE_STATE)
        assert ps == PersonalState("focused", 4)

    def test_has_personal(self):
        ctx = VCPContext(
            personal={PersonalStateDimension.EMOTIONAL_TONE: PersonalState("calm", 5)}
        )
        assert ctx.has(PersonalStateDimension.EMOTIONAL_TONE)
        assert not ctx.has(PersonalStateDimension.ENERGY_LEVEL)

    def test_dimensions_backcompat_alias(self):
        """ctx.dimensions is a compatibility alias for ctx.situational."""
        ctx = VCPContext(situational={SituationalDimension.TIME: ["🌅"]})
        assert ctx.dimensions is ctx.situational

    def test_equality(self):
        ctx1 = VCPContext(situational={SituationalDimension.TIME: ["🌅"]})
        ctx2 = VCPContext(situational={SituationalDimension.TIME: ["🌅"]})
        ctx3 = VCPContext(situational={SituationalDimension.TIME: ["🌙"]})
        assert ctx1 == ctx2
        assert ctx1 != ctx3

    def test_equality_considers_personal_band(self):
        ctx1 = VCPContext(
            situational={SituationalDimension.TIME: ["🌅"]},
            personal={PersonalStateDimension.COGNITIVE_STATE: PersonalState("focused", 4)},
        )
        ctx2 = VCPContext(
            situational={SituationalDimension.TIME: ["🌅"]},
            personal={PersonalStateDimension.COGNITIVE_STATE: PersonalState("focused", 3)},
        )
        assert ctx1 != ctx2

    def test_equality_not_implemented(self):
        ctx = VCPContext()
        assert ctx != "not a context"


# ────────────────────────────────────────────────────────────────────────────
# Wire format
# ────────────────────────────────────────────────────────────────────────────

class TestVCPContextEncoding:
    """Test VCPContext wire format encoding."""

    def test_encode_single_situational(self):
        ctx = VCPContext(situational={SituationalDimension.TIME: ["🌅"]})
        assert ctx.encode() == "⏰🌅"

    def test_encode_multiple_situational(self):
        ctx = VCPContext(
            situational={
                SituationalDimension.TIME: ["🌅"],
                SituationalDimension.SPACE: ["🏡"],
            }
        )
        encoded = ctx.encode()
        assert "⏰🌅" in encoded
        assert "📍🏡" in encoded
        assert "|" in encoded

    def test_encode_personal_separator_is_u2016(self):
        """Personal-state band is separated from situational by U+2016 (‖)."""
        ctx = VCPContext(
            situational={SituationalDimension.TIME: ["🌅"]},
            personal={PersonalStateDimension.COGNITIVE_STATE: PersonalState("focused", 4)},
        )
        encoded = ctx.encode()
        assert "\u2016" in encoded
        assert "‖🧠focused:4" in encoded

    def test_encode_personal_without_intensity(self):
        ctx = VCPContext(
            personal={PersonalStateDimension.EMOTIONAL_TONE: PersonalState("calm")}
        )
        # Situational empty → encoding begins with the ‖ separator.
        assert ctx.encode() == "\u2016💭calm"

    def test_encode_vep_0004_relationship_is_free_form(self):
        ctx = VCPContext(
            situational={SituationalDimension.RELATIONSHIP: ["colleague:professional"]}
        )
        assert ctx.encode() == "🪢colleague:professional"

    def test_encode_full_18_dim_example(self):
        """End-to-end example matching the spec's canonical 18-dim wire string."""
        ctx = VCPContext(
            situational={
                SituationalDimension.TIME: ["🌅"],
                SituationalDimension.SPACE: ["🏢"],
                SituationalDimension.COMPANY: ["👔"],
                SituationalDimension.OCCASION: ["💼"],
                SituationalDimension.EMBODIMENT: ["✋"],
                SituationalDimension.PROXIMITY: ["🤏"],
                SituationalDimension.RELATIONSHIP: ["colleague:professional"],
                SituationalDimension.FORMALITY: ["💼"],
            },
            personal={
                PersonalStateDimension.COGNITIVE_STATE: PersonalState("focused", 4),
                PersonalStateDimension.EMOTIONAL_TONE: PersonalState("calm", 5),
                PersonalStateDimension.ENERGY_LEVEL: PersonalState("rested", 4),
                PersonalStateDimension.PERCEIVED_URGENCY: PersonalState("unhurried", 2),
                PersonalStateDimension.BODY_SIGNALS: PersonalState("neutral", 1),
            },
        )
        expected = (
            "⏰🌅|📍🏢|👥👔|🎭💼|🧍✋|↔️🤏|🪢colleague:professional|🎩💼"
            "\u2016"
            "🧠focused:4|💭calm:5|🔋rested:4|⚡unhurried:2|🩺neutral:1"
        )
        assert ctx.encode() == expected

    def test_decode_empty(self):
        ctx = VCPContext.decode("")
        assert not ctx

    def test_decode_single_situational(self):
        ctx = VCPContext.decode("⏰🌅")
        assert ctx.get(SituationalDimension.TIME) == ["🌅"]

    def test_decode_personal_band(self):
        ctx = VCPContext.decode("⏰🌅\u2016🧠focused:4")
        assert ctx.get(SituationalDimension.TIME) == ["🌅"]
        ps = ctx.get_personal(PersonalStateDimension.COGNITIVE_STATE)
        assert ps == PersonalState("focused", 4)

    def test_decode_relationship_raw_string(self):
        ctx = VCPContext.decode("🪢friend:social")
        assert ctx.get(SituationalDimension.RELATIONSHIP) == ["friend:social"]

    def test_roundtrip_core(self):
        original = VCPContext(
            situational={
                SituationalDimension.TIME: ["🌅"],
                SituationalDimension.SPACE: ["🏡"],
            }
        )
        decoded = VCPContext.decode(original.encode())
        assert decoded.get(SituationalDimension.TIME) == ["🌅"]
        assert decoded.get(SituationalDimension.SPACE) == ["🏡"]

    def test_roundtrip_full_18_dim(self):
        original = VCPContext(
            situational={
                SituationalDimension.TIME: ["🌅"],
                SituationalDimension.EMBODIMENT: ["✋"],
                SituationalDimension.PROXIMITY: ["🤏"],
                SituationalDimension.RELATIONSHIP: ["colleague:professional"],
                SituationalDimension.FORMALITY: ["💼"],
            },
            personal={
                PersonalStateDimension.COGNITIVE_STATE: PersonalState("focused", 4),
                PersonalStateDimension.EMOTIONAL_TONE: PersonalState("calm", 5),
            },
        )
        decoded = VCPContext.decode(original.encode())
        assert decoded == original


# ────────────────────────────────────────────────────────────────────────────
# JSON
# ────────────────────────────────────────────────────────────────────────────

class TestVCPContextJSON:
    """Test VCPContext JSON serialization."""

    def test_to_json_empty(self):
        ctx = VCPContext()
        data = ctx.to_json()
        assert set(data.keys()) == {"situational", "personal"}
        assert all(v == [] for v in data["situational"].values())
        assert data["personal"] == {}

    def test_to_json_with_values(self):
        ctx = VCPContext(
            situational={
                SituationalDimension.TIME: ["🌅"],
                SituationalDimension.COMPANY: ["👶", "👨‍👩‍👧"],
            },
            personal={PersonalStateDimension.COGNITIVE_STATE: PersonalState("focused", 4)},
        )
        data = ctx.to_json()
        assert data["situational"]["time"] == ["🌅"]
        assert data["situational"]["company"] == ["👶", "👨‍👩‍👧"]
        assert data["situational"]["space"] == []
        assert data["personal"]["cognitive_state"] == {
            "value": "focused",
            "intensity": 4,
        }

    def test_from_json_v32_shape(self):
        data = {
            "situational": {"time": ["🌅"], "space": ["🏡"]},
            "personal": {"cognitive_state": {"value": "focused", "intensity": 4}},
        }
        ctx = VCPContext.from_json(data)
        assert ctx.get(SituationalDimension.TIME) == ["🌅"]
        ps = ctx.get_personal(PersonalStateDimension.COGNITIVE_STATE)
        assert ps == PersonalState("focused", 4)

    def test_from_json_legacy_flat_shape(self):
        """Pre-v3.2 flat shape still decodes (situational-only)."""
        data = {"time": ["🌅"], "space": ["🏡"]}
        ctx = VCPContext.from_json(data)
        assert ctx.get(SituationalDimension.TIME) == ["🌅"]
        assert ctx.get(SituationalDimension.SPACE) == ["🏡"]

    def test_from_json_string_value(self):
        data = {"situational": {"time": "🌅"}}
        ctx = VCPContext.from_json(data)
        assert ctx.get(SituationalDimension.TIME) == ["🌅"]

    def test_json_roundtrip(self):
        original = VCPContext(
            situational={
                SituationalDimension.TIME: ["🌅"],
                SituationalDimension.COMPANY: ["👶"],
            },
            personal={
                PersonalStateDimension.EMOTIONAL_TONE: PersonalState("calm", 5),
            },
        )
        restored = VCPContext.from_json(original.to_json())
        assert original == restored


# ────────────────────────────────────────────────────────────────────────────
# ContextEncoder
# ────────────────────────────────────────────────────────────────────────────

class TestContextEncoder:
    """Test ContextEncoder keyword-argument interface."""

    @pytest.fixture
    def encoder(self):
        return ContextEncoder()

    def test_encode_time(self, encoder):
        ctx = encoder.encode(time="morning")
        assert ctx.get(SituationalDimension.TIME) == ["🌅"]

    def test_encode_space(self, encoder):
        ctx = encoder.encode(space="home")
        assert ctx.get(SituationalDimension.SPACE) == ["🏡"]

    def test_encode_company_list(self, encoder):
        ctx = encoder.encode(company=["children", "family"])
        values = ctx.get(SituationalDimension.COMPANY)
        assert "👶" in values
        assert "👨‍👩‍👧" in values

    def test_encode_company_string(self, encoder):
        ctx = encoder.encode(company="alone")
        assert ctx.get(SituationalDimension.COMPANY) == ["👤"]

    def test_encode_multiple(self, encoder):
        ctx = encoder.encode(
            time="morning",
            space="home",
            company=["children"],
            occasion="normal",
        )
        assert ctx.has(SituationalDimension.TIME)
        assert ctx.has(SituationalDimension.SPACE)
        assert ctx.has(SituationalDimension.COMPANY)
        assert ctx.has(SituationalDimension.OCCASION)

    def test_encode_invalid_value(self, encoder):
        ctx = encoder.encode(time="invalid_time")
        assert not ctx.has(SituationalDimension.TIME)

    def test_encode_empty(self, encoder):
        ctx = encoder.encode()
        assert not ctx

    def test_encode_agency(self, encoder):
        ctx = encoder.encode(agency="leader")
        assert ctx.get(SituationalDimension.AGENCY) == ["👑"]

    def test_encode_constraints_list(self, encoder):
        ctx = encoder.encode(constraints=["legal", "time"])
        values = ctx.get(SituationalDimension.CONSTRAINTS)
        assert "⚖️" in values
        assert "⏱️" in values

    # ── VEP-0004 ────────────────────────────────────────────────────────
    def test_encode_embodiment(self, encoder):
        ctx = encoder.encode(embodiment="manipulating")
        assert ctx.get(SituationalDimension.EMBODIMENT) == ["✋"]

    def test_encode_proximity(self, encoder):
        ctx = encoder.encode(proximity="close")
        assert ctx.get(SituationalDimension.PROXIMITY) == ["🤏"]

    def test_encode_relationship_is_passthrough(self, encoder):
        ctx = encoder.encode(relationship="colleague:professional")
        assert ctx.get(SituationalDimension.RELATIONSHIP) == ["colleague:professional"]

    def test_encode_formality(self, encoder):
        ctx = encoder.encode(formality="professional")
        assert ctx.get(SituationalDimension.FORMALITY) == ["💼"]

    def test_encode_system_context(self, encoder):
        ctx = encoder.encode(system_context="online")
        assert ctx.get(SituationalDimension.SYSTEM_CONTEXT) == ["🟢"]

    def test_encode_culture_communication_style(self, encoder):
        """CULTURE must accept communication-style values, not nationalities."""
        ctx = encoder.encode(culture="high_context")
        assert ctx.get(SituationalDimension.CULTURE) == ["🔇"]

    def test_encode_culture_legacy_nationality_is_rejected(self, encoder):
        """Legacy nationality values must no longer resolve (regression guard)."""
        ctx = encoder.encode(culture="american")
        assert not ctx.has(SituationalDimension.CULTURE)

    # ── Personal state ──────────────────────────────────────────────────
    def test_encode_personal_state_as_string(self, encoder):
        ctx = encoder.encode(cognitive_state="focused")
        ps = ctx.get_personal(PersonalStateDimension.COGNITIVE_STATE)
        assert ps == PersonalState("focused")

    def test_encode_personal_state_with_intensity_tuple(self, encoder):
        ctx = encoder.encode(cognitive_state=("focused", 4))
        ps = ctx.get_personal(PersonalStateDimension.COGNITIVE_STATE)
        assert ps == PersonalState("focused", 4)

    def test_encode_personal_state_with_inline_intensity(self, encoder):
        ctx = encoder.encode(emotional_tone="calm:5")
        ps = ctx.get_personal(PersonalStateDimension.EMOTIONAL_TONE)
        assert ps == PersonalState("calm", 5)


# ────────────────────────────────────────────────────────────────────────────
# Conformance classification
# ────────────────────────────────────────────────────────────────────────────

class TestConformanceLevel:
    def test_minimal(self):
        ctx = VCPContext(situational={SituationalDimension.TIME: ["🌅"]})
        assert ctx.conformance_level() == "VCP-Minimal"

    def test_standard(self):
        ctx = VCPContext(
            situational={SituationalDimension.TIME: ["🌅"]},
            personal={PersonalStateDimension.COGNITIVE_STATE: PersonalState("focused", 4)},
        )
        assert ctx.conformance_level() == "VCP-Standard"

    def test_extended(self):
        ctx = VCPContext(
            situational={SituationalDimension.EMBODIMENT: ["✋"]},
        )
        assert ctx.conformance_level() == "VCP-Extended"

    def test_extended_takes_precedence_over_standard(self):
        ctx = VCPContext(
            situational={SituationalDimension.FORMALITY: ["💼"]},
            personal={PersonalStateDimension.COGNITIVE_STATE: PersonalState("focused")},
        )
        assert ctx.conformance_level() == "VCP-Extended"
