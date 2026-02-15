"""
VCP Audit Module

Privacy-preserving audit logging for VCP operations.
"""

import hashlib
import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class AuditLevel(Enum):
    """Audit log detail levels."""

    MINIMAL = "minimal"
    STANDARD = "standard"
    FULL = "full"
    DIAGNOSTIC = "diagnostic"


@dataclass
class AuditEntry:
    """A VCP audit log entry."""

    timestamp: datetime
    session_id_hash: str
    verification_result: str
    checks_passed: list[str]
    bundle_id_hash: str
    content_hash: str
    issuer_hash: str
    version: str
    manifest_signature: str
    audit_level: AuditLevel = AuditLevel.STANDARD

    # Optional fields for higher audit levels
    request_id: str | None = None
    duration_ms: int | None = None
    token_count: int | None = None
    content_preview: str | None = None  # For diagnostic level only

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for logging."""
        verification: dict[str, Any] = {
            "result": self.verification_result,
            "checks_passed": self.checks_passed,
        }
        bundle_ref: dict[str, Any] = {
            "id_hash": self.bundle_id_hash,
            "content_hash": self.content_hash,
            "issuer_hash": self.issuer_hash,
            "version": self.version,
        }
        result: dict[str, Any] = {
            "vcp_audit_version": "1.0",
            "audit_level": self.audit_level.value,
            "timestamp": self.timestamp.isoformat() + "Z",
            "session_id_hash": self.session_id_hash,
            "verification": verification,
            "bundle_ref": bundle_ref,
            "manifest_signature": self.manifest_signature,
        }

        if self.request_id:
            result["request_id"] = self.request_id

        if self.audit_level in (AuditLevel.FULL, AuditLevel.DIAGNOSTIC):
            if self.duration_ms is not None:
                verification["duration_ms"] = self.duration_ms
            if self.token_count is not None:
                bundle_ref["token_count"] = self.token_count

        if self.audit_level == AuditLevel.DIAGNOSTIC and self.content_preview:
            bundle_ref["content_preview"] = self.content_preview

        return result

    def to_json(self, indent: int | None = None) -> str:
        """Serialize to JSON."""
        return json.dumps(self.to_dict(), indent=indent)


def _hash_for_privacy(value: str) -> str:
    """Hash a value for privacy-preserving logging."""
    return f"sha256:{hashlib.sha256(value.encode()).hexdigest()[:32]}"


class AuditLogger:
    """Privacy-preserving audit logger for VCP operations."""

    def __init__(
        self,
        level: AuditLevel = AuditLevel.STANDARD,
        log_callback: Callable[[AuditEntry], None] | None = None,
    ):
        """
        Initialize audit logger.

        Args:
            level: Detail level for logging
            log_callback: Function to call with audit entries
                         (entry: AuditEntry) -> None
        """
        self.level = level
        self._log_callback = log_callback
        self._entries: list[AuditEntry] = []

    def log_verification(
        self,
        bundle: Any,  # Bundle
        result: Any,  # VerificationResult
        session_id: str,
        request_id: str | None = None,
        duration_ms: int | None = None,
    ) -> AuditEntry:
        """
        Log a verification operation.

        Args:
            bundle: Verified bundle
            result: Verification result
            session_id: Session identifier (will be hashed)
            request_id: Optional request ID (will be hashed)
            duration_ms: Verification duration in milliseconds

        Returns:
            Created audit entry
        """
        from .types import VerificationResult

        manifest = bundle.manifest

        # Determine checks passed
        checks = []
        if result == VerificationResult.VALID:
            checks = [
                "size",
                "schema",
                "signature",
                "attestation",
                "hash",
                "temporal",
                "replay",
                "budget",
                "scope",
                "revocation",
            ]
        elif result.value > 0:
            # Partial checks based on error code
            check_order = [
                "size",
                "schema",
                "issuer",
                "signature",
                "auditor",
                "attestation",
                "hash",
                "nbf",
                "exp",
                "timestamp",
                "replay",
                "tokens",
                "budget",
                "scope",
                "revoked",
            ]
            # All checks before the failing one passed
            if result.value <= len(check_order):
                checks = check_order[: result.value - 1]

        # Extract signature value (truncated for log)
        sig = manifest.signature.value
        if sig.startswith("base64:"):
            sig = sig[7:]
        sig_truncated = sig[:32] + "..." if len(sig) > 32 else sig

        entry = AuditEntry(
            timestamp=datetime.utcnow(),
            session_id_hash=_hash_for_privacy(session_id),
            verification_result=result.name,
            checks_passed=checks,
            bundle_id_hash=_hash_for_privacy(manifest.bundle.id),
            content_hash=manifest.bundle.content_hash,
            issuer_hash=_hash_for_privacy(manifest.issuer.id),
            version=manifest.bundle.version,
            manifest_signature=sig_truncated,
            audit_level=self.level,
            request_id=(
                _hash_for_privacy(request_id) if request_id else None
            ),
            duration_ms=(
                duration_ms
                if self.level in (AuditLevel.FULL, AuditLevel.DIAGNOSTIC)
                else None
            ),
            token_count=(
                manifest.budget.token_count
                if self.level in (AuditLevel.FULL, AuditLevel.DIAGNOSTIC)
                else None
            ),
            content_preview=(
                bundle.content[:100]
                if self.level == AuditLevel.DIAGNOSTIC
                else None
            ),
        )

        self._entries.append(entry)

        if self._log_callback:
            self._log_callback(entry)

        return entry

    def get_entries(self, since: datetime | None = None) -> list[AuditEntry]:
        """
        Get audit entries.

        Args:
            since: Only return entries after this time

        Returns:
            List of audit entries
        """
        if since:
            return [e for e in self._entries if e.timestamp > since]
        return list(self._entries)

    def clear(self) -> None:
        """Clear stored entries."""
        self._entries.clear()

    def export_json(self, path: str) -> None:
        """Export entries to JSON file."""
        with open(path, "w", encoding="utf-8") as f:
            entries = [e.to_dict() for e in self._entries]
            json.dump({"entries": entries}, f, indent=2)
