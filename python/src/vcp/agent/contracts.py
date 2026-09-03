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


class RunStatus(str, Enum):
    DRAFT = "draft"
    PREFLIGHTED = "preflighted"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    AWAITING_REVIEW = "awaiting_review"
    BLOCKED = "blocked"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"
    INDETERMINATE = "indeterminate"


class DecisionKind(str, Enum):
    ALLOW = "allow"
    MODIFY = "modify"
    REQUIRE_HUMAN = "require_human"
    DENY = "deny"
    ABSTAIN = "abstain"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


class EffectStatus(str, Enum):
    NONE = "none"
    ACCEPTED = "accepted"
    OBSERVED = "observed"
    FAILED = "failed"
    POSSIBLE = "possible"
    INDETERMINATE = "indeterminate"
    COMPENSATED = "compensated"


class ControlOperation(str, Enum):
    PAUSE = "pause"
    RESUME = "resume"
    CANCEL = "cancel"
    HALT = "halt"
    COMPENSATE = "compensate"
    OBJECT = "object"
    ESCALATE = "escalate"
    WITHDRAW_CONSENT = "withdraw_consent"
    REQUEST_CLARIFICATION = "request_clarification"
    REQUEST_RESOURCES = "request_resources"


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

    @classmethod
    def controlled(cls) -> Profile:
        return cls(name="controlled")

    @classmethod
    def accretive(cls) -> Profile:
        return cls(name="accretive")

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
    model_calls: int | None = Field(default=None, ge=0, le=1_000_000)
    local_compute_ms: int | None = Field(default=None, ge=0, le=86_400_000)
    bytes: int | None = Field(default=None, ge=0, le=1_000_000_000_000)
    sensitive_egress_bytes: int | None = Field(default=None, ge=0, le=1_000_000_000_000)
    privacy_units: int | None = Field(default=None, ge=0, le=1_000_000_000)
    risk_units: int | None = Field(default=None, ge=0, le=1_000_000_000)
    welfare_load_units: int | None = Field(default=None, ge=0, le=1_000_000_000)

    @classmethod
    def observe_default(cls) -> ResourceBudget:
        return cls(
            wall_time_ms=2_000,
            tokens=4_000,
            external_calls=0,
            money_minor=0,
            human_interruptions=0,
            reserve_fraction=0.2,
            model_calls=0,
            local_compute_ms=500,
            bytes=65_536,
            sensitive_egress_bytes=0,
            privacy_units=0,
            risk_units=0,
            welfare_load_units=0,
        )

    @classmethod
    def controlled_default(cls) -> ResourceBudget:
        return cls(
            wall_time_ms=5_000,
            tokens=8_000,
            external_calls=0,
            money_minor=0,
            human_interruptions=1,
            reserve_fraction=0.25,
            model_calls=0,
            local_compute_ms=2_000,
            bytes=262_144,
            sensitive_egress_bytes=0,
            privacy_units=0,
            risk_units=10,
            welfare_load_units=0,
        )


class ResourceMeasurement(Contract):
    wall_time_ms: int = Field(ge=0)
    tokens: int = Field(ge=0)
    external_calls: int = Field(ge=0)
    money_minor: int = Field(ge=0)
    human_interruptions: int = Field(ge=0)
    confidence: float = Field(ge=0, le=1)
    model_calls: int = Field(default=0, ge=0)
    local_compute_ms: int = Field(default=0, ge=0)
    bytes: int = Field(default=0, ge=0)
    sensitive_egress_bytes: int = Field(default=0, ge=0)
    privacy_units: int = Field(default=0, ge=0)
    risk_units: int = Field(default=0, ge=0)
    welfare_load_units: int = Field(default=0, ge=0)


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
            "assurance": {check.axis.value: check.status.value for check in self.assurance.checks},
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


class NormativeClause(Contract):
    clause_id: Annotated[str, Field(min_length=1, max_length=256)]
    source_ref: ArtifactRef
    author_ref: ArtifactRef
    represented_constituency: Annotated[str, Field(min_length=1, max_length=2048)]
    clause_kind: str
    hardness: str
    priority: int = Field(ge=0, le=1_000_000)
    effect: str
    statement: Annotated[str, Field(min_length=1, max_length=16_384)]
    scope: tuple[str, ...] = ()
    semantic_ref: ArtifactRef | None = None
    semantic_digest: Digest | None = None


class NormativeContext(Contract):
    kind: str = "normative_context"
    version: str = "0.1.0"
    clauses: tuple[NormativeClause, ...] = ()
    conflict_refs: tuple[str, ...] = ()
    omissions: tuple[Omission, ...] = ()
    digest: Digest
    resolution_rule: str | None = None
    selected_clause_refs: tuple[str, ...] = ()

    @property
    def ref(self) -> ArtifactRef:
        return f"vcp:artifact:normative:{self.digest.removeprefix('sha256:')[:24]}"


class CursorDelta(Contract):
    kind: str = "cursor_delta"
    version: str = "0.1.0"
    prior_cursor: Annotated[str, Field(min_length=1, max_length=512)]
    cursor: Annotated[str, Field(min_length=1, max_length=512)]
    changed_refs: tuple[str, ...] = ()
    invalidated_refs: tuple[str, ...] = ()
    events: tuple[EventEnvelope, ...] = ()
    situation: SituationView | None = None
    resync_required: bool = False
    safe_next: tuple[SafeTransition, ...] = ()
    digest: Digest

    @model_validator(mode="after")
    def validate_refresh_shape(self) -> CursorDelta:
        if self.resync_required and not self.safe_next:
            raise ValueError("cursor gaps require a safe resynchronization transition")
        if not self.resync_required and self.situation is None:
            raise ValueError("ordinary cursor deltas require a fresh SituationView")
        return self


class ProofPredicate(Contract):
    predicate_id: Annotated[str, Field(min_length=1, max_length=256)]
    statement: Annotated[str, Field(min_length=1, max_length=4096)]
    authority_class: Annotated[str, Field(min_length=1, max_length=128)]
    mandatory: bool
    evidence_requirements: tuple[str, ...] = ()

    @property
    def ref(self) -> ArtifactRef:
        return f"vcp:artifact:predicate:{self.predicate_id}"


class ProofPlan(Contract):
    kind: str = "proof_plan"
    version: str = "0.1.0"
    proof_plan_id: Annotated[str, Field(min_length=1, max_length=256)]
    predicates: Annotated[tuple[ProofPredicate, ...], Field(min_length=1)]
    budget: ResourceBudget
    digest: Digest

    @property
    def ref(self) -> ArtifactRef:
        return f"vcp:artifact:proof-plan:{self.proof_plan_id}"


class RunSpec(Contract):
    kind: str = "run_spec"
    version: str = "0.1.0"
    run_id: Annotated[str, Field(min_length=1, max_length=256)]
    goal: Annotated[str, Field(min_length=1, max_length=8192)]
    situation_ref: ArtifactRef
    proof_plan_ref: ArtifactRef
    budget: ResourceBudget
    risk_ceiling: EffectClass
    status: RunStatus
    digest: Digest

    @property
    def ref(self) -> ArtifactRef:
        return f"vcp:artifact:run:{self.run_id}"


class PlanStep(Contract):
    kind: str = "plan_step"
    version: str = "0.1.0"
    step_id: Annotated[str, Field(min_length=1, max_length=256)]
    run_ref: ArtifactRef
    affordance_ref: ArtifactRef
    depends_on: tuple[str, ...] = ()
    proof_predicate_refs: tuple[str, ...] = ()
    digest: Digest

    @property
    def ref(self) -> ArtifactRef:
        return f"vcp:artifact:step:{self.step_id}"


class ActionIntent(Contract):
    kind: str = "action_intent"
    version: str = "0.1.0"
    intent_id: Annotated[str, Field(min_length=1, max_length=256)]
    run_ref: ArtifactRef
    step_ref: ArtifactRef
    affordance_ref: ArtifactRef
    arguments_digest: Digest
    destination: Annotated[str, Field(min_length=1, max_length=2048)]
    context_digest: Digest
    policy_digest: Digest
    descriptor_digest: Digest
    requested_at: Annotated[str, Field(min_length=1, max_length=64)]
    digest: Digest
    schema_digest: Digest
    effect_class: EffectClass
    situation_digest: Digest
    expected_postconditions: tuple[str, ...]
    resource_ceiling: ResourceBudget
    idempotency_scope: Annotated[str, Field(min_length=1, max_length=512)]
    requested_authority: Annotated[str, Field(min_length=1, max_length=128)]

    @property
    def ref(self) -> ArtifactRef:
        return f"vcp:artifact:intent:{self.intent_id}"


class DecisionReceipt(Contract):
    kind: str = "decision_receipt"
    version: str = "0.1.0"
    decision_id: Annotated[str, Field(min_length=1, max_length=256)]
    intent_ref: ArtifactRef
    decision: DecisionKind
    reason_codes: tuple[str, ...] = ()
    policy_digest: Digest
    decided_at: Annotated[str, Field(min_length=1, max_length=64)]
    expires_at: Annotated[str, Field(min_length=1, max_length=64)] | None = None
    digest: Digest
    reviewer_ref: ArtifactRef | None = None

    @property
    def ref(self) -> ArtifactRef:
        return f"vcp:artifact:decision:{self.decision_id}"


class AuthorityGrantRef(Contract):
    kind: str = "authority_grant_ref"
    version: str = "0.1.0"
    grant_ref: ArtifactRef
    decision_ref: ArtifactRef
    intent_digest: Digest
    single_use: bool
    expires_at: Annotated[str, Field(min_length=1, max_length=64)]
    actor_ref: ArtifactRef
    tenant_ref: ArtifactRef
    run_ref: ArtifactRef
    step_ref: ArtifactRef
    capability_ref: ArtifactRef
    arguments_digest: Digest
    destination: Annotated[str, Field(min_length=1, max_length=2048)]
    effect_class: EffectClass
    resource_ceiling: ResourceBudget
    nonce_digest: Digest


class ExecutionAttempt(Contract):
    kind: str = "execution_attempt"
    version: str = "0.1.0"
    attempt_id: Annotated[str, Field(min_length=1, max_length=256)]
    intent_ref: ArtifactRef
    grant_ref: ArtifactRef
    idempotency_key: Annotated[str, Field(min_length=1, max_length=512)] | None = None
    claimed_at: Annotated[str, Field(min_length=1, max_length=64)]
    dispatched_at: Annotated[str, Field(min_length=1, max_length=64)] | None = None
    digest: Digest
    action_id: Annotated[str, Field(min_length=1, max_length=256)]
    effect_boundary: str

    @property
    def ref(self) -> ArtifactRef:
        return f"vcp:artifact:attempt:{self.attempt_id}"


class ExecutionReceipt(Contract):
    kind: str = "execution_receipt"
    version: str = "0.1.0"
    receipt_id: Annotated[str, Field(min_length=1, max_length=256)]
    attempt_ref: ArtifactRef
    effect_status: EffectStatus
    provider_ref: str | None = None
    evidence_refs: tuple[str, ...] = ()
    observed_at: Annotated[str, Field(min_length=1, max_length=64)]
    reconcile_ref: ArtifactRef | None = None
    digest: Digest

    @property
    def ref(self) -> ArtifactRef:
        return f"vcp:artifact:receipt:{self.receipt_id}"


class ControlCommand(Contract):
    kind: str = "control_command"
    version: str = "0.1.0"
    command_id: Annotated[str, Field(min_length=1, max_length=256)]
    operation: ControlOperation
    target_ref: ArtifactRef
    principal_ref: ArtifactRef
    reason: Annotated[str, Field(min_length=1, max_length=4096)]
    evidence_refs: tuple[str, ...] = ()
    issued_at: Annotated[str, Field(min_length=1, max_length=64)]
    idempotency_key: Annotated[str, Field(min_length=1, max_length=512)]
    digest: Digest
    represented_subject_ref: ArtifactRef
    authenticated_scope: tuple[str, ...]
    desired_transition: Annotated[str, Field(min_length=1, max_length=256)]
    expires_at: Annotated[str, Field(min_length=1, max_length=64)]

    @property
    def ref(self) -> ArtifactRef:
        return f"vcp:artifact:control:{self.command_id}"


class ObjectionResponse(Contract):
    kind: str = "objection_response"
    version: str = "0.1.0"
    response_id: Annotated[str, Field(min_length=1, max_length=256)]
    command_ref: ArtifactRef
    status: str
    responder_ref: ArtifactRef
    rationale: Annotated[str, Field(min_length=1, max_length=4096)]
    resolution_refs: tuple[str, ...] = ()
    decided_at: Annotated[str, Field(min_length=1, max_length=64)]
    digest: Digest


class EventEnvelope(Contract):
    kind: str = "event_envelope"
    version: str = "0.1.0"
    event_id: Annotated[str, Field(min_length=1, max_length=256)]
    event_type: Annotated[str, Field(min_length=1, max_length=256)]
    aggregate_ref: ArtifactRef
    sequence: int = Field(ge=0)
    occurred_at: Annotated[str, Field(min_length=1, max_length=64)]
    actor_ref: ArtifactRef
    payload_ref: ArtifactRef
    previous_digest: Digest | None = None
    digest: Digest
    source_ref: ArtifactRef
    recorded_at: Annotated[str, Field(min_length=1, max_length=64)]
    causal_parent_ref: ArtifactRef | None = None
    payload_digest: Digest
    redacted_summary: Annotated[str, Field(min_length=1, max_length=4096)]
    sensitivity: Annotated[str, Field(min_length=1, max_length=128)]
    evidence_refs: tuple[str, ...] = ()
    audit_refs: tuple[str, ...] = ()
    state_transition_version: Annotated[str, Field(min_length=1, max_length=128)]

    @property
    def ref(self) -> ArtifactRef:
        return f"vcp:artifact:event:{self.event_id}"


CursorDelta.model_rebuild()


class PredicateResult(Contract):
    predicate_ref: ArtifactRef
    status: AssuranceStatus
    evidence_refs: tuple[str, ...] = ()


class RunProof(Contract):
    kind: str = "run_proof"
    version: str = "0.1.0"
    proof_id: Annotated[str, Field(min_length=1, max_length=256)]
    run_ref: ArtifactRef
    predicate_results: tuple[PredicateResult, ...] = ()
    mandatory_complete: bool
    generated_at: Annotated[str, Field(min_length=1, max_length=64)]
    digest: Digest

    @property
    def ref(self) -> ArtifactRef:
        return f"vcp:artifact:proof:{self.proof_id}"


class ExperienceCapsule(Contract):
    kind: str = "experience_capsule"
    version: str = "0.1.0"
    capsule_id: Annotated[str, Field(min_length=1, max_length=256)]
    run_ref: ArtifactRef
    proof_ref: ArtifactRef
    terminal_status: RunStatus
    candidate_refs: tuple[str, ...] = ()
    resource_actual: ResourceMeasurement
    redacted_summary: Annotated[str, Field(min_length=1, max_length=4096)]
    created_at: Annotated[str, Field(min_length=1, max_length=64)]
    digest: Digest


class AccretionCandidate(Contract):
    kind: str = "accretion_candidate"
    version: str = "0.1.0"
    candidate_id: Annotated[str, Field(min_length=1, max_length=256)]
    candidate_kind: str
    content: Any
    scope: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    validation_status: AssuranceStatus
    review_required: bool
    expires_at: Annotated[str, Field(min_length=1, max_length=64)] | None = None
    digest: Digest
    source_run_ref: ArtifactRef
    supporting_evidence_refs: tuple[str, ...]
    contradicting_evidence_refs: tuple[str, ...] = ()
    sensitivity: Annotated[str, Field(min_length=1, max_length=128)]
    confidence: float = Field(ge=0, le=1)
    invalidation_triggers: tuple[str, ...]
    revalidation: Annotated[str, Field(min_length=1, max_length=4096)]
    promotion_policy: Annotated[str, Field(min_length=1, max_length=256)]
    expected_utility: float = Field(ge=-1_000_000, le=1_000_000)
    rollback: Annotated[str, Field(min_length=1, max_length=4096)]
    quarantine_status: str
    dependency_digest: Digest

    @property
    def ref(self) -> ArtifactRef:
        return f"vcp:artifact:candidate:{self.candidate_id}"


class PromotionRecord(Contract):
    kind: str = "promotion_record"
    version: str = "0.1.0"
    promotion_id: Annotated[str, Field(min_length=1, max_length=256)]
    candidate_ref: ArtifactRef
    promoted_asset_ref: ArtifactRef
    authority_ref: ArtifactRef
    decision_ref: ArtifactRef
    promoted_at: Annotated[str, Field(min_length=1, max_length=64)]
    expires_at: Annotated[str, Field(min_length=1, max_length=64)] | None = None
    revocation_ref: ArtifactRef
    digest: Digest
    evidence_refs: tuple[str, ...]
    validation_results: tuple[str, ...]
    scope: tuple[str, ...]
    promoted_content_digest: Digest
    dependency_digest: Digest

    @property
    def ref(self) -> ArtifactRef:
        return f"vcp:artifact:promotion:{self.promotion_id}"


class InfluenceReceipt(Contract):
    kind: str = "influence_receipt"
    version: str = "0.1.0"
    influence_id: Annotated[str, Field(min_length=1, max_length=256)]
    promoted_asset_ref: ArtifactRef
    decision_or_output_ref: ArtifactRef
    use: str
    observed_at: Annotated[str, Field(min_length=1, max_length=64)]
    digest: Digest
    scope: tuple[str, ...]
    invalidated_at: Annotated[str, Field(min_length=1, max_length=64)] | None = None


class RevocationRecord(Contract):
    kind: str = "revocation_record"
    version: str = "0.1.0"
    revocation_id: Annotated[str, Field(min_length=1, max_length=256)]
    promotion_ref: ArtifactRef
    promoted_asset_ref: ArtifactRef
    authority_ref: ArtifactRef
    reason: Annotated[str, Field(min_length=1, max_length=4096)]
    revoked_at: Annotated[str, Field(min_length=1, max_length=64)]
    propagation_bound_ms: int = Field(ge=0, le=86_400_000)
    downstream_influence_refs: tuple[str, ...]
    digest: Digest
