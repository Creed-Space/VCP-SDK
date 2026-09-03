"""Explicit observe transport seams with no implicit network behavior."""

from __future__ import annotations

from .contracts import (
    Affordance,
    AffordanceQuery,
    AgentResult,
    Contract,
    Goal,
    ResourceBudget,
    SituationView,
)
from .service import ObserveService


class DelegatingObserveTransport:
    """Transport seam that delegates to the same typed observe service contract."""

    transport_name = "delegating"

    def __init__(self, service: ObserveService) -> None:
        self._service = service

    async def bootstrap(
        self,
        goal: Goal,
        budget: ResourceBudget,
    ) -> AgentResult[SituationView]:
        return await self._service.bootstrap(goal, budget)

    async def find_affordances(
        self,
        situation: SituationView,
        query: AffordanceQuery,
    ) -> AgentResult[tuple[Affordance, ...]]:
        return await self._service.find_affordances(situation, query)

    async def expand(self, ref: str) -> AgentResult[Contract]:
        return await self._service.expand(ref)


class HTTPObserveTransportStub(DelegatingObserveTransport):
    """Typed HTTP integration seam. A host must inject its authenticated service."""

    transport_name = "http"


class MCPObserveTransportStub(DelegatingObserveTransport):
    """Typed MCP integration seam. A host must inject its negotiated service."""

    transport_name = "mcp"
