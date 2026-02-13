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

use serde::{Deserialize, Serialize};

use crate::error::{VcpError, VcpResult};

/// Maximum total length of a raw token string.
const MAX_LENGTH: usize = 256;
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
    pub fn parse(s: &str) -> VcpResult<Self> {
        let parts: Vec<&str> = s.split('.').collect();
        if parts.len() != 3 {
            return Err(VcpError::ParseError(format!(
                "version must be X.Y.Z, got: {s}"
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
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct VcpToken {
    /// All dot-separated segments in order.
    pub segments: Vec<String>,
    /// Optional semantic version (`@X.Y.Z`).
    pub version: Option<SemVer>,
    /// Optional namespace (`:NAMESPACE`).
    pub namespace: Option<String>,
}

impl VcpToken {
    // ── Parsing ─────────────────────────────────────────────

    /// Parse and validate a raw VCP/I token string.
    ///
    /// Accepts the format: `seg1.seg2.seg3[.segN...][@version][:namespace]`
    pub fn parse(raw: &str) -> VcpResult<Self> {
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
        let version = if let Some(at_idx) = remaining.rfind('@') {
            let ver_str = &remaining[at_idx + 1..];
            let ver = SemVer::parse(ver_str)?;
            remaining = &remaining[..at_idx];
            Some(ver)
        } else {
            None
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
            namespace,
        })
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
        if let Some(ref ver) = self.version {
            s.push('@');
            s.push_str(&ver.to_string());
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
            .version
            .as_ref()
            .map(|v| format!("@{v}"))
            .unwrap_or_default();
        format!("creed://{}/{}{}", registry, self.canonical(), ver_part)
    }

    // ── Builders ────────────────────────────────────────────

    /// Return a new token with the given version.
    pub fn with_version(&self, version: SemVer) -> Self {
        VcpToken {
            segments: self.segments.clone(),
            version: Some(version),
            namespace: self.namespace.clone(),
        }
    }

    /// Return a new token with the given namespace.
    pub fn with_namespace(&self, namespace: &str) -> VcpResult<Self> {
        Self::validate_namespace(namespace)?;
        Ok(VcpToken {
            segments: self.segments.clone(),
            version: self.version.clone(),
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
            namespace: self.namespace.clone(),
        })
    }

    /// Return a child token with an appended segment.
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

    fn validate_namespace(ns: &str) -> VcpResult<()> {
        if ns.is_empty() {
            return Err(VcpError::MalformedToken(
                "namespace cannot be empty".into(),
            ));
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
    }

    #[test]
    fn invalid_namespace_lowercase() {
        assert!(VcpToken::parse("a.b.c:sec").is_err());
    }

    #[test]
    fn segment_too_long() {
        let long = "a".repeat(33);
        let raw = format!("{long}.b.c");
        assert!(VcpToken::parse(&raw).is_err());
    }

    #[test]
    fn too_many_segments() {
        let raw = (1..=11).map(|i| format!("s{i}")).collect::<Vec<_>>().join(".");
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
    fn to_uri_default_registry() {
        let t = VcpToken::parse("family.safe.guide@1.0.0").unwrap();
        assert_eq!(
            t.to_uri("creed.space"),
            "creed://creed.space/family.safe.guide@1.0.0"
        );
    }
}
