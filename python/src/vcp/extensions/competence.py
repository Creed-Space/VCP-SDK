"""VCP Competence Extensions.

User competence attestation framework based on the five minimum competence
criteria for safe GenAI use (Frischmann 2026): Epistemic, Instrumental,
Discernment, Risk Sensitivity, and Self-Regulation.

Provides score decay utilities and re-exports the core competence types
from vcp.types for convenience.
"""

from __future__ import annotations

from vcp.types import (
    CompetenceClaim,
    CompetenceCriterion,
    CompetenceMeasurementBasis,
    CompetenceProfile,
    SelfRegulationCommitment,
    apply_decay,
)

__all__ = [
    "CompetenceCriterion",
    "CompetenceMeasurementBasis",
    "CompetenceClaim",
    "SelfRegulationCommitment",
    "CompetenceProfile",
    "apply_decay",
]
