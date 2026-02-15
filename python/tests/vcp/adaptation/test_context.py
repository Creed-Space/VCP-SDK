"""Tests for VCP/A Context Encoder."""

import pytest
from services.vcp.adaptation import ContextEncoder, Dimension, VCPContext


class TestDimension:
    """Test Dimension enum."""

    def test_all_dimensions_have_symbol(self):
        """All dimensions should have a symbol."""
        for dim in Dimension:
            assert dim.symbol
            assert isinstance(dim.symbol, str)

    def test_all_dimensions_have_position(self):
        """All dimensions should have unique positions 1-9."""
        positions = [dim.position for dim in Dimension]
        assert sorted(positions) == list(range(1, 10))

    def test_all_dimensions_have_values(self):
        """All dimensions should have value mappings."""
        for dim in Dimension:
            assert dim.values
            assert isinstance(dim.values, dict)

    def test_from_name(self):
        """from_name should return correct dimension."""
        assert Dimension.from_name("time") == Dimension.TIME
        assert Dimension.from_name("TIME") == Dimension.TIME
        assert Dimension.from_name("Space") == Dimension.SPACE

    def test_from_name_invalid(self):
        """from_name should raise for invalid name."""
        with pytest.raises(ValueError, match="Unknown dimension"):
            Dimension.from_name("invalid")


class TestVCPContext:
    """Test VCPContext class."""

    def test_empty_context(self):
        """Empty context should be falsy."""
        ctx = VCPContext()
        assert not ctx
        assert ctx.encode() == ""

    def test_single_dimension(self):
        """Context with single dimension."""
        ctx = VCPContext(dimensions={Dimension.TIME: ["🌅"]})
        assert ctx
        assert ctx.has(Dimension.TIME)
        assert not ctx.has(Dimension.SPACE)

    def test_multiple_dimensions(self):
        """Context with multiple dimensions."""
        ctx = VCPContext(
            dimensions={
                Dimension.TIME: ["🌅"],
                Dimension.SPACE: ["🏡"],
                Dimension.COMPANY: ["👶", "👨‍👩‍👧"],
            }
        )
        assert ctx.get(Dimension.TIME) == ["🌅"]
        assert ctx.get(Dimension.COMPANY) == ["👶", "👨‍👩‍👧"]

    def test_get_missing_dimension(self):
        """get() should return empty list for missing dimension."""
        ctx = VCPContext()
        assert ctx.get(Dimension.TIME) == []

    def test_set_returns_new_context(self):
        """set() should return new context."""
        ctx1 = VCPContext()
        ctx2 = ctx1.set(Dimension.TIME, ["🌅"])
        assert ctx1.get(Dimension.TIME) == []
        assert ctx2.get(Dimension.TIME) == ["🌅"]

    def test_equality(self):
        """Context equality comparison."""
        ctx1 = VCPContext(dimensions={Dimension.TIME: ["🌅"]})
        ctx2 = VCPContext(dimensions={Dimension.TIME: ["🌅"]})
        ctx3 = VCPContext(dimensions={Dimension.TIME: ["🌙"]})

        assert ctx1 == ctx2
        assert ctx1 != ctx3

    def test_equality_not_implemented(self):
        """Equality with non-context returns NotImplemented."""
        ctx = VCPContext()
        assert ctx != "not a context"


class TestVCPContextEncoding:
    """Test VCPContext wire format encoding."""

    def test_encode_single(self):
        """Encode single dimension."""
        ctx = VCPContext(dimensions={Dimension.TIME: ["🌅"]})
        assert ctx.encode() == "⏰🌅"

    def test_encode_multiple(self):
        """Encode multiple dimensions."""
        ctx = VCPContext(
            dimensions={
                Dimension.TIME: ["🌅"],
                Dimension.SPACE: ["🏡"],
            }
        )
        encoded = ctx.encode()
        assert "⏰🌅" in encoded
        assert "📍🏡" in encoded
        assert "|" in encoded

    def test_decode_single(self):
        """Decode single dimension."""
        ctx = VCPContext.decode("⏰🌅")
        assert ctx.get(Dimension.TIME) == ["🌅"]

    def test_decode_empty(self):
        """Decode empty string."""
        ctx = VCPContext.decode("")
        assert not ctx

    def test_roundtrip(self):
        """Encode and decode should roundtrip."""
        original = VCPContext(
            dimensions={
                Dimension.TIME: ["🌅"],
                Dimension.SPACE: ["🏡"],
            }
        )
        encoded = original.encode()
        decoded = VCPContext.decode(encoded)

        # Note: exact equality may fail due to emoji parsing variations
        assert decoded.get(Dimension.TIME) == original.get(Dimension.TIME)
        assert decoded.get(Dimension.SPACE) == original.get(Dimension.SPACE)


class TestVCPContextJSON:
    """Test VCPContext JSON serialization."""

    def test_to_json_empty(self):
        """Empty context to JSON."""
        ctx = VCPContext()
        data = ctx.to_json()
        assert all(v == [] for v in data.values())

    def test_to_json_with_values(self):
        """Context with values to JSON."""
        ctx = VCPContext(
            dimensions={
                Dimension.TIME: ["🌅"],
                Dimension.COMPANY: ["👶", "👨‍👩‍👧"],
            }
        )
        data = ctx.to_json()
        assert data["time"] == ["🌅"]
        assert data["company"] == ["👶", "👨‍👩‍👧"]
        assert data["space"] == []

    def test_from_json(self):
        """Create context from JSON."""
        data = {"time": ["🌅"], "space": ["🏡"]}
        ctx = VCPContext.from_json(data)
        assert ctx.get(Dimension.TIME) == ["🌅"]
        assert ctx.get(Dimension.SPACE) == ["🏡"]

    def test_from_json_string_value(self):
        """from_json should handle single string value."""
        data = {"time": "🌅"}
        ctx = VCPContext.from_json(data)
        assert ctx.get(Dimension.TIME) == ["🌅"]

    def test_json_roundtrip(self):
        """JSON serialization should roundtrip."""
        original = VCPContext(
            dimensions={
                Dimension.TIME: ["🌅"],
                Dimension.COMPANY: ["👶"],
            }
        )
        data = original.to_json()
        restored = VCPContext.from_json(data)
        assert original == restored


class TestContextEncoder:
    """Test ContextEncoder class."""

    @pytest.fixture
    def encoder(self):
        """Create encoder instance."""
        return ContextEncoder()

    def test_encode_time(self, encoder):
        """Encode time context."""
        ctx = encoder.encode(time="morning")
        assert ctx.get(Dimension.TIME) == ["🌅"]

    def test_encode_space(self, encoder):
        """Encode space context."""
        ctx = encoder.encode(space="home")
        assert ctx.get(Dimension.SPACE) == ["🏡"]

    def test_encode_company_list(self, encoder):
        """Encode company as list."""
        ctx = encoder.encode(company=["children", "family"])
        values = ctx.get(Dimension.COMPANY)
        assert "👶" in values
        assert "👨‍👩‍👧" in values

    def test_encode_company_string(self, encoder):
        """Encode company as string."""
        ctx = encoder.encode(company="alone")
        assert ctx.get(Dimension.COMPANY) == ["👤"]

    def test_encode_multiple(self, encoder):
        """Encode multiple dimensions."""
        ctx = encoder.encode(
            time="morning",
            space="home",
            company=["children"],
            occasion="normal",
        )
        assert ctx.has(Dimension.TIME)
        assert ctx.has(Dimension.SPACE)
        assert ctx.has(Dimension.COMPANY)
        assert ctx.has(Dimension.OCCASION)

    def test_encode_invalid_value(self, encoder):
        """Unknown values should not be added."""
        ctx = encoder.encode(time="invalid_time")
        assert not ctx.has(Dimension.TIME)

    def test_encode_empty(self, encoder):
        """Encoding with no args returns empty context."""
        ctx = encoder.encode()
        assert not ctx

    def test_encode_state(self, encoder):
        """Encode mental state."""
        ctx = encoder.encode(state="happy")
        assert ctx.get(Dimension.STATE) == ["😊"]

    def test_encode_agency(self, encoder):
        """Encode agency level."""
        ctx = encoder.encode(agency="leader")
        assert ctx.get(Dimension.AGENCY) == ["👑"]

    def test_encode_constraints_list(self, encoder):
        """Encode constraints as list."""
        ctx = encoder.encode(constraints=["legal", "time"])
        values = ctx.get(Dimension.CONSTRAINTS)
        assert "⚖️" in values
        assert "⏱️" in values
