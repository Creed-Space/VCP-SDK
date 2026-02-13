"""
VCP/S (Semantics Layer) - Constitutional semantics and composition.

Provides CSM1 grammar parsing, persona definitions, and composition engine.
"""

from .composer import Composer, CompositionConflictError, CompositionResult, Conflict
from .csm1 import CSM1Code, Persona, Scope

__all__ = [
    "CSM1Code",
    "Persona",
    "Scope",
    "Composer",
    "CompositionResult",
    "Conflict",
    "CompositionConflictError",
]
