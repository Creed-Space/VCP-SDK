//! Revocation checking for VCP bundles.
//!
//! Provides SSRF-safe URI validation, CRL (Certificate Revocation List)
//! parsing, and a caching revocation checker. The checker supports live
//! online status endpoints, live CRL retrieval, and preloaded CRLs.
//!
//! # SSRF Protection
//!
//! All URIs are validated before any network request:
//! - Private/reserved IP ranges are rejected (IPv4 and IPv6).
//! - Only `https` is permitted for network revocation checks.
//! - Non-standard ports are rejected.
//!
//! # Network Boundaries
//!
//! The default transport resolves every hostname before connecting, rejects
//! the entire resolution set if any address is non-global, and pins the
//! validated addresses into the TLS client. Redirects, proxies, retries, and
//! transparent decompression are disabled. Response headers and bodies are
//! bounded before JSON parsing.
//!
//! # Example
//!
//! ```
//! use vcp_core::revocation::{is_private_ip, validate_uri, RevocationStatus};
//! use std::net::IpAddr;
//!
//! // SSRF validation
//! assert!(is_private_ip("127.0.0.1".parse::<IpAddr>().unwrap()));
//! assert!(!is_private_ip("8.8.8.8".parse::<IpAddr>().unwrap()));
//!
//! assert!(validate_uri("file:///etc/passwd").is_err());
//! assert!(validate_uri("https://creed.space/api/v1/revoked").is_ok());
//!
//! // Default status
//! let status = RevocationStatus::default();
//! assert!(!status.revoked);
//! ```

use std::collections::{HashMap, HashSet, VecDeque};
#[cfg(not(all(target_arch = "wasm32", target_os = "unknown")))]
use std::io::Read;
use std::net::{IpAddr, Ipv4Addr, Ipv6Addr};
#[cfg(not(all(target_arch = "wasm32", target_os = "unknown")))]
use std::net::{SocketAddr, ToSocketAddrs};
use std::sync::{Arc, LazyLock};
use std::time::{Duration, Instant};

use regex::Regex;
#[cfg(not(all(target_arch = "wasm32", target_os = "unknown")))]
use reqwest::header::{ACCEPT, CONTENT_ENCODING, CONTENT_LENGTH, CONTENT_TYPE};
#[cfg(not(all(target_arch = "wasm32", target_os = "unknown")))]
use reqwest::redirect::Policy;
#[cfg(not(all(target_arch = "wasm32", target_os = "unknown")))]
use reqwest::StatusCode;
use serde::Deserialize;
use serde_json::Value;
use url::Url;

use crate::error::{VcpError, VcpResult};

static STRICT_RFC3339: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(
        r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?(?:Z|[+-][0-9]{2}:[0-9]{2})$",
    )
    .expect("strict RFC 3339 regex is valid")
});

fn parse_strict_rfc3339(
    value: &str,
    field: &str,
) -> VcpResult<chrono::DateTime<chrono::FixedOffset>> {
    if !STRICT_RFC3339.is_match(value) {
        return Err(VcpError::RevocationError(format!(
            "invalid CRL {field}: expected strict RFC 3339"
        )));
    }
    chrono::DateTime::parse_from_rfc3339(value)
        .map_err(|error| VcpError::RevocationError(format!("invalid CRL {field}: {error}")))
}

// ── RevocationStatus ────────────────────────────────────────

/// The three possible outcomes of a revocation lookup.
#[derive(Debug, Clone, Copy, Default, PartialEq, Eq)]
pub enum RevocationDecision {
    /// The configured source established that the bundle is not revoked.
    #[default]
    NotRevoked,
    /// The configured source established that the bundle is revoked.
    Revoked,
    /// No configured source could establish a trustworthy decision.
    Unavailable,
}

/// Revocation status of a VCP bundle.
#[derive(Debug, Clone, Default)]
pub struct RevocationStatus {
    /// Exact revocation decision. Callers must reject `Unavailable` fail closed.
    pub decision: RevocationDecision,
    /// Compatibility flag that is true only for a confirmed revocation.
    pub revoked: bool,
    /// Human-readable reason for revocation, if revoked.
    pub reason: Option<String>,
    /// ISO 8601 timestamp of when the bundle was revoked, if revoked.
    pub revoked_at: Option<String>,
}

impl RevocationStatus {
    /// Create a status indicating the bundle is not revoked.
    pub fn not_revoked() -> Self {
        Self::default()
    }

    /// Create a status indicating the bundle has been revoked.
    pub fn revoked(reason: impl Into<String>, revoked_at: impl Into<String>) -> Self {
        Self {
            decision: RevocationDecision::Revoked,
            revoked: true,
            reason: Some(reason.into()),
            revoked_at: Some(revoked_at.into()),
        }
    }

    /// Create a fail-closed status for an unavailable revocation decision.
    pub fn unavailable() -> Self {
        Self {
            decision: RevocationDecision::Unavailable,
            revoked: false,
            reason: Some("revocation_status_unavailable".to_string()),
            revoked_at: None,
        }
    }

    /// Whether this result must cause verification to fail closed.
    pub fn should_reject(&self) -> bool {
        self.decision != RevocationDecision::NotRevoked
    }
}

// ── SSRF protection ─────────────────────────────────────────

/// Check whether an IP address belongs to a non-global range.
///
/// Rejects:
/// This includes private, loopback, link-local, shared, documentation,
/// benchmarking, multicast, unspecified, and reserved address space.
pub fn is_private_ip(ip: IpAddr) -> bool {
    match ip {
        IpAddr::V4(v4) => is_private_ipv4(v4),
        IpAddr::V6(v6) => is_private_ipv6(v6),
    }
}

/// IPv4 private/reserved range check.
fn is_private_ipv4(ip: Ipv4Addr) -> bool {
    let octets = ip.octets();
    matches!(
        octets,
        [0 | 10 | 127 | 224..=239 | 240..=255, ..]
        | [100, 64..=127, ..]
        | [169, 254, ..]
        | [172, 16..=31, ..]
        | [192, 0, 0 | 2, ..]
        | [192, 88, 99, ..]
        | [192, 168, ..]
        | [198, 18..=19, ..]
        | [198, 51, 100, ..]
        | [203, 0, 113, ..]
    )
}

/// IPv6 private/reserved range check.
fn is_private_ipv6(ip: Ipv6Addr) -> bool {
    if let Some(mapped) = ip.to_ipv4_mapped() {
        return is_private_ipv4(mapped);
    }
    // ::1 (loopback)
    if ip == Ipv6Addr::LOCALHOST {
        return true;
    }
    let segments = ip.segments();
    // fe80::/10 (link-local) and fec0::/10 (deprecated site-local)
    if segments[0] & 0xffc0 == 0xfe80 || segments[0] & 0xffc0 == 0xfec0 {
        return true;
    }
    // fc00::/7 (unique local address)
    if segments[0] & 0xfe00 == 0xfc00 {
        return true;
    }
    // :: (unspecified)
    if ip == Ipv6Addr::UNSPECIFIED {
        return true;
    }
    // ff00::/8 (multicast)
    if segments[0] & 0xff00 == 0xff00 {
        return true;
    }
    // 64:ff9b:1::/48 (local-use translation)
    if segments[0] == 0x0064 && segments[1] == 0xff9b && segments[2] == 0x0001 {
        return true;
    }
    // 64:ff9b::/96 (well-known NAT64 translation). Reject the translation
    // prefix rather than trusting an embedded IPv4 destination.
    if segments[..6] == [0x0064, 0xff9b, 0, 0, 0, 0] {
        return true;
    }
    // ::/96 (deprecated IPv4-compatible and other special addresses).
    // IPv4-mapped addresses were handled above.
    if segments[..6] == [0, 0, 0, 0, 0, 0] {
        return true;
    }
    // 100::/64 (discard-only)
    if segments[0] == 0x0100 && segments[1..4] == [0, 0, 0] {
        return true;
    }
    // 2001::/23 (IETF special-purpose space, including documentation and ORCHID)
    if segments[0] == 0x2001 && segments[1] <= 0x01ff {
        return true;
    }
    // 2001:db8::/32 (documentation)
    if segments[0] == 0x2001 && segments[1] == 0x0db8 {
        return true;
    }
    // 2002::/16 (deprecated 6to4)
    if segments[0] == 0x2002 {
        return true;
    }
    // 3fff::/20 (documentation)
    if segments[0] == 0x3fff && segments[1] & 0xf000 == 0 {
        return true;
    }
    // 5f00::/16 (segment-routing SIDs)
    if segments[0] == 0x5f00 {
        return true;
    }
    false
}

/// Validate a URI for safe external access (SSRF protection).
///
/// Accepts only `https` with port 443 (or no explicit port). Rejects literal
/// private or reserved IP ranges. A future network client must also resolve
/// and pin a public address before connecting.
///
/// # Errors
///
/// Returns [`VcpError::RevocationError`] if the URI is unsafe.
pub fn validate_uri(uri: &str) -> VcpResult<()> {
    // Parse scheme.
    let (scheme, rest) = uri
        .split_once("://")
        .ok_or_else(|| VcpError::RevocationError(format!("invalid URI (no scheme): {uri}")))?;

    let scheme_lower = scheme.to_ascii_lowercase();
    if scheme_lower != "https" {
        return Err(VcpError::RevocationError(format!(
            "unsupported URI scheme '{scheme}': only https is allowed"
        )));
    }

    if uri.contains('#') {
        return Err(VcpError::RevocationError(format!(
            "fragments are not allowed in URI: {uri}"
        )));
    }

    // Extract host (and optional port) from the authority portion.
    let authority = rest.split(['/', '?', '#']).next().unwrap_or(rest);
    if authority.contains('@') {
        return Err(VcpError::RevocationError(format!(
            "credentials are not allowed in URI: {uri}"
        )));
    }
    let (host, port) = if let Some(bracketed) = authority.strip_prefix('[') {
        let (address, suffix) = bracketed.split_once(']').ok_or_else(|| {
            VcpError::RevocationError(format!("invalid bracketed IPv6 host in URI: {uri}"))
        })?;
        let parsed_port =
            if suffix.is_empty() {
                None
            } else if let Some(raw_port) = suffix.strip_prefix(':') {
                Some(raw_port.parse::<u16>().map_err(|_| {
                    VcpError::RevocationError(format!("invalid port in URI: {uri}"))
                })?)
            } else {
                return Err(VcpError::RevocationError(format!(
                    "invalid authority in URI: {uri}"
                )));
            };
        (address, parsed_port)
    } else if let Some((h, p)) = authority.rsplit_once(':') {
        if h.contains(':') {
            return Err(VcpError::RevocationError(format!(
                "IPv6 hosts must be bracketed in URI: {uri}"
            )));
        }
        let parsed_port = p
            .parse::<u16>()
            .map_err(|_| VcpError::RevocationError(format!("invalid port in URI: {uri}")))?;
        (h, Some(parsed_port))
    } else {
        (authority, None)
    };

    if port.is_some_and(|port| port != 443) {
        return Err(VcpError::RevocationError(format!(
            "non-standard HTTPS port in URI: {uri}"
        )));
    }

    // If the host parses as an IP address, check for private ranges.
    // Strip brackets from IPv6 addresses.
    let clean_host = host.trim_end_matches('.').to_ascii_lowercase();
    if clean_host.is_empty()
        || clean_host.chars().any(char::is_whitespace)
        || clean_host.contains('%')
    {
        return Err(VcpError::RevocationError(format!(
            "invalid host in URI: {uri}"
        )));
    }
    if let Ok(ip) = clean_host.parse::<IpAddr>() {
        if is_private_ip(ip) {
            return Err(VcpError::RevocationError(format!(
                "private/reserved IP address in URI: {uri}"
            )));
        }
    }

    // Reject empty host.
    // Reject localhost by name.
    if clean_host == "localhost" || clean_host.ends_with(".localhost") {
        return Err(VcpError::RevocationError(format!(
            "localhost is not allowed in URI: {uri}"
        )));
    }

    Ok(())
}

/// Maximum accepted JSON response body, in bytes.
pub const MAX_RESPONSE_BYTES: usize = 327_680;
/// Maximum accepted response header count.
pub const MAX_RESPONSE_HEADERS: usize = 64;
/// Maximum aggregate response header name and value bytes.
pub const MAX_RESPONSE_HEADER_BYTES: usize = 32_768;

/// Injectable JSON transport for revocation status and CRL retrieval.
///
/// Production callers normally use [`ReqwestRevocationTransport`]. The trait
/// makes parser, cache, and fallback behavior testable without a live network.
pub trait RevocationTransport: Send + Sync {
    /// Retrieve one JSON object from an already validated revocation URI.
    ///
    /// # Errors
    ///
    /// Returns an error when URI validation, DNS resolution, transport,
    /// response-bound enforcement, or JSON decoding fails.
    fn get_json(&self, uri: &str, timeout: Duration) -> VcpResult<Value>;
}

/// HTTPS transport with DNS pinning and bounded response processing.
///
/// On `wasm32-unknown-unknown`, live blocking HTTP is unavailable. The
/// transport validates the URI and then fails closed. Browser hosts can inject
/// a custom transport or preload CRLs into [`RevocationChecker`].
#[derive(Debug, Clone, Copy, Default)]
pub struct ReqwestRevocationTransport;

#[cfg(not(all(target_arch = "wasm32", target_os = "unknown")))]
impl RevocationTransport for ReqwestRevocationTransport {
    fn get_json(&self, uri: &str, timeout: Duration) -> VcpResult<Value> {
        validate_uri(uri)?;
        if timeout.is_zero() {
            return Err(VcpError::RevocationError(
                "revocation timeout must be positive".to_string(),
            ));
        }

        let url = Url::parse(uri).map_err(|error| {
            VcpError::RevocationError(format!("invalid revocation URI: {error}"))
        })?;
        let host = url.host_str().ok_or_else(|| {
            VcpError::RevocationError("revocation URI requires a hostname".to_string())
        })?;
        let port = url.port_or_known_default().ok_or_else(|| {
            VcpError::RevocationError("revocation URI requires a known HTTPS port".to_string())
        })?;
        let addresses = resolve_public_addresses(host, port)?;

        let client = build_revocation_client(host, &addresses, timeout)?;
        let response = client
            .get(url)
            .header(ACCEPT, "application/json")
            .header("Accept-Encoding", "identity")
            .send()
            .map_err(|error| {
                VcpError::RevocationError(format!("revocation request failed: {error}"))
            })?;

        parse_json_response(response)
    }
}

#[cfg(all(target_arch = "wasm32", target_os = "unknown"))]
impl RevocationTransport for ReqwestRevocationTransport {
    fn get_json(&self, uri: &str, timeout: Duration) -> VcpResult<Value> {
        validate_uri(uri)?;
        if timeout.is_zero() {
            return Err(VcpError::RevocationError(
                "revocation timeout must be positive".to_string(),
            ));
        }
        Err(VcpError::RevocationError(
            "live revocation transport is unavailable on wasm32-unknown-unknown; inject a host transport or preload a CRL"
                .to_string(),
        ))
    }
}

#[cfg(not(all(target_arch = "wasm32", target_os = "unknown")))]
fn build_revocation_client(
    host: &str,
    addresses: &[SocketAddr],
    timeout: Duration,
) -> VcpResult<reqwest::blocking::Client> {
    let connect_timeout = std::cmp::min(timeout, Duration::from_secs(5));
    reqwest::blocking::Client::builder()
        .tls_backend_rustls()
        .https_only(true)
        .no_proxy()
        .redirect(Policy::none())
        .retry(reqwest::retry::never())
        .referer(false)
        .timeout(timeout)
        .connect_timeout(connect_timeout)
        .pool_max_idle_per_host(0)
        .http1_only()
        .http1_allow_obsolete_multiline_headers_in_responses(false)
        .http1_ignore_invalid_headers_in_responses(false)
        .http1_allow_spaces_after_header_name_in_responses(false)
        .no_gzip()
        .no_brotli()
        .no_deflate()
        .no_zstd()
        .no_hickory_dns()
        .tls_sni(true)
        .resolve_to_addrs(host, addresses)
        .build()
        .map_err(|error| {
            VcpError::RevocationError(format!("failed to build revocation client: {error}"))
        })
}

#[cfg(not(all(target_arch = "wasm32", target_os = "unknown")))]
fn parse_json_response(mut response: reqwest::blocking::Response) -> VcpResult<Value> {
    if response.status() != StatusCode::OK {
        return Err(VcpError::RevocationError(format!(
            "revocation endpoint returned HTTP {}",
            response.status()
        )));
    }

    validate_response_headers(response.headers())?;
    if response
        .headers()
        .get(CONTENT_ENCODING)
        .is_some_and(|value| !value.as_bytes().eq_ignore_ascii_case(b"identity"))
    {
        return Err(VcpError::RevocationError(
            "compressed revocation responses are not accepted".to_string(),
        ));
    }
    let content_type = response
        .headers()
        .get(CONTENT_TYPE)
        .and_then(|value| value.to_str().ok())
        .and_then(|value| value.split(';').next())
        .map(str::trim)
        .unwrap_or_default()
        .to_ascii_lowercase();
    if content_type != "application/json" && !content_type.ends_with("+json") {
        return Err(VcpError::RevocationError(
            "revocation response requires a JSON content type".to_string(),
        ));
    }
    if let Some(length) = response
        .headers()
        .get(CONTENT_LENGTH)
        .and_then(|value| value.to_str().ok())
        .and_then(|value| value.parse::<u64>().ok())
    {
        if length > MAX_RESPONSE_BYTES as u64 {
            return Err(VcpError::RevocationError(format!(
                "revocation response exceeds {MAX_RESPONSE_BYTES} bytes"
            )));
        }
    }

    let mut body = Vec::with_capacity(4096);
    response
        .by_ref()
        .take((MAX_RESPONSE_BYTES + 1) as u64)
        .read_to_end(&mut body)
        .map_err(|error| {
            VcpError::RevocationError(format!("failed to read revocation response: {error}"))
        })?;
    if body.len() > MAX_RESPONSE_BYTES {
        return Err(VcpError::RevocationError(format!(
            "revocation response exceeds {MAX_RESPONSE_BYTES} bytes"
        )));
    }
    let value: Value = serde_json::from_slice(&body)
        .map_err(|error| VcpError::RevocationError(format!("invalid revocation JSON: {error}")))?;
    if !value.is_object() {
        return Err(VcpError::RevocationError(
            "revocation response must be a JSON object".to_string(),
        ));
    }
    Ok(value)
}

#[cfg(not(all(target_arch = "wasm32", target_os = "unknown")))]
fn validate_response_headers(headers: &reqwest::header::HeaderMap) -> VcpResult<()> {
    if headers.len() > MAX_RESPONSE_HEADERS {
        return Err(VcpError::RevocationError(format!(
            "revocation response exceeds {MAX_RESPONSE_HEADERS} headers"
        )));
    }
    let total = headers
        .iter()
        .try_fold(0usize, |sum, (name, value)| {
            sum.checked_add(name.as_str().len())
                .and_then(|value_sum| value_sum.checked_add(value.as_bytes().len()))
        })
        .ok_or_else(|| {
            VcpError::RevocationError("revocation response header size overflow".to_string())
        })?;
    if total > MAX_RESPONSE_HEADER_BYTES {
        return Err(VcpError::RevocationError(format!(
            "revocation response headers exceed {MAX_RESPONSE_HEADER_BYTES} bytes"
        )));
    }
    Ok(())
}

#[cfg(not(all(target_arch = "wasm32", target_os = "unknown")))]
fn resolve_public_addresses(host: &str, port: u16) -> VcpResult<Vec<SocketAddr>> {
    let addresses = (host, port).to_socket_addrs().map_err(|error| {
        VcpError::RevocationError(format!("failed to resolve revocation host: {error}"))
    })?;
    validate_resolved_addresses(addresses)
}

#[cfg(not(all(target_arch = "wasm32", target_os = "unknown")))]
fn validate_resolved_addresses(
    addresses: impl IntoIterator<Item = SocketAddr>,
) -> VcpResult<Vec<SocketAddr>> {
    let mut addresses: Vec<_> = addresses.into_iter().collect();
    addresses.sort_unstable();
    addresses.dedup();
    if addresses.is_empty() {
        return Err(VcpError::RevocationError(
            "revocation hostname resolved to no addresses".to_string(),
        ));
    }
    if addresses.iter().any(|address| is_private_ip(address.ip())) {
        return Err(VcpError::RevocationError(
            "revocation hostname resolved to a private or reserved address".to_string(),
        ));
    }
    Ok(addresses)
}

// ── CRL types ───────────────────────────────────────────────

/// An entry in a Certificate Revocation List.
#[derive(Debug, Clone, Deserialize)]
pub struct CrlEntry {
    /// The JTI (unique identifier) of the revoked bundle.
    pub jti: String,
    /// ISO 8601 timestamp of when the bundle was revoked.
    pub revoked_at: String,
    /// Human-readable reason for revocation.
    pub reason: String,
}

/// A Certificate Revocation List (CRL) for VCP bundles.
#[derive(Debug, Clone, Deserialize)]
pub struct Crl {
    /// The issuer that published this CRL.
    pub issuer: String,
    /// ISO 8601 timestamp of when this CRL was last updated.
    pub updated_at: String,
    /// ISO 8601 timestamp of when the next update is expected.
    pub next_update: String,
    /// List of revoked bundle entries.
    pub revoked: Vec<CrlEntry>,
}

impl Crl {
    /// Look up a JTI in the CRL.
    ///
    /// Returns the matching entry if found, or `None` if the JTI is not revoked.
    pub fn find(&self, jti: &str) -> Option<&CrlEntry> {
        self.revoked.iter().find(|entry| entry.jti == jti)
    }

    fn validate(
        &self,
        expected_issuer: Option<&str>,
    ) -> VcpResult<chrono::DateTime<chrono::FixedOffset>> {
        if self.issuer.trim().is_empty() {
            return Err(VcpError::RevocationError(
                "CRL issuer must not be empty".to_string(),
            ));
        }
        if let Some(expected) = expected_issuer {
            if expected.trim().is_empty() || self.issuer != expected {
                return Err(VcpError::RevocationError(
                    "CRL issuer does not match expected issuer".to_string(),
                ));
            }
        }
        let updated_at = parse_strict_rfc3339(&self.updated_at, "updated_at")?;
        let next_update = parse_strict_rfc3339(&self.next_update, "next_update")?;
        if updated_at > next_update {
            return Err(VcpError::RevocationError(
                "CRL updated_at must not be after next_update".to_string(),
            ));
        }
        let mut seen = HashSet::new();
        for entry in &self.revoked {
            if entry.jti.trim().is_empty() {
                return Err(VcpError::RevocationError(
                    "CRL entry jti must not be empty".to_string(),
                ));
            }
            parse_strict_rfc3339(&entry.revoked_at, "revoked[].revoked_at")?;
            if entry.reason.trim().is_empty() {
                return Err(VcpError::RevocationError(
                    "CRL entry reason must not be empty".to_string(),
                ));
            }
            if !seen.insert(entry.jti.as_str()) {
                return Err(VcpError::RevocationError(format!(
                    "CRL contains duplicate jti {:?}",
                    entry.jti
                )));
            }
        }
        Ok(next_update)
    }

    /// Parse a CRL from a JSON string.
    ///
    /// # Errors
    ///
    /// Returns [`VcpError::RevocationError`] if the JSON is invalid or does
    /// not match the expected CRL structure.
    pub fn from_json(json_str: &str) -> VcpResult<Self> {
        let crl: Self = serde_json::from_str(json_str)
            .map_err(|e| VcpError::RevocationError(format!("failed to parse CRL: {e}")))?;
        crl.validate(None)?;
        Ok(crl)
    }
}

#[derive(Debug, Deserialize)]
struct OnlineRevocationResponse {
    revoked: bool,
    jti: String,
    issuer: String,
    #[serde(default)]
    reason: Option<String>,
    #[serde(default)]
    revoked_at: Option<String>,
}

impl OnlineRevocationResponse {
    fn into_status(self, expected_jti: &str, expected_issuer: &str) -> VcpResult<RevocationStatus> {
        if self.jti != expected_jti {
            return Err(VcpError::RevocationError(
                "online revocation response JTI does not match the request".to_string(),
            ));
        }
        if self.issuer != expected_issuer {
            return Err(VcpError::RevocationError(
                "online revocation response issuer does not match the request".to_string(),
            ));
        }
        if self.revoked {
            let reason = self
                .reason
                .filter(|value| !value.trim().is_empty())
                .ok_or_else(|| {
                    VcpError::RevocationError(
                        "confirmed revocation requires a non-empty reason".to_string(),
                    )
                })?;
            let revoked_at = self.revoked_at.ok_or_else(|| {
                VcpError::RevocationError("confirmed revocation requires revoked_at".to_string())
            })?;
            parse_strict_rfc3339(&revoked_at, "online.revoked_at")?;
            Ok(RevocationStatus::revoked(reason, revoked_at))
        } else {
            if self.reason.is_some() || self.revoked_at.is_some() {
                return Err(VcpError::RevocationError(
                    "non-revoked response must not include revocation details".to_string(),
                ));
            }
            Ok(RevocationStatus::not_revoked())
        }
    }
}

// ── RevocationChecker ───────────────────────────────────────

/// Synchronous revocation checker with caching.
///
/// Checks bundle revocation status via online endpoints and CRL lists.
/// Results are cached for the configured TTL to avoid redundant network
/// requests.
///
/// The default transport uses rustls, validates and pins DNS results, disables
/// redirects and proxies, and bounds every accepted response. A custom
/// transport can be injected for deterministic tests.
pub struct RevocationChecker {
    /// How long cached results remain valid.
    cache_ttl: Duration,
    /// Maximum time to wait for an HTTP response.
    timeout: Duration,
    /// Cache of revocation decisions keyed by source URI, issuer, and JTI.
    cache: HashMap<(String, String, String), CachedDecision>,
    cache_order: VecDeque<(String, String, String)>,
    /// Cache of parsed CRLs keyed by URI.
    crl_cache: HashMap<String, (Crl, Instant)>,
    crl_order: VecDeque<String>,
    max_cache_entries: usize,
    max_crl_cache_entries: usize,
    transport: Arc<dyn RevocationTransport>,
}

const DEFAULT_MAX_CACHE_ENTRIES: usize = 4096;
const DEFAULT_MAX_CRL_CACHE_ENTRIES: usize = 256;

struct CachedDecision {
    status: RevocationStatus,
    expires_at: Instant,
}

impl std::fmt::Debug for RevocationChecker {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("RevocationChecker")
            .field("cache_ttl", &self.cache_ttl)
            .field("timeout", &self.timeout)
            .field("cache_entries", &self.cache.len())
            .field("cache_order", &self.cache_order.len())
            .field("crl_entries", &self.crl_cache.len())
            .field("crl_order", &self.crl_order.len())
            .field("max_cache_entries", &self.max_cache_entries)
            .field("max_crl_cache_entries", &self.max_crl_cache_entries)
            .field("transport", &"dyn RevocationTransport")
            .finish()
    }
}

impl RevocationChecker {
    /// Create a new revocation checker.
    ///
    /// # Arguments
    ///
    /// * `cache_ttl` - How long cached results remain valid.
    /// * `timeout` - Maximum time to wait for an HTTP response.
    pub fn new(cache_ttl: Duration, timeout: Duration) -> Self {
        Self::with_limits(
            cache_ttl,
            timeout,
            DEFAULT_MAX_CACHE_ENTRIES,
            DEFAULT_MAX_CRL_CACHE_ENTRIES,
        )
    }

    /// Create a checker with explicit bounded cache capacities.
    ///
    /// # Panics
    ///
    /// Panics when either cache limit is zero.
    pub fn with_limits(
        cache_ttl: Duration,
        timeout: Duration,
        max_cache_entries: usize,
        max_crl_cache_entries: usize,
    ) -> Self {
        Self::with_limits_and_transport(
            cache_ttl,
            timeout,
            max_cache_entries,
            max_crl_cache_entries,
            Arc::new(ReqwestRevocationTransport),
        )
    }

    /// Create a checker with an injected transport.
    pub fn with_transport<T>(cache_ttl: Duration, timeout: Duration, transport: T) -> Self
    where
        T: RevocationTransport + 'static,
    {
        Self::with_limits_and_transport(
            cache_ttl,
            timeout,
            DEFAULT_MAX_CACHE_ENTRIES,
            DEFAULT_MAX_CRL_CACHE_ENTRIES,
            Arc::new(transport),
        )
    }

    fn with_limits_and_transport(
        cache_ttl: Duration,
        timeout: Duration,
        max_cache_entries: usize,
        max_crl_cache_entries: usize,
        transport: Arc<dyn RevocationTransport>,
    ) -> Self {
        assert!(
            max_cache_entries > 0,
            "decision cache limit must be positive"
        );
        assert!(
            max_crl_cache_entries > 0,
            "CRL cache limit must be positive"
        );
        assert!(!timeout.is_zero(), "revocation timeout must be positive");
        Self {
            cache_ttl,
            timeout,
            cache: HashMap::new(),
            cache_order: VecDeque::new(),
            crl_cache: HashMap::new(),
            crl_order: VecDeque::new(),
            max_cache_entries,
            max_crl_cache_entries,
            transport,
        }
    }

    fn cache_key(uri: &str, expected_issuer: Option<&str>, jti: &str) -> (String, String, String) {
        (
            uri.to_string(),
            expected_issuer.unwrap_or_default().to_string(),
            jti.to_string(),
        )
    }

    fn cached(&mut self, key: &(String, String, String)) -> Option<RevocationStatus> {
        match self.cache.get(key) {
            Some(entry) if entry.expires_at > Instant::now() => {
                return Some(entry.status.clone());
            }
            Some(_) => {}
            None => return None,
        }
        self.cache.remove(key);
        self.cache_order.retain(|candidate| candidate != key);
        None
    }

    fn insert_decision(
        &mut self,
        key: (String, String, String),
        status: RevocationStatus,
        ttl: Duration,
    ) {
        let now = Instant::now();
        self.cache.retain(|_, entry| entry.expires_at > now);
        self.cache_order
            .retain(|candidate| candidate != &key && self.cache.contains_key(candidate));
        while self.cache.len() >= self.max_cache_entries {
            let Some(oldest) = self.cache_order.pop_front() else {
                break;
            };
            self.cache.remove(&oldest);
        }
        self.cache_order.push_back(key.clone());
        self.cache.insert(
            key,
            CachedDecision {
                status,
                expires_at: now + ttl,
            },
        );
    }

    /// Check the revocation status of a bundle by JTI.
    ///
    /// Checks in order:
    /// 1. Cache (if a cached result exists and has not expired).
    /// 2. Online endpoint (if `check_uri` is provided).
    /// 3. CRL (if `crl_uri` is provided).
    ///
    /// If a configured check cannot establish status, returns a fail-closed
    /// unavailable status. A manifest with no revocation configuration remains
    /// not revoked.
    pub fn check(
        &mut self,
        jti: &str,
        check_uri: Option<&str>,
        crl_uri: Option<&str>,
    ) -> RevocationStatus {
        self.check_with_issuer(jti, check_uri, crl_uri, None)
    }

    /// Check revocation while binding CRLs and cached decisions to an issuer.
    pub fn check_with_issuer(
        &mut self,
        jti: &str,
        check_uri: Option<&str>,
        crl_uri: Option<&str>,
        expected_issuer: Option<&str>,
    ) -> RevocationStatus {
        if jti.trim().is_empty()
            || expected_issuer.is_some_and(|issuer| issuer.trim().is_empty())
            || ((check_uri.is_some() || crl_uri.is_some()) && expected_issuer.is_none())
        {
            return RevocationStatus::unavailable();
        }

        let mut attempted = false;

        // 2. Online check.
        if let Some(uri) = check_uri {
            attempted = true;
            let key = Self::cache_key(uri, expected_issuer, jti);
            if let Some(status) = self.cached(&key) {
                return status;
            }
            let Some(issuer) = expected_issuer else {
                return RevocationStatus::unavailable();
            };
            if let Ok(status) = self.check_online(uri, jti, issuer) {
                self.insert_decision(key, status.clone(), self.cache_ttl);
                return status;
            }
        }

        // 3. CRL check.
        if let Some(uri) = crl_uri {
            attempted = true;
            let key = Self::cache_key(uri, expected_issuer, jti);
            if let Some(status) = self.cached(&key) {
                return status;
            }
            if let Ok((status, freshness)) = self.check_crl(uri, jti, expected_issuer) {
                self.insert_decision(
                    key,
                    status.clone(),
                    std::cmp::min(self.cache_ttl, freshness),
                );
                return status;
            }
        }

        if attempted {
            RevocationStatus::unavailable()
        } else {
            RevocationStatus::not_revoked()
        }
    }

    /// Attempt an online revocation check against a status endpoint.
    ///
    /// Returns an error if the check cannot be performed.
    fn check_online(
        &self,
        uri: &str,
        jti: &str,
        expected_issuer: &str,
    ) -> VcpResult<RevocationStatus> {
        validate_uri(uri)?;
        let mut url = Url::parse(uri).map_err(|error| {
            VcpError::RevocationError(format!("invalid revocation URI: {error}"))
        })?;
        let retained: Vec<(String, String)> = url
            .query_pairs()
            .filter(|(key, _)| key != "jti" && key != "issuer")
            .map(|(key, value)| (key.into_owned(), value.into_owned()))
            .collect();
        url.set_query(None);
        {
            let mut query = url.query_pairs_mut();
            for (key, value) in retained {
                query.append_pair(&key, &value);
            }
            query.append_pair("jti", jti);
            query.append_pair("issuer", expected_issuer);
        }
        let value = self.transport.get_json(url.as_str(), self.timeout)?;
        let response: OnlineRevocationResponse =
            serde_json::from_value(value).map_err(|error| {
                VcpError::RevocationError(format!("invalid online revocation response: {error}"))
            })?;
        response.into_status(jti, expected_issuer)
    }

    /// Check revocation status against a cached or fetched CRL.
    ///
    /// If the CRL for the given URI is cached and not expired, uses the
    /// cached version. Otherwise attempts to fetch and parse a fresh CRL.
    fn check_crl(
        &mut self,
        uri: &str,
        jti: &str,
        expected_issuer: Option<&str>,
    ) -> VcpResult<(RevocationStatus, Duration)> {
        // Check CRL cache.
        if let Some((crl, cached_at)) = self.crl_cache.get(uri) {
            if cached_at.elapsed() < self.cache_ttl {
                return crl_lookup_status(crl, jti, expected_issuer);
            }
        }

        validate_uri(uri)?;
        let value = self.transport.get_json(uri, self.timeout)?;
        let crl: Crl = serde_json::from_value(value)
            .map_err(|error| VcpError::RevocationError(format!("failed to parse CRL: {error}")))?;
        let (_, freshness) = crl_lookup_status(&crl, jti, expected_issuer)?;
        self.insert_crl(uri, crl);
        let (crl, _) = self
            .crl_cache
            .get(uri)
            .expect("freshly inserted CRL is present");
        let (status, _) = crl_lookup_status(crl, jti, expected_issuer)?;
        Ok((status, freshness))
    }

    /// Manually insert a CRL into the cache (useful for testing and
    /// offline operation).
    pub fn insert_crl(&mut self, uri: &str, crl: Crl) {
        let uri = uri.to_string();
        self.crl_order.retain(|candidate| candidate != &uri);
        while self.crl_cache.len() >= self.max_crl_cache_entries {
            let Some(oldest) = self.crl_order.pop_front() else {
                break;
            };
            self.crl_cache.remove(&oldest);
        }
        self.crl_order.push_back(uri.clone());
        self.crl_cache.insert(uri, (crl, Instant::now()));
    }

    /// Clear all caches.
    pub fn clear_cache(&mut self) {
        self.cache.clear();
        self.cache_order.clear();
        self.crl_cache.clear();
        self.crl_order.clear();
    }
}

/// Look up a JTI in a CRL and return the appropriate status.
fn crl_lookup_status(
    crl: &Crl,
    jti: &str,
    expected_issuer: Option<&str>,
) -> VcpResult<(RevocationStatus, Duration)> {
    let next_update = crl.validate(expected_issuer)?;
    if next_update <= chrono::Utc::now() {
        return Err(VcpError::RevocationError("CRL is expired".to_string()));
    }
    let freshness = (next_update.with_timezone(&chrono::Utc) - chrono::Utc::now())
        .to_std()
        .map_err(|_| VcpError::RevocationError("CRL is expired".to_string()))?;
    let status = match crl.find(jti) {
        Some(entry) => RevocationStatus::revoked(&entry.reason, &entry.revoked_at),
        None => RevocationStatus::not_revoked(),
    };
    Ok((status, freshness))
}

// ── Tests ───────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::Mutex;

    #[derive(Clone)]
    struct FakeTransport {
        responses: Arc<Mutex<VecDeque<Result<Value, String>>>>,
        requests: Arc<Mutex<Vec<String>>>,
    }

    impl FakeTransport {
        fn new(responses: impl IntoIterator<Item = Result<Value, String>>) -> Self {
            Self {
                responses: Arc::new(Mutex::new(responses.into_iter().collect())),
                requests: Arc::new(Mutex::new(Vec::new())),
            }
        }
    }

    impl RevocationTransport for FakeTransport {
        fn get_json(&self, uri: &str, _timeout: Duration) -> VcpResult<Value> {
            self.requests.lock().unwrap().push(uri.to_string());
            self.responses
                .lock()
                .unwrap()
                .pop_front()
                .expect("fake response available")
                .map_err(VcpError::RevocationError)
        }
    }

    // ── is_private_ip tests ─────────────────────────────────

    #[test]
    fn private_ip_loopback_v4() {
        let ip: IpAddr = "127.0.0.1".parse().unwrap();
        assert!(is_private_ip(ip));
    }

    #[test]
    fn private_ip_loopback_v4_other() {
        let ip: IpAddr = "127.255.255.255".parse().unwrap();
        assert!(is_private_ip(ip));
    }

    #[test]
    fn private_ip_10_range() {
        let ip: IpAddr = "10.0.0.1".parse().unwrap();
        assert!(is_private_ip(ip));
    }

    #[test]
    fn private_ip_10_range_high() {
        let ip: IpAddr = "10.255.255.255".parse().unwrap();
        assert!(is_private_ip(ip));
    }

    #[test]
    fn private_ip_172_16_range() {
        let ip: IpAddr = "172.16.0.1".parse().unwrap();
        assert!(is_private_ip(ip));
    }

    #[test]
    fn private_ip_172_31_range() {
        let ip: IpAddr = "172.31.255.255".parse().unwrap();
        assert!(is_private_ip(ip));
    }

    #[test]
    fn not_private_172_15() {
        let ip: IpAddr = "172.15.0.1".parse().unwrap();
        assert!(!is_private_ip(ip));
    }

    #[test]
    fn not_private_172_32() {
        let ip: IpAddr = "172.32.0.1".parse().unwrap();
        assert!(!is_private_ip(ip));
    }

    #[test]
    fn private_ip_192_168_range() {
        let ip: IpAddr = "192.168.1.1".parse().unwrap();
        assert!(is_private_ip(ip));
    }

    #[test]
    fn private_ip_192_168_0() {
        let ip: IpAddr = "192.168.0.0".parse().unwrap();
        assert!(is_private_ip(ip));
    }

    #[test]
    fn private_ip_link_local() {
        let ip: IpAddr = "169.254.1.1".parse().unwrap();
        assert!(is_private_ip(ip));
    }

    #[test]
    fn private_ip_zero_network() {
        let ip: IpAddr = "0.0.0.0".parse().unwrap();
        assert!(is_private_ip(ip));
    }

    #[test]
    fn private_ip_v6_loopback() {
        let ip: IpAddr = "::1".parse().unwrap();
        assert!(is_private_ip(ip));
    }

    #[test]
    fn private_ip_v6_link_local() {
        let ip: IpAddr = "fe80::1".parse().unwrap();
        assert!(is_private_ip(ip));
    }

    #[test]
    fn private_ip_v6_unique_local() {
        let ip: IpAddr = "fc00::1".parse().unwrap();
        assert!(is_private_ip(ip));
    }

    #[test]
    fn private_ip_v6_unique_local_fd() {
        let ip: IpAddr = "fd00::1".parse().unwrap();
        assert!(is_private_ip(ip));
    }

    #[test]
    fn private_ip_v6_unspecified() {
        let ip: IpAddr = "::".parse().unwrap();
        assert!(is_private_ip(ip));
    }

    #[test]
    fn public_ip_v4() {
        let ip: IpAddr = "8.8.8.8".parse().unwrap();
        assert!(!is_private_ip(ip));
    }

    #[test]
    fn documentation_ip_v4_is_reserved() {
        let ip: IpAddr = "203.0.113.1".parse().unwrap();
        assert!(is_private_ip(ip));
    }

    #[test]
    fn documentation_ip_v6_is_reserved() {
        let ip: IpAddr = "2001:db8::1".parse().unwrap();
        assert!(is_private_ip(ip));
    }

    // ── validate_uri tests ──────────────────────────────────

    #[test]
    fn validate_uri_rejects_file_scheme() {
        let result = validate_uri("file:///etc/passwd");
        assert!(result.is_err());
        assert!(result.unwrap_err().to_string().contains("scheme"));
    }

    #[test]
    fn validate_uri_rejects_ftp_scheme() {
        let result = validate_uri("ftp://example.com/file");
        assert!(result.is_err());
    }

    #[test]
    fn validate_uri_accepts_https() {
        assert!(validate_uri("https://creed.space/api/v1/revoked").is_ok());
    }

    #[test]
    fn validate_uri_rejects_http() {
        assert!(validate_uri("http://creed.space/api/v1/revoked").is_err());
    }

    #[test]
    fn validate_uri_rejects_non_standard_port() {
        let result = validate_uri("https://example.com:8080/api");
        assert!(result.is_err());
        assert!(result.unwrap_err().to_string().contains("port"));
    }

    #[test]
    fn validate_uri_accepts_standard_port_443() {
        assert!(validate_uri("https://example.com:443/api").is_ok());
    }

    #[test]
    fn validate_uri_rejects_http_default_port_for_https() {
        assert!(validate_uri("https://example.com:80/api").is_err());
    }

    #[test]
    fn validate_uri_rejects_private_ip() {
        let result = validate_uri("https://192.168.1.1/api");
        assert!(result.is_err());
        assert!(result.unwrap_err().to_string().contains("private"));
    }

    #[test]
    fn validate_uri_rejects_loopback() {
        let result = validate_uri("https://127.0.0.1/api");
        assert!(result.is_err());
    }

    #[test]
    fn validate_uri_rejects_localhost() {
        let result = validate_uri("https://localhost/api");
        assert!(result.is_err());
        assert!(result.unwrap_err().to_string().contains("localhost"));
    }

    #[test]
    fn validate_uri_rejects_no_scheme() {
        let result = validate_uri("example.com/api");
        assert!(result.is_err());
    }

    #[test]
    fn validate_uri_rejects_credentials() {
        assert!(validate_uri("https://user:secret@example.com/revoked").is_err());
    }

    #[test]
    fn validate_uri_rejects_fragments_and_localhost_variants() {
        assert!(validate_uri("https://example.com/revoked#ignored").is_err());
        assert!(validate_uri("https://localhost./revoked").is_err());
        assert!(validate_uri("https://service.localhost/revoked").is_err());
    }

    #[test]
    fn validate_uri_rejects_reserved_literal_addresses() {
        assert!(validate_uri("https://100.64.0.1/revoked").is_err());
        assert!(validate_uri("https://192.0.2.1/revoked").is_err());
        assert!(validate_uri("https://198.18.0.1/revoked").is_err());
        assert!(validate_uri("https://[2001:db8::1]/revoked").is_err());
    }

    // ── CRL parsing tests ───────────────────────────────────

    #[test]
    fn crl_from_json_valid() {
        let json = r#"{
            "issuer": "creed-space",
            "updated_at": "2026-02-01T00:00:00Z",
            "next_update": "2026-03-01T00:00:00Z",
            "revoked": [
                {
                    "jti": "bundle-abc-123",
                    "revoked_at": "2026-01-15T12:00:00Z",
                    "reason": "content policy violation"
                },
                {
                    "jti": "bundle-def-456",
                    "revoked_at": "2026-01-20T08:00:00Z",
                    "reason": "key compromise"
                }
            ]
        }"#;

        let crl = Crl::from_json(json).unwrap();
        assert_eq!(crl.issuer, "creed-space");
        assert_eq!(crl.revoked.len(), 2);

        // Look up a known revoked JTI.
        let entry = crl.find("bundle-abc-123");
        assert!(entry.is_some());
        assert_eq!(entry.unwrap().reason, "content policy violation");

        // Look up an unknown JTI.
        assert!(crl.find("unknown-jti").is_none());
    }

    #[test]
    fn crl_from_json_empty_revoked_list() {
        let json = r#"{
            "issuer": "test",
            "updated_at": "2026-02-01T00:00:00Z",
            "next_update": "2026-03-01T00:00:00Z",
            "revoked": []
        }"#;

        let crl = Crl::from_json(json).unwrap();
        assert!(crl.revoked.is_empty());
        assert!(crl.find("any-jti").is_none());
    }

    #[test]
    fn crl_from_json_invalid() {
        let result = Crl::from_json("not valid json");
        assert!(result.is_err());
    }

    // ── RevocationStatus tests ──────────────────────────────

    #[test]
    fn revocation_status_default_not_revoked() {
        let status = RevocationStatus::default();
        assert!(!status.revoked);
        assert!(status.reason.is_none());
        assert!(status.revoked_at.is_none());
    }

    #[test]
    fn revocation_status_revoked() {
        let status = RevocationStatus::revoked("policy violation", "2026-01-15T12:00:00Z");
        assert!(status.revoked);
        assert_eq!(status.decision, RevocationDecision::Revoked);
        assert_eq!(status.reason.as_deref(), Some("policy violation"));
        assert_eq!(status.revoked_at.as_deref(), Some("2026-01-15T12:00:00Z"));
    }

    #[test]
    fn revocation_status_not_revoked() {
        let status = RevocationStatus::not_revoked();
        assert!(!status.revoked);
    }

    #[test]
    fn unavailable_is_distinct_from_confirmed_revocation() {
        let status = RevocationStatus::unavailable();
        assert_eq!(status.decision, RevocationDecision::Unavailable);
        assert!(!status.revoked);
        assert!(status.should_reject());
    }

    #[test]
    fn resolved_addresses_reject_empty_private_and_mixed_sets() {
        assert!(validate_resolved_addresses(Vec::<SocketAddr>::new()).is_err());
        assert!(validate_resolved_addresses(["127.0.0.1:443".parse().unwrap()]).is_err());
        assert!(validate_resolved_addresses([
            "8.8.8.8:443".parse().unwrap(),
            "10.0.0.1:443".parse().unwrap(),
        ])
        .is_err());
        assert_eq!(
            validate_resolved_addresses([
                "8.8.8.8:443".parse().unwrap(),
                "8.8.8.8:443".parse().unwrap(),
            ])
            .unwrap()
            .len(),
            1
        );
    }

    #[test]
    fn rejects_translation_and_compatible_ipv6() {
        for ip in ["64:ff9b::7f00:1", "64:ff9b:1::808:808", "::808:808"] {
            assert!(is_private_ip(ip.parse().unwrap()), "{ip}");
        }
        assert!(!is_private_ip("3ff0::1".parse().unwrap()));
    }

    #[test]
    fn online_transport_binds_query_and_response_to_jti_and_issuer() {
        let transport = FakeTransport::new([Ok(serde_json::json!({
            "revoked": false,
            "jti": "real-jti",
            "issuer": "issuer.example"
        }))]);
        let requests = transport.requests.clone();
        let mut checker = RevocationChecker::with_transport(
            Duration::from_secs(300),
            Duration::from_secs(5),
            transport,
        );

        let status = checker.check_with_issuer(
            "real-jti",
            Some("https://status.example/check?jti=attacker&issuer=attacker&mode=full"),
            None,
            Some("issuer.example"),
        );

        assert_eq!(status.decision, RevocationDecision::NotRevoked);
        let requested = requests.lock().unwrap().first().unwrap().clone();
        let url = Url::parse(&requested).unwrap();
        let pairs: Vec<_> = url.query_pairs().collect();
        assert_eq!(pairs.iter().filter(|(key, _)| key == "jti").count(), 1);
        assert_eq!(pairs.iter().filter(|(key, _)| key == "issuer").count(), 1);
        assert!(pairs
            .iter()
            .any(|(key, value)| key == "jti" && value == "real-jti"));
        assert!(pairs
            .iter()
            .any(|(key, value)| key == "issuer" && value == "issuer.example"));
    }

    #[test]
    fn online_response_binding_mismatch_is_unavailable() {
        let transport = FakeTransport::new([Ok(serde_json::json!({
            "revoked": false,
            "jti": "other-jti",
            "issuer": "issuer.example"
        }))]);
        let mut checker = RevocationChecker::with_transport(
            Duration::from_secs(300),
            Duration::from_secs(5),
            transport,
        );
        let status = checker.check_with_issuer(
            "real-jti",
            Some("https://status.example/check"),
            None,
            Some("issuer.example"),
        );
        assert_eq!(status.decision, RevocationDecision::Unavailable);
        assert!(!status.revoked);
    }

    #[test]
    fn live_crl_fetch_uses_injected_transport_and_caches_result() {
        let now = chrono::Utc::now();
        let transport = FakeTransport::new([Ok(serde_json::json!({
            "issuer": "issuer.example",
            "updated_at": now.to_rfc3339(),
            "next_update": (now + chrono::Duration::hours(1)).to_rfc3339(),
            "revoked": [{
                "jti": "revoked-jti",
                "revoked_at": now.to_rfc3339(),
                "reason": "key compromise"
            }]
        }))]);
        let requests = transport.requests.clone();
        let mut checker = RevocationChecker::with_transport(
            Duration::from_secs(300),
            Duration::from_secs(5),
            transport,
        );
        let uri = "https://status.example/crl.json";

        let first =
            checker.check_with_issuer("revoked-jti", None, Some(uri), Some("issuer.example"));
        let second =
            checker.check_with_issuer("revoked-jti", None, Some(uri), Some("issuer.example"));

        assert_eq!(first.decision, RevocationDecision::Revoked);
        assert_eq!(second.decision, RevocationDecision::Revoked);
        assert_eq!(requests.lock().unwrap().len(), 1);
    }

    #[test]
    fn shared_online_response_contract_matches_rust_parser() {
        let fixture: Value = serde_json::from_str(include_str!(
            "../../../conformance/security/revocation-responses.json"
        ))
        .unwrap();
        for case in fixture["vectors"].as_array().unwrap() {
            let actual = match serde_json::from_value::<OnlineRevocationResponse>(
                case["response"].clone(),
            ) {
                Ok(response) => match response.into_status(
                    case["jti"].as_str().unwrap(),
                    case["issuer"].as_str().unwrap(),
                ) {
                    Ok(status) => match status.decision {
                        RevocationDecision::NotRevoked => "not_revoked",
                        RevocationDecision::Revoked => "revoked",
                        RevocationDecision::Unavailable => "unavailable",
                    },
                    Err(_) => "unavailable",
                },
                Err(_) => "unavailable",
            };
            assert_eq!(
                actual,
                case["expected"].as_str().unwrap(),
                "case {}",
                case["id"].as_str().unwrap()
            );
        }
    }

    #[test]
    fn shared_crl_response_contract_matches_rust_parser() {
        let fixture: Value = serde_json::from_str(include_str!(
            "../../../conformance/security/revocation-crl-responses.json"
        ))
        .unwrap();
        for case in fixture["vectors"].as_array().unwrap() {
            let actual = match serde_json::from_value::<Crl>(case["response"].clone()) {
                Ok(crl) => match crl_lookup_status(
                    &crl,
                    case["jti"].as_str().unwrap(),
                    case["issuer"].as_str(),
                ) {
                    Ok((status, _)) => match status.decision {
                        RevocationDecision::NotRevoked => "not_revoked",
                        RevocationDecision::Revoked => "revoked",
                        RevocationDecision::Unavailable => "unavailable",
                    },
                    Err(_) => "unavailable",
                },
                Err(_) => "unavailable",
            };
            assert_eq!(
                actual,
                case["expected"].as_str().unwrap(),
                "case {}",
                case["id"].as_str().unwrap()
            );
        }
    }

    // ── RevocationChecker tests ─────────────────────────────

    #[test]
    fn checker_returns_not_revoked_by_default() {
        let mut checker = RevocationChecker::new(Duration::from_secs(300), Duration::from_secs(5));

        let status = checker.check("some-jti", None, None);
        assert!(!status.revoked);
    }

    #[test]
    fn checker_crl_cache_lookup() {
        let mut checker = RevocationChecker::new(Duration::from_secs(300), Duration::from_secs(5));

        let crl = Crl {
            issuer: "test".into(),
            updated_at: "2026-02-01T00:00:00Z".into(),
            next_update: (chrono::Utc::now() + chrono::Duration::days(1)).to_rfc3339(),
            revoked: vec![CrlEntry {
                jti: "revoked-bundle".into(),
                revoked_at: "2026-01-15T12:00:00Z".into(),
                reason: "key compromise".into(),
            }],
        };

        checker.insert_crl("https://creed.space/crl/2026.json", crl);

        // Check a revoked JTI.
        let status = checker.check_with_issuer(
            "revoked-bundle",
            None,
            Some("https://creed.space/crl/2026.json"),
            Some("test"),
        );
        assert!(status.revoked);
        assert_eq!(status.decision, RevocationDecision::Revoked);
        assert_eq!(status.reason.as_deref(), Some("key compromise"));

        // Check a non-revoked JTI.
        let status = checker.check_with_issuer(
            "good-bundle",
            None,
            Some("https://creed.space/crl/2026.json"),
            Some("test"),
        );
        assert!(!status.revoked);
    }

    #[test]
    fn checker_cache_is_bound_to_uri_issuer_and_jti() {
        let mut checker = RevocationChecker::new(Duration::from_secs(300), Duration::from_secs(5));

        let revoked_crl = Crl {
            issuer: "test".into(),
            updated_at: chrono::Utc::now().to_rfc3339(),
            next_update: (chrono::Utc::now() + chrono::Duration::days(1)).to_rfc3339(),
            revoked: vec![CrlEntry {
                jti: "cached-jti".into(),
                revoked_at: "2026-01-15T12:00:00Z".into(),
                reason: "test".into(),
            }],
        };
        checker.insert_crl("https://example.com/a.json", revoked_crl);
        checker.insert_crl(
            "https://example.com/b.json",
            Crl {
                issuer: "test".into(),
                updated_at: chrono::Utc::now().to_rfc3339(),
                next_update: (chrono::Utc::now() + chrono::Duration::days(1)).to_rfc3339(),
                revoked: vec![],
            },
        );

        let status = checker.check_with_issuer(
            "cached-jti",
            None,
            Some("https://example.com/a.json"),
            Some("test"),
        );
        assert!(status.revoked);
        assert_eq!(status.decision, RevocationDecision::Revoked);

        // A context-free lookup cannot reuse a prior source-specific decision.
        let status = checker.check("cached-jti", None, None);
        assert!(!status.revoked);

        let status = checker.check_with_issuer(
            "cached-jti",
            None,
            Some("https://example.com/b.json"),
            Some("test"),
        );
        assert!(!status.revoked);

        let status = checker.check_with_issuer(
            "cached-jti",
            None,
            Some("https://example.com/a.json"),
            Some("other"),
        );
        assert!(!status.revoked);
        assert_eq!(status.decision, RevocationDecision::Unavailable);
        assert_eq!(
            status.reason.as_deref(),
            Some("revocation_status_unavailable")
        );
    }

    #[test]
    fn valid_cached_decision_is_retained_across_repeated_hits() {
        let mut checker = RevocationChecker::new(Duration::from_secs(300), Duration::from_secs(5));
        let uri = "https://example.com/repeated.json";
        checker.insert_crl(
            uri,
            Crl {
                issuer: "test".into(),
                updated_at: chrono::Utc::now().to_rfc3339(),
                next_update: (chrono::Utc::now() + chrono::Duration::days(1)).to_rfc3339(),
                revoked: vec![CrlEntry {
                    jti: "repeated-jti".into(),
                    revoked_at: "2026-01-01T00:00:00Z".into(),
                    reason: "test".into(),
                }],
            },
        );

        let first = checker.check_with_issuer("repeated-jti", None, Some(uri), Some("test"));
        assert!(first.revoked);
        checker.crl_cache.clear();

        for _ in 0..2 {
            let cached = checker.check_with_issuer("repeated-jti", None, Some(uri), Some("test"));
            assert!(cached.revoked);
            assert_eq!(checker.cache.len(), 1);
        }
    }

    #[test]
    fn crl_uri_without_expected_issuer_fails_closed() {
        let mut checker = RevocationChecker::new(Duration::from_secs(300), Duration::from_secs(5));
        let uri = "https://example.com/issuer-required.json";
        checker.insert_crl(
            uri,
            Crl {
                issuer: "test".into(),
                updated_at: chrono::Utc::now().to_rfc3339(),
                next_update: (chrono::Utc::now() + chrono::Duration::days(1)).to_rfc3339(),
                revoked: vec![],
            },
        );

        let status = checker.check("clean-jti", None, Some(uri));

        assert!(!status.revoked);
        assert_eq!(status.decision, RevocationDecision::Unavailable);
        assert_eq!(
            status.reason.as_deref(),
            Some("revocation_status_unavailable")
        );
    }

    #[test]
    fn crl_validation_rejects_bad_timestamps_and_jtis() {
        for json in [
            r#"{"issuer":"test","updated_at":"2026-01-01 00:00:00Z","next_update":"2026-02-01T00:00:00Z","revoked":[]}"#,
            r#"{"issuer":"test","updated_at":"2026-01-01T00:00:00","next_update":"2026-02-01T00:00:00Z","revoked":[]}"#,
            r#"{"issuer":"test","updated_at":"2026-01-01T00:00:00.Z","next_update":"2026-02-01T00:00:00Z","revoked":[]}"#,
            r#"{"issuer":"test","updated_at":"2026-01-01T00:00:00+1:00","next_update":"2026-02-01T00:00:00Z","revoked":[]}"#,
            r#"{"issuer":"test","updated_at":"2026-03-01T00:00:00Z","next_update":"2026-02-01T00:00:00Z","revoked":[]}"#,
            r#"{"issuer":"test","updated_at":"2026-01-01T00:00:00Z","next_update":"2026-02-01T00:00:00Z","revoked":[{"jti":"missing-zone","revoked_at":"2026-01-01T00:00:00","reason":"bad"}]}"#,
            r#"{"issuer":"test","updated_at":"2026-01-01T00:00:00Z","next_update":"2026-02-01T00:00:00Z","revoked":[{"jti":"","revoked_at":"2026-01-01T00:00:00Z","reason":"bad"}]}"#,
            r#"{"issuer":"test","updated_at":"2026-01-01T00:00:00Z","next_update":"2026-02-01T00:00:00Z","revoked":[{"jti":"same","revoked_at":"2026-01-01T00:00:00Z","reason":"one"},{"jti":"same","revoked_at":"2026-01-02T00:00:00Z","reason":"two"}]}"#,
        ] {
            assert!(Crl::from_json(json).is_err(), "{json}");
        }
    }

    #[test]
    fn crl_decision_cache_is_bounded_by_next_update() {
        let mut checker =
            RevocationChecker::new(Duration::from_secs(86_400), Duration::from_secs(5));
        let now = chrono::Utc::now();
        checker.insert_crl(
            "https://example.com/short-lived.json",
            Crl {
                issuer: "test".into(),
                updated_at: now.to_rfc3339(),
                next_update: (now + chrono::Duration::seconds(10)).to_rfc3339(),
                revoked: vec![CrlEntry {
                    jti: "short-lived".into(),
                    revoked_at: now.to_rfc3339(),
                    reason: "test".into(),
                }],
            },
        );

        let status = checker.check_with_issuer(
            "short-lived",
            None,
            Some("https://example.com/short-lived.json"),
            Some("test"),
        );
        assert!(status.revoked);
        let cached = checker.cache.values().next().expect("decision cached");
        assert!(cached.expires_at <= Instant::now() + Duration::from_secs(11));
    }

    #[test]
    fn checker_rejects_empty_jti_and_expected_issuer() {
        let mut checker = RevocationChecker::new(Duration::from_secs(300), Duration::from_secs(5));
        assert_eq!(
            checker.check("", None, None).decision,
            RevocationDecision::Unavailable
        );
        assert_eq!(
            checker
                .check_with_issuer("jti", None, None, Some(" "))
                .decision,
            RevocationDecision::Unavailable
        );
    }

    #[test]
    fn checker_clear_cache() {
        let mut checker = RevocationChecker::new(Duration::from_secs(300), Duration::from_secs(5));

        let crl = Crl {
            issuer: "test".into(),
            updated_at: "2026-02-01T00:00:00Z".into(),
            next_update: (chrono::Utc::now() + chrono::Duration::days(1)).to_rfc3339(),
            revoked: vec![CrlEntry {
                jti: "cleared-jti".into(),
                revoked_at: "2026-01-15T12:00:00Z".into(),
                reason: "test".into(),
            }],
        };
        checker.insert_crl("https://example.com/crl.json", crl);

        // Populate cache.
        let status = checker.check_with_issuer(
            "cleared-jti",
            None,
            Some("https://example.com/crl.json"),
            Some("test"),
        );
        assert!(status.revoked);
        assert_eq!(status.decision, RevocationDecision::Revoked);

        // Clear and verify cache is empty.
        checker.clear_cache();
        let status = checker.check("cleared-jti", None, None);
        assert!(!status.revoked);
    }

    #[test]
    fn checker_caches_are_bounded_with_deterministic_eviction() {
        let mut checker =
            RevocationChecker::with_limits(Duration::from_secs(300), Duration::from_secs(5), 2, 1);
        checker.insert_decision(
            ("one".into(), "issuer".into(), "jti-1".into()),
            RevocationStatus::not_revoked(),
            Duration::from_secs(60),
        );
        checker.insert_decision(
            ("two".into(), "issuer".into(), "jti-2".into()),
            RevocationStatus::not_revoked(),
            Duration::from_secs(60),
        );
        checker.insert_decision(
            ("three".into(), "issuer".into(), "jti-3".into()),
            RevocationStatus::not_revoked(),
            Duration::from_secs(60),
        );
        assert_eq!(checker.cache.len(), 2);
        assert!(!checker
            .cache
            .contains_key(&("one".into(), "issuer".into(), "jti-1".into())));

        let crl = |issuer: &str| Crl {
            issuer: issuer.into(),
            updated_at: chrono::Utc::now().to_rfc3339(),
            next_update: (chrono::Utc::now() + chrono::Duration::days(1)).to_rfc3339(),
            revoked: vec![],
        };
        checker.insert_crl("https://example.com/one.json", crl("one"));
        checker.insert_crl("https://example.com/two.json", crl("two"));
        assert_eq!(checker.crl_cache.len(), 1);
        assert!(checker
            .crl_cache
            .contains_key("https://example.com/two.json"));
    }

    #[test]
    fn checker_rejects_unsafe_crl_uri() {
        let mut checker = RevocationChecker::new(Duration::from_secs(300), Duration::from_secs(5));

        // Private IP CRL URI must fail closed.
        let status = checker.check_with_issuer(
            "some-jti",
            None,
            Some("https://192.168.1.1/crl.json"),
            Some("test"),
        );
        assert!(!status.revoked);
        assert_eq!(status.decision, RevocationDecision::Unavailable);
        assert_eq!(
            status.reason.as_deref(),
            Some("revocation_status_unavailable")
        );
    }

    #[test]
    fn checker_rejects_unsafe_check_uri() {
        let mut checker = RevocationChecker::new(Duration::from_secs(300), Duration::from_secs(5));

        // Online check with private IP must fail closed.
        let status = checker.check_with_issuer(
            "some-jti",
            Some("https://10.0.0.1/revoked"),
            None,
            Some("test"),
        );
        assert!(!status.revoked);
        assert_eq!(status.decision, RevocationDecision::Unavailable);
        assert_eq!(
            status.reason.as_deref(),
            Some("revocation_status_unavailable")
        );
    }

    #[test]
    fn checker_rejects_expired_cached_crl() {
        let mut checker = RevocationChecker::new(Duration::from_secs(300), Duration::from_secs(5));
        checker.insert_crl(
            "https://example.com/crl.json",
            Crl {
                issuer: "test".into(),
                updated_at: (chrono::Utc::now() - chrono::Duration::days(2)).to_rfc3339(),
                next_update: (chrono::Utc::now() - chrono::Duration::days(1)).to_rfc3339(),
                revoked: vec![],
            },
        );

        let status = checker.check_with_issuer(
            "some-jti",
            None,
            Some("https://example.com/crl.json"),
            Some("test"),
        );
        assert!(!status.revoked);
        assert_eq!(status.decision, RevocationDecision::Unavailable);
        assert_eq!(
            status.reason.as_deref(),
            Some("revocation_status_unavailable")
        );
    }
}
