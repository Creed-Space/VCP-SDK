//! Trust anchor management for VCP issuers and auditors.
//!
//! Mirrors the Python SDK's `vcp.trust` module. A [`TrustConfig`] holds
//! collections of [`TrustAnchor`] entries keyed by entity ID. Each anchor
//! represents a public key for an issuer or auditor, with validity windows
//! and lifecycle state tracking.
//!
//! # Examples
//!
//! ```
//! use vcp_core::trust::{AnchorState, AnchorType, TrustAnchor, TrustConfig};
//! use chrono::{Utc, Duration};
//!
//! let mut config = TrustConfig::default();
//!
//! let anchor = TrustAnchor {
//!     id: "creed-space".into(),
//!     key_id: "key-2025-01".into(),
//!     algorithm: "ed25519".into(),
//!     public_key: "base64:AAAA".into(),
//!     anchor_type: AnchorType::Issuer,
//!     valid_from: Utc::now() - Duration::days(1),
//!     valid_until: Utc::now() + Duration::days(365),
//!     state: AnchorState::Active,
//! };
//!
//! config.add_issuer("creed-space", anchor);
//! assert!(config.get_issuer_key("creed-space", None).is_some());
//! ```

use std::collections::HashMap;

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

use crate::error::{VcpError, VcpResult};

// ── Anchor types ────────────────────────────────────────────

/// The role an anchor fulfills in the trust chain.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum AnchorType {
    Issuer,
    Auditor,
}

/// Lifecycle state of a trust anchor.
///
/// Only `Active` and `Rotating` anchors are considered valid for
/// signature verification.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum AnchorState {
    Active,
    Rotating,
    Retired,
    Compromised,
}

impl AnchorState {
    /// Returns `true` if the anchor is in a state that allows verification.
    pub fn allows_verification(self) -> bool {
        matches!(self, AnchorState::Active | AnchorState::Rotating)
    }
}

// ── TrustAnchor ─────────────────────────────────────────────

/// A trusted public key for an issuer or auditor.
///
/// Corresponds to the Python SDK's `TrustAnchor` dataclass.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct TrustAnchor {
    /// Entity identifier (e.g., `"creed-space"`).
    pub id: String,
    /// Key identifier within the entity (e.g., `"key-2025-01"`).
    pub key_id: String,
    /// Signing algorithm (e.g., `"ed25519"`).
    pub algorithm: String,
    /// Public key material, typically `"base64:<encoded>"`.
    pub public_key: String,
    /// Whether this anchor is for an issuer or auditor.
    pub anchor_type: AnchorType,
    /// Start of the validity window.
    pub valid_from: DateTime<Utc>,
    /// End of the validity window.
    pub valid_until: DateTime<Utc>,
    /// Lifecycle state of this anchor.
    #[serde(default = "default_anchor_state")]
    pub state: AnchorState,
}

fn default_anchor_state() -> AnchorState {
    AnchorState::Active
}

impl TrustAnchor {
    /// Check whether this anchor is valid at the given time.
    ///
    /// An anchor is valid when its state allows verification and the
    /// provided timestamp falls within `[valid_from, valid_until]`.
    ///
    /// If `at_time` is `None`, the current UTC time is used.
    pub fn is_valid(&self, at_time: Option<DateTime<Utc>>) -> bool {
        let at = at_time.unwrap_or_else(Utc::now);
        self.state.allows_verification() && at >= self.valid_from && at <= self.valid_until
    }

    /// Parse a `TrustAnchor` from a dictionary-style JSON value.
    ///
    /// Expects the same shape as the Python `TrustAnchor.from_dict()`:
    ///
    /// ```json
    /// {
    ///   "id": "key-2025-01",
    ///   "algorithm": "ed25519",
    ///   "public_key": "base64:...",
    ///   "type": "issuer",
    ///   "valid_from": "2025-01-01T00:00:00Z",
    ///   "valid_until": "2026-01-01T00:00:00Z",
    ///   "state": "active"
    /// }
    /// ```
    ///
    /// # Errors
    ///
    /// Returns [`VcpError::ParseError`] if required fields are missing or
    /// dates cannot be parsed.
    pub fn from_dict(entity_id: &str, data: &serde_json::Value) -> VcpResult<Self> {
        let obj = data
            .as_object()
            .ok_or_else(|| VcpError::ParseError("trust anchor data must be an object".into()))?;

        let key_id = obj
            .get("id")
            .and_then(|v| v.as_str())
            .ok_or_else(|| VcpError::ParseError("missing 'id' in trust anchor".into()))?;

        let algorithm = obj
            .get("algorithm")
            .and_then(|v| v.as_str())
            .ok_or_else(|| VcpError::ParseError("missing 'algorithm' in trust anchor".into()))?;

        let public_key = obj
            .get("public_key")
            .and_then(|v| v.as_str())
            .ok_or_else(|| VcpError::ParseError("missing 'public_key' in trust anchor".into()))?;

        let anchor_type_str = obj
            .get("type")
            .and_then(|v| v.as_str())
            .unwrap_or("issuer");
        let anchor_type = match anchor_type_str {
            "auditor" => AnchorType::Auditor,
            _ => AnchorType::Issuer,
        };

        let valid_from = parse_datetime(
            obj.get("valid_from")
                .and_then(|v| v.as_str())
                .ok_or_else(|| VcpError::ParseError("missing 'valid_from'".into()))?,
        )?;

        let valid_until = parse_datetime(
            obj.get("valid_until")
                .and_then(|v| v.as_str())
                .ok_or_else(|| VcpError::ParseError("missing 'valid_until'".into()))?,
        )?;

        let state_str = obj
            .get("state")
            .and_then(|v| v.as_str())
            .unwrap_or("active");
        let state = match state_str {
            "rotating" => AnchorState::Rotating,
            "retired" => AnchorState::Retired,
            "compromised" => AnchorState::Compromised,
            _ => AnchorState::Active,
        };

        Ok(Self {
            id: entity_id.to_string(),
            key_id: key_id.to_string(),
            algorithm: algorithm.to_string(),
            public_key: public_key.to_string(),
            anchor_type,
            valid_from,
            valid_until,
            state,
        })
    }
}

/// Parse a datetime string, stripping a trailing `Z` if present and
/// falling back to RFC 3339 parsing.
fn parse_datetime(s: &str) -> VcpResult<DateTime<Utc>> {
    // The Python SDK does `fromisoformat(data.rstrip("Z"))`. We handle
    // both `2025-01-01T00:00:00Z` and `2025-01-01T00:00:00` (naive, treated as UTC).
    let trimmed = s.trim_end_matches('Z');
    let with_tz = if trimmed.contains('+') || trimmed.contains('-') && trimmed.len() > 10 {
        // Already has timezone offset, try as-is first.
        s.to_string()
    } else {
        format!("{trimmed}+00:00")
    };

    DateTime::parse_from_rfc3339(&with_tz)
        .map(|dt| dt.with_timezone(&Utc))
        .or_else(|_| {
            // Try with Z suffix.
            DateTime::parse_from_rfc3339(&format!("{trimmed}Z"))
                .map(|dt| dt.with_timezone(&Utc))
        })
        .map_err(|e| VcpError::ParseError(format!("invalid datetime '{s}': {e}")))
}

// ── TrustConfig ─────────────────────────────────────────────

/// Configuration holding trusted issuers and auditors.
///
/// Corresponds to the Python SDK's `TrustConfig` dataclass.
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct TrustConfig {
    /// Trusted issuer anchors, keyed by entity ID.
    pub issuers: HashMap<String, Vec<TrustAnchor>>,
    /// Trusted auditor anchors, keyed by entity ID.
    pub auditors: HashMap<String, Vec<TrustAnchor>>,
}

impl TrustConfig {
    /// Create an empty trust configuration.
    pub fn new() -> Self {
        Self::default()
    }

    /// Add a trusted issuer key.
    pub fn add_issuer(&mut self, issuer_id: &str, anchor: TrustAnchor) {
        self.issuers
            .entry(issuer_id.to_string())
            .or_default()
            .push(anchor);
    }

    /// Add a trusted auditor key.
    pub fn add_auditor(&mut self, auditor_id: &str, anchor: TrustAnchor) {
        self.auditors
            .entry(auditor_id.to_string())
            .or_default()
            .push(anchor);
    }

    /// Get the first valid trust anchor for an issuer.
    ///
    /// If `key_id` is `Some`, only anchors with that key ID are considered.
    /// Returns the first anchor that is currently valid (active/rotating and
    /// within its validity window).
    pub fn get_issuer_key(
        &self,
        issuer_id: &str,
        key_id: Option<&str>,
    ) -> Option<&TrustAnchor> {
        let anchors = self.issuers.get(issuer_id)?;
        let now = Utc::now();
        anchors.iter().find(|a| {
            if let Some(kid) = key_id {
                if a.key_id != kid {
                    return false;
                }
            }
            a.is_valid(Some(now))
        })
    }

    /// Get the first valid trust anchor for an auditor.
    ///
    /// If `key_id` is `Some`, only anchors with that key ID are considered.
    /// Returns the first anchor that is currently valid (active/rotating and
    /// within its validity window).
    pub fn get_auditor_key(
        &self,
        auditor_id: &str,
        key_id: Option<&str>,
    ) -> Option<&TrustAnchor> {
        let anchors = self.auditors.get(auditor_id)?;
        let now = Utc::now();
        anchors.iter().find(|a| {
            if let Some(kid) = key_id {
                if a.key_id != kid {
                    return false;
                }
            }
            a.is_valid(Some(now))
        })
    }

    /// Parse a `TrustConfig` from a dictionary-style JSON value.
    ///
    /// Expects the same shape as the Python `TrustConfig.from_dict()`:
    ///
    /// ```json
    /// {
    ///   "trust_anchors": {
    ///     "creed-space": {
    ///       "type": "issuer",
    ///       "keys": [
    ///         { "id": "key-2025-01", "algorithm": "ed25519", ... }
    ///       ]
    ///     }
    ///   }
    /// }
    /// ```
    ///
    /// # Errors
    ///
    /// Returns [`VcpError::ParseError`] if the structure is malformed.
    pub fn from_dict(data: &serde_json::Value) -> VcpResult<Self> {
        let mut config = Self::new();

        let Some(anchors_obj) = data.get("trust_anchors").and_then(|v| v.as_object()) else {
            return Ok(config); // No trust anchors, return empty config.
        };

        for (entity_id, entity_data) in anchors_obj {
            let entity_type = entity_data
                .get("type")
                .and_then(|v| v.as_str())
                .unwrap_or("issuer");

            let keys = entity_data
                .get("keys")
                .and_then(|v| v.as_array())
                .ok_or_else(|| {
                    VcpError::ParseError(format!(
                        "missing 'keys' array for trust anchor '{entity_id}'"
                    ))
                })?;

            for key_data in keys {
                // Inject the entity type into the key data for parsing.
                let mut key_obj = key_data.clone();
                if let Some(obj) = key_obj.as_object_mut() {
                    obj.insert("type".to_string(), serde_json::json!(entity_type));
                }

                let anchor = TrustAnchor::from_dict(entity_id, &key_obj)?;

                if entity_type == "auditor" {
                    config.add_auditor(entity_id, anchor);
                } else {
                    config.add_issuer(entity_id, anchor);
                }
            }
        }

        Ok(config)
    }

    /// Parse a `TrustConfig` from a JSON string.
    ///
    /// # Errors
    ///
    /// Returns [`VcpError::JsonError`] if the JSON is invalid, or
    /// [`VcpError::ParseError`] if the structure is malformed.
    pub fn from_json(json_str: &str) -> VcpResult<Self> {
        let data: serde_json::Value = serde_json::from_str(json_str)?;
        Self::from_dict(&data)
    }

    /// Serialize the trust config to a dictionary-style JSON value.
    ///
    /// Produces the same shape as the Python `TrustConfig.to_dict()`.
    pub fn to_dict(&self) -> serde_json::Value {
        let mut trust_anchors = serde_json::Map::new();

        for (issuer_id, anchors) in &self.issuers {
            let keys: Vec<serde_json::Value> = anchors
                .iter()
                .map(|a| {
                    serde_json::json!({
                        "id": a.key_id,
                        "algorithm": a.algorithm,
                        "public_key": a.public_key,
                        "state": format!("{}", serde_json::to_value(a.state).unwrap_or_default()).trim_matches('"'),
                        "valid_from": a.valid_from.to_rfc3339(),
                        "valid_until": a.valid_until.to_rfc3339(),
                    })
                })
                .collect();

            trust_anchors.insert(
                issuer_id.clone(),
                serde_json::json!({
                    "type": "issuer",
                    "keys": keys,
                }),
            );
        }

        for (auditor_id, anchors) in &self.auditors {
            let keys: Vec<serde_json::Value> = anchors
                .iter()
                .map(|a| {
                    serde_json::json!({
                        "id": a.key_id,
                        "algorithm": a.algorithm,
                        "public_key": a.public_key,
                        "state": format!("{}", serde_json::to_value(a.state).unwrap_or_default()).trim_matches('"'),
                        "valid_from": a.valid_from.to_rfc3339(),
                        "valid_until": a.valid_until.to_rfc3339(),
                    })
                })
                .collect();

            trust_anchors.insert(
                auditor_id.clone(),
                serde_json::json!({
                    "type": "auditor",
                    "keys": keys,
                }),
            );
        }

        serde_json::json!({ "trust_anchors": trust_anchors })
    }

    /// Serialize the trust config to a JSON string.
    ///
    /// # Errors
    ///
    /// Returns [`VcpError::JsonError`] if serialization fails.
    pub fn to_json(&self) -> VcpResult<String> {
        serde_json::to_string_pretty(&self.to_dict())
            .map_err(|e| VcpError::JsonError(e.to_string()))
    }
}

// ── Tests ───────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;
    use chrono::Duration;
    use pretty_assertions::assert_eq;

    fn make_anchor(
        entity_id: &str,
        key_id: &str,
        anchor_type: AnchorType,
        state: AnchorState,
        days_before: i64,
        days_after: i64,
    ) -> TrustAnchor {
        TrustAnchor {
            id: entity_id.to_string(),
            key_id: key_id.to_string(),
            algorithm: "ed25519".to_string(),
            public_key: "base64:AAAA".to_string(),
            anchor_type,
            valid_from: Utc::now() - Duration::days(days_before),
            valid_until: Utc::now() + Duration::days(days_after),
            state,
        }
    }

    #[test]
    fn anchor_valid_active_within_window() {
        let anchor = make_anchor("test", "k1", AnchorType::Issuer, AnchorState::Active, 1, 365);
        assert!(anchor.is_valid(None));
    }

    #[test]
    fn anchor_valid_rotating_within_window() {
        let anchor = make_anchor("test", "k1", AnchorType::Issuer, AnchorState::Rotating, 1, 365);
        assert!(anchor.is_valid(None));
    }

    #[test]
    fn anchor_invalid_retired() {
        let anchor = make_anchor("test", "k1", AnchorType::Issuer, AnchorState::Retired, 1, 365);
        assert!(!anchor.is_valid(None));
    }

    #[test]
    fn anchor_invalid_compromised() {
        let anchor = make_anchor("test", "k1", AnchorType::Issuer, AnchorState::Compromised, 1, 365);
        assert!(!anchor.is_valid(None));
    }

    #[test]
    fn anchor_invalid_expired() {
        let anchor = make_anchor("test", "k1", AnchorType::Issuer, AnchorState::Active, 365, -1);
        assert!(!anchor.is_valid(None));
    }

    #[test]
    fn anchor_invalid_not_yet_valid() {
        let anchor = make_anchor("test", "k1", AnchorType::Issuer, AnchorState::Active, -1, 365);
        assert!(!anchor.is_valid(None));
    }

    #[test]
    fn anchor_valid_at_specific_time() {
        let anchor = make_anchor("test", "k1", AnchorType::Issuer, AnchorState::Active, 30, 30);
        let past = Utc::now() - Duration::days(10);
        assert!(anchor.is_valid(Some(past)));

        let too_early = Utc::now() - Duration::days(60);
        assert!(!anchor.is_valid(Some(too_early)));
    }

    #[test]
    fn config_add_and_get_issuer() {
        let mut config = TrustConfig::new();
        let anchor = make_anchor("creed", "k1", AnchorType::Issuer, AnchorState::Active, 1, 365);
        config.add_issuer("creed", anchor);

        assert!(config.get_issuer_key("creed", None).is_some());
        assert!(config.get_issuer_key("creed", Some("k1")).is_some());
        assert!(config.get_issuer_key("creed", Some("wrong-key")).is_none());
        assert!(config.get_issuer_key("unknown", None).is_none());
    }

    #[test]
    fn config_add_and_get_auditor() {
        let mut config = TrustConfig::new();
        let anchor = make_anchor("auditor-1", "k1", AnchorType::Auditor, AnchorState::Active, 1, 365);
        config.add_auditor("auditor-1", anchor);

        assert!(config.get_auditor_key("auditor-1", None).is_some());
        assert!(config.get_auditor_key("auditor-1", Some("k1")).is_some());
        assert!(config.get_auditor_key("auditor-1", Some("wrong")).is_none());
        assert!(config.get_auditor_key("unknown", None).is_none());
    }

    #[test]
    fn config_skips_invalid_anchors() {
        let mut config = TrustConfig::new();

        // Add an expired anchor and a valid one.
        let expired = make_anchor("creed", "old", AnchorType::Issuer, AnchorState::Active, 365, -1);
        let valid = make_anchor("creed", "new", AnchorType::Issuer, AnchorState::Active, 1, 365);

        config.add_issuer("creed", expired);
        config.add_issuer("creed", valid);

        let found = config.get_issuer_key("creed", None).unwrap();
        assert_eq!(found.key_id, "new");
    }

    #[test]
    fn config_from_dict_issuers() {
        let data = serde_json::json!({
            "trust_anchors": {
                "creed-space": {
                    "type": "issuer",
                    "keys": [{
                        "id": "key-2025-01",
                        "algorithm": "ed25519",
                        "public_key": "base64:test-key",
                        "valid_from": "2020-01-01T00:00:00Z",
                        "valid_until": "2030-01-01T00:00:00Z",
                        "state": "active"
                    }]
                }
            }
        });

        let config = TrustConfig::from_dict(&data).unwrap();
        let anchor = config.get_issuer_key("creed-space", Some("key-2025-01"));
        assert!(anchor.is_some());

        let a = anchor.unwrap();
        assert_eq!(a.algorithm, "ed25519");
        assert_eq!(a.public_key, "base64:test-key");
    }

    #[test]
    fn config_from_dict_auditors() {
        let data = serde_json::json!({
            "trust_anchors": {
                "safety-auditor": {
                    "type": "auditor",
                    "keys": [{
                        "id": "aud-key-01",
                        "algorithm": "ed25519",
                        "public_key": "base64:auditor-key",
                        "valid_from": "2020-01-01T00:00:00Z",
                        "valid_until": "2030-01-01T00:00:00Z"
                    }]
                }
            }
        });

        let config = TrustConfig::from_dict(&data).unwrap();
        assert!(config.get_auditor_key("safety-auditor", None).is_some());
        assert!(config.get_issuer_key("safety-auditor", None).is_none());
    }

    #[test]
    fn config_from_dict_mixed() {
        let data = serde_json::json!({
            "trust_anchors": {
                "creed-space": {
                    "type": "issuer",
                    "keys": [{
                        "id": "k1",
                        "algorithm": "ed25519",
                        "public_key": "base64:issuer-key",
                        "valid_from": "2020-01-01T00:00:00Z",
                        "valid_until": "2030-01-01T00:00:00Z"
                    }]
                },
                "safety-co": {
                    "type": "auditor",
                    "keys": [{
                        "id": "k2",
                        "algorithm": "ed25519",
                        "public_key": "base64:auditor-key",
                        "valid_from": "2020-01-01T00:00:00Z",
                        "valid_until": "2030-01-01T00:00:00Z"
                    }]
                }
            }
        });

        let config = TrustConfig::from_dict(&data).unwrap();
        assert!(config.get_issuer_key("creed-space", None).is_some());
        assert!(config.get_auditor_key("safety-co", None).is_some());
    }

    #[test]
    fn config_from_json_roundtrip() {
        let json_str = r#"{
            "trust_anchors": {
                "test-issuer": {
                    "type": "issuer",
                    "keys": [{
                        "id": "k1",
                        "algorithm": "ed25519",
                        "public_key": "base64:roundtrip-key",
                        "valid_from": "2020-01-01T00:00:00Z",
                        "valid_until": "2030-01-01T00:00:00Z",
                        "state": "active"
                    }]
                }
            }
        }"#;

        let config = TrustConfig::from_json(json_str).unwrap();
        assert!(config.get_issuer_key("test-issuer", Some("k1")).is_some());

        // Verify to_dict produces valid structure.
        let dict = config.to_dict();
        let reparsed = TrustConfig::from_dict(&dict).unwrap();
        assert!(reparsed.get_issuer_key("test-issuer", Some("k1")).is_some());
    }

    #[test]
    fn config_empty_trust_anchors() {
        let data = serde_json::json!({});
        let config = TrustConfig::from_dict(&data).unwrap();
        assert!(config.issuers.is_empty());
        assert!(config.auditors.is_empty());
    }

    #[test]
    fn config_from_dict_missing_keys_error() {
        let data = serde_json::json!({
            "trust_anchors": {
                "bad-entity": {
                    "type": "issuer"
                    // missing "keys" array
                }
            }
        });

        let result = TrustConfig::from_dict(&data);
        assert!(result.is_err());
        assert!(result.unwrap_err().to_string().contains("keys"));
    }

    #[test]
    fn anchor_from_dict_defaults() {
        let data = serde_json::json!({
            "id": "k1",
            "algorithm": "ed25519",
            "public_key": "base64:test",
            "valid_from": "2020-01-01T00:00:00Z",
            "valid_until": "2030-01-01T00:00:00Z"
            // no "type" or "state" — should default to issuer/active
        });

        let anchor = TrustAnchor::from_dict("test-entity", &data).unwrap();
        assert_eq!(anchor.anchor_type, AnchorType::Issuer);
        assert_eq!(anchor.state, AnchorState::Active);
    }

    #[test]
    fn anchor_from_dict_auditor_rotating() {
        let data = serde_json::json!({
            "id": "k2",
            "algorithm": "ed25519",
            "public_key": "base64:test",
            "type": "auditor",
            "state": "rotating",
            "valid_from": "2020-01-01T00:00:00Z",
            "valid_until": "2030-01-01T00:00:00Z"
        });

        let anchor = TrustAnchor::from_dict("aud", &data).unwrap();
        assert_eq!(anchor.anchor_type, AnchorType::Auditor);
        assert_eq!(anchor.state, AnchorState::Rotating);
        assert!(anchor.is_valid(None));
    }

    #[test]
    fn parse_datetime_variants() {
        // With Z suffix.
        assert!(parse_datetime("2025-01-01T00:00:00Z").is_ok());
        // Without Z suffix (treated as UTC).
        assert!(parse_datetime("2025-01-01T00:00:00").is_ok());
        // Invalid.
        assert!(parse_datetime("not-a-date").is_err());
    }

    #[test]
    fn config_multiple_keys_per_entity() {
        let mut config = TrustConfig::new();
        let k1 = make_anchor("creed", "k1", AnchorType::Issuer, AnchorState::Active, 1, 365);
        let k2 = make_anchor("creed", "k2", AnchorType::Issuer, AnchorState::Active, 1, 365);

        config.add_issuer("creed", k1);
        config.add_issuer("creed", k2);

        assert_eq!(config.issuers["creed"].len(), 2);

        // Without key_id filter, returns first valid.
        assert!(config.get_issuer_key("creed", None).is_some());

        // With specific key_id.
        let found = config.get_issuer_key("creed", Some("k2")).unwrap();
        assert_eq!(found.key_id, "k2");
    }

    #[test]
    fn anchor_state_allows_verification() {
        assert!(AnchorState::Active.allows_verification());
        assert!(AnchorState::Rotating.allows_verification());
        assert!(!AnchorState::Retired.allows_verification());
        assert!(!AnchorState::Compromised.allows_verification());
    }
}
