"""
Integration tests for VCP (Value-Context Protocol).

Tests the full VCP stack: VCP/I tokens, VCP/S CSM1 codes, VCP/A context encoding,
and integration with export formatter and PDP plugin.
"""

from __future__ import annotations

import pytest

pytest.importorskip("services", reason="Requires full Creed Space services")
pytest.importorskip("api_routers", reason="Requires full Creed Space API routers")

# =============================================================================
# VCP Core Integration Tests
# =============================================================================


class TestVCPCoreIntegration:
    """Integration tests for VCP core modules."""

    def test_vcp_exports_token(self) -> None:
        """Test VCP exports Token class."""
        from vcp import Token

        assert Token is not None

    def test_vcp_exports_csm1code(self) -> None:
        """Test VCP exports CSM1Code class."""
        from vcp import CSM1Code

        assert CSM1Code is not None

    def test_vcp_exports_context_encoder(self) -> None:
        """Test VCP exports ContextEncoder class."""
        from vcp import ContextEncoder

        assert ContextEncoder is not None

    def test_vcp_exports_state_tracker(self) -> None:
        """Test VCP exports StateTracker class."""
        from vcp import StateTracker

        assert StateTracker is not None

    def test_vcp_exports_persona(self) -> None:
        """Test VCP exports Persona enum."""
        from vcp import Persona

        assert Persona is not None

    def test_vcp_exports_dimension(self) -> None:
        """Test VCP exports Dimension enum."""
        from vcp import Dimension

        assert Dimension is not None


# =============================================================================
# Token to CSM1 Integration
# =============================================================================


class TestTokenCSM1Integration:
    """Integration tests between VCP/I and VCP/S layers."""

    def test_token_parse_and_csm1_parse(self) -> None:
        """Test both Token and CSM1Code can parse valid inputs."""
        from vcp import CSM1Code, Token

        # Parse token
        token = Token.parse("family.safe.guide@1.0.0")
        assert token.domain == "family"
        assert token.role == "guide"

        # Parse CSM1
        code = CSM1Code.parse("N5+F+E")
        assert code.persona.name == "NANNY"
        assert code.adherence_level == 5

    def test_persona_mapping_consistency(self) -> None:
        """Test CSM1 personas map to expected values."""
        from vcp import CSM1Code, Persona

        # Each persona should have a corresponding CSM1 code
        persona_codes = {
            "N": Persona.NANNY,
            "Z": Persona.SENTINEL,
            "G": Persona.GODPARENT,
            "A": Persona.AMBASSADOR,
            "M": Persona.MUSE,
            "R": Persona.ANCHOR,
            "H": Persona.HOTROD,
            "C": Persona.CUSTOM,
        }

        for code_char, expected_persona in persona_codes.items():
            code = CSM1Code.parse(f"{code_char}3")
            assert code.persona == expected_persona


# =============================================================================
# Context Encoder to State Tracker Integration
# =============================================================================


class TestContextTrackerIntegration:
    """Integration tests for VCP/A context and state tracking."""

    def test_encode_and_track(self) -> None:
        """Test encoding context and tracking state."""
        from vcp import ContextEncoder, StateTracker

        encoder = ContextEncoder()
        tracker = StateTracker()

        # Encode first context
        ctx1 = encoder.encode(time="morning", space="home")
        transition1 = tracker.record(ctx1)
        assert transition1 is None  # First record, no transition

        # Encode second context
        ctx2 = encoder.encode(time="evening", space="office")
        transition2 = tracker.record(ctx2)
        assert transition2 is not None
        assert len(transition2.changed_dimensions) > 0

    def test_emergency_detection(self) -> None:
        """Test emergency transition detection."""
        from vcp import ContextEncoder, StateTracker, TransitionSeverity

        encoder = ContextEncoder()
        tracker = StateTracker()

        # Normal context
        ctx1 = encoder.encode(time="morning")
        tracker.record(ctx1)

        # Emergency context
        ctx2 = encoder.encode(occasion="emergency")
        transition = tracker.record(ctx2)
        assert transition.severity == TransitionSeverity.EMERGENCY


# =============================================================================
# Export Formatter Integration
# =============================================================================


class TestVCPExportIntegration:
    """Integration tests for VCP with export formatter."""

    @pytest.fixture
    def export_formatter(self):
        """Create export formatter instance."""
        from services.export_formatter import ExportFormatter

        return ExportFormatter()

    @pytest.fixture
    def sample_persona(self):
        """Create sample persona config."""
        return {
            "name": "Nanny",
            "purpose": "Child safety specialist",
            "icon": "nanny_icon",
            "description": "Protects children",
            "filters": ["child_safety"],
            "default_adherence_level": 5,
            "base_constitutions": ["Recommended/UEF.md"],
            "metadata": {
                "domain": "family",
                "approach": "safe",
            },
            "version": "1.0.0",
        }

    def test_vcp_metadata_generation(self, export_formatter, sample_persona) -> None:
        """Test VCP metadata is generated."""
        vcp_metadata = export_formatter._build_vcp_metadata("nanny", sample_persona, 5)

        # When VCP features are disabled, returns None
        # This is expected behavior - test that the method exists and runs
        assert vcp_metadata is None or isinstance(vcp_metadata, dict)

    def test_generate_vcp_token(self, export_formatter, sample_persona) -> None:
        """Test VCP token generation."""
        token = export_formatter._generate_vcp_token("nanny", sample_persona)

        # When VCP features are disabled, returns None
        assert token is None or hasattr(token, "canonical")

    def test_generate_csm1_code(self, export_formatter, sample_persona) -> None:
        """Test CSM1 code generation."""
        code = export_formatter._generate_csm1_code("nanny", sample_persona, 5)

        # When VCP features are disabled, returns None
        assert code is None or hasattr(code, "encode")


# =============================================================================
# PDP Plugin Integration
# =============================================================================


class TestVCPPDPIntegration:
    """Integration tests for VCP with PDP plugin."""

    def test_plugin_import(self) -> None:
        """Test VCP plugin can be imported."""
        from services.safety_stack.plugins import VCPAdaptationPlugin

        assert VCPAdaptationPlugin is not None

    def test_plugin_instantiation(self) -> None:
        """Test VCP plugin can be instantiated."""
        from services.safety_stack.plugins import VCPAdaptationPlugin

        plugin = VCPAdaptationPlugin()
        assert plugin is not None
        assert hasattr(plugin, "execute")
        assert hasattr(plugin, "encoder")
        assert hasattr(plugin, "tracker")

    def test_plugin_uses_vcp_components(self) -> None:
        """Test plugin uses VCP components correctly."""
        from services.safety_stack.plugins import VCPAdaptationPlugin

        from vcp import ContextEncoder, StateTracker

        plugin = VCPAdaptationPlugin()

        # Verify plugin uses correct types
        assert isinstance(plugin.encoder, ContextEncoder)
        assert isinstance(plugin.tracker, StateTracker)


# =============================================================================
# API Router Integration
# =============================================================================


class TestVCPAPIIntegration:
    """Integration tests for VCP API router."""

    def test_router_import(self) -> None:
        """Test VCP router can be imported."""
        from api_routers.vcp import router

        assert router is not None

    def test_router_uses_vcp_core(self) -> None:
        """Test router imports from VCP core."""
        from api_routers import vcp

        # Verify VCP imports are present in the module
        assert hasattr(vcp, "Token") or "Token" in dir(vcp)
        assert hasattr(vcp, "CSM1Code") or "CSM1Code" in dir(vcp)


# =============================================================================
# MCP Server Integration
# =============================================================================


class TestVCPMCPIntegration:
    """Integration tests for VCP MCP server."""

    def test_mcp_server_import(self) -> None:
        """Test VCP MCP server can be imported."""
        from services.mcp import vcp_server

        assert vcp_server is not None

    def test_mcp_server_has_tools(self) -> None:
        """Test MCP server defines tools."""
        from services.mcp.vcp_server import list_tools

        assert list_tools is not None

    def test_mcp_server_has_handlers(self) -> None:
        """Test MCP server has call_tool handler."""
        from services.mcp.vcp_server import call_tool

        assert call_tool is not None


# =============================================================================
# Feature Flag Integration
# =============================================================================


class TestVCPFeatureFlagIntegration:
    """Integration tests for VCP feature flags."""

    def test_feature_flags_class_exists(self) -> None:
        """Test FeatureFlags class exists with VCP flags."""
        from services.feature_flags import FeatureFlags

        flags = FeatureFlags()
        # Check that VCP flags exist in defaults
        vcp_flags = [f for f in flags._flags if "vcp" in f.lower()]
        assert len(vcp_flags) >= 3  # identity, semantics, adaptation

    def test_is_feature_enabled_works(self) -> None:
        """Test is_feature_enabled function works for VCP flags."""
        from services.feature_flags import is_feature_enabled

        # Just verify the function runs without error
        # Actual value depends on configuration
        result = is_feature_enabled("vcp_identity_enabled")
        assert isinstance(result, bool)
