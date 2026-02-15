"""
Tests for VCP Revocation Checking Module.

Covers: online endpoint checks, CRL checks, SSRF protection,
caching, timeout handling, malformed responses, and orchestrator integration.
"""

from __future__ import annotations

import json
import socket
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from vcp.revocation import (
    MAX_RESPONSE_BYTES,
    RevocationChecker,
    RevocationError,
    RevocationStatus,
    _fetch_json,
    _is_private_ip,
    validate_uri,
)


# ---------------------------------------------------------------------------
# Helpers: minimal Manifest stub for testing
# ---------------------------------------------------------------------------


@dataclass
class _StubTimestamps:
    jti: str = "550e8400-e29b-41d4-a716-446655440000"
    iat: datetime = field(default_factory=lambda: datetime(2026, 1, 10))
    nbf: datetime = field(default_factory=lambda: datetime(2026, 1, 10))
    exp: datetime = field(default_factory=lambda: datetime(2026, 1, 17))


@dataclass
class _StubManifest:
    timestamps: _StubTimestamps = field(default_factory=_StubTimestamps)
    revocation: dict[str, Any] | None = None


def _manifest(
    jti: str = "550e8400-e29b-41d4-a716-446655440000",
    check_uri: str | None = None,
    crl_uri: str | None = None,
) -> _StubManifest:
    revocation: dict[str, str] | None = None
    if check_uri or crl_uri:
        revocation = {}
        if check_uri:
            revocation["check_uri"] = check_uri
        if crl_uri:
            revocation["crl_uri"] = crl_uri
    return _StubManifest(
        timestamps=_StubTimestamps(jti=jti),
        revocation=revocation,
    )


def _crl_response(
    revoked_entries: list[dict[str, str]] | None = None,
    next_update: str | None = None,
) -> dict[str, Any]:
    """Build a CRL JSON response body."""
    return {
        "issuer": "creed.space",
        "updated_at": "2026-02-15T10:00:00Z",
        "next_update": next_update or "2026-02-16T10:00:00Z",
        "revoked": revoked_entries or [],
    }


# ---------------------------------------------------------------------------
# SSRF / URI validation
# ---------------------------------------------------------------------------


class TestValidateUri:
    """Tests for the SSRF-safe URI validator."""

    def test_rejects_file_scheme(self) -> None:
        ok, reason = validate_uri("file:///etc/passwd")
        assert not ok
        assert "scheme" in reason.lower()

    def test_rejects_ftp_scheme(self) -> None:
        ok, reason = validate_uri("ftp://example.com/data")
        assert not ok
        assert "scheme" in reason.lower()

    def test_rejects_no_hostname(self) -> None:
        ok, _ = validate_uri("http://")
        assert not ok

    @patch("vcp.revocation.socket.getaddrinfo")
    def test_rejects_private_ip_10(self, mock_gai: MagicMock) -> None:
        mock_gai.return_value = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("10.0.0.1", 443)),
        ]
        ok, reason = validate_uri("https://internal.example.com/revoked")
        assert not ok
        assert "private" in reason.lower() or "reserved" in reason.lower()

    @patch("vcp.revocation.socket.getaddrinfo")
    def test_rejects_loopback_127(self, mock_gai: MagicMock) -> None:
        mock_gai.return_value = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 443)),
        ]
        ok, reason = validate_uri("https://localhost/revoked")
        assert not ok
        assert "private" in reason.lower() or "reserved" in reason.lower()

    @patch("vcp.revocation.socket.getaddrinfo")
    def test_rejects_ipv6_loopback(self, mock_gai: MagicMock) -> None:
        mock_gai.return_value = [
            (socket.AF_INET6, socket.SOCK_STREAM, 6, "", ("::1", 443, 0, 0)),
        ]
        ok, reason = validate_uri("https://localhost/revoked")
        assert not ok
        assert "private" in reason.lower() or "reserved" in reason.lower()

    @patch("vcp.revocation.socket.getaddrinfo")
    def test_rejects_link_local_169_254(self, mock_gai: MagicMock) -> None:
        mock_gai.return_value = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("169.254.1.1", 443)),
        ]
        ok, reason = validate_uri("https://metadata.example.com/revoked")
        assert not ok
        assert "private" in reason.lower() or "reserved" in reason.lower()

    @patch("vcp.revocation.socket.getaddrinfo")
    def test_rejects_172_16_private(self, mock_gai: MagicMock) -> None:
        mock_gai.return_value = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("172.16.0.1", 443)),
        ]
        ok, reason = validate_uri("https://internal.local/revoked")
        assert not ok

    @patch("vcp.revocation.socket.getaddrinfo")
    def test_rejects_192_168_private(self, mock_gai: MagicMock) -> None:
        mock_gai.return_value = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("192.168.1.1", 443)),
        ]
        ok, reason = validate_uri("https://router.local/revoked")
        assert not ok

    @patch("vcp.revocation.socket.getaddrinfo")
    def test_accepts_public_ip(self, mock_gai: MagicMock) -> None:
        mock_gai.return_value = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443)),
        ]
        ok, reason = validate_uri("https://creed.space/api/v1/revoked")
        assert ok
        assert reason == "OK"

    def test_rejects_non_standard_port(self) -> None:
        with patch("vcp.revocation.socket.getaddrinfo") as mock_gai:
            mock_gai.return_value = [
                (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 8080)),
            ]
            ok, reason = validate_uri("https://creed.space:8080/revoked")
            assert not ok
            assert "port" in reason.lower()

    def test_accepts_non_standard_port_when_allowlisted(self) -> None:
        with patch("vcp.revocation.socket.getaddrinfo") as mock_gai:
            mock_gai.return_value = [
                (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 8080)),
            ]
            ok, reason = validate_uri(
                "https://creed.space:8080/revoked",
                allowed_ports={8080},
            )
            assert ok

    @patch("vcp.revocation.socket.getaddrinfo", side_effect=socket.gaierror("DNS fail"))
    def test_rejects_unresolvable_hostname(self, mock_gai: MagicMock) -> None:
        ok, reason = validate_uri("https://nonexistent.invalid/revoked")
        assert not ok
        assert "dns" in reason.lower() or "resolution" in reason.lower()


class TestIsPrivateIp:
    """Direct tests for _is_private_ip helper."""

    @pytest.mark.parametrize(
        "ip",
        ["127.0.0.1", "10.0.0.1", "172.16.0.1", "192.168.1.1", "169.254.0.1", "::1"],
    )
    def test_private_ips(self, ip: str) -> None:
        assert _is_private_ip(ip) is True

    @pytest.mark.parametrize(
        "ip",
        ["93.184.216.34", "8.8.8.8", "1.1.1.1", "2606:4700::1"],
    )
    def test_public_ips(self, ip: str) -> None:
        assert _is_private_ip(ip) is False

    def test_unparseable_ip(self) -> None:
        assert _is_private_ip("not-an-ip") is True


# ---------------------------------------------------------------------------
# RevocationChecker: online endpoint
# ---------------------------------------------------------------------------


class TestOnlineCheck:
    """Tests for check_uri (online revocation endpoint)."""

    @patch("vcp.revocation.validate_uri", return_value=(True, "OK"))
    @patch("vcp.revocation._fetch_json")
    def test_not_revoked_online(
        self, mock_fetch: MagicMock, mock_validate: MagicMock
    ) -> None:
        mock_fetch.return_value = {"revoked": False}
        checker = RevocationChecker(cache_ttl=60)
        manifest = _manifest(check_uri="https://creed.space/api/v1/revoked")
        result = checker.check(manifest)
        assert result.revoked is False
        assert result.reason is None

    @patch("vcp.revocation.validate_uri", return_value=(True, "OK"))
    @patch("vcp.revocation._fetch_json")
    def test_revoked_online(
        self, mock_fetch: MagicMock, mock_validate: MagicMock
    ) -> None:
        mock_fetch.return_value = {
            "revoked": True,
            "reason": "key_compromise",
            "revoked_at": "2026-02-14T08:00:00Z",
        }
        checker = RevocationChecker(cache_ttl=60)
        manifest = _manifest(check_uri="https://creed.space/api/v1/revoked")
        result = checker.check(manifest)
        assert result.revoked is True
        assert result.reason == "key_compromise"
        assert result.revoked_at == "2026-02-14T08:00:00Z"

    @patch("vcp.revocation.validate_uri", return_value=(True, "OK"))
    @patch("vcp.revocation._fetch_json")
    def test_online_cache_hit(
        self, mock_fetch: MagicMock, mock_validate: MagicMock
    ) -> None:
        mock_fetch.return_value = {"revoked": False}
        checker = RevocationChecker(cache_ttl=300)
        manifest = _manifest(check_uri="https://creed.space/api/v1/revoked")

        # First call fetches
        result1 = checker.check(manifest)
        assert result1.revoked is False
        assert mock_fetch.call_count == 1

        # Second call should hit cache
        result2 = checker.check(manifest)
        assert result2.revoked is False
        assert mock_fetch.call_count == 1  # NOT incremented


# ---------------------------------------------------------------------------
# RevocationChecker: CRL
# ---------------------------------------------------------------------------


class TestCRLCheck:
    """Tests for crl_uri (Certificate Revocation List)."""

    @patch("vcp.revocation.validate_uri", return_value=(True, "OK"))
    @patch("vcp.revocation._fetch_json")
    def test_revoked_via_crl(
        self, mock_fetch: MagicMock, mock_validate: MagicMock
    ) -> None:
        target_jti = "550e8400-e29b-41d4-a716-446655440000"
        mock_fetch.return_value = _crl_response(
            revoked_entries=[
                {
                    "jti": target_jti,
                    "revoked_at": "2026-02-14T08:00:00Z",
                    "reason": "key_compromise",
                }
            ]
        )
        checker = RevocationChecker(cache_ttl=60)
        manifest = _manifest(jti=target_jti, crl_uri="https://creed.space/crl/2026.json")
        result = checker.check(manifest)
        assert result.revoked is True
        assert result.reason == "key_compromise"

    @patch("vcp.revocation.validate_uri", return_value=(True, "OK"))
    @patch("vcp.revocation._fetch_json")
    def test_not_revoked_via_crl(
        self, mock_fetch: MagicMock, mock_validate: MagicMock
    ) -> None:
        mock_fetch.return_value = _crl_response(
            revoked_entries=[
                {
                    "jti": "other-jti-not-ours",
                    "revoked_at": "2026-02-14T08:00:00Z",
                    "reason": "superseded",
                }
            ]
        )
        checker = RevocationChecker(cache_ttl=60)
        manifest = _manifest(crl_uri="https://creed.space/crl/2026.json")
        result = checker.check(manifest)
        assert result.revoked is False

    @patch("vcp.revocation.validate_uri", return_value=(True, "OK"))
    @patch("vcp.revocation._fetch_json")
    def test_crl_cache_hit(
        self, mock_fetch: MagicMock, mock_validate: MagicMock
    ) -> None:
        mock_fetch.return_value = _crl_response(revoked_entries=[])
        checker = RevocationChecker(cache_ttl=300)
        manifest = _manifest(crl_uri="https://creed.space/crl/2026.json")

        checker.check(manifest)
        assert mock_fetch.call_count == 1

        # Second call should use cached CRL
        checker.check(manifest)
        assert mock_fetch.call_count == 1

    @patch("vcp.revocation.validate_uri", return_value=(True, "OK"))
    @patch("vcp.revocation._fetch_json")
    def test_crl_expired_warns_but_proceeds(
        self, mock_fetch: MagicMock, mock_validate: MagicMock
    ) -> None:
        """An expired CRL logs a warning but still returns its data."""
        mock_fetch.return_value = _crl_response(
            revoked_entries=[],
            next_update="2020-01-01T00:00:00Z",  # long expired
        )
        checker = RevocationChecker(cache_ttl=60)
        manifest = _manifest(crl_uri="https://creed.space/crl/2026.json")
        result = checker.check(manifest)
        # Not revoked -- the CRL had no matching entry
        assert result.revoked is False


# ---------------------------------------------------------------------------
# Fallback behaviour
# ---------------------------------------------------------------------------


class TestFallbackBehaviour:
    """Tests for fallback from online to CRL and missing URIs."""

    def test_no_revocation_uris_returns_not_revoked(self) -> None:
        checker = RevocationChecker()
        manifest = _manifest()  # no revocation URIs
        result = checker.check(manifest)
        assert result.revoked is False

    @patch("vcp.revocation.validate_uri", return_value=(True, "OK"))
    @patch("vcp.revocation._fetch_json")
    def test_online_fails_falls_back_to_crl(
        self, mock_fetch: MagicMock, mock_validate: MagicMock
    ) -> None:
        """If online check errors, CRL should be tried."""
        target_jti = "550e8400-e29b-41d4-a716-446655440000"

        def fetch_side_effect(uri: str, **kwargs: Any) -> dict[str, Any]:
            if "revoked?" in uri or "jti=" in uri:
                raise RevocationError("Server error 500")
            # CRL fetch
            return _crl_response(
                revoked_entries=[
                    {"jti": target_jti, "revoked_at": "2026-02-14T08:00:00Z", "reason": "superseded"}
                ]
            )

        mock_fetch.side_effect = fetch_side_effect
        checker = RevocationChecker(cache_ttl=60)
        manifest = _manifest(
            jti=target_jti,
            check_uri="https://creed.space/api/v1/revoked",
            crl_uri="https://creed.space/crl/2026.json",
        )
        result = checker.check(manifest)
        assert result.revoked is True
        assert result.reason == "superseded"


# ---------------------------------------------------------------------------
# SSRF rejection through RevocationChecker
# ---------------------------------------------------------------------------


class TestSSRFThroughChecker:
    """End-to-end SSRF rejection when used via RevocationChecker."""

    @patch("vcp.revocation.socket.getaddrinfo")
    def test_ssrf_private_ip_online(self, mock_gai: MagicMock) -> None:
        mock_gai.return_value = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("10.0.0.1", 443)),
        ]
        checker = RevocationChecker(cache_ttl=60)
        # Only check_uri, no CRL fallback
        manifest = _manifest(check_uri="https://internal.corp/revoked")
        result = checker.check(manifest)
        # Should NOT be revoked -- the check failed, treated as not-revoked
        assert result.revoked is False

    @patch("vcp.revocation.socket.getaddrinfo")
    def test_ssrf_loopback_online(self, mock_gai: MagicMock) -> None:
        mock_gai.return_value = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 443)),
        ]
        checker = RevocationChecker(cache_ttl=60)
        manifest = _manifest(check_uri="https://localhost/revoked")
        result = checker.check(manifest)
        assert result.revoked is False

    @patch("vcp.revocation.socket.getaddrinfo")
    def test_ssrf_ipv6_loopback_online(self, mock_gai: MagicMock) -> None:
        mock_gai.return_value = [
            (socket.AF_INET6, socket.SOCK_STREAM, 6, "", ("::1", 443, 0, 0)),
        ]
        checker = RevocationChecker(cache_ttl=60)
        manifest = _manifest(check_uri="https://localhost/revoked")
        result = checker.check(manifest)
        assert result.revoked is False

    def test_ssrf_file_scheme(self) -> None:
        checker = RevocationChecker(cache_ttl=60)
        manifest = _manifest(check_uri="file:///etc/passwd")
        result = checker.check(manifest)
        assert result.revoked is False


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


class TestErrorHandling:
    """Tests for timeout, malformed response, and oversize response."""

    @patch("vcp.revocation.validate_uri", return_value=(True, "OK"))
    @patch("vcp.revocation._fetch_json", side_effect=RevocationError("Request timed out"))
    def test_timeout_handling(
        self, mock_fetch: MagicMock, mock_validate: MagicMock
    ) -> None:
        checker = RevocationChecker(cache_ttl=60, timeout=0.001)
        manifest = _manifest(check_uri="https://slow.example.com/revoked")
        result = checker.check(manifest)
        # Timeout fails gracefully -- not revoked
        assert result.revoked is False

    @patch("vcp.revocation.validate_uri", return_value=(True, "OK"))
    @patch(
        "vcp.revocation._fetch_json",
        side_effect=RevocationError("Invalid JSON response"),
    )
    def test_malformed_json_response(
        self, mock_fetch: MagicMock, mock_validate: MagicMock
    ) -> None:
        checker = RevocationChecker(cache_ttl=60)
        manifest = _manifest(check_uri="https://broken.example.com/revoked")
        result = checker.check(manifest)
        assert result.revoked is False

    @patch("vcp.revocation.validate_uri", return_value=(True, "OK"))
    @patch(
        "vcp.revocation._fetch_json",
        side_effect=RevocationError(
            f"Response body exceeds limit of {MAX_RESPONSE_BYTES} bytes"
        ),
    )
    def test_response_too_large(
        self, mock_fetch: MagicMock, mock_validate: MagicMock
    ) -> None:
        checker = RevocationChecker(cache_ttl=60)
        manifest = _manifest(check_uri="https://large.example.com/revoked")
        result = checker.check(manifest)
        assert result.revoked is False


# ---------------------------------------------------------------------------
# RevocationStatus dataclass
# ---------------------------------------------------------------------------


class TestRevocationStatus:
    """Basic tests for the RevocationStatus dataclass."""

    def test_defaults(self) -> None:
        status = RevocationStatus(revoked=False)
        assert status.revoked is False
        assert status.reason is None
        assert status.revoked_at is None

    def test_revoked_with_details(self) -> None:
        status = RevocationStatus(
            revoked=True,
            reason="key_compromise",
            revoked_at="2026-02-14T08:00:00Z",
        )
        assert status.revoked is True
        assert status.reason == "key_compromise"
        assert status.revoked_at == "2026-02-14T08:00:00Z"


# ---------------------------------------------------------------------------
# Cache expiration
# ---------------------------------------------------------------------------


class TestCacheExpiration:
    """Verify cache entries expire after TTL."""

    @patch("vcp.revocation.validate_uri", return_value=(True, "OK"))
    @patch("vcp.revocation._fetch_json")
    def test_online_cache_expires(
        self, mock_fetch: MagicMock, mock_validate: MagicMock
    ) -> None:
        mock_fetch.return_value = {"revoked": False}
        checker = RevocationChecker(cache_ttl=1)  # 1 second TTL
        manifest = _manifest(check_uri="https://creed.space/api/v1/revoked")

        checker.check(manifest)
        assert mock_fetch.call_count == 1

        # Manually expire the cache by manipulating the entry
        for entry in checker._cache.values():
            entry.expires_at = time.monotonic() - 1

        checker.check(manifest)
        assert mock_fetch.call_count == 2  # Fetched again after expiry

    @patch("vcp.revocation.validate_uri", return_value=(True, "OK"))
    @patch("vcp.revocation._fetch_json")
    def test_crl_cache_expires(
        self, mock_fetch: MagicMock, mock_validate: MagicMock
    ) -> None:
        mock_fetch.return_value = _crl_response(revoked_entries=[])
        checker = RevocationChecker(cache_ttl=1)
        manifest = _manifest(crl_uri="https://creed.space/crl/2026.json")

        checker.check(manifest)
        assert mock_fetch.call_count == 1

        for entry in checker._crl_cache.values():
            entry.expires_at = time.monotonic() - 1

        checker.check(manifest)
        assert mock_fetch.call_count == 2

    def test_clear_cache(self) -> None:
        checker = RevocationChecker()
        # Manually insert cache entries
        from vcp.revocation import _CacheEntry

        checker._cache["test"] = _CacheEntry(
            value=RevocationStatus(revoked=False),
            expires_at=time.monotonic() + 9999,
        )
        checker._crl_cache["test"] = _CacheEntry(
            value={},
            expires_at=time.monotonic() + 9999,
        )

        checker.clear_cache()
        assert len(checker._cache) == 0
        assert len(checker._crl_cache) == 0


# ---------------------------------------------------------------------------
# Orchestrator integration
# ---------------------------------------------------------------------------


class TestOrchestratorIntegration:
    """Verify RevocationChecker integrates with the Orchestrator."""

    def test_orchestrator_accepts_revocation_checker_param(self) -> None:
        """Orchestrator __init__ should accept revocation_checker kwarg."""
        from vcp.orchestrator import Orchestrator
        from vcp.trust import TrustConfig

        config = TrustConfig()
        checker = RevocationChecker()
        orch = Orchestrator(
            trust_config=config,
            revocation_checker=checker,
        )
        assert orch.revocation_checker is checker

    def test_orchestrator_defaults_to_no_checker(self) -> None:
        from vcp.orchestrator import Orchestrator
        from vcp.trust import TrustConfig

        orch = Orchestrator(trust_config=TrustConfig())
        assert orch.revocation_checker is None

    def test_revocation_exports(self) -> None:
        """RevocationChecker and RevocationStatus should be importable from vcp."""
        from vcp import RevocationChecker as RC
        from vcp import RevocationError as RE
        from vcp import RevocationStatus as RS

        assert RC is RevocationChecker
        assert RS is RevocationStatus
        assert RE is RevocationError
