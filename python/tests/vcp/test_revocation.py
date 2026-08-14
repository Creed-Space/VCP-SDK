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
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from vcp.revocation import (
    MAX_RESPONSE_BYTES,
    MAX_RESPONSE_HEADER_BYTES,
    MAX_RESPONSE_HEADERS,
    RevocationChecker,
    RevocationDecision,
    RevocationError,
    RevocationStatus,
    _fetch_json,
    _is_private_ip,
    _PinnedHTTPSConnection,
    validate_uri,
)


def _conformance_fixture(name: str) -> Path:
    """Locate a repository conformance fixture from normal or copied test trees."""
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "conformance" / "security" / name
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(f"Could not locate conformance/security/{name}")


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
class _StubIssuer:
    id: str = "creed.space"


@dataclass
class _StubManifest:
    timestamps: _StubTimestamps = field(default_factory=_StubTimestamps)
    issuer: _StubIssuer = field(default_factory=_StubIssuer)
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
    now = datetime.now(timezone.utc)
    return {
        "issuer": "creed.space",
        "updated_at": now.isoformat().replace("+00:00", "Z"),
        "next_update": next_update or (now + timedelta(hours=1)).isoformat().replace("+00:00", "Z"),
        "revoked": revoked_entries or [],
    }


def _online_response(
    *,
    revoked: bool = False,
    jti: str = "550e8400-e29b-41d4-a716-446655440000",
    issuer: str = "creed.space",
    reason: str | None = None,
    revoked_at: str | None = None,
) -> dict[str, Any]:
    return {
        "revoked": revoked,
        "jti": jti,
        "issuer": issuer,
        "reason": reason,
        "revoked_at": revoked_at,
    }


def _assert_unavailable(status: RevocationStatus) -> None:
    assert status.revoked is False
    assert status.decision is RevocationDecision.UNAVAILABLE
    assert status.should_reject
    assert status.reason == "revocation_status_unavailable"


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

    def test_rejects_plain_http(self) -> None:
        ok, reason = validate_uri("http://example.com/revoked")
        assert not ok
        assert "https" in reason.lower()

    def test_rejects_no_hostname(self) -> None:
        ok, _ = validate_uri("http://")
        assert not ok

    def test_rejects_embedded_credentials(self) -> None:
        ok, reason = validate_uri("https://user:secret@example.com/revoked")
        assert not ok
        assert "credentials" in reason.lower()

    def test_rejects_invalid_port(self) -> None:
        ok, reason = validate_uri("https://example.com:not-a-port/revoked")
        assert not ok
        assert "port" in reason.lower()

    def test_rejects_http_default_port_for_https(self) -> None:
        ok, reason = validate_uri("https://example.com:80/revoked")
        assert not ok
        assert "port" in reason.lower()

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

    @pytest.mark.parametrize("ip", ["192.0.2.1", "198.51.100.1", "203.0.113.1"])
    def test_reserved_documentation_ips(self, ip: str) -> None:
        assert _is_private_ip(ip) is True

    @pytest.mark.parametrize(
        "ip",
        [
            "64:ff9b::7f00:1",
            "64:ff9b:1::808:808",
            "::808:808",
        ],
    )
    def test_rejects_translation_and_compatible_ipv6(self, ip: str) -> None:
        assert _is_private_ip(ip) is True


def _mock_response(
    *,
    body: bytes = b'{"revoked": false}',
    status: int = 200,
    headers: list[tuple[str, str]] | None = None,
) -> MagicMock:
    response = MagicMock()
    response.status = status
    normalized = headers or [("Content-Type", "application/json")]
    response.getheaders.return_value = normalized
    by_name = {name.lower(): value for name, value in normalized}
    response.getheader.side_effect = lambda name: by_name.get(name.lower())
    response.read.return_value = body
    return response


class TestPinnedHttpsTransport:
    """Exercise the DNS-pinned TLS connection and bounded JSON transport."""

    @patch("vcp.revocation.ssl.create_default_context")
    def test_connection_preserves_tls_hostname_and_uses_pinned_ip(
        self, mock_context_factory: MagicMock
    ) -> None:
        context = mock_context_factory.return_value
        raw_socket = object()
        wrapped_socket = object()
        context.wrap_socket.return_value = wrapped_socket

        with patch("vcp.revocation.socket.create_connection", return_value=raw_socket) as connect:
            connection = _PinnedHTTPSConnection("status.example", 443, "93.184.216.34", 2.5)
            connection.connect()

        connect.assert_called_once_with(("93.184.216.34", 443), timeout=2.5)
        context.wrap_socket.assert_called_once_with(raw_socket, server_hostname="status.example")
        assert connection.sock is wrapped_socket

    @patch("vcp.revocation.validate_uri", return_value=(False, "blocked"))
    def test_fetch_rejects_uri_before_dns(self, mock_validate: MagicMock) -> None:
        with (
            patch("vcp.revocation.socket.getaddrinfo") as getaddrinfo,
            pytest.raises(RevocationError, match="SSRF protection: blocked"),
        ):
            _fetch_json("https://status.example/check")
        getaddrinfo.assert_not_called()

    @patch("vcp.revocation.validate_uri", return_value=(True, "OK"))
    @patch("vcp.revocation.socket.getaddrinfo", side_effect=socket.gaierror("no DNS"))
    def test_fetch_rejects_second_dns_failure(
        self, mock_getaddrinfo: MagicMock, mock_validate: MagicMock
    ) -> None:
        with pytest.raises(RevocationError, match="DNS resolution failed"):
            _fetch_json("https://status.example/check")

    @pytest.mark.parametrize(
        "addresses",
        [
            [],
            [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("10.0.0.1", 443))],
            [
                (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443)),
                (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 443)),
            ],
        ],
    )
    @patch("vcp.revocation.validate_uri", return_value=(True, "OK"))
    def test_fetch_rejects_empty_or_mixed_safety_resolution(
        self, mock_validate: MagicMock, addresses: list[tuple[Any, ...]]
    ) -> None:
        with (
            patch("vcp.revocation.socket.getaddrinfo", return_value=addresses),
            pytest.raises(RevocationError, match="unsafe address"),
        ):
            _fetch_json("https://status.example/check")

    @patch("vcp.revocation.validate_uri", return_value=(True, "OK"))
    def test_fetch_uses_sorted_pinned_addresses_and_exact_request_contract(
        self, mock_validate: MagicMock
    ) -> None:
        response = _mock_response(
            body=b'{"revoked": false, "jti": "abc"}',
            headers=[
                ("Content-Type", "application/problem+json; charset=utf-8"),
                ("Content-Encoding", "identity"),
                ("Content-Length", "32"),
            ],
        )
        connection = MagicMock()
        connection.getresponse.return_value = response
        addresses = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.35", 8443)),
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 8443)),
        ]
        with (
            patch("vcp.revocation.socket.getaddrinfo", return_value=addresses),
            patch("vcp.revocation._PinnedHTTPSConnection", return_value=connection) as factory,
        ):
            result = _fetch_json(
                "https://status.example:8443/check;v=1?jti=abc",
                timeout=3.5,
                allowed_ports={8443},
            )

        assert result == {"revoked": False, "jti": "abc"}
        factory.assert_called_once_with("status.example", 8443, "93.184.216.34", 3.5)
        connection.request.assert_called_once_with(
            "GET",
            "/check;v=1?jti=abc",
            headers={
                "Accept": "application/json",
                "Accept-Encoding": "identity",
                "Host": "status.example:8443",
                "User-Agent": "VCP-SDK/4.2",
            },
        )
        response.read.assert_called_once_with(MAX_RESPONSE_BYTES + 1)
        connection.close.assert_called_once_with()

    @patch("vcp.revocation.validate_uri", return_value=(True, "OK"))
    def test_fetch_retries_next_validated_address_after_network_error(
        self, mock_validate: MagicMock
    ) -> None:
        failed = MagicMock()
        failed.request.side_effect = OSError("first address unavailable")
        succeeded = MagicMock()
        succeeded.getresponse.return_value = _mock_response(body=b'{"ok": true}')
        addresses = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443)),
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.35", 443)),
        ]
        with (
            patch("vcp.revocation.socket.getaddrinfo", return_value=addresses),
            patch(
                "vcp.revocation._PinnedHTTPSConnection", side_effect=[failed, succeeded]
            ) as factory,
        ):
            assert _fetch_json("https://status.example") == {"ok": True}

        assert [call.args[2] for call in factory.call_args_list] == [
            "93.184.216.34",
            "93.184.216.35",
        ]
        failed.close.assert_called_once_with()
        succeeded.close.assert_called_once_with()

    @patch("vcp.revocation.validate_uri", return_value=(True, "OK"))
    def test_fetch_reports_all_address_network_failure(self, mock_validate: MagicMock) -> None:
        connection = MagicMock()
        connection.request.side_effect = TimeoutError("timed out")
        addresses = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443))]
        with (
            patch("vcp.revocation.socket.getaddrinfo", return_value=addresses),
            patch("vcp.revocation._PinnedHTTPSConnection", return_value=connection),
            pytest.raises(RevocationError, match="HTTPS request failed: timed out"),
        ):
            _fetch_json("https://status.example/check")
        connection.close.assert_called_once_with()

    @pytest.mark.parametrize(
        ("response", "message"),
        [
            (_mock_response(status=503), "status 503"),
            (
                _mock_response(
                    headers=[("Content-Type", "application/json")] * (MAX_RESPONSE_HEADERS + 1)
                ),
                "limit of 64 headers",
            ),
            (
                _mock_response(
                    headers=[
                        ("Content-Type", "application/json"),
                        ("X-Large", "a" * MAX_RESPONSE_HEADER_BYTES),
                    ]
                ),
                "headers exceed",
            ),
            (
                _mock_response(
                    headers=[
                        ("Content-Type", "application/json"),
                        ("Content-Encoding", "gzip"),
                    ]
                ),
                "Compressed",
            ),
            (_mock_response(headers=[("Content-Type", "text/plain")]), "JSON content type"),
            (
                _mock_response(
                    headers=[("Content-Type", "application/json"), ("Content-Length", "many")]
                ),
                "Invalid Content-Length",
            ),
            (
                _mock_response(
                    headers=[("Content-Type", "application/json"), ("Content-Length", "-1")]
                ),
                "valid range",
            ),
            (
                _mock_response(
                    headers=[("Content-Type", "application/json"), ("Content-Length", "9")]
                ),
                "valid range",
            ),
            (_mock_response(body=b"123456789"), "body exceeds"),
            (_mock_response(body=b"not-json"), "Invalid JSON"),
            (_mock_response(body=b"\xff"), "Invalid JSON"),
            (_mock_response(body=b"[]"), "must be a JSON object"),
        ],
    )
    @patch("vcp.revocation.validate_uri", return_value=(True, "OK"))
    def test_fetch_rejects_invalid_bounded_response(
        self, mock_validate: MagicMock, response: MagicMock, message: str
    ) -> None:
        connection = MagicMock()
        connection.getresponse.return_value = response
        addresses = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443))]
        with (
            patch("vcp.revocation.socket.getaddrinfo", return_value=addresses),
            patch("vcp.revocation._PinnedHTTPSConnection", return_value=connection),
            pytest.raises(RevocationError, match=message),
        ):
            _fetch_json("https://status.example/check", max_bytes=8)
        connection.close.assert_called_once_with()


# ---------------------------------------------------------------------------
# RevocationChecker: online endpoint
# ---------------------------------------------------------------------------


class TestOnlineCheck:
    """Tests for check_uri (online revocation endpoint)."""

    @patch("vcp.revocation.validate_uri", return_value=(True, "OK"))
    @patch("vcp.revocation._fetch_json")
    def test_not_revoked_online(self, mock_fetch: MagicMock, mock_validate: MagicMock) -> None:
        mock_fetch.return_value = _online_response()
        checker = RevocationChecker(cache_ttl=60)
        manifest = _manifest(check_uri="https://creed.space/api/v1/revoked")
        result = checker.check(manifest)
        assert result.revoked is False
        assert result.reason is None

    @patch("vcp.revocation.validate_uri", return_value=(True, "OK"))
    @patch("vcp.revocation._fetch_json")
    def test_revoked_online(self, mock_fetch: MagicMock, mock_validate: MagicMock) -> None:
        mock_fetch.return_value = _online_response(
            revoked=True,
            reason="key_compromise",
            revoked_at="2026-02-14T08:00:00Z",
        )
        checker = RevocationChecker(cache_ttl=60)
        manifest = _manifest(check_uri="https://creed.space/api/v1/revoked")
        result = checker.check(manifest)
        assert result.revoked is True
        assert result.reason == "key_compromise"
        assert result.revoked_at == "2026-02-14T08:00:00Z"

    @patch("vcp.revocation.validate_uri", return_value=(True, "OK"))
    @patch("vcp.revocation._fetch_json")
    def test_online_cache_hit(self, mock_fetch: MagicMock, mock_validate: MagicMock) -> None:
        mock_fetch.return_value = _online_response()
        checker = RevocationChecker(cache_ttl=300)
        manifest = _manifest(check_uri="https://creed.space/api/v1/revoked")

        # First call fetches
        result1 = checker.check(manifest, expected_issuer="creed.space")
        assert result1.revoked is False
        assert mock_fetch.call_count == 1

        # Second call should hit cache
        result2 = checker.check(manifest, expected_issuer="creed.space")
        assert result2.revoked is False
        assert mock_fetch.call_count == 1  # NOT incremented

    @patch("vcp.revocation.validate_uri", return_value=(True, "OK"))
    @patch("vcp.revocation._fetch_json")
    def test_online_cache_is_bound_to_issuer(
        self, mock_fetch: MagicMock, mock_validate: MagicMock
    ) -> None:
        mock_fetch.side_effect = [
            _online_response(issuer="issuer-a"),
            _online_response(
                revoked=True,
                issuer="issuer-b",
                reason="rotated",
                revoked_at="2026-02-14T08:00:00Z",
            ),
        ]
        checker = RevocationChecker(cache_ttl=300)
        manifest = _manifest(check_uri="https://creed.space/api/v1/revoked")

        assert not checker.check(manifest, expected_issuer="issuer-a").revoked
        assert checker.check(manifest, expected_issuer="issuer-b").revoked
        assert mock_fetch.call_count == 2

    @patch("vcp.revocation.validate_uri", return_value=(True, "OK"))
    @patch("vcp.revocation._fetch_json")
    def test_existing_jti_query_is_replaced(
        self, mock_fetch: MagicMock, mock_validate: MagicMock
    ) -> None:
        mock_fetch.return_value = _online_response(jti="real-jti")
        checker = RevocationChecker(cache_ttl=60)
        manifest = _manifest(
            jti="real-jti",
            check_uri=("https://creed.space/revoked?jti=attacker-value&issuer=attacker&mode=full"),
        )

        checker.check(manifest)

        requested_uri = mock_fetch.call_args.args[0]
        assert requested_uri.count("jti=") == 1
        assert requested_uri.count("issuer=") == 1
        assert "jti=real-jti" in requested_uri
        assert "issuer=creed.space" in requested_uri
        assert "attacker-value" not in requested_uri
        assert "issuer=attacker" not in requested_uri

    def test_shared_online_response_contract_matches_python_parser(self) -> None:
        fixture_path = _conformance_fixture("revocation-responses.json")
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))

        for case in fixture["vectors"]:
            manifest = _manifest(jti=case["jti"], check_uri="https://status.example/check")
            manifest.issuer.id = case["issuer"]
            with (
                patch("vcp.revocation.validate_uri", return_value=(True, "OK")),
                patch("vcp.revocation._fetch_json", return_value=case["response"]),
            ):
                result = RevocationChecker().check(manifest)
            assert result.decision is not None
            assert result.decision.value == case["expected"], case["id"]


# ---------------------------------------------------------------------------
# RevocationChecker: CRL
# ---------------------------------------------------------------------------


class TestCRLCheck:
    """Tests for crl_uri (Certificate Revocation List)."""

    def test_shared_crl_response_contract_matches_python_parser(self) -> None:
        fixture_path = _conformance_fixture("revocation-crl-responses.json")
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))

        for case in fixture["vectors"]:
            manifest = _manifest(jti=case["jti"], crl_uri="https://status.example/crl.json")
            manifest.issuer.id = case["issuer"]
            with (
                patch("vcp.revocation.validate_uri", return_value=(True, "OK")),
                patch("vcp.revocation._fetch_json", return_value=case["response"]),
            ):
                result = RevocationChecker().check(manifest)
            assert result.decision is not None
            assert result.decision.value == case["expected"], case["id"]

    @patch("vcp.revocation.validate_uri", return_value=(True, "OK"))
    @patch("vcp.revocation._fetch_json")
    def test_revoked_via_crl(self, mock_fetch: MagicMock, mock_validate: MagicMock) -> None:
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
    def test_not_revoked_via_crl(self, mock_fetch: MagicMock, mock_validate: MagicMock) -> None:
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
    def test_crl_cache_hit(self, mock_fetch: MagicMock, mock_validate: MagicMock) -> None:
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
    def test_expired_crl_fails_closed(
        self, mock_fetch: MagicMock, mock_validate: MagicMock
    ) -> None:
        """An expired CRL cannot establish non-revocation."""
        mock_fetch.return_value = _crl_response(
            revoked_entries=[],
            next_update="2020-01-01T00:00:00Z",  # long expired
        )
        checker = RevocationChecker(cache_ttl=60)
        manifest = _manifest(crl_uri="https://creed.space/crl/2026.json")
        result = checker.check(manifest)
        _assert_unavailable(result)

    @patch("vcp.revocation.validate_uri", return_value=(True, "OK"))
    @patch("vcp.revocation._fetch_json")
    def test_crl_requires_available_expected_issuer(
        self, mock_fetch: MagicMock, mock_validate: MagicMock
    ) -> None:
        manifest = _manifest(crl_uri="https://creed.space/crl.json")
        delattr(manifest, "issuer")

        result = RevocationChecker(cache_ttl=60).check(manifest)

        _assert_unavailable(result)
        mock_fetch.assert_not_called()

    @patch("vcp.revocation.validate_uri", return_value=(True, "OK"))
    @patch("vcp.revocation._fetch_json")
    def test_crl_issuer_must_match_expected_issuer(
        self, mock_fetch: MagicMock, mock_validate: MagicMock
    ) -> None:
        mock_fetch.return_value = _crl_response()
        checker = RevocationChecker(cache_ttl=60)
        result = checker.check(
            _manifest(crl_uri="https://creed.space/crl.json"),
            expected_issuer="other.example",
        )
        _assert_unavailable(result)

    @pytest.mark.parametrize(
        ("field", "value"),
        [
            ("updated_at", None),
            ("updated_at", "2026-01-01 00:00:00Z"),
            ("updated_at", "2026-01-01T00:00:00"),
            ("next_update", "2026-01-01 00:00:00Z"),
            ("next_update", "2026-01-01T00:00:00"),
        ],
    )
    @patch("vcp.revocation.validate_uri", return_value=(True, "OK"))
    @patch("vcp.revocation._fetch_json")
    def test_crl_requires_strict_rfc3339_timestamps(
        self,
        mock_fetch: MagicMock,
        mock_validate: MagicMock,
        field: str,
        value: str | None,
    ) -> None:
        crl = _crl_response()
        crl[field] = value
        mock_fetch.return_value = crl
        checker = RevocationChecker(cache_ttl=60)
        result = checker.check(_manifest(crl_uri="https://creed.space/crl.json"))
        _assert_unavailable(result)

    @patch("vcp.revocation.validate_uri", return_value=(True, "OK"))
    @patch("vcp.revocation._fetch_json")
    def test_crl_updated_at_must_not_follow_next_update(
        self, mock_fetch: MagicMock, mock_validate: MagicMock
    ) -> None:
        now = datetime.now(timezone.utc)
        mock_fetch.return_value = _crl_response(
            next_update=(now + timedelta(hours=1)).isoformat().replace("+00:00", "Z")
        )
        mock_fetch.return_value["updated_at"] = (
            (now + timedelta(hours=2)).isoformat().replace("+00:00", "Z")
        )
        result = RevocationChecker().check(_manifest(crl_uri="https://creed.space/crl.json"))
        _assert_unavailable(result)

    @pytest.mark.parametrize(
        "entries",
        [
            [{"jti": "", "reason": "invalid", "revoked_at": "2026-01-01T00:00:00Z"}],
            [
                {"jti": "duplicate", "reason": "first", "revoked_at": "2026-01-01T00:00:00Z"},
                {"jti": "duplicate", "reason": "second", "revoked_at": "2026-01-02T00:00:00Z"},
            ],
        ],
    )
    @patch("vcp.revocation.validate_uri", return_value=(True, "OK"))
    @patch("vcp.revocation._fetch_json")
    def test_crl_rejects_empty_and_duplicate_jtis(
        self,
        mock_fetch: MagicMock,
        mock_validate: MagicMock,
        entries: list[dict[str, str]],
    ) -> None:
        mock_fetch.return_value = _crl_response(revoked_entries=entries)
        result = RevocationChecker().check(_manifest(crl_uri="https://creed.space/crl.json"))
        _assert_unavailable(result)

    @patch("vcp.revocation.validate_uri", return_value=(True, "OK"))
    @patch("vcp.revocation._fetch_json")
    def test_omitted_expected_issuer_derives_from_manifest(
        self, mock_fetch: MagicMock, mock_validate: MagicMock
    ) -> None:
        mock_fetch.return_value = _crl_response()
        manifest = _manifest(crl_uri="https://creed.space/crl.json")
        manifest.issuer.id = "other.example"
        result = RevocationChecker().check(manifest)
        _assert_unavailable(result)

    @patch("vcp.revocation.validate_uri", return_value=(True, "OK"))
    @patch("vcp.revocation._fetch_json")
    def test_every_non_null_crl_revoked_at_requires_strict_rfc3339(
        self, mock_fetch: MagicMock, mock_validate: MagicMock
    ) -> None:
        mock_fetch.return_value = _crl_response(
            revoked_entries=[
                {
                    "jti": "unrelated-jti",
                    "reason": "bad timestamp",
                    "revoked_at": "2026-01-01T00:00:00",
                }
            ]
        )
        result = RevocationChecker().check(_manifest(crl_uri="https://creed.space/crl.json"))
        _assert_unavailable(result)


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
                    {
                        "jti": target_jti,
                        "revoked_at": "2026-02-14T08:00:00Z",
                        "reason": "superseded",
                    }
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
        _assert_unavailable(result)

    @patch("vcp.revocation.socket.getaddrinfo")
    def test_ssrf_loopback_online(self, mock_gai: MagicMock) -> None:
        mock_gai.return_value = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 443)),
        ]
        checker = RevocationChecker(cache_ttl=60)
        manifest = _manifest(check_uri="https://localhost/revoked")
        result = checker.check(manifest)
        _assert_unavailable(result)

    @patch("vcp.revocation.socket.getaddrinfo")
    def test_ssrf_ipv6_loopback_online(self, mock_gai: MagicMock) -> None:
        mock_gai.return_value = [
            (socket.AF_INET6, socket.SOCK_STREAM, 6, "", ("::1", 443, 0, 0)),
        ]
        checker = RevocationChecker(cache_ttl=60)
        manifest = _manifest(check_uri="https://localhost/revoked")
        result = checker.check(manifest)
        _assert_unavailable(result)

    def test_ssrf_file_scheme(self) -> None:
        checker = RevocationChecker(cache_ttl=60)
        manifest = _manifest(check_uri="file:///etc/passwd")
        result = checker.check(manifest)
        _assert_unavailable(result)


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


class TestErrorHandling:
    """Tests for timeout, malformed response, and oversize response."""

    @patch("vcp.revocation.validate_uri", return_value=(True, "OK"))
    @patch("vcp.revocation._fetch_json", side_effect=RevocationError("Request timed out"))
    def test_timeout_handling(self, mock_fetch: MagicMock, mock_validate: MagicMock) -> None:
        checker = RevocationChecker(cache_ttl=60, timeout=0.001)
        manifest = _manifest(check_uri="https://slow.example.com/revoked")
        result = checker.check(manifest)
        _assert_unavailable(result)

    @patch("vcp.revocation.validate_uri", return_value=(True, "OK"))
    @patch(
        "vcp.revocation._fetch_json",
        side_effect=RevocationError("Invalid JSON response"),
    )
    def test_malformed_json_response(self, mock_fetch: MagicMock, mock_validate: MagicMock) -> None:
        checker = RevocationChecker(cache_ttl=60)
        manifest = _manifest(check_uri="https://broken.example.com/revoked")
        result = checker.check(manifest)
        _assert_unavailable(result)

    @patch("vcp.revocation.validate_uri", return_value=(True, "OK"))
    @patch(
        "vcp.revocation._fetch_json",
        side_effect=RevocationError(f"Response body exceeds limit of {MAX_RESPONSE_BYTES} bytes"),
    )
    def test_response_too_large(self, mock_fetch: MagicMock, mock_validate: MagicMock) -> None:
        checker = RevocationChecker(cache_ttl=60)
        manifest = _manifest(check_uri="https://large.example.com/revoked")
        result = checker.check(manifest)
        _assert_unavailable(result)

    @patch("vcp.revocation.validate_uri", return_value=(True, "OK"))
    @patch("vcp.revocation._fetch_json", return_value={"revoked": "false"})
    def test_non_boolean_online_status_fails_closed(
        self, mock_fetch: MagicMock, mock_validate: MagicMock
    ) -> None:
        checker = RevocationChecker(cache_ttl=60)
        result = checker.check(_manifest(check_uri="https://example.com/revoked"))
        _assert_unavailable(result)

    @patch("vcp.revocation.validate_uri", return_value=(True, "OK"))
    @patch("vcp.revocation._fetch_json", return_value={"next_update": None, "revoked": {}})
    def test_non_array_crl_fails_closed(
        self, mock_fetch: MagicMock, mock_validate: MagicMock
    ) -> None:
        checker = RevocationChecker(cache_ttl=60)
        result = checker.check(_manifest(crl_uri="https://example.com/crl.json"))
        _assert_unavailable(result)


# ---------------------------------------------------------------------------
# RevocationStatus dataclass
# ---------------------------------------------------------------------------


class TestRevocationStatus:
    """Basic tests for the RevocationStatus dataclass."""

    def test_defaults(self) -> None:
        status = RevocationStatus(revoked=False)
        assert status.revoked is False
        assert status.decision is RevocationDecision.NOT_REVOKED
        assert status.reason is None
        assert status.revoked_at is None

    def test_revoked_with_details(self) -> None:
        status = RevocationStatus(
            revoked=True,
            reason="key_compromise",
            revoked_at="2026-02-14T08:00:00Z",
        )
        assert status.revoked is True
        assert status.decision is RevocationDecision.REVOKED
        assert status.reason == "key_compromise"
        assert status.revoked_at == "2026-02-14T08:00:00Z"

    def test_unavailable_is_distinct_and_fail_closed(self) -> None:
        status = RevocationStatus.unavailable()
        assert status.revoked is False
        assert status.decision is RevocationDecision.UNAVAILABLE
        assert status.should_reject


# ---------------------------------------------------------------------------
# Cache expiration
# ---------------------------------------------------------------------------


class TestCacheExpiration:
    """Verify cache entries expire after TTL."""

    @patch("vcp.revocation.validate_uri", return_value=(True, "OK"))
    @patch("vcp.revocation._fetch_json")
    def test_online_cache_expires(self, mock_fetch: MagicMock, mock_validate: MagicMock) -> None:
        mock_fetch.return_value = _online_response()
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
    def test_crl_cache_expires(self, mock_fetch: MagicMock, mock_validate: MagicMock) -> None:
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

    def test_orchestrator_defaults_to_bounded_checker(self) -> None:
        from vcp.orchestrator import Orchestrator
        from vcp.trust import TrustConfig

        orch = Orchestrator(trust_config=TrustConfig())
        assert isinstance(orch.revocation_checker, RevocationChecker)


class TestBoundedCaches:
    def test_decision_cache_evicts_oldest_entry(self) -> None:
        checker = RevocationChecker(max_cache_entries=2)
        checker._set_cached("first", RevocationStatus(revoked=False))
        checker._set_cached("second", RevocationStatus(revoked=False))
        checker._set_cached("third", RevocationStatus(revoked=False))
        assert list(checker._cache) == ["second", "third"]

    def test_crl_cache_evicts_oldest_entry(self) -> None:
        checker = RevocationChecker(max_crl_cache_entries=1)
        checker._set_crl_cached("first", {})
        checker._set_crl_cached("second", {})
        assert list(checker._crl_cache) == ["second"]

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"cache_ttl": -1},
            {"timeout": 0},
            {"max_cache_entries": 0},
            {"max_crl_cache_entries": 0},
        ],
    )
    def test_invalid_limits_are_rejected(self, kwargs: dict[str, int]) -> None:
        with pytest.raises(ValueError):
            RevocationChecker(**kwargs)

    def test_revocation_exports(self) -> None:
        """RevocationChecker and RevocationStatus should be importable from vcp."""
        from vcp import RevocationChecker as RChecker
        from vcp import RevocationError as RError
        from vcp import RevocationStatus as RStatus

        assert RChecker is RevocationChecker
        assert RStatus is RevocationStatus
        assert RError is RevocationError
