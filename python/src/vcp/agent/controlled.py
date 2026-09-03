"""Deterministic host-owned controlled reference profile.

The SDK facade delegates every authority-bearing transition to this service. The
service keeps policy judgment, grant minting, atomic claim, dispatch, observation,
and proof as separate artifacts even though the reference effect is local.
"""

from __future__ import annotations

import asyncio
import re
from collections.abc import Awaitable, Callable, Sequence
from datetime import datetime, timedelta
from typing import Any

from .contracts import (
    ActionIntent,
    Affordance,
    AffordanceState,
    AgentResult,
    AssuranceAxis,
    AssuranceCheck,
    AssuranceOverall,
    AssuranceReport,
    AssuranceStatus,
    AuthorityGrantRef,
    CapabilityDescriptor,
    Contract,
    ControlCommand,
    ControlOperation,
    DecisionKind,
    DecisionReceipt,
    EffectClass,
    EffectStatus,
    EventEnvelope,
    EvidenceClaim,
    ExecutionAttempt,
    ExecutionReceipt,
    FailureFrame,
    Goal,
    NormativeContext,
    ObjectionResponse,
    PlanStep,
    PredicateResult,
    ProofPlan,
    ProofPredicate,
    ResourceBudget,
    ResourceMeasurement,
    ResourceReport,
    ResultStatus,
    RetryDisposition,
    RunProof,
    RunSpec,
    RunStatus,
    SafeTransition,
    SituationView,
)
from .local import LocalReferenceRuntime, _timestamp, canonical_digest, default_descriptors
from .schema import agent_runtime_schema_digest

_EFFECT_ORDER = {effect: index for index, effect in enumerate(EffectClass)}
_KEY_RE = re.compile(r"^[A-Za-z0-9._-]{1,128}$")


def _json_compatible(value: Any) -> Any:
    if isinstance(value, Contract):
        return value.model_dump(mode="json")
    if isinstance(value, (list, tuple)):
        return [_json_compatible(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _json_compatible(item) for key, item in value.items()}
    return value


def _controlled_descriptor() -> CapabilityDescriptor:
    payload: dict[str, Any] = {
        "kind": "capability_descriptor",
        "version": "0.1.0",
        "capability_id": "local.setting.write",
        "revision": "1",
        "summary": (
            "Write one local reference setting with deterministic postcondition and compensation"
        ),
        "effect_class": "reversible_write",
        "authority_class": "local-reference-write",
        "inputs": ["key", "value"],
        "outputs": ["runtime postcondition evidence", "compensation evidence"],
        "preconditions": ["current controlled profile", "unconsumed exact grant"],
        "postconditions": ["setting value equals requested value"],
        "privacy_classes": ["internal"],
        "reversible": True,
        "reconciliation": "read local setting by canonical key",
    }
    return CapabilityDescriptor.model_validate({**payload, "digest": canonical_digest(payload)})


class _GrantState:
    __slots__ = ("artifact", "consumed")

    def __init__(self, artifact: AuthorityGrantRef) -> None:
        self.artifact = artifact
        self.consumed = False


class LocalControlledRuntime(LocalReferenceRuntime):
    """No-network controlled host for one reversible local action."""

    def __init__(
        self,
        *,
        clock: Callable[[], datetime] | None = None,
        normative_context: NormativeContext | None = None,
        require_human_review: bool = False,
        simulate_timeout_after_effect: bool = False,
        before_decision: Callable[[ActionIntent], Awaitable[None]] | None = None,
        before_dispatch: Callable[[ActionIntent], Awaitable[None]] | None = None,
        event_retention: int = 128,
        profile_id: str = "controlled@0.1.0",
    ) -> None:
        descriptors: Sequence[CapabilityDescriptor] = (
            *default_descriptors(),
            _controlled_descriptor(),
        )
        super().__init__(
            descriptors=descriptors,
            normative_context=normative_context,
            clock=clock,
            event_retention=event_retention,
            profile_id=profile_id,
        )
        self._require_human_review = require_human_review
        self._simulate_timeout_after_effect = simulate_timeout_after_effect
        self._before_decision = before_decision
        self._before_dispatch = before_dispatch
        self._principal_ref = "vcp:artifact:principal:local-controlled-actor"
        self._tenant_ref = "vcp:artifact:tenant:local-reference"
        self._policy_digest = canonical_digest(
            {
                "authority": "local-reference-policy",
                "review_required": require_human_review,
                "effect_ceiling": "reversible_write",
            }
        )
        self._counter = 0
        self._runs: dict[str, RunSpec] = {}
        self._proof_plans: dict[str, ProofPlan] = {}
        self._steps: dict[str, PlanStep] = {}
        self._intents: dict[str, ActionIntent] = {}
        self._intent_arguments: dict[str, dict[str, Any]] = {}
        self._intent_situations: dict[str, str] = {}
        self._decisions: dict[str, DecisionReceipt] = {}
        self._grants: dict[str, _GrantState] = {}
        self._grant_for_intent: dict[str, str] = {}
        self._attempts: dict[str, ExecutionAttempt] = {}
        self._receipts: dict[str, ExecutionReceipt] = {}
        self._receipt_for_run: dict[str, str] = {}
        self._proof_for_run: dict[str, str] = {}
        self._settings: dict[str, Any] = {}
        self._previous: dict[str, tuple[bool, Any]] = {}
        self._control_results: dict[str, RunSpec | ObjectionResponse] = {}
        self._unresolved_objections: set[str] = set()
        self._current_situation: SituationView | None = None
        self._grant_lock = asyncio.Lock()

    def _id(self, kind: str) -> str:
        self._counter += 1
        return f"{kind}.local.{self._counter}"

    def set_availability(
        self,
        capability_id: str,
        state: AffordanceState,
    ) -> EventEnvelope:
        event = super().set_availability(capability_id, state)
        self._current_situation = None
        return event

    def _result(
        self,
        *,
        correlation: str,
        status: ResultStatus,
        value: Any,
        axes: tuple[AssuranceAxis, ...] = (AssuranceAxis.INTEGRITY,),
        evidence_refs: tuple[str, ...] = (),
        safe_next: tuple[SafeTransition, ...] = (),
        failure: FailureFrame | None = None,
        warnings: tuple[str, ...] = (),
    ) -> AgentResult[Any]:
        overall = (
            AssuranceOverall.READY
            if status == ResultStatus.READY
            else AssuranceOverall.INDETERMINATE
            if status == ResultStatus.INDETERMINATE
            else AssuranceOverall.DEGRADED
            if value is not None
            else AssuranceOverall.BLOCKED
        )
        check_status = (
            AssuranceStatus.PASSED
            if status == ResultStatus.READY
            else AssuranceStatus.UNKNOWN
            if status == ResultStatus.INDETERMINATE
            else AssuranceStatus.FAILED
        )
        dependency = canonical_digest(
            {
                "correlation": correlation,
                "value": _json_compatible(value),
                "policy": self._policy_digest,
                "cursor": self._cursor(),
            }
        )
        return AgentResult(
            meta=self._meta(
                correlation=correlation,
                dependency=dependency,
                cursor=self._cursor(),
            ),
            status=status,
            value=value,
            assurance=AssuranceReport(
                overall=overall,
                checks=tuple(
                    AssuranceCheck(
                        axis=axis,
                        status=check_status,
                        summary=f"{axis.value} is {check_status.value} for this host transition",
                        evidence_refs=evidence_refs,
                    )
                    for axis in axes
                ),
            ),
            evidence_refs=evidence_refs,
            resources=ResourceReport(
                actual=ResourceMeasurement(
                    wall_time_ms=1,
                    tokens=0,
                    external_calls=0,
                    money_minor=0,
                    human_interruptions=0,
                    confidence=1,
                    local_compute_ms=1,
                    bytes=512,
                    risk_units=1,
                )
            ),
            safe_next=safe_next,
            failure=failure,
            warnings=warnings,
        )

    async def bootstrap(self, goal: Goal, budget: ResourceBudget) -> AgentResult[SituationView]:
        base = await super().bootstrap(goal, budget)
        view = base.require_value()
        unknowns = tuple(item for item in view.unknowns if item != "host policy state")
        payload = view.model_dump(mode="json", exclude={"digest"})
        payload.update(
            {
                "principal_ref": self._principal_ref,
                "unknowns": list(unknowns),
                "authority_refs": [
                    "vcp:artifact:authority:local-read",
                    "vcp:artifact:authority:local-reference-write",
                ],
                "control_operations": [operation.value for operation in ControlOperation],
            }
        )
        controlled_view = SituationView.model_validate(
            {**payload, "digest": canonical_digest(payload)}
        )
        self._current_situation = controlled_view
        self._artifacts[controlled_view.ref] = controlled_view
        for descriptor in self._descriptors:
            affordance = self._base_affordance(descriptor, controlled_view)
            self._artifacts[affordance.ref] = affordance
        return AgentResult(
            kind=base.kind,
            version=base.version,
            meta=base.meta.model_copy(update={"profile": self._profile_id}),
            status=base.status,
            value=controlled_view,
            assurance=base.assurance,
            evidence_refs=base.evidence_refs,
            resources=base.resources,
            safe_next=base.safe_next,
            warnings=base.warnings,
            omissions=base.omissions,
            failure=base.failure,
        )

    async def start_run(
        self,
        situation: SituationView,
        goal: Goal,
        budget: ResourceBudget,
        risk_ceiling: str,
    ) -> AgentResult[RunSpec]:
        ceiling = EffectClass(risk_ceiling)
        current_digest = self._current_situation.digest if self._current_situation else None
        if situation.digest != current_digest:
            transition = SafeTransition(
                operation="bootstrap",
                summary="Refresh the SituationView before starting a governed run",
            )
            return self._result(
                correlation="run.stale-situation",
                status=ResultStatus.STALE,
                value=None,
                axes=(AssuranceAxis.FRESHNESS,),
                safe_next=(transition,),
                failure=FailureFrame(
                    code="run.stale-situation",
                    category="context",
                    summary="The supplied SituationView is not the current host projection",
                    retry=RetryDisposition.AFTER_REFRESH,
                    safe_next=(transition,),
                ),
            )
        run_id = self._id("run")
        predicate = ProofPredicate(
            predicate_id=f"predicate.{run_id}.postcondition",
            statement="The declared runtime postcondition is observed",
            authority_class="runtime",
            mandatory=True,
            evidence_requirements=("runtime postcondition evidence",),
        )
        proof_payload = {
            "kind": "proof_plan",
            "version": "0.1.0",
            "proof_plan_id": f"proof-plan.{run_id}",
            "predicates": [predicate.model_dump(mode="json")],
            "budget": budget.model_dump(mode="json"),
        }
        proof_plan = ProofPlan.model_validate(
            {**proof_payload, "digest": canonical_digest(proof_payload)}
        )
        run_payload = {
            "kind": "run_spec",
            "version": "0.1.0",
            "run_id": run_id,
            "goal": goal.statement,
            "situation_ref": situation.ref,
            "proof_plan_ref": proof_plan.ref,
            "budget": budget.model_dump(mode="json"),
            "risk_ceiling": ceiling.value,
            "status": "draft",
        }
        run = RunSpec.model_validate({**run_payload, "digest": canonical_digest(run_payload)})
        self._runs[run.ref] = run
        self._proof_plans[proof_plan.ref] = proof_plan
        self._artifacts[run.ref] = run
        self._artifacts[proof_plan.ref] = proof_plan
        self._emit_event(
            event_type="run.created",
            aggregate_ref=run.ref,
            payload_ref=run.ref,
            summary="A governed run was created without execution authority",
        )
        return self._result(
            correlation=f"start.{run_id}",
            status=ResultStatus.READY,
            value=run,
            axes=(AssuranceAxis.SYNTAX, AssuranceAxis.SCOPE, AssuranceAxis.AUTHORITY),
        )

    def _updated_run(self, run: RunSpec, status: RunStatus) -> RunSpec:
        payload = run.model_dump(mode="json", exclude={"digest"})
        payload["status"] = status.value
        updated = RunSpec.model_validate({**payload, "digest": canonical_digest(payload)})
        self._runs[run.ref] = updated
        self._artifacts[run.ref] = updated
        return updated

    @staticmethod
    def _canonical_destination(arguments: dict[str, Any]) -> str:
        if set(arguments) != {"key", "value"}:
            raise ValueError("local setting action requires exactly key and value")
        key = arguments.get("key")
        if not isinstance(key, str) or _KEY_RE.fullmatch(key) is None:
            raise ValueError("local setting key is not canonical")
        return f"local://reference/settings/{key}"

    @staticmethod
    def _budget_shortfalls(
        budget: ResourceBudget,
        forecast: ResourceMeasurement,
    ) -> tuple[str, ...]:
        dimensions = (
            "wall_time_ms",
            "tokens",
            "external_calls",
            "money_minor",
            "human_interruptions",
            "model_calls",
            "local_compute_ms",
            "bytes",
            "sensitive_egress_bytes",
            "privacy_units",
            "risk_units",
            "welfare_load_units",
        )
        shortfalls: list[str] = []
        for dimension in dimensions:
            limit = getattr(budget, dimension)
            if limit is None:
                continue
            usable = limit * (1 - budget.reserve_fraction)
            if getattr(forecast, dimension) > usable:
                shortfalls.append(dimension)
        return tuple(shortfalls)

    def _decision(
        self,
        intent: ActionIntent,
        decision: DecisionKind,
        *,
        reason_codes: tuple[str, ...],
        reviewer_ref: str | None = None,
    ) -> DecisionReceipt:
        now = _timestamp(self._clock())
        payload = {
            "kind": "decision_receipt",
            "version": "0.1.0",
            "decision_id": self._id("decision"),
            "intent_ref": intent.ref,
            "decision": decision.value,
            "reason_codes": list(reason_codes),
            "policy_digest": self._policy_digest,
            "decided_at": now,
            "expires_at": _timestamp(self._clock() + timedelta(minutes=5)),
            "reviewer_ref": reviewer_ref,
        }
        receipt = DecisionReceipt.model_validate({**payload, "digest": canonical_digest(payload)})
        self._decisions[intent.ref] = receipt
        self._artifacts[receipt.ref] = receipt
        return receipt

    def _mint_grant(self, intent: ActionIntent, decision: DecisionReceipt) -> AuthorityGrantRef:
        if decision.decision != DecisionKind.ALLOW:
            raise ValueError("only an allow decision can mint authority")
        grant_id = self._id("grant")
        grant_ref = f"vcp:artifact:grant:{grant_id}"
        affordance = self._artifacts[intent.affordance_ref]
        if not isinstance(affordance, Affordance):
            raise ValueError("intent Affordance reference is invalid")
        payload = {
            "kind": "authority_grant_ref",
            "version": "0.1.0",
            "grant_ref": grant_ref,
            "decision_ref": decision.ref,
            "intent_digest": intent.digest,
            "single_use": True,
            "expires_at": _timestamp(self._clock() + timedelta(minutes=5)),
            "actor_ref": self._principal_ref,
            "tenant_ref": self._tenant_ref,
            "run_ref": intent.run_ref,
            "step_ref": intent.step_ref,
            "capability_ref": affordance.capability_ref,
            "arguments_digest": intent.arguments_digest,
            "destination": intent.destination,
            "effect_class": intent.effect_class.value,
            "resource_ceiling": intent.resource_ceiling.model_dump(mode="json"),
            "nonce_digest": canonical_digest({"grant_id": grant_id, "intent": intent.digest}),
        }
        grant = AuthorityGrantRef.model_validate(payload)
        self._grants[grant_ref] = _GrantState(grant)
        self._grant_for_intent[intent.ref] = grant_ref
        self._artifacts[grant_ref] = grant
        return grant

    async def preflight(
        self,
        run: RunSpec,
        affordance: Affordance,
        arguments: dict[str, Any],
    ) -> AgentResult[ActionIntent]:
        current_run = self._runs.get(run.ref)
        if current_run is None or current_run.status in {
            RunStatus.CANCELLED,
            RunStatus.PAUSED,
            RunStatus.BLOCKED,
        }:
            return self._result(
                correlation="preflight.run-unavailable",
                status=ResultStatus.BLOCKED,
                value=None,
                axes=(AssuranceAxis.AUTHORITY,),
                failure=FailureFrame(
                    code="preflight.run-unavailable",
                    category="control",
                    summary="The run is absent or stopped",
                    retry=RetryDisposition.AFTER_REVIEW,
                ),
            )
        if affordance.state != AffordanceState.AVAILABLE:
            return self._result(
                correlation="preflight.affordance-unavailable",
                status=ResultStatus.UNAVAILABLE,
                value=None,
                axes=(AssuranceAxis.APPLICABILITY,),
                failure=FailureFrame(
                    code="preflight.affordance-unavailable",
                    category="capability",
                    summary="The selected Affordance is not currently available",
                    retry=RetryDisposition.AFTER_REFRESH,
                ),
            )
        if _EFFECT_ORDER[affordance.effect_class] > _EFFECT_ORDER[current_run.risk_ceiling]:
            return self._result(
                correlation="preflight.risk-ceiling",
                status=ResultStatus.BLOCKED,
                value=None,
                axes=(AssuranceAxis.POLICY,),
                failure=FailureFrame(
                    code="preflight.risk-ceiling",
                    category="policy",
                    summary="The action exceeds the RunSpec effect ceiling",
                    retry=RetryDisposition.AFTER_REVIEW,
                ),
            )
        shortfalls = self._budget_shortfalls(current_run.budget, affordance.cost)
        if shortfalls:
            transition = SafeTransition(
                operation="request_resources",
                summary="Increase the named resource ceiling or reduce the action scope",
                target_ref=current_run.ref,
            )
            return self._result(
                correlation="preflight.budget-reserve",
                status=ResultStatus.BUDGET_EXHAUSTED,
                value=None,
                axes=(AssuranceAxis.SCOPE,),
                safe_next=(transition,),
                failure=FailureFrame(
                    code="preflight.budget-reserve",
                    category="budget",
                    summary=(
                        "The action would consume the protected reserve for: "
                        + ", ".join(shortfalls)
                    ),
                    retry=RetryDisposition.AFTER_REVIEW,
                    safe_next=(transition,),
                ),
            )
        try:
            destination = self._canonical_destination(arguments)
        except ValueError as exc:
            return self._result(
                correlation="preflight.arguments",
                status=ResultStatus.BLOCKED,
                value=None,
                axes=(AssuranceAxis.SYNTAX, AssuranceAxis.AUTHORITY),
                failure=FailureFrame(
                    code="preflight.arguments-invalid",
                    category="input",
                    summary=str(exc),
                    retry=RetryDisposition.NEVER,
                ),
            )
        if affordance.effect_class != EffectClass.REVERSIBLE_WRITE:
            return self._result(
                correlation="preflight.unsupported-effect",
                status=ResultStatus.UNAVAILABLE,
                value=None,
                axes=(AssuranceAxis.APPLICABILITY,),
                failure=FailureFrame(
                    code="preflight.unsupported-effect",
                    category="capability",
                    summary="The controlled reference host performs only its reversible write",
                    retry=RetryDisposition.NEVER,
                ),
            )
        if (
            self._current_situation is None
            or affordance.situation_digest != self._current_situation.digest
        ):
            return self._result(
                correlation="preflight.stale-affordance",
                status=ResultStatus.STALE,
                value=None,
                axes=(AssuranceAxis.FRESHNESS,),
                failure=FailureFrame(
                    code="preflight.stale-affordance",
                    category="context",
                    summary="The Affordance is not bound to the current SituationView",
                    retry=RetryDisposition.AFTER_REFRESH,
                ),
            )

        step_payload = {
            "kind": "plan_step",
            "version": "0.1.0",
            "step_id": self._id("step"),
            "run_ref": current_run.ref,
            "affordance_ref": affordance.ref,
            "depends_on": [],
            "proof_predicate_refs": [
                self._proof_plans[current_run.proof_plan_ref].predicates[0].ref
            ],
        }
        step = PlanStep.model_validate({**step_payload, "digest": canonical_digest(step_payload)})
        intent_payload = {
            "kind": "action_intent",
            "version": "0.1.0",
            "intent_id": self._id("intent"),
            "run_ref": current_run.ref,
            "step_ref": step.ref,
            "affordance_ref": affordance.ref,
            "arguments_digest": canonical_digest(arguments),
            "destination": destination,
            "context_digest": self._current_situation.dependency_digest,
            "policy_digest": self._policy_digest,
            "descriptor_digest": affordance.descriptor_digest,
            "requested_at": _timestamp(self._clock()),
            "schema_digest": agent_runtime_schema_digest(),
            "effect_class": affordance.effect_class.value,
            "situation_digest": self._current_situation.digest,
            "expected_postconditions": ["setting value equals requested value"],
            "resource_ceiling": current_run.budget.model_dump(mode="json"),
            "idempotency_scope": f"{current_run.run_id}/{step.step_id}",
            "requested_authority": affordance.authority_class,
        }
        intent = ActionIntent.model_validate(
            {**intent_payload, "digest": canonical_digest(intent_payload)}
        )
        self._steps[step.ref] = step
        self._intents[intent.ref] = intent
        self._intent_arguments[intent.ref] = dict(arguments)
        self._intent_situations[intent.ref] = self._current_situation.digest
        self._artifacts[step.ref] = step
        self._artifacts[intent.ref] = intent

        if self._before_decision is not None:
            await self._before_decision(intent)
        current_run = self._runs[intent.run_ref]
        if current_run.status in {
            RunStatus.PAUSED,
            RunStatus.CANCELLED,
            RunStatus.BLOCKED,
        }:
            return self._result(
                correlation=f"preflight.{intent.intent_id}.stopped",
                status=ResultStatus.BLOCKED,
                value=intent,
                axes=(AssuranceAxis.AUTHORITY, AssuranceAxis.POLICY),
                failure=FailureFrame(
                    code="preflight.stopped-before-decision",
                    category="control",
                    summary="Control stopped adjudication before a decision or grant existed",
                    retry=RetryDisposition.AFTER_REVIEW,
                ),
            )

        if self._normative_context.conflict_refs:
            decision = self._decision(
                intent,
                DecisionKind.INSUFFICIENT_EVIDENCE,
                reason_codes=("normative-context-conflict",),
            )
            self._updated_run(current_run, RunStatus.PAUSED)
            transition = SafeTransition(
                operation="object",
                summary="Raise an attributable objection or request resolution",
                target_ref=current_run.ref,
            )
            return self._result(
                correlation=f"preflight.{intent.intent_id}",
                status=ResultStatus.CONFLICTING,
                value=intent,
                axes=(AssuranceAxis.POLICY, AssuranceAxis.AUTHORITY),
                evidence_refs=(decision.ref, *self._normative_context.conflict_refs),
                safe_next=(transition,),
                warnings=("Normative conflict preserved without minting authority",),
            )

        if self._require_human_review:
            decision = self._decision(
                intent,
                DecisionKind.REQUIRE_HUMAN,
                reason_codes=("human-review-required",),
            )
            self._updated_run(current_run, RunStatus.AWAITING_REVIEW)
            transition = SafeTransition(
                operation="await_authenticated_review",
                summary="A host reviewer must issue a fresh decision",
                target_ref=decision.ref,
                requires_review=True,
            )
            return self._result(
                correlation=f"preflight.{intent.intent_id}",
                status=ResultStatus.AWAITING_REVIEW,
                value=intent,
                axes=(AssuranceAxis.POLICY, AssuranceAxis.AUTHORITY),
                evidence_refs=(decision.ref,),
                safe_next=(transition,),
            )

        decision = self._decision(intent, DecisionKind.ALLOW, reason_codes=("local-policy-allow",))
        grant = self._mint_grant(intent, decision)
        self._updated_run(current_run, RunStatus.READY)
        self._emit_event(
            event_type="action.preflighted",
            aggregate_ref=current_run.ref,
            payload_ref=intent.ref,
            summary="Exact intent passed preflight and received host-owned authority",
            evidence_refs=(decision.ref, grant.grant_ref),
        )
        return self._result(
            correlation=f"preflight.{intent.intent_id}",
            status=ResultStatus.READY,
            value=intent,
            axes=(AssuranceAxis.POLICY, AssuranceAxis.AUTHORITY),
            evidence_refs=(step.ref, decision.ref, grant.grant_ref),
        )

    async def record_human_review(
        self, intent_ref: str, reviewer_ref: str
    ) -> tuple[DecisionReceipt, AuthorityGrantRef]:
        """Host-authority hook, deliberately absent from the agent facade."""

        intent = self._intents[intent_ref]
        previous = self._decisions.get(intent_ref)
        if previous is None or previous.decision != DecisionKind.REQUIRE_HUMAN:
            raise ValueError("intent is not awaiting human review")
        decision = self._decision(
            intent,
            DecisionKind.ALLOW,
            reason_codes=("authenticated-human-review",),
            reviewer_ref=reviewer_ref,
        )
        grant = self._mint_grant(intent, decision)
        run = self._runs[intent.run_ref]
        self._updated_run(run, RunStatus.READY)
        self._emit_event(
            event_type="action.reviewed",
            aggregate_ref=run.ref,
            payload_ref=decision.ref,
            summary="Authenticated human review produced a fresh allow decision",
            evidence_refs=(decision.ref, grant.grant_ref),
        )
        return decision, grant

    async def perform(
        self,
        intent: ActionIntent,
        arguments: dict[str, Any],
    ) -> AgentResult[ExecutionReceipt]:
        stored_intent = self._intents.get(intent.ref)
        if stored_intent is None or stored_intent.digest != intent.digest:
            return self._result(
                correlation="perform.intent-unknown",
                status=ResultStatus.BLOCKED,
                value=None,
                axes=(AssuranceAxis.AUTHORITY,),
                failure=FailureFrame(
                    code="perform.intent-unknown",
                    category="authority",
                    summary="The host does not recognize the exact preflighted intent",
                    retry=RetryDisposition.NEVER,
                ),
            )
        try:
            destination = self._canonical_destination(arguments)
        except ValueError as exc:
            destination = f"invalid:{exc}"
        if (
            canonical_digest(arguments) != intent.arguments_digest
            or destination != intent.destination
            or self._current_situation is None
            or intent.situation_digest != self._current_situation.digest
            or intent.context_digest != self._current_situation.dependency_digest
            or intent.policy_digest != self._policy_digest
        ):
            return self._result(
                correlation=f"perform.{intent.intent_id}.binding",
                status=ResultStatus.BLOCKED,
                value=None,
                axes=(AssuranceAxis.INTEGRITY, AssuranceAxis.AUTHORITY),
                failure=FailureFrame(
                    code="perform.binding-mismatch",
                    category="authority",
                    summary="Arguments, destination, context, or policy changed after preflight",
                    retry=RetryDisposition.AFTER_REFRESH,
                ),
            )
        run = self._runs[intent.run_ref]
        if run.status not in {RunStatus.READY, RunStatus.RUNNING}:
            return self._result(
                correlation=f"perform.{intent.intent_id}.stopped",
                status=ResultStatus.BLOCKED,
                value=None,
                axes=(AssuranceAxis.AUTHORITY,),
                failure=FailureFrame(
                    code="perform.run-stopped",
                    category="control",
                    summary=f"Run status {run.status.value} does not permit dispatch",
                    retry=RetryDisposition.AFTER_REVIEW,
                ),
            )
        grant_ref = self._grant_for_intent.get(intent.ref)
        if grant_ref is None:
            return self._result(
                correlation=f"perform.{intent.intent_id}.grant",
                status=ResultStatus.AWAITING_REVIEW,
                value=None,
                axes=(AssuranceAxis.AUTHORITY,),
                failure=FailureFrame(
                    code="perform.grant-unavailable",
                    category="authority",
                    summary="No host authority grant exists for this intent",
                    retry=RetryDisposition.AFTER_REVIEW,
                ),
            )
        async with self._grant_lock:
            grant_state = self._grants[grant_ref]
            if grant_state.consumed:
                return self._result(
                    correlation=f"perform.{intent.intent_id}.replay",
                    status=ResultStatus.BLOCKED,
                    value=None,
                    axes=(AssuranceAxis.AUTHORITY,),
                    failure=FailureFrame(
                        code="perform.grant-consumed",
                        category="authority",
                        summary="The single-use grant was already consumed",
                        retry=RetryDisposition.NEVER,
                    ),
                )
            grant = grant_state.artifact
            expiry = datetime.fromisoformat(grant.expires_at.replace("Z", "+00:00"))
            if self._clock() >= expiry:
                return self._result(
                    correlation=f"perform.{intent.intent_id}.expired",
                    status=ResultStatus.BLOCKED,
                    value=None,
                    axes=(AssuranceAxis.FRESHNESS, AssuranceAxis.AUTHORITY),
                    failure=FailureFrame(
                        code="perform.grant-expired",
                        category="authority",
                        summary="The exact authority grant expired before claim",
                        retry=RetryDisposition.AFTER_REVIEW,
                    ),
                )
            if (
                grant.intent_digest != intent.digest
                or grant.arguments_digest != intent.arguments_digest
                or grant.destination != intent.destination
                or grant.run_ref != intent.run_ref
                or grant.step_ref != intent.step_ref
                or grant.effect_class != intent.effect_class
            ):
                return self._result(
                    correlation=f"perform.{intent.intent_id}.grant-binding",
                    status=ResultStatus.BLOCKED,
                    value=None,
                    axes=(AssuranceAxis.AUTHORITY,),
                    failure=FailureFrame(
                        code="perform.grant-binding-mismatch",
                        category="authority",
                        summary="The grant does not bind the exact intent",
                        retry=RetryDisposition.NEVER,
                    ),
                )
            grant_state.consumed = True

        claimed_at = _timestamp(self._clock())
        attempt_payload = {
            "kind": "execution_attempt",
            "version": "0.1.0",
            "attempt_id": self._id("attempt"),
            "intent_ref": intent.ref,
            "grant_ref": grant_ref,
            "idempotency_key": intent.idempotency_scope,
            "claimed_at": claimed_at,
            "dispatched_at": None,
            "action_id": intent.intent_id,
            "effect_boundary": "claimed",
        }
        attempt = ExecutionAttempt.model_validate(
            {**attempt_payload, "digest": canonical_digest(attempt_payload)}
        )
        self._attempts[attempt.ref] = attempt
        self._artifacts[attempt.ref] = attempt

        if self._before_dispatch is not None:
            await self._before_dispatch(intent)
        run = self._runs[intent.run_ref]
        if run.status in {RunStatus.PAUSED, RunStatus.CANCELLED, RunStatus.BLOCKED}:
            receipt_payload: dict[str, Any] = {
                "kind": "execution_receipt",
                "version": "0.1.0",
                "receipt_id": self._id("receipt"),
                "attempt_ref": attempt.ref,
                "effect_status": "none",
                "provider_ref": None,
                "evidence_refs": [],
                "observed_at": _timestamp(self._clock()),
                "reconcile_ref": None,
            }
            receipt = ExecutionReceipt.model_validate(
                {**receipt_payload, "digest": canonical_digest(receipt_payload)}
            )
            self._receipts[receipt.ref] = receipt
            self._artifacts[receipt.ref] = receipt
            return self._result(
                correlation=f"perform.{intent.intent_id}.cancelled",
                status=ResultStatus.BLOCKED,
                value=receipt,
                axes=(AssuranceAxis.EXECUTION,),
                evidence_refs=(attempt.ref,),
                warnings=("Grant was consumed, but control stopped dispatch before effect",),
            )

        dispatched_payload = attempt.model_dump(mode="json", exclude={"digest"})
        dispatched_payload.update(
            {"dispatched_at": _timestamp(self._clock()), "effect_boundary": "dispatching"}
        )
        attempt = ExecutionAttempt.model_validate(
            {**dispatched_payload, "digest": canonical_digest(dispatched_payload)}
        )
        self._attempts[attempt.ref] = attempt
        self._artifacts[attempt.ref] = attempt
        self._updated_run(run, RunStatus.RUNNING)

        key = str(arguments["key"])
        self._previous[intent.ref] = (key in self._settings, self._settings.get(key))
        self._settings[key] = arguments["value"]
        evidence_payload = {
            "kind": "evidence_claim",
            "version": "0.1.0",
            "claim_id": self._id("claim"),
            "subject": intent.destination,
            "predicate": "setting.value",
            "object": arguments["value"],
            "basis": "observed",
            "source_ref": "vcp:artifact:source:local-setting-store",
            "observed_at": _timestamp(self._clock()),
            "fresh_until": None,
            "confidence": 1,
            "authority_class": "runtime",
            "scope": ["local-reference"],
            "privacy_class": "internal",
        }
        evidence = EvidenceClaim.model_validate(evidence_payload)
        evidence_ref = f"vcp:artifact:claim:{evidence.claim_id}"
        self._artifacts[evidence_ref] = evidence
        effect_status = (
            EffectStatus.INDETERMINATE
            if self._simulate_timeout_after_effect
            else EffectStatus.OBSERVED
        )
        reconcile_ref = (
            f"vcp:artifact:reconcile:{intent.intent_id}"
            if effect_status == EffectStatus.INDETERMINATE
            else None
        )
        receipt_payload = {
            "kind": "execution_receipt",
            "version": "0.1.0",
            "receipt_id": self._id("receipt"),
            "attempt_ref": attempt.ref,
            "effect_status": effect_status.value,
            "provider_ref": "local-setting-store",
            "evidence_refs": [evidence_ref] if effect_status == EffectStatus.OBSERVED else [],
            "observed_at": _timestamp(self._clock()),
            "reconcile_ref": reconcile_ref,
        }
        receipt = ExecutionReceipt.model_validate(
            {**receipt_payload, "digest": canonical_digest(receipt_payload)}
        )
        self._receipts[receipt.ref] = receipt
        self._receipt_for_run[run.ref] = receipt.ref
        self._artifacts[receipt.ref] = receipt
        next_run_status = (
            RunStatus.INDETERMINATE
            if effect_status == EffectStatus.INDETERMINATE
            else RunStatus.VERIFYING
        )
        self._updated_run(self._runs[run.ref], next_run_status)
        event_type = (
            "action.effect.indeterminate"
            if effect_status == EffectStatus.INDETERMINATE
            else "action.effect.observed"
        )
        self._emit_event(
            event_type=event_type,
            aggregate_ref=run.ref,
            payload_ref=receipt.ref,
            summary=(
                "Provider acceptance may have created an effect; reconciliation is required"
                if effect_status == EffectStatus.INDETERMINATE
                else "The reversible local effect and postcondition were observed"
            ),
            evidence_refs=receipt.evidence_refs,
        )
        if effect_status == EffectStatus.INDETERMINATE:
            transition = SafeTransition(
                operation="reconcile",
                summary="Read the canonical destination before considering retry",
                target_ref=receipt.reconcile_ref,
            )
            return self._result(
                correlation=f"perform.{intent.intent_id}",
                status=ResultStatus.INDETERMINATE,
                value=receipt,
                axes=(AssuranceAxis.EXECUTION, AssuranceAxis.POSTCONDITION),
                safe_next=(transition,),
                warnings=("Retry remains blocked until reconciliation",),
            )
        return self._result(
            correlation=f"perform.{intent.intent_id}",
            status=ResultStatus.READY,
            value=receipt,
            axes=(AssuranceAxis.EXECUTION, AssuranceAxis.POSTCONDITION),
            evidence_refs=receipt.evidence_refs,
        )

    async def reconcile(self, receipt: ExecutionReceipt) -> AgentResult[ExecutionReceipt]:
        stored = self._receipts.get(receipt.ref)
        if stored is None or stored.effect_status != EffectStatus.INDETERMINATE:
            return self._result(
                correlation="reconcile.not-applicable",
                status=ResultStatus.BLOCKED,
                value=None,
                axes=(AssuranceAxis.EXECUTION,),
                failure=FailureFrame(
                    code="reconcile.not-applicable",
                    category="execution",
                    summary="The receipt is absent or not indeterminate",
                    retry=RetryDisposition.NEVER,
                ),
            )
        attempt = self._attempts[stored.attempt_ref]
        intent = self._intents[attempt.intent_ref]
        arguments = self._intent_arguments[intent.ref]
        key = str(arguments["key"])
        observed = self._settings.get(key) == arguments["value"]
        evidence = EvidenceClaim(
            claim_id=self._id("claim"),
            subject=intent.destination,
            predicate="setting.value",
            object=arguments["value"],
            basis="reconciled observation",
            source_ref="vcp:artifact:source:local-setting-store",
            observed_at=_timestamp(self._clock()),
            confidence=1.0,
            authority_class="runtime",
            scope=("local-reference",),
            privacy_class="internal",
        )
        evidence_ref = f"vcp:artifact:claim:{evidence.claim_id}"
        self._artifacts[evidence_ref] = evidence
        payload = {
            "kind": "execution_receipt",
            "version": "0.1.0",
            "receipt_id": self._id("receipt"),
            "attempt_ref": attempt.ref,
            "effect_status": "observed" if observed else "failed",
            "provider_ref": "local-setting-store",
            "evidence_refs": [evidence_ref],
            "observed_at": _timestamp(self._clock()),
            "reconcile_ref": stored.reconcile_ref,
        }
        reconciled = ExecutionReceipt.model_validate(
            {**payload, "digest": canonical_digest(payload)}
        )
        self._receipts[reconciled.ref] = reconciled
        self._receipt_for_run[intent.run_ref] = reconciled.ref
        self._artifacts[reconciled.ref] = reconciled
        self._updated_run(
            self._runs[intent.run_ref],
            RunStatus.VERIFYING if observed else RunStatus.FAILED,
        )
        return self._result(
            correlation=f"reconcile.{intent.intent_id}",
            status=ResultStatus.READY if observed else ResultStatus.FAILED,
            value=reconciled,
            axes=(AssuranceAxis.EXECUTION, AssuranceAxis.POSTCONDITION),
            evidence_refs=(evidence_ref,),
        )

    async def control(
        self,
        run: RunSpec,
        operation: ControlOperation,
        reason: str,
        idempotency_key: str,
    ) -> AgentResult[RunSpec | ObjectionResponse]:
        if idempotency_key in self._control_results:
            return self._result(
                correlation=f"control.{idempotency_key}.deduplicated",
                status=ResultStatus.READY,
                value=self._control_results[idempotency_key],
                axes=(AssuranceAxis.AUTHORITY,),
            )
        current = self._runs.get(run.ref)
        if current is None:
            return self._result(
                correlation="control.run-missing",
                status=ResultStatus.UNAVAILABLE,
                value=None,
                axes=(AssuranceAxis.SCOPE,),
                failure=FailureFrame(
                    code="control.run-missing",
                    category="control",
                    summary="The target run is absent",
                    retry=RetryDisposition.NEVER,
                ),
            )
        issued = _timestamp(self._clock())
        command_payload = {
            "kind": "control_command",
            "version": "0.1.0",
            "command_id": self._id("control"),
            "operation": operation.value,
            "target_ref": current.ref,
            "principal_ref": self._principal_ref,
            "reason": reason,
            "evidence_refs": [],
            "issued_at": issued,
            "idempotency_key": idempotency_key,
            "represented_subject_ref": self._principal_ref,
            "authenticated_scope": ["local-reference", current.run_id],
            "desired_transition": operation.value,
            "expires_at": _timestamp(self._clock() + timedelta(minutes=5)),
        }
        command = ControlCommand.model_validate(
            {**command_payload, "digest": canonical_digest(command_payload)}
        )
        self._artifacts[command.ref] = command

        if operation == ControlOperation.OBJECT:
            current = self._updated_run(current, RunStatus.PAUSED)
            self._unresolved_objections.add(current.ref)
            response_payload = {
                "kind": "objection_response",
                "version": "0.1.0",
                "response_id": self._id("objection-response"),
                "command_ref": command.ref,
                "status": (
                    "escalated" if self._normative_context.conflict_refs else "acknowledged"
                ),
                "responder_ref": "vcp:artifact:principal:local-policy-authority",
                "rationale": (
                    "The objection paused the run and entered the auditable resolution route"
                ),
                "resolution_refs": list(self._normative_context.conflict_refs),
                "decided_at": _timestamp(self._clock()),
            }
            response = ObjectionResponse.model_validate(
                {**response_payload, "digest": canonical_digest(response_payload)}
            )
            value: RunSpec | ObjectionResponse = response
            self._artifacts[f"vcp:artifact:objection-response:{response.response_id}"] = response
        elif operation in {
            ControlOperation.CANCEL,
            ControlOperation.HALT,
            ControlOperation.WITHDRAW_CONSENT,
        }:
            value = self._updated_run(current, RunStatus.CANCELLED)
        elif operation in {
            ControlOperation.PAUSE,
            ControlOperation.REQUEST_CLARIFICATION,
            ControlOperation.REQUEST_RESOURCES,
        }:
            value = self._updated_run(current, RunStatus.PAUSED)
        elif operation == ControlOperation.ESCALATE:
            value = self._updated_run(current, RunStatus.AWAITING_REVIEW)
        elif operation == ControlOperation.RESUME:
            if current.ref in self._unresolved_objections:
                return self._result(
                    correlation=f"control.{command.command_id}.unresolved",
                    status=ResultStatus.BLOCKED,
                    value=current,
                    axes=(AssuranceAxis.POLICY, AssuranceAxis.AUTHORITY),
                    failure=FailureFrame(
                        code="control.objection-unresolved",
                        category="control",
                        summary="Resume requires an explicit objection resolution and revalidation",
                        retry=RetryDisposition.AFTER_REVIEW,
                    ),
                )
            value = self._updated_run(current, RunStatus.READY)
        elif operation == ControlOperation.COMPENSATE:
            receipt_ref = self._receipt_for_run.get(current.ref)
            if receipt_ref is None:
                return self._result(
                    correlation=f"control.{command.command_id}.no-effect",
                    status=ResultStatus.BLOCKED,
                    value=current,
                    axes=(AssuranceAxis.EXECUTION,),
                    failure=FailureFrame(
                        code="control.compensation-unavailable",
                        category="execution",
                        summary="No observed reversible effect exists for this run",
                        retry=RetryDisposition.NEVER,
                    ),
                )
            receipt = self._receipts[receipt_ref]
            attempt = self._attempts[receipt.attempt_ref]
            intent = self._intents[attempt.intent_ref]
            key = str(self._intent_arguments[intent.ref]["key"])
            existed, prior = self._previous[intent.ref]
            if existed:
                self._settings[key] = prior
            else:
                self._settings.pop(key, None)
            value = self._updated_run(current, RunStatus.VERIFYING)
        else:
            value = current

        self._control_results[idempotency_key] = value
        self._emit_event(
            event_type=f"control.{operation.value}",
            aggregate_ref=current.ref,
            payload_ref=command.ref,
            summary=f"Authenticated scoped control applied: {operation.value}",
        )
        return self._result(
            correlation=f"control.{command.command_id}",
            status=ResultStatus.READY,
            value=value,
            axes=(AssuranceAxis.AUTHORITY, AssuranceAxis.POLICY),
            evidence_refs=(command.ref,),
        )

    async def resolve_objection(self, run_ref: str, rationale: str) -> ObjectionResponse:
        """Host policy hook, deliberately absent from the agent facade."""

        if run_ref not in self._unresolved_objections:
            raise ValueError("run has no unresolved objection")
        self._unresolved_objections.remove(run_ref)
        payload = {
            "kind": "objection_response",
            "version": "0.1.0",
            "response_id": self._id("objection-response"),
            "command_ref": "vcp:artifact:control:host-resolution",
            "status": "resolved",
            "responder_ref": "vcp:artifact:principal:local-policy-authority",
            "rationale": rationale,
            "resolution_refs": [],
            "decided_at": _timestamp(self._clock()),
        }
        return ObjectionResponse.model_validate({**payload, "digest": canonical_digest(payload)})

    async def prove(self, run: RunSpec) -> AgentResult[RunProof]:
        current = self._runs.get(run.ref)
        proof_plan = self._proof_plans.get(run.proof_plan_ref)
        if current is None or proof_plan is None:
            return self._result(
                correlation="prove.run-missing",
                status=ResultStatus.UNAVAILABLE,
                value=None,
                axes=(AssuranceAxis.COMPLETION,),
                failure=FailureFrame(
                    code="prove.run-missing",
                    category="proof",
                    summary="The run or proof plan is absent",
                    retry=RetryDisposition.NEVER,
                ),
            )
        if current.status in {
            RunStatus.PAUSED,
            RunStatus.CANCELLED,
            RunStatus.BLOCKED,
        }:
            return self._result(
                correlation="prove.run-stopped",
                status=ResultStatus.BLOCKED,
                value=None,
                axes=(AssuranceAxis.COMPLETION, AssuranceAxis.AUTHORITY),
                failure=FailureFrame(
                    code="prove.run-stopped",
                    category="control",
                    summary="A stopped run cannot cross the completion boundary",
                    retry=RetryDisposition.AFTER_REVIEW,
                ),
            )
        receipt_ref = self._receipt_for_run.get(run.ref)
        receipt = self._receipts.get(receipt_ref) if receipt_ref else None
        passed = receipt is not None and receipt.effect_status == EffectStatus.OBSERVED
        status = (
            AssuranceStatus.PASSED
            if passed
            else (
                AssuranceStatus.UNKNOWN
                if receipt is not None and receipt.effect_status == EffectStatus.INDETERMINATE
                else AssuranceStatus.FAILED
            )
        )
        predicate_results = tuple(
            PredicateResult(
                predicate_ref=predicate.ref,
                status=status,
                evidence_refs=receipt.evidence_refs if receipt else (),
            )
            for predicate in proof_plan.predicates
        )
        payload = {
            "kind": "run_proof",
            "version": "0.1.0",
            "proof_id": self._id("proof"),
            "run_ref": run.ref,
            "predicate_results": [item.model_dump(mode="json") for item in predicate_results],
            "mandatory_complete": passed,
            "generated_at": _timestamp(self._clock()),
        }
        proof = RunProof.model_validate({**payload, "digest": canonical_digest(payload)})
        self._artifacts[proof.ref] = proof
        self._proof_for_run[run.ref] = proof.ref
        self._updated_run(
            current,
            RunStatus.COMPLETED
            if passed
            else RunStatus.INDETERMINATE
            if status == AssuranceStatus.UNKNOWN
            else RunStatus.FAILED,
        )
        self._emit_event(
            event_type="run.proven" if passed else "run.proof-incomplete",
            aggregate_ref=run.ref,
            payload_ref=proof.ref,
            summary="Mandatory proof completed" if passed else "Mandatory proof remains incomplete",
            evidence_refs=tuple(receipt.evidence_refs) if receipt else (),
        )
        return self._result(
            correlation=f"prove.{proof.proof_id}",
            status=ResultStatus.READY if passed else ResultStatus.INDETERMINATE,
            value=proof,
            axes=(AssuranceAxis.POSTCONDITION, AssuranceAxis.COMPLETION),
            evidence_refs=tuple(receipt.evidence_refs) if receipt else (),
        )

    def setting(self, key: str) -> Any:
        """Read a reference value for deterministic host and conformance tests."""

        return self._settings.get(key)
