"""
Tests for vcp.audit — Amendment J privacy-preserving audit logging.

Verifies:
    - Audit tier boundaries (minimal/standard/full/diagnostic)
    - GDPR log purge (right to erasure)
    - Privacy filter audit events
"""

from __future__ import annotations

from datetime import datetime

from vcp.audit import AuditEntry, AuditLevel, AuditLogger, _hash_for_privacy

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_entry(level: AuditLevel = AuditLevel.STANDARD, **kwargs) -> AuditEntry:
    """Create a test audit entry with sensible defaults."""
    defaults = dict(
        timestamp=datetime(2026, 1, 10, 12, 0, 0),
        session_id_hash=_hash_for_privacy("sess-1"),
        verification_result="VALID",
        checks_passed=["size", "schema", "signature"],
        bundle_id_hash=_hash_for_privacy("bundle-1"),
        content_hash="sha256:abc123",
        issuer_hash=_hash_for_privacy("issuer-1"),
        version="1.2.0",
        manifest_signature="base64sig...",
        audit_level=level,
        request_id=_hash_for_privacy("req-1"),
        duration_ms=42,
        token_count=500,
        content_preview="First 100 chars of content...",
    )
    defaults.update(kwargs)
    return AuditEntry(**defaults)


# ---------------------------------------------------------------------------
# Amendment J: Audit tier boundaries
# ---------------------------------------------------------------------------


class TestAuditTierBoundaries:
    """Amendment J: each tier only exposes the fields it should."""

    def test_minimal_excludes_timestamp(self) -> None:
        d = _make_entry(AuditLevel.MINIMAL).to_dict()
        assert "timestamp" not in d

    def test_minimal_excludes_session_id(self) -> None:
        d = _make_entry(AuditLevel.MINIMAL).to_dict()
        assert "session_id_hash" not in d

    def test_minimal_excludes_issuer(self) -> None:
        d = _make_entry(AuditLevel.MINIMAL).to_dict()
        assert "issuer_hash" not in d["bundle_ref"]

    def test_minimal_excludes_version(self) -> None:
        d = _make_entry(AuditLevel.MINIMAL).to_dict()
        assert "version" not in d["bundle_ref"]

    def test_minimal_excludes_signature(self) -> None:
        d = _make_entry(AuditLevel.MINIMAL).to_dict()
        assert "manifest_signature" not in d

    def test_minimal_excludes_checks_passed(self) -> None:
        d = _make_entry(AuditLevel.MINIMAL).to_dict()
        assert "checks_passed" not in d["verification"]

    def test_minimal_includes_bundle_hash(self) -> None:
        d = _make_entry(AuditLevel.MINIMAL).to_dict()
        assert "id_hash" in d["bundle_ref"]
        assert "content_hash" in d["bundle_ref"]

    def test_minimal_includes_verification_result(self) -> None:
        d = _make_entry(AuditLevel.MINIMAL).to_dict()
        assert d["verification"]["result"] == "VALID"

    def test_minimal_excludes_duration(self) -> None:
        d = _make_entry(AuditLevel.MINIMAL).to_dict()
        assert "duration_ms" not in d["verification"]

    def test_minimal_excludes_content_preview(self) -> None:
        d = _make_entry(AuditLevel.MINIMAL).to_dict()
        assert "content_preview" not in d["bundle_ref"]

    def test_standard_includes_timestamp(self) -> None:
        d = _make_entry(AuditLevel.STANDARD).to_dict()
        assert "timestamp" in d

    def test_standard_includes_session_and_issuer(self) -> None:
        d = _make_entry(AuditLevel.STANDARD).to_dict()
        assert "session_id_hash" in d
        assert "issuer_hash" in d["bundle_ref"]
        assert "version" in d["bundle_ref"]

    def test_standard_includes_checks_passed(self) -> None:
        d = _make_entry(AuditLevel.STANDARD).to_dict()
        assert "checks_passed" in d["verification"]

    def test_standard_excludes_duration(self) -> None:
        d = _make_entry(AuditLevel.STANDARD).to_dict()
        assert "duration_ms" not in d["verification"]

    def test_standard_excludes_content_preview(self) -> None:
        d = _make_entry(AuditLevel.STANDARD).to_dict()
        assert "content_preview" not in d["bundle_ref"]

    def test_full_includes_duration(self) -> None:
        d = _make_entry(AuditLevel.FULL).to_dict()
        assert d["verification"]["duration_ms"] == 42

    def test_full_includes_token_count(self) -> None:
        d = _make_entry(AuditLevel.FULL).to_dict()
        assert d["bundle_ref"]["token_count"] == 500

    def test_full_excludes_content_preview(self) -> None:
        d = _make_entry(AuditLevel.FULL).to_dict()
        assert "content_preview" not in d["bundle_ref"]

    def test_diagnostic_includes_content_preview(self) -> None:
        d = _make_entry(AuditLevel.DIAGNOSTIC).to_dict()
        assert "content_preview" in d["bundle_ref"]

    def test_diagnostic_includes_everything(self) -> None:
        d = _make_entry(AuditLevel.DIAGNOSTIC).to_dict()
        assert "timestamp" in d
        assert "session_id_hash" in d
        assert d["verification"]["duration_ms"] == 42
        assert d["bundle_ref"]["token_count"] == 500
        assert "content_preview" in d["bundle_ref"]

    def test_audit_version_is_1_1(self) -> None:
        d = _make_entry(AuditLevel.MINIMAL).to_dict()
        assert d["vcp_audit_version"] == "1.1"

    def test_to_json_roundtrip(self) -> None:
        import json

        entry = _make_entry(AuditLevel.STANDARD)
        parsed = json.loads(entry.to_json())
        assert parsed["verification"]["result"] == "VALID"


# ---------------------------------------------------------------------------
# GDPR log purge
# ---------------------------------------------------------------------------


class TestGDPRPurge:
    def test_purge_removes_matching_entries(self) -> None:
        logger = AuditLogger(level=AuditLevel.STANDARD)
        logger._entries.append(_make_entry(session_id_hash=_hash_for_privacy("user-A")))
        logger._entries.append(_make_entry(session_id_hash=_hash_for_privacy("user-B")))
        logger._entries.append(_make_entry(session_id_hash=_hash_for_privacy("user-A")))

        tombstone = logger.purge_by_session("user-A")
        assert tombstone["entries_removed"] == 2
        assert "purge_id" in tombstone
        assert "timestamp" in tombstone
        assert tombstone["scope"] == "in-memory audit entries only"
        assert len(logger._entries) == 1
        assert logger._entries[0].session_id_hash == _hash_for_privacy("user-B")

    def test_purge_returns_zero_if_no_match(self) -> None:
        logger = AuditLogger(level=AuditLevel.STANDARD)
        logger._entries.append(_make_entry(session_id_hash=_hash_for_privacy("user-B")))

        tombstone = logger.purge_by_session("user-Z")
        assert tombstone["entries_removed"] == 0
        assert len(logger._entries) == 1

    def test_purge_on_empty_log(self) -> None:
        logger = AuditLogger(level=AuditLevel.STANDARD)
        tombstone = logger.purge_by_session("any")
        assert tombstone["entries_removed"] == 0


# ---------------------------------------------------------------------------
# Privacy filter audit event
# ---------------------------------------------------------------------------


class TestPrivacyFilterAudit:
    def test_log_privacy_filter_creates_entry(self) -> None:
        logger = AuditLogger(level=AuditLevel.STANDARD)
        entry = logger.log_privacy_filter(
            platform_id="guitar-app",
            session_id="sess-1",
            fields_shared=5,
            fields_withheld=3,
            constraint_flags_active=2,
        )
        assert entry.verification_result == "PRIVACY_FILTER"
        assert len(logger._entries) == 1

    def test_log_privacy_filter_records_counts_in_checks(self) -> None:
        logger = AuditLogger(level=AuditLevel.STANDARD)
        entry = logger.log_privacy_filter(
            platform_id="guitar-app",
            session_id="sess-1",
            fields_shared=5,
            fields_withheld=3,
            constraint_flags_active=2,
        )
        assert "shared:5" in entry.checks_passed
        assert "withheld:3" in entry.checks_passed
        assert "constraints:2" in entry.checks_passed
        assert "private_fields_exposed:0" in entry.checks_passed

    def test_log_privacy_filter_hashes_platform_id(self) -> None:
        logger = AuditLogger(level=AuditLevel.STANDARD)
        entry = logger.log_privacy_filter(
            platform_id="guitar-app",
            session_id="sess-1",
            fields_shared=5,
            fields_withheld=3,
            constraint_flags_active=2,
        )
        assert entry.bundle_id_hash == _hash_for_privacy("guitar-app")

    def test_log_privacy_filter_fires_callback(self) -> None:
        captured = []
        logger = AuditLogger(
            level=AuditLevel.STANDARD,
            log_callback=captured.append,
        )
        logger.log_privacy_filter(
            platform_id="p", session_id="s",
            fields_shared=1, fields_withheld=0, constraint_flags_active=0,
        )
        assert len(captured) == 1
        assert captured[0].verification_result == "PRIVACY_FILTER"


# ---------------------------------------------------------------------------
# Hash privacy helper
# ---------------------------------------------------------------------------


class TestHashForPrivacy:
    def test_deterministic(self) -> None:
        assert _hash_for_privacy("test") == _hash_for_privacy("test")

    def test_different_inputs_different_hashes(self) -> None:
        assert _hash_for_privacy("a") != _hash_for_privacy("b")

    def test_prefix_format(self) -> None:
        assert _hash_for_privacy("x").startswith("sha256:")

    def test_truncated_to_32_hex(self) -> None:
        h = _hash_for_privacy("x")
        hex_part = h.split(":")[1]
        assert len(hex_part) == 32
