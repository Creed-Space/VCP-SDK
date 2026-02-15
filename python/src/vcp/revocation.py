"""
VCP Revocation Checking Module

Checks bundle revocation status via online endpoint (check_uri) or
Certificate Revocation List (crl_uri) as defined in VCP Spec v1.0 Section 8.
"""

from __future__ import annotations

import ipaddress
import json
import logging
import socket
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# Maximum response size: 320KB
MAX_RESPONSE_BYTES = 327_680

# Standard HTTP(S) ports
_STANDARD_PORTS = {80, 443}

# Private/reserved IPv4 networks to reject (SSRF protection)
_PRIVATE_IPV4_NETWORKS = [
    ipaddress.IPv4Network("127.0.0.0/8"),       # Loopback
    ipaddress.IPv4Network("10.0.0.0/8"),         # Private Class A
    ipaddress.IPv4Network("172.16.0.0/12"),      # Private Class B
    ipaddress.IPv4Network("192.168.0.0/16"),     # Private Class C
    ipaddress.IPv4Network("169.254.0.0/16"),     # Link-local
    ipaddress.IPv4Network("0.0.0.0/8"),          # "This" network
    ipaddress.IPv4Network("100.64.0.0/10"),      # Shared address space (CGN)
    ipaddress.IPv4Network("192.0.0.0/24"),       # IETF protocol assignments
    ipaddress.IPv4Network("198.18.0.0/15"),      # Benchmark testing
    ipaddress.IPv4Network("224.0.0.0/4"),        # Multicast
    ipaddress.IPv4Network("240.0.0.0/4"),        # Reserved
    ipaddress.IPv4Network("255.255.255.255/32"), # Broadcast
]

# Private/reserved IPv6 networks to reject
_PRIVATE_IPV6_NETWORKS = [
    ipaddress.IPv6Network("::1/128"),            # Loopback
    ipaddress.IPv6Network("fe80::/10"),           # Link-local
    ipaddress.IPv6Network("fc00::/7"),            # Unique local
    ipaddress.IPv6Network("::/128"),              # Unspecified
    ipaddress.IPv6Network("::ffff:0:0/96"),       # IPv4-mapped (checked via v4)
    ipaddress.IPv6Network("ff00::/8"),            # Multicast
]


class RevocationError(Exception):
    """Raised when revocation checking encounters an unrecoverable error."""


@dataclass
class RevocationStatus:
    """Result of a revocation check."""

    revoked: bool
    reason: str | None = None
    revoked_at: str | None = None


@dataclass
class _CacheEntry:
    """Internal cache entry with expiration."""

    value: Any
    expires_at: float


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

    if isinstance(addr, ipaddress.IPv4Address):
        return any(addr in net for net in _PRIVATE_IPV4_NETWORKS)
    elif isinstance(addr, ipaddress.IPv6Address):
        # Check IPv6-mapped IPv4 addresses
        if addr.ipv4_mapped:
            return _is_private_ip(str(addr.ipv4_mapped))
        return any(addr in net for net in _PRIVATE_IPV6_NETWORKS)
    return True  # Unknown address type -- reject


def validate_uri(uri: str, allowed_ports: set[int] | None = None) -> tuple[bool, str]:
    """Validate a URI for SSRF safety BEFORE making any HTTP request.

    Resolves the hostname and checks that the resolved IP is not in any
    private/reserved range.  Rejects non-HTTP(S) schemes, non-standard
    ports (unless allowlisted), and unresolvable hostnames.

    Args:
        uri: The URI to validate.
        allowed_ports: Additional ports to allow beyond 80/443.

    Returns:
        Tuple of (is_safe, reason).  If is_safe is False, reason explains why.
    """
    parsed = urlparse(uri)

    # Scheme check
    if parsed.scheme not in ("http", "https"):
        return False, f"Rejected scheme: {parsed.scheme!r} (only http/https allowed)"

    # Hostname check
    hostname = parsed.hostname
    if not hostname:
        return False, "No hostname in URI"

    # Port check
    port = parsed.port
    valid_ports = _STANDARD_PORTS | (allowed_ports or set())
    if port is not None and port not in valid_ports:
        return False, f"Non-standard port {port} not in allowed set {valid_ports}"

    # Resolve hostname to IP addresses
    try:
        addrinfo = socket.getaddrinfo(hostname, port or 443, proto=socket.IPPROTO_TCP)
    except socket.gaierror as exc:
        return False, f"DNS resolution failed for {hostname!r}: {exc}"

    if not addrinfo:
        return False, f"No addresses resolved for {hostname!r}"

    # Check ALL resolved IPs -- reject if ANY is private
    for family, _type, _proto, _canonname, sockaddr in addrinfo:
        ip_str = sockaddr[0]
        if _is_private_ip(ip_str):
            return False, f"Resolved IP {ip_str} is in a private/reserved range"

    return True, "OK"


def _fetch_json(
    uri: str,
    timeout: float = 10.0,
    max_bytes: int = MAX_RESPONSE_BYTES,
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
    request = urllib.request.Request(
        uri,
        headers={"Accept": "application/json", "User-Agent": "VCP-SDK/2.0"},
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as resp:
            # Check Content-Length header if present
            content_length = resp.headers.get("Content-Length")
            if content_length is not None and int(content_length) > max_bytes:
                raise RevocationError(
                    f"Response Content-Length {content_length} exceeds limit of {max_bytes} bytes"
                )

            # Read with size limit
            data = resp.read(max_bytes + 1)
            if len(data) > max_bytes:
                raise RevocationError(
                    f"Response body exceeds limit of {max_bytes} bytes"
                )

            # Check redirect didn't change host (urllib follows redirects)
            final_url = resp.url
            if final_url:
                original_host = urlparse(uri).hostname
                final_host = urlparse(final_url).hostname
                if original_host != final_host:
                    raise RevocationError(
                        f"Redirect changed host from {original_host!r} to {final_host!r}"
                    )

            return json.loads(data.decode("utf-8"))  # type: ignore[no-any-return]

    except urllib.error.URLError as exc:
        raise RevocationError(f"HTTP request failed: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise RevocationError(f"Invalid JSON response: {exc}") from exc
    except TimeoutError as exc:
        raise RevocationError(f"Request timed out after {timeout}s") from exc


class RevocationChecker:
    """Check bundle revocation status via online endpoint or CRL.

    Tries check_uri first (real-time status), falls back to CRL.
    Both results are cached for cache_ttl seconds.

    Args:
        cache_ttl: Cache time-to-live in seconds.
        timeout: HTTP request timeout in seconds.
        allowed_ports: Additional ports beyond 80/443 to allow.
    """

    def __init__(
        self,
        cache_ttl: int = 300,
        timeout: float = 10.0,
        allowed_ports: set[int] | None = None,
    ) -> None:
        self._cache: dict[str, _CacheEntry] = {}
        self._crl_cache: dict[str, _CacheEntry] = {}
        self._cache_ttl = cache_ttl
        self._timeout = timeout
        self._allowed_ports = allowed_ports

    def check(self, manifest: Any) -> RevocationStatus:
        """Check if a bundle is revoked.

        Tries the online check_uri endpoint first.  If unavailable or
        erroring, falls back to the CRL.  If neither revocation URI is
        configured, returns not-revoked with a logged warning.

        Args:
            manifest: A VCP Manifest object with .timestamps.jti and
                      .revocation dict.

        Returns:
            RevocationStatus indicating whether the bundle is revoked.
        """
        jti = manifest.timestamps.jti
        revocation = manifest.revocation

        if not revocation:
            logger.warning(
                "No revocation URIs configured for bundle jti=%s; treating as not revoked",
                jti,
            )
            return RevocationStatus(revoked=False)

        check_uri = revocation.get("check_uri")
        crl_uri = revocation.get("crl_uri")

        # Try online endpoint first
        if check_uri:
            try:
                result = self._check_online(check_uri, jti)
                if result is not None:
                    return result
            except RevocationError as exc:
                logger.warning("Online revocation check failed: %s", exc)

        # Fall back to CRL
        if crl_uri:
            try:
                return self._check_crl(crl_uri, jti)
            except RevocationError as exc:
                logger.warning("CRL revocation check failed: %s", exc)

        # Neither check succeeded
        if not check_uri and not crl_uri:
            logger.warning(
                "No revocation URIs in manifest for jti=%s; treating as not revoked",
                jti,
            )
        else:
            logger.warning(
                "All revocation checks failed for jti=%s; treating as not revoked",
                jti,
            )

        return RevocationStatus(revoked=False)

    def _check_online(self, uri: str, jti: str) -> RevocationStatus | None:
        """Check revocation via online endpoint.

        GET {check_uri}?jti={jti} expecting:
            {"revoked": bool, "reason": str | null, "revoked_at": str | null}

        Args:
            uri: The check_uri from the manifest.
            jti: The bundle's unique token ID.

        Returns:
            RevocationStatus if the endpoint responds, None if unreachable.

        Raises:
            RevocationError: On SSRF rejection or critical failures.
        """
        # Check cache first
        cache_key = f"online:{uri}:{jti}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached  # type: ignore[return-value]

        # SSRF validation
        is_safe, reason = validate_uri(uri, self._allowed_ports)
        if not is_safe:
            raise RevocationError(f"SSRF protection: {reason}")

        # Build request URL
        separator = "&" if "?" in uri else "?"
        full_uri = f"{uri}{separator}jti={jti}"

        data = _fetch_json(full_uri, timeout=self._timeout)

        revoked = bool(data.get("revoked", False))
        status = RevocationStatus(
            revoked=revoked,
            reason=data.get("reason"),
            revoked_at=data.get("revoked_at"),
        )

        self._set_cached(cache_key, status)
        return status

    def _check_crl(self, uri: str, jti: str) -> RevocationStatus:
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

        Returns:
            RevocationStatus.

        Raises:
            RevocationError: On SSRF rejection or fetch failure.
        """
        # Check CRL cache first
        crl_cache_key = f"crl:{uri}"
        cached_crl = self._get_crl_cached(crl_cache_key)

        if cached_crl is None:
            # SSRF validation
            is_safe, reason = validate_uri(uri, self._allowed_ports)
            if not is_safe:
                raise RevocationError(f"SSRF protection: {reason}")

            crl_data = _fetch_json(uri, timeout=self._timeout)

            # Warn if CRL is expired
            next_update = crl_data.get("next_update")
            if next_update:
                try:
                    from datetime import datetime, timezone

                    next_dt = datetime.fromisoformat(next_update.rstrip("Z")).replace(
                        tzinfo=timezone.utc
                    )
                    if next_dt < datetime.now(timezone.utc):
                        logger.warning(
                            "CRL at %s is expired (next_update=%s); "
                            "treating entries as authoritative but stale",
                            uri,
                            next_update,
                        )
                except (ValueError, TypeError):
                    pass

            revoked_list: list[dict[str, str]] = crl_data.get("revoked", [])
            # Store as a lookup dict keyed by jti
            revoked_map: dict[str, dict[str, str]] = {
                entry["jti"]: entry for entry in revoked_list if "jti" in entry
            }
            self._set_crl_cached(crl_cache_key, revoked_map)
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
        entry = self._cache.get(key)
        if entry and entry.expires_at > time.monotonic():
            return entry.value  # type: ignore[return-value]
        if entry:
            del self._cache[key]
        return None

    def _set_cached(self, key: str, value: RevocationStatus) -> None:
        """Store a value in the cache."""
        self._cache[key] = _CacheEntry(
            value=value,
            expires_at=time.monotonic() + self._cache_ttl,
        )

    def _get_crl_cached(self, key: str) -> dict[str, dict[str, str]] | None:
        """Retrieve a non-expired CRL cache entry."""
        entry = self._crl_cache.get(key)
        if entry and entry.expires_at > time.monotonic():
            return entry.value  # type: ignore[return-value]
        if entry:
            del self._crl_cache[key]
        return None

    def _set_crl_cached(self, key: str, value: dict[str, dict[str, str]]) -> None:
        """Store a CRL in the cache."""
        self._crl_cache[key] = _CacheEntry(
            value=value,
            expires_at=time.monotonic() + self._cache_ttl,
        )

    def clear_cache(self) -> None:
        """Clear all caches."""
        self._cache.clear()
        self._crl_cache.clear()
