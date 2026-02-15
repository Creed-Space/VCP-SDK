"""
VCP/A Redis-backed State Tracking.

Provides persistent state tracking across multiple workers via Redis.
Falls back to in-memory StateTracker if Redis is unavailable.

Uses sync Redis client since PDP plugins run in sync context.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Callable
from datetime import datetime
from typing import TYPE_CHECKING, Any, cast

from .context import Dimension, VCPContext
from .state import EMERGENCY_VALUES, MAJOR_DIMENSIONS, StateTracker, Transition, TransitionSeverity

if TYPE_CHECKING:
    import redis

logger = logging.getLogger(__name__)


def get_sync_redis_client() -> redis.Redis | None:
    """Get sync Redis client for VCP state persistence.

    Returns:
        Sync Redis client or None if unavailable
    """
    try:
        import os

        import redis as redis_sync

        redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
        client = cast(
            "redis.Redis",
            redis_sync.from_url(redis_url, decode_responses=True),
        )
        # Test connection
        client.ping()
        return client
    except Exception as e:
        logger.debug(f"VCP: Sync Redis unavailable: {e}")
        return None


class RedisStateTracker:
    """Redis-backed state tracker for multi-worker persistence.

    Stores context history in Redis with TTL. Transition detection
    and handlers work the same as in-memory StateTracker.

    Uses SYNC Redis operations since PDP plugins run in sync context.
    Thread-safety: Redis operations are atomic. Local handlers
    are not thread-safe but are per-instance.
    """

    # Redis key prefix
    KEY_PREFIX = "vcp:state"

    def __init__(
        self,
        session_id: str,
        redis_client: redis.Redis,
        max_history: int = 100,
        ttl_seconds: int = 3600,
    ):
        """Initialize Redis state tracker.

        Args:
            session_id: Session identifier for key scoping
            redis_client: Sync Redis client
            max_history: Maximum history entries to keep
            ttl_seconds: TTL for Redis keys
        """
        self._session_id = session_id
        self._redis = redis_client
        self._max_history = max_history
        self._ttl_seconds = ttl_seconds
        self._handlers: dict[TransitionSeverity, list[Callable[[Transition], None]]] = {
            s: [] for s in TransitionSeverity
        }

    @property
    def _history_key(self) -> str:
        """Redis key for history storage."""
        return f"{self.KEY_PREFIX}:{self._session_id}:history"

    def record(self, context: VCPContext) -> Transition | None:
        """Record new context state, return transition if any.

        Args:
            context: New context state

        Returns:
            Transition if state changed, None if first record or no change
        """
        now = datetime.utcnow()
        now_iso = now.isoformat()

        # Get current history from Redis
        history = self._get_history()

        if not history:
            # First record - just store it
            entry = {"timestamp": now_iso, "context": context.to_json()}
            try:
                self._redis.setex(
                    self._history_key,
                    self._ttl_seconds,
                    json.dumps([entry]),
                )
            except Exception as e:
                logger.warning(f"VCP Redis write error on initial record: {type(e).__name__}: {e}")
            return None

        # Detect transition from previous
        previous_ctx = VCPContext.from_json(history[-1]["context"])
        transition = self._detect_transition(previous_ctx, context)

        # Append new entry
        entry = {"timestamp": now_iso, "context": context.to_json()}
        history.append(entry)

        # Trim if needed
        if len(history) > self._max_history:
            history = history[-self._max_history :]

        # Store back to Redis with TTL refresh
        try:
            self._redis.setex(
                self._history_key,
                self._ttl_seconds,
                json.dumps(history),
            )
        except Exception as e:
            logger.warning(f"VCP Redis write error during history update: {type(e).__name__}: {e}")

        # Invoke handlers (local only)
        if transition.severity != TransitionSeverity.NONE:
            for handler in self._handlers[transition.severity]:
                try:
                    handler(transition)
                except Exception as e:
                    logger.warning(f"VCP transition handler error: {e}")

        return transition

    def _get_history(self) -> list[dict[str, Any]]:
        """Get history from Redis.

        Returns:
            List of {timestamp, context} dicts
        """
        try:
            data = cast("str | None", self._redis.get(self._history_key))
            if data:
                result: list[dict[str, Any]] = json.loads(data)
                return result
        except Exception as e:
            logger.warning(f"VCP Redis history read error: {e}")
        return []

    def _detect_transition(
        self,
        previous: VCPContext,
        current: VCPContext,
    ) -> Transition:
        """Detect transition between two contexts.

        Args:
            previous: Previous context state
            current: Current context state

        Returns:
            Transition describing the change
        """
        changed: list[Dimension] = []

        for dim in Dimension:
            prev_vals = set(previous.get(dim))
            curr_vals = set(current.get(dim))
            if prev_vals != curr_vals:
                changed.append(dim)

        # Check for emergency values
        all_current_values: set[str] = set()
        for vals in current.dimensions.values():
            all_current_values.update(vals)

        # Determine severity
        if all_current_values & EMERGENCY_VALUES:
            severity = TransitionSeverity.EMERGENCY
        elif any(d in MAJOR_DIMENSIONS for d in changed) or len(changed) >= 3:
            severity = TransitionSeverity.MAJOR
        elif changed:
            severity = TransitionSeverity.MINOR
        else:
            severity = TransitionSeverity.NONE

        return Transition(
            severity=severity,
            changed_dimensions=changed,
            previous=previous,
            current=current,
            timestamp=datetime.utcnow(),
        )

    def register_handler(
        self,
        severity: TransitionSeverity,
        handler: Callable[[Transition], None],
    ) -> None:
        """Register a transition handler (local only).

        Args:
            severity: Severity level to handle
            handler: Function to call with transition
        """
        self._handlers[severity].append(handler)

    @property
    def current(self) -> VCPContext | None:
        """Get current context.

        Returns:
            Current context or None if no history
        """
        history = self._get_history()
        if history:
            return VCPContext.from_json(history[-1]["context"])
        return None

    @property
    def history_count(self) -> int:
        """Get number of history entries."""
        return len(self._get_history())

    def clear(self) -> None:
        """Clear all history."""
        try:
            self._redis.delete(self._history_key)
        except Exception as e:
            logger.warning(f"VCP Redis delete error: {e}")


class HybridStateTracker:
    """State tracker that uses Redis when available, falls back to in-memory.

    Provides a unified sync interface. Redis is used for cross-worker
    persistence; memory tracker provides immediate response.
    """

    def __init__(
        self,
        session_id: str,
        redis_client: redis.Redis | None = None,
        max_history: int = 100,
        ttl_seconds: int = 3600,
    ):
        """Initialize hybrid tracker.

        Args:
            session_id: Session identifier
            redis_client: Optional sync Redis client
            max_history: Maximum history entries
            ttl_seconds: TTL for Redis keys
        """
        self._session_id = session_id
        self._max_history = max_history
        self._ttl_seconds = ttl_seconds

        # In-memory for immediate response (always available)
        self._memory_tracker = StateTracker(max_history=max_history)

        # Redis tracker for persistence (optional)
        self._redis_tracker: RedisStateTracker | None = None
        if redis_client:
            self._redis_tracker = RedisStateTracker(
                session_id=session_id,
                redis_client=redis_client,
                max_history=max_history,
                ttl_seconds=ttl_seconds,
            )

    def record(self, context: VCPContext) -> Transition | None:
        """Record context state.

        Writes to Redis for cross-worker persistence, uses memory
        tracker for immediate response.

        Args:
            context: New context state

        Returns:
            Transition if state changed
        """
        # Try Redis first for cross-worker persistence
        if self._redis_tracker:
            try:
                transition = self._redis_tracker.record(context)
                # Also record to memory for handler invocation
                self._memory_tracker.record(context)
                return transition
            except Exception as e:
                logger.warning(f"VCP Redis record failed, using memory: {e}")

        # Memory-only fallback
        return self._memory_tracker.record(context)

    def register_handler(
        self,
        severity: TransitionSeverity,
        handler: Callable[[Transition], None],
    ) -> None:
        """Register handler on both trackers."""
        self._memory_tracker.register_handler(severity, handler)
        if self._redis_tracker:
            self._redis_tracker.register_handler(severity, handler)

    @property
    def current(self) -> VCPContext | None:
        """Get current context (prefer Redis for cross-worker consistency)."""
        if self._redis_tracker:
            try:
                return self._redis_tracker.current
            except Exception as e:
                logger.warning(
                    "Failed to get current context from Redis: "
                    f"{type(e).__name__}: {e}. Using memory fallback."
                )
        return self._memory_tracker.current

    @property
    def history_count(self) -> int:
        """Get history count (prefer Redis for cross-worker consistency)."""
        if self._redis_tracker:
            try:
                return self._redis_tracker.history_count
            except Exception as e:
                logger.warning(
                    "Failed to get history count from Redis: "
                    f"{type(e).__name__}: {e}. Using memory fallback."
                )
        return self._memory_tracker.history_count

    def find_transitions(
        self,
        min_severity: TransitionSeverity = TransitionSeverity.MINOR,
    ) -> list[Transition]:
        """Find transitions in memory history."""
        return self._memory_tracker.find_transitions(min_severity)

    @property
    def uses_redis(self) -> bool:
        """Check if Redis persistence is active."""
        return self._redis_tracker is not None
