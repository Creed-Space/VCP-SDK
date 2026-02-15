"""
VCP Hook Chain Executor.

Runs hook chains with timeout enforcement, error handling, predicate
evaluation, and cascading failure detection.

Spec reference: VCP_HOOKS.md sections 5, 7.
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Any

from .registry import HookRegistry
from .types import (
    ChainResult,
    Hook,
    HookInput,
    HookResult,
    HookType,
    ResultStatus,
)

logger = logging.getLogger(__name__)


class HookExecutor:
    """Execute hook chains with timeout and error handling.

    Processes hooks in priority order (descending), with deployment hooks
    running before session hooks at equal priority. Handles:
    - Predicate evaluation (skip hooks whose condition returns False)
    - Timeout enforcement per hook
    - Exception handling (fail-open: treat as "continue")
    - Abort semantics (halt chain on first abort)
    - Modify semantics (pass modified data to next hook)
    - Cascading failure detection (>50% hooks fail -> warning)
    - Chain state passing between hooks
    """

    def __init__(self, registry: HookRegistry) -> None:
        """Initialize executor with a hook registry.

        Args:
            registry: The HookRegistry to pull chains from.
        """
        self._registry = registry

    def execute(
        self,
        hook_type: HookType,
        session_id: str,
        context: Any,
        constitution: Any,
        event: Any,
        session_info: dict[str, Any] | None = None,
    ) -> ChainResult:
        """Execute the hook chain for a given type.

        Args:
            hook_type: Which hook type to fire.
            session_id: Session identifier for scope resolution.
            context: Current VCP context.
            constitution: Current/candidate constitution.
            event: Type-specific event payload.
            session_info: Optional session metadata dict.

        Returns:
            ChainResult with final context/constitution and per-hook results.
        """
        chain = self._registry.get_chain(hook_type, session_id)

        if not chain:
            return ChainResult(
                status="completed",
                context=context,
                constitution=constitution,
            )

        chain_state: dict[str, Any] = {}
        current_context = context
        current_constitution = constitution
        results: list[tuple[str, HookResult]] = []
        errors = 0
        executed = 0

        for hook in chain:
            if not hook.enabled:
                logger.debug("hook.skipped: name=%s reason=disabled", hook.name)
                continue

            # Build input for this hook
            hook_input = HookInput(
                context=current_context,
                constitution=current_constitution,
                event=event,
                session=session_info or {},
                chain_state=chain_state,
            )

            # Evaluate predicate
            if hook.condition is not None:
                try:
                    if not hook.condition(hook_input):
                        logger.debug(
                            "hook.skipped: name=%s reason=predicate_false",
                            hook.name,
                        )
                        continue
                except Exception:
                    logger.warning(
                        "hook.skipped: name=%s reason=predicate_error",
                        hook.name,
                        exc_info=True,
                    )
                    continue

            # Execute with timeout
            executed += 1
            logger.debug("hook.fired: name=%s type=%s", hook.name, hook_type.value)
            start_ns = time.monotonic_ns()

            try:
                result = self._execute_with_timeout(hook, hook_input)
            except _HookTimeoutError:
                elapsed_ms = (time.monotonic_ns() - start_ns) // 1_000_000
                logger.warning(
                    "hook.timeout: name=%s timeout_ms=%d elapsed_ms=%d",
                    hook.name,
                    hook.timeout_ms,
                    elapsed_ms,
                )
                result = HookResult(status=ResultStatus.CONTINUE)
                errors += 1
            except Exception:
                elapsed_ms = (time.monotonic_ns() - start_ns) // 1_000_000
                logger.error(
                    "hook.error: name=%s elapsed_ms=%d",
                    hook.name,
                    elapsed_ms,
                    exc_info=True,
                )
                result = HookResult(status=ResultStatus.CONTINUE)
                errors += 1

            # Record duration
            duration_ms = (time.monotonic_ns() - start_ns) // 1_000_000
            result.duration_ms = duration_ms
            results.append((hook.name, result))

            logger.debug(
                "hook.completed: name=%s status=%s duration_ms=%d",
                hook.name,
                result.status.value if isinstance(result.status, ResultStatus) else result.status,
                duration_ms,
            )

            # Process result
            if result.status == ResultStatus.ABORT:
                return ChainResult(
                    status="aborted",
                    reason=result.reason,
                    context=current_context,
                    constitution=current_constitution,
                    hook_results=results,
                    aborted_by=hook.name,
                )
            elif result.status == ResultStatus.MODIFY:
                if result.modified_context is not None:
                    current_context = result.modified_context
                if result.modified_constitution is not None:
                    current_constitution = result.modified_constitution

        # Cascading failure detection
        cascade_failure = False
        if executed > 0 and errors / executed > 0.5:
            logger.warning(
                "hook.cascade_failure: type=%s total=%d errors=%d",
                hook_type.value,
                executed,
                errors,
            )
            cascade_failure = True

        return ChainResult(
            status="completed",
            context=current_context,
            constitution=current_constitution,
            hook_results=results,
            cascade_failure=cascade_failure,
        )

    @staticmethod
    def _execute_with_timeout(hook: Hook, hook_input: HookInput) -> HookResult:
        """Execute a hook action with timeout enforcement.

        Uses a background thread to enforce the timeout. If the hook
        exceeds its timeout_ms, raises _HookTimeoutError.

        Args:
            hook: The hook to execute.
            hook_input: Input to pass to the hook action.

        Returns:
            The HookResult from the hook action.

        Raises:
            _HookTimeoutError: If execution exceeds timeout_ms.
            Exception: Any exception raised by the hook action.
        """
        result_container: list[HookResult | None] = [None]
        error_container: list[Exception | None] = [None]

        def _run() -> None:
            try:
                result_container[0] = hook.action(hook_input)
            except Exception as exc:
                error_container[0] = exc

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()
        thread.join(timeout=hook.timeout_ms / 1000.0)

        if thread.is_alive():
            # Thread exceeded timeout - we can't forcibly kill it,
            # but we treat it as timed out per spec
            raise _HookTimeoutError(
                f"Hook '{hook.name}' exceeded timeout of {hook.timeout_ms}ms"
            )

        if error_container[0] is not None:
            raise error_container[0]

        if result_container[0] is None:
            # Hook returned None - treat as continue per spec (invalid result)
            logger.warning(
                "hook.invalid_result: name=%s returned None, treating as continue",
                hook.name,
            )
            return HookResult(status=ResultStatus.CONTINUE)

        return result_container[0]


class _HookTimeoutError(Exception):
    """Internal exception for hook timeout. Not part of public API."""
