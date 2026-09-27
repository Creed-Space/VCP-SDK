"""
Tests for vcp.audit — Amendment J privacy-preserving audit logging.

Verifies:
    - Audit tier boundaries (minimal/standard/full/diagnostic)
    - GDPR log purge (right to erasure)
    - Privacy filter audit events
"""

from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from vcp.audit import AuditEntry, AuditLevel, AuditLogger, _hash_for_privacy

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_entry(level: AuditLevel = AuditLevel.STANDARD, **kwargs) -> AuditEntry:
    """Create a test audit entry with sensible defaults."""
    defaults = dict(
        timestamp=datetime(2026, 1, 10, 12, 0, 0, tzinfo=timezone.utc),
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
        # RFC 3339 UTC with a single trailing Z that round-trips
        assert d["timestamp"].endswith("Z") and "+00:00" not in d["timestamp"]
        parsed = datetime.fromisoformat(d["timestamp"].replace("Z", "+00:00"))
        assert parsed == datetime(2026, 1, 10, 12, 0, 0, tzinfo=timezone.utc)

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


class TestAuditDefaultLevel:
    """VCP core audit §3.1 and Amendment J: ``minimal`` is the default level."""

    @staticmethod
    def _bundle() -> SimpleNamespace:
        manifest = SimpleNamespace(
            signature=SimpleNamespace(value="base64:" + "A" * 64),
            bundle=SimpleNamespace(id="bundle-1", content_hash="sha256:abc123", version="1.2.0"),
            issuer=SimpleNamespace(id="issuer-1"),
            budget=SimpleNamespace(token_count=500),
        )
        return SimpleNamespace(manifest=manifest, content="Constitution text " * 20)

    def test_logger_defaults_to_minimal(self) -> None:
        assert AuditLogger().level is AuditLevel.MINIMAL

    def test_entry_defaults_to_minimal(self) -> None:
        entry = _make_entry()
        entry_default = AuditEntry(
            **{k: v for k, v in entry.__dict__.items() if k != "audit_level"}
        )
        assert entry_default.audit_level is AuditLevel.MINIMAL

    def test_minimal_emits_exactly_the_minimal_fields(self) -> None:
        d = _make_entry(AuditLevel.MINIMAL).to_dict()
        assert d == {
            "vcp_audit_version": "1.1",
            "audit_level": "minimal",
            "verification": {"result": "VALID"},
            "bundle_ref": {
                "id_hash": _hash_for_privacy("bundle-1"),
                "content_hash": "sha256:abc123",
            },
        }

    def test_standard_includes_request_id(self) -> None:
        assert "request_id" not in _make_entry(AuditLevel.MINIMAL).to_dict()
        assert "request_id" in _make_entry(AuditLevel.STANDARD).to_dict()

    def test_default_logger_emits_no_session_or_timing_data(self) -> None:
        from vcp.types import VerificationResult

        logger = AuditLogger()
        entry = logger.log_verification(
            self._bundle(),
            VerificationResult.VALID,
            session_id="sess-1",
            request_id="req-1",
            duration_ms=12,
        )
        assert entry.audit_level is AuditLevel.MINIMAL
        assert entry.duration_ms is None
        assert entry.token_count is None
        assert entry.content_preview is None
        d = entry.to_dict()
        assert set(d) == {"vcp_audit_version", "audit_level", "verification", "bundle_ref"}
        assert set(d["verification"]) == {"result"}
        assert set(d["bundle_ref"]) == {"id_hash", "content_hash"}

    def test_standard_is_opt_in(self) -> None:
        from vcp.types import VerificationResult

        logger = AuditLogger(level=AuditLevel.STANDARD)
        d = logger.log_verification(
            self._bundle(), VerificationResult.VALID, session_id="sess-1"
        ).to_dict()
        assert d["audit_level"] == "standard"
        assert "session_id_hash" in d
        assert "timestamp" in d


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
        assert tombstone["scope"] == "in-memory audit entries + tracked exported JSON files"
        assert tombstone["external_sink_results"] == []
        # Tombstone must NOT contain session_id_hash (GDPR: the hash itself is PII)
        assert "session_id_hash" not in tombstone
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

    def test_purge_scrubs_exported_json_file(self, tmp_path) -> None:
        logger = AuditLogger(level=AuditLevel.STANDARD)
        hash_a = _hash_for_privacy("user-A")
        hash_b = _hash_for_privacy("user-B")
        logger._entries.append(_make_entry(session_id_hash=hash_a))
        logger._entries.append(_make_entry(session_id_hash=hash_b))
        logger._entries.append(_make_entry(session_id_hash=hash_a))

        export_path = str(tmp_path / "audit_export.json")
        logger.export_json(export_path)

        # Clear in-memory so we test file-only purge
        logger._entries.clear()
        tombstone = logger.purge_by_session("user-A")

        assert tombstone["entries_removed"] == 0  # already cleared
        assert tombstone["file_entries_removed"] == 2
        assert export_path in tombstone["files_purged"]

        import json

        with open(export_path) as f:
            data = json.load(f)
        remaining = data["entries"]
        assert len(remaining) == 1
        # Remaining entry should be user-B (at STANDARD+, session_id_hash is present)
        assert remaining[0].get("session_id_hash") == hash_b

    def test_export_json_tracks_path(self, tmp_path) -> None:
        logger = AuditLogger(level=AuditLevel.STANDARD)
        p = str(tmp_path / "out.json")
        logger.export_json(p)
        assert p in logger._exported_paths

    def test_purge_handles_missing_export_file(self, tmp_path) -> None:
        logger = AuditLogger(level=AuditLevel.STANDARD)
        logger._exported_paths.append(str(tmp_path / "gone.json"))
        tombstone = logger.purge_by_session("user-X")
        assert tombstone["file_entries_removed"] == 0

    def test_purge_handler_called_with_hash_and_id(self) -> None:
        calls = []

        def handler(session_hash: str, purge_id: str) -> dict:
            calls.append((session_hash, purge_id))
            return {"redis_keys_deleted": 3}

        logger = AuditLogger(level=AuditLevel.STANDARD)
        logger.register_purge_handler(handler)
        logger._entries.append(_make_entry(session_id_hash=_hash_for_privacy("user-A")))

        tombstone = logger.purge_by_session("user-A")

        assert len(calls) == 1
        assert calls[0][0] == _hash_for_privacy("user-A")
        assert calls[0][1] == tombstone["purge_id"]
        assert tombstone["external_sink_results"] == [{"redis_keys_deleted": 3}]
        assert "1 external sink(s)" in tombstone["scope"]

    def test_purge_handler_exception_does_not_crash(self) -> None:
        def bad_handler(session_hash: str, purge_id: str) -> dict:
            raise RuntimeError("redis down")

        logger = AuditLogger(level=AuditLevel.STANDARD)
        logger.register_purge_handler(bad_handler)

        tombstone = logger.purge_by_session("user-A")
        assert len(tombstone["external_sink_results"]) == 1
        assert "error" in tombstone["external_sink_results"][0]

    def test_warns_when_callback_set_without_purge_handler(self, caplog) -> None:
        import logging as _logging

        captured = []
        logger = AuditLogger(
            level=AuditLevel.STANDARD,
            log_callback=captured.append,
        )
        logger._entries.append(_make_entry(session_id_hash=_hash_for_privacy("user-A")))

        with caplog.at_level(_logging.WARNING, logger="vcp.audit"):
            logger.purge_by_session("user-A")

        assert any("no purge handlers are registered" in r.message for r in caplog.records)

    def test_no_warning_when_purge_handler_registered(self, caplog) -> None:
        import logging as _logging

        logger = AuditLogger(
            level=AuditLevel.STANDARD,
            log_callback=lambda _: None,
        )
        logger.register_purge_handler(lambda h, p: {"ok": True})

        with caplog.at_level(_logging.WARNING, logger="vcp.audit"):
            logger.purge_by_session("user-A")

        assert not any("no purge handlers" in r.message for r in caplog.records)


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
            platform_id="p",
            session_id="s",
            fields_shared=1,
            fields_withheld=0,
            constraint_flags_active=0,
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
        assert _hash_for_privacy("x").startswith("hmac-sha256:")

    def test_truncated_to_32_hex(self) -> None:
        h = _hash_for_privacy("x")
        hex_part = h.split(":")[1]
        assert len(hex_part) == 32
        assert len(h) == 44
        assert hex_part == hex_part.lower()

    def test_spec_vectors(self) -> None:
        """VCP core audit §6.2 test vectors, K_audit = bytes 00..1f."""
        key = bytes(range(32))
        assert _hash_for_privacy("session-123", key) == (
            "hmac-sha256:155ac01a3ea3ea086d4b81a0927566d1"
        )
        assert _hash_for_privacy("bundle:family.safe.guide@1.2.0", key) == (
            "hmac-sha256:f5ac6afff147efb0a91ea7e2476025fd"
        )

    def test_value_is_not_normalized(self) -> None:
        key = bytes(range(32))
        assert _hash_for_privacy("Session-123", key) != _hash_for_privacy("session-123", key)
        assert _hash_for_privacy(" session-123", key) != _hash_for_privacy("session-123", key)

    def test_is_hmac_not_salted_sha256(self) -> None:
        import hashlib

        key = bytes(range(32))
        salted = hashlib.sha256(key + b"session-123").hexdigest()[:32]
        assert _hash_for_privacy("session-123", key) != f"hmac-sha256:{salted}"


class TestAuditKeySource:
    """VCP core audit §6.2 key sourcing."""

    def test_operator_key_is_used(self) -> None:
        key = bytes(range(32))
        logger = AuditLogger(audit_key=key)
        assert logger._hash("session-123") == "hmac-sha256:155ac01a3ea3ea086d4b81a0927566d1"

    def test_text_key_is_utf8_encoded(self) -> None:
        text = "k" * 32
        logger = AuditLogger(audit_key=text)
        assert logger._hash("v") == _hash_for_privacy("v", text.encode("utf-8"))

    def test_short_keys_are_rejected(self) -> None:
        with pytest.raises(ValueError, match="at least 32 bytes"):
            AuditLogger(audit_key=b"x" * 31)
        with pytest.raises(ValueError, match="at least 32 bytes"):
            AuditLogger(audit_key="short")

    def test_default_key_is_per_process_random(self) -> None:
        from vcp import audit

        assert len(audit._PROCESS_AUDIT_KEY) == 32
        assert AuditLogger()._hash("v") == _hash_for_privacy("v")
        assert AuditLogger(audit_key=bytes(range(32)))._hash("v") != _hash_for_privacy("v")

    def test_two_loggers_with_same_operator_key_agree(self) -> None:
        key = bytes(range(32, 64))
        assert AuditLogger(audit_key=key)._hash("s") == AuditLogger(audit_key=key)._hash("s")

    def test_privacy_salt_is_a_deprecated_alias(self) -> None:
        key = bytes(range(32))
        with pytest.warns(DeprecationWarning, match="audit_key"):
            logger = AuditLogger(privacy_salt=key)
        assert logger._hash("session-123") == "hmac-sha256:155ac01a3ea3ea086d4b81a0927566d1"
        with pytest.warns(DeprecationWarning), pytest.raises(ValueError):
            AuditLogger(privacy_salt=b"short")
        with pytest.raises(TypeError):
            AuditLogger(privacy_salt=key, audit_key=key)


class TestCallbackRedaction:
    """log_callback receives only the fields permitted at the level."""

    @staticmethod
    def _log(level: AuditLevel) -> tuple[AuditEntry, AuditEntry]:
        from vcp.types import VerificationResult

        captured: list[AuditEntry] = []
        logger = AuditLogger(level=level, log_callback=captured.append)
        returned = logger.log_verification(
            TestAuditDefaultLevel._bundle(),
            VerificationResult.VALID,
            session_id="sess-1",
            request_id="req-1",
            duration_ms=12,
        )
        assert len(captured) == 1
        return captured[0], returned

    @pytest.mark.parametrize("level", list(AuditLevel))
    def test_callback_matches_serialized_output(self, level: AuditLevel) -> None:
        seen, returned = self._log(level)
        assert seen == returned
        emitted = seen.to_dict()
        permitted = {
            "timestamp": "timestamp" in emitted,
            "session_id_hash": "session_id_hash" in emitted,
            "checks_passed": "checks_passed" in emitted["verification"],
            "issuer_hash": "issuer_hash" in emitted["bundle_ref"],
            "version": "version" in emitted["bundle_ref"],
            "manifest_signature": "manifest_signature" in emitted,
            "request_id": "request_id" in emitted,
            "duration_ms": "duration_ms" in emitted["verification"],
            "token_count": "token_count" in emitted["bundle_ref"],
            "content_preview": "content_preview" in emitted["bundle_ref"],
        }
        for field_name, is_emitted in permitted.items():
            assert (getattr(seen, field_name) is not None) == is_emitted, field_name

    def test_minimal_callback_has_no_session_data(self) -> None:
        seen, _ = self._log(AuditLevel.MINIMAL)
        assert seen.timestamp is None
        assert seen.session_id_hash is None
        assert seen.issuer_hash is None
        assert seen.request_id is None
        assert seen.manifest_signature is None
        assert seen.checks_passed is None
        assert seen.bundle_id_hash.startswith("hmac-sha256:")

    def test_get_entries_is_redacted_but_purge_still_works(self) -> None:
        from vcp.types import VerificationResult

        logger = AuditLogger()
        logger.log_verification(
            TestAuditDefaultLevel._bundle(), VerificationResult.VALID, session_id="sess-1"
        )
        assert all(entry.session_id_hash is None for entry in logger.get_entries())
        assert logger.purge_by_session("sess-1")["entries_removed"] == 1

    def test_purge_tombstone_callback_is_redacted(self) -> None:
        captured: list[AuditEntry] = []
        logger = AuditLogger(log_callback=captured.append)
        logger.register_purge_handler(lambda _hash, _purge: {"ok": True})
        logger._entries.append(_make_entry(session_id_hash=_hash_for_privacy("user-A")))
        logger.purge_by_session("user-A")
        tombstone = [e for e in captured if e.verification_result == "PURGE_TOMBSTONE"]
        assert tombstone and tombstone[0].session_id_hash is None


class TestSinceFilterPrivacy:
    """get_entries(since=...) must not reveal timing below the standard level."""

    def test_since_is_rejected_at_minimal(self) -> None:
        logger = AuditLogger()
        logger._entries.append(_make_entry(AuditLevel.MINIMAL))
        with pytest.raises(ValueError, match="minimal"):
            logger.get_entries(since=datetime(2020, 1, 1, tzinfo=timezone.utc))
        assert len(logger.get_entries()) == 1

    def test_since_skips_entries_below_standard(self) -> None:
        logger = AuditLogger(level=AuditLevel.STANDARD)
        logger._entries.append(_make_entry(AuditLevel.MINIMAL))
        logger._entries.append(_make_entry(AuditLevel.STANDARD))
        entries = logger.get_entries(since=datetime(2020, 1, 1, tzinfo=timezone.utc))
        assert [e.audit_level for e in entries] == [AuditLevel.STANDARD]
        assert entries[0].timestamp is not None
        later = logger.get_entries(since=datetime(2030, 1, 1, tzinfo=timezone.utc))
        assert later == []
