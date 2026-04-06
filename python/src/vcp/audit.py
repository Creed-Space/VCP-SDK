"""
VCP Audit Module

Privacy-preserving audit logging for VCP operations.
"""

import hashlib
import json
import logging
import os
import threading
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from .metrics import vcp_audit_events_total

logger = logging.getLogger(__name__)

# Per-process random salt for privacy hashing. Makes hashes non-reversible
# from known inputs while remaining deterministic within a process lifetime
# (required for purge_by_session matching).
_PRIVACY_SALT: bytes = os.urandom(32)


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
        """Convert to dictionary for logging.

        Respects Amendment J audit tier boundaries:
            minimal:    bundle ID hash, content hash, verification result only
            standard:   + timestamps, session, issuer, version, signature
            full:       + duration, token count (complete manifest, no content)
            diagnostic: + content preview (first 100 chars)
        """
        verification: dict[str, Any] = {
            "result": self.verification_result,
        }
        bundle_ref: dict[str, Any] = {
            "id_hash": self.bundle_id_hash,
            "content_hash": self.content_hash,
        }
        result: dict[str, Any] = {
            "vcp_audit_version": "1.1",
            "audit_level": self.audit_level.value,
            "verification": verification,
            "bundle_ref": bundle_ref,
        }

        # MINIMAL: only bundle hash + verification result (above)

        # STANDARD+: add timestamps, session, issuer, version, signature, checks
        if self.audit_level in (
            AuditLevel.STANDARD,
            AuditLevel.FULL,
            AuditLevel.DIAGNOSTIC,
        ):
            result["timestamp"] = self.timestamp.isoformat() + "Z"
            result["session_id_hash"] = self.session_id_hash
            result["manifest_signature"] = self.manifest_signature
            verification["checks_passed"] = self.checks_passed
            bundle_ref["issuer_hash"] = self.issuer_hash
            bundle_ref["version"] = self.version

            if self.request_id:
                result["request_id"] = self.request_id

        # FULL+: add duration, token count
        if self.audit_level in (AuditLevel.FULL, AuditLevel.DIAGNOSTIC):
            if self.duration_ms is not None:
                verification["duration_ms"] = self.duration_ms
            if self.token_count is not None:
                bundle_ref["token_count"] = self.token_count

        # DIAGNOSTIC only: content preview
        if self.audit_level == AuditLevel.DIAGNOSTIC and self.content_preview:
            bundle_ref["content_preview"] = self.content_preview

        return result

    def to_json(self, indent: int | None = None) -> str:
        """Serialize to JSON."""
        return json.dumps(self.to_dict(), indent=indent)


def _hash_for_privacy(value: str) -> str:
    """Hash a value for privacy-preserving logging.

    Uses a per-process random salt so hashes are not reversible from
    known inputs, but remain deterministic within the same process
    (required for purge_by_session matching).
    """
    salted = _PRIVACY_SALT + value.encode()
    return f"sha256:{hashlib.sha256(salted).hexdigest()[:32]}"


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
        self._exported_paths: list[str] = []
        self._purge_handlers: list[Callable[[str, str], dict[str, Any]]] = []
        self._lock = threading.Lock()

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
            timestamp=datetime.now(timezone.utc),
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
        vcp_audit_events_total.labels(event_type="verification").inc()

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

    def log_privacy_filter(
        self,
        platform_id: str,
        session_id: str,
        fields_shared: int,
        fields_withheld: int,
        constraint_flags_active: int,
    ) -> AuditEntry:
        """Log a privacy filtering operation (Amendment J §5).

        Creates a lightweight audit entry recording that context was filtered
        for a platform. Private field values are never included — only counts.

        Args:
            platform_id: Platform identifier (will be hashed)
            session_id: Session identifier (will be hashed)
            fields_shared: Number of fields shared
            fields_withheld: Number of fields withheld
            constraint_flags_active: Number of active boolean constraint flags

        Returns:
            Created audit entry
        """
        # Only include session_id_hash at FULL+ tier. At STANDARD, the
        # privacy-filter event (which records that context was *withheld*)
        # should not itself emit a linkable session identifier.
        include_session = self.level in (AuditLevel.FULL, AuditLevel.DIAGNOSTIC)

        entry = AuditEntry(
            timestamp=datetime.now(timezone.utc),
            session_id_hash=(
                _hash_for_privacy(session_id) if include_session else "redacted"
            ),
            verification_result="PRIVACY_FILTER",
            checks_passed=[
                f"shared:{fields_shared}",
                f"withheld:{fields_withheld}",
                f"constraints:{constraint_flags_active}",
                "private_fields_exposed:0",
            ],
            bundle_id_hash=_hash_for_privacy(platform_id),
            content_hash="n/a",
            issuer_hash="n/a",
            version="n/a",
            manifest_signature="n/a",
            audit_level=self.level,
        )

        self._entries.append(entry)
        vcp_audit_events_total.labels(event_type="privacy_filter").inc()

        if self._log_callback:
            self._log_callback(entry)

        return entry

    def clear(self) -> None:
        """Clear stored entries."""
        self._entries.clear()

    def register_purge_handler(
        self,
        handler: Callable[[str, str], dict[str, Any]],
    ) -> None:
        """Register an external sink's purge handler.

        When :meth:`purge_by_session` runs, each registered handler is
        called with ``(session_id_hash, purge_id)`` and should delete
        that session's data from its store, returning a dict describing
        what was removed (included in the tombstone receipt).

        If ``log_callback`` is set without any purge handler, purge_by_session
        will log a warning — the callback sink likely holds data that won't
        be reached.

        Args:
            handler: ``(session_id_hash: str, purge_id: str) -> dict[str, Any]``
        """
        self._purge_handlers.append(handler)

    def purge_by_session(self, session_id: str) -> dict[str, Any]:
        """Purge all audit entries for a session (GDPR right to erasure).

        Purges matching entries from:
        1. The in-memory entry list
        2. Any JSON files previously written via :meth:`export_json`
        3. Any external sinks via registered purge handlers

        A tombstone receipt is returned so that compliance can be
        demonstrated to a regulator.

        Args:
            session_id: Raw session identifier (will be hashed for comparison)

        Returns:
            Tombstone receipt dict with purge_id, timestamp, entries_removed,
            files_purged, external_sink_results, and scope description.
        """
        target_hash = _hash_for_privacy(session_id)
        purge_id = str(uuid.uuid4())

        with self._lock:
            before = len(self._entries)
            self._entries = [
                e for e in self._entries if e.session_id_hash != target_hash
            ]
            removed = before - len(self._entries)

            # Scrub exported JSON files while still holding the lock so
            # concurrent export_json() calls cannot interleave.
            files_purged = self._purge_exported_files(target_hash)
        total_file_entries = sum(files_purged.values())

        # Propagate purge to registered external sinks
        external_results: list[dict[str, Any]] = []
        for handler in self._purge_handlers:
            try:
                result = handler(target_hash, purge_id)
                external_results.append(result)
            except Exception:
                logger.exception(
                    "[GDPR] External purge handler failed for purge_id=%s",
                    purge_id,
                )
                external_results.append({"error": "handler raised exception"})

        # Warn if log_callback is set but no purge handler covers it
        if self._log_callback and not self._purge_handlers:
            logger.warning(
                "[GDPR] log_callback is set but no purge handlers are registered. "
                "Data delivered to the callback sink may not be purged. "
                "Use register_purge_handler() to close this gap."
            )

        if removed > 0 or total_file_entries > 0 or external_results:
            vcp_audit_events_total.labels(event_type="purge").inc()

        scope_parts = ["in-memory audit entries", "tracked exported JSON files"]
        if self._purge_handlers:
            scope_parts.append(f"{len(self._purge_handlers)} external sink(s)")

        tombstone: dict[str, Any] = {
            "purge_id": purge_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "entries_removed": removed,
            "file_entries_removed": total_file_entries,
            "files_purged": files_purged,
            "external_sink_results": external_results,
            "scope": " + ".join(scope_parts),
        }

        if self._log_callback and (removed > 0 or total_file_entries > 0 or external_results):
            purge_entry = AuditEntry(
                timestamp=datetime.now(timezone.utc),
                session_id_hash=target_hash,
                verification_result="PURGE_TOMBSTONE",
                checks_passed=[
                    f"memory_removed:{removed}",
                    f"file_removed:{total_file_entries}",
                    f"external_sinks:{len(external_results)}",
                ],
                bundle_id_hash=purge_id,
                content_hash="n/a",
                issuer_hash="n/a",
                version="n/a",
                manifest_signature="n/a",
                audit_level=self.level,
            )
            self._log_callback(purge_entry)

        return tombstone

    def export_json(self, path: str) -> None:
        """Export entries to JSON file.

        The path is tracked so that :meth:`purge_by_session` can also
        scrub session data from previously exported files.
        """
        with self._lock:
            with open(path, "w", encoding="utf-8") as f:
                entries = [e.to_dict() for e in self._entries]
                json.dump({"entries": entries}, f, indent=2)
            if path not in self._exported_paths:
                self._exported_paths.append(path)

    def _purge_exported_files(self, session_id_hash: str) -> dict[str, int]:
        """Remove entries matching session_id_hash from all exported JSON files.

        Rewrites each file in-place (atomic replace). Files that no longer
        exist are silently skipped and removed from the tracking list.

        Returns:
            Dict mapping file path to number of entries removed from that file.
        """
        results: dict[str, int] = {}
        surviving_paths: list[str] = []

        for path in self._exported_paths:
            if not os.path.isfile(path):
                continue
            surviving_paths.append(path)

            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            entries = data.get("entries", [])
            before = len(entries)
            filtered = [
                e for e in entries
                if e.get("session_id_hash") != session_id_hash
            ]
            removed = before - len(filtered)

            if removed > 0:
                tmp_path = path + ".purge.tmp"
                data["entries"] = filtered
                with open(tmp_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                os.replace(tmp_path, path)
                results[path] = removed

        self._exported_paths = surviving_paths
        return results
