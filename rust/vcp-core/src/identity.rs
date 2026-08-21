//! VCP/I Token parsing and validation.
//!
//! Token format (ABNF from spec):
//! ```text
//! token     = segment 2*("." segment) ["@" version] [":" namespace]
//! segment   = ALPHA *(ALPHA / DIGIT / "-")
//! version   = 1*DIGIT "." 1*DIGIT "." 1*DIGIT
//! namespace = UPALPHA *(UPALPHA / DIGIT)
//! ```
//!
//! Minimum 3 segments, maximum 10. The first segment is the domain,
//! the last is the role, and everything in between is the path.
//!
//! # Examples
//!
//! ```
//! use vcp_core::identity::{VcpToken, SemVer};
//!
//! let token = VcpToken::parse("family.safe.guide@1.2.0").unwrap();
//! assert_eq!(token.domain(), "family");
//! assert_eq!(token.approach(), "safe");
//! assert_eq!(token.role(), "guide");
//! assert_eq!(token.version, Some(SemVer { major: 1, minor: 2, patch: 0 }));
//! assert_eq!(token.to_string(), "family.safe.guide@1.2.0");
//! ```

use std::fmt;

use regex::Regex;
use serde::de::Error as _;
use serde::{Deserialize, Deserializer, Serialize};
use unicode_normalization::UnicodeNormalization;

use crate::error::{VcpError, VcpResult};

/// Maximum total length of a raw token string.
const MAX_LENGTH: usize = 256;
/// Maximum raw input length accepted by the lossy canonicalizer.
const MAX_CANONICALIZATION_INPUT_LENGTH: usize = 4_096;
/// Maximum length of a `creed://` identity URI in its ASCII wire form.
pub const MAX_IDENTITY_URI_BYTES: usize = 518;
/// Maximum length of a single segment.
const MAX_SEGMENT_LEN: usize = 32;
/// Minimum number of dot-separated segments.
const MIN_SEGMENTS: usize = 3;
/// Maximum number of dot-separated segments.
const MAX_SEGMENTS: usize = 10;

/// Semantic version triplet `major.minor.patch`.
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct SemVer {
    pub major: u32,
    pub minor: u32,
    pub patch: u32,
}

impl SemVer {
    /// Parse a `"X.Y.Z"` string.
    ///
    /// # Errors
    ///
    /// Returns [`VcpError::ParseError`] if the string does not contain
    /// exactly three dot-separated numeric components.
    pub fn parse(s: &str) -> VcpResult<Self> {
        let parts: Vec<&str> = s.split('.').collect();
        if parts.len() != 3 {
            return Err(VcpError::ParseError(format!(
                "version must be X.Y.Z, got: {s}"
            )));
        }
        if parts.iter().any(|part| {
            part.is_empty() || part.len() > 5 || !part.as_bytes().iter().all(u8::is_ascii_digit)
        }) {
            return Err(VcpError::ParseError(format!(
                "version components must contain 1 to 5 ASCII digits: {s}"
            )));
        }
        let major = parts[0]
            .parse::<u32>()
            .map_err(|_| VcpError::ParseError(format!("invalid major version: {}", parts[0])))?;
        let minor = parts[1]
            .parse::<u32>()
            .map_err(|_| VcpError::ParseError(format!("invalid minor version: {}", parts[1])))?;
        let patch = parts[2]
            .parse::<u32>()
            .map_err(|_| VcpError::ParseError(format!("invalid patch version: {}", parts[2])))?;
        Ok(SemVer {
            major,
            minor,
            patch,
        })
    }
}

/// Selector semantics for an identity-token version.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum VersionConstraint {
    /// An unprefixed exact semantic version.
    Exact,
    /// A caret-prefixed compatible semantic version.
    Compatible,
    /// A tilde-prefixed approximate semantic version.
    Approximate,
    /// The `latest` or `canary` alias.
    Alias,
}

type ParsedVersion = (
    Option<SemVer>,
    Option<VersionConstraint>,
    Option<String>,
    Option<String>,
);

impl fmt::Display for SemVer {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}.{}.{}", self.major, self.minor, self.patch)
    }
}

/// A parsed and validated VCP/I identity token.
///
/// Tokens have the shape `domain.path*.approach.role[@version][:namespace]`
/// where there are at least 3 dot-separated segments. The first segment is
/// the *domain*, the last is the *role*, and the penultimate is the *approach*.
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize)]
pub struct VcpToken {
    /// All dot-separated segments in order.
    pub segments: Vec<String>,
    /// Optional semantic version (`@X.Y.Z`).
    pub version: Option<SemVer>,
    /// Classification of the version selector.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub version_constraint: Option<VersionConstraint>,
    /// Optional semantic-version prerelease suffix, without the leading `-`.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub version_prerelease: Option<String>,
    /// Optional version alias (`latest` or `canary`).
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub version_alias: Option<String>,
    /// Optional namespace (`:NAMESPACE`).
    pub namespace: Option<String>,
}

impl<'de> Deserialize<'de> for VcpToken {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: Deserializer<'de>,
    {
        #[derive(Deserialize)]
        #[serde(deny_unknown_fields)]
        struct WireToken {
            segments: Vec<String>,
            version: Option<SemVer>,
            #[serde(default)]
            version_constraint: Option<VersionConstraint>,
            #[serde(default)]
            version_prerelease: Option<String>,
            #[serde(default)]
            version_alias: Option<String>,
            namespace: Option<String>,
        }

        let wire = WireToken::deserialize(deserializer)?;
        let version_constraint = match (&wire.version, &wire.version_alias, wire.version_constraint)
        {
            (Some(_), None, None) => Some(VersionConstraint::Exact),
            (_, _, constraint) => constraint,
        };
        let token = VcpToken {
            segments: wire.segments,
            version: wire.version,
            version_constraint,
            version_prerelease: wire.version_prerelease,
            version_alias: wire.version_alias,
            namespace: wire.namespace,
        };
        let parsed = VcpToken::parse(&token.full()).map_err(D::Error::custom)?;
        if parsed != token {
            return Err(D::Error::custom(
                "identity token fields form an inconsistent version state",
            ));
        }
        Ok(token)
    }
}

impl VcpToken {
    // ── Parsing ─────────────────────────────────────────────

    /// Parse and validate a raw VCP/I token string.
    ///
    /// Accepts the format: `seg1.seg2.seg3[.segN...][@version][:namespace]`
    ///
    /// # Errors
    ///
    /// Returns [`VcpError::MalformedToken`] if the token is empty, exceeds
    /// the maximum length, has too few or too many segments, or contains
    /// invalid characters. Returns [`VcpError::ParseError`] if the version
    /// string is malformed.
    pub fn parse(raw: &str) -> VcpResult<Self> {
        Self::parse_token(raw)
    }

    fn parse_token(raw: &str) -> VcpResult<Self> {
        if raw.is_empty() {
            return Err(VcpError::MalformedToken("token cannot be empty".into()));
        }
        if raw.len() > MAX_LENGTH {
            return Err(VcpError::MalformedToken(format!(
                "token exceeds max length {MAX_LENGTH}: {}",
                raw.len()
            )));
        }

        let mut remaining = raw;

        // Extract namespace (last `:` suffix).
        let namespace = if let Some(colon_idx) = remaining.rfind(':') {
            // Namespace must come after any `@` version.
            let ns_str = &remaining[colon_idx + 1..];
            Self::validate_namespace(ns_str)?;
            remaining = &remaining[..colon_idx];
            Some(ns_str.to_string())
        } else {
            None
        };

        // Extract version (`@X.Y.Z`).
        let (version, version_constraint, version_prerelease, version_alias) =
            if let Some(at_idx) = remaining.rfind('@') {
                let ver_str = &remaining[at_idx + 1..];
                let parsed = Self::parse_version(ver_str)?;
                remaining = &remaining[..at_idx];
                parsed
            } else {
                (None, None, None, None)
            };

        // Remaining string is the dot-separated path.
        let segments: Vec<String> = remaining.split('.').map(String::from).collect();

        if segments.len() < MIN_SEGMENTS {
            return Err(VcpError::MalformedToken(format!(
                "token requires at least {MIN_SEGMENTS} segments, got {}",
                segments.len()
            )));
        }
        if segments.len() > MAX_SEGMENTS {
            return Err(VcpError::MalformedToken(format!(
                "token exceeds maximum {MAX_SEGMENTS} segments, got {}",
                segments.len()
            )));
        }

        for (i, seg) in segments.iter().enumerate() {
            Self::validate_segment(seg, i)?;
        }

        Ok(VcpToken {
            segments,
            version,
            version_constraint,
            version_prerelease,
            version_alias,
            namespace,
        })
    }

    /// Parse a strict VCP/I URI into its canonical token representation.
    ///
    /// `creed://` URIs require a DNS issuer and accept either the canonical
    /// dotted token path or the legacy slash-separated path. The alternative
    /// `vcp://` form carries the canonical dotted token directly. URI
    /// namespaces, queries, fragments, percent escapes, user information,
    /// ports, IP authorities, and mixed dotted/slash paths are rejected.
    ///
    /// # Errors
    ///
    /// Returns [`VcpError::MalformedToken`] for an unsupported, oversized, or
    /// ambiguous URI, or the underlying token parsing error when the decoded
    /// identity is invalid.
    pub fn from_uri(raw: &str) -> VcpResult<Self> {
        if raw.is_empty() || raw.len() > MAX_IDENTITY_URI_BYTES {
            return Err(VcpError::MalformedToken(format!(
                "identity URI must contain 1 to {MAX_IDENTITY_URI_BYTES} bytes"
            )));
        }
        if !raw.is_ascii()
            || raw
                .bytes()
                .any(|byte| byte.is_ascii_whitespace() || byte.is_ascii_control())
            || raw.contains(['?', '#', '%', '\\'])
        {
            return Err(VcpError::MalformedToken(
                "identity URI contains forbidden or non-ASCII characters".into(),
            ));
        }

        if let Some(rest) = raw.strip_prefix("creed://") {
            let Some((issuer, identity)) = rest.split_once('/') else {
                return Err(VcpError::MalformedToken(
                    "creed identity URI requires an issuer and path".into(),
                ));
            };
            Self::validate_uri_issuer(issuer)?;
            return Self::parse_uri_identity(identity, true);
        }
        if let Some(identity) = raw.strip_prefix("vcp://") {
            return Self::parse_uri_identity(identity, false);
        }
        Err(VcpError::MalformedToken(
            "identity URI scheme must be creed:// or vcp://".into(),
        ))
    }

    fn parse_uri_identity(identity: &str, allow_legacy_slashes: bool) -> VcpResult<Self> {
        if identity.is_empty() || identity.contains(':') {
            return Err(VcpError::MalformedToken(
                "identity URI path is empty or contains a namespace".into(),
            ));
        }
        let path_end = identity.find('@').unwrap_or(identity.len());
        let path = &identity[..path_end];
        let suffix = &identity[path_end..];
        let canonical_path = if path.contains('/') {
            if !allow_legacy_slashes
                || path.contains('.')
                || path.starts_with('/')
                || path.ends_with('/')
                || path.split('/').any(str::is_empty)
            {
                return Err(VcpError::MalformedToken(
                    "identity URI has an ambiguous slash path".into(),
                ));
            }
            path.replace('/', ".")
        } else {
            path.to_string()
        };
        Self::parse_token(&format!("{canonical_path}{suffix}"))
    }

    fn validate_uri_issuer(issuer: &str) -> VcpResult<()> {
        let valid = !issuer.is_empty()
            && issuer.len() <= 253
            && issuer.bytes().any(|byte| byte.is_ascii_alphabetic())
            && issuer.split('.').all(|label| {
                !label.is_empty()
                    && label.len() <= 63
                    && label
                        .bytes()
                        .all(|byte| byte.is_ascii_alphanumeric() || byte == b'-')
                    && label
                        .as_bytes()
                        .first()
                        .is_some_and(u8::is_ascii_alphanumeric)
                    && label
                        .as_bytes()
                        .last()
                        .is_some_and(u8::is_ascii_alphanumeric)
            });
        if !valid {
            return Err(VcpError::MalformedToken(
                "identity URI issuer must be a valid DNS name".into(),
            ));
        }
        Ok(())
    }

    /// Canonicalize and validate a potentially non-canonical identity token.
    ///
    /// The token path and version are lowercased after Unicode NFKC
    /// normalization. Whitespace is removed, dot runs are collapsed, numeric
    /// semantic-version components lose redundant leading zeroes, and the
    /// namespace is normalized to the uppercase form required by the grammar.
    ///
    /// # Errors
    ///
    /// Returns a [`VcpError`] when the input is empty, cannot be normalized,
    /// contains an out-of-range semantic-version component, or does not parse
    /// as a valid canonical token.
    pub fn canonicalize(raw: &str) -> VcpResult<String> {
        if raw.is_empty() {
            return Err(VcpError::MalformedToken("token cannot be empty".into()));
        }
        if raw.len() > MAX_CANONICALIZATION_INPUT_LENGTH {
            return Err(VcpError::MalformedToken(format!(
                "canonicalization input exceeds max length {MAX_CANONICALIZATION_INPUT_LENGTH}: {}",
                raw.len()
            )));
        }
        let compact: String = raw
            .nfkc()
            .filter(|character| !character.is_whitespace())
            .collect();

        let (without_namespace, namespace) = if let Some(index) = compact.rfind(':') {
            (&compact[..index], Some(compact[index + 1..].to_uppercase()))
        } else {
            (compact.as_str(), None)
        };
        let (raw_path, version) = if let Some(index) = without_namespace.rfind('@') {
            let raw_version = without_namespace[index + 1..].to_lowercase();
            let (prefix, numeric) = if raw_version.starts_with(['^', '~']) {
                (&raw_version[..1], &raw_version[1..])
            } else {
                ("", raw_version.as_str())
            };
            let version_pattern =
                Regex::new(r"^(\d+)\.(\d+)\.(\d+)(-[a-z0-9.-]+)?$").map_err(|error| {
                    VcpError::ParseError(format!("internal version pattern failed: {error}"))
                })?;
            let normalized_version = if let Some(captures) = version_pattern.captures(numeric) {
                format!(
                    "{}{}.{}.{}{}",
                    prefix,
                    captures[1].parse::<u32>().map_err(|_| {
                        VcpError::ParseError("version component out of range".into())
                    })?,
                    captures[2].parse::<u32>().map_err(|_| {
                        VcpError::ParseError("version component out of range".into())
                    })?,
                    captures[3].parse::<u32>().map_err(|_| {
                        VcpError::ParseError("version component out of range".into())
                    })?,
                    captures.get(4).map_or("", |value| value.as_str()),
                )
            } else {
                format!("{prefix}{numeric}")
            };
            (&without_namespace[..index], Some(normalized_version))
        } else {
            (without_namespace, None)
        };

        let path = raw_path
            .to_lowercase()
            .split('.')
            .filter(|segment| !segment.is_empty())
            .collect::<Vec<_>>()
            .join(".");
        let mut candidate = path;
        if let Some(version) = version {
            candidate.push('@');
            candidate.push_str(&version);
        }
        if let Some(namespace) = namespace {
            candidate.push(':');
            candidate.push_str(&namespace);
        }
        Ok(Self::parse(&candidate)?.full())
    }

    // ── Accessors ───────────────────────────────────────────

    /// First segment -- the domain / category.
    pub fn domain(&self) -> &str {
        &self.segments[0]
    }

    /// Penultimate segment -- the approach / method.
    pub fn approach(&self) -> &str {
        &self.segments[self.segments.len() - 2]
    }

    /// Last segment -- the role / function.
    pub fn role(&self) -> &str {
        &self.segments[self.segments.len() - 1]
    }

    /// Middle segments between domain and approach (empty for 3-segment tokens).
    pub fn path(&self) -> &[String] {
        if self.segments.len() <= 3 {
            &[]
        } else {
            &self.segments[1..self.segments.len() - 2]
        }
    }

    /// Canonical form: all segments joined (no version/namespace).
    pub fn canonical(&self) -> String {
        self.segments.join(".")
    }

    /// Full form including version and namespace if present.
    pub fn full(&self) -> String {
        let mut s = self.canonical();
        if let Some(ver) = self.version_text() {
            s.push('@');
            s.push_str(&ver);
        }
        if let Some(ref ns) = self.namespace {
            s.push(':');
            s.push_str(ns);
        }
        s
    }

    /// Number of segments.
    pub fn depth(&self) -> usize {
        self.segments.len()
    }

    /// Convert to a VCP/T bundle URI.
    pub fn to_uri(&self, registry: &str) -> String {
        let ver_part = self
            .version_text()
            .map(|v| format!("@{v}"))
            .unwrap_or_default();
        format!("creed://{}/{}{}", registry, self.canonical(), ver_part)
    }

    // ── Builders ────────────────────────────────────────────

    /// Return a new token with the given version.
    #[must_use]
    pub fn with_version(&self, version: SemVer) -> Self {
        VcpToken {
            segments: self.segments.clone(),
            version: Some(version),
            version_constraint: Some(VersionConstraint::Exact),
            version_prerelease: None,
            version_alias: None,
            namespace: self.namespace.clone(),
        }
    }

    /// Return a new token with the given namespace.
    ///
    /// # Errors
    ///
    /// Returns [`VcpError::MalformedToken`] if the namespace is empty,
    /// does not start with an uppercase letter, or contains invalid
    /// characters.
    pub fn with_namespace(&self, namespace: &str) -> VcpResult<Self> {
        Self::validate_namespace(namespace)?;
        Ok(VcpToken {
            segments: self.segments.clone(),
            version: self.version.clone(),
            version_constraint: self.version_constraint,
            version_prerelease: self.version_prerelease.clone(),
            version_alias: self.version_alias.clone(),
            namespace: Some(namespace.to_string()),
        })
    }

    /// Return the parent token (one segment shorter), or `None` at minimum depth.
    pub fn parent(&self) -> Option<Self> {
        if self.segments.len() <= MIN_SEGMENTS {
            return None;
        }
        Some(VcpToken {
            segments: self.segments[..self.segments.len() - 1].to_vec(),
            version: None,
            version_constraint: None,
            version_prerelease: None,
            version_alias: None,
            namespace: self.namespace.clone(),
        })
    }

    /// Return a child token with an appended segment.
    ///
    /// # Errors
    ///
    /// Returns [`VcpError::MalformedToken`] if the segment is invalid or
    /// the token is already at maximum depth.
    pub fn child(&self, segment: &str) -> VcpResult<Self> {
        Self::validate_segment(segment, self.segments.len())?;
        if self.segments.len() >= MAX_SEGMENTS {
            return Err(VcpError::MalformedToken(format!(
                "cannot add segment: max depth {MAX_SEGMENTS}"
            )));
        }
        let mut segs = self.segments.clone();
        segs.push(segment.to_string());
        Ok(VcpToken {
            segments: segs,
            version: None,
            version_constraint: None,
            version_prerelease: None,
            version_alias: None,
            namespace: self.namespace.clone(),
        })
    }

    /// Check whether this token's segments are a prefix of `other`.
    pub fn is_ancestor_of(&self, other: &VcpToken) -> bool {
        if self.segments.len() >= other.segments.len() {
            return false;
        }
        other.segments[..self.segments.len()] == self.segments[..]
    }

    /// Check whether `other`'s segments are a prefix of this token's.
    pub fn is_descendant_of(&self, other: &VcpToken) -> bool {
        other.is_ancestor_of(self)
    }

    /// Check whether this token matches a glob-like pattern.
    ///
    /// Supports `*` as a single-segment wildcard and `**` as a
    /// multi-segment wildcard.
    pub fn matches_pattern(&self, pattern: &str) -> bool {
        let parts: Vec<&str> = pattern.split('.').collect();

        if let Some(star_idx) = parts.iter().position(|p| *p == "**") {
            let prefix = &parts[..star_idx];
            let suffix = &parts[star_idx + 1..];

            if self.segments.len() < prefix.len() + suffix.len() {
                return false;
            }

            for (i, p) in prefix.iter().enumerate() {
                if *p != "*" && *p != self.segments[i] {
                    return false;
                }
            }

            for (i, p) in suffix.iter().enumerate() {
                let seg_idx = self.segments.len() - suffix.len() + i;
                if *p != "*" && *p != self.segments[seg_idx] {
                    return false;
                }
            }

            return true;
        }

        if parts.len() != self.segments.len() {
            return false;
        }

        parts
            .iter()
            .zip(self.segments.iter())
            .all(|(pat, seg)| *pat == "*" || *pat == seg.as_str())
    }

    // ── Validation helpers ──────────────────────────────────

    fn validate_segment(seg: &str, index: usize) -> VcpResult<()> {
        if seg.is_empty() {
            return Err(VcpError::MalformedToken(format!(
                "segment {index} is empty"
            )));
        }
        if seg.len() > MAX_SEGMENT_LEN {
            return Err(VcpError::MalformedToken(format!(
                "segment {index} exceeds max length {MAX_SEGMENT_LEN}: {seg}"
            )));
        }
        let mut chars = seg.chars();
        let first = chars.next().unwrap(); // safe: non-empty
        if !first.is_ascii_lowercase() {
            return Err(VcpError::MalformedToken(format!(
                "segment must start with lowercase letter, got '{first}' in '{seg}'"
            )));
        }
        for ch in chars {
            if !(ch.is_ascii_lowercase() || ch.is_ascii_digit() || ch == '-') {
                return Err(VcpError::MalformedToken(format!(
                    "invalid character '{ch}' in segment '{seg}'"
                )));
            }
        }
        Ok(())
    }

    fn parse_version(raw: &str) -> VcpResult<ParsedVersion> {
        if matches!(raw, "latest" | "canary") {
            return Ok((
                None,
                Some(VersionConstraint::Alias),
                None,
                Some(raw.to_string()),
            ));
        }

        let (constraint, numeric) = match raw.as_bytes().first() {
            Some(b'^') => (VersionConstraint::Compatible, &raw[1..]),
            Some(b'~') => (VersionConstraint::Approximate, &raw[1..]),
            _ => (VersionConstraint::Exact, raw),
        };
        let (numeric, prerelease) = if let Some((numeric, prerelease)) = numeric.split_once('-') {
            if prerelease.is_empty()
                || !prerelease
                    .as_bytes()
                    .iter()
                    .all(|byte| byte.is_ascii_alphanumeric() || matches!(byte, b'.' | b'-'))
            {
                return Err(VcpError::ParseError(format!(
                    "invalid version prerelease: {prerelease}"
                )));
            }
            (numeric, Some(prerelease.to_ascii_lowercase()))
        } else {
            (numeric, None)
        };
        Ok((
            Some(SemVer::parse(numeric)?),
            Some(constraint),
            prerelease,
            None,
        ))
    }

    /// Return the canonical complete version selector.
    pub fn version_text(&self) -> Option<String> {
        if let Some(alias) = &self.version_alias {
            return Some(alias.clone());
        }
        let version = self.version.as_ref()?;
        let prefix = match self.version_constraint {
            Some(VersionConstraint::Compatible) => "^",
            Some(VersionConstraint::Approximate) => "~",
            _ => "",
        };
        let prerelease = self
            .version_prerelease
            .as_ref()
            .map(|value| format!("-{value}"))
            .unwrap_or_default();
        Some(format!("{prefix}{version}{prerelease}"))
    }

    fn validate_namespace(ns: &str) -> VcpResult<()> {
        if ns.is_empty() {
            return Err(VcpError::MalformedToken("namespace cannot be empty".into()));
        }
        if ns.len() > MAX_SEGMENT_LEN {
            return Err(VcpError::MalformedToken(format!(
                "namespace exceeds max length {MAX_SEGMENT_LEN}: {ns}"
            )));
        }
        let mut chars = ns.chars();
        let first = chars.next().unwrap();
        if !first.is_ascii_uppercase() {
            return Err(VcpError::MalformedToken(format!(
                "namespace must start with uppercase letter, got '{first}'"
            )));
        }
        for ch in chars {
            if !(ch.is_ascii_uppercase() || ch.is_ascii_digit()) {
                return Err(VcpError::MalformedToken(format!(
                    "invalid namespace character: '{ch}'"
                )));
            }
        }
        Ok(())
    }
}

impl fmt::Display for VcpToken {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(&self.full())
    }
}

// ── Tests ───────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;
    use pretty_assertions::assert_eq;

    // ── Parsing ─────────────────────────────────────────

    #[test]
    fn parse_minimal_3_segment() {
        let t = VcpToken::parse("family.safe.guide").unwrap();
        assert_eq!(t.domain(), "family");
        assert_eq!(t.approach(), "safe");
        assert_eq!(t.role(), "guide");
        assert_eq!(t.version, None);
        assert_eq!(t.namespace, None);
        assert!(t.path().is_empty());
    }

    #[test]
    fn parse_with_version() {
        let t = VcpToken::parse("family.safe.guide@1.2.0").unwrap();
        assert_eq!(
            t.version,
            Some(SemVer {
                major: 1,
                minor: 2,
                patch: 0
            })
        );
    }

    #[test]
    fn standalone_identity_accepts_and_normalizes_leading_zero_version() {
        let token = VcpToken::parse("family.safe.guide@01.002.00003").unwrap();
        assert_eq!(
            token.version,
            Some(SemVer {
                major: 1,
                minor: 2,
                patch: 3
            })
        );
        assert_eq!(token.full(), "family.safe.guide@1.2.3");
        assert_eq!(
            token.to_uri("creed.space"),
            "creed://creed.space/family.safe.guide@1.2.3"
        );
    }

    #[test]
    fn standalone_identity_normalizes_selector_and_prerelease_case() {
        let token = VcpToken::parse("family.safe.guide@^00001.00002.00003-RC.1").unwrap();
        assert_eq!(token.version_text().as_deref(), Some("^1.2.3-rc.1"));
        assert_eq!(token.full(), "family.safe.guide@^1.2.3-rc.1");
        assert_eq!(
            token.to_uri("creed.space"),
            "creed://creed.space/family.safe.guide@^1.2.3-rc.1"
        );
    }

    #[test]
    fn canonicalization_input_limit_is_inclusive() {
        let token = "a.b.c";
        let at_limit = format!(
            "{}{token}",
            " ".repeat(MAX_CANONICALIZATION_INPUT_LENGTH - token.len())
        );
        assert_eq!(at_limit.len(), MAX_CANONICALIZATION_INPUT_LENGTH);
        assert_eq!(VcpToken::canonicalize(&at_limit).unwrap(), token);
        assert!(VcpToken::canonicalize(&format!(" {at_limit}")).is_err());
    }

    #[test]
    fn parse_with_namespace() {
        let t = VcpToken::parse("company.acme.legal.compliance:SEC").unwrap();
        assert_eq!(t.namespace.as_deref(), Some("SEC"));
        assert_eq!(t.depth(), 4);
    }

    #[test]
    fn parse_with_version_and_namespace() {
        let t = VcpToken::parse("org.example.dept.team.policy@1.0.0:GOV").unwrap();
        assert_eq!(t.depth(), 5);
        assert_eq!(
            t.version,
            Some(SemVer {
                major: 1,
                minor: 0,
                patch: 0
            })
        );
        assert_eq!(t.namespace.as_deref(), Some("GOV"));
    }

    #[test]
    fn parse_preserves_selectors_prereleases_and_aliases() {
        for (raw, constraint) in [
            (
                "my-org.safe-net.web-guard@^2.0.0",
                VersionConstraint::Compatible,
            ),
            (
                "my-org.safe-net.web-guard@~2.1.3-beta.1",
                VersionConstraint::Approximate,
            ),
            ("my-org.safe-net.web-guard@latest", VersionConstraint::Alias),
            ("my-org.safe-net.web-guard@canary", VersionConstraint::Alias),
        ] {
            let token = VcpToken::parse(raw).unwrap();
            assert_eq!(token.version_constraint, Some(constraint));
            assert_eq!(token.full(), raw);
            assert_eq!(
                token.to_uri("creed.space"),
                format!("creed://creed.space/{raw}")
            );
        }
    }

    #[test]
    fn parse_with_hyphens() {
        let t = VcpToken::parse("my-org.safe-net.web-guard").unwrap();
        assert_eq!(t.domain(), "my-org");
        assert_eq!(t.role(), "web-guard");
    }

    // ── Display roundtrip ───────────────────────────────

    #[test]
    fn roundtrip_simple() {
        let raw = "family.safe.guide";
        let t = VcpToken::parse(raw).unwrap();
        assert_eq!(t.to_string(), raw);
    }

    #[test]
    fn roundtrip_full() {
        let raw = "company.acme.legal.compliance@2.1.0:SEC";
        let t = VcpToken::parse(raw).unwrap();
        assert_eq!(t.to_string(), raw);
    }

    #[test]
    fn deserialization_rejects_corrupt_identity_state() {
        let token = VcpToken::parse("my-org.safe.web@^2.0.0:SEC").unwrap();
        let valid = serde_json::to_value(&token).unwrap();
        assert_eq!(serde_json::from_value::<VcpToken>(valid).unwrap(), token);

        for invalid in [
            serde_json::json!({
                "segments": [], "version": null, "namespace": null
            }),
            serde_json::json!({
                "segments": ["a", "b", "c"],
                "version": {"major": 100_000, "minor": 0, "patch": 0},
                "version_constraint": "exact", "namespace": null
            }),
            serde_json::json!({
                "segments": ["a", "b", "c"],
                "version": {"major": 1, "minor": 2, "patch": 3},
                "version_constraint": "alias", "version_alias": "latest",
                "namespace": null
            }),
            serde_json::json!({
                "segments": ["a", "b", "c"], "version": null,
                "version_constraint": "alias", "version_alias": "stable",
                "namespace": null
            }),
            serde_json::json!({
                "segments": ["a", "b", "c"], "version": null,
                "namespace": null, "unexpected": true
            }),
        ] {
            assert!(serde_json::from_value::<VcpToken>(invalid).is_err());
        }
    }

    // ── Errors ──────────────────────────────────────────

    #[test]
    fn empty_token() {
        assert!(VcpToken::parse("").is_err());
    }

    #[test]
    fn too_few_segments() {
        assert!(VcpToken::parse("one.two").is_err());
    }

    #[test]
    fn uppercase_segment() {
        assert!(VcpToken::parse("Family.safe.guide").is_err());
    }

    #[test]
    fn invalid_version() {
        assert!(VcpToken::parse("a.b.c@1.2").is_err());
        for invalid in [
            "a.b.c@100000.2.3",
            "a.b.c@^1.2",
            "a.b.c@~1.2.3-",
            "a.b.c@LATEST",
            "a.b.c@^^1.2.3",
            "a.b.c@1.2.3+build",
        ] {
            assert!(VcpToken::parse(invalid).is_err(), "accepted {invalid}");
        }
    }

    #[test]
    fn invalid_namespace_lowercase() {
        assert!(VcpToken::parse("a.b.c:sec").is_err());
        assert!(VcpToken::parse(&format!("a.b.c:{}", "N".repeat(33))).is_err());
    }

    #[test]
    fn segment_too_long() {
        let long = "a".repeat(33);
        let raw = format!("{long}.b.c");
        assert!(VcpToken::parse(&raw).is_err());
    }

    #[test]
    fn too_many_segments() {
        let raw = (1..=11)
            .map(|i| format!("s{i}"))
            .collect::<Vec<_>>()
            .join(".");
        assert!(VcpToken::parse(&raw).is_err());
    }

    // ── Hierarchy ───────────────────────────────────────

    #[test]
    fn parent_and_child() {
        let t = VcpToken::parse("company.acme.legal.compliance").unwrap();
        let parent = t.parent().unwrap();
        assert_eq!(parent.canonical(), "company.acme.legal");

        let child = parent.child("compliance").unwrap();
        assert_eq!(child.canonical(), "company.acme.legal.compliance");
    }

    #[test]
    fn parent_at_min_depth() {
        let t = VcpToken::parse("a.b.c").unwrap();
        assert!(t.parent().is_none());
    }

    #[test]
    fn ancestor_descendant() {
        let ancestor = VcpToken::parse("company.acme.legal").unwrap();
        let descendant = VcpToken::parse("company.acme.legal.compliance").unwrap();
        assert!(ancestor.is_ancestor_of(&descendant));
        assert!(descendant.is_descendant_of(&ancestor));
        assert!(!descendant.is_ancestor_of(&ancestor));
    }

    // ── Pattern matching ────────────────────────────────

    #[test]
    fn pattern_wildcard() {
        let t = VcpToken::parse("family.safe.guide").unwrap();
        assert!(t.matches_pattern("family.*.guide"));
        assert!(!t.matches_pattern("family.*.policy"));
    }

    #[test]
    fn pattern_double_star() {
        let t = VcpToken::parse("company.acme.legal.compliance").unwrap();
        assert!(t.matches_pattern("company.**"));
        assert!(t.matches_pattern("**.compliance"));
        assert!(!t.matches_pattern("org.**"));
    }

    // ── URI ─────────────────────────────────────────────

    #[test]
    fn uri_parser_accepts_canonical_and_legacy_forms_with_normalization() {
        for (raw, expected) in [
            (
                "creed://creed.space/family.safe.guide@^00001.00002.00003-RC.1",
                "family.safe.guide@^1.2.3-rc.1",
            ),
            (
                "creed://creed.space/family/safe/guide@01.2.3",
                "family.safe.guide@1.2.3",
            ),
            (
                "vcp://family.safe.guide@~00001.00002.00003",
                "family.safe.guide@~1.2.3",
            ),
        ] {
            let token = VcpToken::from_uri(raw).unwrap();
            assert_eq!(token.full(), expected, "failed to normalize {raw}");
            assert!(VcpToken::parse(raw).is_err());
        }
    }

    #[test]
    fn uri_parser_rejects_authority_path_and_component_confusion() {
        for invalid in [
            "",
            "https://creed.space/family.safe.guide",
            "CREED://creed.space/family.safe.guide",
            "creed://",
            "creed://creed.space",
            "creed:///family.safe.guide",
            "creed://user@creed.space/family.safe.guide",
            "creed://creed.space:443/family.safe.guide",
            "creed://127.0.0.1/family.safe.guide",
            "creed://[::1]/family.safe.guide",
            "creed://creed.space/family.safe.guide?query=true",
            "creed://creed.space/family.safe.guide#fragment",
            "creed://creed.space/family%2Esafe.guide",
            "creed://creed.space/family\\safe\\guide",
            "creed://creed.space/familý.safe.guide",
            "creed://creed.space/family.safe.guide:SEC",
            "creed://creed.space/family.safe/guide",
            "creed://creed.space/family//safe/guide",
            "creed://creed.space//family/safe/guide",
            "creed://creed.space/family/safe/guide/",
            "vcp://family/safe/guide",
        ] {
            assert!(
                VcpToken::from_uri(invalid).is_err(),
                "accepted invalid identity URI {invalid:?}"
            );
        }
    }

    #[test]
    fn uri_parser_enforces_inclusive_wire_limit() {
        let issuer = [
            "a".repeat(63),
            "b".repeat(63),
            "c".repeat(63),
            "d".repeat(61),
        ]
        .join(".");
        let token = std::iter::once("e".repeat(32))
            .chain((0..7).map(|_| "f".repeat(31)))
            .collect::<Vec<_>>()
            .join(".");
        let at_limit = format!("creed://{issuer}/{token}");
        assert_eq!(issuer.len(), 253);
        assert_eq!(token.len(), MAX_LENGTH);
        assert_eq!(at_limit.len(), MAX_IDENTITY_URI_BYTES);
        assert_eq!(VcpToken::from_uri(&at_limit).unwrap().full(), token);

        let over_limit = format!("creed://{issuer}a/{token}");
        assert_eq!(over_limit.len(), MAX_IDENTITY_URI_BYTES + 1);
        assert!(VcpToken::from_uri(&over_limit).is_err());
    }

    #[test]
    fn to_uri_default_registry() {
        let t = VcpToken::parse("family.safe.guide@1.0.0:SEC").unwrap();
        assert_eq!(
            t.to_uri("creed.space"),
            "creed://creed.space/family.safe.guide@1.0.0"
        );
    }
}
