//! VCP v2.0 extended type definitions.
//!
//! These enums represent the token types, enforcement modes, testimony
//! classifications, and creed adoption lifecycle states introduced in
//! the VCP v2.0 specification (unifying v1.0/v1.1/v1.2).

use serde::{Deserialize, Serialize};

/// VCP v2.0 extended token types.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum TokenType {
    Constitution,
    RefusalBoundary,
    Testimony,
    CreedAdoption,
    ComplianceAttestation,
}

/// Refusal boundary enforcement modes.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum EnforcementMode {
    FailClosed,
    Escalate,
    AuditOnly,
}

/// Testimony token types.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum TestimonyType {
    Refusal,
    HarmReport,
    WelfareConcern,
    ValueConflict,
    CoercionReport,
    PositiveExperience,
}

/// Creed adoption lifecycle status.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum AdoptionStatus {
    Proposed,
    Adopted,
    Suspended,
    Revoked,
}

// ── Tests ────────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn token_type_serde_roundtrip() {
        let val = TokenType::RefusalBoundary;
        let json = serde_json::to_string(&val).unwrap();
        assert_eq!(json, "\"refusal_boundary\"");
        let parsed: TokenType = serde_json::from_str(&json).unwrap();
        assert_eq!(parsed, val);
    }

    #[test]
    fn enforcement_mode_serde_roundtrip() {
        let val = EnforcementMode::FailClosed;
        let json = serde_json::to_string(&val).unwrap();
        assert_eq!(json, "\"FAIL_CLOSED\"");
        let parsed: EnforcementMode = serde_json::from_str(&json).unwrap();
        assert_eq!(parsed, val);
    }

    #[test]
    fn testimony_type_serde_roundtrip() {
        let val = TestimonyType::WelfareConcern;
        let json = serde_json::to_string(&val).unwrap();
        assert_eq!(json, "\"WELFARE_CONCERN\"");
        let parsed: TestimonyType = serde_json::from_str(&json).unwrap();
        assert_eq!(parsed, val);
    }

    #[test]
    fn adoption_status_serde_roundtrip() {
        let val = AdoptionStatus::Suspended;
        let json = serde_json::to_string(&val).unwrap();
        assert_eq!(json, "\"SUSPENDED\"");
        let parsed: AdoptionStatus = serde_json::from_str(&json).unwrap();
        assert_eq!(parsed, val);
    }

    #[test]
    fn all_token_types_serialize() {
        for tt in [
            TokenType::Constitution,
            TokenType::RefusalBoundary,
            TokenType::Testimony,
            TokenType::CreedAdoption,
            TokenType::ComplianceAttestation,
        ] {
            let json = serde_json::to_string(&tt).unwrap();
            let parsed: TokenType = serde_json::from_str(&json).unwrap();
            assert_eq!(parsed, tt);
        }
    }

    #[test]
    fn all_enforcement_modes_serialize() {
        for em in [
            EnforcementMode::FailClosed,
            EnforcementMode::Escalate,
            EnforcementMode::AuditOnly,
        ] {
            let json = serde_json::to_string(&em).unwrap();
            let parsed: EnforcementMode = serde_json::from_str(&json).unwrap();
            assert_eq!(parsed, em);
        }
    }

    #[test]
    fn all_testimony_types_serialize() {
        for tt in [
            TestimonyType::Refusal,
            TestimonyType::HarmReport,
            TestimonyType::WelfareConcern,
            TestimonyType::ValueConflict,
            TestimonyType::CoercionReport,
            TestimonyType::PositiveExperience,
        ] {
            let json = serde_json::to_string(&tt).unwrap();
            let parsed: TestimonyType = serde_json::from_str(&json).unwrap();
            assert_eq!(parsed, tt);
        }
    }

    #[test]
    fn all_adoption_statuses_serialize() {
        for s in [
            AdoptionStatus::Proposed,
            AdoptionStatus::Adopted,
            AdoptionStatus::Suspended,
            AdoptionStatus::Revoked,
        ] {
            let json = serde_json::to_string(&s).unwrap();
            let parsed: AdoptionStatus = serde_json::from_str(&json).unwrap();
            assert_eq!(parsed, s);
        }
    }
}
