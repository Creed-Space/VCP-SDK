"""
VCP/A (Adaptation Layer) — Context-aware adaptation.

Provides context encoding (VCP v3.2 / VEP-0004), state tracking, and
transition handling.
"""

from .context import (
    ContextEncoder,
    Dimension,  # backwards-compat alias → SituationalDimension
    PersonalState,
    PersonalStateDimension,
    SituationalDimension,
    VCPContext,
)
from .redis_state import HybridStateTracker, RedisStateTracker, get_sync_redis_client
from .state import StateTracker, Transition, TransitionSeverity
from .state_machine import OperationalState, StateMachineConfig, VCPStateMachine

__all__ = [
    "VCPContext",
    "ContextEncoder",
    "SituationalDimension",
    "PersonalStateDimension",
    "PersonalState",
    "Dimension",  # deprecated alias kept for backwards compatibility
    "StateTracker",
    "Transition",
    "TransitionSeverity",
    "OperationalState",
    "StateMachineConfig",
    "VCPStateMachine",
    # Redis persistence
    "RedisStateTracker",
    "HybridStateTracker",
    "get_sync_redis_client",
]
