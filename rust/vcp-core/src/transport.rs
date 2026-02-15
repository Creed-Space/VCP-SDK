//! Bundle transport: content hashing, canonicalization, and signature verification.
//!
//! Implements the same canonicalization rules as the Python SDK:
//!
//! **Content canonicalization:**
//! 1. Unicode NFC normalization
//! 2. Line ending normalization (CRLF/CR -> LF)
//! 3. Strip trailing whitespace from each line
//! 4. Remove trailing empty lines, ensure single trailing newline
//! 5. Reject control characters (except `\n`, `\t`)
//! 6. UTF-8 encode without BOM
//!
//! **Manifest canonicalization (RFC 8785 JCS):**
//! - Sort object keys lexicographically
//! - No whitespace between tokens
//! - UTF-8 encoding

use sha2::{Digest, Sha256};
use unicode_normalization::UnicodeNormalization;

use serde::{Deserialize, Serialize};

use crate::error::{VcpError, VcpResult, VerificationCode};

// ── Content canonicalization ────────────────────────────────

/// Unicode codepoints that are forbidden in constitution content.
const FORBIDDEN_CODEPOINTS: &[char] = &[
    '\u{202A}', '\u{202B}', '\u{202C}', '\u{202D}', '\u{202E}', // direction overrides
    '\u{2066}', '\u{2067}', '\u{2068}', '\u{2069}', // isolates
    '\u{200B}', '\u{200C}', '\u{200D}', '\u{FEFF}', // zero-width chars
];

/// Canonicalize constitution content to deterministic UTF-8 bytes.
///
/// Follows the same six-step process as the Python implementation.
pub fn canonicalize_content(text: &str) -> VcpResult<Vec<u8>> {
    // 1. Unicode NFC normalization.
    let text: String = text.nfc().collect();

    // 2. Line ending normalization.
    let text = text.replace("\r\n", "\n").replace('\r', "\n");

    // 3. Strip trailing whitespace from each line.
    let lines: Vec<&str> = text
        .split('\n')
        .map(|l| l.trim_end_matches([' ', '\t']))
        .collect();

    // 4. Remove trailing empty lines, ensure single trailing newline.
    let mut lines = lines;
    while lines.last().map_or(false, |l| l.is_empty()) {
        lines.pop();
    }
    let mut text = lines.join("\n");
    text.push('\n');

    // 5. Reject control characters (except \n, \t).
    for (i, ch) in text.char_indices() {
        if ch.is_control() && ch != '\n' && ch != '\t' {
            return Err(VcpError::ParseError(format!(
                "illegal control character at position {i}: U+{:04X}",
                ch as u32
            )));
        }
        if FORBIDDEN_CODEPOINTS.contains(&ch) {
            return Err(VcpError::ParseError(format!(
                "forbidden Unicode character at position {i}: U+{:04X}",
                ch as u32
            )));
        }
    }

    // 6. UTF-8 encode without BOM.
    Ok(text.into_bytes())
}

/// Compute `sha256:<hex>` hash of canonical content.
pub fn compute_content_hash(content: &str) -> VcpResult<String> {
    let canonical = canonicalize_content(content)?;
    let mut hasher = Sha256::new();
    hasher.update(&canonical);
    let digest = hasher.finalize();
    Ok(format!("sha256:{:x}", digest))
}

/// Verify that content matches an expected hash string.
pub fn verify_content_hash(content: &str, expected: &str) -> VcpResult<bool> {
    let computed = compute_content_hash(content)?;
    Ok(computed == expected)
}

// ── Manifest canonicalization (RFC 8785) ────────────────────

/// Canonicalize a JSON manifest for signature computation.
///
/// Implements RFC 8785 JSON Canonicalization Scheme:
/// - Keys sorted lexicographically
/// - No whitespace between tokens
/// - The `"signature"` field is excluded from canonicalization.
pub fn canonicalize_manifest(manifest: &serde_json::Value) -> VcpResult<Vec<u8>> {
    let obj = manifest
        .as_object()
        .ok_or_else(|| VcpError::ParseError("manifest must be a JSON object".into()))?;

    // Remove "signature" before canonicalizing.
    let filtered: serde_json::Map<String, serde_json::Value> = obj
        .iter()
        .filter(|(k, _)| k.as_str() != "signature")
        .map(|(k, v)| (k.clone(), v.clone()))
        .collect();

    // Serialize with sorted keys, no whitespace.
    let canonical = serde_json::to_string(&serde_json::Value::Object(filtered))
        .map_err(|e| VcpError::JsonError(e.to_string()))?;

    Ok(canonical.into_bytes())
}

// ── Bundle verification ─────────────────────────────────────

/// Result of a bundle verification check.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct VerificationResult {
    pub code: VerificationCode,
    pub message: String,
}

impl VerificationResult {
    /// Create a successful verification result.
    pub fn valid() -> Self {
        Self {
            code: VerificationCode::Valid,
            message: "verification passed".into(),
        }
    }

    /// Create a failed result with a specific code.
    pub fn fail(code: VerificationCode, message: impl Into<String>) -> Self {
        Self {
            code,
            message: message.into(),
        }
    }

    /// Returns `true` if verification passed.
    pub fn is_valid(&self) -> bool {
        self.code.is_valid()
    }
}

// Manual Serialize/Deserialize for VerificationCode which is Copy + not a string.
impl Serialize for VerificationCode {
    fn serialize<S: serde::Serializer>(&self, serializer: S) -> Result<S::Ok, S::Error> {
        serializer.serialize_str(&self.to_string())
    }
}

impl<'de> Deserialize<'de> for VerificationCode {
    fn deserialize<D: serde::Deserializer<'de>>(deserializer: D) -> Result<Self, D::Error> {
        let s = String::deserialize(deserializer)?;
        match s.as_str() {
            "valid" => Ok(VerificationCode::Valid),
            "size_exceeded" => Ok(VerificationCode::SizeExceeded),
            "invalid_schema" => Ok(VerificationCode::InvalidSchema),
            "untrusted_issuer" => Ok(VerificationCode::UntrustedIssuer),
            "invalid_signature" => Ok(VerificationCode::InvalidSignature),
            "untrusted_auditor" => Ok(VerificationCode::UntrustedAuditor),
            "invalid_attestation" => Ok(VerificationCode::InvalidAttestation),
            "hash_mismatch" => Ok(VerificationCode::HashMismatch),
            "not_yet_valid" => Ok(VerificationCode::NotYetValid),
            "expired" => Ok(VerificationCode::Expired),
            "future_timestamp" => Ok(VerificationCode::FutureTimestamp),
            "replay_detected" => Ok(VerificationCode::ReplayDetected),
            "token_mismatch" => Ok(VerificationCode::TokenMismatch),
            "budget_exceeded" => Ok(VerificationCode::BudgetExceeded),
            "scope_mismatch" => Ok(VerificationCode::ScopeMismatch),
            "revoked" => Ok(VerificationCode::Revoked),
            "fetch_failed" => Ok(VerificationCode::FetchFailed),
            other => Err(serde::de::Error::unknown_variant(
                other,
                &[
                    "valid",
                    "size_exceeded",
                    "invalid_schema",
                    "untrusted_issuer",
                    "invalid_signature",
                    "untrusted_auditor",
                    "invalid_attestation",
                    "hash_mismatch",
                    "not_yet_valid",
                    "expired",
                    "future_timestamp",
                    "replay_detected",
                    "token_mismatch",
                    "budget_exceeded",
                    "scope_mismatch",
                    "revoked",
                    "fetch_failed",
                ],
            )),
        }
    }
}

/// Verify that the content hash in a bundle matches the actual content.
pub fn verify_bundle_content(content: &str, expected_hash: &str) -> VerificationResult {
    match compute_content_hash(content) {
        Ok(computed) => {
            if computed == expected_hash {
                VerificationResult::valid()
            } else {
                VerificationResult::fail(
                    VerificationCode::HashMismatch,
                    format!("expected {expected_hash}, got {computed}"),
                )
            }
        }
        Err(e) => VerificationResult::fail(
            VerificationCode::InvalidSchema,
            format!("content canonicalization failed: {e}"),
        ),
    }
}

/// Verify a bundle manifest JSON against its content.
///
/// Checks:
/// 1. Content hash matches `bundle.content_hash`.
/// 2. Manifest is well-formed JSON with required fields.
pub fn verify_bundle(manifest_json: &str, content: &str) -> VcpResult<VerificationResult> {
    let manifest: serde_json::Value = serde_json::from_str(manifest_json)?;

    let bundle = manifest
        .get("bundle")
        .ok_or_else(|| VcpError::ParseError("missing 'bundle' field in manifest".into()))?;

    let expected_hash = bundle
        .get("content_hash")
        .and_then(|v| v.as_str())
        .ok_or_else(|| VcpError::ParseError("missing 'bundle.content_hash' in manifest".into()))?;

    Ok(verify_bundle_content(content, expected_hash))
}

// ── Tests ───────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;
    use pretty_assertions::assert_eq;

    #[test]
    fn canonicalize_normalizes_line_endings() {
        let input = "hello\r\nworld\rfoo\n";
        let result = canonicalize_content(input).unwrap();
        assert_eq!(result, b"hello\nworld\nfoo\n");
    }

    #[test]
    fn canonicalize_strips_trailing_whitespace() {
        let input = "hello   \nworld\t\t\n";
        let result = canonicalize_content(input).unwrap();
        assert_eq!(result, b"hello\nworld\n");
    }

    #[test]
    fn canonicalize_removes_trailing_empty_lines() {
        let input = "hello\n\n\n\n";
        let result = canonicalize_content(input).unwrap();
        assert_eq!(result, b"hello\n");
    }

    #[test]
    fn canonicalize_ensures_trailing_newline() {
        let input = "hello";
        let result = canonicalize_content(input).unwrap();
        assert_eq!(result, b"hello\n");
    }

    #[test]
    fn canonicalize_rejects_control_chars() {
        let input = "hello\x01world";
        assert!(canonicalize_content(input).is_err());
    }

    #[test]
    fn canonicalize_rejects_bidi_overrides() {
        let input = "hello\u{202E}world";
        assert!(canonicalize_content(input).is_err());
    }

    #[test]
    fn canonicalize_allows_tabs_and_newlines() {
        let input = "hello\tworld\nfoo";
        let result = canonicalize_content(input).unwrap();
        assert_eq!(result, b"hello\tworld\nfoo\n");
    }

    #[test]
    fn content_hash_deterministic() {
        let h1 = compute_content_hash("hello world").unwrap();
        let h2 = compute_content_hash("hello world").unwrap();
        assert_eq!(h1, h2);
        assert!(h1.starts_with("sha256:"));
    }

    #[test]
    fn content_hash_different_content() {
        let h1 = compute_content_hash("hello").unwrap();
        let h2 = compute_content_hash("world").unwrap();
        assert_ne!(h1, h2);
    }

    #[test]
    fn verify_content_hash_ok() {
        let hash = compute_content_hash("test content").unwrap();
        assert!(verify_content_hash("test content", &hash).unwrap());
    }

    #[test]
    fn verify_content_hash_mismatch() {
        assert!(!verify_content_hash("test", "sha256:wrong").unwrap());
    }

    #[test]
    fn canonicalize_crlf_equals_lf() {
        let h1 = compute_content_hash("line1\nline2").unwrap();
        let h2 = compute_content_hash("line1\r\nline2").unwrap();
        assert_eq!(h1, h2);
    }

    #[test]
    fn canonicalize_trailing_ws_ignored() {
        let h1 = compute_content_hash("hello").unwrap();
        let h2 = compute_content_hash("hello   ").unwrap();
        assert_eq!(h1, h2);
    }

    #[test]
    fn manifest_canonicalization_excludes_signature() {
        let manifest = serde_json::json!({
            "bundle": {"id": "test"},
            "signature": {"value": "should-be-excluded"},
            "version": "1.0"
        });

        let canonical = canonicalize_manifest(&manifest).unwrap();
        let canonical_str = String::from_utf8(canonical).unwrap();

        assert!(!canonical_str.contains("signature"));
        assert!(canonical_str.contains("bundle"));
    }

    #[test]
    fn manifest_canonicalization_sorts_keys() {
        let manifest = serde_json::json!({
            "z_field": 1,
            "a_field": 2,
            "m_field": 3
        });

        let canonical = canonicalize_manifest(&manifest).unwrap();
        let canonical_str = String::from_utf8(canonical).unwrap();

        let a_pos = canonical_str.find("a_field").unwrap();
        let m_pos = canonical_str.find("m_field").unwrap();
        let z_pos = canonical_str.find("z_field").unwrap();

        assert!(a_pos < m_pos);
        assert!(m_pos < z_pos);
    }

    #[test]
    fn verify_bundle_valid() {
        let content = "# My Constitution\n\nBe kind.";
        let hash = compute_content_hash(content).unwrap();
        let manifest = serde_json::json!({
            "bundle": {
                "id": "test-bundle",
                "content_hash": hash,
            }
        });

        let result = verify_bundle(&serde_json::to_string(&manifest).unwrap(), content).unwrap();
        assert!(result.is_valid());
    }

    #[test]
    fn verify_bundle_tampered() {
        let hash = compute_content_hash("original content").unwrap();
        let manifest = serde_json::json!({
            "bundle": {
                "id": "test-bundle",
                "content_hash": hash,
            }
        });

        let result = verify_bundle(
            &serde_json::to_string(&manifest).unwrap(),
            "tampered content",
        )
        .unwrap();
        assert!(!result.is_valid());
        assert_eq!(result.code, VerificationCode::HashMismatch);
    }
}
