"""
VCP Revocation Checking Module

Checks bundle revocation status via online endpoint (check_uri) or
Certificate Revocation List (crl_uri) as defined in VCP Spec v1.0 Section 8.
"""

from __future__ import annotations

import http.client
import ipaddress
import json
import logging
import re
import socket
import ssl
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

logger = logging.getLogger(__name__)

# Maximum response size: 320KB
MAX_RESPONSE_BYTES = 327_680
MAX_RESPONSE_HEADERS = 64
MAX_RESPONSE_HEADER_BYTES = 32_768

# The revocation transport is HTTPS-only, so its sole default port is 443.
_STANDARD_PORTS = {443}
DEFAULT_MAX_DECISION_CACHE_ENTRIES = 4096
DEFAULT_MAX_CRL_CACHE_ENTRIES = 256


class RevocationError(Exception):
    """Raised when revocation checking encounters an unrecoverable error."""


class RevocationDecision(str, Enum):
    """Exact outcome of a revocation lookup."""

    NOT_REVOKED = "not_revoked"
    REVOKED = "revoked"
    UNAVAILABLE = "unavailable"


@dataclass
class RevocationStatus:
    """Result of a revocation check."""

    revoked: bool
    reason: str | None = None
    revoked_at: str | None = None
    decision: RevocationDecision | None = None

    def __post_init__(self) -> None:
        if self.decision is None:
            self.decision = (
                RevocationDecision.REVOKED if self.revoked else RevocationDecision.NOT_REVOKED
            )

    @classmethod
    def unavailable(cls) -> RevocationStatus:
        """Create a distinct fail-closed status for an unavailable decision."""
        return cls(
            revoked=False,
            reason="revocation_status_unavailable",
            decision=RevocationDecision.UNAVAILABLE,
        )

    @property
    def should_reject(self) -> bool:
        """Whether verification must reject this result fail closed."""
        return self.decision is not RevocationDecision.NOT_REVOKED


@dataclass
class _CacheEntry:
    """Internal cache entry with expiration."""

    value: Any
    expires_at: float


_RFC3339_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
    r"(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)


def _parse_rfc3339(value: Any, field: str) -> datetime:
    """Parse a required, timezone-qualified RFC 3339 timestamp."""
    if not isinstance(value, str) or not _RFC3339_RE.fullmatch(value):
        raise RevocationError(f"CRL '{field}' must be an RFC 3339 string with timezone")
    normalized = f"{value[:-1]}+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise RevocationError(f"CRL '{field}' must be an RFC 3339 string with timezone") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise RevocationError(f"CRL '{field}' must include a timezone")
    return parsed.astimezone(timezone.utc)


def _is_private_ip(ip_str: str) -> bool:
    """Check whether an IP address falls within private/reserved ranges.

    Args:
        ip_str: String representation of an IP address.

    Returns:
        True if the IP is private, loopback, link-local, or otherwise reserved.
    """
    try:
        addr = ipaddress.ip_address(ip_str)
    except ValueError:
        # Unparseable IP -- reject for safety
        return True

    if isinstance(addr, ipaddress.IPv6Address) and addr.ipv4_mapped:
        return _is_private_ip(str(addr.ipv4_mapped))
    if isinstance(addr, ipaddress.IPv6Address):
        packed = addr.packed
        # Reject NAT64 and deprecated IPv4-compatible translation space. These
        # prefixes can route an apparently public IPv6 address to an embedded
        # private IPv4 destination on some networks.
        if packed[:12] == bytes.fromhex("0064ff9b0000000000000000"):
            return True
        if packed[:6] == bytes.fromhex("0064ff9b0001"):
            return True
        if packed[:12] == b"\x00" * 12:
            return True
    return not addr.is_global


def validate_uri(uri: str, allowed_ports: set[int] | None = None) -> tuple[bool, str]:
    """Validate a URI for SSRF safety BEFORE making any HTTP request.

    Resolves the hostname and checks that the resolved IP is not in any
    private/reserved range. Rejects non-HTTPS schemes, ports other than 443
    (unless allowlisted), and unresolvable hostnames.

    Args:
        uri: The URI to validate.
        allowed_ports: Additional HTTPS ports to allow beyond 443.

    Returns:
        Tuple of (is_safe, reason).  If is_safe is False, reason explains why.
    """
    parsed = urlparse(uri)

    # Scheme check
    if parsed.scheme != "https":
        return False, f"Rejected scheme: {parsed.scheme!r} (only https is allowed)"
    if parsed.fragment:
        return False, "Fragments are not permitted in revocation URIs"

    # Hostname check
    hostname = parsed.hostname
    if not hostname:
        return False, "No hostname in URI"
    if parsed.username is not None or parsed.password is not None:
        return False, "Credentials are not permitted in revocation URIs"

    # Port check
    try:
        port = parsed.port
    except ValueError as exc:
        return False, f"Invalid port: {exc}"
    valid_ports = _STANDARD_PORTS | (allowed_ports or set())
    if port is not None and port not in valid_ports:
        return False, f"Non-standard port {port} not in allowed set {valid_ports}"

    # Resolve hostname to IP addresses
    try:
        addrinfo = socket.getaddrinfo(
            hostname,
            port or 443,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP,
        )
    except socket.gaierror as exc:
        return False, f"DNS resolution failed for {hostname!r}: {exc}"

    if not addrinfo:
        return False, f"No addresses resolved for {hostname!r}"

    # Check ALL resolved IPs -- reject if ANY is private
    for family, _type, _proto, _canonname, sockaddr in addrinfo:
        ip_str = str(sockaddr[0])
        if _is_private_ip(ip_str):
            return False, f"Resolved IP {ip_str} is in a private/reserved range"

    return True, "OK"


class _PinnedHTTPSConnection(http.client.HTTPSConnection):
    """HTTPS connection pinned to a prevalidated address while retaining TLS SNI."""

    def __init__(self, hostname: str, port: int, resolved_ip: str, timeout: float):
        tls_context = ssl.create_default_context()
        # Make the network security contract explicit. CPython's default
        # context currently rejects TLS 1.0 and 1.1, but relying on an
        # interpreter default makes the floor difficult to audit and can let
        # platform policy drift change revocation-check behavior.
        tls_context.minimum_version = ssl.TLSVersion.TLSv1_2
        super().__init__(hostname, port=port, timeout=timeout, context=tls_context)
        self._resolved_ip = resolved_ip
        self._tls_context = tls_context

    def connect(self) -> None:
        raw_socket = socket.create_connection(
            (self._resolved_ip, self.port),
            timeout=self.timeout,
        )
        self.sock = self._tls_context.wrap_socket(raw_socket, server_hostname=self.host)


def _fetch_json(
    uri: str,
    timeout: float = 10.0,
    max_bytes: int = MAX_RESPONSE_BYTES,
    allowed_ports: set[int] | None = None,
) -> dict[str, Any]:
    """Fetch JSON from a URI with size and timeout limits.

    Args:
        uri: The URL to fetch.
        timeout: Request timeout in seconds.
        max_bytes: Maximum response body size.

    Returns:
        Parsed JSON as a dict.

    Raises:
        RevocationError: On network, size, or parse errors.
    """
    is_safe, reason = validate_uri(uri, allowed_ports)
    if not is_safe:
        raise RevocationError(f"SSRF protection: {reason}")
    parsed = urlparse(uri)
    hostname = parsed.hostname
    if hostname is None:
        raise RevocationError("No hostname in revocation URI")
    port = parsed.port or 443
    try:
        addresses = {
            str(sockaddr[0])
            for _family, _type, _proto, _canonname, sockaddr in socket.getaddrinfo(
                hostname,
                port,
                type=socket.SOCK_STREAM,
                proto=socket.IPPROTO_TCP,
            )
        }
    except socket.gaierror as exc:
        raise RevocationError(f"DNS resolution failed for {hostname!r}: {exc}") from exc
    if not addresses or any(_is_private_ip(address) for address in addresses):
        raise RevocationError("DNS resolution returned an unsafe address")

    target = urlunparse(("", "", parsed.path or "/", parsed.params, parsed.query, ""))
    host_header = hostname if port == 443 else f"{hostname}:{port}"
    last_error: Exception | None = None
    for address in sorted(addresses):
        connection = _PinnedHTTPSConnection(hostname, port, address, timeout)
        try:
            connection.request(
                "GET",
                target,
                headers={
                    "Accept": "application/json",
                    "Accept-Encoding": "identity",
                    "Host": host_header,
                    "User-Agent": "VCP-SDK/4.2",
                },
            )
            response = connection.getresponse()
            if response.status != 200:
                raise RevocationError(f"HTTP request failed with status {response.status}")
            response_headers = response.getheaders()
            if len(response_headers) > MAX_RESPONSE_HEADERS:
                raise RevocationError(
                    f"Response exceeds the limit of {MAX_RESPONSE_HEADERS} headers"
                )
            header_bytes = sum(
                len(name.encode("ascii", "strict")) + len(value.encode("latin-1", "strict"))
                for name, value in response_headers
            )
            if header_bytes > MAX_RESPONSE_HEADER_BYTES:
                raise RevocationError(f"Response headers exceed {MAX_RESPONSE_HEADER_BYTES} bytes")
            content_encoding = response.getheader("Content-Encoding")
            if content_encoding is not None and content_encoding.lower() != "identity":
                raise RevocationError("Compressed revocation responses are not accepted")
            content_type = response.getheader("Content-Type")
            media_type = (content_type or "").split(";", 1)[0].strip().lower()
            if media_type != "application/json" and not media_type.endswith("+json"):
                raise RevocationError("Revocation response requires a JSON content type")
            content_length = response.getheader("Content-Length")
            if content_length is not None:
                try:
                    parsed_content_length = int(content_length)
                except ValueError as exc:
                    raise RevocationError(
                        f"Invalid Content-Length header: {content_length!r}"
                    ) from exc
                if parsed_content_length < 0 or parsed_content_length > max_bytes:
                    raise RevocationError(
                        f"Response Content-Length {content_length} exceeds valid range "
                        f"of 0-{max_bytes} bytes"
                    )
            data = response.read(max_bytes + 1)
            if len(data) > max_bytes:
                raise RevocationError(f"Response body exceeds limit of {max_bytes} bytes")
            parsed_data = json.loads(data.decode("utf-8"))
            if not isinstance(parsed_data, dict):
                raise RevocationError("Revocation response must be a JSON object")
            return parsed_data
        except (OSError, TimeoutError, ssl.SSLError, http.client.HTTPException) as exc:
            last_error = exc
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RevocationError(f"Invalid JSON response: {exc}") from exc
        finally:
            connection.close()
    raise RevocationError(f"HTTPS request failed: {last_error}") from last_error


class RevocationChecker:
    """Check bundle revocation status via online endpoint or CRL.

    Tries check_uri first (real-time status), falls back to CRL.
    Both results are cached for cache_ttl seconds.

    Args:
        cache_ttl: Cache time-to-live in seconds.
        timeout: HTTP request timeout in seconds.
        allowed_ports: Additional HTTPS ports beyond 443 to allow.
    """

    def __init__(
        self,
        cache_ttl: int = 300,
        timeout: float = 10.0,
        allowed_ports: set[int] | None = None,
        max_cache_entries: int = DEFAULT_MAX_DECISION_CACHE_ENTRIES,
        max_crl_cache_entries: int = DEFAULT_MAX_CRL_CACHE_ENTRIES,
    ) -> None:
        if cache_ttl < 0 or timeout <= 0:
            raise ValueError("cache_ttl must be non-negative and timeout must be positive")
        if max_cache_entries < 1 or max_crl_cache_entries < 1:
            raise ValueError("revocation cache limits must be positive")
        self._cache: dict[str, _CacheEntry] = {}
        self._crl_cache: dict[str, _CacheEntry] = {}
        self._cache_ttl = cache_ttl
        self._timeout = timeout
        self._allowed_ports = allowed_ports
        self._max_cache_entries = max_cache_entries
        self._max_crl_cache_entries = max_crl_cache_entries
        self._cache_lock = threading.RLock()

    def check(self, manifest: Any, expected_issuer: str | None = None) -> RevocationStatus:
        """Check if a bundle is revoked.

        Tries the online check_uri endpoint first.  If unavailable or
        erroring, falls back to the CRL.  If neither revocation URI is
        configured, returns not-revoked with a logged warning.

        Args:
            manifest: A VCP Manifest object with .timestamps.jti and
                      .revocation dict.
            expected_issuer: Issuer identity expected to publish any CRL.

        Returns:
            RevocationStatus indicating whether the bundle is revoked.
        """
        jti = manifest.timestamps.jti
        revocation = manifest.revocation
        if expected_issuer is None:
            manifest_issuer = getattr(manifest, "issuer", None)
            manifest_issuer_id = getattr(manifest_issuer, "id", None)
            if isinstance(manifest_issuer_id, str):
                expected_issuer = manifest_issuer_id
        if not isinstance(jti, str) or not jti.strip():
            logger.error("Revocation check rejected an empty bundle jti")
            return RevocationStatus.unavailable()
        if expected_issuer is not None and (
            not isinstance(expected_issuer, str) or not expected_issuer.strip()
        ):
            logger.error("Revocation check rejected an empty expected issuer")
            return RevocationStatus.unavailable()

        if not revocation:
            logger.warning(
                "No revocation URIs configured for bundle jti=%s; treating as not revoked",
                jti,
            )
            return RevocationStatus(revoked=False)

        check_uri = revocation.get("check_uri")
        crl_uri = revocation.get("crl_uri")
        if (check_uri or crl_uri) and expected_issuer is None:
            logger.error("Configured revocation checks require an expected issuer")
            return RevocationStatus.unavailable()

        # Try online endpoint first
        if check_uri:
            try:
                result = self._check_online(check_uri, jti, expected_issuer)
                if result is not None:
                    return result
            except RevocationError as exc:
                logger.warning("Online revocation check failed: %s", exc)

        # Fall back to CRL
        if crl_uri:
            try:
                return self._check_crl(crl_uri, jti, expected_issuer)
            except RevocationError as exc:
                logger.warning("CRL revocation check failed: %s", exc)

        # Neither check succeeded
        if not check_uri and not crl_uri:
            logger.warning(
                "No revocation URIs in manifest for jti=%s; treating as not revoked",
                jti,
            )
        else:
            logger.error(
                "All configured revocation checks failed for jti=%s; rejecting fail-closed",
                jti,
            )
            return RevocationStatus.unavailable()

        return RevocationStatus(revoked=False)

    def _check_online(
        self, uri: str, jti: str, expected_issuer: str | None
    ) -> RevocationStatus | None:
        """Check revocation via online endpoint.

        GET {check_uri}?jti={jti}&issuer={issuer} expecting an object that
        echoes both binding values and includes a boolean ``revoked``.

        Args:
            uri: The check_uri from the manifest.
            jti: The bundle's unique token ID.
            expected_issuer: Issuer context for cache isolation.

        Returns:
            RevocationStatus if the endpoint responds, None if unreachable.

        Raises:
            RevocationError: On SSRF rejection or critical failures.
        """
        # Check cache first
        cache_key = f"online:{uri}:{expected_issuer or ''}:{jti}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        # SSRF validation
        is_safe, reason = validate_uri(uri, self._allowed_ports)
        if not is_safe:
            raise RevocationError(f"SSRF protection: {reason}")

        # Build request URL
        parsed_uri = urlparse(uri)
        query = [
            (key, value)
            for key, value in parse_qsl(parsed_uri.query, keep_blank_values=True)
            if key not in {"jti", "issuer"}
        ]
        query.append(("jti", jti))
        if expected_issuer is None:
            raise RevocationError("Online revocation check requires an expected issuer")
        query.append(("issuer", expected_issuer))
        full_uri = urlunparse(parsed_uri._replace(query=urlencode(query)))

        data = _fetch_json(
            full_uri,
            timeout=self._timeout,
            allowed_ports=self._allowed_ports,
        )

        revoked = data.get("revoked")
        if not isinstance(revoked, bool):
            raise RevocationError("Online revocation response requires boolean 'revoked'")
        response_jti = data.get("jti")
        response_issuer = data.get("issuer")
        if response_jti != jti:
            raise RevocationError("Online revocation response jti does not match the request")
        if response_issuer != expected_issuer:
            raise RevocationError("Online revocation response issuer does not match the request")
        online_reason = data.get("reason")
        online_revoked_at = data.get("revoked_at")
        if online_reason is not None and not isinstance(online_reason, str):
            raise RevocationError("Online revocation 'reason' must be a string or null")
        if online_revoked_at is not None and not isinstance(online_revoked_at, str):
            raise RevocationError("Online revocation 'revoked_at' must be a string or null")
        if revoked:
            if not isinstance(online_reason, str) or not online_reason.strip():
                raise RevocationError("Confirmed revocation requires a non-empty reason")
            _parse_rfc3339(online_revoked_at, "online.revoked_at")
        elif online_reason is not None or online_revoked_at is not None:
            raise RevocationError("Non-revoked response must not include revocation details")
        status = RevocationStatus(
            revoked=revoked,
            reason=online_reason,
            revoked_at=online_revoked_at,
        )

        self._set_cached(cache_key, status)
        return status

    def _check_crl(self, uri: str, jti: str, expected_issuer: str | None) -> RevocationStatus:
        """Check revocation via Certificate Revocation List.

        Fetches the CRL JSON and checks if the jti appears in the
        revoked list.

        CRL format:
            {
                "issuer": "creed.space",
                "updated_at": "...",
                "next_update": "...",
                "revoked": [
                    {"jti": "...", "revoked_at": "...", "reason": "..."}
                ]
            }

        Args:
            uri: The crl_uri from the manifest.
            jti: The bundle's unique token ID.
            expected_issuer: Issuer identity the CRL must match, when supplied.

        Returns:
            RevocationStatus.

        Raises:
            RevocationError: On SSRF rejection or fetch failure.
        """
        # Check CRL cache first
        crl_cache_key = f"crl:{uri}:{expected_issuer or ''}"
        cached_crl = self._get_crl_cached(crl_cache_key)

        if cached_crl is None:
            # SSRF validation
            is_safe, reason = validate_uri(uri, self._allowed_ports)
            if not is_safe:
                raise RevocationError(f"SSRF protection: {reason}")

            crl_data = _fetch_json(
                uri,
                timeout=self._timeout,
                allowed_ports=self._allowed_ports,
            )

            issuer = crl_data.get("issuer")
            if not isinstance(issuer, str) or not issuer.strip():
                raise RevocationError("CRL requires a non-empty string 'issuer'")
            if expected_issuer is not None and issuer != expected_issuer:
                raise RevocationError(f"CRL issuer {issuer!r} does not match expected issuer")

            updated_dt = _parse_rfc3339(crl_data.get("updated_at"), "updated_at")
            next_dt = _parse_rfc3339(crl_data.get("next_update"), "next_update")
            if updated_dt > next_dt:
                raise RevocationError("CRL 'updated_at' must not be after 'next_update'")
            now = datetime.now(timezone.utc)
            if next_dt <= now:
                raise RevocationError(f"CRL at {uri} is expired")

            revoked_list = crl_data.get("revoked")
            if not isinstance(revoked_list, list):
                raise RevocationError("CRL 'revoked' must be an array")
            # Store as a lookup dict keyed by jti
            revoked_map: dict[str, dict[str, str]] = {}
            seen_jtis: set[str] = set()
            for entry in revoked_list:
                if not isinstance(entry, dict) or not isinstance(entry.get("jti"), str):
                    raise RevocationError("Each CRL entry requires a string 'jti'")
                entry_jti = entry["jti"]
                if not entry_jti.strip():
                    raise RevocationError("CRL entry 'jti' must not be empty")
                if entry_jti in seen_jtis:
                    raise RevocationError(f"CRL contains duplicate jti {entry_jti!r}")
                seen_jtis.add(entry_jti)
                entry_reason = entry.get("reason")
                entry_revoked_at = entry.get("revoked_at")
                if not isinstance(entry_reason, str) or not entry_reason.strip():
                    raise RevocationError("CRL entry 'reason' must be a non-empty string")
                if not isinstance(entry_revoked_at, str):
                    raise RevocationError("CRL entry 'revoked_at' must be a string")
                _parse_rfc3339(entry_revoked_at, "revoked[].revoked_at")
                revoked_map[entry_jti] = entry
            seconds_until_update = (next_dt - now).total_seconds()
            self._set_crl_cached(
                crl_cache_key,
                revoked_map,
                max_age=min(float(self._cache_ttl), seconds_until_update),
            )
            cached_crl = revoked_map

        # Look up our jti
        entry = cached_crl.get(jti)
        if entry:
            return RevocationStatus(
                revoked=True,
                reason=entry.get("reason"),
                revoked_at=entry.get("revoked_at"),
            )

        return RevocationStatus(revoked=False)

    # -- Cache helpers ---------------------------------------------------------

    def _get_cached(self, key: str) -> RevocationStatus | None:
        """Retrieve a non-expired cache entry."""
        with self._cache_lock:
            entry = self._cache.get(key)
            if entry and entry.expires_at > time.monotonic():
                return entry.value  # type: ignore[no-any-return]
            if entry:
                del self._cache[key]
            return None

    def _set_cached(self, key: str, value: RevocationStatus) -> None:
        """Store a value in the cache."""
        with self._cache_lock:
            self._prune_for_insert(self._cache, self._max_cache_entries, key)
            self._cache[key] = _CacheEntry(
                value=value,
                expires_at=time.monotonic() + self._cache_ttl,
            )

    def _get_crl_cached(self, key: str) -> dict[str, dict[str, str]] | None:
        """Retrieve a non-expired CRL cache entry."""
        with self._cache_lock:
            entry = self._crl_cache.get(key)
            if entry and entry.expires_at > time.monotonic():
                return entry.value  # type: ignore[no-any-return]
            if entry:
                del self._crl_cache[key]
            return None

    def _set_crl_cached(
        self,
        key: str,
        value: dict[str, dict[str, str]],
        max_age: float | None = None,
    ) -> None:
        """Store a CRL in the cache."""
        with self._cache_lock:
            self._prune_for_insert(self._crl_cache, self._max_crl_cache_entries, key)
            self._crl_cache[key] = _CacheEntry(
                value=value,
                expires_at=time.monotonic()
                + (float(self._cache_ttl) if max_age is None else max_age),
            )

    @staticmethod
    def _prune_for_insert(cache: dict[str, _CacheEntry], limit: int, key: str) -> None:
        """Expire stale entries and evict oldest insertions deterministically."""
        now = time.monotonic()
        for stale_key in [k for k, entry in cache.items() if entry.expires_at <= now]:
            del cache[stale_key]
        # Reinsert updates at the newest position in dict insertion order.
        cache.pop(key, None)
        while len(cache) >= limit:
            del cache[next(iter(cache))]

    def clear_cache(self) -> None:
        """Clear all caches."""
        with self._cache_lock:
            self._cache.clear()
            self._crl_cache.clear()
