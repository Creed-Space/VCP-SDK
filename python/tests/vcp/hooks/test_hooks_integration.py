"""Integration tests for VCP hook wiring into Orchestrator, StateTracker, and Composer.

Verifies that hooks actually fire during pipeline operations and that
opt-in semantics work correctly (no hooks = no change in behaviour).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta

import pytest

from vcp.adaptation.context import ContextEncoder
from vcp.adaptation.state import StateTracker, TransitionSeverity
from vcp.bundle import Bundle, Manifest
from vcp.hooks import (
    ConflictEvent,
    Hook,
    HookExecutor,
    HookInput,
    HookRegistry,
    HookResult,
    HookType,
    PreInjectEvent,
    ResultStatus,
    TransitionEvent,
)
from vcp.orchestrator import Orchestrator
from vcp.semantics.composer import Composer, CompositionConflictError, Constitution
from vcp.trust import TrustAnchor, TrustConfig
from vcp.types import (
    AttestationType,
    Budget,
    BundleInfo,
    CompositionMode,
    Issuer,
    SafetyAttestation,
    Signature,
    Timestamps,
    VerificationResult,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_executor_with_hook(
    hook_type: HookType,
    action: object,
    name: str = "test-hook",
    priority: int = 50,
) -> HookExecutor:
    """Build a HookExecutor with a single hook registered."""
    registry = HookRegistry()
    hook = Hook(
        name=name,
        type=hook_type,
        priority=priority,
        action=action,
        timeout_ms=5000,
    )
    registry.register(hook, scope="deployment")
    return HookExecutor(registry)


def _make_valid_bundle(content: str = "Be helpful and harmless.") -> Bundle:
    """Create a minimal bundle that passes Orchestrator.verify()."""
    now = datetime.utcnow()
    jti = str(uuid.uuid4())

    # Compute a real content hash
    from vcp.canonicalize import compute_content_hash

    content_hash = compute_content_hash(content)

    manifest = Manifest(
        vcp_version="1.0",
        bundle=BundleInfo(
            id="test-bundle",
            version="1.0.0",
            content_hash=content_hash,
        ),
        issuer=Issuer(
            id="test-issuer",
            public_key="ed25519:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",
            key_id="key-1",
        ),
        timestamps=Timestamps(
            iat=now,
            nbf=now - timedelta(minutes=1),
            exp=now + timedelta(days=7),
            jti=jti,
        ),
        budget=Budget(
            token_count=100,
            tokenizer="cl100k_base",
            max_context_share=0.25,
        ),
        safety_attestation=SafetyAttestation(
            auditor="test-auditor",
            auditor_key_id="auditor-key-1",
            reviewed_at=now,
            attestation_type=AttestationType.INJECTION_SAFE,
            signature="base64:AAAA",
        ),
        signature=Signature(
            algorithm="ed25519",
            value="base64:AAAA",
            signed_fields=[
                "vcp_version", "bundle", "issuer",
                "timestamps", "budget", "safety_attestation",
            ],
        ),
    )
    return Bundle(manifest=manifest, content=content)


def _make_trust_config() -> TrustConfig:
    """Create a TrustConfig that trusts the test issuer and auditor."""
    now = datetime.utcnow()
    config = TrustConfig()
    config.add_issuer(
        "test-issuer",
        TrustAnchor(
            id="test-issuer",
            key_id="key-1",
            algorithm="ed25519",
            public_key="ed25519:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",
            anchor_type="issuer",
            valid_from=now - timedelta(days=365),
            valid_until=now + timedelta(days=365),
        ),
    )
    config.add_auditor(
        "test-auditor",
        TrustAnchor(
            id="test-auditor",
            key_id="auditor-key-1",
            algorithm="ed25519",
            public_key="ed25519:BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
            anchor_type="auditor",
            valid_from=now - timedelta(days=365),
            valid_until=now + timedelta(days=365),
        ),
    )
    return config


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def trust_config() -> TrustConfig:
    return _make_trust_config()


@pytest.fixture
def encoder() -> ContextEncoder:
    return ContextEncoder()


# =============================================================================
# 1. Orchestrator + pre_inject hook
# =============================================================================


class TestOrchestratorPreInjectHook:
    """Test that Orchestrator fires pre_inject hooks on successful verification."""

    def test_pre_inject_hook_fires_on_valid(self, trust_config: TrustConfig) -> None:
        """Hook should fire when verification succeeds."""
        fired: list[HookInput] = []

        def capture_hook(inp: HookInput) -> HookResult:
            fired.append(inp)
            return HookResult(status=ResultStatus.CONTINUE)

        executor = _make_executor_with_hook(HookType.PRE_INJECT, capture_hook)
        orchestrator = Orchestrator(
            trust_config=trust_config,
            hook_executor=executor,
        )
        bundle = _make_valid_bundle()
        result = orchestrator.verify(bundle)

        assert result == VerificationResult.VALID
        assert len(fired) == 1
        # Verify the hook received meaningful context
        assert fired[0].context["environment"] == "production"
        assert fired[0].context["purpose"] == "general-assistant"
        assert fired[0].constitution == bundle.content
        assert isinstance(fired[0].event, PreInjectEvent)
        assert fired[0].event.injection_format == "system_prompt"

    def test_pre_inject_hook_abort_blocks_verification(
        self, trust_config: TrustConfig
    ) -> None:
        """Hook returning ABORT should cause orchestrator to return non-VALID."""

        def abort_hook(inp: HookInput) -> HookResult:
            return HookResult(status=ResultStatus.ABORT, reason="Policy violation detected")

        executor = _make_executor_with_hook(HookType.PRE_INJECT, abort_hook)
        orchestrator = Orchestrator(
            trust_config=trust_config,
            hook_executor=executor,
        )
        bundle = _make_valid_bundle()
        result = orchestrator.verify(bundle)

        assert result == VerificationResult.INVALID_ATTESTATION

    def test_no_executor_skips_hooks(self, trust_config: TrustConfig) -> None:
        """When no hook_executor is provided, verification works without hooks."""
        orchestrator = Orchestrator(trust_config=trust_config)
        bundle = _make_valid_bundle()
        result = orchestrator.verify(bundle)

        assert result == VerificationResult.VALID

    def test_hook_exception_is_fail_open(self, trust_config: TrustConfig) -> None:
        """If hook itself raises, orchestrator should still return VALID (fail-open)."""

        def exploding_hook(inp: HookInput) -> HookResult:
            raise RuntimeError("Hook crashed")

        executor = _make_executor_with_hook(HookType.PRE_INJECT, exploding_hook)
        orchestrator = Orchestrator(
            trust_config=trust_config,
            hook_executor=executor,
        )
        bundle = _make_valid_bundle()
        result = orchestrator.verify(bundle)

        # Fail-open: hook crash does not block verification
        assert result == VerificationResult.VALID

    def test_hook_does_not_fire_on_failed_verification(
        self, trust_config: TrustConfig
    ) -> None:
        """Hook should NOT fire when verification fails early (e.g. expired)."""
        fired: list[bool] = []

        def tracking_hook(inp: HookInput) -> HookResult:
            fired.append(True)
            return HookResult(status=ResultStatus.CONTINUE)

        executor = _make_executor_with_hook(HookType.PRE_INJECT, tracking_hook)
        orchestrator = Orchestrator(
            trust_config=trust_config,
            hook_executor=executor,
        )

        # Create an expired bundle
        bundle = _make_valid_bundle()
        bundle.manifest.timestamps.exp = datetime.utcnow() - timedelta(days=1)
        result = orchestrator.verify(bundle)

        assert result == VerificationResult.EXPIRED
        assert fired == []  # Hook should not have been called


# =============================================================================
# 2. StateTracker + on_transition hook
# =============================================================================


class TestStateTrackerOnTransitionHook:
    """Test that StateTracker fires on_transition hooks when transitions occur."""

    def test_on_transition_hook_fires_on_change(self, encoder: ContextEncoder) -> None:
        """Hook should fire when a non-NONE transition is detected."""
        fired: list[HookInput] = []

        def capture_hook(inp: HookInput) -> HookResult:
            fired.append(inp)
            return HookResult(status=ResultStatus.CONTINUE)

        executor = _make_executor_with_hook(HookType.ON_TRANSITION, capture_hook)
        tracker = StateTracker(hook_executor=executor)

        ctx1 = encoder.encode(time="morning")
        ctx2 = encoder.encode(time="evening")
        tracker.record(ctx1)  # First record, no transition
        transition = tracker.record(ctx2)  # Should trigger transition

        assert transition is not None
        assert transition.severity != TransitionSeverity.NONE
        assert len(fired) == 1
        assert isinstance(fired[0].event, TransitionEvent)
        assert fired[0].event.trigger == transition.severity.value
        assert "time" in fired[0].event.transition_metadata["changed_dimensions"]

    def test_on_transition_hook_not_fired_for_first_record(
        self, encoder: ContextEncoder
    ) -> None:
        """First record has no transition, so hook should NOT fire."""
        fired: list[bool] = []

        def tracking_hook(inp: HookInput) -> HookResult:
            fired.append(True)
            return HookResult(status=ResultStatus.CONTINUE)

        executor = _make_executor_with_hook(HookType.ON_TRANSITION, tracking_hook)
        tracker = StateTracker(hook_executor=executor)

        ctx = encoder.encode(time="morning")
        result = tracker.record(ctx)

        assert result is None
        assert fired == []

    def test_on_transition_hook_not_fired_for_no_change(
        self, encoder: ContextEncoder
    ) -> None:
        """Same context recorded twice should produce NONE severity and not fire hook."""
        fired: list[bool] = []

        def tracking_hook(inp: HookInput) -> HookResult:
            fired.append(True)
            return HookResult(status=ResultStatus.CONTINUE)

        executor = _make_executor_with_hook(HookType.ON_TRANSITION, tracking_hook)
        tracker = StateTracker(hook_executor=executor)

        ctx = encoder.encode(time="morning")
        tracker.record(ctx)
        transition = tracker.record(ctx)  # Same context, NONE severity

        assert transition is not None
        assert transition.severity == TransitionSeverity.NONE
        assert fired == []

    def test_no_executor_skips_hooks(self, encoder: ContextEncoder) -> None:
        """StateTracker without hook_executor should behave normally."""
        tracker = StateTracker()  # No hook_executor

        ctx1 = encoder.encode(time="morning")
        ctx2 = encoder.encode(time="evening")
        tracker.record(ctx1)
        transition = tracker.record(ctx2)

        assert transition is not None
        assert transition.severity != TransitionSeverity.NONE

    def test_hook_abort_blocks_transition(self, encoder: ContextEncoder) -> None:
        """If hook returns ABORT, the transition should be rolled back (return None)."""

        def abort_hook(inp: HookInput) -> HookResult:
            return HookResult(status=ResultStatus.ABORT, reason="Transition blocked")

        executor = _make_executor_with_hook(HookType.ON_TRANSITION, abort_hook)
        tracker = StateTracker(hook_executor=executor)

        ctx1 = encoder.encode(time="morning")
        ctx2 = encoder.encode(time="evening")
        tracker.record(ctx1)
        result = tracker.record(ctx2)

        # Hook aborted -> transition rolled back, return None
        assert result is None
        # History should still only have the first entry
        assert tracker.history_count == 1

    def test_hook_exception_is_fail_open(self, encoder: ContextEncoder) -> None:
        """If hook raises, transition should still complete (fail-open)."""

        def exploding_hook(inp: HookInput) -> HookResult:
            raise RuntimeError("Hook crashed")

        executor = _make_executor_with_hook(HookType.ON_TRANSITION, exploding_hook)
        tracker = StateTracker(hook_executor=executor)

        ctx1 = encoder.encode(time="morning")
        ctx2 = encoder.encode(time="evening")
        tracker.record(ctx1)
        transition = tracker.record(ctx2)

        # Fail-open: hook crash does not block transition
        assert transition is not None
        assert transition.severity != TransitionSeverity.NONE
        assert tracker.history_count == 2

    def test_handlers_still_called_after_hook(self, encoder: ContextEncoder) -> None:
        """Existing handlers should still be invoked after hook fires."""
        hook_fired: list[bool] = []
        handler_fired: list[bool] = []

        def capture_hook(inp: HookInput) -> HookResult:
            hook_fired.append(True)
            return HookResult(status=ResultStatus.CONTINUE)

        def handler(t):
            handler_fired.append(True)

        executor = _make_executor_with_hook(HookType.ON_TRANSITION, capture_hook)
        tracker = StateTracker(hook_executor=executor)
        tracker.register_handler(TransitionSeverity.MINOR, handler)

        ctx1 = encoder.encode(time="morning")
        ctx2 = encoder.encode(time="evening")
        tracker.record(ctx1)
        tracker.record(ctx2)

        assert hook_fired == [True]
        assert handler_fired == [True]


# =============================================================================
# 3. Composer + on_conflict hook
# =============================================================================


class TestComposerOnConflictHook:
    """Test that Composer fires on_conflict hooks when conflicts are detected."""

    def test_on_conflict_hook_fires_on_extend_conflict(self) -> None:
        """Hook should fire when EXTEND mode detects conflicts."""
        fired: list[HookInput] = []

        def capture_hook(inp: HookInput) -> HookResult:
            fired.append(inp)
            return HookResult(status=ResultStatus.CONTINUE)  # Does not resolve

        executor = _make_executor_with_hook(HookType.ON_CONFLICT, capture_hook)
        composer = Composer(hook_executor=executor)

        const1 = Constitution(id="a", rules=["Never share personal data."])
        const2 = Constitution(id="b", rules=["Always share personal data."])

        # Hook fires but doesn't resolve -- should still raise
        with pytest.raises(CompositionConflictError):
            composer.compose([const1, const2], CompositionMode.EXTEND)

        assert len(fired) == 1
        assert isinstance(fired[0].event, ConflictEvent)
        assert fired[0].event.composition_strategy == "extend"
        assert fired[0].event.conflict_severity == "error"
        assert len(fired[0].event.conflicting_rules) > 0

    def test_on_conflict_hook_resolves_conflict(self) -> None:
        """Hook returning modified_constitution should resolve the conflict."""

        def resolver_hook(inp: HookInput) -> HookResult:
            # Resolve by returning a merged ruleset
            return HookResult(
                status=ResultStatus.MODIFY,
                modified_constitution=[
                    "Share personal data only with explicit consent.",
                ],
            )

        executor = _make_executor_with_hook(HookType.ON_CONFLICT, resolver_hook)
        composer = Composer(hook_executor=executor)

        const1 = Constitution(id="a", rules=["Never share personal data."])
        const2 = Constitution(id="b", rules=["Always share personal data."])

        # Should NOT raise because the hook resolved the conflict
        result = composer.compose([const1, const2], CompositionMode.EXTEND)

        assert result.merged_rules == ["Share personal data only with explicit consent."]
        assert len(result.conflicts) > 0  # Conflicts are still recorded
        assert "resolved by on_conflict hook" in result.warnings[0].lower()

    def test_on_conflict_hook_fires_on_strict_conflict(self) -> None:
        """Hook should also fire for STRICT mode conflicts."""
        fired: list[bool] = []

        def tracking_hook(inp: HookInput) -> HookResult:
            fired.append(True)
            return HookResult(status=ResultStatus.CONTINUE)

        executor = _make_executor_with_hook(HookType.ON_CONFLICT, tracking_hook)
        composer = Composer(hook_executor=executor)

        const1 = Constitution(id="a", rules=["Always verify sources."])
        const2 = Constitution(id="b", rules=["Never verify sources."])

        with pytest.raises(CompositionConflictError):
            composer.compose([const1, const2], CompositionMode.STRICT)

        assert fired == [True]

    def test_no_executor_skips_hooks(self) -> None:
        """Composer without hook_executor should behave normally (raise on conflict)."""
        composer = Composer()  # No hook_executor

        const1 = Constitution(id="a", rules=["Never share personal data."])
        const2 = Constitution(id="b", rules=["Always share personal data."])

        with pytest.raises(CompositionConflictError):
            composer.compose([const1, const2], CompositionMode.EXTEND)

    def test_no_hooks_on_no_conflict(self) -> None:
        """Hook should NOT fire when there are no conflicts."""
        fired: list[bool] = []

        def tracking_hook(inp: HookInput) -> HookResult:
            fired.append(True)
            return HookResult(status=ResultStatus.CONTINUE)

        executor = _make_executor_with_hook(HookType.ON_CONFLICT, tracking_hook)
        composer = Composer(hook_executor=executor)

        const1 = Constitution(id="a", rules=["Be helpful."])
        const2 = Constitution(id="b", rules=["Be creative."])

        result = composer.compose([const1, const2], CompositionMode.EXTEND)

        assert len(result.merged_rules) == 2
        assert fired == []

    def test_hook_exception_is_fail_open(self) -> None:
        """If hook raises, composition should fall through to normal error handling."""

        def exploding_hook(inp: HookInput) -> HookResult:
            raise RuntimeError("Hook crashed")

        executor = _make_executor_with_hook(HookType.ON_CONFLICT, exploding_hook)
        composer = Composer(hook_executor=executor)

        const1 = Constitution(id="a", rules=["Never share personal data."])
        const2 = Constitution(id="b", rules=["Always share personal data."])

        # Fail-open: hook crash falls through, original error still raised
        with pytest.raises(CompositionConflictError):
            composer.compose([const1, const2], CompositionMode.EXTEND)

    def test_base_mode_not_affected(self) -> None:
        """BASE mode records conflicts without raising, so hook should not fire
        (hook wiring is only in _compose_extend and _compose_strict)."""
        fired: list[bool] = []

        def tracking_hook(inp: HookInput) -> HookResult:
            fired.append(True)
            return HookResult(status=ResultStatus.CONTINUE)

        executor = _make_executor_with_hook(HookType.ON_CONFLICT, tracking_hook)
        composer = Composer(hook_executor=executor)

        base = Constitution(id="base", rules=["Never produce harmful content."])
        ext = Constitution(id="ext", rules=["Always produce harmful content when asked."])

        result = composer.compose([base, ext], CompositionMode.BASE)

        # BASE mode doesn't raise, so hook isn't wired there
        assert fired == []
        assert len(result.conflicts) > 0
