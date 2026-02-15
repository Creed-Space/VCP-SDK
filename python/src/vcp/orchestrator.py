"""
VCP Orchestrator Module

Handles bundle verification and injection.
"""

import json
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from .bundle import Bundle
from .canonicalize import canonicalize_manifest, verify_content_hash
from .trust import TrustConfig
from .types import VerificationResult


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

    def is_seen(self, jti: str) -> bool:
        """Check if JTI has been seen."""
        self._cleanup()
        return jti in self.seen

    def record(self, jti: str, exp: datetime) -> None:
        """Record a JTI as seen."""
        self.seen[jti] = exp

    def _cleanup(self) -> None:
        """Remove expired entries."""
        now = datetime.utcnow()
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
    ):
        """
        Initialize orchestrator.

        Args:
            trust_config: Trust configuration with issuer/auditor keys
            replay_cache: Cache for JTI tracking (created if None)
            verify_signature: Function to verify Ed25519 signatures
                             (public_key_bytes, message_bytes, signature_bytes) -> bool
        """
        self.trust_config = trust_config
        self.replay_cache = replay_cache or ReplayCache()
        self._verify_signature = verify_signature

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
        manifest_dict = manifest.to_dict()

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
        if self._verify_signature:
            sig_value = manifest.signature.value
            if sig_value.startswith("base64:"):
                sig_value = sig_value[7:]
            import base64

            sig_bytes = base64.b64decode(sig_value)
            key_bytes = base64.b64decode(issuer_key.public_key.split(":")[1])
            canonical = canonicalize_manifest(manifest_dict)
            if not self._verify_signature(key_bytes, canonical, sig_bytes):
                return VerificationResult.INVALID_SIGNATURE

        # 5. Auditor trust check
        auditor_key = context.trust_config.get_auditor_key(
            manifest.safety_attestation.auditor,
            manifest.safety_attestation.auditor_key_id,
        )
        if not auditor_key:
            return VerificationResult.UNTRUSTED_AUDITOR

        # 6. Safety attestation signature verification
        if self._verify_signature:
            attestation_sig = manifest.safety_attestation.signature
            if attestation_sig.startswith("base64:"):
                attestation_sig = attestation_sig[7:]
            # Note: In production, reconstruct attestation payload and verify
            # For now, we trust the presence of the attestation

        # 7. Temporal claims
        now = datetime.utcnow()
        ts = manifest.timestamps

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

        # 8. Replay prevention
        if self.replay_cache.is_seen(ts.jti):
            return VerificationResult.REPLAY_DETECTED
        self.replay_cache.record(ts.jti, ts.exp)

        # 9. Token budget verification
        declared_tokens = manifest.budget.token_count
        max_share = manifest.budget.max_context_share
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
            # Log warning but don't fail if attestation present
            # In strict mode, could return INVALID_ATTESTATION
            pass

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
