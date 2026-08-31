"""Service boundary shared by local and transported observe runtimes."""

from __future__ import annotations

from typing import Protocol

from .contracts import (
    Affordance,
    AffordanceQuery,
    AgentResult,
    Contract,
    Goal,
    ResourceBudget,
    SituationView,
)


class ObserveService(Protocol):
    """The complete service surface of the observe-only vertical slice."""

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
