"""VCP 3.1 Extension modules for Creed Space SDK.

Provides pure-Python data structures and algorithms for:
- Personal context signals with decay
- Relational context (trust, standing, self-model)
- Schulze consensus voting
- Torch session handoff
"""

from vcp.extensions.consensus import (
    Ballot,
    ElectionResult,
    PairwiseResult,
    SchulzeElection,
    SchulzeRanking,
)
from vcp.extensions.personal import (
    DECAY_CONFIGS,
    DecayConfig,
    LifecycleState,
    PersonalContext,
    PersonalDimension,
    PersonalSignal,
    compute_decayed_intensity,
)
from vcp.extensions.relational import (
    AISelfModel,
    DimensionReport,
    RelationalContext,
    RelationalNorm,
    StandingLevel,
    TrustLevel,
)
from vcp.extensions.torch import (
    TorchConsumer,
    TorchGenerator,
    TorchLineage,
    TorchSummary,
)

__all__ = [
    # Personal
    "PersonalDimension",
    "PersonalSignal",
    "PersonalContext",
    "DecayConfig",
    "DECAY_CONFIGS",
    "compute_decayed_intensity",
    "LifecycleState",
    # Relational
    "TrustLevel",
    "StandingLevel",
    "DimensionReport",
    "AISelfModel",
    "RelationalContext",
    "RelationalNorm",
    # Consensus
    "Ballot",
    "PairwiseResult",
    "SchulzeRanking",
    "ElectionResult",
    "SchulzeElection",
    # Torch
    "TorchSummary",
    "TorchLineage",
    "TorchGenerator",
    "TorchConsumer",
]
