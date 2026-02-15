"""
VCP Hook System - Deterministic extension mechanism for the adaptation pipeline.

Provides six hook types (pre_inject, post_select, on_transition, on_conflict,
on_violation, periodic) with priority-ordered chain execution, timeout
enforcement, and error handling.

Public API:
    HookType          - Enum of hook interception points
    Hook              - Hook definition dataclass
    HookInput         - Input passed to hook actions
    HookResult        - Structured return value from hooks
    ResultStatus      - Continue/abort/modify enum
    ChainResult       - Result of chain execution
    HookRegistry      - Central registry (deployment + session scopes)
    HookExecutor      - Chain executor with timeout and error handling

Event payloads:
    PreInjectEvent, PostSelectEvent, TransitionEvent,
    ConflictEvent, ViolationEvent, PeriodicEvent

Built-in hooks:
    persona_select_hook, adherence_escalate_hook,
    scope_filter_hook, audit_hook

Exceptions:
    HookError, HookValidationError, DuplicateHookError
"""

from .builtin import (
    adherence_escalate_hook,
    audit_hook,
    persona_select_hook,
    scope_filter_hook,
)
from .executor import HookExecutor
from .registry import HookRegistry
from .types import (
    ChainResult,
    ConflictEvent,
    DuplicateHookError,
    Hook,
    HookError,
    HookInput,
    HookResult,
    HookType,
    HookValidationError,
    PeriodicEvent,
    PostSelectEvent,
    PreInjectEvent,
    ResultStatus,
    TransitionEvent,
    ViolationEvent,
)

__all__ = [
    # Core types
    "HookType",
    "ResultStatus",
    "Hook",
    "HookInput",
    "HookResult",
    "ChainResult",
    # Event payloads
    "PreInjectEvent",
    "PostSelectEvent",
    "TransitionEvent",
    "ConflictEvent",
    "ViolationEvent",
    "PeriodicEvent",
    # Registry and executor
    "HookRegistry",
    "HookExecutor",
    # Built-in hooks
    "persona_select_hook",
    "adherence_escalate_hook",
    "scope_filter_hook",
    "audit_hook",
    # Exceptions
    "HookError",
    "HookValidationError",
    "DuplicateHookError",
]
