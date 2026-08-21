"""Deterministic VCP/A operational state machine.

This module implements the guard conditions in the shared state-machine
conformance profile. It is separate from :mod:`vcp.adaptation.state`, whose
``StateTracker`` detects context-difference severity but does not manage
operational lifecycle states.
"""

from __future__ import annotations

import math
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

    def __post_init__(self) -> None:
        for name in (
            "signal_stability_seconds",
            "active_dwell_seconds",
            "transition_timeout_seconds",
            "signal_loss_seconds",
        ):
            _nonnegative_number(getattr(self, name), f"config.{name}")
        if not 1 <= self.signal_stability_seconds <= 10:
            raise ValueError("config.signal_stability_seconds must be between 1 and 10")
        if not 0 < self.transition_timeout_seconds <= 30:
            raise ValueError(
                "config.transition_timeout_seconds must be greater than 0 and at most 30"
            )
        if self.signal_loss_seconds <= 0:
            raise ValueError("config.signal_loss_seconds must be greater than 0")
        for name in ("hysteresis_dimensions", "hysteresis_magnitude"):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value < 1:
                raise ValueError(f"config.{name} must be a positive integer")


def _nonnegative_number(value: Any, field_name: str) -> int | float:
    if (
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        or value < 0
        or (isinstance(value, float) and not math.isfinite(value))
    ):
        raise ValueError(f"{field_name} must be a finite non-negative number")
    return value


def _nonnegative_integer(value: Any, field_name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{field_name} must be a non-negative integer")
    return value


def _optional_boolean(value: dict[str, Any], field_name: str) -> None:
    if field_name in value and not isinstance(value[field_name], bool):
        raise ValueError(f"event.{field_name} must be a boolean")


class VCPStateMachine:
    """Evaluate one event from an explicit state and precondition snapshot."""

    def __init__(self, config: StateMachineConfig | None = None) -> None:
        if config is not None and not isinstance(config, StateMachineConfig):
            raise TypeError("config must be a StateMachineConfig or null")
        self.config = StateMachineConfig() if config is None else config

    def evaluate(
        self,
        initial_state: str | OperationalState,
        event: dict[str, Any],
        preconditions: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Return the deterministic transition outcome for one event."""
        if not isinstance(event, dict):
            raise TypeError("event must be an object")
        if preconditions is not None and not isinstance(preconditions, dict):
            raise TypeError("preconditions must be an object or null")
        state = OperationalState(initial_state)
        pre = {} if preconditions is None else preconditions
        event_type = event.get("type")
        if event_type not in {"context_signal", "clear_emergency", "tick", "signal_loss"}:
            raise ValueError("event.type is missing or unsupported")
        for field_name in (
            "is_emergency",
            "signals_still_degraded",
            "context_changed_during_emergency",
            "no_valid_context",
            "context_still_valid",
        ):
            _optional_boolean(event, field_name)
        for field_name in (
            "stable_for_seconds",
            "elapsed_since_transition_seconds",
            "silence_duration_seconds",
        ):
            if field_name in event:
                _nonnegative_number(event[field_name], f"event.{field_name}")
        for field_name in ("dimensions_changed", "magnitude"):
            if field_name in event:
                _nonnegative_integer(event[field_name], f"event.{field_name}")
        if "dwell_time_elapsed_seconds" in pre:
            _nonnegative_number(
                pre["dwell_time_elapsed_seconds"],
                "preconditions.dwell_time_elapsed_seconds",
            )
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
                >= self.config.transition_timeout_seconds
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
