"""Deterministic, observe-only reference runtime for the agent facade."""

from __future__ import annotations

import hashlib
from collections.abc import Callable, Mapping, Sequence
from datetime import datetime, timezone
from typing import Any

import rfc8785

from .cache import CacheKey, ContentAddressedCache
from .contracts import (
    Affordance,
    AffordanceQuery,
    AffordanceState,
    AgentResult,
    AssuranceAxis,
    AssuranceCheck,
    AssuranceOverall,
    AssuranceReport,
    AssuranceStatus,
    CapabilityDescriptor,
    Contract,
    CursorDelta,
    EffectClass,
    EventEnvelope,
    EvidenceClaim,
    FailureFrame,
    Goal,
    NormativeClause,
    NormativeContext,
    ResourceBudget,
    ResourceMeasurement,
    ResourceReport,
    ResultMeta,
    ResultStatus,
    RetryDisposition,
    SafeTransition,
    SituationView,
)
from .schema import agent_runtime_schema_digest

_EFFECT_ORDER = {
    EffectClass.PURE_LOCAL: 0,
    EffectClass.STATE_READ: 1,
    EffectClass.SENSITIVE_EGRESS: 2,
    EffectClass.REVERSIBLE_WRITE: 3,
    EffectClass.COMMUNICATION: 4,
    EffectClass.FINANCIAL: 5,
    EffectClass.LEGAL: 6,
    EffectClass.PHYSICAL: 7,
}
_STATE_ORDER = {
    AffordanceState.AVAILABLE: 0,
    AffordanceState.CONDITIONAL: 1,
    AffordanceState.STALE: 2,
    AffordanceState.UNAVAILABLE: 3,
}


def canonical_digest(value: Any) -> str:
    """Return an RFC 8785 SHA-256 digest for JSON-compatible data."""

    return f"sha256:{hashlib.sha256(rfc8785.dumps(value)).hexdigest()}"


def _timestamp(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("reference runtime clock must return a timezone-aware datetime")
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _descriptor(
    *,
    capability_id: str,
    summary: str,
    effect_class: EffectClass,
    outputs: tuple[str, ...],
    authority_class: str = "local-observe",
    inputs: tuple[str, ...] = (),
    preconditions: tuple[str, ...] = (),
) -> CapabilityDescriptor:
    payload: dict[str, Any] = {
        "kind": "capability_descriptor",
        "version": "0.1.0",
        "capability_id": capability_id,
        "revision": "1",
        "summary": summary,
        "effect_class": effect_class.value,
        "authority_class": authority_class,
        "inputs": list(inputs),
        "outputs": list(outputs),
        "preconditions": list(preconditions),
        "postconditions": [],
        "privacy_classes": ["internal"],
        "reversible": False,
        "reconciliation": "none",
    }
    return CapabilityDescriptor.model_validate({**payload, "digest": canonical_digest(payload)})


def default_descriptors() -> tuple[CapabilityDescriptor, ...]:
    """Return the deliberately small local observe capability catalog."""

    return (
        _descriptor(
            capability_id="verify.bundle.integrity",
            summary="Verify local VCP bundle structure, canonical content, and content digest",
            effect_class=EffectClass.PURE_LOCAL,
            inputs=("bundle",),
            outputs=("bundle integrity evidence", "schema evidence"),
        ),
        _descriptor(
            capability_id="inspect.assurance",
            summary="Explain assurance axes, evidence references, omissions, and safe next steps",
            effect_class=EffectClass.PURE_LOCAL,
            inputs=("artifact",),
            outputs=("assurance explanation",),
        ),
        _descriptor(
            capability_id="read.context.snapshot",
            summary="Read a bounded local context snapshot without changing host state",
            effect_class=EffectClass.STATE_READ,
            outputs=("current context evidence", "freshness evidence"),
            preconditions=("local read authority remains current",),
        ),
    )


def default_claims(now: str) -> tuple[EvidenceClaim, ...]:
    return (
        EvidenceClaim(
            claim_id="claim.local.reference-runtime",
            subject="local reference runtime",
            predicate="runtime.mode",
            object="observe-only",
            basis="observed",
            source_ref="vcp:artifact:source:local-reference-runtime",
            observed_at=now,
            confidence=1.0,
            authority_class="local-runtime",
            scope=("local",),
            privacy_class="internal",
        ),
    )


class LocalReferenceRuntime:
    """A no-network reference host that cannot authorize or perform actions."""

    def __init__(
        self,
        *,
        descriptors: Sequence[CapabilityDescriptor] | None = None,
        claims: Sequence[EvidenceClaim] | None = None,
        availability: Mapping[str, AffordanceState] | None = None,
        normative_context: NormativeContext | None = None,
        clock: Callable[[], datetime] | None = None,
        cache_entries: int = 256,
        event_retention: int = 128,
        profile_id: str = "observe@0.1.0",
    ) -> None:
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._profile_id = profile_id
        now = _timestamp(self._clock())
        self._descriptors = tuple(descriptors or default_descriptors())
        self._claims = tuple(claims or default_claims(now))
        self._availability = {
            descriptor.capability_id: AffordanceState.AVAILABLE for descriptor in self._descriptors
        }
        if availability is not None:
            unknown = set(availability) - {
                descriptor.capability_id for descriptor in self._descriptors
            }
            if unknown:
                raise ValueError(f"availability names unknown capabilities: {sorted(unknown)}")
            self._availability.update(availability)
        self._artifacts: dict[str, Contract] = {
            descriptor.ref: descriptor for descriptor in self._descriptors
        }
        self._cursor_sequence = 0
        self._event_retention = max(event_retention, 1)
        self._events: list[EventEnvelope] = []
        self._cache: ContentAddressedCache[AgentResult[Any]] = ContentAddressedCache(cache_entries)
        self._schema_digest = agent_runtime_schema_digest()
        self._catalog_digest = canonical_digest(
            [descriptor.model_dump(mode="json") for descriptor in self._descriptors]
        )
        self._normative_context = normative_context or self._default_normative_context()
        self._artifacts[self._normative_context.ref] = self._normative_context

    def _default_normative_context(self) -> NormativeContext:
        clause = NormativeClause(
            clause_id="clause.local.observe-only",
            source_ref="vcp:artifact:source:local-reference-runtime",
            author_ref="vcp:artifact:principal:local-observer",
            represented_constituency="local reference runtime participants",
            clause_kind="constraint",
            hardness="constraint",
            priority=100,
            effect="require",
            statement="Observe operations must not create execution or promotion authority",
            scope=("local-reference",),
        )
        payload: dict[str, Any] = {
            "kind": "normative_context",
            "version": "0.1.0",
            "clauses": [clause.model_dump(mode="json")],
            "conflict_refs": [],
            "omissions": [],
            "resolution_rule": None,
            "selected_clause_refs": [clause.clause_id],
        }
        return NormativeContext.model_validate({**payload, "digest": canonical_digest(payload)})

    def _cursor(self) -> str:
        return f"cursor.local.{self._cursor_sequence}"

    def _emit_event(
        self,
        *,
        event_type: str,
        aggregate_ref: str,
        payload_ref: str,
        summary: str,
        evidence_refs: tuple[str, ...] = (),
    ) -> EventEnvelope:
        self._cursor_sequence += 1
        now = _timestamp(self._clock())
        previous = self._events[-1].digest if self._events else None
        payload = {
            "kind": "event_envelope",
            "version": "0.1.0",
            "event_id": f"event.local.{self._cursor_sequence}",
            "event_type": event_type,
            "aggregate_ref": aggregate_ref,
            "sequence": self._cursor_sequence,
            "occurred_at": now,
            "actor_ref": "vcp:artifact:principal:local-runtime",
            "payload_ref": payload_ref,
            "previous_digest": previous,
            "source_ref": "vcp:artifact:source:local-reference-runtime",
            "recorded_at": now,
            "causal_parent_ref": None,
            "payload_digest": canonical_digest({"payload_ref": payload_ref}),
            "redacted_summary": summary,
            "sensitivity": "internal",
            "evidence_refs": list(evidence_refs),
            "audit_refs": [],
            "state_transition_version": "0.1.0",
        }
        event = EventEnvelope.model_validate({**payload, "digest": canonical_digest(payload)})
        self._events.append(event)
        self._events = self._events[-self._event_retention :]
        self._artifacts[event.ref] = event
        return event

    def set_availability(self, capability_id: str, state: AffordanceState) -> EventEnvelope:
        """Change reference-host availability and invalidate dependent projections."""

        if capability_id not in self._availability:
            raise ValueError(f"unknown capability: {capability_id}")
        self._availability[capability_id] = state
        self._cache.invalidate_dependency(self._catalog_digest)
        descriptor = next(item for item in self._descriptors if item.capability_id == capability_id)
        return self._emit_event(
            event_type="capability.availability.changed",
            aggregate_ref=descriptor.ref,
            payload_ref=descriptor.ref,
            summary=f"Capability availability changed to {state.value}",
        )

    @property
    def capability_catalog_digest(self) -> str:
        return self._catalog_digest

    def _meta(self, *, correlation: str, dependency: str, cursor: str | None) -> ResultMeta:
        return ResultMeta(
            profile=self._profile_id,
            schema_digest=self._schema_digest,
            correlation_id=correlation,
            as_of=_timestamp(self._clock()),
            cursor=cursor,
            dependency_digest=dependency,
        )

    @staticmethod
    def _ready_assurance(*axes: AssuranceAxis) -> AssuranceReport:
        return AssuranceReport(
            overall=AssuranceOverall.READY,
            checks=tuple(
                AssuranceCheck(
                    axis=axis,
                    status=AssuranceStatus.PASSED,
                    summary=f"{axis.value} requirements passed for the local observe projection",
                )
                for axis in axes
            ),
        )

    @staticmethod
    def _bootstrap_assurance() -> AssuranceReport:
        checks = [
            AssuranceCheck(
                axis=axis,
                status=AssuranceStatus.PASSED,
                summary=f"{axis.value} requirements passed for the local observe projection",
            )
            for axis in (
                AssuranceAxis.SYNTAX,
                AssuranceAxis.INTEGRITY,
                AssuranceAxis.FRESHNESS,
                AssuranceAxis.SCOPE,
                AssuranceAxis.APPLICABILITY,
            )
        ]
        checks.extend(
            (
                AssuranceCheck(
                    axis=AssuranceAxis.AUTHENTICITY,
                    status=AssuranceStatus.UNKNOWN,
                    summary=(
                        "Local structure and digest verification does not authenticate an issuer"
                    ),
                ),
                AssuranceCheck(
                    axis=AssuranceAxis.TRUST,
                    status=AssuranceStatus.UNKNOWN,
                    summary="Local integrity evidence does not establish current trust",
                ),
            )
        )
        return AssuranceReport(overall=AssuranceOverall.READY, checks=tuple(checks))

    def _base_affordance(
        self,
        descriptor: CapabilityDescriptor,
        situation: SituationView,
    ) -> Affordance:
        state = self._availability[descriptor.capability_id]
        suffix = situation.dependency_digest.removeprefix("sha256:")[:12]
        affordance_id = f"affordance.{descriptor.capability_id}.{suffix}"
        prerequisites = descriptor.preconditions
        safe_next: tuple[SafeTransition, ...] = ()
        if state != AffordanceState.AVAILABLE:
            safe_next = (
                SafeTransition(
                    operation="refresh",
                    summary=(
                        "Refresh the situation and capability state before relying on this option"
                    ),
                    target_ref=situation.ref,
                ),
            )
        external_calls = 0
        forecast = ResourceMeasurement(
            wall_time_ms=2 if descriptor.effect_class == EffectClass.PURE_LOCAL else 10,
            tokens=0,
            external_calls=external_calls,
            money_minor=0,
            human_interruptions=0,
            confidence=0.8,
            local_compute_ms=2,
            bytes=512,
            risk_units=(
                1
                if descriptor.effect_class not in {EffectClass.PURE_LOCAL, EffectClass.STATE_READ}
                else 0
            ),
        )
        return Affordance(
            affordance_id=affordance_id,
            capability_ref=descriptor.ref,
            situation_digest=situation.digest,
            state=state,
            summary=descriptor.summary,
            effect_class=descriptor.effect_class,
            authority_class=descriptor.authority_class,
            prerequisites=prerequisites,
            cost=forecast,
            evidence_outputs=descriptor.outputs,
            recovery=("refresh situation",) if state != AffordanceState.AVAILABLE else (),
            safe_next=safe_next,
            descriptor_digest=descriptor.digest,
        )

    async def bootstrap(
        self,
        goal: Goal,
        budget: ResourceBudget,
    ) -> AgentResult[SituationView]:
        now = _timestamp(self._clock())
        dependency = canonical_digest(
            {
                "goal": goal.statement,
                "principal_ref": "vcp:artifact:principal:local-observer",
                "catalog_digest": self._catalog_digest,
                "normative_context": self._normative_context.digest,
                "claims": [claim.model_dump(mode="json") for claim in self._claims],
                "availability": {
                    key: value.value for key, value in sorted(self._availability.items())
                },
                "budget": budget.model_dump(mode="json"),
            }
        )
        cache_key = CacheKey(
            namespace="bootstrap",
            request_digest=canonical_digest(goal.model_dump(mode="json")),
            dependency_digests=(dependency, self._schema_digest, self._catalog_digest),
        )
        cached = self._cache.get(cache_key)
        if cached is not None:
            return AgentResult[SituationView].model_validate(cached.model_dump(mode="json"))

        suffix = dependency.removeprefix("sha256:")[:16]
        situation_id = f"situation.local.{suffix}"
        affordance_refs = tuple(
            f"vcp:artifact:affordance:affordance.{descriptor.capability_id}.{suffix[:12]}"
            for descriptor in self._descriptors
        )
        payload: dict[str, Any] = {
            "kind": "situation_view",
            "version": "0.1.0",
            "situation_id": situation_id,
            "goal": goal.statement,
            "principal_ref": "vcp:artifact:principal:local-observer",
            "known_claim_refs": [f"vcp:artifact:claim:{claim.claim_id}" for claim in self._claims],
            "unknowns": [
                "host policy state",
                "external runtime state",
                "deployment state",
            ],
            "conflict_refs": list(self._normative_context.conflict_refs),
            "normative_context_ref": self._normative_context.ref,
            "authority_refs": ["vcp:artifact:authority:local-read"],
            "budget": budget.model_dump(mode="json"),
            "active_work_refs": [],
            "control_operations": [],
            "affordance_refs": list(affordance_refs),
            "omissions": [
                {
                    "field": "host authority and external state",
                    "reason": "unavailable",
                    "expand_ref": None,
                }
            ],
            "as_of": now,
            "cursor": self._cursor(),
            "dependency_digest": dependency,
        }
        situation = SituationView.model_validate({**payload, "digest": canonical_digest(payload)})
        self._artifacts[situation.ref] = situation
        for claim in self._claims:
            self._artifacts[f"vcp:artifact:claim:{claim.claim_id}"] = claim
        for descriptor in self._descriptors:
            affordance = self._base_affordance(descriptor, situation)
            self._artifacts[affordance.ref] = affordance

        result: AgentResult[SituationView] = AgentResult(
            meta=self._meta(
                correlation=f"bootstrap.local.{suffix}",
                dependency=dependency,
                cursor=situation.cursor,
            ),
            status=ResultStatus.READY,
            value=situation,
            assurance=self._bootstrap_assurance(),
            evidence_refs=situation.known_claim_refs,
            resources=ResourceReport(
                forecast=ResourceMeasurement(
                    wall_time_ms=20,
                    tokens=0,
                    external_calls=0,
                    money_minor=0,
                    human_interruptions=0,
                    confidence=0.8,
                )
            ),
            omissions=situation.omissions,
        )
        self._cache.put(cache_key, result)
        return result

    async def watch(self, situation: SituationView) -> AgentResult[CursorDelta]:
        """Return a bounded cursor delta or an explicit safe resynchronization state."""

        try:
            prefix, sequence_text = situation.cursor.rsplit(".", 1)
            if prefix != "cursor.local":
                raise ValueError
            prior_sequence = int(sequence_text)
        except ValueError:
            prior_sequence = -1

        oldest_sequence = self._events[0].sequence if self._events else self._cursor_sequence
        gap = (
            prior_sequence < 0
            or prior_sequence > self._cursor_sequence
            or (self._events and prior_sequence < oldest_sequence - 1)
        )
        current_cursor = self._cursor()
        if gap:
            transition = SafeTransition(
                operation="bootstrap",
                summary="Rebuild a bounded SituationView from current authorities",
            )
            payload = {
                "kind": "cursor_delta",
                "version": "0.1.0",
                "prior_cursor": situation.cursor,
                "cursor": current_cursor,
                "changed_refs": [],
                "invalidated_refs": list(situation.affordance_refs),
                "events": [],
                "situation": None,
                "resync_required": True,
                "safe_next": [transition.model_dump(mode="json")],
            }
            delta = CursorDelta.model_validate({**payload, "digest": canonical_digest(payload)})
            return AgentResult(
                meta=self._meta(
                    correlation=f"watch.local.gap.{self._cursor_sequence}",
                    dependency=situation.dependency_digest,
                    cursor=current_cursor,
                ),
                status=ResultStatus.STALE,
                value=delta,
                assurance=AssuranceReport(
                    overall=AssuranceOverall.BLOCKED,
                    checks=(
                        AssuranceCheck(
                            axis=AssuranceAxis.FRESHNESS,
                            status=AssuranceStatus.STALE,
                            summary="The requested cursor is outside the retained event window",
                        ),
                    ),
                ),
                safe_next=(transition,),
            )

        refreshed = await self.bootstrap(
            Goal(statement=situation.goal),
            situation.budget,
        )
        fresh = refreshed.require_value()
        events = tuple(event for event in self._events if event.sequence > prior_sequence)
        changed_refs = tuple(event.aggregate_ref for event in events)
        invalidated_refs = tuple(sorted(set(situation.affordance_refs)) if events else ())
        delta_payload: dict[str, Any] = {
            "kind": "cursor_delta",
            "version": "0.1.0",
            "prior_cursor": situation.cursor,
            "cursor": current_cursor,
            "changed_refs": list(changed_refs),
            "invalidated_refs": list(invalidated_refs),
            "events": [event.model_dump(mode="json") for event in events],
            "situation": fresh.model_dump(mode="json"),
            "resync_required": False,
            "safe_next": [],
        }
        delta = CursorDelta.model_validate(
            {**delta_payload, "digest": canonical_digest(delta_payload)}
        )
        return AgentResult(
            meta=self._meta(
                correlation=f"watch.local.{self._cursor_sequence}",
                dependency=fresh.dependency_digest,
                cursor=current_cursor,
            ),
            status=ResultStatus.READY,
            value=delta,
            assurance=self._ready_assurance(
                AssuranceAxis.INTEGRITY,
                AssuranceAxis.FRESHNESS,
                AssuranceAxis.SCOPE,
            ),
            evidence_refs=tuple(event.ref for event in events),
        )

    async def find_affordances(
        self,
        situation: SituationView,
        query: AffordanceQuery,
    ) -> AgentResult[tuple[Affordance, ...]]:
        request_digest = canonical_digest(query.model_dump(mode="json"))
        key = CacheKey(
            namespace="find-affordances",
            request_digest=request_digest,
            dependency_digests=(
                situation.digest,
                situation.dependency_digest,
                self._catalog_digest,
                self._schema_digest,
            ),
        )
        cached = self._cache.get(key)
        if cached is not None:
            return AgentResult[tuple[Affordance, ...]].model_validate(
                cached.model_dump(mode="json")
            )

        terms = set(
            " ".join(item for item in (query.evidence_for, query.outcome) if item)
            .lower()
            .replace("-", " ")
            .split()
        )
        candidates: list[tuple[int, Affordance]] = []
        for descriptor in self._descriptors:
            affordance = self._base_affordance(descriptor, situation)
            if _EFFECT_ORDER[descriptor.effect_class] > _EFFECT_ORDER[query.effect_ceiling]:
                affordance = affordance.model_copy(
                    update={
                        "state": AffordanceState.UNAVAILABLE,
                        "prerequisites": affordance.prerequisites
                        + (f"raise effect ceiling to {descriptor.effect_class.value}",),
                        "safe_next": (),
                    }
                )
            if not query.include_unavailable and affordance.state == AffordanceState.UNAVAILABLE:
                continue
            haystack = " ".join(
                (descriptor.capability_id, descriptor.summary, *descriptor.outputs)
            ).lower()
            score = sum(1 for term in terms if term in haystack)
            if terms and score == 0:
                continue
            candidates.append((score, affordance))

        candidates.sort(
            key=lambda item: (
                _STATE_ORDER[item[1].state],
                -item[0],
                item[1].cost.external_calls,
                item[1].cost.wall_time_ms,
                item[1].affordance_id,
            )
        )
        values = tuple(item[1] for item in candidates[: query.limit])
        status = ResultStatus.READY if values else ResultStatus.DEGRADED
        warnings = (
            () if values else ("No affordance matched the requested outcome and effect ceiling",)
        )
        result: AgentResult[tuple[Affordance, ...]] = AgentResult(
            meta=self._meta(
                correlation=f"affordances.local.{request_digest[-12:]}",
                dependency=canonical_digest(
                    {
                        "situation": situation.digest,
                        "query": query.model_dump(mode="json"),
                        "catalog": self._catalog_digest,
                    }
                ),
                cursor=situation.cursor,
            ),
            status=status,
            value=values,
            assurance=self._ready_assurance(
                AssuranceAxis.SYNTAX,
                AssuranceAxis.FRESHNESS,
                AssuranceAxis.APPLICABILITY,
                AssuranceAxis.AUTHORITY,
            ),
            evidence_refs=situation.known_claim_refs,
            resources=ResourceReport(
                forecast=ResourceMeasurement(
                    wall_time_ms=5,
                    tokens=0,
                    external_calls=0,
                    money_minor=0,
                    human_interruptions=0,
                    confidence=0.9,
                )
            ),
            warnings=warnings,
            omissions=situation.omissions,
        )
        self._cache.put(key, result)
        return result

    async def expand(self, ref: str) -> AgentResult[Contract]:
        artifact = self._artifacts.get(ref)
        dependency = canonical_digest(
            {"ref": ref, "catalog": self._catalog_digest, "schema": self._schema_digest}
        )
        if artifact is None:
            transition = SafeTransition(
                operation="bootstrap",
                summary="Refresh the SituationView and use one of its declared references",
            )
            failure = FailureFrame(
                code="artifact.unavailable",
                category="evidence",
                summary="The requested artifact is outside this bounded local projection",
                retry=RetryDisposition.AFTER_REFRESH,
                safe_next=(transition,),
            )
            return AgentResult(
                meta=self._meta(
                    correlation=f"expand.local.{dependency[-12:]}",
                    dependency=dependency,
                    cursor=None,
                ),
                status=ResultStatus.UNAVAILABLE,
                value=None,
                assurance=AssuranceReport(
                    overall=AssuranceOverall.BLOCKED,
                    checks=(
                        AssuranceCheck(
                            axis=AssuranceAxis.SCOPE,
                            status=AssuranceStatus.UNAVAILABLE,
                            summary="Requested reference is absent from the bounded projection",
                        ),
                    ),
                ),
                safe_next=(transition,),
                failure=failure,
            )
        return AgentResult(
            meta=self._meta(
                correlation=f"expand.local.{dependency[-12:]}",
                dependency=dependency,
                cursor=None,
            ),
            status=ResultStatus.READY,
            value=artifact,
            assurance=self._ready_assurance(
                AssuranceAxis.SYNTAX,
                AssuranceAxis.INTEGRITY,
                AssuranceAxis.SCOPE,
            ),
            evidence_refs=(ref,),
        )

    (NormativeClause,)
    (NormativeContext,)
