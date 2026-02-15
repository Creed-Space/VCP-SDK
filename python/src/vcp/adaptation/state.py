"""
VCP/A State Tracking.

Tracks context state over time and detects transitions.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from .context import Dimension, VCPContext

if TYPE_CHECKING:
    from ..hooks.executor import HookExecutor


class TransitionSeverity(Enum):
    """Transition severity levels."""

    NONE = "none"  # No change
    MINOR = "minor"  # Single dimension change
    MAJOR = "major"  # Multiple dimensions or key dimension
    EMERGENCY = "emergency"  # Emergency flag detected


# Dimensions that trigger major transitions when changed
MAJOR_DIMENSIONS = {Dimension.OCCASION, Dimension.AGENCY, Dimension.CONSTRAINTS}

# Values that indicate emergency state
EMERGENCY_VALUES = {"🚨", "⚠️", "🆘"}


@dataclass
class Transition:
    """Detected context transition."""

    severity: TransitionSeverity
    changed_dimensions: list[Dimension]
    previous: VCPContext
    current: VCPContext
    timestamp: datetime

    @property
    def is_significant(self) -> bool:
        """Check if transition is significant (MAJOR or EMERGENCY)."""
        return self.severity in {TransitionSeverity.MAJOR, TransitionSeverity.EMERGENCY}

    @property
    def is_emergency(self) -> bool:
        """Check if this is an emergency transition."""
        return self.severity == TransitionSeverity.EMERGENCY

    def __str__(self) -> str:
        dims = ", ".join(d._name for d in self.changed_dimensions)
        return f"Transition({self.severity.value}: {dims})"


class StateTracker:
    """Track context state and detect transitions."""

    def __init__(
        self,
        max_history: int = 100,
        hook_executor: HookExecutor | None = None,
    ):
        """Initialize state tracker.

        Args:
            max_history: Maximum history entries to keep
            hook_executor: Optional HookExecutor for firing on_transition hooks.
                          When provided, on_transition hooks fire whenever a
                          non-NONE severity transition is detected.
                          Import: ``from vcp.hooks import HookExecutor``.
        """
        self._history: list[tuple[datetime, VCPContext]] = []
        self._max_history = max_history
        self._handlers: dict[TransitionSeverity, list[Callable[[Transition], None]]] = {
            s: [] for s in TransitionSeverity
        }
        self._hook_executor = hook_executor

    def record(self, context: VCPContext) -> Transition | None:
        """Record new context state, return transition if any.

        Args:
            context: New context state

        Returns:
            Transition if state changed, None if first record or no change
        """
        now = datetime.utcnow()

        if not self._history:
            self._history.append((now, context))
            return None

        previous = self._history[-1][1]
        transition = self._detect_transition(previous, context)

        self._history.append((now, context))

        # Trim history if needed
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history :]

        # Fire on_transition hook (if executor configured)
        if transition.severity != TransitionSeverity.NONE and self._hook_executor is not None:
            try:
                from ..hooks.types import HookType, TransitionEvent

                hook_result = self._hook_executor.execute(
                    HookType.ON_TRANSITION,
                    session_id="default",
                    context=context.to_json() if hasattr(context, "to_json") else {},
                    constitution=None,
                    event=TransitionEvent(
                        previous_state=str(transition.previous.encode())
                        if hasattr(transition.previous, "encode")
                        else str(transition.previous),
                        new_state=str(transition.current.encode())
                        if hasattr(transition.current, "encode")
                        else str(transition.current),
                        trigger=transition.severity.value,
                        transition_metadata={
                            "changed_dimensions": [
                                d._name for d in transition.changed_dimensions
                            ]
                        },
                    ),
                )
                if hook_result.status == "aborted":
                    # Hook aborted the transition -- remove the recorded entry
                    # and return None to indicate the transition was blocked
                    self._history.pop()
                    return None
            except Exception:
                # Fail-open: if hook execution throws, continue with normal flow
                import logging

                logging.getLogger(__name__).exception(
                    "on_transition hook execution error; continuing"
                )

        # Invoke handlers
        if transition.severity != TransitionSeverity.NONE:
            for handler in self._handlers[transition.severity]:
                handler(transition)

        return transition

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

        # Check for emergency values in current context
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
        """Register a transition handler.

        Args:
            severity: Severity level to handle
            handler: Function to call with transition
        """
        self._handlers[severity].append(handler)

    def unregister_handler(
        self,
        severity: TransitionSeverity,
        handler: Callable[[Transition], None],
    ) -> bool:
        """Unregister a transition handler.

        Args:
            severity: Severity level
            handler: Handler to remove

        Returns:
            True if handler was found and removed
        """
        try:
            self._handlers[severity].remove(handler)
            return True
        except ValueError:
            return False

    @property
    def current(self) -> VCPContext | None:
        """Get current context.

        Returns:
            Current context or None if no history
        """
        return self._history[-1][1] if self._history else None

    @property
    def history(self) -> list[tuple[datetime, VCPContext]]:
        """Get full history.

        Returns:
            List of (timestamp, context) tuples
        """
        return list(self._history)

    @property
    def history_count(self) -> int:
        """Get number of history entries."""
        return len(self._history)

    def get_recent(self, count: int = 10) -> list[tuple[datetime, VCPContext]]:
        """Get recent history entries.

        Args:
            count: Maximum entries to return

        Returns:
            List of recent (timestamp, context) tuples
        """
        return self._history[-count:]

    def clear(self) -> None:
        """Clear all history."""
        self._history.clear()

    def find_transitions(
        self,
        min_severity: TransitionSeverity = TransitionSeverity.MINOR,
    ) -> list[Transition]:
        """Find all transitions in history above minimum severity.

        Args:
            min_severity: Minimum severity to include

        Returns:
            List of transitions
        """
        if len(self._history) < 2:
            return []

        severity_order = [
            TransitionSeverity.NONE,
            TransitionSeverity.MINOR,
            TransitionSeverity.MAJOR,
            TransitionSeverity.EMERGENCY,
        ]
        try:
            min_idx = severity_order.index(min_severity)
        except ValueError:
            # Unknown severity - default to no filtering
            min_idx = 0

        transitions = []
        for i in range(1, len(self._history)):
            prev_ctx = self._history[i - 1][1]
            curr_ctx = self._history[i][1]
            transition = self._detect_transition(prev_ctx, curr_ctx)

            try:
                severity_idx = severity_order.index(transition.severity)
            except ValueError:
                # Unknown severity - treat as highest priority
                severity_idx = len(severity_order)
            if severity_idx >= min_idx:
                transitions.append(transition)

        return transitions
