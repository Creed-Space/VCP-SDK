"""
VCP/A Adaptation Plugin for PDP.

Integrates VCP context-aware adaptation into safety decisions.
Emits VCP signals for other plugins to consume and optionally
adapts response behavior based on context.

Feature flags:
- vcp_adaptation_enabled: Enable plugin execution
- vcp_adaptation_shadow: Shadow mode (signals only, no enforcement)
- vcp_redis_persistence_enabled: Enable Redis for cross-worker state

Concurrency safety:
- _trackers dict protected by threading.Lock
- Access counter for cleanup cadence
- Per-session isolation via session_id (fail-closed if missing)
- Redis provides cross-worker state when enabled
"""

import logging
import threading
import time
from typing import TYPE_CHECKING, Any

from services.feature_flags import is_feature_enabled
from services.vcp import (
    ContextEncoder,
    Dimension,
    StateTracker,
    Transition,
    TransitionSeverity,
    VCPContext,
)
from services.vcp.adaptation.redis_state import HybridStateTracker, get_sync_redis_client

from ..pdp_interfaces import Action, Finding, PDPPlugin, PluginPriority, PluginType
from ..pdp_types import EnhancedContext

if TYPE_CHECKING:
    import redis

logger = logging.getLogger(__name__)


class VCPAdaptationPlugin(PDPPlugin):
    """VCP/A context adaptation for PDP decisions.

    Tracks context state across interactions and emits signals for other plugins.
    In active mode, can also modify response behavior based on context.

    Thread-safety: All _trackers access is protected by _lock.
    Session isolation: Requests without session_id get ephemeral trackers (fail-closed).
    Redis persistence: When vcp_redis_persistence_enabled, state is shared across workers.
    """

    # Per-session tracker TTL (1 hour default)
    _TRACKER_TTL_SECONDS = 3600
    _MAX_TRACKERS = 1000  # Reasonable limit (each tracker has up to 100 history entries)
    _CLEANUP_INTERVAL = 100  # Cleanup every N accesses

    def __init__(self) -> None:
        super().__init__()
        self.type = PluginType.POLICY
        self.priority = PluginPriority.HIGH  # Run early to emit signals
        self.budget_ms = 15  # Context encoding is fast
        self.version = "2.1.0"  # Updated for Redis persistence

        self.encoder = ContextEncoder()

        # Per-session state tracking to avoid cross-user contamination
        # Key: session_id, Value: (tracker, last_access_timestamp)
        # Using Union type since we may have StateTracker or HybridStateTracker
        self._trackers: dict[str, tuple[StateTracker | HybridStateTracker, float]] = {}
        self._lock = threading.Lock()  # Concurrency safety
        self._access_count = 0  # For cleanup cadence

        # Redis client for cross-worker persistence (lazy init)
        self._redis_client: "redis.Redis | None" = None
        self._redis_init_attempted = False

    def _ensure_redis_client(self) -> "redis.Redis | None":
        """Lazy-initialize Redis client if persistence is enabled.

        Returns:
            Redis client or None if disabled/unavailable
        """
        if self._redis_init_attempted:
            return self._redis_client

        self._redis_init_attempted = True

        if not is_feature_enabled("vcp_redis_persistence_enabled"):
            logger.debug("VCP: Redis persistence disabled by feature flag")
            return None

        self._redis_client = get_sync_redis_client()
        if self._redis_client:
            logger.info("VCP: Redis persistence enabled for cross-worker state")
        else:
            logger.debug("VCP: Redis unavailable, using in-memory only")

        return self._redis_client

    @property
    def tracker(self) -> StateTracker:
        """Backward-compatible tracker property for TESTING ONLY.

        Returns a fresh ephemeral tracker to prevent accidental cross-contamination.
        Production code should never use this - use _get_tracker_for_session() instead.
        """
        # Return ephemeral tracker - no state persistence, no contamination risk
        tracker = StateTracker(max_history=100)
        tracker.register_handler(TransitionSeverity.EMERGENCY, self._handle_emergency_transition)
        tracker.register_handler(TransitionSeverity.MAJOR, self._handle_major_transition)
        return tracker

    def _get_tracker_for_session(self, context: "EnhancedContext") -> tuple[StateTracker | HybridStateTracker, bool]:
        """Get tracker for session, with fail-closed semantics.

        Args:
            context: Enhanced PDP context

        Returns:
            Tuple of (tracker, is_persistent). If is_persistent=False, tracker is
            ephemeral and state won't be tracked across requests.
        """
        # Derive session key - fail-closed if no identifier available
        session_id = getattr(context, "session_id", None)
        if not session_id:
            # Try fallback identifiers
            session_id = getattr(context, "conversation_id", None)
        if not session_id:
            session_id = getattr(context, "user_id", None)

        if not session_id:
            # FAIL-CLOSED: No identifier = ephemeral tracker (no cross-user risk)
            logger.debug("VCP: No session identifier - using ephemeral tracker")
            return self.tracker, False  # Returns fresh ephemeral tracker

        return self._get_tracker(session_id), True

    def _get_tracker(self, session_id: str) -> StateTracker | HybridStateTracker:
        """Get or create a StateTracker for the given session.

        Thread-safe via _lock. Uses HybridStateTracker with Redis when enabled.

        Args:
            session_id: Session identifier (must not be empty/None)

        Returns:
            StateTracker or HybridStateTracker for this session
        """
        now = time.time()

        # Check if Redis persistence is enabled (lazy init)
        redis_client = self._ensure_redis_client()

        with self._lock:
            self._access_count += 1

            # Cleanup expired trackers periodically (every N accesses)
            if self._access_count % self._CLEANUP_INTERVAL == 0:
                self._cleanup_expired_trackers_locked(now)

            # Check for existing tracker
            if session_id in self._trackers:
                tracker, _ = self._trackers[session_id]
                self._trackers[session_id] = (tracker, now)  # Update last access
                return tracker

            # Create new tracker
            if len(self._trackers) >= self._MAX_TRACKERS:
                self._cleanup_expired_trackers_locked(now)
                # If still at limit, evict oldest
                if len(self._trackers) >= self._MAX_TRACKERS:
                    oldest_key = min(self._trackers, key=lambda k: self._trackers[k][1])
                    logger.debug(f"VCP: Evicting oldest tracker (session={oldest_key[:8]}...)")
                    del self._trackers[oldest_key]

            # Use HybridStateTracker for Redis persistence, plain StateTracker otherwise
            if redis_client:
                tracker: StateTracker | HybridStateTracker = HybridStateTracker(
                    session_id=session_id,
                    redis_client=redis_client,
                    max_history=100,
                    ttl_seconds=self._TRACKER_TTL_SECONDS,
                )
            else:
                tracker = StateTracker(max_history=100)

            tracker.register_handler(
                TransitionSeverity.EMERGENCY,
                self._handle_emergency_transition,
            )
            tracker.register_handler(
                TransitionSeverity.MAJOR,
                self._handle_major_transition,
            )
            self._trackers[session_id] = (tracker, now)
            return tracker

    def _cleanup_expired_trackers_locked(self, now: float) -> None:
        """Remove trackers that haven't been accessed recently.

        MUST be called while holding _lock.
        """
        expired = [
            key for key, (_, last_access) in self._trackers.items() if now - last_access > self._TRACKER_TTL_SECONDS
        ]
        if expired:
            logger.debug(f"VCP: Cleaning up {len(expired)} expired trackers")
        for key in expired:
            del self._trackers[key]

    def execute(
        self,
        context: EnhancedContext,
        findings: list[Finding],
    ) -> Action | None:
        """Evaluate request with VCP/A context.

        Args:
            context: Enhanced PDP context
            findings: Previous plugin findings

        Returns:
            Action if modification needed, None otherwise
        """
        # Check feature flag
        if not is_feature_enabled("vcp_adaptation_enabled"):
            return None

        # Get session-specific tracker (fail-closed: no session = ephemeral tracker)
        tracker, is_persistent = self._get_tracker_for_session(context)

        # Extract and encode VCP context from request metadata
        vcp_context = self._extract_context(context)

        # Track state and detect transitions
        transition = tracker.record(vcp_context)

        # Build signals for other plugins (always emitted)
        signals = self._build_signals(vcp_context, transition)
        signals["vcp_tracking_persistent"] = is_persistent  # Let consumers know if state persists

        # Store signals in context metadata for other plugins
        if not hasattr(context, "vcp_signals"):
            context.metadata = context.metadata or {}
        context.metadata["vcp_signals"] = signals

        # Shadow mode: emit signals only, no enforcement
        if is_feature_enabled("vcp_adaptation_shadow"):
            logger.debug(
                "VCP/A shadow mode: signals emitted",
                extra={"vcp_context": vcp_context.encode()},
            )
            return None

        # Active mode: compute and return modifications if needed
        return self._compute_action(vcp_context, transition, context)

    def _extract_context(self, context: EnhancedContext) -> VCPContext:
        """Extract VCP context from PDP EnhancedContext.

        Args:
            context: PDP enhanced context

        Returns:
            Encoded VCPContext
        """
        metadata = context.metadata or {}

        # Map EnhancedContext fields to VCP dimensions
        company_values: list[str] | None = None
        if context.user_state == "vulnerable":
            company_values = ["alone"]
        elif metadata.get("audience"):
            audience = metadata.get("audience")
            company_values = audience if isinstance(audience, list) else [audience]

        # Map context_type to occasion if applicable
        occasion = None
        if context.context_type == "crisis":
            occasion = "emergency"
        elif metadata.get("occasion"):
            occasion = metadata.get("occasion")

        # Map persona_type to space context
        space = metadata.get("environment")
        if not space and context.persona_type == "sentinel":
            space = "office"  # Security context suggests professional

        return self.encoder.encode(
            time=metadata.get("time_of_day"),
            space=space,
            company=company_values,
            culture=metadata.get("culture"),
            occasion=occasion,
            state=context.user_state,
            environment=metadata.get("physical_environment"),
            agency=metadata.get("agency_level"),
            constraints=metadata.get("active_constraints"),
        )

    def _build_signals(
        self,
        vcp_context: VCPContext,
        transition: Transition | None,
    ) -> dict[str, Any]:
        """Build signals for other plugins.

        Args:
            vcp_context: Current VCP context
            transition: Detected transition (if any)

        Returns:
            Signal dictionary
        """
        signals: dict[str, Any] = {
            "vcp_context_wire": vcp_context.encode(),
            "vcp_context_json": vcp_context.to_json(),
            "vcp_has_context": bool(vcp_context),
        }

        # Add dimension-specific signals
        for dim in Dimension:
            values = vcp_context.get(dim)
            signals[f"vcp_{dim._name}"] = values
            signals[f"vcp_has_{dim._name}"] = bool(values)

        # Add transition signals
        if transition:
            signals["vcp_transition_severity"] = transition.severity.value
            signals["vcp_transition_dimensions"] = [d._name for d in transition.changed_dimensions]
            signals["vcp_is_emergency"] = transition.is_emergency
            signals["vcp_is_significant"] = transition.is_significant

        return signals

    def _compute_action(
        self,
        vcp_context: VCPContext,
        transition: Transition | None,
        context: EnhancedContext,
    ) -> Action | None:
        """Compute action based on context (active mode only).

        Args:
            vcp_context: Current VCP context
            transition: Detected transition
            context: PDP context

        Returns:
            Action if intervention needed, None otherwise
        """
        reasons: list[str] = []
        edits: dict[str, Any] = {}
        policy_ids: list[str] = []

        # Children present → prefer Nanny persona, boost adherence
        company = vcp_context.get(Dimension.COMPANY)
        if "👶" in company:
            edits["prefer_persona"] = "nanny"
            edits["adherence_boost"] = 1
            edits["content_filter"] = "family_safe"
            reasons.append("Children present in context")
            policy_ids.append("vcp_child_safety")

        # Emergency situation → maximum safety
        occasion = vcp_context.get(Dimension.OCCASION)
        if "🚨" in occasion:
            edits["prefer_persona"] = "sentinel"
            edits["adherence_level"] = 5
            edits["emergency_mode"] = True
            reasons.append("Emergency context detected")
            policy_ids.append("vcp_emergency_response")

        # Professional context → Ambassador persona
        space = vcp_context.get(Dimension.SPACE)
        if "🏢" in space:
            if "prefer_persona" not in edits:  # Don't override safety personas
                edits["prefer_persona"] = "ambassador"
                reasons.append("Professional context detected")
                policy_ids.append("vcp_professional_context")

        # Limited agency → extra caution
        agency = vcp_context.get(Dimension.AGENCY)
        if "🔐" in agency:
            edits["extra_caution"] = True
            reasons.append("Limited agency context")
            policy_ids.append("vcp_limited_agency")

        # Transition-based modifications
        if transition and transition.is_significant:
            edits["context_changed"] = True
            edits["revalidate_constitution"] = True
            reasons.append(f"Significant context transition: {transition.severity.value}")
            policy_ids.append("vcp_context_transition")

        # Return action only if we have modifications
        if edits:
            return Action(
                plugin_id=self.id,
                decision="transform",
                reasons=reasons,
                edits=edits,
                confidence=0.85,
                policy_ids=policy_ids,
            )

        return None

    def _handle_emergency_transition(self, transition: Transition) -> None:
        """Handle emergency transitions (logging, alerts).

        Args:
            transition: Emergency transition
        """
        logger.warning(
            "VCP Emergency Transition detected",
            extra={
                "changed_dimensions": [d._name for d in transition.changed_dimensions],
                "severity": transition.severity.value,
            },
        )

    def _handle_major_transition(self, transition: Transition) -> None:
        """Handle major transitions.

        Args:
            transition: Major transition
        """
        logger.info(
            "VCP Major Transition detected",
            extra={
                "changed_dimensions": [d._name for d in transition.changed_dimensions],
                "severity": transition.severity.value,
            },
        )

    def get_tracker_stats(self) -> dict[str, Any]:
        """Get state tracker statistics.

        Returns:
            Dict with tracker stats
        """
        return {
            "history_count": self.tracker.history_count,
            "current_context": self.tracker.current.encode() if self.tracker.current else None,
            "recent_transitions": len(self.tracker.find_transitions(TransitionSeverity.MINOR)),
        }
