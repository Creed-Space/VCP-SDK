//! VCP error types.
//!
//! All fallible operations in `vcp-core` return [`VcpError`] through
//! the standard [`Result`] alias [`VcpResult`].

use std::fmt;

/// Convenience alias used throughout the crate.
pub type VcpResult<T> = Result<T, VcpError>;

/// Errors that can occur during VCP token parsing, encoding, or verification.
#[derive(Debug, Clone, PartialEq, Eq, thiserror::Error)]
pub enum VcpError {
    /// A string could not be parsed into the expected VCP structure.
    #[error("parse error: {0}")]
    ParseError(String),

    /// An unrecognised persona character was encountered.
    #[error("invalid persona character: '{0}'")]
    InvalidPersona(char),

    /// An adherence level outside the valid 0-5 range.
    #[error("invalid adherence level: {0} (must be 0-5)")]
    InvalidAdherence(u8),

    /// An intensity value outside the valid 1-5 range.
    #[error("invalid intensity: {0} (must be 1-5)")]
    InvalidIntensity(u8),

    /// An unrecognised scope character was encountered.
    #[error("invalid scope character: '{0}'")]
    InvalidScope(char),

    /// A token string is structurally malformed.
    #[error("malformed token: {0}")]
    MalformedToken(String),

    /// A content hash did not match its expected value.
    #[error("hash mismatch: expected {expected}, got {actual}")]
    HashMismatch { expected: String, actual: String },

    /// A cryptographic signature could not be verified.
    #[error("signature error: {0}")]
    SignatureError(String),

    /// A JSON serialization / deserialization error.
    #[error("json error: {0}")]
    JsonError(String),
}

impl From<serde_json::Error> for VcpError {
    fn from(err: serde_json::Error) -> Self {
        VcpError::JsonError(err.to_string())
    }
}

/// Validation result codes mirroring the Python `VerificationResult` enum.
///
/// These are returned by bundle verification routines to indicate
/// exactly why verification succeeded or failed.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
#[repr(u8)]
pub enum VerificationCode {
    Valid = 0,
    SizeExceeded = 1,
    InvalidSchema = 2,
    UntrustedIssuer = 3,
    InvalidSignature = 4,
    UntrustedAuditor = 5,
    InvalidAttestation = 6,
    HashMismatch = 7,
    NotYetValid = 8,
    Expired = 9,
    FutureTimestamp = 10,
    ReplayDetected = 11,
    TokenMismatch = 12,
    BudgetExceeded = 13,
    ScopeMismatch = 14,
    Revoked = 15,
    FetchFailed = 16,
}

impl VerificationCode {
    /// Returns `true` when the code represents a successful verification.
    pub fn is_valid(self) -> bool {
        matches!(self, VerificationCode::Valid)
    }

    /// Broad classification of the failure reason.
    pub fn category(self) -> &'static str {
        match self {
            VerificationCode::Valid => "success",
            VerificationCode::InvalidSignature
            | VerificationCode::InvalidAttestation
            | VerificationCode::HashMismatch
            | VerificationCode::FutureTimestamp
            | VerificationCode::ReplayDetected
            | VerificationCode::TokenMismatch
            | VerificationCode::SizeExceeded
            | VerificationCode::Revoked => "security",
            VerificationCode::NotYetValid | VerificationCode::Expired => "temporal",
            VerificationCode::FetchFailed => "transient",
            _ => "configuration",
        }
    }
}

impl fmt::Display for VerificationCode {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let label = match self {
            VerificationCode::Valid => "valid",
            VerificationCode::SizeExceeded => "size_exceeded",
            VerificationCode::InvalidSchema => "invalid_schema",
            VerificationCode::UntrustedIssuer => "untrusted_issuer",
            VerificationCode::InvalidSignature => "invalid_signature",
            VerificationCode::UntrustedAuditor => "untrusted_auditor",
            VerificationCode::InvalidAttestation => "invalid_attestation",
            VerificationCode::HashMismatch => "hash_mismatch",
            VerificationCode::NotYetValid => "not_yet_valid",
            VerificationCode::Expired => "expired",
            VerificationCode::FutureTimestamp => "future_timestamp",
            VerificationCode::ReplayDetected => "replay_detected",
            VerificationCode::TokenMismatch => "token_mismatch",
            VerificationCode::BudgetExceeded => "budget_exceeded",
            VerificationCode::ScopeMismatch => "scope_mismatch",
            VerificationCode::Revoked => "revoked",
            VerificationCode::FetchFailed => "fetch_failed",
        };
        f.write_str(label)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn verification_code_valid() {
        assert!(VerificationCode::Valid.is_valid());
        assert!(!VerificationCode::Expired.is_valid());
    }

    #[test]
    fn verification_code_categories() {
        assert_eq!(VerificationCode::Valid.category(), "success");
        assert_eq!(VerificationCode::HashMismatch.category(), "security");
        assert_eq!(VerificationCode::Expired.category(), "temporal");
        assert_eq!(VerificationCode::FetchFailed.category(), "transient");
        assert_eq!(VerificationCode::BudgetExceeded.category(), "configuration");
    }

    #[test]
    fn vcp_error_display() {
        let e = VcpError::InvalidPersona('X');
        assert_eq!(e.to_string(), "invalid persona character: 'X'");

        let e = VcpError::HashMismatch {
            expected: "abc".into(),
            actual: "def".into(),
        };
        assert!(e.to_string().contains("abc"));
        assert!(e.to_string().contains("def"));
    }
}
