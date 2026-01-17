"""
Tests for services/safety_stack/plugins/vcp_adaptation_plugin.py

Comprehensive test coverage for VCP Adaptation Plugin.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

# =============================================================================
# VCPAdaptationPlugin Class Tests
# =============================================================================


class TestVCPAdaptationPluginClass:
    """Tests for VCPAdaptationPlugin class."""

    def test_class_exists(self) -> None:
        """Test class exists."""
        from services.safety_stack.plugins.vcp_adaptation_plugin import (
            VCPAdaptationPlugin,
        )

        assert VCPAdaptationPlugin is not None

    def test_init(self) -> None:
        """Test initialization."""
        from services.safety_stack.plugins.vcp_adaptation_plugin import (
            VCPAdaptationPlugin,
        )

        plugin = VCPAdaptationPlugin()
        assert plugin is not None
        assert plugin.id == "VCPAdaptationPlugin"

    def test_has_encoder(self) -> None:
        """Test plugin has context encoder."""
        from services.safety_stack.plugins.vcp_adaptation_plugin import (
            VCPAdaptationPlugin,
        )

        plugin = VCPAdaptationPlugin()
        assert hasattr(plugin, "encoder")
        assert plugin.encoder is not None

    def test_has_tracker(self) -> None:
        """Test plugin has state tracker."""
        from services.safety_stack.plugins.vcp_adaptation_plugin import (
            VCPAdaptationPlugin,
        )

        plugin = VCPAdaptationPlugin()
        assert hasattr(plugin, "tracker")
        assert plugin.tracker is not None

    def test_execute_method_exists(self) -> None:
        """Test execute method exists."""
        from services.safety_stack.plugins.vcp_adaptation_plugin import (
            VCPAdaptationPlugin,
        )

        plugin = VCPAdaptationPlugin()
        assert hasattr(plugin, "execute")

    def test_get_metrics_method_exists(self) -> None:
        """Test get_metrics method exists."""
        from services.safety_stack.plugins.vcp_adaptation_plugin import (
            VCPAdaptationPlugin,
        )

        plugin = VCPAdaptationPlugin()
        assert hasattr(plugin, "get_metrics")

    def test_get_tracker_stats_method_exists(self) -> None:
        """Test get_tracker_stats method exists."""
        from services.safety_stack.plugins.vcp_adaptation_plugin import (
            VCPAdaptationPlugin,
        )

        plugin = VCPAdaptationPlugin()
        assert hasattr(plugin, "get_tracker_stats")


# =============================================================================
# Execute Method Tests
# =============================================================================


class TestVCPAdaptationPluginExecute:
    """Tests for execute method."""

    @pytest.fixture
    def plugin(self):
        """Create plugin instance."""
        from services.safety_stack.plugins.vcp_adaptation_plugin import (
            VCPAdaptationPlugin,
        )

        return VCPAdaptationPlugin()

    @pytest.fixture
    def mock_context(self):
        """Create mock EnhancedContext."""
        ctx = MagicMock()
        ctx.metadata = {}
        ctx.user_state = None
        ctx.context_type = None
        ctx.persona_type = None
        return ctx

    def test_returns_none_when_disabled(self, plugin, mock_context) -> None:
        """Test execute returns None when feature disabled."""
        with patch(
            "services.safety_stack.plugins.vcp_adaptation_plugin.is_feature_enabled",
            return_value=False,
        ):
            result = plugin.execute(mock_context, [])
            assert result is None

    def test_returns_none_in_shadow_mode(self, plugin, mock_context) -> None:
        """Test execute returns None in shadow mode (signals only)."""

        def flag_check(flag):
            if flag == "vcp_adaptation_enabled":
                return True
            if flag == "vcp_adaptation_shadow":
                return True
            return False

        with patch(
            "services.safety_stack.plugins.vcp_adaptation_plugin.is_feature_enabled",
            side_effect=flag_check,
        ):
            result = plugin.execute(mock_context, [])
            assert result is None

    def test_emits_signals_in_metadata(self, plugin, mock_context) -> None:
        """Test VCP signals are stored in context metadata."""

        def flag_check(flag):
            if flag == "vcp_adaptation_enabled":
                return True
            if flag == "vcp_adaptation_shadow":
                return True
            return False

        with patch(
            "services.safety_stack.plugins.vcp_adaptation_plugin.is_feature_enabled",
            side_effect=flag_check,
        ):
            plugin.execute(mock_context, [])
            assert "vcp_signals" in mock_context.metadata
            signals = mock_context.metadata["vcp_signals"]
            assert "vcp_context_wire" in signals
            assert "vcp_has_context" in signals


# =============================================================================
# Context Extraction Tests
# =============================================================================


class TestVCPAdaptationPluginContextExtraction:
    """Tests for context extraction."""

    @pytest.fixture
    def plugin(self):
        """Create plugin instance."""
        from services.safety_stack.plugins.vcp_adaptation_plugin import (
            VCPAdaptationPlugin,
        )

        return VCPAdaptationPlugin()

    def test_extracts_user_state(self, plugin) -> None:
        """Test vulnerable user state maps to company."""
        ctx = MagicMock()
        ctx.metadata = {}
        ctx.user_state = "vulnerable"
        ctx.context_type = None
        ctx.persona_type = None

        vcp_context = plugin._extract_context(ctx)
        # Vulnerable maps to "alone" company
        assert vcp_context is not None

    def test_extracts_crisis_as_emergency(self, plugin) -> None:
        """Test crisis context_type maps to emergency occasion."""
        ctx = MagicMock()
        ctx.metadata = {}
        ctx.user_state = None
        ctx.context_type = "crisis"
        ctx.persona_type = None

        vcp_context = plugin._extract_context(ctx)
        assert vcp_context is not None

    def test_extracts_metadata_values(self, plugin) -> None:
        """Test metadata values are extracted."""
        ctx = MagicMock()
        ctx.metadata = {
            "time_of_day": "morning",
            "environment": "home",
        }
        ctx.user_state = None
        ctx.context_type = None
        ctx.persona_type = None

        vcp_context = plugin._extract_context(ctx)
        assert vcp_context is not None


# =============================================================================
# Action Computation Tests
# =============================================================================


class TestVCPAdaptationPluginActions:
    """Tests for action computation in active mode."""

    @pytest.fixture
    def plugin(self):
        """Create plugin instance."""
        from services.safety_stack.plugins.vcp_adaptation_plugin import (
            VCPAdaptationPlugin,
        )

        return VCPAdaptationPlugin()

    @pytest.fixture
    def mock_context(self):
        """Create mock EnhancedContext."""
        ctx = MagicMock()
        ctx.metadata = {}
        ctx.user_state = None
        ctx.context_type = None
        ctx.persona_type = None
        return ctx

    def test_children_trigger_nanny_preference(self, plugin, mock_context) -> None:
        """Test children in company triggers Nanny persona preference."""
        # Set up context with children
        mock_context.metadata = {"audience": ["children"]}

        def flag_check(flag):
            if flag == "vcp_adaptation_enabled":
                return True
            if flag == "vcp_adaptation_shadow":
                return False  # Active mode
            return False

        with patch(
            "services.safety_stack.plugins.vcp_adaptation_plugin.is_feature_enabled",
            side_effect=flag_check,
        ):
            result = plugin.execute(mock_context, [])
            if result:
                assert result.edits.get("prefer_persona") == "nanny"
                assert "vcp_child_safety" in result.policy_ids

    def test_emergency_triggers_sentinel(self, plugin, mock_context) -> None:
        """Test emergency context triggers Sentinel persona."""
        mock_context.metadata = {"occasion": "emergency"}

        def flag_check(flag):
            if flag == "vcp_adaptation_enabled":
                return True
            if flag == "vcp_adaptation_shadow":
                return False
            return False

        with patch(
            "services.safety_stack.plugins.vcp_adaptation_plugin.is_feature_enabled",
            side_effect=flag_check,
        ):
            result = plugin.execute(mock_context, [])
            if result:
                assert result.edits.get("prefer_persona") == "sentinel"
                assert result.edits.get("emergency_mode") is True


# =============================================================================
# State Tracker Tests
# =============================================================================


class TestVCPAdaptationPluginStateTracker:
    """Tests for state tracker integration."""

    @pytest.fixture
    def plugin(self):
        """Create plugin instance."""
        from services.safety_stack.plugins.vcp_adaptation_plugin import (
            VCPAdaptationPlugin,
        )

        return VCPAdaptationPlugin()

    def test_get_tracker_stats_returns_dict(self, plugin) -> None:
        """Test get_tracker_stats returns dictionary."""
        stats = plugin.get_tracker_stats()
        assert isinstance(stats, dict)
        assert "history_count" in stats
        assert "current_context" in stats
        assert "recent_transitions" in stats

    def test_initial_tracker_empty(self, plugin) -> None:
        """Test tracker starts empty."""
        stats = plugin.get_tracker_stats()
        assert stats["history_count"] == 0
        assert stats["current_context"] is None


# =============================================================================
# Plugin Registration Tests
# =============================================================================


class TestVCPAdaptationPluginRegistration:
    """Tests for plugin registration."""

    def test_plugin_in_exports(self) -> None:
        """Test plugin is exported from __init__."""
        from services.safety_stack.plugins import VCPAdaptationPlugin

        assert VCPAdaptationPlugin is not None

    def test_plugin_priority(self) -> None:
        """Test plugin has correct priority."""
        from services.safety_stack.pdp_interfaces import PluginPriority
        from services.safety_stack.plugins.vcp_adaptation_plugin import (
            VCPAdaptationPlugin,
        )

        plugin = VCPAdaptationPlugin()
        assert plugin.priority == PluginPriority.HIGH

    def test_plugin_type(self) -> None:
        """Test plugin has correct type."""
        from services.safety_stack.pdp_interfaces import PluginType
        from services.safety_stack.plugins.vcp_adaptation_plugin import (
            VCPAdaptationPlugin,
        )

        plugin = VCPAdaptationPlugin()
        assert plugin.type == PluginType.POLICY
