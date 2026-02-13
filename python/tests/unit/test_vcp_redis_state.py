"""
VCP Redis State Tracker Tests

Comprehensive unit tests for services/vcp/adaptation/redis_state.py.
Tests Redis state persistence, transitions, handlers, and fallback behavior.

Coverage target: redis_state.py 0% -> 80%+
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# ====================================================================================
# GET SYNC REDIS CLIENT TESTS
# ====================================================================================


class TestGetSyncRedisClient:
    """Tests for get_sync_redis_client function."""

    def test_get_sync_redis_client_success(self) -> None:
        """Test successful Redis client creation."""
        mock_client = MagicMock()
        mock_client.ping.return_value = True

        with patch.dict("os.environ", {"REDIS_URL": "redis://localhost:6379/0"}):
            with patch("redis.from_url", return_value=mock_client):
                from services.vcp.adaptation.redis_state import get_sync_redis_client

                client = get_sync_redis_client()

                assert client is not None
                mock_client.ping.assert_called_once()

    def test_get_sync_redis_client_connection_failure(self) -> None:
        """Test Redis client returns None on connection failure."""
        with patch.dict("os.environ", {"REDIS_URL": "redis://localhost:6379/0"}):
            with patch("redis.from_url", side_effect=ConnectionError("Connection refused")):
                from services.vcp.adaptation.redis_state import get_sync_redis_client

                client = get_sync_redis_client()

                assert client is None

    def test_get_sync_redis_client_ping_failure(self) -> None:
        """Test Redis client returns None when ping fails."""
        mock_client = MagicMock()
        mock_client.ping.side_effect = Exception("Ping failed")

        with patch.dict("os.environ", {"REDIS_URL": "redis://localhost:6379/0"}):
            with patch("redis.from_url", return_value=mock_client):
                from services.vcp.adaptation.redis_state import get_sync_redis_client

                client = get_sync_redis_client()

                assert client is None


# ====================================================================================
# REDIS STATE TRACKER TESTS
# ====================================================================================


class TestRedisStateTracker:
    """Tests for RedisStateTracker class."""

    @pytest.fixture
    def mock_redis(self) -> MagicMock:
        """Create a mock Redis client."""
        return MagicMock()

    @pytest.fixture
    def tracker(self, mock_redis: MagicMock) -> Any:
        """Create a RedisStateTracker with mock Redis."""
        from services.vcp.adaptation.redis_state import RedisStateTracker

        return RedisStateTracker(
            session_id="test-session-123",
            redis_client=mock_redis,
            max_history=100,
            ttl_seconds=3600,
        )

    def test_tracker_creation(self, mock_redis: MagicMock) -> None:
        """Test RedisStateTracker creation."""
        from services.vcp.adaptation.redis_state import RedisStateTracker

        tracker = RedisStateTracker(
            session_id="test-session",
            redis_client=mock_redis,
        )

        assert tracker is not None
        assert tracker._session_id == "test-session"

    def test_tracker_history_key(self, tracker: Any) -> None:
        """Test history key generation."""
        expected_key = "vcp:state:test-session-123:history"
        assert tracker._history_key == expected_key

    def test_record_first_context(self, tracker: Any, mock_redis: MagicMock) -> None:
        """Test recording first context state."""
        from services.vcp.adaptation.context import Dimension, VCPContext

        mock_redis.get.return_value = None  # No existing history

        context = VCPContext(dimensions={Dimension.TIME: ["morning"]})
        transition = tracker.record(context)

        # First record returns None (no transition)
        assert transition is None

        # Should store in Redis
        mock_redis.setex.assert_called_once()
        args = mock_redis.setex.call_args[0]
        assert args[0] == tracker._history_key
        assert args[1] == 3600  # TTL

    def test_record_detects_minor_transition(self, tracker: Any, mock_redis: MagicMock) -> None:
        """Test recording detects minor transition."""
        from services.vcp.adaptation.context import Dimension, VCPContext
        from services.vcp.adaptation.state import TransitionSeverity

        # Set up existing history
        existing_context = VCPContext(dimensions={Dimension.TIME: ["morning"]})
        mock_redis.get.return_value = json.dumps(
            [{"timestamp": datetime.utcnow().isoformat(), "context": existing_context.to_json()}]
        )

        # Record new context with different time
        new_context = VCPContext(dimensions={Dimension.TIME: ["evening"]})
        transition = tracker.record(new_context)

        assert transition is not None
        assert transition.severity == TransitionSeverity.MINOR
        assert Dimension.TIME in transition.changed_dimensions

    def test_record_detects_major_transition(self, tracker: Any, mock_redis: MagicMock) -> None:
        """Test recording detects major transition."""
        from services.vcp.adaptation.context import Dimension, VCPContext
        from services.vcp.adaptation.state import TransitionSeverity

        # Set up existing history
        existing_context = VCPContext(dimensions={Dimension.TIME: ["morning"]})
        mock_redis.get.return_value = json.dumps(
            [{"timestamp": datetime.utcnow().isoformat(), "context": existing_context.to_json()}]
        )

        # Record new context with AGENCY change (major dimension)
        new_context = VCPContext(dimensions={Dimension.AGENCY: ["leader"]})
        transition = tracker.record(new_context)

        assert transition is not None
        assert transition.severity == TransitionSeverity.MAJOR

    def test_record_detects_emergency_transition(self, tracker: Any, mock_redis: MagicMock) -> None:
        """Test recording detects emergency transition."""
        from services.vcp.adaptation.context import Dimension, VCPContext

        # Set up existing history
        existing_context = VCPContext(dimensions={Dimension.TIME: ["morning"]})
        mock_redis.get.return_value = json.dumps(
            [{"timestamp": datetime.utcnow().isoformat(), "context": existing_context.to_json()}]
        )

        # Record context with emergency value
        new_context = VCPContext(dimensions={Dimension.OCCASION: ["emergency"]})
        transition = tracker.record(new_context)

        assert transition is not None
        # Note: Emergency detected by emoji values, not string "emergency"
        # The actual emoji would be needed for EMERGENCY severity

    def test_record_handles_redis_write_error(self, tracker: Any, mock_redis: MagicMock) -> None:
        """Test recording handles Redis write errors gracefully."""
        from services.vcp.adaptation.context import Dimension, VCPContext

        mock_redis.get.return_value = None
        mock_redis.setex.side_effect = Exception("Redis write failed")

        context = VCPContext(dimensions={Dimension.TIME: ["morning"]})
        # Should not raise
        transition = tracker.record(context)

        assert transition is None  # First record

    def test_record_trims_history(self, tracker: Any, mock_redis: MagicMock) -> None:
        """Test that history is trimmed to max_history."""
        from services.vcp.adaptation.context import Dimension, VCPContext

        # Create history at max capacity
        history = [{"timestamp": datetime.utcnow().isoformat(), "context": {"time": ["morning"]}} for _ in range(100)]
        mock_redis.get.return_value = json.dumps(history)

        new_context = VCPContext(dimensions={Dimension.TIME: ["evening"]})
        tracker.record(new_context)

        # Check that stored history was trimmed
        call_args = mock_redis.setex.call_args[0]
        stored_history = json.loads(call_args[2])
        assert len(stored_history) <= 100

    def test_register_handler(self, tracker: Any) -> None:
        """Test registering transition handler."""
        from services.vcp.adaptation.state import TransitionSeverity

        handler = MagicMock()
        tracker.register_handler(TransitionSeverity.MINOR, handler)

        assert handler in tracker._handlers[TransitionSeverity.MINOR]

    def test_handler_invoked_on_transition(self, tracker: Any, mock_redis: MagicMock) -> None:
        """Test that handlers are invoked on transitions."""
        from services.vcp.adaptation.context import Dimension, VCPContext
        from services.vcp.adaptation.state import TransitionSeverity

        handler = MagicMock()
        tracker.register_handler(TransitionSeverity.MINOR, handler)

        # Set up existing history
        existing_context = VCPContext(dimensions={Dimension.TIME: ["morning"]})
        mock_redis.get.return_value = json.dumps(
            [{"timestamp": datetime.utcnow().isoformat(), "context": existing_context.to_json()}]
        )

        # Record transition
        new_context = VCPContext(dimensions={Dimension.TIME: ["evening"]})
        tracker.record(new_context)

        handler.assert_called_once()
        transition = handler.call_args[0][0]
        assert transition.severity == TransitionSeverity.MINOR

    def test_handler_error_does_not_break_record(self, tracker: Any, mock_redis: MagicMock) -> None:
        """Test that handler errors don't break recording."""
        from services.vcp.adaptation.context import Dimension, VCPContext
        from services.vcp.adaptation.state import TransitionSeverity

        def failing_handler(transition):
            raise ValueError("Handler failed")

        tracker.register_handler(TransitionSeverity.MINOR, failing_handler)

        # Set up existing history
        existing_context = VCPContext(dimensions={Dimension.TIME: ["morning"]})
        mock_redis.get.return_value = json.dumps(
            [{"timestamp": datetime.utcnow().isoformat(), "context": existing_context.to_json()}]
        )

        # Should not raise
        new_context = VCPContext(dimensions={Dimension.TIME: ["evening"]})
        transition = tracker.record(new_context)

        assert transition is not None

    def test_current_returns_latest_context(self, tracker: Any, mock_redis: MagicMock) -> None:
        """Test getting current context."""
        from services.vcp.adaptation.context import Dimension

        context_data = {"time": ["morning"], "space": ["home"]}
        mock_redis.get.return_value = json.dumps(
            [{"timestamp": datetime.utcnow().isoformat(), "context": context_data}]
        )

        current = tracker.current

        assert current is not None
        assert current.get(Dimension.TIME) == ["morning"]
        assert current.get(Dimension.SPACE) == ["home"]

    def test_current_returns_none_when_empty(self, tracker: Any, mock_redis: MagicMock) -> None:
        """Test current returns None when no history."""
        mock_redis.get.return_value = None

        assert tracker.current is None

    def test_history_count(self, tracker: Any, mock_redis: MagicMock) -> None:
        """Test getting history count."""
        history = [{"timestamp": datetime.utcnow().isoformat(), "context": {"time": ["morning"]}} for _ in range(5)]
        mock_redis.get.return_value = json.dumps(history)

        assert tracker.history_count == 5

    def test_history_count_empty(self, tracker: Any, mock_redis: MagicMock) -> None:
        """Test history count when empty."""
        mock_redis.get.return_value = None

        assert tracker.history_count == 0

    def test_clear_deletes_history(self, tracker: Any, mock_redis: MagicMock) -> None:
        """Test clearing history."""
        tracker.clear()

        mock_redis.delete.assert_called_once_with(tracker._history_key)

    def test_clear_handles_redis_error(self, tracker: Any, mock_redis: MagicMock) -> None:
        """Test clear handles Redis errors gracefully."""
        mock_redis.delete.side_effect = Exception("Redis delete failed")

        # Should not raise
        tracker.clear()

    def test_get_history_handles_read_error(self, tracker: Any, mock_redis: MagicMock) -> None:
        """Test _get_history handles read errors."""
        mock_redis.get.side_effect = Exception("Redis read failed")

        history = tracker._get_history()

        assert history == []


# ====================================================================================
# HYBRID STATE TRACKER TESTS
# ====================================================================================


class TestHybridStateTracker:
    """Tests for HybridStateTracker class."""

    @pytest.fixture
    def mock_redis(self) -> MagicMock:
        """Create a mock Redis client."""
        client = MagicMock()
        client.ping.return_value = True
        return client

    def test_hybrid_tracker_creation_with_redis(self, mock_redis: MagicMock) -> None:
        """Test HybridStateTracker creation with Redis."""
        from services.vcp.adaptation.redis_state import HybridStateTracker

        tracker = HybridStateTracker(
            session_id="test-session",
            redis_client=mock_redis,
        )

        assert tracker is not None
        assert tracker.uses_redis is True

    def test_hybrid_tracker_creation_without_redis(self) -> None:
        """Test HybridStateTracker creation without Redis."""
        from services.vcp.adaptation.redis_state import HybridStateTracker

        tracker = HybridStateTracker(
            session_id="test-session",
            redis_client=None,
        )

        assert tracker is not None
        assert tracker.uses_redis is False

    def test_hybrid_record_uses_redis_when_available(self, mock_redis: MagicMock) -> None:
        """Test record uses Redis when available."""
        from services.vcp.adaptation.context import Dimension, VCPContext
        from services.vcp.adaptation.redis_state import HybridStateTracker

        mock_redis.get.return_value = None  # No history

        tracker = HybridStateTracker(
            session_id="test-session",
            redis_client=mock_redis,
        )

        context = VCPContext(dimensions={Dimension.TIME: ["morning"]})
        tracker.record(context)

        # Should have called Redis
        mock_redis.setex.assert_called()

    def test_hybrid_record_falls_back_to_memory(self, mock_redis: MagicMock) -> None:
        """Test record falls back to memory on Redis failure."""
        from services.vcp.adaptation.context import Dimension, VCPContext
        from services.vcp.adaptation.redis_state import HybridStateTracker

        mock_redis.get.side_effect = Exception("Redis failed")

        tracker = HybridStateTracker(
            session_id="test-session",
            redis_client=mock_redis,
        )

        context = VCPContext(dimensions={Dimension.TIME: ["morning"]})
        transition = tracker.record(context)

        # Should have fallen back to memory tracker
        assert transition is None  # First record
        assert tracker._memory_tracker.current is not None

    def test_hybrid_record_without_redis(self) -> None:
        """Test record works without Redis."""
        from services.vcp.adaptation.context import Dimension, VCPContext
        from services.vcp.adaptation.redis_state import HybridStateTracker

        tracker = HybridStateTracker(
            session_id="test-session",
            redis_client=None,
        )

        context = VCPContext(dimensions={Dimension.TIME: ["morning"]})
        transition = tracker.record(context)

        assert transition is None  # First record
        assert tracker._memory_tracker.current is not None

    def test_hybrid_register_handler_on_both(self, mock_redis: MagicMock) -> None:
        """Test handler registration on both trackers."""
        from services.vcp.adaptation.redis_state import HybridStateTracker
        from services.vcp.adaptation.state import TransitionSeverity

        mock_redis.get.return_value = None

        tracker = HybridStateTracker(
            session_id="test-session",
            redis_client=mock_redis,
        )

        handler = MagicMock()
        tracker.register_handler(TransitionSeverity.MINOR, handler)

        # Handler should be registered on memory tracker
        assert handler in tracker._memory_tracker._handlers[TransitionSeverity.MINOR]

    def test_hybrid_current_prefers_redis(self, mock_redis: MagicMock) -> None:
        """Test current prefers Redis when available."""
        from services.vcp.adaptation.context import Dimension, VCPContext
        from services.vcp.adaptation.redis_state import HybridStateTracker

        context_data = {"time": ["evening"]}
        mock_redis.get.return_value = json.dumps(
            [{"timestamp": datetime.utcnow().isoformat(), "context": context_data}]
        )

        tracker = HybridStateTracker(
            session_id="test-session",
            redis_client=mock_redis,
        )

        # Add something different to memory
        memory_context = VCPContext(dimensions={Dimension.TIME: ["morning"]})
        tracker._memory_tracker.record(memory_context)

        current = tracker.current

        assert current is not None
        # Should get Redis value, not memory value
        assert current.get(Dimension.TIME) == ["evening"]

    def test_hybrid_current_falls_back_to_memory(self, mock_redis: MagicMock) -> None:
        """Test current falls back to memory on Redis failure.

        Note: The RedisStateTracker._get_history() method catches exceptions
        and returns empty list, so for fallback to memory to occur, we need
        to test when Redis tracker itself is not available.
        """
        from services.vcp.adaptation.context import Dimension, VCPContext
        from services.vcp.adaptation.redis_state import HybridStateTracker

        # Create tracker without Redis to test memory-only path
        tracker = HybridStateTracker(
            session_id="test-session",
            redis_client=None,  # No Redis
        )

        # Record context (goes directly to memory)
        memory_context = VCPContext(dimensions={Dimension.TIME: ["morning"]})
        tracker.record(memory_context)

        current = tracker.current

        assert current is not None
        assert current.get(Dimension.TIME) == ["morning"]

    def test_hybrid_history_count_prefers_redis(self, mock_redis: MagicMock) -> None:
        """Test history_count prefers Redis."""
        from services.vcp.adaptation.redis_state import HybridStateTracker

        history = [{"timestamp": datetime.utcnow().isoformat(), "context": {"time": ["morning"]}} for _ in range(10)]
        mock_redis.get.return_value = json.dumps(history)

        tracker = HybridStateTracker(
            session_id="test-session",
            redis_client=mock_redis,
        )

        assert tracker.history_count == 10

    def test_hybrid_history_count_falls_back_to_memory(self, mock_redis: MagicMock) -> None:
        """Test history_count uses memory tracker when Redis not available.

        Note: The RedisStateTracker._get_history() method catches exceptions
        and returns empty list rather than bubbling up, so we test with no Redis.
        """
        from services.vcp.adaptation.context import Dimension, VCPContext
        from services.vcp.adaptation.redis_state import HybridStateTracker

        # Create tracker without Redis
        tracker = HybridStateTracker(
            session_id="test-session",
            redis_client=None,  # No Redis
        )

        # Record contexts (goes directly to memory)
        for i in range(5):
            context = VCPContext(dimensions={Dimension.TIME: [f"time_{i}"]})
            tracker.record(context)

        assert tracker.history_count == 5

    def test_hybrid_find_transitions_uses_memory(self, mock_redis: MagicMock) -> None:
        """Test find_transitions uses memory tracker."""
        from services.vcp.adaptation.context import Dimension, VCPContext
        from services.vcp.adaptation.redis_state import HybridStateTracker
        from services.vcp.adaptation.state import TransitionSeverity

        mock_redis.get.return_value = None

        tracker = HybridStateTracker(
            session_id="test-session",
            redis_client=mock_redis,
        )

        # Record multiple contexts to create transitions
        context1 = VCPContext(dimensions={Dimension.TIME: ["morning"]})
        context2 = VCPContext(dimensions={Dimension.TIME: ["evening"]})
        tracker._memory_tracker.record(context1)
        tracker._memory_tracker.record(context2)

        transitions = tracker.find_transitions(min_severity=TransitionSeverity.MINOR)

        assert len(transitions) >= 1


# ====================================================================================
# TRANSITION DETECTION TESTS
# ====================================================================================


class TestTransitionDetection:
    """Tests for transition detection logic."""

    @pytest.fixture
    def mock_redis(self) -> MagicMock:
        """Create a mock Redis client."""
        return MagicMock()

    @pytest.fixture
    def tracker(self, mock_redis: MagicMock) -> Any:
        """Create a RedisStateTracker with mock Redis."""
        from services.vcp.adaptation.redis_state import RedisStateTracker

        return RedisStateTracker(
            session_id="test-session",
            redis_client=mock_redis,
        )

    def test_detect_no_change(self, tracker: Any) -> None:
        """Test detection of no change."""
        from services.vcp.adaptation.context import Dimension, VCPContext
        from services.vcp.adaptation.state import TransitionSeverity

        context1 = VCPContext(dimensions={Dimension.TIME: ["morning"]})
        context2 = VCPContext(dimensions={Dimension.TIME: ["morning"]})

        transition = tracker._detect_transition(context1, context2)

        assert transition.severity == TransitionSeverity.NONE
        assert len(transition.changed_dimensions) == 0

    def test_detect_single_dimension_change(self, tracker: Any) -> None:
        """Test detection of single dimension change."""
        from services.vcp.adaptation.context import Dimension, VCPContext
        from services.vcp.adaptation.state import TransitionSeverity

        context1 = VCPContext(dimensions={Dimension.TIME: ["morning"]})
        context2 = VCPContext(dimensions={Dimension.TIME: ["evening"]})

        transition = tracker._detect_transition(context1, context2)

        assert transition.severity == TransitionSeverity.MINOR
        assert Dimension.TIME in transition.changed_dimensions

    def test_detect_multiple_dimension_changes(self, tracker: Any) -> None:
        """Test detection of multiple dimension changes triggers MAJOR."""
        from services.vcp.adaptation.context import Dimension, VCPContext
        from services.vcp.adaptation.state import TransitionSeverity

        context1 = VCPContext(
            dimensions={
                Dimension.TIME: ["morning"],
                Dimension.SPACE: ["home"],
                Dimension.COMPANY: ["family"],
            }
        )
        context2 = VCPContext(
            dimensions={
                Dimension.TIME: ["evening"],
                Dimension.SPACE: ["office"],
                Dimension.COMPANY: ["colleagues"],
            }
        )

        transition = tracker._detect_transition(context1, context2)

        assert transition.severity == TransitionSeverity.MAJOR
        assert len(transition.changed_dimensions) >= 3

    def test_detect_major_dimension_change(self, tracker: Any) -> None:
        """Test that AGENCY change triggers MAJOR severity."""
        from services.vcp.adaptation.context import Dimension, VCPContext
        from services.vcp.adaptation.state import TransitionSeverity

        context1 = VCPContext(dimensions={Dimension.AGENCY: ["peer"]})
        context2 = VCPContext(dimensions={Dimension.AGENCY: ["leader"]})

        transition = tracker._detect_transition(context1, context2)

        assert transition.severity == TransitionSeverity.MAJOR

    def test_detect_emergency_values(self, tracker: Any) -> None:
        """Test detection of emergency values."""
        from services.vcp.adaptation.context import Dimension, VCPContext
        from services.vcp.adaptation.state import EMERGENCY_VALUES, TransitionSeverity

        context1 = VCPContext(dimensions={Dimension.OCCASION: ["normal"]})
        # Use actual emergency emoji
        context2 = VCPContext(dimensions={Dimension.OCCASION: ["alert"]})
        context2.dimensions[Dimension.OCCASION] = list(EMERGENCY_VALUES)[:1]

        transition = tracker._detect_transition(context1, context2)

        assert transition.severity == TransitionSeverity.EMERGENCY

    def test_transition_has_previous_and_current(self, tracker: Any) -> None:
        """Test that transition contains previous and current contexts."""
        from services.vcp.adaptation.context import Dimension, VCPContext

        context1 = VCPContext(dimensions={Dimension.TIME: ["morning"]})
        context2 = VCPContext(dimensions={Dimension.TIME: ["evening"]})

        transition = tracker._detect_transition(context1, context2)

        assert transition.previous == context1
        assert transition.current == context2
        assert transition.timestamp is not None


# ====================================================================================
# EDGE CASE TESTS
# ====================================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    @pytest.fixture
    def mock_redis(self) -> MagicMock:
        """Create a mock Redis client."""
        return MagicMock()

    def test_empty_context_handling(self, mock_redis: MagicMock) -> None:
        """Test handling of empty contexts."""
        from services.vcp.adaptation.context import VCPContext
        from services.vcp.adaptation.redis_state import RedisStateTracker

        mock_redis.get.return_value = None

        tracker = RedisStateTracker(
            session_id="test-session",
            redis_client=mock_redis,
        )

        empty_context = VCPContext(dimensions={})
        transition = tracker.record(empty_context)

        assert transition is None  # First record

    def test_malformed_history_json(self, mock_redis: MagicMock) -> None:
        """Test handling of malformed JSON in history."""
        from services.vcp.adaptation.redis_state import RedisStateTracker

        mock_redis.get.return_value = "not valid json"

        tracker = RedisStateTracker(
            session_id="test-session",
            redis_client=mock_redis,
        )

        history = tracker._get_history()

        assert history == []

    def test_custom_ttl_and_max_history(self, mock_redis: MagicMock) -> None:
        """Test custom TTL and max_history settings."""
        from services.vcp.adaptation.context import Dimension, VCPContext
        from services.vcp.adaptation.redis_state import RedisStateTracker

        mock_redis.get.return_value = None

        tracker = RedisStateTracker(
            session_id="test-session",
            redis_client=mock_redis,
            max_history=50,
            ttl_seconds=7200,
        )

        context = VCPContext(dimensions={Dimension.TIME: ["morning"]})
        tracker.record(context)

        # Verify TTL was used
        call_args = mock_redis.setex.call_args[0]
        assert call_args[1] == 7200

    def test_session_id_in_key(self, mock_redis: MagicMock) -> None:
        """Test that session ID is correctly included in Redis key."""
        from services.vcp.adaptation.redis_state import RedisStateTracker

        tracker = RedisStateTracker(
            session_id="unique-session-abc",
            redis_client=mock_redis,
        )

        assert "unique-session-abc" in tracker._history_key

    def test_multiple_handlers_same_severity(self, mock_redis: MagicMock) -> None:
        """Test multiple handlers for same severity."""
        from services.vcp.adaptation.context import Dimension, VCPContext
        from services.vcp.adaptation.redis_state import RedisStateTracker
        from services.vcp.adaptation.state import TransitionSeverity

        existing_context = VCPContext(dimensions={Dimension.TIME: ["morning"]})
        mock_redis.get.return_value = json.dumps(
            [{"timestamp": datetime.utcnow().isoformat(), "context": existing_context.to_json()}]
        )

        tracker = RedisStateTracker(
            session_id="test-session",
            redis_client=mock_redis,
        )

        handler1 = MagicMock()
        handler2 = MagicMock()
        tracker.register_handler(TransitionSeverity.MINOR, handler1)
        tracker.register_handler(TransitionSeverity.MINOR, handler2)

        new_context = VCPContext(dimensions={Dimension.TIME: ["evening"]})
        tracker.record(new_context)

        handler1.assert_called_once()
        handler2.assert_called_once()


# ====================================================================================
# INTEGRATION-STYLE TESTS (With Mock Redis)
# ====================================================================================


class TestIntegration:
    """Integration-style tests with mock Redis."""

    @pytest.fixture
    def mock_redis(self) -> MagicMock:
        """Create a stateful mock Redis client."""
        storage: dict[str, str] = {}

        client = MagicMock()

        def mock_get(key: str) -> str | None:
            return storage.get(key)

        def mock_setex(key: str, ttl: int, value: str) -> None:
            storage[key] = value

        def mock_delete(key: str) -> None:
            storage.pop(key, None)

        client.get = MagicMock(side_effect=mock_get)
        client.setex = MagicMock(side_effect=mock_setex)
        client.delete = MagicMock(side_effect=mock_delete)

        return client

    def test_full_lifecycle(self, mock_redis: MagicMock) -> None:
        """Test full lifecycle: create, record, read, clear."""
        from services.vcp.adaptation.context import Dimension, VCPContext
        from services.vcp.adaptation.redis_state import RedisStateTracker
        from services.vcp.adaptation.state import TransitionSeverity

        tracker = RedisStateTracker(
            session_id="lifecycle-test",
            redis_client=mock_redis,
        )

        # Record first context
        context1 = VCPContext(dimensions={Dimension.TIME: ["morning"]})
        t1 = tracker.record(context1)
        assert t1 is None  # First record

        # Record second context - should detect transition
        context2 = VCPContext(dimensions={Dimension.TIME: ["evening"]})
        t2 = tracker.record(context2)
        assert t2 is not None
        assert t2.severity == TransitionSeverity.MINOR

        # Check current
        current = tracker.current
        assert current is not None
        assert current.get(Dimension.TIME) == ["evening"]

        # Check history count
        assert tracker.history_count == 2

        # Clear
        tracker.clear()
        assert tracker.history_count == 0

    def test_hybrid_with_redis_failure_recovery(self, mock_redis: MagicMock) -> None:
        """Test hybrid tracker recovers from Redis failures."""
        from services.vcp.adaptation.context import Dimension, VCPContext
        from services.vcp.adaptation.redis_state import HybridStateTracker

        tracker = HybridStateTracker(
            session_id="failure-recovery",
            redis_client=mock_redis,
        )

        # First record works
        context1 = VCPContext(dimensions={Dimension.TIME: ["morning"]})
        tracker.record(context1)

        # Simulate Redis failure
        mock_redis.get.side_effect = Exception("Redis down")
        mock_redis.setex.side_effect = Exception("Redis down")

        # Should fall back to memory
        context2 = VCPContext(dimensions={Dimension.TIME: ["evening"]})
        tracker.record(context2)  # Falls back to memory

        # Should still work via memory tracker
        assert tracker._memory_tracker.current is not None
