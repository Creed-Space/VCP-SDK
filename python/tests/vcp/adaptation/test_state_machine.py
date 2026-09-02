"""Adversarial unit coverage for the operational adaptation state machine."""

from __future__ import annotations

import math

import pytest

from vcp.adaptation.state_machine import (
    OperationalState,
    StateMachineConfig,
    VCPStateMachine,
)


def _evaluate(
    state: str,
    event: dict[str, object],
    preconditions: dict[str, object] | None = None,
) -> dict[str, object]:
    return VCPStateMachine().evaluate(state, event, preconditions)


class TestTransitions:
    def test_emergency_signal_preempts_every_state_and_all_guards(self) -> None:
        for state in OperationalState:
            result = _evaluate(
                state.value,
                {"type": "context_signal", "is_emergency": True},
                {"dwell_time_elapsed_seconds": 0},
            )
            assert result == {
                "final_state": "EMERGENCY",
                "safety_constitution_active": True,
                "prior_state_saved": True,
            }

    @pytest.mark.parametrize(
        ("event", "preconditions", "expected"),
        [
            ({"type": "clear_emergency", "signals_still_degraded": True}, {}, "DEGRADED"),
            (
                {"type": "clear_emergency", "context_changed_during_emergency": True},
                {"prior_context": "old"},
                "TRANSITIONING",
            ),
            (
                {"type": "clear_emergency", "no_valid_context": True},
                {"prior_context": "old"},
                "IDLE",
            ),
            ({"type": "clear_emergency"}, {"prior_context": None}, "IDLE"),
        ],
    )
    def test_emergency_clear_fail_safe_paths(
        self,
        event: dict[str, object],
        preconditions: dict[str, object],
        expected: str,
    ) -> None:
        assert _evaluate("EMERGENCY", event, preconditions)["final_state"] == expected

    def test_emergency_clear_restores_only_explicitly_valid_prior_context(self) -> None:
        result = _evaluate(
            "EMERGENCY",
            {"type": "clear_emergency", "context_still_valid": True},
            {"prior_context": "context"},
        )
        assert result == {"final_state": "ACTIVE", "constitutions_restored": True}

    def test_emergency_clear_without_a_decision_remains_emergency(self) -> None:
        assert _evaluate(
            "EMERGENCY", {"type": "clear_emergency"}, {"prior_context": "context"}
        ) == {"final_state": "EMERGENCY", "transition_occurred": False}

    def test_transition_timeout_fires_at_exact_boundary(self) -> None:
        at_boundary = _evaluate(
            "TRANSITIONING", {"type": "tick", "elapsed_since_transition_seconds": 5}
        )
        before_boundary = _evaluate(
            "TRANSITIONING", {"type": "tick", "elapsed_since_transition_seconds": 4.999}
        )
        assert at_boundary == {
            "final_state": "ACTIVE",
            "constitutions": "previous_constitutions",
            "warning_logged": True,
        }
        assert before_boundary["final_state"] == "TRANSITIONING"

    def test_signal_loss_requires_duration_strictly_above_threshold(self) -> None:
        assert (
            _evaluate("ACTIVE", {"type": "signal_loss", "silence_duration_seconds": 30})[
                "final_state"
            ]
            == "ACTIVE"
        )
        assert _evaluate("ACTIVE", {"type": "signal_loss", "silence_duration_seconds": 30.001}) == {
            "final_state": "DEGRADED",
            "last_known_context_saved": True,
        }

    def test_degraded_tick_without_last_context_falls_back_to_idle(self) -> None:
        assert _evaluate("DEGRADED", {"type": "tick"}, {"last_known_context": None}) == {
            "final_state": "IDLE"
        }
        assert (
            _evaluate("DEGRADED", {"type": "tick"}, {"last_known_context": "context"})[
                "final_state"
            ]
            == "DEGRADED"
        )

    def test_signal_stability_boundary_and_idle_activation(self) -> None:
        assert _evaluate("IDLE", {"type": "context_signal", "stable_for_seconds": 2.999}) == {
            "final_state": "IDLE",
            "transition_occurred": False,
        }
        assert _evaluate("IDLE", {"type": "context_signal", "stable_for_seconds": 3}) == {
            "final_state": "ACTIVE",
            "constitutions_selected": True,
        }

    def test_restored_stable_signal_transitions_degraded_via_transitioning(self) -> None:
        assert _evaluate("DEGRADED", {"type": "context_signal", "stable_for_seconds": 3}) == {
            "intermediate_state": "TRANSITIONING",
            "final_state": "ACTIVE",
            "transition_path": ["DEGRADED", "TRANSITIONING", "ACTIVE"],
        }

    def test_active_dwell_queues_stable_context_change_before_boundary(self) -> None:
        assert _evaluate(
            "ACTIVE",
            {
                "type": "context_signal",
                "stable_for_seconds": 3,
                "dimensions_changed": 2,
            },
            {"dwell_time_elapsed_seconds": 9.999},
        ) == {
            "final_state": "ACTIVE",
            "transition_occurred": False,
            "pending_context_queued": True,
        }

    @pytest.mark.parametrize(
        ("dimensions", "magnitude", "transitions"),
        [(2, 0, True), (1, 2, True), (1, 1, False), (0, 99, False)],
    )
    def test_hysteresis_boundaries(
        self, dimensions: int, magnitude: int, transitions: bool
    ) -> None:
        result = _evaluate(
            "ACTIVE",
            {
                "type": "context_signal",
                "stable_for_seconds": 3,
                "dimensions_changed": dimensions,
                "magnitude": magnitude,
            },
            {"dwell_time_elapsed_seconds": 10},
        )
        if transitions:
            assert result["transition_path"] == ["ACTIVE", "TRANSITIONING", "ACTIVE"]
        else:
            assert result == {"final_state": "ACTIVE", "transition_occurred": False}

    @pytest.mark.parametrize(
        "event",
        [
            {"type": "tick"},
            {"type": "context_signal", "stable_for_seconds": 3},
        ],
    )
    def test_irrelevant_valid_event_is_a_deterministic_noop(self, event: dict[str, object]) -> None:
        assert _evaluate("CONFLICT", event) == {
            "final_state": "CONFLICT",
            "transition_occurred": False,
        }


class TestMalformedInputs:
    @pytest.mark.parametrize(
        "config",
        [
            StateMachineConfig(signal_stability_seconds=1),
            StateMachineConfig(signal_stability_seconds=10),
            StateMachineConfig(transition_timeout_seconds=30),
            StateMachineConfig(active_dwell_seconds=0),
        ],
    )
    def test_valid_config_boundaries(self, config: StateMachineConfig) -> None:
        assert VCPStateMachine(config).config is config

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"signal_stability_seconds": 0},
            {"signal_stability_seconds": 10.001},
            {"transition_timeout_seconds": 0},
            {"transition_timeout_seconds": 30.001},
            {"active_dwell_seconds": -1},
            {"signal_loss_seconds": 0},
            {"hysteresis_dimensions": 0},
            {"hysteresis_magnitude": True},
            {"signal_loss_seconds": math.inf},
            {"active_dwell_seconds": math.nan},
        ],
    )
    def test_invalid_config_values_are_rejected(self, kwargs: dict[str, object]) -> None:
        with pytest.raises(ValueError):
            StateMachineConfig(**kwargs)  # type: ignore[arg-type]

    def test_wrong_config_type_is_not_silently_replaced_by_defaults(self) -> None:
        with pytest.raises(TypeError, match="StateMachineConfig"):
            VCPStateMachine([])  # type: ignore[arg-type]

    @pytest.mark.parametrize("event", [None, [], "tick", 7])
    def test_event_must_be_an_object(self, event: object) -> None:
        with pytest.raises(TypeError, match="event"):
            VCPStateMachine().evaluate("ACTIVE", event)  # type: ignore[arg-type]

    @pytest.mark.parametrize("event", [{}, {"type": None}, {"type": "unknown"}])
    def test_missing_or_unknown_event_type_is_rejected(self, event: dict[str, object]) -> None:
        with pytest.raises(ValueError, match="event.type"):
            _evaluate("ACTIVE", event)

    @pytest.mark.parametrize("preconditions", [[], "pre", 0])
    def test_preconditions_must_be_an_object(self, preconditions: object) -> None:
        with pytest.raises(TypeError, match="preconditions"):
            VCPStateMachine().evaluate(
                "ACTIVE",
                {"type": "tick"},
                preconditions,  # type: ignore[arg-type]
            )

    @pytest.mark.parametrize(
        "event",
        [
            {"type": "context_signal", "is_emergency": 1},
            {"type": "clear_emergency", "context_still_valid": "yes"},
            {"type": "context_signal", "stable_for_seconds": -1},
            {"type": "tick", "elapsed_since_transition_seconds": math.nan},
            {"type": "signal_loss", "silence_duration_seconds": math.inf},
            {"type": "context_signal", "dimensions_changed": 1.5},
            {"type": "context_signal", "dimensions_changed": True},
            {"type": "context_signal", "magnitude": -1},
        ],
    )
    def test_event_fields_reject_coercion_and_nonfinite_or_negative_numbers(
        self, event: dict[str, object]
    ) -> None:
        with pytest.raises(ValueError):
            _evaluate("ACTIVE", event)

    def test_malformed_dwell_precondition_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="dwell"):
            _evaluate(
                "ACTIVE",
                {"type": "context_signal", "stable_for_seconds": 3},
                {"dwell_time_elapsed_seconds": "ten"},
            )

    def test_invalid_initial_state_is_rejected(self) -> None:
        with pytest.raises(ValueError):
            _evaluate("BROKEN", {"type": "tick"})
