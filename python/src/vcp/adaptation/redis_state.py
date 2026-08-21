"""
VCP/A Redis-backed State Tracking.

Provides persistent state tracking across multiple workers via Redis.
Falls back to in-memory StateTracker if Redis is unavailable.

Uses sync Redis client since PDP plugins run in sync context.
"""

from __future__ import annotations

import json
import logging
import threading
from collections.abc import Callable
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

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
        client = redis_sync.Redis.from_url(redis_url, decode_responses=True)
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
    Official Redis clients use WATCH/MULTI optimistic transactions so a
    concurrent writer is retried instead of overwritten. Local handler
    registration and invocation are protected by an instance lock.
    """

    # Redis key prefix
    KEY_PREFIX = "vcp:state"
    MAX_TRANSACTION_RETRIES = 16

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
        if not isinstance(session_id, str) or not session_id or len(session_id) > 256:
            raise ValueError("session_id must be a non-empty string of at most 256 characters")
        if not isinstance(max_history, int) or isinstance(max_history, bool) or max_history < 1:
            raise ValueError("max_history must be a positive integer")
        if not isinstance(ttl_seconds, int) or isinstance(ttl_seconds, bool) or ttl_seconds < 1:
            raise ValueError("ttl_seconds must be a positive integer")
        self._session_id = session_id
        self._redis = redis_client
        self._max_history = max_history
        self._ttl_seconds = ttl_seconds
        self._handlers: dict[TransitionSeverity, list[Callable[[Transition], None]]] = {
            s: [] for s in TransitionSeverity
        }
        self._lock = threading.RLock()

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
        if not isinstance(context, VCPContext):
            raise TypeError("context must be a VCPContext")
        context = VCPContext.from_json(context.to_json())
        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()

        with self._lock:
            return self._record_locked(context, now_iso)

    def _record_locked(self, context: VCPContext, now_iso: str) -> Transition | None:
        """Atomically append a validated snapshot while holding the instance lock."""
        pipeline_factory = getattr(self._redis, "pipeline", None)
        if not callable(pipeline_factory):
            return self._record_without_transactions(context, now_iso)

        try:
            from redis.exceptions import WatchError
        except ImportError:
            return self._record_without_transactions(context, now_iso)

        for _attempt in range(self.MAX_TRANSACTION_RETRIES):
            pipeline = pipeline_factory()
            try:
                pipeline.watch(self._history_key)
                raw_history = pipeline.get(self._history_key)
                # Lightweight Redis-compatible test doubles may expose only
                # get/setex. Preserve that compatibility without pretending
                # they provide cross-worker transaction semantics.
                if not isinstance(raw_history, (str, bytes, type(None))):
                    return self._record_without_transactions(context, now_iso)
                try:
                    history = self._decode_history(raw_history)
                except (TypeError, ValueError) as exc:
                    logger.warning("VCP Redis history read error: %s", exc)
                    history = []

                transition = self._transition_from_history(history, context)
                history.append({"timestamp": now_iso, "context": context.to_json()})
                history = history[-self._max_history :]

                pipeline.multi()
                pipeline.setex(
                    self._history_key,
                    self._ttl_seconds,
                    json.dumps(history),
                )
                pipeline.execute()
                self._invoke_handlers(transition)
                return transition
            except WatchError:
                continue
            except Exception as exc:
                raise RuntimeError("VCP Redis transactional history update failed") from exc
            finally:
                try:
                    pipeline.reset()
                except Exception:
                    logger.debug("VCP Redis pipeline reset failed", exc_info=True)

        raise RuntimeError("VCP Redis history update exceeded transaction retry limit")

    def _record_without_transactions(
        self, context: VCPContext, now_iso: str
    ) -> Transition | None:
        """Compatibility path for clients that do not implement WATCH/MULTI."""
        history = self._get_history()
        transition = self._transition_from_history(history, context)
        history.append({"timestamp": now_iso, "context": context.to_json()})
        history = history[-self._max_history :]
        try:
            self._redis.setex(
                self._history_key,
                self._ttl_seconds,
                json.dumps(history),
            )
        except Exception as exc:
            logger.warning(
                "VCP Redis write error during history update: %s: %s",
                type(exc).__name__,
                exc,
            )
        self._invoke_handlers(transition)
        return transition

    def _transition_from_history(
        self, history: list[dict[str, Any]], context: VCPContext
    ) -> Transition | None:
        if not history:
            return None
        previous_ctx = VCPContext.from_json(history[-1]["context"])
        return self._detect_transition(previous_ctx, context)

    def _invoke_handlers(self, transition: Transition | None) -> None:
        if transition is None or transition.severity is TransitionSeverity.NONE:
            return
        for handler in self._handlers[transition.severity]:
            try:
                handler(transition)
            except Exception as exc:
                logger.warning("VCP transition handler error: %s", exc)

    def _get_history(self) -> list[dict[str, Any]]:
        """Get history from Redis.

        Returns:
            List of {timestamp, context} dicts
        """
        try:
            data: str | bytes | None = self._redis.get(self._history_key)
            return self._decode_history(data)
        except Exception as exc:
            logger.warning("VCP Redis history read error: %s", exc)
        return []

    def _decode_history(self, data: str | bytes | None) -> list[dict[str, Any]]:
        if data is None or data == "" or data == b"":
            return []
        if isinstance(data, bytes):
            data = data.decode("utf-8")
        if not isinstance(data, str):
            raise TypeError("history value must be text")
        parsed = json.loads(data)
        if not isinstance(parsed, list):
            raise ValueError("history root must be an array")
        result: list[dict[str, Any]] = []
        for entry in parsed:
            if (
                not isinstance(entry, dict)
                or not isinstance(entry.get("timestamp"), str)
                or not isinstance(entry.get("context"), dict)
            ):
                raise ValueError("history contains a malformed entry")
            VCPContext.from_json(entry["context"])
            result.append(entry)
        return result[-self._max_history :]

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
            timestamp=datetime.now(timezone.utc),
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
        if not isinstance(severity, TransitionSeverity) or not callable(handler):
            raise ValueError("severity and a callable handler are required")
        with self._lock:
            self._handlers[severity].append(handler)

    @property
    def current(self) -> VCPContext | None:
        """Get current context.

        Returns:
            Current context or None if no history
        """
        with self._lock:
            history = self._get_history()
            if history:
                return VCPContext.from_json(history[-1]["context"])
            return None

    @property
    def history_count(self) -> int:
        """Get number of history entries."""
        with self._lock:
            return len(self._get_history())

    def clear(self) -> None:
        """Clear all history."""
        with self._lock:
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
        if redis_client is not None:
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
        # The hybrid record path writes to both trackers. Registering on both
        # would invoke the same callback twice for one logical transition.
        self._memory_tracker.register_handler(severity, handler)

    @property
    def current(self) -> VCPContext | None:
        """Get current context (prefer Redis for cross-worker consistency)."""
        if self._redis_tracker:
            try:
                current = self._redis_tracker.current
                if current is not None:
                    return current
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
                count = self._redis_tracker.history_count
                if count:
                    return count
            except Exception as e:
                logger.warning(
                    "Failed to get history count from Redis: "
                    f"{type(e).__name__}: {e}. Using memory fallback."
                )
        return self._memory_tracker.history_count

    def clear(self) -> None:
        """Clear all history from both backends."""
        self._memory_tracker.clear()
        if self._redis_tracker:
            self._redis_tracker.clear()

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
