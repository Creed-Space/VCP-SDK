"""Immutable typed handles that retain lineage for agent follow-up calls."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .contracts import (
    Affordance,
    AffordanceQuery,
    AgentResult,
    Contract,
    CursorDelta,
    EffectClass,
    ExecutionReceipt,
    Goal,
    ResourceBudget,
    RunProof,
    RunSpec,
    SituationView,
)

if TYPE_CHECKING:
    from .runtime import AgentRuntime


class SituationHandle:
    """An immutable SituationView bound to the runtime that produced it."""

    _runtime: AgentRuntime
    view: SituationView

    __slots__ = ("_runtime", "view")

    def __init__(self, runtime: AgentRuntime, view: SituationView) -> None:
        object.__setattr__(self, "_runtime", runtime)
        object.__setattr__(self, "view", view)

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError(f"{type(self).__name__} is immutable")

    @property
    def goal(self) -> str:
        return self.view.goal

    @property
    def digest(self) -> str:
        return self.view.digest

    @property
    def unknowns(self) -> tuple[str, ...]:
        return self.view.unknowns

    @property
    def omissions(self) -> tuple[Any, ...]:
        return self.view.omissions

    async def find_affordances(
        self,
        *,
        evidence_for: str | None = None,
        outcome: str | None = None,
        effect_ceiling: EffectClass | str = EffectClass.STATE_READ,
        include_unavailable: bool = True,
        limit: int = 10,
    ) -> AgentResult[tuple[Affordance, ...]]:
        ceiling = (
            effect_ceiling
            if isinstance(effect_ceiling, EffectClass)
            else EffectClass(effect_ceiling)
        )
        return await self._runtime._find_affordances(
            self.view,
            AffordanceQuery(
                evidence_for=evidence_for,
                outcome=outcome,
                effect_ceiling=ceiling,
                include_unavailable=include_unavailable,
                limit=limit,
            ),
        )

    async def expand(self, ref: str) -> AgentResult[Contract]:
        return await self._runtime.expand(ref)

    async def watch(self) -> AgentResult[CursorDelta]:
        return await self._runtime._watch(self.view)

    async def start_run(
        self,
        goal: Goal | str | None = None,
        *,
        budget: ResourceBudget | None = None,
        risk_ceiling: EffectClass | str = EffectClass.REVERSIBLE_WRITE,
    ) -> AgentResult[RunHandle]:
        return await self._runtime._start_run(
            self.view,
            goal if goal is not None else self.view.goal,
            budget=budget,
            risk_ceiling=risk_ceiling,
        )

    def explain(self) -> dict[str, Any]:
        return {
            "situation_id": self.view.situation_id,
            "goal": self.view.goal,
            "known_claim_refs": list(self.view.known_claim_refs),
            "unknowns": list(self.view.unknowns),
            "conflict_refs": list(self.view.conflict_refs),
            "authority_refs": list(self.view.authority_refs),
            "affordance_refs": list(self.view.affordance_refs),
            "omissions": [item.model_dump(mode="json") for item in self.view.omissions],
            "dependency_digest": self.view.dependency_digest,
            "digest": self.view.digest,
        }


class RunHandle:
    """An immutable governed run bound to its producing runtime."""

    _runtime: AgentRuntime
    run: RunSpec

    __slots__ = ("_runtime", "run")

    def __init__(self, runtime: AgentRuntime, run: RunSpec) -> None:
        object.__setattr__(self, "_runtime", runtime)
        object.__setattr__(self, "run", run)

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError(f"{type(self).__name__} is immutable")

    @property
    def ref(self) -> str:
        return self.run.ref

    @property
    def status(self) -> str:
        return self.run.status.value

    async def preflight(
        self,
        affordance: Affordance,
        arguments: dict[str, Any],
    ) -> AgentResult[Contract]:
        return await self._runtime._preflight(self.run, affordance, arguments)

    async def control(
        self,
        operation: str,
        reason: str,
        *,
        idempotency_key: str,
    ) -> AgentResult[Contract]:
        return await self._runtime._control(
            self.run,
            operation,
            reason,
            idempotency_key=idempotency_key,
        )

    async def prove(self) -> AgentResult[RunProof]:
        return await self._runtime._prove(self.run)

    async def reconcile(
        self,
        receipt: ExecutionReceipt,
    ) -> AgentResult[ExecutionReceipt]:
        return await self._runtime._reconcile(receipt)
