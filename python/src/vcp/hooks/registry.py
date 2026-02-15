"""
VCP Hook Registry.

Central registry managing hook registration, deregistration, and chain
assembly across deployment and session scopes.

Deployment hooks execute before session hooks at the same priority level,
ensuring organizational policies take precedence.

Spec reference: VCP_HOOKS.md section 6.
"""

from __future__ import annotations

import logging
import threading
from typing import Any

from .types import (
    DuplicateHookError,
    Hook,
    HookType,
    HookValidationError,
)

logger = logging.getLogger(__name__)


class HookRegistry:
    """Central hook registry with deployment and session scopes.

    Thread-safe registration and deregistration. Chains are assembled
    on-demand by merging deployment and session hooks in priority order.
    """

    def __init__(self) -> None:
        self._deployment_hooks: dict[HookType, list[Hook]] = {
            t: [] for t in HookType
        }
        self._session_hooks: dict[str, dict[HookType, list[Hook]]] = {}
        self._lock = threading.Lock()

    def register(
        self,
        hook: Hook,
        scope: str = "deployment",
        session_id: str | None = None,
    ) -> None:
        """Register a hook.

        Args:
            hook: The hook to register.
            scope: "deployment" or "session".
            session_id: Required when scope is "session".

        Raises:
            HookValidationError: If hook definition is invalid.
            DuplicateHookError: If a hook with the same name exists in scope.
            ValueError: If scope is unknown or session_id missing for session scope.
        """
        hook.validate()

        if scope == "session" and session_id is None:
            raise ValueError("session_id is required for session-scoped hooks")

        with self._lock:
            target = self._get_target_list(hook.type, scope, session_id)

            if any(h.name == hook.name for h in target):
                raise DuplicateHookError(
                    f"Hook '{hook.name}' already registered in {scope}"
                    + (f" (session={session_id})" if session_id else "")
                )

            target.append(hook)
            target.sort(key=lambda h: h.priority, reverse=True)

        logger.info(
            "hook.registered: name=%s type=%s scope=%s priority=%d",
            hook.name,
            hook.type.value,
            scope,
            hook.priority,
        )

    def deregister(
        self,
        name: str,
        scope: str = "deployment",
        session_id: str | None = None,
    ) -> bool:
        """Remove a hook by name.

        Args:
            name: Name of the hook to remove.
            scope: "deployment" or "session".
            session_id: Required when scope is "session".

        Returns:
            True if the hook was found and removed, False otherwise.
        """
        found = False
        with self._lock:
            if scope == "deployment":
                for hook_type in HookType:
                    before = len(self._deployment_hooks[hook_type])
                    self._deployment_hooks[hook_type] = [
                        h for h in self._deployment_hooks[hook_type] if h.name != name
                    ]
                    if len(self._deployment_hooks[hook_type]) < before:
                        found = True
            elif scope == "session" and session_id is not None:
                session_hooks = self._session_hooks.get(session_id, {})
                for hook_type in HookType:
                    hooks = session_hooks.get(hook_type, [])
                    before = len(hooks)
                    session_hooks[hook_type] = [h for h in hooks if h.name != name]
                    if len(session_hooks.get(hook_type, [])) < before:
                        found = True

        if found:
            logger.info(
                "hook.deregistered: name=%s scope=%s",
                name,
                scope,
            )
        return found

    def get_chain(self, hook_type: HookType, session_id: str) -> list[Hook]:
        """Return the ordered hook chain for a given type and session.

        Deployment hooks run before session hooks at the same priority level.
        All hooks are sorted by priority descending.

        Args:
            hook_type: The hook type to get the chain for.
            session_id: The session to include session-scoped hooks from.

        Returns:
            Merged, priority-ordered list of hooks.
        """
        with self._lock:
            deployment = list(self._deployment_hooks.get(hook_type, []))
            session = list(
                self._session_hooks.get(session_id, {}).get(hook_type, [])
            )

        return self._merge_by_priority(deployment, session)

    def get_registered_count(
        self,
        scope: str = "deployment",
        session_id: str | None = None,
    ) -> int:
        """Get total number of registered hooks in a scope.

        Args:
            scope: "deployment" or "session".
            session_id: Required for session scope.

        Returns:
            Total hook count.
        """
        with self._lock:
            if scope == "deployment":
                return sum(
                    len(hooks) for hooks in self._deployment_hooks.values()
                )
            elif scope == "session" and session_id is not None:
                session_hooks = self._session_hooks.get(session_id, {})
                return sum(len(hooks) for hooks in session_hooks.values())
        return 0

    def clear_session(self, session_id: str) -> None:
        """Remove all hooks for a session.

        Args:
            session_id: Session to clear.
        """
        with self._lock:
            self._session_hooks.pop(session_id, None)
        logger.info("hook.session_cleared: session_id=%s", session_id)

    def _get_target_list(
        self,
        hook_type: HookType,
        scope: str,
        session_id: str | None,
    ) -> list[Hook]:
        """Get the mutable list to register into.

        Must be called under self._lock.
        """
        if scope == "deployment":
            return self._deployment_hooks[hook_type]
        elif scope == "session":
            if session_id is None:
                raise ValueError("session_id required for session scope")
            if session_id not in self._session_hooks:
                self._session_hooks[session_id] = {t: [] for t in HookType}
            return self._session_hooks[session_id][hook_type]
        else:
            raise ValueError(f"Unknown scope: {scope}")

    @staticmethod
    def _merge_by_priority(
        deployment: list[Hook],
        session: list[Hook],
    ) -> list[Hook]:
        """Merge two sorted lists, preferring deployment hooks at equal priority.

        Both input lists must be sorted by priority descending.

        Args:
            deployment: Deployment-scoped hooks (sorted).
            session: Session-scoped hooks (sorted).

        Returns:
            Merged list with deployment hooks first at equal priority.
        """
        result: list[Hook] = []
        d_idx, s_idx = 0, 0

        while d_idx < len(deployment) and s_idx < len(session):
            if deployment[d_idx].priority >= session[s_idx].priority:
                result.append(deployment[d_idx])
                d_idx += 1
            else:
                result.append(session[s_idx])
                s_idx += 1

        result.extend(deployment[d_idx:])
        result.extend(session[s_idx:])
        return result
