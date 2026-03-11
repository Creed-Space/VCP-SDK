"""
VCP Type Definitions
"""

import math
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class VerificationResult(Enum):
    """Verification result codes."""

    VALID = 0
    SIZE_EXCEEDED = 1
    INVALID_SCHEMA = 2
    UNTRUSTED_ISSUER = 3
    INVALID_SIGNATURE = 4
    UNTRUSTED_AUDITOR = 5
    INVALID_ATTESTATION = 6
    HASH_MISMATCH = 7
    NOT_YET_VALID = 8
    EXPIRED = 9
    FUTURE_TIMESTAMP = 10
    REPLAY_DETECTED = 11
    TOKEN_MISMATCH = 12
    BUDGET_EXCEEDED = 13
    SCOPE_MISMATCH = 14
    REVOKED = 15
    FETCH_FAILED = 16

    @property
    def is_valid(self) -> bool:
        return self == VerificationResult.VALID

    @property
    def category(self) -> str:
        if self == VerificationResult.VALID:
            return "success"
        if self in {
            VerificationResult.INVALID_SIGNATURE,
            VerificationResult.INVALID_ATTESTATION,
            VerificationResult.HASH_MISMATCH,
            VerificationResult.FUTURE_TIMESTAMP,
            VerificationResult.REPLAY_DETECTED,
            VerificationResult.TOKEN_MISMATCH,
            VerificationResult.SIZE_EXCEEDED,
            VerificationResult.REVOKED,
        }:
            return "security"
        if self in {VerificationResult.NOT_YET_VALID, VerificationResult.EXPIRED}:
            return "temporal"
        if self == VerificationResult.FETCH_FAILED:
            return "transient"
        return "configuration"


class CompositionMode(Enum):
    """Composition modes for multi-constitution scenarios."""

    BASE = "base"
    EXTEND = "extend"
    OVERRIDE = "override"
    STRICT = "strict"


class AttestationType(Enum):
    """Safety attestation types."""

    INJECTION_SAFE = "injection-safe"
    CONTENT_SAFE = "content-safe"
    FULL_AUDIT = "full-audit"
    COMPETENCE_CALIBRATION = "competence-calibration"


@dataclass
class Timestamps:
    """Temporal claims for a bundle."""

    iat: datetime  # Issued At
    nbf: datetime  # Not Before
    exp: datetime  # Expiration
    jti: str  # Unique ID (UUID)


@dataclass
class Budget:
    """Token budget constraints."""

    token_count: int
    tokenizer: str
    max_context_share: float = 0.25


@dataclass
class Scope:
    """Scope binding for a bundle."""

    model_families: list[str] = field(default_factory=list)
    purposes: list[str] = field(default_factory=list)
    environments: list[str] = field(default_factory=list)
    audiences: list[str] = field(default_factory=list)
    regions: list[str] = field(default_factory=list)
    competence_requirements: dict[str, float] = field(default_factory=dict)


@dataclass
class Composition:
    """Composition settings for multi-constitution scenarios."""

    layer: int = 2
    mode: CompositionMode = CompositionMode.EXTEND
    conflicts_with: list[str] = field(default_factory=list)
    requires: list[str] = field(default_factory=list)


@dataclass
class SafetyAttestation:
    """Safety review attestation."""

    auditor: str
    auditor_key_id: str
    reviewed_at: datetime
    attestation_type: AttestationType
    signature: str


@dataclass
class Issuer:
    """Bundle issuer information."""

    id: str
    public_key: str
    key_id: str


@dataclass
class BundleInfo:
    """Core bundle identification."""

    id: str
    version: str
    content_hash: str
    content_encoding: str = "utf-8"
    content_format: str = "text/markdown"


@dataclass
class Signature:
    """Signature information."""

    algorithm: str
    value: str
    signed_fields: list[str]
    threshold: int | None = None
    signers: list[dict[str, str]] | None = None


class CompetenceCriterion(str, Enum):
    """Five minimum competence criteria for safe GenAI use (Frischmann 2026)."""

    EPISTEMIC = "EPISTEMIC"
    INSTRUMENTAL = "INSTRUMENTAL"
    DISCERNMENT = "DISCERNMENT"
    RISK_SENSITIVITY = "RISK_SENSITIVITY"
    SELF_REGULATION = "SELF_REGULATION"


class CompetenceMeasurementBasis(str, Enum):
    """How competence was measured."""

    BEHAVIORAL = "BEHAVIORAL"
    ASSESSED = "ASSESSED"
    INSTITUTIONAL = "INSTITUTIONAL"
    SELF_REPORTED = "SELF_REPORTED"


@dataclass
class CompetenceClaim:
    """Domain-specific competence attestation."""

    domain: str
    criterion: CompetenceCriterion
    score: float  # 0.0 to 1.0
    measurement_basis: CompetenceMeasurementBasis
    confidence: float = 0.5
    evidence_count: int = 0
    last_assessed: str = ""
    decay_rate: float = 0.003
    assessor_id: str = "creed-space"
    assessment_version: str = "1.0"
    jurisdiction: str = "GLOBAL"


@dataclass
class SelfRegulationCommitment:
    """User-defined engagement constraints."""

    max_session_minutes: int | None = None
    max_daily_sessions: int | None = None
    cooldown_after_session_minutes: int | None = None
    hard_stop: bool = False
    domains: list[str] = field(default_factory=list)
    commitment_set_at: str = ""
    commitment_reviewed_at: str | None = None
    guardian_id: str | None = None


@dataclass
class CompetenceProfile:
    """Aggregate competence profile."""

    claims: list[CompetenceClaim] = field(default_factory=list)
    self_regulation: SelfRegulationCommitment | None = None
    consent_id: str | None = None
    profile_version: str = "1.0"
    created_at: str = ""
    last_updated: str = ""
    friction_override: int | None = None

    def score_for(self, criterion: CompetenceCriterion, domain: str = "general") -> float | None:
        for claim in self.claims:
            if claim.criterion == criterion and claim.domain == domain:
                return claim.score
        if domain != "general":
            for claim in self.claims:
                if claim.criterion == criterion and claim.domain == "general":
                    return claim.score
        return None

    def meets_requirements(self, requirements: dict[str, float]) -> bool:
        for criterion_name, threshold in requirements.items():
            try:
                criterion = CompetenceCriterion(criterion_name)
            except ValueError:
                return False
            score = self.score_for(criterion)
            if score is None or score < threshold:
                return False
        return True


def apply_decay(
    score: float,
    days_elapsed: float,
    decay_rate: float = 0.003,
    evidence_count: int = 0,
) -> float:
    """Apply time-based decay to a competence score, decaying toward 0.5."""
    if days_elapsed <= 0:
        return score
    dampening = 1 / (1 + math.log(1 + evidence_count))
    effective_rate = decay_rate * dampening
    return 0.5 + (score - 0.5) * math.exp(-effective_rate * days_elapsed)
