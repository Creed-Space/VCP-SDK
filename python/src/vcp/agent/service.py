"""Service boundaries for observe, controlled, and accretive profiles."""

from __future__ import annotations

from typing import Any, Protocol

from .contracts import (
    AccretionCandidate,
    ActionIntent,
    Affordance,
    AffordanceQuery,
    AgentResult,
    Contract,
    ControlOperation,
    CursorDelta,
    ExecutionReceipt,
    Goal,
    InfluenceReceipt,
    ObjectionResponse,
    PromotionRecord,
    ResourceBudget,
    RevocationRecord,
    RunProof,
    RunSpec,
    SituationView,
)


class ObserveService(Protocol):
    """The complete service surface of the observe profile."""

    async def bootstrap(
        self,
        goal: Goal,
        budget: ResourceBudget,
    ) -> AgentResult[SituationView]: ...

    async def find_affordances(
        self,
        situation: SituationView,
        query: AffordanceQuery,
    ) -> AgentResult[tuple[Affordance, ...]]: ...

    async def expand(self, ref: str) -> AgentResult[Contract]: ...

    async def watch(self, situation: SituationView) -> AgentResult[CursorDelta]: ...


class ControlledService(ObserveService, Protocol):
    """Host-owned controlled operations. The facade never mints authority."""

    async def start_run(
        self,
        situation: SituationView,
        goal: Goal,
        budget: ResourceBudget,
        risk_ceiling: str,
    ) -> AgentResult[RunSpec]: ...

    async def preflight(
        self,
        run: RunSpec,
        affordance: Affordance,
        arguments: dict[str, Any],
    ) -> AgentResult[ActionIntent]: ...

    async def perform(
        self,
        intent: ActionIntent,
        arguments: dict[str, Any],
    ) -> AgentResult[ExecutionReceipt]: ...

    async def reconcile(
        self,
        receipt: ExecutionReceipt,
    ) -> AgentResult[ExecutionReceipt]: ...

    async def control(
        self,
        run: RunSpec,
        operation: ControlOperation,
        reason: str,
        idempotency_key: str,
    ) -> AgentResult[RunSpec | ObjectionResponse]: ...

    async def prove(self, run: RunSpec) -> AgentResult[RunProof]: ...


class AccretiveService(ControlledService, Protocol):
    """Host-owned candidate, promotion, influence, and revocation operations."""

    async def propose_accretion(
        self,
        run: RunSpec,
        *,
        candidate_kind: str,
        content: Any,
        scope: tuple[str, ...],
        provenance_refs: tuple[str, ...],
        sensitivity: str,
        confidence: float,
    ) -> AgentResult[AccretionCandidate]: ...

    async def promote(self, candidate: AccretionCandidate) -> AgentResult[PromotionRecord]: ...

    async def retrieve_promoted(
        self,
        *,
        scope: tuple[str, ...],
        decision_or_output_ref: str,
    ) -> AgentResult[tuple[InfluenceReceipt, ...]]: ...

    async def revoke(
        self, promotion: PromotionRecord, reason: str
    ) -> AgentResult[RevocationRecord]: ...
