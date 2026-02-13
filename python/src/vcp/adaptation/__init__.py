"""
VCP/A (Adaptation Layer) - Context-aware adaptation.

Provides context encoding, state tracking, and transition handling.
"""

from .context import ContextEncoder, Dimension, VCPContext
from .redis_state import HybridStateTracker, RedisStateTracker, get_sync_redis_client
from .state import StateTracker, Transition, TransitionSeverity

__all__ = [
    "VCPContext",
    "ContextEncoder",
    "Dimension",
    "StateTracker",
    "Transition",
    "TransitionSeverity",
    # Redis persistence
    "RedisStateTracker",
    "HybridStateTracker",
    "get_sync_redis_client",
]
