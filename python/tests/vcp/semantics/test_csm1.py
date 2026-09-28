"""Tests for VCP/S CSM1 Grammar Parser."""

import pytest

from vcp.semantics import CSM1Code, Persona, Scope


class TestPersona:
    """Test Persona enum."""

    def test_all_personas_have_single_char(self):
        """All personas should have single character value."""
        for persona in Persona:
            assert len(persona.value) == 1

    def test_from_char(self):
        """from_char should return correct persona."""
        assert Persona.from_char("N") == Persona.NANNY
        assert Persona.from_char("Z") == Persona.SENTINEL
        assert Persona.from_char("G") == Persona.GODPARENT
        assert Persona.from_char("A") == Persona.AMBASSADOR
        assert Persona.from_char("M") == Persona.MUSE
        assert Persona.from_char("D") == Persona.MEDIATOR
        assert Persona.from_char("C") == Persona.CUSTOM

    def test_from_char_lowercase(self):
        """from_char should handle lowercase."""
        assert Persona.from_char("n") == Persona.NANNY

    def test_from_char_invalid(self):
        """from_char should raise for invalid char."""
        with pytest.raises(ValueError, match="Unknown persona"):
            Persona.from_char("X")

    def test_description(self):
        """Each persona should have a description."""
        for persona in Persona:
            assert persona.description
            assert isinstance(persona.description, str)


class TestScope:
    """Test Scope enum."""

    def test_all_scopes_have_single_char(self):
        """All scopes should have single character value."""
        for scope in Scope:
            assert len(scope.value) == 1

    def test_from_char(self):
        """from_char should return correct scope."""
        assert Scope.from_char("F") == Scope.FAMILY
        assert Scope.from_char("W") == Scope.WORK
        assert Scope.from_char("P") == Scope.PRIVACY
        assert Scope.from_char("E") == Scope.EDUCATION
        assert Scope.from_char("T") == Scope.TECHNICAL
        assert Scope.from_char("O") == Scope.OFFICIAL
        assert Scope.from_char("V") == Scope.VULNERABLE
        assert Scope.from_char("A") == Scope.ADULT
        assert Scope.from_char("H") == Scope.HEALTHCARE
        assert Scope.from_char("S") == Scope.SOCIAL
        assert Scope.from_char("R") == Scope.RELIGIOUS

    def test_from_char_invalid(self):
        """from_char should raise for invalid char."""
        with pytest.raises(ValueError, match="Unknown scope"):
            Scope.from_char("X")

    def test_description(self):
        """Each scope should have a description."""
        for scope in Scope:
            assert scope.description
            assert isinstance(scope.description, str)


class TestCSM1Parsing:
    """Test CSM1 code parsing."""

    def test_simple_code(self):
        """Parse basic persona+level code."""
        code = CSM1Code.parse("N5")
        assert code.persona == Persona.NANNY
        assert code.adherence_level == 5
        assert code.scopes == []
        assert code.namespace is None
        assert code.version is None

    def test_code_with_scopes(self):
        """Parse code with scope modifiers."""
        code = CSM1Code.parse("N5+F+E")
        assert code.persona == Persona.NANNY
        assert code.adherence_level == 5
        assert code.scopes == [Scope.FAMILY, Scope.EDUCATION]

    def test_code_with_namespace(self):
        """Parse code with namespace."""
        code = CSM1Code.parse("Z3+P:SEC")
        assert code.persona == Persona.SENTINEL
        assert code.adherence_level == 3
        assert code.scopes == [Scope.PRIVACY]
        assert code.namespace == "SEC"

    def test_code_with_version(self):
        """Parse code with version."""
        code = CSM1Code.parse("M2@1.0.0")
        assert code.persona == Persona.MUSE
        assert code.adherence_level == 2
        assert code.version == "1.0.0"

    def test_full_code(self):
        """Parse code with all components."""
        code = CSM1Code.parse("G4+F+E+H:ELEM@2.1.0")
        assert code.persona == Persona.GODPARENT
        assert code.adherence_level == 4
        assert code.scopes == [Scope.FAMILY, Scope.EDUCATION, Scope.HEALTHCARE]
        assert code.namespace == "ELEM"
        assert code.version == "2.1.0"

    def test_lowercase_input_is_rejected_to_match_schema(self):
        with pytest.raises(ValueError, match="Invalid CSM1"):
            CSM1Code.parse("n5+f+e")

    def test_all_personas(self):
        """Parse all persona types."""
        for persona in Persona:
            raw = "C3:CUSTOM" if persona is Persona.CUSTOM else f"{persona.value}3"
            code = CSM1Code.parse(raw)
            assert code.persona == persona

    def test_all_levels(self):
        """Parse all adherence levels."""
        for level in range(6):
            code = CSM1Code.parse(f"N{level}")
            assert code.adherence_level == level


class TestCSM1Validation:
    """Test CSM1 validation rules."""

    def test_empty_raises(self):
        """Empty string should raise."""
        with pytest.raises(ValueError, match="cannot be empty"):
            CSM1Code.parse("")

    def test_invalid_persona_raises(self):
        """Invalid persona character should raise."""
        with pytest.raises(ValueError, match="Invalid CSM1"):
            CSM1Code.parse("X5")

    def test_invalid_level_raises(self):
        """Invalid level should raise."""
        with pytest.raises(ValueError, match="Invalid CSM1"):
            CSM1Code.parse("N9")  # Level must be 0-5

    def test_invalid_scope_raises(self):
        """Invalid scope character should raise."""
        with pytest.raises(ValueError, match="Invalid CSM1"):
            CSM1Code.parse("N5+X")

    def test_missing_level_raises(self):
        """Missing level should raise."""
        with pytest.raises(ValueError, match="Invalid CSM1"):
            CSM1Code.parse("N")

    @pytest.mark.parametrize("legacy_scope", ["I", "L", "G"])
    def test_schema_rejected_legacy_scopes_are_rejected(self, legacy_scope):
        with pytest.raises(ValueError, match="Invalid CSM1"):
            CSM1Code.parse(f"N5+{legacy_scope}")

    def test_custom_persona_requires_namespace(self):
        with pytest.raises(ValueError, match="requires a namespace"):
            CSM1Code.parse("C3")
        assert CSM1Code.parse("C3:ACME").namespace == "ACME"

    def test_duplicate_scopes_are_rejected(self):
        with pytest.raises(ValueError, match="unique"):
            CSM1Code.parse("N5+F+F")

    @pytest.mark.parametrize("code", ["N5+F+A", "N5+V+A", "N5+H+A"])
    def test_incompatible_scopes_conflict(self, code):
        with pytest.raises(ValueError, match="cannot be combined"):
            CSM1Code.parse(code)

    def test_namespace_length_is_bounded(self):
        with pytest.raises(ValueError, match="Invalid CSM1"):
            CSM1Code.parse("N5:TOOLONGNS")
        with pytest.raises(ValueError, match="Invalid CSM1"):
            CSM1Code.parse("N5:A1")

    def test_wire_length_limit_matches_the_canonical_schema(self):
        assert CSM1Code.MAX_LENGTH == 45
        with pytest.raises(ValueError, match="maximum length 45"):
            CSM1Code.parse("N5" + "X" * 44)

    @pytest.mark.parametrize("version", ["latest", "canary", "1.2.3"])
    def test_schema_versions_are_supported(self, version):
        assert CSM1Code.parse(f"N5@{version}").version == version

    @pytest.mark.parametrize("version", ["01.2.3", "1.02.3", "1.2.03"])
    def test_semver_components_with_leading_zero_are_rejected(self, version):
        with pytest.raises(ValueError, match="Invalid CSM1"):
            CSM1Code.parse(f"N5@{version}")
        with pytest.raises(ValueError, match="Invalid CSM1 version"):
            CSM1Code(Persona.NANNY, 5, version=version)


class TestCSM1Encoding:
    """Test CSM1 encoding back to string."""

    def test_simple_encode(self):
        """Encode basic code."""
        code = CSM1Code.parse("N5")
        assert code.encode() == "N5"

    def test_encode_with_scopes(self):
        """Encode with scopes."""
        code = CSM1Code.parse("N5+F+E")
        assert code.encode() == "N5+E+F"

    def test_encode_with_namespace(self):
        """Encode with namespace."""
        code = CSM1Code.parse("Z3+P:SEC")
        assert code.encode() == "Z3+P:SEC"

    def test_encode_with_version(self):
        """Encode with version."""
        code = CSM1Code.parse("M2@1.0.0")
        assert code.encode() == "M2@1.0.0"

    def test_roundtrip(self):
        """Parse and encode should roundtrip."""
        original = "G4+F+E+H:ELEM@2.1.0"
        code = CSM1Code.parse(original)
        assert code.encode() == "G4+E+F+H:ELEM@2.1.0"


class TestCSM1Methods:
    """Test CSM1Code utility methods."""

    def test_applies_to_empty_scopes(self):
        """Empty scopes should apply to all."""
        code = CSM1Code.parse("N5")
        assert code.applies_to(Scope.FAMILY) is True
        assert code.applies_to(Scope.WORK) is True

    def test_applies_to_specific_scopes(self):
        """Specific scopes should only match."""
        code = CSM1Code.parse("N5+F+E")
        assert code.applies_to(Scope.FAMILY) is True
        assert code.applies_to(Scope.EDUCATION) is True
        assert code.applies_to(Scope.WORK) is False

    def test_with_scopes(self):
        """with_scopes should return new code."""
        code1 = CSM1Code.parse("N5")
        code2 = code1.with_scopes([Scope.FAMILY, Scope.WORK])
        assert code1.scopes == []
        assert code2.scopes == [Scope.FAMILY, Scope.WORK]

    def test_with_level(self):
        """with_level should return new code."""
        code1 = CSM1Code.parse("N5")
        code2 = code1.with_level(3)
        assert code1.adherence_level == 5
        assert code2.adherence_level == 3

    def test_with_level_invalid(self):
        """with_level should reject invalid levels."""
        code = CSM1Code.parse("N5")
        with pytest.raises(ValueError, match="Level must be"):
            code.with_level(6)

    def test_is_active(self):
        """is_active should check level > 0."""
        assert CSM1Code.parse("N0").is_active is False
        assert CSM1Code.parse("N1").is_active is True
        assert CSM1Code.parse("N5").is_active is True

    def test_is_maximum(self):
        """is_maximum should check level == 5."""
        assert CSM1Code.parse("N4").is_maximum is False
        assert CSM1Code.parse("N5").is_maximum is True

    def test_str(self):
        """str() should return encoded form."""
        code = CSM1Code.parse("N5+F")
        assert str(code) == "N5+F"

    def test_repr(self):
        """repr() should include class name."""
        code = CSM1Code.parse("N5")
        assert repr(code) == "CSM1Code('N5')"


class TestCSM1Compact:
    """COMPACT tier (VCP/S §2.8.3): CS1|<persona>|<level>|<token>|<scopes>."""

    @pytest.mark.parametrize(
        ("raw", "persona", "level", "token", "scopes"),
        [
            (
                "CS1|nanny|5|family.safe.guide|E,F",
                Persona.NANNY,
                5,
                "family.safe.guide",
                [Scope.EDUCATION, Scope.FAMILY],
            ),
            (
                "CS1|sentinel|4|secure.privacy.guardian|P,W",
                Persona.SENTINEL,
                4,
                "secure.privacy.guardian",
                [Scope.PRIVACY, Scope.WORK],
            ),
            (
                "CS1|custom|3|company.acme.legal|O,W",
                Persona.CUSTOM,
                3,
                "company.acme.legal",
                [Scope.OFFICIAL, Scope.WORK],
            ),
            (
                "CS1|nanny|5|family.safe.guide@1.2.3:CORE|F,E",
                Persona.NANNY,
                5,
                "family.safe.guide@1.2.3:CORE",
                [Scope.FAMILY, Scope.EDUCATION],
            ),
        ],
    )
    def test_parse_spec_examples(self, raw, persona, level, token, scopes):
        code = CSM1Code.parse(raw)
        assert code.persona is persona
        assert code.adherence_level == level
        assert code.uvc_token == token
        assert code.scopes == scopes  # wire order is preserved
        assert code.namespace is None
        assert code.version is None
        assert CSM1Code.parse_compact(raw) == code

    @pytest.mark.parametrize(
        "raw",
        [
            "CS1|nanny|5|family.safe.guide|",  # no scope
            "CS1|nanny|5|family.safe.guide|F,F",  # duplicate scope
            "CS1|nanny|5|family.safe.guide|F,A",  # conflicting scopes
            "CS1|nanny|5|family.safe.guide|V,A",
            "CS1|nanny|5|family.safe.guide|H,A",
            "CS1|Nanny|5|family.safe.guide|F",  # persona name must be lowercase
            "CS1|nanny|5|family.guide|F",  # token needs 3+ segments
            "CS1|nanny|5|a.b.c.d.e.f.g.h.i.j.k|F",  # token allows at most 10 segments
            "CS1|nanny|5|Family.safe.guide|F",  # token must be canonical
            "CS1|nanny|5|family.safe.guide@01.2.3|F",  # no leading zeroes on input
            "CS1|nanny|6|family.safe.guide|F",  # level out of range
            "CS1|nanny|5|family.safe.guide|X",  # unknown scope
            "CS1|nanny|5|family.safe.guide|F+E",  # scopes are comma-separated
            "CS1|robot|5|family.safe.guide|F",  # unknown persona
            "CS1|nanny|5|family.safe.guide@1.2.3-beta|F",  # no prerelease
            " CS1|nanny|5|family.safe.guide|F",  # surrounding whitespace
            "CS1|nanny|5|family.safe.guide|F ",
            "CS1|nanny|5|family.safe.guide|F|E",
        ],
    )
    def test_parse_rejects_malformed(self, raw):
        with pytest.raises(ValueError):
            CSM1Code.parse(raw)

    def test_parse_rejects_over_length(self):
        segments = ".".join(["a" + "b" * 31] * 10)
        raw = f"CS1|ambassador|3|{segments}@^99999.99999.99999:{'N' * 32}|F,W"
        assert len(raw) > CSM1Code.COMPACT_MAX_LENGTH
        with pytest.raises(ValueError, match="characters"):
            CSM1Code.parse(raw)

    def test_parse_accepts_maximum_length(self):
        segments = ".".join(["a" + "b" * 26] * 9)
        raw = f"CS1|ambassador|3|{segments}@^99999.99999.99999:NNNN|F"
        assert len(raw) == CSM1Code.COMPACT_MAX_LENGTH
        assert CSM1Code.parse(raw).encode_compact() == raw

    def test_parse_rejects_too_short(self):
        with pytest.raises(ValueError, match="characters"):
            CSM1Code.parse("CS1|muse|0|a.b|F")

    def test_encode_compact_round_trip(self):
        raw = "CS1|nanny|5|family.safe.guide|E,F"
        assert CSM1Code.parse(raw).encode_compact() == raw

    def test_encode_compact_sorts_scopes(self):
        code = CSM1Code.parse("CS1|nanny|5|family.safe.guide@1.2.3:CORE|F,E")
        assert code.encode_compact() == "CS1|nanny|5|family.safe.guide@1.2.3:CORE|E,F"

    def test_encode_compact_from_micro_with_token(self):
        code = CSM1Code.parse("Z4+W+P:SEC@1.0.0")
        assert (
            code.encode_compact("secure.privacy.guardian")
            == "CS1|sentinel|4|secure.privacy.guardian|P,W"
        )

    def test_encode_compact_normalizes_leading_zeroes(self):
        code = CSM1Code.parse("N5+F")
        assert (
            code.encode_compact("family.safe.guide@01.02.003:CORE")
            == "CS1|nanny|5|family.safe.guide@1.2.3:CORE|F"
        )
        stored = CSM1Code(Persona.NANNY, 5, [Scope.FAMILY], uvc_token="family.safe.guide@~01.0.0")
        assert stored.uvc_token == "family.safe.guide@~1.0.0"

    def test_encode_compact_requires_token(self):
        with pytest.raises(ValueError, match="token"):
            CSM1Code.parse("N5+F").encode_compact()

    def test_encode_compact_rejects_invalid_token(self):
        with pytest.raises(ValueError, match="Invalid constitution token"):
            CSM1Code.parse("N5+F").encode_compact("family.guide")

    def test_encode_compact_rejects_over_length(self):
        token = ".".join(["a" + "b" * 31] * 10)
        with pytest.raises(ValueError, match="characters"):
            CSM1Code.parse("A3+W").encode_compact(token)

    def test_encode_compact_requires_scope(self):
        with pytest.raises(ValueError, match="at least one scope"):
            CSM1Code.parse("N5").encode_compact("family.safe.guide")

    def test_micro_form_of_compact_code(self):
        code = CSM1Code.parse("CS1|nanny|5|family.safe.guide|F,E")
        assert code.encode() == "N5+E+F"
        assert str(code) == "N5+E+F"

    def test_custom_without_namespace_has_only_compact_form(self):
        code = CSM1Code.parse("CS1|custom|3|company.acme.legal|O,W")
        assert code.has_micro_form is False
        with pytest.raises(ValueError, match="no MICRO form"):
            code.encode()
        assert str(code) == "CS1|custom|3|company.acme.legal|O,W"
        assert repr(code) == "CSM1Code('CS1|custom|3|company.acme.legal|O,W')"
        assert code.with_level(4).encode_compact() == "CS1|custom|4|company.acme.legal|O,W"
        with pytest.raises(ValueError, match="namespace"):
            code.with_scopes([])

    def test_custom_still_needs_namespace_without_token(self):
        with pytest.raises(ValueError, match="namespace"):
            CSM1Code(Persona.CUSTOM, 3, [Scope.WORK])
        with pytest.raises(ValueError):
            CSM1Code.parse("C3+W")

    def test_persona_names(self):
        assert [p.wire_name for p in Persona] == [
            "nanny",
            "sentinel",
            "godparent",
            "ambassador",
            "muse",
            "mediator",
            "custom",
        ]
        for persona in Persona:
            assert Persona.from_name(persona.wire_name) is persona
        with pytest.raises(ValueError, match="Unknown persona name"):
            Persona.from_name("Nanny")

    def test_nano_and_micro_unchanged(self):
        assert CSM1Code.parse("N5+F+E").uvc_token is None
        assert CSM1Code.parse("N5+F+E").encode() == "N5+E+F"
        assert CSM1Code.parse("N5+F+E+W+P+T+O+V+H+S+R:ABCDEFGH@100.100.100").namespace == (
            "ABCDEFGH"
        )
        with pytest.raises(ValueError, match="maximum length"):
            CSM1Code.parse("N5" + "+F" * 22)
