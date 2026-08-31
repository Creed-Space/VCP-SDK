"""High-level, task-oriented VCP agent facade."""

from __future__ import annotations

from typing import Any

from .contracts import (
    Affordance,
    AffordanceQuery,
    AgentResult,
    Contract,
    Goal,
    Profile,
    ResourceBudget,
    SituationView,
)
from .handles import SituationHandle
from .local import LocalReferenceRuntime
from .service import ObserveService


class AgentRuntime:
    """Observe-only candidate facade over an explicit runtime service."""

    def __init__(self, service: ObserveService, profile: Profile) -> None:
        if profile.name != "observe":
            raise ValueError(
                "this candidate slice implements observe@0.1.0 only; "
                "controlled actions and accretion remain unavailable"
            )
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
                    "remote endpoints require an explicit observe transport; "
                    "the SDK never opens a network connection implicitly"
                )
            service = LocalReferenceRuntime()
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
        return AgentResult[SituationHandle](
            kind=raw.kind,
            version=raw.version,
            meta=raw.meta,
            status=raw.status,
            value=handle,
            assurance=raw.assurance,
            evidence_refs=raw.evidence_refs,
            resources=raw.resources,
            safe_next=raw.safe_next,
            warnings=raw.warnings,
            omissions=raw.omissions,
            failure=raw.failure,
        )

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
