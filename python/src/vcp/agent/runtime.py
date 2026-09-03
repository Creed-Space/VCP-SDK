"""High-level, task-oriented VCP agent facade."""

from __future__ import annotations

from typing import Any, TypeVar, cast

from .accretion import LocalAccretiveRuntime
from .contracts import (
    AccretionCandidate,
    ActionIntent,
    Affordance,
    AffordanceQuery,
    AgentResult,
    Contract,
    ControlOperation,
    CursorDelta,
    EffectClass,
    ExecutionReceipt,
    Goal,
    InfluenceReceipt,
    ObjectionResponse,
    Profile,
    PromotionRecord,
    ResourceBudget,
    RevocationRecord,
    RunProof,
    RunSpec,
    SituationView,
)
from .controlled import LocalControlledRuntime
from .handles import RunHandle, SituationHandle
from .local import LocalReferenceRuntime
from .service import AccretiveService, ControlledService, ObserveService

T = TypeVar("T")
U = TypeVar("U")


def _replace_value(result: AgentResult[T], value: U | None) -> AgentResult[U]:
    """Preserve the result grammar while replacing only its typed value."""

    return AgentResult[U](
        kind=result.kind,
        version=result.version,
        meta=result.meta,
        status=result.status,
        value=value,
        assurance=result.assurance,
        evidence_refs=result.evidence_refs,
        resources=result.resources,
        safe_next=result.safe_next,
        warnings=result.warnings,
        omissions=result.omissions,
        failure=result.failure,
    )


class AgentRuntime:
    """Observe profile facade. More capable profiles use explicit subclasses."""

    def __init__(self, service: ObserveService, profile: Profile) -> None:
        self._service = service
        self.profile = profile
        self._closed = False

    @classmethod
    def connect(
        cls,
        endpoint: str = "local://reference",
        *,
        profile: Profile | str = "observe@0.1.0",
        service: ObserveService | None = None,
    ) -> AgentRuntime:
        selected = cls._parse_profile(profile)
        if service is None:
            if endpoint != "local://reference":
                raise ValueError(
                    "remote endpoints require an explicit typed transport; "
                    "the SDK never opens a network connection implicitly"
                )
            if selected.name == "observe":
                service = LocalReferenceRuntime()
            elif selected.name == "controlled":
                service = LocalControlledRuntime()
            else:
                service = LocalAccretiveRuntime()
        if selected.name == "controlled":
            return ControlledAgentRuntime(cast(ControlledService, service), selected)
        if selected.name == "accretive":
            return AccretiveAgentRuntime(cast(AccretiveService, service), selected)
        return cls(service, selected)

    @staticmethod
    def _parse_profile(profile: Profile | str) -> Profile:
        if isinstance(profile, Profile):
            return profile
        name, separator, version = profile.partition("@")
        if not separator:
            raise ValueError("profile must use name@version")
        return Profile(name=name, version=version)

    async def __aenter__(self) -> AgentRuntime:
        if self._closed:
            raise RuntimeError("AgentRuntime cannot be reopened after close")
        return self

    async def __aexit__(self, *_: Any) -> None:
        self._closed = True

    def _ensure_open(self) -> None:
        if self._closed:
            raise RuntimeError("AgentRuntime is closed")

    async def bootstrap(
        self,
        goal: Goal | str,
        *,
        budget: ResourceBudget | None = None,
    ) -> AgentResult[SituationHandle]:
        self._ensure_open()
        objective = goal if isinstance(goal, Goal) else Goal(statement=goal)
        raw = await self._service.bootstrap(
            objective,
            budget or ResourceBudget.observe_default(),
        )
        handle = SituationHandle(self, raw.value) if raw.value is not None else None
        return _replace_value(raw, handle)

    async def _find_affordances(
        self,
        situation: SituationView,
        query: AffordanceQuery,
    ) -> AgentResult[tuple[Affordance, ...]]:
        self._ensure_open()
        return await self._service.find_affordances(situation, query)

    async def expand(self, ref: str) -> AgentResult[Contract]:
        self._ensure_open()
        return await self._service.expand(ref)

    async def _watch(self, situation: SituationView) -> AgentResult[CursorDelta]:
        self._ensure_open()
        return await self._service.watch(situation)

    async def _start_run(
        self,
        situation: SituationView,
        goal: Goal | str,
        *,
        budget: ResourceBudget | None,
        risk_ceiling: EffectClass | str,
    ) -> AgentResult[RunHandle]:
        raise RuntimeError("start_run requires controlled@0.1.0 or accretive@0.1.0")

    async def _preflight(
        self,
        run: RunSpec,
        affordance: Affordance,
        arguments: dict[str, Any],
    ) -> AgentResult[Contract]:
        raise RuntimeError("preflight requires controlled@0.1.0 or accretive@0.1.0")

    async def _control(
        self,
        run: RunSpec,
        operation: str,
        reason: str,
        *,
        idempotency_key: str,
    ) -> AgentResult[Contract]:
        raise RuntimeError("control requires controlled@0.1.0 or accretive@0.1.0")

    async def _prove(self, run: RunSpec) -> AgentResult[RunProof]:
        raise RuntimeError("prove requires controlled@0.1.0 or accretive@0.1.0")

    async def _reconcile(self, receipt: ExecutionReceipt) -> AgentResult[ExecutionReceipt]:
        raise RuntimeError("reconcile requires controlled@0.1.0 or accretive@0.1.0")


class ControlledAgentRuntime(AgentRuntime):
    """Controlled facade over a host service that alone owns policy and grants."""

    _service: ControlledService

    def __init__(self, service: ControlledService, profile: Profile) -> None:
        super().__init__(service, profile)

    async def start_run(
        self,
        situation: SituationHandle | SituationView,
        goal: Goal | str | None = None,
        *,
        budget: ResourceBudget | None = None,
        risk_ceiling: EffectClass | str = EffectClass.REVERSIBLE_WRITE,
    ) -> AgentResult[RunHandle]:
        view = situation.view if isinstance(situation, SituationHandle) else situation
        return await self._start_run(
            view,
            goal if goal is not None else view.goal,
            budget=budget,
            risk_ceiling=risk_ceiling,
        )

    async def _start_run(
        self,
        situation: SituationView,
        goal: Goal | str,
        *,
        budget: ResourceBudget | None,
        risk_ceiling: EffectClass | str,
    ) -> AgentResult[RunHandle]:
        self._ensure_open()
        objective = goal if isinstance(goal, Goal) else Goal(statement=goal)
        ceiling = risk_ceiling.value if isinstance(risk_ceiling, EffectClass) else risk_ceiling
        raw = await self._service.start_run(
            situation,
            objective,
            budget or ResourceBudget.controlled_default(),
            ceiling,
        )
        handle = RunHandle(self, raw.value) if raw.value is not None else None
        return _replace_value(raw, handle)

    async def preflight(
        self,
        run: RunHandle | RunSpec,
        affordance: Affordance,
        arguments: dict[str, Any],
    ) -> AgentResult[ActionIntent]:
        self._ensure_open()
        spec = run.run if isinstance(run, RunHandle) else run
        return await self._service.preflight(spec, affordance, arguments)

    async def _preflight(
        self,
        run: RunSpec,
        affordance: Affordance,
        arguments: dict[str, Any],
    ) -> AgentResult[Contract]:
        return cast(AgentResult[Contract], await self.preflight(run, affordance, arguments))

    async def perform(
        self,
        intent: ActionIntent,
        arguments: dict[str, Any],
    ) -> AgentResult[ExecutionReceipt]:
        self._ensure_open()
        return await self._service.perform(intent, arguments)

    async def reconcile(
        self,
        receipt: ExecutionReceipt,
    ) -> AgentResult[ExecutionReceipt]:
        self._ensure_open()
        return await self._service.reconcile(receipt)

    async def _reconcile(
        self,
        receipt: ExecutionReceipt,
    ) -> AgentResult[ExecutionReceipt]:
        return await self.reconcile(receipt)

    async def control(
        self,
        run: RunHandle | RunSpec,
        operation: ControlOperation | str,
        reason: str,
        *,
        idempotency_key: str,
    ) -> AgentResult[RunSpec | ObjectionResponse]:
        self._ensure_open()
        spec = run.run if isinstance(run, RunHandle) else run
        selected = (
            operation if isinstance(operation, ControlOperation) else ControlOperation(operation)
        )
        return await self._service.control(spec, selected, reason, idempotency_key)

    async def _control(
        self,
        run: RunSpec,
        operation: str,
        reason: str,
        *,
        idempotency_key: str,
    ) -> AgentResult[Contract]:
        return cast(
            AgentResult[Contract],
            await self.control(
                run,
                operation,
                reason,
                idempotency_key=idempotency_key,
            ),
        )

    async def prove(self, run: RunHandle | RunSpec) -> AgentResult[RunProof]:
        self._ensure_open()
        spec = run.run if isinstance(run, RunHandle) else run
        return await self._service.prove(spec)

    async def _prove(self, run: RunSpec) -> AgentResult[RunProof]:
        return await self.prove(run)


class AccretiveAgentRuntime(ControlledAgentRuntime):
    """Accretive facade with candidate-first memory and traceable influence."""

    _service: AccretiveService

    def __init__(self, service: AccretiveService, profile: Profile) -> None:
        super().__init__(service, profile)

    async def propose_accretion(
        self,
        run: RunHandle | RunSpec,
        *,
        candidate_kind: str,
        content: Any,
        scope: tuple[str, ...],
        provenance_refs: tuple[str, ...],
        sensitivity: str = "internal",
        confidence: float = 1.0,
    ) -> AgentResult[AccretionCandidate]:
        self._ensure_open()
        spec = run.run if isinstance(run, RunHandle) else run
        return await self._service.propose_accretion(
            spec,
            candidate_kind=candidate_kind,
            content=content,
            scope=scope,
            provenance_refs=provenance_refs,
            sensitivity=sensitivity,
            confidence=confidence,
        )

    async def promote(
        self,
        candidate: AccretionCandidate,
    ) -> AgentResult[PromotionRecord]:
        self._ensure_open()
        return await self._service.promote(candidate)

    async def retrieve_promoted(
        self,
        *,
        scope: tuple[str, ...],
        decision_or_output_ref: str,
    ) -> AgentResult[tuple[InfluenceReceipt, ...]]:
        self._ensure_open()
        return await self._service.retrieve_promoted(
            scope=scope,
            decision_or_output_ref=decision_or_output_ref,
        )

    async def revoke(
        self,
        promotion: PromotionRecord,
        reason: str,
    ) -> AgentResult[RevocationRecord]:
        self._ensure_open()
        return await self._service.revoke(promotion, reason)
