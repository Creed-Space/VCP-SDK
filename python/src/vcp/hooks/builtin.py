"""
VCP Built-in Hooks.

Reference implementations of common hook patterns:
- persona_select_hook: Select persona based on context signals
- adherence_escalate_hook: Increase adherence during emergency states
- scope_filter_hook: Skip out-of-scope constitutions
- audit_hook: Log every hook execution to an audit trail

These can be registered directly or used as templates for custom hooks.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from .types import (
    Hook,
    HookInput,
    HookResult,
    HookType,
    ResultStatus,
    TransitionEvent,
)

logger = logging.getLogger(__name__)


def _persona_select_action(hook_input: HookInput) -> HookResult:
    """Select persona based on context signals.

    Checks for children present in context and switches to a
    child-safe persona if detected. Uses chain_state to communicate
    the selected persona to downstream hooks.

    The context object is expected to have a `get` method (VCPContext style)
    or be a dict with dimension keys.
    """
    context = hook_input.context
    company_values: list[str] = []

    # Support both VCPContext and plain dict
    is_vcp_context = False
    try:
        from ..adaptation.context import Dimension, VCPContext
        if isinstance(context, VCPContext):
            company_values = context.get(Dimension.COMPANY)
            is_vcp_context = True
    except ImportError:
        pass

    if not is_vcp_context and isinstance(context, dict):
        raw = context.get("company", [])
        if isinstance(raw, str):
            company_values = [raw]
        elif isinstance(raw, list):
            company_values = raw
        else:
            company_values = []

    # Check for children indicators
    children_indicators = {"children", "child", "kids", "minors"}
    # Also check for child emoji
    children_emojis = {"\U0001f476"}  # baby emoji

    has_children = bool(
        (set(company_values) & children_indicators)
        or (set(company_values) & children_emojis)
    )

    if has_children:
        hook_input.chain_state["selected_persona"] = "nanny"
        return HookResult(
            status=ResultStatus.MODIFY,
            modified_context=context,
            annotations={"persona_selected": "nanny", "reason": "children_present"},
        )

    return HookResult(status=ResultStatus.CONTINUE)


def _adherence_escalate_action(hook_input: HookInput) -> HookResult:
    """Increase adherence level during emergency state transitions.

    Fires on on_transition events. If the transition indicates an
    emergency state, annotates the result with escalated adherence.
    """
    event = hook_input.event

    is_emergency = False

    if isinstance(event, TransitionEvent):
        emergency_states = {"emergency", "crisis", "critical"}
        is_emergency = event.new_state.lower() in emergency_states
    elif isinstance(event, dict):
        new_state = event.get("new_state", "")
        is_emergency = new_state.lower() in {"emergency", "crisis", "critical"}

    if is_emergency:
        hook_input.chain_state["adherence_escalated"] = True
        return HookResult(
            status=ResultStatus.MODIFY,
            modified_context=hook_input.context,
            annotations={
                "adherence_escalated": True,
                "reason": "emergency_state_detected",
            },
        )

    return HookResult(status=ResultStatus.CONTINUE)


def _scope_filter_action(hook_input: HookInput) -> HookResult:
    """Skip constitutions that are out of scope for the current environment.

    Checks constitution metadata for scope restrictions and compares
    against the session's environment. If out of scope, aborts injection.
    """
    constitution = hook_input.constitution
    session = hook_input.session

    if constitution is None:
        return HookResult(status=ResultStatus.CONTINUE)

    # Get scope from constitution (supports dict or object with .scope)
    scope: dict[str, Any] | None = None
    if isinstance(constitution, dict):
        scope = constitution.get("scope")
    elif hasattr(constitution, "scope"):
        scope_obj = constitution.scope
        if isinstance(scope_obj, dict):
            scope = scope_obj
        elif scope_obj is not None:
            # Try to extract environments from a Scope object
            scope = {
                "environments": getattr(scope_obj, "environments", []),
            }

    if scope is None:
        return HookResult(status=ResultStatus.CONTINUE)

    # Check environment scope
    allowed_envs = scope.get("environments", [])
    current_env = session.get("environment", "")

    if allowed_envs and current_env and current_env not in allowed_envs:
        return HookResult(
            status=ResultStatus.ABORT,
            reason=(
                f"Constitution out of scope: environment '{current_env}' "
                f"not in allowed environments {allowed_envs}"
            ),
            annotations={
                "scope_check": "failed",
                "current_environment": current_env,
                "allowed_environments": allowed_envs,
            },
        )

    return HookResult(status=ResultStatus.CONTINUE)


def _audit_action(hook_input: HookInput) -> HookResult:
    """Log hook execution details to an audit trail.

    Records timestamp, session info, event type, and context hash
    to the audit logger. Always returns continue.
    """
    session_id = hook_input.session.get("id", "unknown")
    event_type = type(hook_input.event).__name__

    audit_entry = {
        "timestamp_ms": int(time.time() * 1000),
        "session_id": session_id,
        "event_type": event_type,
        "context_hash": hash(str(hook_input.context)) if hook_input.context else 0,
        "constitution_id": _extract_id(hook_input.constitution),
        "chain_state_keys": list(hook_input.chain_state.keys()),
    }

    logger.info("hook.audit: %s", audit_entry)

    return HookResult(
        status=ResultStatus.CONTINUE,
        annotations={"audit_logged": True, "audit_entry": audit_entry},
    )


def _extract_id(obj: Any) -> str:
    """Extract an id from an object, dict, or return 'unknown'."""
    if obj is None:
        return "none"
    if isinstance(obj, dict):
        return str(obj.get("id", "unknown"))
    if hasattr(obj, "id"):
        return str(obj.id)
    return "unknown"


# --- Public hook constructors ---


def persona_select_hook(priority: int = 80, timeout_ms: int = 5000) -> Hook:
    """Create a persona selection hook.

    Fires on post_select. Selects child-safe persona when children
    are detected in the context.

    Args:
        priority: Hook priority (0-100). Default 80.
        timeout_ms: Timeout in milliseconds. Default 5000.

    Returns:
        Configured Hook instance.
    """
    return Hook(
        name="persona_select",
        type=HookType.POST_SELECT,
        priority=priority,
        action=_persona_select_action,
        timeout_ms=timeout_ms,
        description="Select persona based on context (e.g., children present -> Nanny)",
    )


def adherence_escalate_hook(priority: int = 90, timeout_ms: int = 3000) -> Hook:
    """Create an adherence escalation hook.

    Fires on on_transition. Increases adherence level during
    emergency state transitions.

    Args:
        priority: Hook priority (0-100). Default 90.
        timeout_ms: Timeout in milliseconds. Default 3000.

    Returns:
        Configured Hook instance.
    """
    return Hook(
        name="adherence_escalate",
        type=HookType.ON_TRANSITION,
        priority=priority,
        action=_adherence_escalate_action,
        timeout_ms=timeout_ms,
        description="Increase adherence level during emergency state",
    )


def scope_filter_hook(priority: int = 95, timeout_ms: int = 2000) -> Hook:
    """Create a scope filter hook.

    Fires on pre_inject. Aborts injection if the constitution
    is out of scope for the current environment.

    Args:
        priority: Hook priority (0-100). Default 95.
        timeout_ms: Timeout in milliseconds. Default 2000.

    Returns:
        Configured Hook instance.
    """
    return Hook(
        name="scope_filter",
        type=HookType.PRE_INJECT,
        priority=priority,
        action=_scope_filter_action,
        timeout_ms=timeout_ms,
        description="Skip constitutions out of scope for current environment",
    )


def audit_hook(priority: int = 10, timeout_ms: int = 2000) -> Hook:
    """Create an audit logging hook.

    Can be registered for any hook type. Logs execution details
    to the audit trail. Runs at low priority to capture the
    final state after other hooks have processed.

    Args:
        priority: Hook priority (0-100). Default 10 (runs last).
        timeout_ms: Timeout in milliseconds. Default 2000.

    Returns:
        Configured Hook instance for pre_inject by default.
        Change .type before registering for other hook types.
    """
    return Hook(
        name="audit",
        type=HookType.PRE_INJECT,
        priority=priority,
        action=_audit_action,
        timeout_ms=timeout_ms,
        description="Log every hook execution to audit trail",
    )
