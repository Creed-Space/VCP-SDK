"""Portable contracts for the VCP Agent Runtime Profile observe slice."""

from __future__ import annotations

import re
from enum import Enum
from typing import Annotated, Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field, model_validator

Digest = Annotated[str, Field(pattern=r"^sha256:[a-f0-9]{64}$")]
ArtifactRef = Annotated[
    str,
    Field(
        pattern=(
            r"^vcp:artifact:[a-z][a-z0-9-]{0,63}:"
            r"[A-Za-z0-9._~:/?#@!$&()*+,;=%-]{1,1024}$"
        )
    ),
]


class Contract(BaseModel):
    """Closed, immutable base for authority-sensitive portable contracts."""

    model_config = ConfigDict(extra="forbid", frozen=True, arbitrary_types_allowed=True)


class AssuranceStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    UNKNOWN = "unknown"
    UNAVAILABLE = "unavailable"
    STALE = "stale"
    CONFLICTING = "conflicting"
    WITHHELD = "withheld"
    NOT_APPLICABLE = "not_applicable"


class AssuranceAxis(str, Enum):
    SYNTAX = "syntax"
    INTEGRITY = "integrity"
    AUTHENTICITY = "authenticity"
    TRUST = "trust"
    FRESHNESS = "freshness"
    SCOPE = "scope"
    SEMANTICS = "semantics"
    APPLICABILITY = "applicability"
    POLICY = "policy"
    AUTHORITY = "authority"
    EXECUTION = "execution"
    POSTCONDITION = "postcondition"
    COMPLETION = "completion"


class AssuranceOverall(str, Enum):
    READY = "ready"
    DEGRADED = "degraded"
    BLOCKED = "blocked"
    INDETERMINATE = "indeterminate"


class ResultStatus(str, Enum):
    READY = "ready"
    DEGRADED = "degraded"
    AWAITING_REVIEW = "awaiting_review"
    BLOCKED = "blocked"
    UNAVAILABLE = "unavailable"
    STALE = "stale"
    CONFLICTING = "conflicting"
    BUDGET_EXHAUSTED = "budget_exhausted"
    INDETERMINATE = "indeterminate"
    FAILED = "failed"


class EffectClass(str, Enum):
    PURE_LOCAL = "pure_local"
    STATE_READ = "state_read"
    SENSITIVE_EGRESS = "sensitive_egress"
    REVERSIBLE_WRITE = "reversible_write"
    COMMUNICATION = "communication"
    FINANCIAL = "financial"
    LEGAL = "legal"
    PHYSICAL = "physical"


class AffordanceState(str, Enum):
    AVAILABLE = "available"
    CONDITIONAL = "conditional"
    UNAVAILABLE = "unavailable"
    STALE = "stale"


class RetryDisposition(str, Enum):
    NEVER = "never"
    SAFE = "safe"
    AFTER_REFRESH = "after_refresh"
    AFTER_RECONCILE = "after_reconcile"
    AFTER_REVIEW = "after_review"


class Goal(Contract):
    """A bounded natural-language objective for situation compilation."""

    statement: Annotated[str, Field(min_length=1, max_length=8192)]

    def __str__(self) -> str:
        return self.statement


class Profile(Contract):
    """An exact Agent Runtime Profile selection."""

    name: str
    version: str = "0.1.0"

    @classmethod
    def observe(cls) -> Profile:
        return cls(name="observe")

    @property
    def identifier(self) -> str:
        return f"{self.name}@{self.version}"

    @model_validator(mode="after")
    def validate_supported_candidate(self) -> Profile:
        if self.name not in {"observe", "controlled", "accretive"}:
            raise ValueError("unknown Agent Runtime Profile name")
        if self.version != "0.1.0":
            raise ValueError("unsupported Agent Runtime Profile candidate version")
        return self


_PROFILE_ID_RE = re.compile(r"^(observe|controlled|accretive)@0\.1\.0$")


class ProfileOffer(Contract):
    """Required and optional exact Agent Runtime Profile versions."""

    kind: str = "agent_runtime_profile_offer"
    version: str = "0.1.0"
    required: tuple[str, ...]
    optional: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_profiles(self) -> ProfileOffer:
        combined = self.required + self.optional
        if len(combined) != len(set(combined)):
            raise ValueError("required and optional profile offers must be unique")
        if len(self.required) > 3 or len(self.optional) > 3:
            raise ValueError("at most three required and three optional profiles are allowed")
        if any(_PROFILE_ID_RE.fullmatch(item) is None for item in combined):
            raise ValueError("profile offers must use an exact supported candidate version")
        return self


class ProfileAcknowledgement(Contract):
    """Bound acknowledgement of exact selected and unsupported profiles."""

    kind: str = "agent_runtime_profile_ack"
    version: str = "0.1.0"
    selected: tuple[str, ...]
    unsupported_optional: tuple[str, ...] = ()
    bootstrap_ref: str
    capability_catalog_digest: Digest
    principal_session_ref: ArtifactRef
    event_binding: str
    expires_at: str


class ResultMeta(Contract):
    profile: str = "observe@0.1.0"
    schema_version: str = "0.1.0"
    schema_digest: Digest
    correlation_id: Annotated[str, Field(min_length=1, max_length=256)]
    as_of: Annotated[str, Field(min_length=1, max_length=64)]
    cursor: Annotated[str, Field(min_length=1, max_length=512)] | None = None
    dependency_digest: Digest


class AssuranceCheck(Contract):
    axis: AssuranceAxis
    status: AssuranceStatus
    summary: Annotated[str, Field(min_length=1, max_length=2048)]
    evidence_refs: tuple[str, ...] = ()


class AssuranceReport(Contract):
    overall: AssuranceOverall
    checks: Annotated[tuple[AssuranceCheck, ...], Field(min_length=1, max_length=64)]

    def status_for(self, axis: AssuranceAxis) -> AssuranceStatus | None:
        return next((check.status for check in self.checks if check.axis == axis), None)


class ResourceBudget(Contract):
    wall_time_ms: int | None = Field(default=None, ge=0, le=86_400_000)
    tokens: int | None = Field(default=None, ge=0, le=1_000_000_000)
    external_calls: int | None = Field(default=None, ge=0, le=1_000_000)
    money_minor: int | None = Field(default=None, ge=0, le=1_000_000_000_000)
    human_interruptions: int | None = Field(default=None, ge=0, le=1_000_000)
    reserve_fraction: float = Field(default=0.2, ge=0, le=1)

    @classmethod
    def observe_default(cls) -> ResourceBudget:
        return cls(
            wall_time_ms=2_000,
            tokens=4_000,
            external_calls=0,
            money_minor=0,
            human_interruptions=0,
            reserve_fraction=0.2,
        )


class ResourceMeasurement(Contract):
    wall_time_ms: int = Field(ge=0)
    tokens: int = Field(ge=0)
    external_calls: int = Field(ge=0)
    money_minor: int = Field(ge=0)
    human_interruptions: int = Field(ge=0)
    confidence: float = Field(ge=0, le=1)


class ResourceReport(Contract):
    forecast: ResourceMeasurement | None = None
    actual: ResourceMeasurement | None = None


class SafeTransition(Contract):
    operation: Annotated[str, Field(min_length=1, max_length=256)]
    summary: Annotated[str, Field(min_length=1, max_length=1024)]
    target_ref: ArtifactRef | None = None
    requires_review: bool = False


class Omission(Contract):
    field: Annotated[str, Field(min_length=1, max_length=512)]
    reason: str
    expand_ref: ArtifactRef | None = None


class FailureFrame(Contract):
    code: Annotated[str, Field(min_length=1, max_length=256)]
    category: str
    summary: Annotated[str, Field(min_length=1, max_length=4096)]
    retry: RetryDisposition
    reconcile_ref: ArtifactRef | None = None
    safe_next: tuple[SafeTransition, ...] = ()
    evidence_refs: tuple[str, ...] = ()


class ExpectedStateError(RuntimeError):
    """Raised only when a caller explicitly selects exception-style handling."""

    def __init__(self, status: ResultStatus, failure: FailureFrame | None) -> None:
        self.status = status
        self.failure = failure
        summary = failure.summary if failure is not None else "result has no value"
        super().__init__(f"{status.value}: {summary}")


T = TypeVar("T")


class AgentResult(Contract, Generic[T]):
    """One result grammar for expected operational states."""

    kind: str = "agent_result"
    version: str = "0.1.0"
    meta: ResultMeta
    status: ResultStatus
    value: T | None
    assurance: AssuranceReport
    evidence_refs: tuple[str, ...] = ()
    resources: ResourceReport = ResourceReport()
    safe_next: tuple[SafeTransition, ...] = ()
    warnings: tuple[str, ...] = ()
    omissions: tuple[Omission, ...] = ()
    failure: FailureFrame | None = None

    @model_validator(mode="after")
    def validate_state_shape(self) -> AgentResult[T]:
        if self.status in {ResultStatus.READY, ResultStatus.DEGRADED} and self.value is None:
            raise ValueError("ready and degraded AgentResult values must be present")
        if self.status == ResultStatus.READY and self.failure is not None:
            raise ValueError("ready AgentResult cannot contain a FailureFrame")
        return self

    def is_ready(self) -> bool:
        return self.status == ResultStatus.READY

    def require_value(self) -> T:
        if self.value is None:
            raise ExpectedStateError(self.status, self.failure)
        return self.value

    def can_retry(self) -> bool:
        return self.failure is not None and self.failure.retry != RetryDisposition.NEVER

    def explain(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "assurance": {
                check.axis.value: check.status.value for check in self.assurance.checks
            },
            "evidence_refs": list(self.evidence_refs),
            "warnings": list(self.warnings),
            "omissions": [item.model_dump(mode="json") for item in self.omissions],
            "safe_next": [item.model_dump(mode="json") for item in self.safe_next],
            "failure": self.failure.model_dump(mode="json") if self.failure else None,
        }


class EvidenceClaim(Contract):
    kind: str = "evidence_claim"
    version: str = "0.1.0"
    claim_id: Annotated[str, Field(min_length=1, max_length=256)]
    subject: Annotated[str, Field(min_length=1, max_length=2048)]
    predicate: Annotated[str, Field(min_length=1, max_length=256)]
    object: Any
    basis: str
    source_ref: ArtifactRef
    observed_at: Annotated[str, Field(min_length=1, max_length=64)]
    fresh_until: Annotated[str, Field(min_length=1, max_length=64)] | None = None
    confidence: float = Field(ge=0, le=1)
    authority_class: Annotated[str, Field(min_length=1, max_length=128)]
    scope: tuple[str, ...] = ()
    privacy_class: str = "internal"


class CapabilityDescriptor(Contract):
    kind: str = "capability_descriptor"
    version: str = "0.1.0"
    capability_id: Annotated[str, Field(min_length=1, max_length=256)]
    revision: Annotated[str, Field(min_length=1, max_length=128)]
    summary: Annotated[str, Field(min_length=1, max_length=2048)]
    effect_class: EffectClass
    authority_class: Annotated[str, Field(min_length=1, max_length=128)]
    inputs: tuple[str, ...] = ()
    outputs: tuple[str, ...] = ()
    preconditions: tuple[str, ...] = ()
    postconditions: tuple[str, ...] = ()
    privacy_classes: tuple[str, ...] = ()
    reversible: bool = False
    reconciliation: str = "none"
    digest: Digest

    @property
    def ref(self) -> ArtifactRef:
        return f"vcp:artifact:capability:{self.capability_id}"


class Affordance(Contract):
    kind: str = "affordance"
    version: str = "0.1.0"
    affordance_id: Annotated[str, Field(min_length=1, max_length=256)]
    capability_ref: ArtifactRef
    situation_digest: Digest
    state: AffordanceState
    summary: Annotated[str, Field(min_length=1, max_length=2048)]
    effect_class: EffectClass
    authority_class: Annotated[str, Field(min_length=1, max_length=128)]
    prerequisites: tuple[str, ...] = ()
    cost: ResourceMeasurement
    evidence_outputs: tuple[str, ...] = ()
    recovery: tuple[str, ...] = ()
    safe_next: tuple[SafeTransition, ...] = ()
    descriptor_digest: Digest

    @property
    def ref(self) -> ArtifactRef:
        return f"vcp:artifact:affordance:{self.affordance_id}"


class SituationView(Contract):
    kind: str = "situation_view"
    version: str = "0.1.0"
    situation_id: Annotated[str, Field(min_length=1, max_length=256)]
    goal: Annotated[str, Field(min_length=1, max_length=8192)]
    principal_ref: ArtifactRef
    known_claim_refs: tuple[str, ...] = ()
    unknowns: tuple[str, ...] = ()
    conflict_refs: tuple[str, ...] = ()
    normative_context_ref: ArtifactRef
    authority_refs: tuple[str, ...] = ()
    budget: ResourceBudget
    active_work_refs: tuple[str, ...] = ()
    control_operations: tuple[str, ...] = ()
    affordance_refs: tuple[str, ...] = ()
    omissions: tuple[Omission, ...] = ()
    as_of: Annotated[str, Field(min_length=1, max_length=64)]
    cursor: Annotated[str, Field(min_length=1, max_length=512)]
    dependency_digest: Digest
    digest: Digest

    @property
    def ref(self) -> ArtifactRef:
        return f"vcp:artifact:situation:{self.situation_id}"


class AffordanceQuery(Contract):
    evidence_for: str | None = None
    outcome: str | None = None
    effect_ceiling: EffectClass = EffectClass.STATE_READ
    include_unavailable: bool = True
    limit: int = Field(default=10, ge=1, le=100)
