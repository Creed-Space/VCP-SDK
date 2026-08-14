"""Deterministic VCP/A operational state machine.

This module implements the guard conditions in the shared state-machine
conformance profile. It is separate from :mod:`vcp.adaptation.state`, whose
``StateTracker`` detects context-difference severity but does not manage
operational lifecycle states.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class OperationalState(str, Enum):
    """Runtime states defined by the VCP/A lifecycle profile."""

    IDLE = "IDLE"
    ACTIVE = "ACTIVE"
    TRANSITIONING = "TRANSITIONING"
    CONFLICT = "CONFLICT"
    DEGRADED = "DEGRADED"
    EMERGENCY = "EMERGENCY"


@dataclass(frozen=True)
class StateMachineConfig:
    """Guard thresholds in seconds and changed-dimension units."""

    signal_stability_seconds: float = 3.0
    active_dwell_seconds: float = 10.0
    transition_timeout_seconds: float = 5.0
    signal_loss_seconds: float = 30.0
    hysteresis_dimensions: int = 2
    hysteresis_magnitude: int = 2


class VCPStateMachine:
    """Evaluate one event from an explicit state and precondition snapshot."""

    def __init__(self, config: StateMachineConfig | None = None) -> None:
        self.config = config or StateMachineConfig()

    def evaluate(
        self,
        initial_state: str | OperationalState,
        event: dict[str, Any],
        preconditions: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Return the deterministic transition outcome for one event."""
        state = OperationalState(initial_state)
        pre = preconditions or {}
        event_type = event.get("type")
        if event_type == "context_signal" and event.get("is_emergency"):
            return {
                "final_state": OperationalState.EMERGENCY.value,
                "safety_constitution_active": True,
                "prior_state_saved": True,
            }
        if state is OperationalState.EMERGENCY and event_type == "clear_emergency":
            if event.get("signals_still_degraded"):
                return {"final_state": OperationalState.DEGRADED.value}
            if event.get("context_changed_during_emergency"):
                return {"final_state": OperationalState.TRANSITIONING.value}
            if event.get("no_valid_context") or pre.get("prior_context") is None:
                return {"final_state": OperationalState.IDLE.value}
            if event.get("context_still_valid"):
                return {
                    "final_state": OperationalState.ACTIVE.value,
                    "constitutions_restored": True,
                }
        if state is OperationalState.TRANSITIONING and event_type == "tick":
            if (
                event.get("elapsed_since_transition_seconds", 0)
                > self.config.transition_timeout_seconds
            ):
                return {
                    "final_state": OperationalState.ACTIVE.value,
                    "constitutions": "previous_constitutions",
                    "warning_logged": True,
                }
        if state is OperationalState.ACTIVE and event_type == "signal_loss":
            if event.get("silence_duration_seconds", 0) > self.config.signal_loss_seconds:
                return {
                    "final_state": OperationalState.DEGRADED.value,
                    "last_known_context_saved": True,
                }
        if state is OperationalState.DEGRADED and event_type == "tick":
            if pre.get("last_known_context") is None:
                return {"final_state": OperationalState.IDLE.value}
        if event_type == "context_signal":
            stable = event.get("stable_for_seconds", 0) >= self.config.signal_stability_seconds
            if not stable:
                return {"final_state": state.value, "transition_occurred": False}
            if state is OperationalState.IDLE:
                return {
                    "final_state": OperationalState.ACTIVE.value,
                    "constitutions_selected": True,
                }
            if state is OperationalState.DEGRADED:
                return {
                    "intermediate_state": OperationalState.TRANSITIONING.value,
                    "final_state": OperationalState.ACTIVE.value,
                    "transition_path": [
                        OperationalState.DEGRADED.value,
                        OperationalState.TRANSITIONING.value,
                        OperationalState.ACTIVE.value,
                    ],
                }
            if state is OperationalState.ACTIVE:
                dwell = pre.get("dwell_time_elapsed_seconds", self.config.active_dwell_seconds)
                if dwell < self.config.active_dwell_seconds:
                    return {
                        "final_state": OperationalState.ACTIVE.value,
                        "transition_occurred": False,
                        "pending_context_queued": True,
                    }
                changed = event.get("dimensions_changed", 0)
                magnitude = event.get("magnitude", 0)
                if changed >= self.config.hysteresis_dimensions or (
                    changed >= 1 and magnitude >= self.config.hysteresis_magnitude
                ):
                    return {
                        "intermediate_state": OperationalState.TRANSITIONING.value,
                        "final_state": OperationalState.ACTIVE.value,
                        "transition_path": [
                            OperationalState.ACTIVE.value,
                            OperationalState.TRANSITIONING.value,
                            OperationalState.ACTIVE.value,
                        ],
                    }
                return {
                    "final_state": OperationalState.ACTIVE.value,
                    "transition_occurred": False,
                }
        return {"final_state": state.value, "transition_occurred": False}
