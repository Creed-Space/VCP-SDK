"""Tests for VCP/A Context Encoder (VCP v3.2 / VEP-0004)."""

import pytest

from vcp.adaptation import (
    ContextEncoder,
    Dimension,
    PersonalState,
    PersonalStateDimension,
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
            SituationalDimension.from_name("system_context") == SituationalDimension.SYSTEM_CONTEXT
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

    @pytest.mark.parametrize("intensity", [True, False, 1.5, "3"])
    def test_intensity_rejects_non_integer_runtime_types(self, intensity: object) -> None:
        with pytest.raises(ValueError, match="intensity"):
            PersonalState(value="focused", intensity=intensity)  # type: ignore[arg-type]

    @pytest.mark.parametrize("value", ["", "focused|💭calm", "focused‖💭calm", "focused:4"])
    def test_value_rejects_empty_or_wire_ambiguous_text(self, value: str) -> None:
        with pytest.raises(ValueError):
            PersonalState(value=value)

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
        ctx = VCPContext(personal={PersonalStateDimension.EMOTIONAL_TONE: PersonalState("calm", 5)})
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
        ctx = VCPContext(personal={PersonalStateDimension.EMOTIONAL_TONE: PersonalState("calm")})
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

    def test_relationship_cannot_smuggle_a_second_dimension(self) -> None:
        with pytest.raises(ValueError, match="relationship"):
            ContextEncoder().encode(relationship="friend:social|📍🏡")

    def test_mutable_context_is_intentionally_unhashable(self) -> None:
        with pytest.raises(TypeError):
            hash(VCPContext())

    def test_constructor_and_json_output_do_not_alias_nested_lists(self) -> None:
        values = ["🌅"]
        ctx = VCPContext(situational={SituationalDimension.TIME: values})
        values.append("🌙")
        encoded = ctx.to_json()
        encoded["situational"]["time"].append("🌆")
        assert ctx.get(SituationalDimension.TIME) == ["🌅"]

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

    def test_roundtrip_preserves_multi_codepoint_company_values(self):
        original = VCPContext(situational={SituationalDimension.COMPANY: ["👶", "👨‍👩‍👧"]})
        assert VCPContext.decode(original.encode()) == original

    def test_decode_accepts_bare_vs16_dimension_and_value_symbols(self):
        proximity = VCPContext.decode("↔🤏")
        assert proximity.get(SituationalDimension.PROXIMITY) == ["🤏"]

        midday = VCPContext.decode("⏰☀")
        assert midday.get(SituationalDimension.TIME) == ["☀️"]

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

    @pytest.mark.parametrize(
        "payload",
        [
            [],
            {"situational": []},
            {"personal": {"cognitive_state": 3}},
            {"personal": {"cognitive_state": {"intensity": 3}}},
            {"situational": {"time": [None]}},
        ],
    )
    def test_from_json_rejects_malformed_runtime_shapes(self, payload: object) -> None:
        with pytest.raises((TypeError, ValueError)):
            VCPContext.from_json(payload)  # type: ignore[arg-type]

    def test_from_json_string_value(self):
        data = {"situational": {"time": "🌅"}}
        ctx = VCPContext.from_json(data)
        assert ctx.get(SituationalDimension.TIME) == ["🌅"]

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"situational": []},
            {"situational": ""},
            {"personal": []},
            {"personal": ""},
        ],
    )
    def test_constructor_does_not_coerce_falsey_wrong_shapes_to_empty(
        self, kwargs: dict[str, object]
    ) -> None:
        with pytest.raises((TypeError, ValueError)):
            VCPContext(**kwargs)  # type: ignore[arg-type]

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
        with pytest.raises(ValueError, match="Unknown time value"):
            encoder.encode(time="invalid_time")

    def test_encode_invalid_value_non_strict_drops(self, encoder):
        ctx = encoder.encode(time="invalid_time", strict=False)
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
        assert "⏰" in values

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
        ctx = encoder.encode(system_context="personal_device")
        assert ctx.get(SituationalDimension.SYSTEM_CONTEXT) == ["💻"]

    def test_system_context_vocabulary_matches_spec(self):
        """SYSTEM_CONTEXT follows VCP/A §2.1 (computing environment)."""
        assert SituationalDimension.SYSTEM_CONTEXT.values == {
            "💻": "personal_device",
            "🏢": "workplace_system",
            "🖥️": "shared_terminal",
            "👁️": "monitored_environment",
        }

    @pytest.mark.parametrize("retired", ["online", "degraded", "offline", "sandboxed", "testing"])
    def test_retired_system_context_names_are_rejected(self, encoder, retired):
        with pytest.raises(ValueError, match="Unknown system_context value"):
            encoder.encode(system_context=retired)

    def test_culture_vocabulary_matches_spec(self):
        """CULTURE follows VCP/A §2.1 (communication styles)."""
        assert SituationalDimension.CULTURE.values == {
            "🔇": "high_context",
            "📢": "low_context",
            "🎩": "formal",
            "👋": "informal",
            "📊": "hierarchical",
            "⚖️": "egalitarian",
            "👥": "collectivist",
            "👤": "individualist",
        }

    def test_culture_casual_is_deprecated_alias_for_informal(self, encoder):
        with pytest.warns(DeprecationWarning, match="informal"):
            ctx = encoder.encode(culture="casual")
        assert ctx.get(SituationalDimension.CULTURE) == ["👋"]

    def test_culture_mixed_is_retired(self, encoder):
        with pytest.raises(ValueError, match="Unknown culture value"):
            encoder.encode(culture="mixed")

    def test_new_vocabularies_roundtrip_through_wire(self, encoder):
        ctx = encoder.encode(
            culture=["hierarchical", "collectivist"],
            system_context="monitored_environment",
        )
        wire = ctx.encode()
        assert wire == "🌍📊👥|📡👁️"
        decoded = VCPContext.decode(wire)
        assert decoded.get(SituationalDimension.CULTURE) == ["📊", "👥"]
        assert decoded.get(SituationalDimension.SYSTEM_CONTEXT) == ["👁️"]
        # VS16-less input still resolves to the canonical emoji.
        bare = VCPContext.decode("📡🖥")
        assert bare.get(SituationalDimension.SYSTEM_CONTEXT) == ["🖥️"]

    def test_retired_values_on_the_wire_are_tolerated(self):
        """Unknown values decode as raw strings rather than failing (VCP/A §2.1)."""
        decoded = VCPContext.decode("🌍😎|📡🟢")
        assert decoded.get(SituationalDimension.CULTURE) == ["😎"]
        assert decoded.get(SituationalDimension.SYSTEM_CONTEXT) == ["🟢"]

    def test_encode_culture_communication_style(self, encoder):
        """CULTURE must accept communication-style values, not nationalities."""
        ctx = encoder.encode(culture="high_context")
        assert ctx.get(SituationalDimension.CULTURE) == ["🔇"]

    def test_encode_culture_legacy_nationality_is_rejected(self, encoder):
        """Legacy nationality values must no longer resolve (regression guard)."""
        with pytest.raises(ValueError, match="Unknown culture value"):
            encoder.encode(culture="american")
        ctx = encoder.encode(culture="american", strict=False)
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


# ────────────────────────────────────────────────────────────────────────────
# VCP/A §2.2 vocabularies and §2.3 forward compatibility
# ────────────────────────────────────────────────────────────────────────────

_SCHEMA_PATH = (
    __import__("pathlib").Path(__file__).resolve().parents[4]
    / "schemas"
    / "vcp-adaptation-context.schema.json"
)


def _schema_definitions() -> dict:
    import json

    return json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))["definitions"]


class TestVocabulariesMatchSchema:
    @pytest.mark.parametrize("dim", [d for d in SituationalDimension if not d.is_free_form])
    def test_situational_values_match_schema_enum(self, dim):
        """Every situational vocabulary equals the synchronized schema enum, in order."""
        enum = _schema_definitions()[f"{dim._name}_values"]["enum"]
        assert list(dim.values) == enum

    @pytest.mark.parametrize("pdim", list(PersonalStateDimension))
    def test_personal_categories_match_schema_enum(self, pdim):
        enum = _schema_definitions()[f"{pdim._name}_values"]["enum"]
        assert pdim.values == set(enum)

    @pytest.mark.parametrize(
        ("dimension", "retired", "canonical", "emoji"),
        [
            ("time", "midday", "daytime", "☀️"),
            ("space", "transit", "vehicle", "🚗"),
            ("environment", "noisy", "loud", "📢"),
            ("culture", "casual", "informal", "👋"),
        ],
    )
    def test_renamed_values_are_deprecated_aliases(self, dimension, retired, canonical, emoji):
        encoder = ContextEncoder()
        with pytest.warns(DeprecationWarning, match=canonical):
            ctx = encoder.encode(**{dimension: retired})
        assert ctx.get(SituationalDimension.from_name(dimension)) == [emoji]

    @pytest.mark.parametrize(
        ("dimension", "retired"),
        [("environment", "comfortable"), ("culture", "mixed"), ("system_context", "online")],
    )
    def test_removed_values_have_no_alias(self, dimension, retired):
        with pytest.raises(ValueError, match="Unknown"):
            ContextEncoder().encode(**{dimension: retired})

    def test_value_emoji_changes(self):
        encoder = ContextEncoder()
        ctx = encoder.encode(
            company="strangers",
            occasion="mourning",
            agency="subordinate",
            constraints="time",
        )
        assert ctx.encode() == "👥🧑‍🤝‍🧑|🎭⚰️|🔷👇|🔶⏰"


class TestForwardCompatibleDecoding:
    """VCP/A §2.3: receivers ignore or pass through; strict validators report."""

    def test_unknown_values_are_kept_raw(self):
        ctx = VCPContext.decode("🎭😢|🔷📋|🔶⏱️")
        assert ctx.get(SituationalDimension.OCCASION) == ["😢"]
        assert ctx.get(SituationalDimension.AGENCY) == ["📋"]
        assert ctx.encode() == "🎭😢|🔷📋|🔶⏱️"

    def test_unknown_dimension_groups_pass_through(self):
        wire = "⏰🌅|🦄sparkle|📍🏡‖🧠focused:4|🪐orbit:2"
        ctx = VCPContext.decode(wire)
        assert ctx.unknown_situational == ("🦄sparkle",)
        assert ctx.unknown_personal == ("🪐orbit:2",)
        assert ctx.get(SituationalDimension.TIME) == ["🌅"]
        assert ctx.encode() == "⏰🌅|📍🏡|🦄sparkle‖🧠focused:4|🪐orbit:2"
        assert VCPContext.decode(ctx.encode()) == ctx
        assert VCPContext.from_json(ctx.to_json()) == ctx

    def test_known_emergency_indicator_survives_unknown_groups(self):
        from vcp.adaptation import StateTracker, TransitionSeverity

        tracker = StateTracker()
        tracker.record(VCPContext.decode("⏰🌅"))
        transition = tracker.record(VCPContext.decode("⏰🌅|🦄sparkle|🎭🚨"))
        assert transition.severity is TransitionSeverity.EMERGENCY

    def test_only_unknown_groups(self):
        ctx = VCPContext.decode("🦄sparkle")
        assert not ctx
        assert ctx.encode() == "🦄sparkle"

    @pytest.mark.parametrize(
        "wire",
        [
            "⏰🌅||📍🏡",
            "⏰🌅|",
            "⏰",
            "⏰🌅‖",
            "‖🧠focused:4|",
            "‖🧠",
            "‖🧠focused:9",
            "abc",
            "⏰🌅‖focused",
        ],
    )
    def test_malformed_strings_are_rejected(self, wire):
        with pytest.raises(ValueError):
            VCPContext.decode(wire)

    def test_strict_validator_reports_unknowns(self):
        from vcp.adaptation import validate_context_wire

        assert validate_context_wire("⏰🌅|📍🏡|🎭⚰️‖🧠focused:4") == []
        issues = validate_context_wire("🎭😢|🦄sparkle|🪢friend:gaming‖🧠scattered|🪐orbit")
        assert issues == [
            "unknown situational dimension group: '🦄sparkle'",
            "unknown occasion value: '😢'",
            "unknown relationship value: 'friend:gaming'",
            "unknown personal dimension group: '🪐orbit'",
            "unknown cognitive_state category: 'scattered'",
        ]
        assert validate_context_wire("⏰🌅||📍🏡")[0].startswith("malformed:")

    def test_strict_decode_raises(self):
        with pytest.raises(ValueError, match="unknown occasion value"):
            VCPContext.decode("🎭😢", strict=True)
        assert VCPContext.decode("🎭⚰️", strict=True).get(SituationalDimension.OCCASION) == ["⚰️"]


class TestIntensityGrammar:
    """VCP/A §2.3: an intensity is exactly one digit 1-5."""

    @pytest.mark.parametrize(
        "segment",
        [
            "focused:04",
            "focused:0",
            "focused:6",
            "focused:+4",
            "focused: 4",
            "focused:",
            "focused:٤",
            "focused:4.0",
            "colleague:professional",
        ],
    )
    def test_malformed_intensity_is_rejected(self, segment):
        with pytest.raises(ValueError):
            PersonalState.decode(segment)
        with pytest.raises(ValueError):
            VCPContext.decode(f"‖🧠{segment}")

    @pytest.mark.parametrize("digit", ["1", "2", "3", "4", "5"])
    def test_single_digit_intensity(self, digit):
        assert PersonalState.decode(f"focused:{digit}") == PersonalState("focused", int(digit))

    def test_personal_only_context(self):
        ctx = VCPContext.decode("‖🧠focused:4|💭calm")
        assert ctx.situational == {}
        assert ctx.encode() == "‖🧠focused:4|💭calm"
        from vcp.adaptation import validate_context_wire

        assert validate_context_wire("‖🧠focused:4|💭calm") == []
        assert validate_context_wire("‖🧠focused:04")[0].startswith("malformed:")


class TestReviewFixes:
    """Canon round 4: mixed groups, repeated dimensions, relationship forms."""

    def test_known_values_survive_unknown_neighbors(self):
        ctx = VCPContext.decode("🎭🚨🦖")
        assert ctx.get(SituationalDimension.OCCASION) == ["🚨", "🦖"]
        assert ctx.encode() == "🎭🚨🦖"
        ctx = VCPContext.decode("🎭🦖🚨🎂")
        assert ctx.get(SituationalDimension.OCCASION) == ["🦖", "🚨", "🎂"]
        from vcp.adaptation import validate_context_wire

        assert validate_context_wire("🎭🚨🦖") == ["unknown occasion value: '🦖'"]

    def test_mixed_group_is_an_emergency(self):
        from vcp.adaptation import StateTracker, TransitionSeverity

        tracker = StateTracker()
        tracker.record(VCPContext.decode("⏰🌅"))
        assert tracker.record(VCPContext.decode("🎭🚨🦖")).severity is TransitionSeverity.EMERGENCY
        # An indicator outside the dimension's vocabulary, inside a raw run.
        tracker.record(VCPContext.decode("⏰🌅"))
        assert tracker.record(VCPContext.decode("🎭🦖🔥")).severity is TransitionSeverity.EMERGENCY

    @pytest.mark.parametrize(
        "wire", ["⏰🌅|⏰🌙", "⏰🌅|📍🏡|⏰🌙", "‖🧠focused|🧠foggy", "🌡️🥵|🌡🥶"]
    )
    def test_repeated_dimension_is_malformed(self, wire):
        with pytest.raises(ValueError, match="repeated"):
            VCPContext.decode(wire)

    @pytest.mark.parametrize("value", ["colleague", ":professional", "colleague:professional"])
    def test_relationship_single_part_forms(self, value):
        ctx = VCPContext.decode(f"🪢{value}")
        assert ctx.get(SituationalDimension.RELATIONSHIP) == [value]
        assert ctx.encode() == f"🪢{value}"
        assert ContextEncoder().encode(relationship=value).encode() == f"🪢{value}"

    @pytest.mark.parametrize("value", ["a:b:c", "colleague:", ":"])
    def test_relationship_rejects_other_forms(self, value):
        with pytest.raises(ValueError):
            VCPContext(situational={SituationalDimension.RELATIONSHIP: [value]})

    def test_sub_signals_are_malformed_in_context_strings(self):
        for wire in ("‖🩺pain:4[migraine]", "‖🩺pain:4:migraine"):
            with pytest.raises(ValueError):
                VCPContext.decode(wire)


class TestGraphemeBoundaries:
    """A known value never matches inside an emoji sequence (VCP/A §2.3)."""

    @pytest.mark.parametrize(
        ("wire", "dimension", "values"),
        [
            ("📡👁️‍🗨️", SituationalDimension.SYSTEM_CONTEXT, ["👁️‍🗨️"]),
            ("👥👶🏽", SituationalDimension.COMPANY, ["👶🏽"]),
            ("📍🏠️", SituationalDimension.SPACE, ["🏠️"]),
            ("👥👶🏽👔", SituationalDimension.COMPANY, ["👶🏽", "👔"]),
            ("🔷🧑‍🤝", SituationalDimension.AGENCY, ["🧑‍🤝"]),
            ("👥👨‍👩‍👧👶", SituationalDimension.COMPANY, ["👨‍👩‍👧", "👶"]),
            ("📡👁️", SituationalDimension.SYSTEM_CONTEXT, ["👁️"]),
        ],
    )
    def test_sequences_are_not_split(self, wire, dimension, values):
        ctx = VCPContext.decode(wire)
        assert ctx.get(dimension) == values
        assert ctx.encode() == wire

    def test_unknown_sequence_is_reported_not_treated_as_known(self):
        from vcp.adaptation import validate_context_wire

        sequence = "👁️‍🗨️"
        assert validate_context_wire(f"📡{sequence}") == [
            f"unknown system_context value: {sequence!r}"
        ]
        assert validate_context_wire("👥👶🏽") == ["unknown company value: '👶🏽'"]
