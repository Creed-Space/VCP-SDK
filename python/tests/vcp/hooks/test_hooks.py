"""Tests for VCP Hook System.

Covers registration, validation, chain execution, timeout handling,
error recovery, built-in hooks, and integration scenarios.
"""

from __future__ import annotations

import time

import pytest

from vcp.hooks import (
    ChainResult,
    DuplicateHookError,
    Hook,
    HookExecutor,
    HookInput,
    HookRegistry,
    HookResult,
    HookType,
    HookValidationError,
    PostSelectEvent,
    PreInjectEvent,
    ResultStatus,
    TransitionEvent,
    adherence_escalate_hook,
    audit_hook,
    persona_select_hook,
    scope_filter_hook,
)


# --- Fixtures ---


@pytest.fixture
def registry() -> HookRegistry:
    """Create a fresh hook registry."""
    return HookRegistry()


@pytest.fixture
def executor(registry: HookRegistry) -> HookExecutor:
    """Create a hook executor backed by the registry."""
    return HookExecutor(registry)


def _make_hook(
    name: str = "test_hook",
    hook_type: HookType = HookType.PRE_INJECT,
    priority: int = 50,
    action: object | None = None,
    timeout_ms: int = 5000,
    enabled: bool = True,
    condition: object | None = None,
) -> Hook:
    """Helper to create a hook with defaults."""
    if action is None:
        action = lambda inp: HookResult(status=ResultStatus.CONTINUE)
    return Hook(
        name=name,
        type=hook_type,
        priority=priority,
        action=action,
        timeout_ms=timeout_ms,
        enabled=enabled,
        condition=condition,
    )


# =============================================================================
# 1. Registration and Deregistration
# =============================================================================


class TestHookRegistration:
    """Test hook registration and deregistration."""

    def test_register_deployment_hook(self, registry: HookRegistry) -> None:
        """Deployment hook should be registered and retrievable."""
        hook = _make_hook(name="deploy-hook")
        registry.register(hook, scope="deployment")

        chain = registry.get_chain(HookType.PRE_INJECT, session_id="s1")
        assert len(chain) == 1
        assert chain[0].name == "deploy-hook"

    def test_register_session_hook(self, registry: HookRegistry) -> None:
        """Session hook should be registered for a specific session."""
        hook = _make_hook(name="session-hook")
        registry.register(hook, scope="session", session_id="s1")

        chain_s1 = registry.get_chain(HookType.PRE_INJECT, session_id="s1")
        chain_s2 = registry.get_chain(HookType.PRE_INJECT, session_id="s2")
        assert len(chain_s1) == 1
        assert len(chain_s2) == 0

    def test_deregister_hook(self, registry: HookRegistry) -> None:
        """Deregistered hook should not appear in chains."""
        hook = _make_hook(name="removable")
        registry.register(hook, scope="deployment")
        assert registry.deregister("removable", scope="deployment")

        chain = registry.get_chain(HookType.PRE_INJECT, session_id="s1")
        assert len(chain) == 0

    def test_deregister_nonexistent_returns_false(self, registry: HookRegistry) -> None:
        """Deregistering a non-existent hook should return False."""
        assert not registry.deregister("ghost", scope="deployment")

    def test_duplicate_name_rejected(self, registry: HookRegistry) -> None:
        """Registering two hooks with the same name in the same scope should fail."""
        hook1 = _make_hook(name="unique-hook")
        hook2 = _make_hook(name="unique-hook", priority=90)

        registry.register(hook1, scope="deployment")
        with pytest.raises(DuplicateHookError):
            registry.register(hook2, scope="deployment")

    def test_same_name_different_scopes_allowed(self, registry: HookRegistry) -> None:
        """Same name in deployment and session scopes should be allowed."""
        hook_deploy = _make_hook(name="shared-name", priority=50)
        hook_session = _make_hook(name="shared-name", priority=40)

        registry.register(hook_deploy, scope="deployment")
        registry.register(hook_session, scope="session", session_id="s1")

        chain = registry.get_chain(HookType.PRE_INJECT, session_id="s1")
        assert len(chain) == 2

    def test_session_scope_requires_session_id(self, registry: HookRegistry) -> None:
        """Registering a session hook without session_id should raise ValueError."""
        hook = _make_hook(name="no-session")
        with pytest.raises(ValueError, match="session_id"):
            registry.register(hook, scope="session")

    def test_clear_session(self, registry: HookRegistry) -> None:
        """clear_session should remove all hooks for that session."""
        registry.register(_make_hook(name="s-hook"), scope="session", session_id="s1")
        registry.clear_session("s1")
        chain = registry.get_chain(HookType.PRE_INJECT, session_id="s1")
        assert len(chain) == 0


# =============================================================================
# 2. Validation
# =============================================================================


class TestHookValidation:
    """Test hook definition validation."""

    def test_valid_name_accepted(self) -> None:
        """Valid names should pass validation."""
        for name in ["hook-1", "my_hook", "a", "x" * 64, "abc-def_123"]:
            hook = _make_hook(name=name)
            hook.validate()  # Should not raise

    def test_invalid_name_rejected(self) -> None:
        """Invalid names should raise HookValidationError."""
        invalid_names = [
            "",  # empty
            "UPPERCASE",  # uppercase
            "has spaces",  # spaces
            "x" * 65,  # too long
            "special!char",  # special chars
            "dots.not.allowed",  # dots
        ]
        for name in invalid_names:
            hook = _make_hook(name=name)
            with pytest.raises(HookValidationError):
                hook.validate()

    def test_priority_bounds(self) -> None:
        """Priority outside 0-100 should raise HookValidationError."""
        with pytest.raises(HookValidationError):
            _make_hook(priority=-1).validate()
        with pytest.raises(HookValidationError):
            _make_hook(priority=101).validate()

        # Boundary values should be accepted
        _make_hook(priority=0).validate()
        _make_hook(priority=100).validate()

    def test_timeout_bounds(self) -> None:
        """Timeout outside 1-30000 should raise HookValidationError."""
        with pytest.raises(HookValidationError):
            _make_hook(timeout_ms=0).validate()
        with pytest.raises(HookValidationError):
            _make_hook(timeout_ms=30001).validate()

        # Boundary values should be accepted
        _make_hook(timeout_ms=1).validate()
        _make_hook(timeout_ms=30000).validate()

    def test_non_callable_action_rejected(self) -> None:
        """Non-callable action should raise HookValidationError."""
        hook = Hook(
            name="bad-action",
            type=HookType.PRE_INJECT,
            priority=50,
            action="not a function",  # type: ignore[arg-type]
            timeout_ms=5000,
        )
        with pytest.raises(HookValidationError, match="callable"):
            hook.validate()


# =============================================================================
# 3. Priority Ordering
# =============================================================================


class TestPriorityOrdering:
    """Test that hooks execute in correct priority order."""

    def test_higher_priority_runs_first(
        self, registry: HookRegistry, executor: HookExecutor
    ) -> None:
        """Higher priority hooks should execute before lower ones."""
        order: list[str] = []

        def make_action(name: str):
            def action(inp: HookInput) -> HookResult:
                order.append(name)
                return HookResult(status=ResultStatus.CONTINUE)
            return action

        registry.register(_make_hook(name="low", priority=10, action=make_action("low")))
        registry.register(_make_hook(name="high", priority=90, action=make_action("high")))
        registry.register(_make_hook(name="mid", priority=50, action=make_action("mid")))

        executor.execute(HookType.PRE_INJECT, "s1", None, None, PreInjectEvent())
        assert order == ["high", "mid", "low"]

    def test_deployment_before_session_at_same_priority(
        self, registry: HookRegistry, executor: HookExecutor
    ) -> None:
        """Deployment hooks run before session hooks at the same priority."""
        order: list[str] = []

        def make_action(name: str):
            def action(inp: HookInput) -> HookResult:
                order.append(name)
                return HookResult(status=ResultStatus.CONTINUE)
            return action

        registry.register(
            _make_hook(name="deploy", priority=50, action=make_action("deploy")),
            scope="deployment",
        )
        registry.register(
            _make_hook(name="session", priority=50, action=make_action("session")),
            scope="session",
            session_id="s1",
        )

        executor.execute(HookType.PRE_INJECT, "s1", None, None, PreInjectEvent())
        assert order == ["deploy", "session"]


# =============================================================================
# 4. Chain Execution Semantics
# =============================================================================


class TestChainExecution:
    """Test chain execution: continue, abort, modify."""

    def test_continue_passes_through(
        self, registry: HookRegistry, executor: HookExecutor
    ) -> None:
        """Hooks returning continue should not alter context."""
        original_ctx = {"key": "original"}
        registry.register(_make_hook(name="noop"))

        result = executor.execute(
            HookType.PRE_INJECT, "s1", original_ctx, None, PreInjectEvent()
        )
        assert result.status == "completed"
        assert result.context == original_ctx

    def test_abort_halts_chain(
        self, registry: HookRegistry, executor: HookExecutor
    ) -> None:
        """Abort should halt chain and return aborted status."""
        order: list[str] = []

        def abort_action(inp: HookInput) -> HookResult:
            order.append("abort")
            return HookResult(status=ResultStatus.ABORT, reason="blocked")

        def after_action(inp: HookInput) -> HookResult:
            order.append("after")
            return HookResult(status=ResultStatus.CONTINUE)

        registry.register(
            _make_hook(name="aborter", priority=90, action=abort_action)
        )
        registry.register(
            _make_hook(name="after", priority=10, action=after_action)
        )

        result = executor.execute(
            HookType.PRE_INJECT, "s1", None, None, PreInjectEvent()
        )
        assert result.status == "aborted"
        assert result.aborted_by == "aborter"
        assert result.reason == "blocked"
        assert order == ["abort"]  # "after" should NOT have run

    def test_modify_transforms_context(
        self, registry: HookRegistry, executor: HookExecutor
    ) -> None:
        """Modify should pass modified context to next hook."""
        received_contexts: list[object] = []

        def modifier(inp: HookInput) -> HookResult:
            return HookResult(
                status=ResultStatus.MODIFY,
                modified_context={"modified": True},
            )

        def checker(inp: HookInput) -> HookResult:
            received_contexts.append(inp.context)
            return HookResult(status=ResultStatus.CONTINUE)

        registry.register(
            _make_hook(name="modifier", priority=90, action=modifier)
        )
        registry.register(
            _make_hook(name="checker", priority=10, action=checker)
        )

        result = executor.execute(
            HookType.PRE_INJECT, "s1", {"original": True}, None, PreInjectEvent()
        )

        assert result.context == {"modified": True}
        assert received_contexts[0] == {"modified": True}

    def test_modify_transforms_constitution(
        self, registry: HookRegistry, executor: HookExecutor
    ) -> None:
        """Modify should also allow constitution replacement."""

        def modifier(inp: HookInput) -> HookResult:
            return HookResult(
                status=ResultStatus.MODIFY,
                modified_constitution={"id": "replacement"},
            )

        registry.register(
            _make_hook(name="const-mod", priority=50, action=modifier)
        )

        result = executor.execute(
            HookType.PRE_INJECT, "s1", None, {"id": "original"}, PreInjectEvent()
        )
        assert result.constitution == {"id": "replacement"}

    def test_empty_chain_completes(
        self, registry: HookRegistry, executor: HookExecutor
    ) -> None:
        """Empty chain should return completed with original context."""
        result = executor.execute(
            HookType.PRE_INJECT, "s1", {"ctx": 1}, {"const": 1}, PreInjectEvent()
        )
        assert result.status == "completed"
        assert result.context == {"ctx": 1}
        assert result.constitution == {"const": 1}
        assert result.hook_results == []


# =============================================================================
# 5. Predicate / Condition Filtering
# =============================================================================


class TestPredicateEvaluation:
    """Test hook predicate (condition) evaluation."""

    def test_condition_true_fires_hook(
        self, registry: HookRegistry, executor: HookExecutor
    ) -> None:
        """Hook with condition=True should fire."""
        fired: list[bool] = []

        def action(inp: HookInput) -> HookResult:
            fired.append(True)
            return HookResult(status=ResultStatus.CONTINUE)

        registry.register(
            _make_hook(
                name="cond-true",
                action=action,
                condition=lambda inp: True,
            )
        )

        executor.execute(HookType.PRE_INJECT, "s1", None, None, PreInjectEvent())
        assert fired == [True]

    def test_condition_false_skips_hook(
        self, registry: HookRegistry, executor: HookExecutor
    ) -> None:
        """Hook with condition=False should be skipped."""
        fired: list[bool] = []

        def action(inp: HookInput) -> HookResult:
            fired.append(True)
            return HookResult(status=ResultStatus.CONTINUE)

        registry.register(
            _make_hook(
                name="cond-false",
                action=action,
                condition=lambda inp: False,
            )
        )

        executor.execute(HookType.PRE_INJECT, "s1", None, None, PreInjectEvent())
        assert fired == []

    def test_condition_exception_skips_hook(
        self, registry: HookRegistry, executor: HookExecutor
    ) -> None:
        """If predicate throws, hook should be skipped (not crash chain)."""
        fired: list[bool] = []

        def action(inp: HookInput) -> HookResult:
            fired.append(True)
            return HookResult(status=ResultStatus.CONTINUE)

        def bad_condition(inp: HookInput) -> bool:
            raise RuntimeError("predicate boom")

        registry.register(
            _make_hook(name="cond-err", action=action, condition=bad_condition)
        )

        result = executor.execute(
            HookType.PRE_INJECT, "s1", None, None, PreInjectEvent()
        )
        assert result.status == "completed"
        assert fired == []


# =============================================================================
# 6. Timeout Handling
# =============================================================================


class TestTimeoutHandling:
    """Test hook timeout enforcement."""

    def test_slow_hook_treated_as_continue(
        self, registry: HookRegistry, executor: HookExecutor
    ) -> None:
        """Hook exceeding timeout should be treated as continue."""

        def slow_action(inp: HookInput) -> HookResult:
            time.sleep(2)  # 2 seconds, well over timeout
            return HookResult(status=ResultStatus.ABORT, reason="should not reach")

        registry.register(
            _make_hook(name="slow", action=slow_action, timeout_ms=100)
        )

        result = executor.execute(
            HookType.PRE_INJECT, "s1", {"ctx": 1}, None, PreInjectEvent()
        )
        # Should complete, not abort
        assert result.status == "completed"
        assert result.context == {"ctx": 1}

    def test_timeout_chain_continues(
        self, registry: HookRegistry, executor: HookExecutor
    ) -> None:
        """Chain should continue after a timed-out hook."""
        order: list[str] = []

        def slow_action(inp: HookInput) -> HookResult:
            time.sleep(2)
            return HookResult(status=ResultStatus.CONTINUE)

        def fast_action(inp: HookInput) -> HookResult:
            order.append("fast")
            return HookResult(status=ResultStatus.CONTINUE)

        registry.register(
            _make_hook(name="slow", priority=90, action=slow_action, timeout_ms=100)
        )
        registry.register(
            _make_hook(name="fast", priority=10, action=fast_action, timeout_ms=5000)
        )

        result = executor.execute(
            HookType.PRE_INJECT, "s1", None, None, PreInjectEvent()
        )
        assert result.status == "completed"
        assert order == ["fast"]


# =============================================================================
# 7. Exception Handling
# =============================================================================


class TestExceptionHandling:
    """Test hook exception handling (fail-open)."""

    def test_exception_treated_as_continue(
        self, registry: HookRegistry, executor: HookExecutor
    ) -> None:
        """Hook raising an exception should be treated as continue."""

        def bad_action(inp: HookInput) -> HookResult:
            raise ValueError("hook exploded")

        registry.register(_make_hook(name="bad", action=bad_action))

        result = executor.execute(
            HookType.PRE_INJECT, "s1", {"safe": True}, None, PreInjectEvent()
        )
        assert result.status == "completed"
        assert result.context == {"safe": True}

    def test_exception_chain_continues(
        self, registry: HookRegistry, executor: HookExecutor
    ) -> None:
        """Chain should continue past a hook that throws."""
        order: list[str] = []

        def bad_action(inp: HookInput) -> HookResult:
            raise RuntimeError("boom")

        def good_action(inp: HookInput) -> HookResult:
            order.append("good")
            return HookResult(status=ResultStatus.CONTINUE)

        registry.register(
            _make_hook(name="bad", priority=90, action=bad_action)
        )
        registry.register(
            _make_hook(name="good", priority=10, action=good_action)
        )

        result = executor.execute(
            HookType.PRE_INJECT, "s1", None, None, PreInjectEvent()
        )
        assert result.status == "completed"
        assert order == ["good"]


# =============================================================================
# 8. Cascading Failure Detection
# =============================================================================


class TestCascadingFailure:
    """Test cascading failure detection (>50% hooks fail)."""

    def test_cascade_failure_detected(
        self, registry: HookRegistry, executor: HookExecutor
    ) -> None:
        """If >50% of hooks fail, cascade_failure should be True."""

        def bad_action(inp: HookInput) -> HookResult:
            raise RuntimeError("fail")

        def good_action(inp: HookInput) -> HookResult:
            return HookResult(status=ResultStatus.CONTINUE)

        # 2 bad, 1 good => 66% failure rate
        registry.register(
            _make_hook(name="bad-1", priority=90, action=bad_action)
        )
        registry.register(
            _make_hook(name="bad-2", priority=80, action=bad_action)
        )
        registry.register(
            _make_hook(name="good-1", priority=10, action=good_action)
        )

        result = executor.execute(
            HookType.PRE_INJECT, "s1", None, None, PreInjectEvent()
        )
        assert result.cascade_failure is True

    def test_no_cascade_failure_below_threshold(
        self, registry: HookRegistry, executor: HookExecutor
    ) -> None:
        """If <=50% of hooks fail, cascade_failure should be False."""

        def bad_action(inp: HookInput) -> HookResult:
            raise RuntimeError("fail")

        def good_action(inp: HookInput) -> HookResult:
            return HookResult(status=ResultStatus.CONTINUE)

        # 1 bad, 2 good => 33% failure rate
        registry.register(
            _make_hook(name="bad-1", priority=90, action=bad_action)
        )
        registry.register(
            _make_hook(name="good-1", priority=80, action=good_action)
        )
        registry.register(
            _make_hook(name="good-2", priority=10, action=good_action)
        )

        result = executor.execute(
            HookType.PRE_INJECT, "s1", None, None, PreInjectEvent()
        )
        assert result.cascade_failure is False


# =============================================================================
# 9. Enabled/Disabled Hooks
# =============================================================================


class TestEnabledDisabled:
    """Test that disabled hooks are skipped."""

    def test_disabled_hook_skipped(
        self, registry: HookRegistry, executor: HookExecutor
    ) -> None:
        """Disabled hook should not fire."""
        fired: list[bool] = []

        def action(inp: HookInput) -> HookResult:
            fired.append(True)
            return HookResult(status=ResultStatus.CONTINUE)

        registry.register(
            _make_hook(name="disabled", action=action, enabled=False)
        )

        executor.execute(HookType.PRE_INJECT, "s1", None, None, PreInjectEvent())
        assert fired == []

    def test_enabled_hook_fires(
        self, registry: HookRegistry, executor: HookExecutor
    ) -> None:
        """Enabled hook should fire normally."""
        fired: list[bool] = []

        def action(inp: HookInput) -> HookResult:
            fired.append(True)
            return HookResult(status=ResultStatus.CONTINUE)

        registry.register(
            _make_hook(name="enabled", action=action, enabled=True)
        )

        executor.execute(HookType.PRE_INJECT, "s1", None, None, PreInjectEvent())
        assert fired == [True]


# =============================================================================
# 10. Chain State Passing
# =============================================================================


class TestChainState:
    """Test mutable chain_state passing between hooks."""

    def test_chain_state_flows_between_hooks(
        self, registry: HookRegistry, executor: HookExecutor
    ) -> None:
        """chain_state set by one hook should be visible to the next."""
        received_state: list[dict] = []

        def writer(inp: HookInput) -> HookResult:
            inp.chain_state["compliance_checked"] = True
            return HookResult(status=ResultStatus.CONTINUE)

        def reader(inp: HookInput) -> HookResult:
            received_state.append(dict(inp.chain_state))
            return HookResult(status=ResultStatus.CONTINUE)

        registry.register(
            _make_hook(name="writer", priority=90, action=writer)
        )
        registry.register(
            _make_hook(name="reader", priority=10, action=reader)
        )

        executor.execute(HookType.PRE_INJECT, "s1", None, None, PreInjectEvent())
        assert received_state[0]["compliance_checked"] is True

    def test_chain_state_isolated_between_executions(
        self, registry: HookRegistry, executor: HookExecutor
    ) -> None:
        """chain_state should be fresh for each chain execution."""
        states: list[dict] = []

        def collector(inp: HookInput) -> HookResult:
            states.append(dict(inp.chain_state))
            inp.chain_state["run"] = len(states)
            return HookResult(status=ResultStatus.CONTINUE)

        registry.register(_make_hook(name="collector", action=collector))

        executor.execute(HookType.PRE_INJECT, "s1", None, None, PreInjectEvent())
        executor.execute(HookType.PRE_INJECT, "s1", None, None, PreInjectEvent())

        # Each execution should start with empty chain_state
        assert states[0] == {}
        assert states[1] == {}


# =============================================================================
# 11. HookType Enum
# =============================================================================


class TestHookTypeEnum:
    """Test HookType enum values."""

    def test_all_hook_types_defined(self) -> None:
        """All six hook types from the spec should exist."""
        assert HookType.PRE_INJECT.value == "pre_inject"
        assert HookType.POST_SELECT.value == "post_select"
        assert HookType.ON_TRANSITION.value == "on_transition"
        assert HookType.ON_CONFLICT.value == "on_conflict"
        assert HookType.ON_VIOLATION.value == "on_violation"
        assert HookType.PERIODIC.value == "periodic"

    def test_hook_type_count(self) -> None:
        """There should be exactly 6 hook types."""
        assert len(HookType) == 6


# =============================================================================
# 12. Built-in Hooks
# =============================================================================


class TestBuiltinPersonaSelect:
    """Test the built-in persona_select_hook."""

    def test_persona_select_children_present(
        self, registry: HookRegistry, executor: HookExecutor
    ) -> None:
        """Should select nanny persona when children are in context."""
        hook = persona_select_hook()
        registry.register(hook)

        context = {"company": ["children", "family"]}
        result = executor.execute(
            HookType.POST_SELECT, "s1", context, None, PostSelectEvent()
        )
        assert result.status == "completed"
        # Check that the hook modified with persona annotation
        assert any(
            r.annotations.get("persona_selected") == "nanny"
            for _, r in result.hook_results
        )

    def test_persona_select_no_children(
        self, registry: HookRegistry, executor: HookExecutor
    ) -> None:
        """Should return continue when no children are present."""
        hook = persona_select_hook()
        registry.register(hook)

        context = {"company": ["colleagues"]}
        result = executor.execute(
            HookType.POST_SELECT, "s1", context, None, PostSelectEvent()
        )
        assert result.status == "completed"
        # Should not have persona annotation
        for _, r in result.hook_results:
            assert r.annotations.get("persona_selected") is None


class TestBuiltinAdherenceEscalate:
    """Test the built-in adherence_escalate_hook."""

    def test_escalate_on_emergency(
        self, registry: HookRegistry, executor: HookExecutor
    ) -> None:
        """Should escalate adherence on emergency transition."""
        hook = adherence_escalate_hook()
        registry.register(hook)

        event = TransitionEvent(
            previous_state="normal",
            new_state="emergency",
            trigger="alarm",
        )
        result = executor.execute(
            HookType.ON_TRANSITION, "s1", None, None, event
        )
        assert any(
            r.annotations.get("adherence_escalated") is True
            for _, r in result.hook_results
        )

    def test_no_escalate_on_normal(
        self, registry: HookRegistry, executor: HookExecutor
    ) -> None:
        """Should not escalate on non-emergency transition."""
        hook = adherence_escalate_hook()
        registry.register(hook)

        event = TransitionEvent(
            previous_state="normal",
            new_state="professional",
            trigger="work_hours",
        )
        result = executor.execute(
            HookType.ON_TRANSITION, "s1", None, None, event
        )
        for _, r in result.hook_results:
            assert r.annotations.get("adherence_escalated") is None


class TestBuiltinAudit:
    """Test the built-in audit_hook."""

    def test_audit_logs_execution(
        self, registry: HookRegistry, executor: HookExecutor
    ) -> None:
        """Audit hook should annotate with audit_logged=True."""
        hook = audit_hook()
        registry.register(hook)

        result = executor.execute(
            HookType.PRE_INJECT,
            "s1",
            {"some": "context"},
            {"id": "const-1"},
            PreInjectEvent(),
            session_info={"id": "s1"},
        )
        assert result.status == "completed"
        assert any(
            r.annotations.get("audit_logged") is True
            for _, r in result.hook_results
        )

    def test_audit_captures_session_id(
        self, registry: HookRegistry, executor: HookExecutor
    ) -> None:
        """Audit entry should include session_id."""
        hook = audit_hook()
        registry.register(hook)

        result = executor.execute(
            HookType.PRE_INJECT,
            "s1",
            None,
            None,
            PreInjectEvent(),
            session_info={"id": "test-session-42"},
        )

        for _, r in result.hook_results:
            entry = r.annotations.get("audit_entry", {})
            if entry:
                assert entry["session_id"] == "test-session-42"


class TestBuiltinScopeFilter:
    """Test the built-in scope_filter_hook."""

    def test_scope_filter_blocks_out_of_scope(
        self, registry: HookRegistry, executor: HookExecutor
    ) -> None:
        """Should abort when environment is not in allowed list."""
        hook = scope_filter_hook()
        registry.register(hook)

        constitution = {"id": "c1", "scope": {"environments": ["production"]}}
        result = executor.execute(
            HookType.PRE_INJECT,
            "s1",
            None,
            constitution,
            PreInjectEvent(),
            session_info={"environment": "staging"},
        )
        assert result.status == "aborted"
        assert "out of scope" in (result.reason or "").lower()

    def test_scope_filter_allows_in_scope(
        self, registry: HookRegistry, executor: HookExecutor
    ) -> None:
        """Should continue when environment matches."""
        hook = scope_filter_hook()
        registry.register(hook)

        constitution = {"id": "c1", "scope": {"environments": ["production"]}}
        result = executor.execute(
            HookType.PRE_INJECT,
            "s1",
            None,
            constitution,
            PreInjectEvent(),
            session_info={"environment": "production"},
        )
        assert result.status == "completed"


# =============================================================================
# 13. ResultStatus Enum
# =============================================================================


class TestResultStatus:
    """Test ResultStatus enum."""

    def test_result_status_values(self) -> None:
        """All result statuses should be defined."""
        assert ResultStatus.CONTINUE.value == "continue"
        assert ResultStatus.ABORT.value == "abort"
        assert ResultStatus.MODIFY.value == "modify"

    def test_result_status_count(self) -> None:
        """There should be exactly 3 result statuses."""
        assert len(ResultStatus) == 3


# =============================================================================
# 14. Hook Result Duration
# =============================================================================


class TestHookResultDuration:
    """Test that hook result duration_ms is set by the executor."""

    def test_duration_set_on_result(
        self, registry: HookRegistry, executor: HookExecutor
    ) -> None:
        """Executor should set duration_ms on hook results."""

        def action(inp: HookInput) -> HookResult:
            return HookResult(status=ResultStatus.CONTINUE)

        registry.register(_make_hook(name="timed", action=action))

        result = executor.execute(
            HookType.PRE_INJECT, "s1", None, None, PreInjectEvent()
        )
        assert len(result.hook_results) == 1
        _, hook_result = result.hook_results[0]
        assert hook_result.duration_ms >= 0


# =============================================================================
# 15. Multiple Hook Types Independence
# =============================================================================


class TestHookTypeIndependence:
    """Test that hooks of different types don't interfere."""

    def test_different_types_independent(
        self, registry: HookRegistry, executor: HookExecutor
    ) -> None:
        """Hooks registered for different types should not cross-fire."""
        pre_fired: list[bool] = []
        post_fired: list[bool] = []

        def pre_action(inp: HookInput) -> HookResult:
            pre_fired.append(True)
            return HookResult(status=ResultStatus.CONTINUE)

        def post_action(inp: HookInput) -> HookResult:
            post_fired.append(True)
            return HookResult(status=ResultStatus.CONTINUE)

        registry.register(
            _make_hook(name="pre", hook_type=HookType.PRE_INJECT, action=pre_action)
        )
        registry.register(
            _make_hook(name="post", hook_type=HookType.POST_SELECT, action=post_action)
        )

        executor.execute(HookType.PRE_INJECT, "s1", None, None, PreInjectEvent())
        assert pre_fired == [True]
        assert post_fired == []
