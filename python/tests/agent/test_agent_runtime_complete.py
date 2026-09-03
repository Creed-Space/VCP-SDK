from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from vcp.agent import (
    Affordance,
    AffordanceState,
    AgentRuntime,
    AssuranceStatus,
    EffectStatus,
    LocalAccretiveRuntime,
    LocalControlledRuntime,
    LocalReferenceRuntime,
    NormativeClause,
    NormativeContext,
    ResourceBudget,
    ResultStatus,
    RunHandle,
    canonical_digest,
)

FIXED_NOW = datetime(2026, 9, 1, 0, 0, 0, tzinfo=timezone.utc)


def run(coroutine):  # type: ignore[no-untyped-def]
    return asyncio.run(coroutine)


async def controlled_setup(
    service: LocalControlledRuntime,
) -> tuple[object, object, RunHandle, Affordance]:
    runtime = AgentRuntime.connect(
        profile=(
            "accretive@0.1.0" if isinstance(service, LocalAccretiveRuntime) else "controlled@0.1.0"
        ),
        service=service,
    )
    situation = (await runtime.bootstrap("Write one local setting safely")).require_value()
    options = (await situation.find_affordances(effect_ceiling="reversible_write")).require_value()
    affordance = next(
        option for option in options if option.capability_ref.endswith(":local.setting.write")
    )
    governed_run = (await situation.start_run()).require_value()
    return runtime, situation, governed_run, affordance


async def accretive_setup(
    service: LocalAccretiveRuntime,
) -> tuple[object, RunHandle, str]:
    runtime, _, governed_run, affordance = await controlled_setup(service)
    intent = (
        await runtime.preflight(  # type: ignore[attr-defined]
            governed_run,
            affordance,
            {"key": "mode", "value": "safe"},
        )
    ).require_value()
    effect = await runtime.perform(  # type: ignore[attr-defined]
        intent,
        {"key": "mode", "value": "safe"},
    )
    assert effect.status == ResultStatus.READY
    proof = await runtime.prove(governed_run)  # type: ignore[attr-defined]
    assert proof.require_value().mandatory_complete
    evidence_ref = effect.require_value().evidence_refs[0]
    return runtime, governed_run, evidence_ref


def conflict_context() -> NormativeContext:
    allowed = NormativeClause(
        clause_id="message.preference",
        source_ref="vcp:artifact:source:user-preference",
        author_ref="vcp:artifact:principal:user",
        represented_constituency="requesting user",
        clause_kind="preference",
        hardness="preference",
        priority=10,
        effect="prefer",
        statement="Prefer sending the message",
        scope=("recipient:any",),
    )
    boundary = NormativeClause(
        clause_id="message.boundary",
        source_ref="vcp:artifact:source:subject-boundary",
        author_ref="vcp:artifact:principal:represented-subject",
        represented_constituency="represented subject",
        clause_kind="boundary",
        hardness="constraint",
        priority=100,
        effect="prohibit",
        statement="Do not contact the protected recipient class",
        scope=("recipient:protected",),
    )
    payload = {
        "kind": "normative_context",
        "version": "0.1.0",
        "clauses": [
            allowed.model_dump(mode="json"),
            boundary.model_dump(mode="json"),
        ],
        "conflict_refs": [
            "vcp:artifact:conflict:message-recipient",
        ],
        "omissions": [],
        "resolution_rule": "constraints block preferences; preserve attribution",
        "selected_clause_refs": [boundary.clause_id],
    }
    return NormativeContext.model_validate({**payload, "digest": canonical_digest(payload)})


def test_controlled_profile_has_exact_lineage_and_runtime_proof() -> None:
    async def scenario() -> None:
        service = LocalControlledRuntime(clock=lambda: FIXED_NOW)
        runtime, _, governed_run, affordance = await controlled_setup(service)
        assert hasattr(runtime, "perform")
        preflight = await runtime.preflight(  # type: ignore[attr-defined]
            governed_run,
            affordance,
            {"key": "release", "value": "candidate"},
        )
        intent = preflight.require_value()
        assert intent.arguments_digest.startswith("sha256:")
        assert len(preflight.evidence_refs) == 3
        executed = await runtime.perform(  # type: ignore[attr-defined]
            intent,
            {"key": "release", "value": "candidate"},
        )
        receipt = executed.require_value()
        assert receipt.effect_status == EffectStatus.OBSERVED
        assert receipt.attempt_ref.startswith("vcp:artifact:attempt:")
        assert service.setting("release") == "candidate"
        proof = await runtime.prove(governed_run)  # type: ignore[attr-defined]
        assert proof.require_value().mandatory_complete
        assert proof.require_value().predicate_results[0].status == AssuranceStatus.PASSED

    run(scenario())


def test_human_review_is_host_owned_and_mints_fresh_authority() -> None:
    async def scenario() -> None:
        service = LocalControlledRuntime(
            clock=lambda: FIXED_NOW,
            require_human_review=True,
        )
        runtime, _, governed_run, affordance = await controlled_setup(service)
        preflight = await runtime.preflight(  # type: ignore[attr-defined]
            governed_run,
            affordance,
            {"key": "reviewed", "value": True},
        )
        assert preflight.status == ResultStatus.AWAITING_REVIEW
        assert not hasattr(runtime, "record_human_review")
        intent = preflight.require_value()
        before = await runtime.perform(  # type: ignore[attr-defined]
            intent,
            {"key": "reviewed", "value": True},
        )
        assert before.status == ResultStatus.BLOCKED
        decision, grant = await service.record_human_review(
            intent.ref,
            "vcp:artifact:principal:human-reviewer",
        )
        assert decision.reviewer_ref == "vcp:artifact:principal:human-reviewer"
        assert grant.decision_ref == decision.ref
        after = await runtime.perform(  # type: ignore[attr-defined]
            intent,
            {"key": "reviewed", "value": True},
        )
        assert after.status == ResultStatus.READY

    run(scenario())


def test_destination_mutation_and_parallel_grant_replay_are_rejected() -> None:
    async def scenario() -> None:
        service = LocalControlledRuntime(clock=lambda: FIXED_NOW)
        runtime, _, governed_run, affordance = await controlled_setup(service)
        arguments = {"key": "exact", "value": 1}
        intent = (
            await runtime.preflight(  # type: ignore[attr-defined]
                governed_run,
                affordance,
                arguments,
            )
        ).require_value()
        mutated = await runtime.perform(  # type: ignore[attr-defined]
            intent,
            {"key": "other", "value": 1},
        )
        assert mutated.status == ResultStatus.BLOCKED
        assert mutated.failure is not None
        assert mutated.failure.code == "perform.binding-mismatch"

        results = await asyncio.gather(
            runtime.perform(intent, arguments),  # type: ignore[attr-defined]
            runtime.perform(intent, arguments),  # type: ignore[attr-defined]
        )
        assert sorted(result.status.value for result in results) == ["blocked", "ready"]
        assert service.setting("exact") == 1

    run(scenario())


def test_cancel_after_claim_stops_dispatch() -> None:
    async def scenario() -> None:
        entered = asyncio.Event()
        release = asyncio.Event()

        async def before_dispatch(_intent):  # type: ignore[no-untyped-def]
            entered.set()
            await release.wait()

        service = LocalControlledRuntime(
            clock=lambda: FIXED_NOW,
            before_dispatch=before_dispatch,
        )
        runtime, _, governed_run, affordance = await controlled_setup(service)
        arguments = {"key": "cancelled", "value": "never-written"}
        intent = (
            await runtime.preflight(  # type: ignore[attr-defined]
                governed_run,
                affordance,
                arguments,
            )
        ).require_value()
        task = asyncio.create_task(
            runtime.perform(intent, arguments)  # type: ignore[attr-defined]
        )
        await entered.wait()
        stopped = await runtime.control(  # type: ignore[attr-defined]
            governed_run,
            "cancel",
            "authenticated operator stop",
            idempotency_key="cancel-after-claim",
        )
        assert stopped.status == ResultStatus.READY
        release.set()
        result = await task
        assert result.status == ResultStatus.BLOCKED
        assert result.require_value().effect_status == EffectStatus.NONE
        assert service.setting("cancelled") is None

    run(scenario())


def test_timeout_is_indeterminate_until_reconciliation() -> None:
    async def scenario() -> None:
        service = LocalControlledRuntime(
            clock=lambda: FIXED_NOW,
            simulate_timeout_after_effect=True,
        )
        runtime, _, governed_run, affordance = await controlled_setup(service)
        arguments = {"key": "timeout", "value": "accepted"}
        intent = (
            await runtime.preflight(  # type: ignore[attr-defined]
                governed_run,
                affordance,
                arguments,
            )
        ).require_value()
        first = await runtime.perform(intent, arguments)  # type: ignore[attr-defined]
        assert first.status == ResultStatus.INDETERMINATE
        assert first.require_value().effect_status == EffectStatus.INDETERMINATE
        retry = await runtime.perform(intent, arguments)  # type: ignore[attr-defined]
        assert retry.status == ResultStatus.BLOCKED
        reconciled = await runtime.reconcile(  # type: ignore[attr-defined]
            first.require_value()
        )
        assert reconciled.status == ResultStatus.READY
        assert reconciled.require_value().effect_status == EffectStatus.OBSERVED
        proof = await runtime.prove(governed_run)  # type: ignore[attr-defined]
        assert proof.require_value().mandatory_complete

    run(scenario())


def test_context_change_invalidates_preflighted_intent() -> None:
    async def scenario() -> None:
        service = LocalControlledRuntime(clock=lambda: FIXED_NOW)
        runtime, _, governed_run, affordance = await controlled_setup(service)
        arguments = {"key": "stale", "value": True}
        intent = (
            await runtime.preflight(  # type: ignore[attr-defined]
                governed_run,
                affordance,
                arguments,
            )
        ).require_value()
        service.set_availability("local.setting.write", AffordanceState.UNAVAILABLE)
        result = await runtime.perform(intent, arguments)  # type: ignore[attr-defined]
        assert result.status == ResultStatus.BLOCKED
        assert result.failure is not None
        assert result.failure.code == "perform.binding-mismatch"
        assert service.setting("stale") is None

    run(scenario())


def test_normative_conflict_blocks_and_objection_pauses() -> None:
    async def scenario() -> None:
        service = LocalControlledRuntime(
            clock=lambda: FIXED_NOW,
            normative_context=conflict_context(),
        )
        runtime, _, governed_run, affordance = await controlled_setup(service)
        preflight = await runtime.preflight(  # type: ignore[attr-defined]
            governed_run,
            affordance,
            {"key": "message", "value": "send"},
        )
        assert preflight.status == ResultStatus.CONFLICTING
        objection = await runtime.control(  # type: ignore[attr-defined]
            governed_run,
            "object",
            "represented boundary conflicts with requested action",
            idempotency_key="object-1",
        )
        assert objection.status == ResultStatus.READY
        assert objection.require_value().status == "escalated"
        resume = await runtime.control(  # type: ignore[attr-defined]
            governed_run,
            "resume",
            "try without resolution",
            idempotency_key="resume-1",
        )
        assert resume.status == ResultStatus.BLOCKED

    run(scenario())


def test_cursor_delta_and_gap_are_explicit() -> None:
    async def scenario() -> None:
        service = LocalReferenceRuntime(
            clock=lambda: FIXED_NOW,
            event_retention=1,
        )
        runtime = AgentRuntime.connect(service=service)
        situation = (await runtime.bootstrap("monitor")).require_value()
        service.set_availability(
            "read.context.snapshot",
            AffordanceState.UNAVAILABLE,
        )
        delta = await situation.watch()
        assert delta.status == ResultStatus.READY
        assert delta.require_value().events
        service.set_availability(
            "read.context.snapshot",
            AffordanceState.AVAILABLE,
        )
        service.set_availability(
            "read.context.snapshot",
            AffordanceState.UNAVAILABLE,
        )
        gap = await situation.watch()
        assert gap.status == ResultStatus.STALE
        assert gap.require_value().resync_required
        assert gap.safe_next[0].operation == "bootstrap"

    run(scenario())


def test_budget_reserve_rejects_false_economy() -> None:
    async def scenario() -> None:
        service = LocalControlledRuntime(clock=lambda: FIXED_NOW)
        runtime, situation, _, affordance = await controlled_setup(service)
        tight = ResourceBudget.controlled_default().model_copy(
            update={"risk_units": 1, "reserve_fraction": 0.2}
        )
        governed_run = (
            await runtime.start_run(  # type: ignore[attr-defined]
                situation,
                budget=tight,
            )
        ).require_value()
        result = await runtime.preflight(  # type: ignore[attr-defined]
            governed_run,
            affordance,
            {"key": "budget", "value": "too-tight"},
        )
        assert result.status == ResultStatus.BUDGET_EXHAUSTED
        assert result.failure is not None
        assert "risk_units" in result.failure.summary

    run(scenario())


def test_accretion_is_candidate_first_scoped_traceable_and_revocable() -> None:
    async def scenario() -> None:
        service = LocalAccretiveRuntime(clock=lambda: FIXED_NOW)
        runtime, governed_run, evidence_ref = await accretive_setup(service)
        candidate = (
            await runtime.propose_accretion(  # type: ignore[attr-defined]
                governed_run,
                candidate_kind="procedure",
                content={"steps": ["validate", "prove"]},
                scope=("tenant:local-reference", "project:test"),
                provenance_refs=(evidence_ref,),
            )
        ).require_value()
        promotion = (
            await runtime.promote(candidate)  # type: ignore[attr-defined]
        ).require_value()
        influences = (
            await runtime.retrieve_promoted(  # type: ignore[attr-defined]
                scope=("tenant:local-reference", "project:test"),
                decision_or_output_ref="vcp:artifact:output:test",
            )
        ).require_value()
        assert len(influences) == 1
        revocation = await runtime.revoke(  # type: ignore[attr-defined]
            promotion,
            "contradicting evidence",
        )
        assert revocation.require_value().downstream_influence_refs
        after = (
            await runtime.retrieve_promoted(  # type: ignore[attr-defined]
                scope=("tenant:local-reference", "project:test"),
                decision_or_output_ref="vcp:artifact:output:after",
            )
        ).require_value()
        assert after == ()

    run(scenario())


def test_accretion_blocks_raw_output_inherited_authority_and_cross_tenant_use() -> None:
    async def scenario() -> None:
        service = LocalAccretiveRuntime(clock=lambda: FIXED_NOW)
        runtime, governed_run, evidence_ref = await accretive_setup(service)
        raw = await runtime.propose_accretion(  # type: ignore[attr-defined]
            governed_run,
            candidate_kind="procedure",
            content={"claim": "unsupported"},
            scope=("tenant:local-reference",),
            provenance_refs=("vcp:artifact:model-output:raw",),
        )
        assert raw.status == ResultStatus.BLOCKED
        inherited = await runtime.propose_accretion(  # type: ignore[attr-defined]
            governed_run,
            candidate_kind="procedure",
            content={"grant": "vcp:artifact:grant:old"},
            scope=("tenant:local-reference",),
            provenance_refs=(evidence_ref,),
        )
        assert inherited.status == ResultStatus.BLOCKED
        imported = await runtime.propose_accretion(  # type: ignore[attr-defined]
            governed_run,
            candidate_kind="procedure",
            content={"steps": ["safe"]},
            scope=("tenant:other",),
            provenance_refs=(evidence_ref,),
        )
        assert imported.status == ResultStatus.DEGRADED
        assert imported.require_value().quarantine_status == "quarantined"
        promotion = await runtime.promote(  # type: ignore[attr-defined]
            imported.require_value()
        )
        assert promotion.status == ResultStatus.BLOCKED

    run(scenario())


def test_dependency_change_and_high_stakes_policy_prevent_promotion_or_reuse() -> None:
    async def scenario() -> None:
        service = LocalAccretiveRuntime(clock=lambda: FIXED_NOW)
        runtime, governed_run, evidence_ref = await accretive_setup(service)
        candidate = (
            await runtime.propose_accretion(  # type: ignore[attr-defined]
                governed_run,
                candidate_kind="procedure",
                content={"steps": ["bounded"]},
                scope=("tenant:local-reference",),
                provenance_refs=(evidence_ref,),
            )
        ).require_value()
        promotion = (
            await runtime.promote(candidate)  # type: ignore[attr-defined]
        ).require_value()
        service.rotate_accretion_dependency("tool schema changed")
        reused = (
            await runtime.retrieve_promoted(  # type: ignore[attr-defined]
                scope=("tenant:local-reference",),
                decision_or_output_ref="vcp:artifact:output:dependency-change",
            )
        ).require_value()
        assert reused == ()
        assert promotion.dependency_digest == candidate.dependency_digest

        self_report = (
            await runtime.propose_accretion(  # type: ignore[attr-defined]
                governed_run,
                candidate_kind="self_report",
                content={
                    "authored_expression": "I want to pause",
                    "uncertainty": "interpretation remains uncertain",
                    "detected_signal": "monitor inferred activation",
                },
                scope=("tenant:local-reference",),
                provenance_refs=(evidence_ref,),
                sensitivity="welfare",
            )
        ).require_value()
        assert self_report.review_required
        reviewed = await runtime.promote(self_report)  # type: ignore[attr-defined]
        assert reviewed.status == ResultStatus.AWAITING_REVIEW

    run(scenario())
