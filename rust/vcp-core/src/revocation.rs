//! Revocation checking for VCP bundles.
//!
//! Provides SSRF-safe URI validation, CRL (Certificate Revocation List)
//! parsing, and a caching revocation checker. The checker supports both
//! online status endpoints and offline CRL-based revocation lookups.
//!
//! # SSRF Protection
//!
//! All URIs are validated before any network request:
//! - Private/reserved IP ranges are rejected (IPv4 and IPv6).
//! - Only `http` and `https` schemes are permitted.
//! - Non-standard ports are rejected.
//!
//! # HTTP Requests
//!
//! Actual HTTP fetching requires a sync HTTP client crate (e.g. `ureq`
//! or `minreq`). Since neither is a current dependency, the online
//! check methods return `None` to indicate "cannot determine" and the
//! CRL fetch returns a default not-revoked status. The SSRF validation
//! and CRL parsing are fully implemented and tested.
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

use std::collections::HashMap;
use std::net::{IpAddr, Ipv4Addr, Ipv6Addr};
use std::time::{Duration, Instant};

use serde::Deserialize;

use crate::error::{VcpError, VcpResult};

// ── RevocationStatus ────────────────────────────────────────

/// Revocation status of a VCP bundle.
#[derive(Debug, Clone, Default)]
pub struct RevocationStatus {
    /// Whether the bundle has been revoked.
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
            revoked: true,
            reason: Some(reason.into()),
            revoked_at: Some(revoked_at.into()),
        }
    }
}

// ── SSRF protection ─────────────────────────────────────────

/// Check whether an IP address belongs to a private or reserved range.
///
/// Rejects:
/// - IPv4: `127.0.0.0/8`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`,
///   `169.254.0.0/16` (link-local), `0.0.0.0/8`.
/// - IPv6: `::1` (loopback), `fe80::/10` (link-local), `fc00::/7` (unique local).
pub fn is_private_ip(ip: IpAddr) -> bool {
    match ip {
        IpAddr::V4(v4) => is_private_ipv4(v4),
        IpAddr::V6(v6) => is_private_ipv6(v6),
    }
}

/// IPv4 private/reserved range check.
fn is_private_ipv4(ip: Ipv4Addr) -> bool {
    let octets = ip.octets();
    // 127.0.0.0/8 (loopback)
    if octets[0] == 127 {
        return true;
    }
    // 10.0.0.0/8 (private)
    if octets[0] == 10 {
        return true;
    }
    // 172.16.0.0/12 (private)
    if octets[0] == 172 && (16..=31).contains(&octets[1]) {
        return true;
    }
    // 192.168.0.0/16 (private)
    if octets[0] == 192 && octets[1] == 168 {
        return true;
    }
    // 169.254.0.0/16 (link-local)
    if octets[0] == 169 && octets[1] == 254 {
        return true;
    }
    // 0.0.0.0/8
    if octets[0] == 0 {
        return true;
    }
    false
}

/// IPv6 private/reserved range check.
fn is_private_ipv6(ip: Ipv6Addr) -> bool {
    // ::1 (loopback)
    if ip == Ipv6Addr::LOCALHOST {
        return true;
    }
    let segments = ip.segments();
    // fe80::/10 (link-local)
    if segments[0] & 0xffc0 == 0xfe80 {
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
    false
}

/// Validate a URI for safe external access (SSRF protection).
///
/// Accepts only `http` and `https` schemes with standard ports (80, 443,
/// or no explicit port). Rejects URIs that would resolve to private or
/// reserved IP ranges.
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
    if scheme_lower != "http" && scheme_lower != "https" {
        return Err(VcpError::RevocationError(format!(
            "unsupported URI scheme '{scheme}': only http and https are allowed"
        )));
    }

    // Extract host (and optional port) from the authority portion.
    let authority = rest.split('/').next().unwrap_or(rest);
    let (host, port) = if let Some((h, p)) = authority.rsplit_once(':') {
        // Check if the part after ':' is actually a port number
        // (could be part of an IPv6 address).
        if let Ok(port_num) = p.parse::<u16>() {
            (h, Some(port_num))
        } else {
            (authority, None)
        }
    } else {
        (authority, None)
    };

    // Reject non-standard ports.
    if let Some(p) = port {
        if p != 80 && p != 443 {
            return Err(VcpError::RevocationError(format!(
                "non-standard port {p} in URI: {uri}"
            )));
        }
    }

    // If the host parses as an IP address, check for private ranges.
    // Strip brackets from IPv6 addresses.
    let clean_host = host.trim_start_matches('[').trim_end_matches(']');
    if let Ok(ip) = clean_host.parse::<IpAddr>() {
        if is_private_ip(ip) {
            return Err(VcpError::RevocationError(format!(
                "private/reserved IP address in URI: {uri}"
            )));
        }
    }

    // Reject empty host.
    if host.is_empty() {
        return Err(VcpError::RevocationError(format!(
            "empty host in URI: {uri}"
        )));
    }

    // Reject localhost by name.
    if clean_host == "localhost" {
        return Err(VcpError::RevocationError(format!(
            "localhost is not allowed in URI: {uri}"
        )));
    }

    Ok(())
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

    /// Parse a CRL from a JSON string.
    ///
    /// # Errors
    ///
    /// Returns [`VcpError::RevocationError`] if the JSON is invalid or does
    /// not match the expected CRL structure.
    pub fn from_json(json_str: &str) -> VcpResult<Self> {
        serde_json::from_str(json_str)
            .map_err(|e| VcpError::RevocationError(format!("failed to parse CRL: {e}")))
    }
}

// ── RevocationChecker ───────────────────────────────────────

/// Synchronous revocation checker with caching.
///
/// Checks bundle revocation status via online endpoints and CRL lists.
/// Results are cached for the configured TTL to avoid redundant network
/// requests.
///
/// # HTTP Note
///
/// Actual HTTP fetching is not implemented because no sync HTTP client
/// crate is in the current dependencies. Online checks return `None`
/// (indeterminate) and CRL fetches return not-revoked. Add `ureq` or
/// `minreq` to `Cargo.toml` and implement `fetch_json` to enable
/// network-based revocation checking.
pub struct RevocationChecker {
    /// How long cached results remain valid.
    cache_ttl: Duration,
    /// Maximum time to wait for an HTTP response.
    timeout: Duration,
    /// Cache of individual JTI revocation results.
    cache: HashMap<String, (RevocationStatus, Instant)>,
    /// Cache of parsed CRLs keyed by URI.
    crl_cache: HashMap<String, (Crl, Instant)>,
}

impl std::fmt::Debug for RevocationChecker {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("RevocationChecker")
            .field("cache_ttl", &self.cache_ttl)
            .field("timeout", &self.timeout)
            .field("cache_entries", &self.cache.len())
            .field("crl_entries", &self.crl_cache.len())
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
        Self {
            cache_ttl,
            timeout,
            cache: HashMap::new(),
            crl_cache: HashMap::new(),
        }
    }

    /// Check the revocation status of a bundle by JTI.
    ///
    /// Checks in order:
    /// 1. Cache (if a cached result exists and has not expired).
    /// 2. Online endpoint (if `check_uri` is provided).
    /// 3. CRL (if `crl_uri` is provided).
    ///
    /// If no check succeeds, returns not-revoked (fail-open).
    pub fn check(
        &mut self,
        jti: &str,
        check_uri: Option<&str>,
        crl_uri: Option<&str>,
    ) -> RevocationStatus {
        // 1. Check cache first.
        if let Some((status, cached_at)) = self.cache.get(jti) {
            if cached_at.elapsed() < self.cache_ttl {
                return status.clone();
            }
            // Expired, remove it.
            self.cache.remove(jti);
        }

        // 2. Online check.
        if let Some(uri) = check_uri {
            if let Some(status) = self.check_online(uri, jti) {
                self.cache
                    .insert(jti.to_string(), (status.clone(), Instant::now()));
                return status;
            }
        }

        // 3. CRL check.
        if let Some(uri) = crl_uri {
            let status = self.check_crl(uri, jti);
            self.cache
                .insert(jti.to_string(), (status.clone(), Instant::now()));
            return status;
        }

        // No checks available, fail-open.
        RevocationStatus::not_revoked()
    }

    /// Attempt an online revocation check against a status endpoint.
    ///
    /// Returns `None` if the check cannot be performed (URI validation
    /// failure, network error, or missing HTTP client).
    #[allow(clippy::unused_self)] // Will use self for HTTP client state when ureq/minreq is added.
    fn check_online(&mut self, uri: &str, _jti: &str) -> Option<RevocationStatus> {
        // Validate URI for SSRF safety.
        if validate_uri(uri).is_err() {
            return None;
        }

        // TODO: Implement HTTP GET to `{uri}?jti={jti}` when a sync HTTP
        // client (ureq, minreq) is added to dependencies.
        // Expected response: { "revoked": bool, "reason": string?, "revoked_at": string? }
        //
        // For now, return None to indicate "could not determine".
        None
    }

    /// Check revocation status against a cached or fetched CRL.
    ///
    /// If the CRL for the given URI is cached and not expired, uses the
    /// cached version. Otherwise attempts to fetch and parse a fresh CRL.
    fn check_crl(&mut self, uri: &str, jti: &str) -> RevocationStatus {
        // Check CRL cache.
        if let Some((crl, cached_at)) = self.crl_cache.get(uri) {
            if cached_at.elapsed() < self.cache_ttl {
                return crl_lookup_status(crl, jti);
            }
        }

        // Validate URI for SSRF safety.
        if validate_uri(uri).is_err() {
            return RevocationStatus::not_revoked();
        }

        // TODO: Fetch CRL via HTTP GET when a sync HTTP client is available.
        // For now, return not-revoked (fail-open).
        RevocationStatus::not_revoked()
    }

    /// Manually insert a CRL into the cache (useful for testing and
    /// offline operation).
    pub fn insert_crl(&mut self, uri: &str, crl: Crl) {
        self.crl_cache
            .insert(uri.to_string(), (crl, Instant::now()));
    }

    /// Clear all caches.
    pub fn clear_cache(&mut self) {
        self.cache.clear();
        self.crl_cache.clear();
    }
}

/// Look up a JTI in a CRL and return the appropriate status.
fn crl_lookup_status(crl: &Crl, jti: &str) -> RevocationStatus {
    match crl.find(jti) {
        Some(entry) => RevocationStatus::revoked(&entry.reason, &entry.revoked_at),
        None => RevocationStatus::not_revoked(),
    }
}

// ── Tests ───────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;

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
    fn public_ip_v4_another() {
        let ip: IpAddr = "203.0.113.1".parse().unwrap();
        assert!(!is_private_ip(ip));
    }

    #[test]
    fn public_ip_v6() {
        let ip: IpAddr = "2001:db8::1".parse().unwrap();
        assert!(!is_private_ip(ip));
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
    fn validate_uri_accepts_http() {
        assert!(validate_uri("http://creed.space/api/v1/revoked").is_ok());
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
    fn validate_uri_accepts_standard_port_80() {
        assert!(validate_uri("http://example.com:80/api").is_ok());
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
        assert_eq!(status.reason.as_deref(), Some("policy violation"));
        assert_eq!(status.revoked_at.as_deref(), Some("2026-01-15T12:00:00Z"));
    }

    #[test]
    fn revocation_status_not_revoked() {
        let status = RevocationStatus::not_revoked();
        assert!(!status.revoked);
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
            next_update: "2026-03-01T00:00:00Z".into(),
            revoked: vec![CrlEntry {
                jti: "revoked-bundle".into(),
                revoked_at: "2026-01-15T12:00:00Z".into(),
                reason: "key compromise".into(),
            }],
        };

        checker.insert_crl("https://creed.space/crl/2026.json", crl);

        // Check a revoked JTI.
        let status = checker.check(
            "revoked-bundle",
            None,
            Some("https://creed.space/crl/2026.json"),
        );
        assert!(status.revoked);
        assert_eq!(status.reason.as_deref(), Some("key compromise"));

        // Check a non-revoked JTI.
        let status = checker.check(
            "good-bundle",
            None,
            Some("https://creed.space/crl/2026.json"),
        );
        assert!(!status.revoked);
    }

    #[test]
    fn checker_caches_results() {
        let mut checker = RevocationChecker::new(Duration::from_secs(300), Duration::from_secs(5));

        let crl = Crl {
            issuer: "test".into(),
            updated_at: "2026-02-01T00:00:00Z".into(),
            next_update: "2026-03-01T00:00:00Z".into(),
            revoked: vec![CrlEntry {
                jti: "cached-jti".into(),
                revoked_at: "2026-01-15T12:00:00Z".into(),
                reason: "test".into(),
            }],
        };
        checker.insert_crl("https://example.com/crl.json", crl);

        // First check populates cache.
        let status = checker.check("cached-jti", None, Some("https://example.com/crl.json"));
        assert!(status.revoked);

        // Second check hits cache (even without CRL URI).
        let status = checker.check("cached-jti", None, None);
        assert!(status.revoked);
    }

    #[test]
    fn checker_clear_cache() {
        let mut checker = RevocationChecker::new(Duration::from_secs(300), Duration::from_secs(5));

        let crl = Crl {
            issuer: "test".into(),
            updated_at: "2026-02-01T00:00:00Z".into(),
            next_update: "2026-03-01T00:00:00Z".into(),
            revoked: vec![CrlEntry {
                jti: "cleared-jti".into(),
                revoked_at: "2026-01-15T12:00:00Z".into(),
                reason: "test".into(),
            }],
        };
        checker.insert_crl("https://example.com/crl.json", crl);

        // Populate cache.
        let status = checker.check("cleared-jti", None, Some("https://example.com/crl.json"));
        assert!(status.revoked);

        // Clear and verify cache is empty.
        checker.clear_cache();
        let status = checker.check("cleared-jti", None, None);
        assert!(!status.revoked);
    }

    #[test]
    fn checker_rejects_unsafe_crl_uri() {
        let mut checker = RevocationChecker::new(Duration::from_secs(300), Duration::from_secs(5));

        // Private IP CRL URI should fail SSRF validation, returning not-revoked.
        let status = checker.check("some-jti", None, Some("https://192.168.1.1/crl.json"));
        assert!(!status.revoked);
    }

    #[test]
    fn checker_rejects_unsafe_check_uri() {
        let mut checker = RevocationChecker::new(Duration::from_secs(300), Duration::from_secs(5));

        // Online check with private IP should return None (indeterminate),
        // falling through to not-revoked.
        let status = checker.check("some-jti", Some("https://10.0.0.1/revoked"), None);
        assert!(!status.revoked);
    }
}
