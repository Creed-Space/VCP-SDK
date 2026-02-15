"""
Tests for api_routers/vcp.py

Comprehensive test coverage for VCP API router.
"""

from __future__ import annotations

import pytest

pytest.importorskip("api_routers", reason="Requires full Creed Space API routers")

# =============================================================================
# Pydantic Model Tests
# =============================================================================


class TestTokenValidateRequestModel:
    """Tests for TokenValidateRequest Pydantic model."""

    def test_valid_request(self) -> None:
        """Test creating valid token validation request."""
        from api_routers.vcp import TokenValidateRequest

        model = TokenValidateRequest(token="family.safe.guide@1.2.0")
        assert model.token == "family.safe.guide@1.2.0"

    def test_minimal_token(self) -> None:
        """Test creating request with minimal token."""
        from api_routers.vcp import TokenValidateRequest

        model = TokenValidateRequest(token="a.b.c")
        assert model.token == "a.b.c"


class TestTokenValidateResponseModel:
    """Tests for TokenValidateResponse Pydantic model."""

    def test_valid_response(self) -> None:
        """Test creating valid token response."""
        from api_routers.vcp import TokenValidateResponse

        model = TokenValidateResponse(
            valid=True,
            canonical="family.safe.guide",
            domain="family",
            approach="safe",
            role="guide",
            version="1.2.0",
            uri="creed://creed.space/family.safe.guide@1.2.0",
        )
        assert model.valid is True
        assert model.domain == "family"

    def test_invalid_response(self) -> None:
        """Test creating invalid token response."""
        from api_routers.vcp import TokenValidateResponse

        model = TokenValidateResponse(
            valid=False,
            error="Invalid format",
        )
        assert model.valid is False
        assert model.error == "Invalid format"


class TestCSM1ParseRequestModel:
    """Tests for CSM1ParseRequest Pydantic model."""

    def test_valid_request(self) -> None:
        """Test creating valid CSM1 parse request."""
        from api_routers.vcp import CSM1ParseRequest

        model = CSM1ParseRequest(code="N5+F+E")
        assert model.code == "N5+F+E"

    def test_minimal_code(self) -> None:
        """Test creating request with minimal code."""
        from api_routers.vcp import CSM1ParseRequest

        model = CSM1ParseRequest(code="N5")
        assert model.code == "N5"


class TestCSM1ParseResponseModel:
    """Tests for CSM1ParseResponse Pydantic model."""

    def test_valid_response(self) -> None:
        """Test creating valid CSM1 response."""
        from api_routers.vcp import CSM1ParseResponse

        model = CSM1ParseResponse(
            valid=True,
            persona="NANNY",
            persona_description="Child safety specialist",
            adherence_level=5,
            scopes=["FAMILY", "EDUCATION"],
            encoded="N5+F+E",
        )
        assert model.valid is True
        assert model.persona == "NANNY"
        assert model.adherence_level == 5

    def test_invalid_response(self) -> None:
        """Test creating invalid CSM1 response."""
        from api_routers.vcp import CSM1ParseResponse

        model = CSM1ParseResponse(
            valid=False,
            error="Invalid CSM1 code",
        )
        assert model.valid is False


class TestContextEncodeRequestModel:
    """Tests for ContextEncodeRequest Pydantic model."""

    def test_full_request(self) -> None:
        """Test creating full context encode request."""
        from api_routers.vcp import ContextEncodeRequest

        model = ContextEncodeRequest(
            time="morning",
            space="home",
            company=["children", "family"],
            occasion="normal",
            state="happy",
            agency="leader",
        )
        assert model.time == "morning"
        assert model.company == ["children", "family"]

    def test_minimal_request(self) -> None:
        """Test creating minimal request."""
        from api_routers.vcp import ContextEncodeRequest

        model = ContextEncodeRequest()
        assert model.time is None
        assert model.space is None


class TestContextEncodeResponseModel:
    """Tests for ContextEncodeResponse Pydantic model."""

    def test_valid_response(self) -> None:
        """Test creating valid context encode response."""
        from api_routers.vcp import ContextEncodeResponse

        model = ContextEncodeResponse(
            wire_format="⏰🌅|📍🏡",
            json_format={"time": ["🌅"], "space": ["🏡"]},
            dimensions_set=["time", "space"],
        )
        assert "⏰" in model.wire_format
        assert len(model.dimensions_set) == 2


class TestPersonaInfoModel:
    """Tests for PersonaInfo Pydantic model."""

    def test_valid_persona(self) -> None:
        """Test creating valid persona info."""
        from api_routers.vcp import PersonaInfo

        model = PersonaInfo(
            code="N",
            name="NANNY",
            description="Child safety specialist",
        )
        assert model.code == "N"
        assert model.name == "NANNY"


class TestVCPStatusResponseModel:
    """Tests for VCPStatusResponse Pydantic model."""

    def test_valid_response(self) -> None:
        """Test creating valid status response."""
        from api_routers.vcp import VCPStatusResponse

        model = VCPStatusResponse(
            vcp_identity_enabled=True,
            vcp_semantics_enabled=True,
            vcp_adaptation_enabled=False,
            vcp_full_stack_enabled=False,
            vcp_strict_mode=False,
            version="2.0.0",
        )
        assert model.vcp_identity_enabled is True
        assert model.version == "2.0.0"


# =============================================================================
# Router Configuration Tests
# =============================================================================


class TestVCPRouterConfiguration:
    """Tests for VCP router configuration."""

    def test_router_exists(self) -> None:
        """Test router is defined."""
        from api_routers.vcp import router

        assert router is not None

    def test_router_prefix(self) -> None:
        """Test router has correct prefix."""
        from api_routers.vcp import router

        assert router.prefix == "/api/vcp"

    def test_router_tags(self) -> None:
        """Test router has correct tags."""
        from api_routers.vcp import router

        assert "vcp" in router.tags


# =============================================================================
# Endpoint Existence Tests
# =============================================================================


class TestVCPRouterEndpoints:
    """Tests for VCP router endpoint functions."""

    def test_validate_token_exists(self) -> None:
        """Test validate_token endpoint exists."""
        from api_routers.vcp import validate_token

        assert validate_token is not None

    def test_parse_csm1_exists(self) -> None:
        """Test parse_csm1 endpoint exists."""
        from api_routers.vcp import parse_csm1

        assert parse_csm1 is not None

    def test_encode_context_exists(self) -> None:
        """Test encode_context endpoint exists."""
        from api_routers.vcp import encode_context

        assert encode_context is not None

    def test_list_personas_exists(self) -> None:
        """Test list_personas endpoint exists."""
        from api_routers.vcp import list_personas

        assert list_personas is not None

    def test_list_dimensions_exists(self) -> None:
        """Test list_dimensions endpoint exists."""
        from api_routers.vcp import list_dimensions

        assert list_dimensions is not None

    def test_vcp_status_exists(self) -> None:
        """Test vcp_status endpoint exists."""
        from api_routers.vcp import vcp_status

        assert vcp_status is not None


# =============================================================================
# Route Count Tests
# =============================================================================


class TestVCPRouterRoutes:
    """Tests for VCP router routes."""

    def test_has_expected_routes(self) -> None:
        """Test router has expected number of routes."""
        from api_routers.vcp import router

        # 6 endpoints: validate_token, parse_csm1, encode_context,
        # list_personas, list_dimensions, vcp_status
        assert len(router.routes) >= 6
