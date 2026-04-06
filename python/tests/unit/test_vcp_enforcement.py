"""
Tests for vcp.enforcement — PDP plugin enforcement for VCP bundles.

Verifies:
    - PDPEnforcer orchestration (priority ordering, fail-closed)
    - RefusalBoundaryPlugin (bundle verification enforcement)
    - AdherenceLevelPlugin (minimum adherence level)
    - BundleExpiryPlugin (expired bundle blocking)
    - Plugin crash handling (fail-closed by default)
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest

from vcp.enforcement import (
    AdherenceLevelPlugin,
    BundleExpiryPlugin,
    DecisionType,
    EvaluationContext,
    PDPDecision,
    PDPEnforcer,
    PDPPlugin,
    RefusalBoundaryPlugin,
)
from vcp.types import EnforcementMode, VerificationResult

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_bundle(
    expired: bool = False,
    adherence: int | None = None,
) -> MagicMock:
    """Create a minimal mock bundle."""
    bundle = MagicMock()
    bundle.manifest.metadata = {}
    if adherence is not None:
        bundle.manifest.metadata["adherence_level"] = adherence

    now = datetime.now(timezone.utc)
    if expired:
        bundle.manifest.timestamps.exp = now - timedelta(hours=1)
    else:
        bundle.manifest.timestamps.exp = now + timedelta(hours=1)

    return bundle


class _CrashPlugin(PDPPlugin):
    """Plugin that always raises."""

    @property
    def plugin_id(self) -> str:
        return "crash"

    def evaluate(self, ctx: EvaluationContext) -> PDPDecision | None:
        raise RuntimeError("boom")


class _AllowPlugin(PDPPlugin):
    """Plugin that always abstains (returns None)."""

    @property
    def plugin_id(self) -> str:
        return "allow"

    def evaluate(self, ctx: EvaluationContext) -> PDPDecision | None:
        return None


class _BlockPlugin(PDPPlugin):
    """Plugin that always blocks."""

    @property
    def plugin_id(self) -> str:
        return "block"

    @property
    def priority(self) -> int:
        return 50

    def evaluate(self, ctx: EvaluationContext) -> PDPDecision | None:
        return PDPDecision(
            decision=DecisionType.BLOCK,
            reason="always block",
            plugin_id=self.plugin_id,
        )


# ---------------------------------------------------------------------------
# PDPEnforcer
# ---------------------------------------------------------------------------


class TestPDPEnforcer:
    def test_no_plugins_allows(self) -> None:
        enforcer = PDPEnforcer()
        result = enforcer.evaluate(bundle=_make_bundle(), content="hello")
        assert result.allowed
        assert result.final_decision == DecisionType.ALLOW
        assert result.decisions == []

    def test_block_plugin_blocks(self) -> None:
        enforcer = PDPEnforcer()
        enforcer.register(_BlockPlugin())
        result = enforcer.evaluate(bundle=_make_bundle(), content="hello")
        assert result.blocked
        assert len(result.blocking_reasons) == 1

    def test_allow_plugin_allows(self) -> None:
        enforcer = PDPEnforcer()
        enforcer.register(_AllowPlugin())
        result = enforcer.evaluate(bundle=_make_bundle(), content="hello")
        assert result.allowed

    def test_crash_plugin_fail_closed(self) -> None:
        enforcer = PDPEnforcer(fail_closed=True)
        enforcer.register(_CrashPlugin())
        result = enforcer.evaluate(bundle=_make_bundle(), content="hello")
        assert result.blocked
        assert "crashed" in result.blocking_reasons[0]

    def test_crash_plugin_fail_open(self) -> None:
        enforcer = PDPEnforcer(fail_closed=False)
        enforcer.register(_CrashPlugin())
        result = enforcer.evaluate(bundle=_make_bundle(), content="hello")
        assert result.allowed

    def test_plugins_run_in_priority_order(self) -> None:
        order: list[str] = []

        class _P1(PDPPlugin):
            @property
            def plugin_id(self) -> str:
                return "p1"

            @property
            def priority(self) -> int:
                return 200

            def evaluate(self, ctx: EvaluationContext) -> PDPDecision | None:
                order.append("p1")
                return None

        class _P2(PDPPlugin):
            @property
            def plugin_id(self) -> str:
                return "p2"

            @property
            def priority(self) -> int:
                return 10

            def evaluate(self, ctx: EvaluationContext) -> PDPDecision | None:
                order.append("p2")
                return None

        enforcer = PDPEnforcer()
        enforcer.register(_P1())
        enforcer.register(_P2())
        enforcer.evaluate(bundle=_make_bundle(), content="x")
        assert order == ["p2", "p1"]

    def test_duration_ms_is_populated(self) -> None:
        enforcer = PDPEnforcer()
        result = enforcer.evaluate(bundle=_make_bundle(), content="x")
        assert isinstance(result.duration_ms, int)
        assert result.duration_ms >= 0

    def test_metadata_passed_to_context(self) -> None:
        captured: list[EvaluationContext] = []

        class _Spy(PDPPlugin):
            @property
            def plugin_id(self) -> str:
                return "spy"

            def evaluate(self, ctx: EvaluationContext) -> PDPDecision | None:
                captured.append(ctx)
                return None

        enforcer = PDPEnforcer()
        enforcer.register(_Spy())
        enforcer.evaluate(
            bundle=_make_bundle(),
            content="test",
            session_id="sess-1",
            verification_result=VerificationResult.VALID,
        )
        assert len(captured) == 1
        assert captured[0].session_id == "sess-1"
        assert captured[0].metadata["verification_result"] == VerificationResult.VALID


# ---------------------------------------------------------------------------
# RefusalBoundaryPlugin
# ---------------------------------------------------------------------------


class TestRefusalBoundaryPlugin:
    def test_no_bundle_fail_closed_blocks(self) -> None:
        plugin = RefusalBoundaryPlugin(mode=EnforcementMode.FAIL_CLOSED)
        ctx = EvaluationContext(bundle=None, content="hi")
        decision = plugin.evaluate(ctx)
        assert decision is not None
        assert decision.blocked

    def test_no_bundle_audit_only_allows(self) -> None:
        plugin = RefusalBoundaryPlugin(mode=EnforcementMode.AUDIT_ONLY)
        ctx = EvaluationContext(bundle=None, content="hi")
        assert plugin.evaluate(ctx) is None

    def test_valid_verification_allows(self) -> None:
        plugin = RefusalBoundaryPlugin()
        ctx = EvaluationContext(
            bundle=_make_bundle(),
            content="hi",
            metadata={"verification_result": VerificationResult.VALID},
        )
        assert plugin.evaluate(ctx) is None

    def test_invalid_verification_fail_closed_blocks(self) -> None:
        plugin = RefusalBoundaryPlugin(mode=EnforcementMode.FAIL_CLOSED)
        ctx = EvaluationContext(
            bundle=_make_bundle(),
            content="hi",
            metadata={"verification_result": VerificationResult.EXPIRED},
        )
        decision = plugin.evaluate(ctx)
        assert decision is not None
        assert decision.blocked
        assert "EXPIRED" in decision.reason

    def test_invalid_verification_escalate_escalates(self) -> None:
        plugin = RefusalBoundaryPlugin(mode=EnforcementMode.ESCALATE)
        ctx = EvaluationContext(
            bundle=_make_bundle(),
            content="hi",
            metadata={"verification_result": VerificationResult.HASH_MISMATCH},
        )
        decision = plugin.evaluate(ctx)
        assert decision is not None
        assert decision.decision == DecisionType.ESCALATE


# ---------------------------------------------------------------------------
# AdherenceLevelPlugin
# ---------------------------------------------------------------------------


class TestAdherenceLevelPlugin:
    def test_sufficient_adherence_allows(self) -> None:
        plugin = AdherenceLevelPlugin(min_adherence=3)
        ctx = EvaluationContext(
            bundle=_make_bundle(adherence=4),
            content="hi",
        )
        assert plugin.evaluate(ctx) is None

    def test_insufficient_adherence_blocks(self) -> None:
        plugin = AdherenceLevelPlugin(min_adherence=3)
        ctx = EvaluationContext(
            bundle=_make_bundle(adherence=1),
            content="hi",
        )
        decision = plugin.evaluate(ctx)
        assert decision is not None
        assert decision.blocked

    def test_no_adherence_metadata_abstains(self) -> None:
        plugin = AdherenceLevelPlugin(min_adherence=3)
        ctx = EvaluationContext(bundle=_make_bundle(), content="hi")
        assert plugin.evaluate(ctx) is None

    def test_invalid_adherence_blocks(self) -> None:
        plugin = AdherenceLevelPlugin(min_adherence=3)
        bundle = _make_bundle()
        bundle.manifest.metadata["adherence_level"] = "not_a_number"
        ctx = EvaluationContext(bundle=bundle, content="hi")
        decision = plugin.evaluate(ctx)
        assert decision is not None
        assert decision.blocked

    def test_invalid_min_adherence_raises(self) -> None:
        with pytest.raises(ValueError):
            AdherenceLevelPlugin(min_adherence=6)

    def test_require_declaration_blocks_when_missing(self) -> None:
        plugin = AdherenceLevelPlugin(min_adherence=3, require_declaration=True)
        ctx = EvaluationContext(bundle=_make_bundle(), content="hi")
        decision = plugin.evaluate(ctx)
        assert decision is not None
        assert decision.blocked
        assert "does not declare" in decision.reason

    def test_adherence_from_metadata_kwarg(self) -> None:
        plugin = AdherenceLevelPlugin(min_adherence=3)
        ctx = EvaluationContext(
            bundle=_make_bundle(),
            content="hi",
            metadata={"adherence_level": 2},
        )
        decision = plugin.evaluate(ctx)
        assert decision is not None
        assert decision.blocked


# ---------------------------------------------------------------------------
# BundleExpiryPlugin
# ---------------------------------------------------------------------------


class TestBundleExpiryPlugin:
    def test_valid_bundle_allows(self) -> None:
        plugin = BundleExpiryPlugin()
        ctx = EvaluationContext(bundle=_make_bundle(expired=False), content="hi")
        assert plugin.evaluate(ctx) is None

    def test_expired_bundle_blocks(self) -> None:
        plugin = BundleExpiryPlugin()
        bundle = MagicMock()
        bundle.manifest.timestamps.exp = datetime.now(timezone.utc) - timedelta(hours=1)
        ctx = EvaluationContext(bundle=bundle, content="hi")
        decision = plugin.evaluate(ctx)
        assert decision is not None
        assert decision.blocked
        assert "expired" in decision.reason.lower()

    def test_no_bundle_abstains(self) -> None:
        plugin = BundleExpiryPlugin()
        ctx = EvaluationContext(bundle=None, content="hi")
        assert plugin.evaluate(ctx) is None

    def test_no_expiry_abstains(self) -> None:
        plugin = BundleExpiryPlugin()
        bundle = MagicMock()
        bundle.manifest.timestamps.exp = None
        ctx = EvaluationContext(bundle=bundle, content="hi")
        assert plugin.evaluate(ctx) is None
