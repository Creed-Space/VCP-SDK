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
//! - Only `https` is permitted for network revocation checks.
//! - Non-standard ports are rejected.
//!
//! # HTTP Requests
//!
//! Actual HTTP fetching requires a sync HTTP client crate. Since none is
//! currently configured, network checks fail closed as unavailable. Cached
//! CRLs remain usable until their freshness window expires.
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

use std::collections::{HashMap, HashSet};
use std::net::{IpAddr, Ipv4Addr, Ipv6Addr};
use std::sync::LazyLock;
use std::time::{Duration, Instant};

use regex::Regex;
use serde::Deserialize;

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

    /// Create a fail-closed status for an unavailable revocation decision.
    pub fn unavailable() -> Self {
        Self {
            revoked: true,
            reason: Some("revocation_status_unavailable".to_string()),
            revoked_at: None,
        }
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
    // ff00::/8 (multicast)
    if segments[0] & 0xff00 == 0xff00 {
        return true;
    }
    // 2001:db8::/32 (documentation)
    if segments[0] == 0x2001 && segments[1] == 0x0db8 {
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
/// crate is in the current dependencies. Configured network checks therefore
/// return a fail-closed unavailable status. Callers may preload a fresh CRL
/// for offline operation.
pub struct RevocationChecker {
    /// How long cached results remain valid.
    cache_ttl: Duration,
    /// Maximum time to wait for an HTTP response.
    timeout: Duration,
    /// Cache of revocation decisions keyed by source URI, issuer, and JTI.
    cache: HashMap<(String, String, String), CachedDecision>,
    /// Cache of parsed CRLs keyed by URI.
    crl_cache: HashMap<String, (Crl, Instant)>,
}

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
        None
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
            || (crl_uri.is_some() && expected_issuer.is_none())
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
            if let Ok(Some(status)) = self.check_online(uri, jti) {
                self.cache.insert(
                    key,
                    CachedDecision {
                        status: status.clone(),
                        expires_at: Instant::now() + self.cache_ttl,
                    },
                );
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
                self.cache.insert(
                    key,
                    CachedDecision {
                        status: status.clone(),
                        expires_at: Instant::now() + std::cmp::min(self.cache_ttl, freshness),
                    },
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
    #[allow(clippy::unused_self)] // Will use self for HTTP client state when ureq/minreq is added.
    fn check_online(&mut self, uri: &str, _jti: &str) -> VcpResult<Option<RevocationStatus>> {
        // Validate URI for SSRF safety.
        validate_uri(uri)?;

        // TODO: Implement HTTP GET to `{uri}?jti={jti}` when a sync HTTP
        // client (ureq, minreq) is added to dependencies.
        // Expected response: { "revoked": bool, "reason": string?, "revoked_at": string? }
        //
        Err(VcpError::RevocationError(
            "online revocation client is unavailable".to_string(),
        ))
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

        // Validate URI for SSRF safety.
        validate_uri(uri)?;

        // TODO: Fetch CRL via HTTP GET when a sync HTTP client is available.
        Err(VcpError::RevocationError(
            "CRL fetch client is unavailable".to_string(),
        ))
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
        let mut checker = RevocationChecker::new(Duration::from_mins(5), Duration::from_secs(5));

        let status = checker.check("some-jti", None, None);
        assert!(!status.revoked);
    }

    #[test]
    fn checker_crl_cache_lookup() {
        let mut checker = RevocationChecker::new(Duration::from_mins(5), Duration::from_secs(5));

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
        let mut checker = RevocationChecker::new(Duration::from_mins(5), Duration::from_secs(5));

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
        assert!(status.revoked);
        assert_eq!(
            status.reason.as_deref(),
            Some("revocation_status_unavailable")
        );
    }

    #[test]
    fn valid_cached_decision_is_retained_across_repeated_hits() {
        let mut checker = RevocationChecker::new(Duration::from_mins(5), Duration::from_secs(5));
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
        let mut checker = RevocationChecker::new(Duration::from_mins(5), Duration::from_secs(5));
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

        assert!(status.revoked);
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
        let mut checker = RevocationChecker::new(Duration::from_hours(24), Duration::from_secs(5));
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
        let mut checker = RevocationChecker::new(Duration::from_mins(5), Duration::from_secs(5));
        assert!(checker.check("", None, None).revoked);
        assert!(
            checker
                .check_with_issuer("jti", None, None, Some(" "))
                .revoked
        );
    }

    #[test]
    fn checker_clear_cache() {
        let mut checker = RevocationChecker::new(Duration::from_mins(5), Duration::from_secs(5));

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

        // Clear and verify cache is empty.
        checker.clear_cache();
        let status = checker.check("cleared-jti", None, None);
        assert!(!status.revoked);
    }

    #[test]
    fn checker_rejects_unsafe_crl_uri() {
        let mut checker = RevocationChecker::new(Duration::from_mins(5), Duration::from_secs(5));

        // Private IP CRL URI must fail closed.
        let status = checker.check_with_issuer(
            "some-jti",
            None,
            Some("https://192.168.1.1/crl.json"),
            Some("test"),
        );
        assert!(status.revoked);
        assert_eq!(
            status.reason.as_deref(),
            Some("revocation_status_unavailable")
        );
    }

    #[test]
    fn checker_rejects_unsafe_check_uri() {
        let mut checker = RevocationChecker::new(Duration::from_mins(5), Duration::from_secs(5));

        // Online check with private IP must fail closed.
        let status = checker.check("some-jti", Some("https://10.0.0.1/revoked"), None);
        assert!(status.revoked);
        assert_eq!(
            status.reason.as_deref(),
            Some("revocation_status_unavailable")
        );
    }

    #[test]
    fn checker_rejects_expired_cached_crl() {
        let mut checker = RevocationChecker::new(Duration::from_mins(5), Duration::from_secs(5));
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
        assert!(status.revoked);
        assert_eq!(
            status.reason.as_deref(),
            Some("revocation_status_unavailable")
        );
    }
}
