"""
VCP Type Definitions
"""

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
