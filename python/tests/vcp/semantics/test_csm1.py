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

    @pytest.mark.parametrize("version", ["latest", "canary", "1.2.3"])
    def test_schema_versions_are_supported(self, version):
        assert CSM1Code.parse(f"N5@{version}").version == version


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
