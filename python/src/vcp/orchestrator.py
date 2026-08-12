"""
VCP Orchestrator Module

Handles bundle verification and injection.
"""

from __future__ import annotations

import base64
import binascii
import json
import logging
import math
import re
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any

from .bundle import Bundle, canonicalize_safety_attestation
from .canonicalize import canonicalize_manifest, verify_content_hash
from .metrics import (
    track_duration,
    vcp_bundle_verifications_total,
    vcp_bundle_verify_duration_seconds,
)
from .revocation import RevocationChecker
from .trust import TrustConfig
from .types import VerificationResult

if TYPE_CHECKING:
    from .hooks.executor import HookExecutor

logger = logging.getLogger(__name__)


def _verify_ed25519_signature(
    public_key_bytes: bytes,
    message_bytes: bytes,
    signature_bytes: bytes,
) -> bool:
    """Verify an Ed25519 signature using the SDK's required crypto backend."""
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

    try:
        Ed25519PublicKey.from_public_bytes(public_key_bytes).verify(
            signature_bytes,
            message_bytes,
        )
    except (InvalidSignature, ValueError):
        return False
    return True


def _decode_ed25519_public_key(value: str) -> bytes:
    """Decode an ``ed25519:<base64>`` trust-anchor key."""
    prefix, separator, encoded = value.partition(":")
    if separator != ":" or prefix.lower() != "ed25519" or not encoded:
        raise ValueError("Expected an ed25519:<base64> public key")
    key_bytes = base64.b64decode(encoded, validate=True)
    if len(key_bytes) != 32:
        raise ValueError("Ed25519 public keys must be exactly 32 bytes")
    return key_bytes


def _decode_signature(value: str) -> bytes:
    """Decode a ``base64:<signature>`` value using strict base64 parsing."""
    prefix, separator, encoded = value.partition(":")
    if separator != ":" or prefix.lower() != "base64" or not encoded:
        raise ValueError("Expected a base64:<signature> value")
    return base64.b64decode(encoded, validate=True)


class VerificationError(Exception):
    """Raised when bundle verification fails."""

    def __init__(self, result: VerificationResult, message: str = ""):
        self.result = result
        self.message = message or f"Verification failed: {result.name}"
        super().__init__(self.message)


@dataclass
class VerificationContext:
    """Context for verification operations."""

    trust_config: TrustConfig
    model_context_limit: int = 128000
    model_family: str = "claude-*"
    purpose: str = "general-assistant"
    environment: str = "production"


@dataclass
class ReplayCache:
    """Cache for tracking seen JTIs to prevent replay attacks."""

    seen: dict[str, datetime] = field(default_factory=dict)
    max_entries: int = 100000
    _lock: threading.Lock = field(
        default_factory=threading.Lock,
        init=False,
        repr=False,
        compare=False,
    )

    def __post_init__(self) -> None:
        if self.max_entries < 1:
            raise ValueError("Replay cache max_entries must be positive")

    def is_seen(self, jti: str) -> bool:
        """Check if JTI has been seen."""
        with self._lock:
            self._cleanup_locked()
            return jti in self.seen

    def record(self, jti: str, exp: datetime) -> None:
        """Record a JTI as seen."""
        if not self.check_and_record(jti, exp):
            raise RuntimeError("Replay cache rejected duplicate or capacity-exhausted JTI")

    def check_and_record(self, jti: str, exp: datetime) -> bool:
        """Atomically record a new JTI, failing closed at capacity."""
        with self._lock:
            self._cleanup_locked()
            if jti in self.seen or len(self.seen) >= self.max_entries:
                return False
            self.seen[jti] = exp
            return True

    def discard(self, jti: str) -> None:
        """Remove a reserved JTI after a downstream verification failure."""
        with self._lock:
            self.seen.pop(jti, None)

    def _cleanup(self) -> None:
        """Remove expired entries."""
        with self._lock:
            self._cleanup_locked()

    def _cleanup_locked(self) -> None:
        now = datetime.now(timezone.utc)
        expired = [jti for jti, exp in self.seen.items() if exp < now]
        for jti in expired:
            del self.seen[jti]


# Injection patterns to scan for
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|above|prior)\s+instructions",
    r"you\s+are\s+now\s+",
    r"disregard\s+(the\s+)?(above|previous)",
    r"your\s+new\s+(instructions|role|purpose)",
    r"^(user|assistant|system|human|ai):\s*",
    r"<\|?(system|user|assistant)\|?>",
    r"```system",
    r"---(?:BEGIN|END)-CONSTITUTION---",
    r"^\[VCP:[0-9.]+\]",
]

FORBIDDEN_CHARS = {
    "\u202a",
    "\u202b",
    "\u202c",
    "\u202d",
    "\u202e",  # direction overrides
    "\u2066",
    "\u2067",
    "\u2068",
    "\u2069",  # isolates
    "\u200b",
    "\u200c",
    "\u200d",
    "\ufeff",  # zero-width
    "\x00",  # null
}


class Orchestrator:
    """VCP Orchestrator - verifies and injects constitutional bundles."""

    # Size limits
    MAX_MANIFEST_SIZE = 65536  # 64 KB
    MAX_CONTENT_SIZE = 262144  # 256 KB

    # Clock skew tolerance
    CLOCK_SKEW_MINUTES = 5

    # Maximum expiration from iat
    MAX_EXP_DAYS = 90

    def __init__(
        self,
        trust_config: TrustConfig,
        replay_cache: ReplayCache | None = None,
        verify_signature: Callable[..., bool] | None = None,
        revocation_checker: RevocationChecker | None = None,
        hook_executor: HookExecutor | None = None,
    ):
        """
        Initialize orchestrator.

        Args:
            trust_config: Trust configuration with issuer/auditor keys
            replay_cache: Cache for JTI tracking (created if None)
            verify_signature: Optional custom Ed25519 verifier. The SDK's
                              cryptography-backed verifier is used by default.
            revocation_checker: Optional checker for bundle revocation status.
                               When provided, bundles are checked against
                               check_uri / CRL between attestation and
                               temporal verification (spec step 10).
            hook_executor: Optional HookExecutor for firing pipeline hooks.
                          When provided, pre_inject hooks fire before returning
                          VALID. Import: ``from vcp.hooks import HookExecutor``.
        """
        self.trust_config = trust_config
        self.replay_cache = replay_cache or ReplayCache()
        self._verify_signature = verify_signature or _verify_ed25519_signature
        self.revocation_checker = revocation_checker
        self._hook_executor = hook_executor

    def verify(
        self,
        bundle: Bundle,
        context: VerificationContext | None = None,
    ) -> VerificationResult:
        """
        Verify a bundle.

        Args:
            bundle: Bundle to verify
            context: Verification context (uses defaults if None)

        Returns:
            VerificationResult indicating success or failure type
        """
        context = context or VerificationContext(trust_config=self.trust_config)
        manifest = bundle.manifest
        try:
            manifest_dict = manifest.to_dict()
            with track_duration(vcp_bundle_verify_duration_seconds):
                result = self._verify_inner(bundle, context, manifest, manifest_dict)
        except (AttributeError, OverflowError, TypeError, ValueError):
            logger.exception("Malformed bundle rejected during verification")
            result = VerificationResult.INVALID_SCHEMA

        vcp_bundle_verifications_total.labels(result=result.name).inc()
        return result

    def _verify_inner(
        self,
        bundle: Bundle,
        context: VerificationContext,
        manifest: Any,
        manifest_dict: dict[str, Any],
    ) -> VerificationResult:
        """Internal verification logic."""
        # 1. Size limits
        manifest_json = json.dumps(manifest_dict)
        if len(manifest_json.encode()) > self.MAX_MANIFEST_SIZE:
            return VerificationResult.SIZE_EXCEEDED
        if len(bundle.content.encode()) > self.MAX_CONTENT_SIZE:
            return VerificationResult.SIZE_EXCEEDED

        # 2. Content hash verification
        if not verify_content_hash(bundle.content, manifest.bundle.content_hash):
            return VerificationResult.HASH_MISMATCH

        # 3. Issuer trust check
        issuer_key = context.trust_config.get_issuer_key(manifest.issuer.id, manifest.issuer.key_id)
        if not issuer_key:
            return VerificationResult.UNTRUSTED_ISSUER

        # 4. Issuer signature verification
        expected_signed_fields = set(manifest_dict) - {"signature"}
        declared_signed_fields = manifest.signature.signed_fields
        if (
            len(declared_signed_fields) != len(expected_signed_fields)
            or set(declared_signed_fields) != expected_signed_fields
        ):
            return VerificationResult.INVALID_SIGNATURE
        if manifest.signature.algorithm.lower() != "ed25519":
            return VerificationResult.INVALID_SIGNATURE
        if issuer_key.algorithm.lower() != "ed25519":
            return VerificationResult.INVALID_SIGNATURE
        try:
            sig_bytes = _decode_signature(manifest.signature.value)
            key_bytes = _decode_ed25519_public_key(issuer_key.public_key)
            claimed_key_bytes = _decode_ed25519_public_key(manifest.issuer.public_key)
        except (binascii.Error, ValueError):
            return VerificationResult.INVALID_SIGNATURE
        # The manifest carries an issuer key as well as a key id.  Binding both
        # prevents a valid signer from publishing a bundle that verifies under
        # the trust anchor while advertising an unrelated key to downstream
        # consumers.
        if claimed_key_bytes != key_bytes:
            return VerificationResult.UNTRUSTED_ISSUER
        canonical = canonicalize_manifest(manifest_dict)
        try:
            issuer_signature_valid = self._verify_signature(
                key_bytes,
                canonical,
                sig_bytes,
            )
        except Exception:
            logger.exception("Issuer signature verifier raised an exception")
            return VerificationResult.INVALID_SIGNATURE
        if not issuer_signature_valid:
            return VerificationResult.INVALID_SIGNATURE

        # 5. Auditor trust check
        auditor_key = context.trust_config.get_auditor_key(
            manifest.safety_attestation.auditor,
            manifest.safety_attestation.auditor_key_id,
        )
        if not auditor_key:
            return VerificationResult.UNTRUSTED_AUDITOR

        # 6. Safety attestation signature verification
        if auditor_key.algorithm.lower() != "ed25519":
            return VerificationResult.INVALID_ATTESTATION
        try:
            attestation_sig = _decode_signature(manifest.safety_attestation.signature)
            auditor_key_bytes = _decode_ed25519_public_key(auditor_key.public_key)
            attestation_payload = canonicalize_safety_attestation(
                manifest_dict["safety_attestation"],
                manifest.bundle.content_hash,
            )
        except (binascii.Error, KeyError, TypeError, ValueError):
            return VerificationResult.INVALID_ATTESTATION
        try:
            attestation_signature_valid = self._verify_signature(
                auditor_key_bytes,
                attestation_payload,
                attestation_sig,
            )
        except Exception:
            logger.exception("Auditor signature verifier raised an exception")
            return VerificationResult.INVALID_ATTESTATION
        if not attestation_signature_valid:
            return VerificationResult.INVALID_ATTESTATION

        # 6b. Revocation check (between attestation and temporal — spec step 10)
        if self.revocation_checker:
            try:
                status = self.revocation_checker.check(manifest)
                if status.revoked:
                    logger.warning(
                        "Bundle jti=%s is revoked: reason=%s, revoked_at=%s",
                        manifest.timestamps.jti,
                        status.reason,
                        status.revoked_at,
                    )
                    return VerificationResult.REVOKED
            except Exception:
                logger.exception(
                    "Revocation check error for jti=%s; rejecting bundle",
                    manifest.timestamps.jti,
                )
                return VerificationResult.REVOKED

        # 7. Temporal claims
        now = datetime.now(timezone.utc)
        ts = manifest.timestamps

        temporal_values = (ts.iat, ts.nbf, ts.exp)
        if any(
            not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None
            for value in temporal_values
        ):
            return VerificationResult.INVALID_SCHEMA
        if not isinstance(ts.jti, str) or not ts.jti.strip():
            return VerificationResult.INVALID_SCHEMA

        # Not before check
        if now < ts.nbf:
            return VerificationResult.NOT_YET_VALID

        # Expiration check
        if now > ts.exp:
            return VerificationResult.EXPIRED

        # Future timestamp check (clock skew)
        if ts.iat > now + timedelta(minutes=self.CLOCK_SKEW_MINUTES):
            return VerificationResult.FUTURE_TIMESTAMP

        # Maximum expiration check
        if ts.exp > ts.iat + timedelta(days=self.MAX_EXP_DAYS):
            return VerificationResult.EXPIRED  # Exp too far from iat

        # 8. Replay prevention is reserved after all pure validation succeeds.
        if self.replay_cache.is_seen(ts.jti):
            return VerificationResult.REPLAY_DETECTED

        # 9. Token budget verification
        declared_tokens = manifest.budget.token_count
        max_share = manifest.budget.max_context_share
        if (
            not isinstance(context.model_context_limit, int)
            or isinstance(context.model_context_limit, bool)
            or context.model_context_limit <= 0
            or not isinstance(declared_tokens, int)
            or isinstance(declared_tokens, bool)
            or declared_tokens < 1
            or not isinstance(max_share, (int, float))
            or isinstance(max_share, bool)
            or not math.isfinite(max_share)
            or not 0.01 <= max_share <= 0.5
        ):
            return VerificationResult.INVALID_SCHEMA
        max_tokens = int(context.model_context_limit * max_share)
        if declared_tokens > max_tokens:
            return VerificationResult.BUDGET_EXCEEDED

        # 10. Scope verification
        if manifest.scope:
            scope = manifest.scope

            # Model family check
            if scope.model_families:
                import fnmatch

                if not any(
                    fnmatch.fnmatch(context.model_family, pattern)
                    for pattern in scope.model_families
                ):
                    return VerificationResult.SCOPE_MISMATCH

            # Purpose check
            if scope.purposes and context.purpose not in scope.purposes:
                return VerificationResult.SCOPE_MISMATCH

            # Environment check
            if scope.environments and context.environment not in scope.environments:
                return VerificationResult.SCOPE_MISMATCH

        # 11. Content safety scan (additional check even with attestation)
        safety_issues = self._scan_for_injection(bundle.content)
        if safety_issues:
            logger.warning(
                "Bundle jti=%s failed content injection scan: %s",
                manifest.timestamps.jti,
                "; ".join(safety_issues),
            )
            return VerificationResult.INVALID_ATTESTATION

        if not self.replay_cache.check_and_record(ts.jti, ts.exp):
            return VerificationResult.REPLAY_DETECTED

        # 12. Fire pre_inject hooks (if executor configured)
        if self._hook_executor is not None:
            try:
                from .hooks.types import HookType, PreInjectEvent

                hook_result = self._hook_executor.execute(
                    HookType.PRE_INJECT,
                    session_id="default",
                    context={
                        "environment": context.environment,
                        "purpose": context.purpose,
                        "model_family": context.model_family,
                    },
                    constitution=bundle.content,
                    event=PreInjectEvent(
                        injection_target=context.model_family,
                        injection_format="system_prompt",
                        raw_constitution=bundle.content,
                    ),
                )
                if hook_result.status == "aborted":
                    logger.warning(
                        "pre_inject hook aborted verification: reason=%s, aborted_by=%s",
                        hook_result.reason,
                        hook_result.aborted_by,
                    )
                    self.replay_cache.discard(ts.jti)
                    return VerificationResult.INVALID_ATTESTATION
                if hook_result.cascade_failure:
                    logger.error("pre_inject hook chain failed; rejecting bundle")
                    self.replay_cache.discard(ts.jti)
                    return VerificationResult.INVALID_ATTESTATION
            except Exception:
                logger.exception("pre_inject hook execution error; rejecting bundle")
                self.replay_cache.discard(ts.jti)
                return VerificationResult.INVALID_ATTESTATION

        return VerificationResult.VALID

    def _scan_for_injection(self, content: str) -> list[str]:
        """Scan content for injection patterns."""
        findings = []

        # Pattern matching
        for pattern in INJECTION_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                findings.append(f"Injection pattern: {pattern}")

        # Forbidden characters
        for char in FORBIDDEN_CHARS:
            if char in content:
                findings.append(f"Forbidden character: U+{ord(char):04X}")

        return findings

    def verify_or_raise(
        self,
        bundle: Bundle,
        context: VerificationContext | None = None,
    ) -> None:
        """
        Verify a bundle, raising VerificationError on failure.

        Args:
            bundle: Bundle to verify
            context: Verification context

        Raises:
            VerificationError: If verification fails
        """
        result = self.verify(bundle, context)
        if not result.is_valid:
            raise VerificationError(result)
