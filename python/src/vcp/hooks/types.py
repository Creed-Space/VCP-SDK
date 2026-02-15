"""
VCP Hook System - Type Definitions.

Defines the core data types for the VCP hook system: HookType enum,
Hook definition, HookInput/HookResult contracts, event payloads,
and chain results.

Spec reference: VCP_HOOKS.md sections 3-4.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class HookType(Enum):
    """Six hook interception points in the adaptation pipeline.

    Each type corresponds to a distinct event where hooks may execute.
    """

    PRE_INJECT = "pre_inject"
    POST_SELECT = "post_select"
    ON_TRANSITION = "on_transition"
    ON_CONFLICT = "on_conflict"
    ON_VIOLATION = "on_violation"
    PERIODIC = "periodic"


class ResultStatus(Enum):
    """Hook result status controlling pipeline flow."""

    CONTINUE = "continue"  # No change, pass to next hook
    ABORT = "abort"  # Stop chain, cancel pipeline operation
    MODIFY = "modify"  # Pass modified context/constitution to next hook


# --- Validation constants ---

HOOK_NAME_PATTERN = re.compile(r"^[a-z0-9_-]{1,64}$")
MIN_PRIORITY = 0
MAX_PRIORITY = 100
MIN_TIMEOUT_MS = 1
MAX_TIMEOUT_MS = 30000


# --- Event payloads (type-specific) ---


@dataclass
class PreInjectEvent:
    """Payload for pre_inject hooks.

    Fired before a constitution is injected into LLM context.
    """

    injection_target: str = ""
    injection_format: str = "system_prompt"
    raw_constitution: str = ""


@dataclass
class PostSelectEvent:
    """Payload for post_select hooks.

    Fired after the adaptation layer selects a constitution.
    """

    candidates: list[Any] = field(default_factory=list)
    selection_rationale: str = ""
    selection_algorithm: str = ""
    scores: dict[str, float] = field(default_factory=dict)


@dataclass
class TransitionEvent:
    """Payload for on_transition hooks.

    Fired when the context state machine transitions between states.
    """

    previous_state: str = ""
    new_state: str = ""
    trigger: str = ""
    transition_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ConflictEvent:
    """Payload for on_conflict hooks.

    Fired when composition detects conflicting rules.
    """

    conflicting_rules: list[Any] = field(default_factory=list)
    composition_strategy: str = ""
    conflict_severity: str = "warning"


@dataclass
class ViolationEvent:
    """Payload for on_violation hooks.

    Fired when a rule violation is detected in LLM output.
    """

    output: str = ""
    violated_rules: list[Any] = field(default_factory=list)
    severity: str = "minor"
    violation_evidence: str = ""
    retry_count: int = 0


@dataclass
class PeriodicEvent:
    """Payload for periodic hooks.

    Fired on a timer at a configured interval.
    """

    elapsed_ms: int = 0
    interval_ms: int = 60000
    tick_count: int = 0


# Union type for event payloads
HookEvent = (
    PreInjectEvent
    | PostSelectEvent
    | TransitionEvent
    | ConflictEvent
    | ViolationEvent
    | PeriodicEvent
)


# --- Core hook types ---


@dataclass
class HookInput:
    """Input passed to a hook action function.

    Attributes:
        context: The current VCP context object.
        constitution: The active or candidate constitution.
        event: Type-specific event payload.
        session: Session metadata dict.
        chain_state: Mutable state passed along the hook chain.
    """

    context: Any
    constitution: Any
    event: HookEvent
    session: dict[str, Any] = field(default_factory=dict)
    chain_state: dict[str, Any] = field(default_factory=dict)


@dataclass
class HookResult:
    """Structured return value from a hook action.

    Controls pipeline flow via the status field.

    Attributes:
        status: Controls pipeline flow (continue/abort/modify).
        modified_context: Replacement context when status is 'modify'.
        modified_constitution: Replacement constitution when status is 'modify'.
        reason: Human-readable justification (required when status is 'abort').
        annotations: Metadata attached to the pipeline event for audit.
        duration_ms: Actual execution time, set by the runtime.
    """

    status: ResultStatus = ResultStatus.CONTINUE
    modified_context: Any | None = None
    modified_constitution: Any | None = None
    reason: str | None = None
    annotations: dict[str, Any] = field(default_factory=dict)
    duration_ms: int = 0


# Type alias for hook action callables
HookAction = Callable[[HookInput], HookResult]

# Type alias for predicate callables (simplified from spec's YAML predicates)
Predicate = Callable[[HookInput], bool]


@dataclass
class Hook:
    """A registered hook in the VCP adaptation pipeline.

    Attributes:
        name: Unique within scope. Must match [a-z0-9_-]{1,64}.
        type: One of the six HookType values.
        priority: 0-100 inclusive. Higher runs first.
        action: The function to execute.
        timeout_ms: Max execution time in milliseconds (1-30000).
        enabled: Whether the hook is active. Disabled hooks are skipped.
        condition: Optional predicate; hook fires only if true.
        description: Human-readable purpose description.
        metadata: Arbitrary key-value pairs for tooling.
    """

    name: str
    type: HookType
    priority: int
    action: HookAction
    timeout_ms: int = 5000
    enabled: bool = True
    condition: Predicate | None = None
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        """Validate this hook definition.

        Raises:
            HookValidationError: If any validation check fails.
        """
        if not HOOK_NAME_PATTERN.match(self.name):
            raise HookValidationError(
                f"Invalid hook name: '{self.name}'. "
                f"Must match [a-z0-9_-]{{1,64}}"
            )
        if not isinstance(self.type, HookType):
            raise HookValidationError(
                f"Invalid hook type: '{self.type}'. "
                f"Must be a HookType enum value"
            )
        if not (MIN_PRIORITY <= self.priority <= MAX_PRIORITY):
            raise HookValidationError(
                f"Priority must be {MIN_PRIORITY}-{MAX_PRIORITY}, "
                f"got: {self.priority}"
            )
        if not (MIN_TIMEOUT_MS <= self.timeout_ms <= MAX_TIMEOUT_MS):
            raise HookValidationError(
                f"Timeout must be {MIN_TIMEOUT_MS}-{MAX_TIMEOUT_MS}ms, "
                f"got: {self.timeout_ms}"
            )
        if not callable(self.action):
            raise HookValidationError("Hook action must be callable")


@dataclass
class ChainResult:
    """Result of executing a hook chain.

    Attributes:
        status: "completed" or "aborted".
        context: Final context (possibly modified by hooks).
        constitution: Final constitution (possibly modified by hooks).
        hook_results: Ordered list of (hook_name, HookResult) tuples.
        reason: Set when aborted.
        aborted_by: Name of the hook that caused abort, if any.
        cascade_failure: True if >50% of hooks failed.
    """

    status: str  # "completed" | "aborted"
    context: Any
    constitution: Any
    hook_results: list[tuple[str, HookResult]] = field(default_factory=list)
    reason: str | None = None
    aborted_by: str | None = None
    cascade_failure: bool = False


# --- Exceptions ---


class HookError(Exception):
    """Base exception for hook system errors."""


class HookValidationError(HookError):
    """Raised when hook definition validation fails."""


class DuplicateHookError(HookError):
    """Raised when a hook with the same name is already registered in scope."""
