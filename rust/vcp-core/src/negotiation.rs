//! VCP negotiation — hello/ack handshake for capability exchange.
//!
//! The VCP negotiation protocol allows a client and server to agree on
//! which protocol extensions are supported and at what versions.

use std::cmp::Ordering;
use std::collections::{HashMap, HashSet};
use std::hash::BuildHasher;

use serde_json::{Map, Value};

use crate::identity::VcpToken;

/// Maximum encoded size of either side of a capability handshake.
pub const MAX_HANDSHAKE_BYTES: usize = 65_536;

/// Defensive ceiling for extension requests inside a handshake.
pub const MAX_EXTENSION_COUNT: usize = 256;

/// Maximum characters in a raw extension identifier request.
pub const MAX_EXTENSION_ID_CHARS: usize = 128;

/// Maximum number of versions advertised in a structured negotiation error.
pub const MAX_SUPPORTED_VERSION_COUNT: usize = 64;

const CORE_FEATURE_NAMES: [&str; 5] = [
    "encryption",
    "injection_scanning",
    "revocation",
    "audit_chain",
    "context_opacity",
];

fn minor_version_parts<'a>(value: &'a str, field: &str) -> Result<(&'a str, &'a str), String> {
    let Some((major, minor)) = value.split_once('.') else {
        return Err(format!("{field} must be a semver major.minor string"));
    };
    if major.is_empty()
        || minor.is_empty()
        || minor.contains('.')
        || major.len() > 9
        || minor.len() > 9
        || (major.len() > 1 && major.starts_with('0'))
        || (minor.len() > 1 && minor.starts_with('0'))
        || !major.bytes().all(|byte| byte.is_ascii_digit())
        || !minor.bytes().all(|byte| byte.is_ascii_digit())
    {
        return Err(format!("{field} must be a semver major.minor string"));
    }
    Ok((major, minor))
}

fn normalized_numeric_text(value: &str) -> &str {
    let normalized = value.trim_start_matches('0');
    if normalized.is_empty() {
        "0"
    } else {
        normalized
    }
}

fn compare_numeric_text(left: &str, right: &str) -> Ordering {
    let left = normalized_numeric_text(left);
    let right = normalized_numeric_text(right);
    left.len().cmp(&right.len()).then_with(|| left.cmp(right))
}

fn compare_minor_versions(left: &str, right: &str) -> Ordering {
    let Some((left_major, left_minor)) = left.split_once('.') else {
        return left.cmp(right);
    };
    let Some((right_major, right_minor)) = right.split_once('.') else {
        return left.cmp(right);
    };
    compare_numeric_text(left_major, right_major)
        .then_with(|| compare_numeric_text(left_minor, right_minor))
        // Numerically equivalent spellings are ordered deterministically.
        .then_with(|| left.cmp(right))
}

fn valid_extension_id(value: &str) -> bool {
    if value.chars().count() > MAX_EXTENSION_ID_CHARS {
        return false;
    }
    let Some(suffix) = value.strip_prefix("VCP-X-") else {
        return false;
    };
    let mut bytes = suffix.bytes();
    bytes.next().is_some_and(|byte| byte.is_ascii_alphabetic())
        && bytes.all(|byte| byte.is_ascii_alphanumeric() || byte == b'-')
}

fn bounded_snapshot(value: &Value, label: &str) -> Result<(), String> {
    let encoded = serde_json::to_vec(value)
        .map_err(|error| format!("{label} must be JSON serializable: {error}"))?;
    if encoded.len() > MAX_HANDSHAKE_BYTES {
        return Err(format!("{label} exceeds the 64 KiB wire limit"));
    }
    Ok(())
}

fn bound_handshake(client_hello: &Value, server: &Value) -> Result<(), String> {
    bounded_snapshot(client_hello, "VCP-Hello")?;
    bounded_snapshot(server, "server capability configuration")
}

fn requested_extensions(value: Option<&Value>) -> Result<Vec<String>, String> {
    let Some(value) = value else {
        return Ok(Vec::new());
    };
    let Some(values) = value.as_array() else {
        return Err("extensions must be a bounded array".to_string());
    };
    if values.len() > MAX_EXTENSION_COUNT {
        return Err("extensions must be a bounded array".to_string());
    }

    let mut requested = Vec::new();
    let mut seen = HashSet::new();
    for extension in values {
        let Some(extension) = extension.as_str() else {
            return Err("extensions entries must be strings".to_string());
        };
        if extension.is_empty() || extension.chars().count() > MAX_EXTENSION_ID_CHARS {
            return Err("extensions entries must contain 1 to 128 characters".to_string());
        }
        if !seen.insert(extension.to_string()) {
            return Err("extensions entries must be unique".to_string());
        }
        if valid_extension_id(extension) {
            requested.push(extension.to_string());
        }
    }
    Ok(requested)
}

fn server_versions(server: &Map<String, Value>) -> Result<Vec<String>, String> {
    let Some(values) = server.get("supported_versions").and_then(Value::as_array) else {
        return Err("server.supported_versions must be a non-empty array".to_string());
    };
    if values.is_empty() {
        return Err("server.supported_versions must be a non-empty array".to_string());
    }
    if values.len() > MAX_SUPPORTED_VERSION_COUNT {
        return Err(format!(
            "server.supported_versions exceeds {MAX_SUPPORTED_VERSION_COUNT} entries"
        ));
    }

    let mut versions = Vec::new();
    let mut seen = HashSet::new();
    for value in values {
        let Some(version) = value.as_str() else {
            continue;
        };
        if minor_version_parts(version, "server supported version").is_err() {
            continue;
        }
        if seen.insert(version.to_string()) {
            versions.push(version.to_string());
        }
    }
    if versions.is_empty() {
        return Err("server.supported_versions must contain a valid version".to_string());
    }
    versions.sort_by(|left, right| compare_minor_versions(left, right));
    Ok(versions)
}

fn validate_identifier_field(
    object: &Map<String, Value>,
    field: &str,
    maximum: usize,
) -> Result<Option<String>, String> {
    let Some(value) = object.get(field) else {
        return Ok(None);
    };
    let Some(value) = value.as_str() else {
        return Err(format!(
            "{field} must be a string of at most {maximum} characters"
        ));
    };
    if value.is_empty() || value.chars().count() > maximum {
        return Err(format!(
            "{field} must be a string of at least 1 and at most {maximum} characters"
        ));
    }
    Ok(Some(value.to_string()))
}

fn validate_core_features(server: &Map<String, Value>) -> Result<Map<String, Value>, String> {
    let Some(features) = server.get("core_features").and_then(Value::as_object) else {
        return Err("server.core_features must be an object".to_string());
    };
    for name in CORE_FEATURE_NAMES {
        if !features.get(name).is_some_and(Value::is_boolean) {
            return Err(format!("server.core_features.{name} must be a boolean"));
        }
    }
    if features.values().any(|feature| !feature.is_boolean()) {
        return Err("additional core feature entries must map strings to booleans".to_string());
    }
    Ok(features.clone())
}

fn server_extensions(server: &Map<String, Value>) -> Result<Map<String, Value>, String> {
    let extensions = match server.get("extensions") {
        None => Map::new(),
        Some(value) => value
            .as_object()
            .ok_or_else(|| "server.extensions must be an object".to_string())?
            .clone(),
    };
    if extensions.len() > MAX_EXTENSION_COUNT {
        return Err(format!(
            "server.extensions exceeds {MAX_EXTENSION_COUNT} entries"
        ));
    }
    if extensions
        .iter()
        .any(|(name, capabilities)| !valid_extension_id(name) || !capabilities.is_object())
    {
        return Err("server extensions must map VCP-X-* identifiers to objects".to_string());
    }
    Ok(extensions)
}

fn capability_error(code: &str, message: &str, supported_versions: Option<Vec<String>>) -> Value {
    let mut error = Map::new();
    error.insert("type".to_string(), Value::String("vcp-error".to_string()));
    error.insert("code".to_string(), Value::String(code.to_string()));
    error.insert("message".to_string(), Value::String(message.to_string()));
    if let Some(versions) = supported_versions {
        error.insert(
            "supported_versions".to_string(),
            Value::Array(versions.into_iter().map(Value::String).collect()),
        );
    }
    error.insert("retry_after".to_string(), Value::Null);
    Value::Object(error)
}

fn identity_error(hello: &Map<String, Value>) -> Result<Option<Value>, String> {
    let Some(identity) = hello.get("identity") else {
        return Ok(None);
    };
    if identity.is_null() {
        return Ok(None);
    }
    let Some(identity) = identity.as_str() else {
        return Err("identity must be a string or null".to_string());
    };
    if VcpToken::parse(identity).is_err() {
        return Ok(Some(capability_error(
            "IDENTITY_INVALID",
            "The supplied VCP/I identity token is invalid",
            None,
        )));
    }
    Ok(None)
}

fn apply_dependency_signals(
    active_extensions: &HashSet<String>,
    capabilities: &mut Map<String, Value>,
) {
    for (extension, dependency, signal, value) in [
        (
            "VCP-X-Torch",
            "VCP-X-Relational",
            "degraded",
            Value::Bool(true),
        ),
        (
            "VCP-X-Intent",
            "VCP-X-Personal",
            "personal_signals",
            Value::Bool(false),
        ),
    ] {
        if active_extensions.contains(extension) && !active_extensions.contains(dependency) {
            if let Some(Value::Object(capability)) = capabilities.get_mut(extension) {
                capability.insert(signal.to_string(), value);
            }
        }
    }
}

fn capability_ack(
    negotiated: String,
    supported: Vec<Value>,
    unsupported: Vec<Value>,
    capabilities: Map<String, Value>,
    core_features: Map<String, Value>,
    server_id: Option<String>,
    session_id: Option<String>,
) -> Value {
    let mut ack = Map::new();
    ack.insert("type".to_string(), Value::String("vcp-ack".to_string()));
    ack.insert("version".to_string(), Value::String(negotiated));
    ack.insert("supported".to_string(), Value::Array(supported));
    ack.insert("unsupported".to_string(), Value::Array(unsupported));
    ack.insert("capabilities".to_string(), Value::Object(capabilities));
    ack.insert("core_features".to_string(), Value::Object(core_features));
    if let Some(server_id) = server_id {
        ack.insert("server_id".to_string(), Value::String(server_id));
    }
    if let Some(session_id) = session_id {
        ack.insert("session_id".to_string(), Value::String(session_id));
    }
    Value::Object(ack)
}

/// Negotiate the canonical lowercase `vcp-hello` / `vcp-ack` wire handshake.
///
/// Malformed client extension identifiers are ignored as required by VCP 3.1.
/// Valid identifiers retain client order and duplicate raw entries are rejected. Extension
/// activation is disabled for negotiated versions below 3.1.
///
/// # Errors
///
/// Returns an error for malformed messages or server configuration. A valid
/// handshake with no mutually supported version returns a structured
/// `VERSION_UNSUPPORTED` `vcp-error` value instead.
pub fn negotiate_handshake(client_hello: &Value, server: &Value) -> Result<Value, String> {
    bound_handshake(client_hello, server)?;

    let Some(hello) = client_hello.as_object() else {
        return Err("VCP-Hello must be an object with type 'vcp-hello'".to_string());
    };
    if hello.get("type").and_then(Value::as_str) != Some("vcp-hello") {
        return Err("VCP-Hello must be an object with type 'vcp-hello'".to_string());
    }
    let Some(server) = server.as_object() else {
        return Err("server capability configuration must be an object".to_string());
    };

    let supported_versions = server_versions(server)?;
    let client_version = hello.get("version").and_then(Value::as_str);
    let min_version = hello.get("min_version").map_or(Some("1.0"), Value::as_str);
    let (Some(client_version), Some(min_version)) = (client_version, min_version) else {
        return Ok(capability_error(
            "VERSION_UNSUPPORTED",
            "No mutually supported VCP version",
            Some(supported_versions),
        ));
    };
    if minor_version_parts(client_version, "version").is_err()
        || minor_version_parts(min_version, "min_version").is_err()
    {
        return Ok(capability_error(
            "VERSION_UNSUPPORTED",
            "No mutually supported VCP version",
            Some(supported_versions),
        ));
    }

    if compare_minor_versions(min_version, client_version).is_gt() {
        return Ok(capability_error(
            "VERSION_UNSUPPORTED",
            "No mutually supported VCP version",
            Some(supported_versions),
        ));
    }

    let requested = requested_extensions(hello.get("extensions"))?;
    validate_identifier_field(hello, "client_id", 256)?;

    if let Some(error) = identity_error(hello)? {
        return Ok(error);
    }

    let negotiated = supported_versions
        .iter()
        .rev()
        .find(|version| {
            !compare_minor_versions(version, min_version).is_lt()
                && !compare_minor_versions(version, client_version).is_gt()
        })
        .cloned();
    let Some(negotiated) = negotiated else {
        return Ok(capability_error(
            "VERSION_UNSUPPORTED",
            "No mutually supported VCP version",
            Some(supported_versions),
        ));
    };

    let extensions = server_extensions(server)?;

    let extensions_available = !compare_minor_versions(&negotiated, "3.1").is_lt();
    let mut supported = Vec::new();
    let mut unsupported = Vec::new();
    let mut capabilities = Map::new();
    let mut active_extensions = HashSet::new();
    for extension in requested {
        if extensions_available {
            if let Some(capability) = extensions.get(&extension) {
                supported.push(Value::String(extension.clone()));
                active_extensions.insert(extension.clone());
                capabilities.insert(extension, capability.clone());
                continue;
            }
        }
        unsupported.push(Value::String(extension));
    }

    apply_dependency_signals(&active_extensions, &mut capabilities);

    let core_features = validate_core_features(server)?;
    let server_id = validate_identifier_field(server, "server_id", 256)?;
    let session_id = validate_identifier_field(server, "session_id", 128)?;

    Ok(capability_ack(
        negotiated,
        supported,
        unsupported,
        capabilities,
        core_features,
        server_id,
        session_id,
    ))
}

/// A named extension and its exact semantic version.
#[derive(Debug, Clone, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
pub struct VersionedExtension {
    pub name: String,
    pub version: String,
}

/// A rejected extension and the stable reason code.
#[derive(Debug, Clone, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
pub struct RejectedExtension {
    pub name: String,
    pub reason: String,
}

/// Deterministic result for the versioned conformance profile.
#[derive(Debug, Clone, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
pub struct VersionedNegotiationResult {
    pub vcp_version: String,
    pub active_extensions: Vec<VersionedExtension>,
    pub rejected_extensions: Vec<RejectedExtension>,
}

fn semantic_version(value: &str) -> Result<(u64, u64, u64), String> {
    let parts: Vec<&str> = value.split('.').collect();
    if parts.is_empty() || parts.len() > 3 || parts.iter().any(|part| part.is_empty()) {
        return Err(format!("invalid semantic version: {value}"));
    }
    let mut numbers = [0_u64; 3];
    for (index, part) in parts.iter().enumerate() {
        numbers[index] = part
            .parse::<u64>()
            .map_err(|_| format!("invalid semantic version: {value}"))?;
    }
    Ok((numbers[0], numbers[1], numbers[2]))
}

/// Negotiate exact protocol and extension versions for the conformance profile.
///
/// The lowest compatible version is selected. Extensions with different major
/// versions are rejected rather than silently activated.
///
/// # Errors
///
/// Returns an error when either protocol version or any compared extension
/// version is not a one-to-three-component numeric semantic version.
pub fn negotiate_versioned(
    client_version: &str,
    client_extensions: &[VersionedExtension],
    server_version: &str,
    server_extensions: &[VersionedExtension],
) -> Result<VersionedNegotiationResult, String> {
    let client_protocol = semantic_version(client_version)?;
    let server_protocol = semantic_version(server_version)?;
    let vcp_version = if client_protocol <= server_protocol {
        client_version.to_string()
    } else {
        server_version.to_string()
    };
    let mut active_extensions = Vec::new();
    let mut rejected_extensions = Vec::new();
    for requested in client_extensions {
        let Some(supported) = server_extensions
            .iter()
            .find(|item| item.name == requested.name)
        else {
            rejected_extensions.push(RejectedExtension {
                name: requested.name.clone(),
                reason: "not_supported".to_string(),
            });
            continue;
        };
        let client_extension = semantic_version(&requested.version)?;
        let server_extension = semantic_version(&supported.version)?;
        if client_extension.0 != server_extension.0 {
            rejected_extensions.push(RejectedExtension {
                name: requested.name.clone(),
                reason: "incompatible_version".to_string(),
            });
            continue;
        }
        active_extensions.push(VersionedExtension {
            name: requested.name.clone(),
            version: if client_extension <= server_extension {
                requested.version.clone()
            } else {
                supported.version.clone()
            },
        });
    }
    Ok(VersionedNegotiationResult {
        vcp_version,
        active_extensions,
        rejected_extensions,
    })
}

/// Client's initial hello message in VCP negotiation.
#[derive(Debug, Clone, PartialEq, serde::Serialize, serde::Deserialize)]
pub struct VcpHello {
    /// Protocol version requested (e.g. "3.1.0").
    pub version: String,
    /// Requested extensions with their version constraints.
    /// Key: extension name, Value: version constraint (e.g. ">=1.0").
    pub extensions: HashMap<String, String>,
    /// Client capabilities.
    pub capabilities: HashMap<String, bool>,
}

impl VcpHello {
    /// Create a VCP hello for v2.0.0 with default settings.
    pub fn v2_0() -> Self {
        Self {
            version: "2.0.0".to_string(),
            extensions: HashMap::new(),
            capabilities: HashMap::new(),
        }
    }

    /// Create a VCP hello for v3.1.0 with default settings.
    #[deprecated(since = "4.0.0", note = "Use v2_0() for VCP v2.0 protocol")]
    pub fn v3_1() -> Self {
        Self {
            version: "3.1.0".to_string(),
            extensions: HashMap::new(),
            capabilities: HashMap::new(),
        }
    }

    /// Add an extension request.
    #[must_use]
    pub fn with_extension(mut self, name: impl Into<String>, version: impl Into<String>) -> Self {
        self.extensions.insert(name.into(), version.into());
        self
    }

    /// Add a capability flag.
    #[must_use]
    pub fn with_capability(mut self, name: impl Into<String>, enabled: bool) -> Self {
        self.capabilities.insert(name.into(), enabled);
        self
    }
}

/// Server's acknowledgment in VCP negotiation.
#[derive(Debug, Clone, PartialEq, serde::Serialize, serde::Deserialize)]
pub struct VcpAck {
    /// Agreed protocol version.
    pub version: String,
    /// Accepted extensions with negotiated versions.
    pub accepted_extensions: HashMap<String, String>,
    /// Rejected extensions with reasons.
    pub rejected_extensions: HashMap<String, String>,
    /// Server capabilities.
    pub server_capabilities: HashMap<String, bool>,
}

/// Negotiate a VCP connection.
///
/// Matches requested extensions against server capabilities. An extension is
/// accepted if the server lists it with a truthy capability value. Version
/// negotiation is basic: the client's requested version is accepted as-is if
/// the server supports the extension.
pub fn negotiate<S: BuildHasher>(
    hello: &VcpHello,
    server_capabilities: &HashMap<String, String, S>,
) -> VcpAck {
    let mut accepted = HashMap::new();
    let mut rejected = HashMap::new();
    let mut caps = HashMap::new();

    for ext_name in hello.extensions.keys() {
        if let Some(server_version) = server_capabilities.get(ext_name) {
            accepted.insert(ext_name.clone(), server_version.clone());
            caps.insert(ext_name.clone(), true);
        } else {
            rejected.insert(ext_name.clone(), "unsupported".to_string());
            caps.insert(ext_name.clone(), false);
        }
    }

    // Merge in server-only capabilities that the client didn't request
    for cap_name in server_capabilities.keys() {
        if !accepted.contains_key(cap_name) && !rejected.contains_key(cap_name) {
            caps.insert(cap_name.clone(), true);
        }
    }

    // Version negotiation: use v2.0.0 if client requests 2.x,
    // v3.1.0 if client requests 3.x (legacy), otherwise echo.
    let version = if hello.version.starts_with("2.") {
        "2.0.0".to_string()
    } else if hello.version.starts_with("3.") {
        "3.1.0".to_string()
    } else {
        hello.version.clone()
    };

    VcpAck {
        version,
        accepted_extensions: accepted,
        rejected_extensions: rejected,
        server_capabilities: caps,
    }
}

// ── Tests ──────────────────────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;

    fn canonical_server() -> Value {
        serde_json::json!({
            "supported_versions": ["3.1", "1.0", "3.0", "2.0"],
            "extensions": {
                "VCP-X-Personal": {"decay": true},
                "VCP-X-Torch": {"lineage_tracking": true}
            },
            "core_features": {
                "encryption": true,
                "injection_scanning": true,
                "revocation": true,
                "audit_chain": true,
                "context_opacity": true,
                "future_feature": false
            },
            "server_id": "server-1",
            "session_id": "session-1"
        })
    }

    fn server_caps() -> HashMap<String, String> {
        let mut caps = HashMap::new();
        caps.insert("personal".to_string(), "1.0.0".to_string());
        caps.insert("relational".to_string(), "1.0.0".to_string());
        caps.insert("consensus".to_string(), "1.0.0".to_string());
        caps
    }

    #[test]
    fn test_negotiate_all_accepted() {
        let hello = VcpHello::v2_0()
            .with_extension("personal", ">=1.0")
            .with_extension("relational", ">=1.0");
        let ack = negotiate(&hello, &server_caps());

        assert_eq!(ack.version, "2.0.0");
        assert_eq!(ack.accepted_extensions.len(), 2);
        assert!(ack.rejected_extensions.is_empty());
        assert!(ack.accepted_extensions.contains_key("personal"));
        assert!(ack.accepted_extensions.contains_key("relational"));
    }

    #[test]
    fn test_negotiate_partial_rejection() {
        let hello = VcpHello::v2_0()
            .with_extension("personal", ">=1.0")
            .with_extension("nonexistent", ">=1.0");
        let ack = negotiate(&hello, &server_caps());

        assert_eq!(ack.accepted_extensions.len(), 1);
        assert_eq!(ack.rejected_extensions.len(), 1);
        assert!(ack.rejected_extensions.contains_key("nonexistent"));
    }

    #[test]
    fn test_negotiate_empty_hello() {
        let hello = VcpHello::v2_0();
        let ack = negotiate(&hello, &server_caps());

        assert_eq!(ack.version, "2.0.0");
        assert!(ack.accepted_extensions.is_empty());
        assert!(ack.rejected_extensions.is_empty());
        // Server-only capabilities should still be listed
        assert!(ack.server_capabilities.contains_key("personal"));
    }

    #[test]
    fn test_negotiate_empty_server() {
        let hello = VcpHello::v2_0().with_extension("personal", ">=1.0");
        let ack = negotiate(&hello, &HashMap::new());

        assert_eq!(ack.accepted_extensions.len(), 0);
        assert_eq!(ack.rejected_extensions.len(), 1);
    }

    #[test]
    fn test_vcp_hello_builder() {
        let hello = VcpHello::v2_0()
            .with_extension("personal", ">=1.0")
            .with_capability("streaming", true);
        assert_eq!(hello.version, "2.0.0");
        assert_eq!(hello.extensions.len(), 1);
        assert_eq!(hello.capabilities.get("streaming"), Some(&true));
    }

    #[test]
    fn test_version_negotiation_2x() {
        let hello = VcpHello {
            version: "2.1.0".to_string(),
            extensions: HashMap::new(),
            capabilities: HashMap::new(),
        };
        let ack = negotiate(&hello, &HashMap::new());
        assert_eq!(ack.version, "2.0.0");
    }

    #[test]
    fn test_version_negotiation_3x_legacy() {
        let hello = VcpHello {
            version: "3.0.0".to_string(),
            extensions: HashMap::new(),
            capabilities: HashMap::new(),
        };
        let ack = negotiate(&hello, &HashMap::new());
        assert_eq!(ack.version, "3.1.0");
    }

    #[test]
    fn test_version_negotiation_non_2x_3x() {
        let hello = VcpHello {
            version: "4.0.0".to_string(),
            extensions: HashMap::new(),
            capabilities: HashMap::new(),
        };
        let ack = negotiate(&hello, &HashMap::new());
        assert_eq!(ack.version, "4.0.0");
    }

    #[test]
    fn canonical_handshake_partitions_only_valid_requested_extensions() {
        let hello = serde_json::json!({
            "type": "vcp-hello",
            "version": "3.1",
            "min_version": "3.0",
            "extensions": [
                "VCP-X-Personal",
                "not-an-extension",
                "VCP-X-Unknown"
            ],
            "identity": "family.safe.guide@1.2.0",
            "client_id": "client-1"
        });

        assert_eq!(
            negotiate_handshake(&hello, &canonical_server()).unwrap(),
            serde_json::json!({
                "type": "vcp-ack",
                "version": "3.1",
                "supported": ["VCP-X-Personal"],
                "unsupported": ["VCP-X-Unknown"],
                "capabilities": {"VCP-X-Personal": {"decay": true}},
                "core_features": {
                    "encryption": true,
                    "injection_scanning": true,
                    "revocation": true,
                    "audit_chain": true,
                    "context_opacity": true,
                    "future_feature": false
                },
                "server_id": "server-1",
                "session_id": "session-1"
            })
        );
    }

    #[test]
    fn canonical_handshake_returns_sorted_version_error() {
        let hello = serde_json::json!({
            "type": "vcp-hello",
            "version": "4.0",
            "min_version": "4.0"
        });
        let mut server = canonical_server();
        server["supported_versions"] = serde_json::json!(["3.1", "1.0", "3.0", "3.1"]);

        assert_eq!(
            negotiate_handshake(&hello, &server).unwrap(),
            serde_json::json!({
                "type": "vcp-error",
                "code": "VERSION_UNSUPPORTED",
                "message": "No mutually supported VCP version",
                "supported_versions": ["1.0", "3.0", "3.1"],
                "retry_after": null
            })
        );

        let reversed = serde_json::json!({
            "type": "vcp-hello",
            "version": "3.0",
            "min_version": "3.1"
        });
        assert_eq!(
            negotiate_handshake(&reversed, &server).unwrap()["code"],
            "VERSION_UNSUPPORTED"
        );
    }

    #[test]
    fn canonical_handshake_disables_extensions_before_v3_1() {
        let hello = serde_json::json!({
            "type": "vcp-hello",
            "version": "3.0",
            "min_version": "2.0",
            "extensions": ["VCP-X-Personal", "VCP-X-Unknown"]
        });
        let result = negotiate_handshake(&hello, &canonical_server()).unwrap();

        assert_eq!(result["version"], "3.0");
        assert_eq!(result["supported"], serde_json::json!([]));
        assert_eq!(
            result["unsupported"],
            serde_json::json!(["VCP-X-Personal", "VCP-X-Unknown"])
        );
        assert_eq!(result["capabilities"], serde_json::json!({}));
    }

    #[test]
    fn canonical_handshake_signals_missing_extension_dependencies_fail_safe() {
        let hello = serde_json::json!({
            "type": "vcp-hello",
            "version": "3.1",
            "extensions": ["VCP-X-Torch", "VCP-X-Intent"]
        });
        let mut server = canonical_server();
        server["extensions"]["VCP-X-Torch"] =
            serde_json::json!({"lineage": true, "degraded": false});
        server["extensions"]["VCP-X-Intent"] =
            serde_json::json!({"inference": true, "personal_signals": true});

        let result = negotiate_handshake(&hello, &server).unwrap();
        assert_eq!(
            result["capabilities"],
            serde_json::json!({
                "VCP-X-Torch": {"lineage": true, "degraded": true},
                "VCP-X-Intent": {"inference": true, "personal_signals": false}
            })
        );
    }

    #[test]
    fn canonical_handshake_rejects_malformed_messages_and_configuration() {
        let hello = serde_json::json!({"type": "vcp-hello", "version": "3.1"});
        let server = canonical_server();
        let mut long_client_id = hello.clone();
        long_client_id["client_id"] = Value::String("x".repeat(257));
        let mut empty_client_id = hello.clone();
        empty_client_id["client_id"] = Value::String(String::new());
        let mut null_extensions = hello.clone();
        null_extensions["extensions"] = Value::Null;
        let mut missing_versions = server.clone();
        missing_versions
            .as_object_mut()
            .unwrap()
            .remove("supported_versions");
        let mut bad_extension_registry = server.clone();
        bad_extension_registry["extensions"] = serde_json::json!({"invalid": {}});
        let mut missing_core_feature = server.clone();
        missing_core_feature["core_features"]
            .as_object_mut()
            .unwrap()
            .remove("revocation");
        let mut empty_server_id = server.clone();
        empty_server_id["server_id"] = Value::String(String::new());
        let mut empty_session_id = server.clone();
        empty_session_id["session_id"] = Value::String(String::new());

        for (bad_hello, bad_server, expected) in [
            (
                serde_json::json!({"type": "VCP-Hello", "version": "3.1"}),
                server.clone(),
                "type 'vcp-hello'",
            ),
            (long_client_id, server.clone(), "at most 256"),
            (empty_client_id, server.clone(), "at least 1"),
            (null_extensions, server.clone(), "bounded array"),
            (hello.clone(), missing_versions, "non-empty array"),
            (
                hello.clone(),
                bad_extension_registry,
                "map VCP-X-* identifiers",
            ),
            (
                hello.clone(),
                missing_core_feature,
                "revocation must be a boolean",
            ),
            (hello.clone(), empty_server_id, "at least 1"),
            (hello, empty_session_id, "at least 1"),
        ] {
            let error = negotiate_handshake(&bad_hello, &bad_server).unwrap_err();
            assert!(
                error.contains(expected),
                "{error:?} did not contain {expected:?}"
            );
        }
    }

    #[test]
    fn canonical_handshake_reports_invalid_identity_without_activating_session() {
        let hello = serde_json::json!({
            "type": "vcp-hello",
            "version": "3.1",
            "identity": "not a VCP identity",
            "extensions": ["VCP-X-Personal"]
        });

        assert_eq!(
            negotiate_handshake(&hello, &canonical_server()).unwrap(),
            serde_json::json!({
                "type": "vcp-error",
                "code": "IDENTITY_INVALID",
                "message": "The supplied VCP/I identity token is invalid",
                "retry_after": null
            })
        );
    }

    #[test]
    fn canonical_handshake_enforces_resource_limits_at_the_boundary() {
        let mut hello = serde_json::json!({"type": "vcp-hello", "version": "3.1"});
        hello["extensions"] = Value::Array(
            (0..MAX_EXTENSION_COUNT)
                .map(|index| Value::String(format!("VCP-X-A{index}")))
                .collect(),
        );
        assert!(negotiate_handshake(&hello, &canonical_server()).is_ok());

        hello["extensions"] = Value::Array(
            (0..=MAX_EXTENSION_COUNT)
                .map(|index| Value::String(format!("VCP-X-A{index}")))
                .collect(),
        );
        assert!(negotiate_handshake(&hello, &canonical_server())
            .unwrap_err()
            .contains("bounded array"));

        let oversized = serde_json::json!({
            "type": "vcp-hello",
            "version": "3.1",
            "padding": "x".repeat(MAX_HANDSHAKE_BYTES)
        });
        assert!(negotiate_handshake(&oversized, &canonical_server())
            .unwrap_err()
            .contains("64 KiB"));

        let mut too_many_versions = canonical_server();
        too_many_versions["supported_versions"] = Value::Array(
            (0..=MAX_SUPPORTED_VERSION_COUNT)
                .map(|index| Value::String(format!("{index}.0")))
                .collect(),
        );
        assert!(negotiate_handshake(
            &serde_json::json!({"type": "vcp-hello", "version": "3.1"}),
            &too_many_versions,
        )
        .unwrap_err()
        .contains("64 entries"));

        let mut too_many_server_extensions = canonical_server();
        too_many_server_extensions["extensions"] = Value::Object(
            (0..=MAX_EXTENSION_COUNT)
                .map(|index| (format!("VCP-X-A{index}"), serde_json::json!({})))
                .collect(),
        );
        assert!(negotiate_handshake(
            &serde_json::json!({"type": "vcp-hello", "version": "3.1"}),
            &too_many_server_extensions,
        )
        .unwrap_err()
        .contains("256 entries"));
    }

    #[test]
    fn canonical_handshake_enforces_extension_identifier_length_boundary() {
        let valid = format!("VCP-X-A{}", "b".repeat(121));
        let oversized = format!("{valid}c");
        assert_eq!(valid.len(), MAX_EXTENSION_ID_CHARS);

        let hello = serde_json::json!({
            "type": "vcp-hello",
            "version": "3.1",
            "extensions": [valid]
        });
        let mut server = canonical_server();
        server["extensions"] = serde_json::json!({(valid.clone()): {"enabled": true}});
        let result = negotiate_handshake(&hello, &server).unwrap();

        assert_eq!(result["supported"], serde_json::json!([valid]));
        assert_eq!(result["unsupported"], serde_json::json!([]));

        let oversized_hello = serde_json::json!({
            "type": "vcp-hello",
            "version": "3.1",
            "extensions": [oversized]
        });
        assert!(negotiate_handshake(&oversized_hello, &canonical_server())
            .unwrap_err()
            .contains("1 to 128"));

        let mut oversized_server = canonical_server();
        oversized_server["extensions"] = serde_json::json!({
            (format!("VCP-X-A{}", "b".repeat(122))): {}
        });
        assert!(negotiate_handshake(&hello, &oversized_server)
            .unwrap_err()
            .contains("map VCP-X-* identifiers"));
    }

    #[test]
    fn canonical_handshake_string_limits_count_unicode_code_points() {
        let filtered_at_limit = "😀".repeat(MAX_EXTENSION_ID_CHARS);
        let hello = serde_json::json!({
            "type": "vcp-hello",
            "version": "3.1",
            "client_id": "😀".repeat(256),
            "extensions": [filtered_at_limit]
        });
        let result = negotiate_handshake(&hello, &canonical_server()).unwrap();
        assert_eq!(result["supported"], serde_json::json!([]));
        assert_eq!(result["unsupported"], serde_json::json!([]));

        let mut oversized_extension = hello.clone();
        oversized_extension["extensions"] =
            serde_json::json!(["😀".repeat(MAX_EXTENSION_ID_CHARS + 1)]);
        assert!(
            negotiate_handshake(&oversized_extension, &canonical_server())
                .unwrap_err()
                .contains("1 to 128")
        );

        let mut oversized_client = hello;
        oversized_client["client_id"] = Value::String("😀".repeat(257));
        assert!(negotiate_handshake(&oversized_client, &canonical_server())
            .unwrap_err()
            .contains("at most 256"));
    }

    #[test]
    fn canonical_handshake_rejects_duplicate_raw_extension_strings() {
        for extensions in [
            serde_json::json!(["VCP-X-Personal", "VCP-X-Personal"]),
            serde_json::json!(["invalid", "invalid"]),
        ] {
            let hello = serde_json::json!({
                "type": "vcp-hello",
                "version": "3.1",
                "extensions": extensions
            });
            assert!(negotiate_handshake(&hello, &canonical_server())
                .unwrap_err()
                .contains("unique"));
        }
    }

    #[test]
    fn canonical_handshake_enforces_version_component_boundaries() {
        let version = "999999999.999999999";
        let hello = serde_json::json!({
            "type": "vcp-hello",
            "version": version,
            "min_version": version
        });
        let mut server = canonical_server();
        server["supported_versions"] = serde_json::json!([version]);

        assert_eq!(
            negotiate_handshake(&hello, &server).unwrap()["version"],
            version
        );

        for malformed in ["1000000000.0", "3.0000000000", "03.1", "3.01"] {
            let hello = serde_json::json!({"type": "vcp-hello", "version": malformed});
            assert_eq!(
                negotiate_handshake(&hello, &canonical_server()).unwrap()["code"],
                "VERSION_UNSUPPORTED"
            );
        }
    }

    #[test]
    fn canonical_handshake_ignores_invalid_server_versions() {
        let hello = serde_json::json!({"type": "vcp-hello", "version": "3.1"});
        let mut server = canonical_server();
        server["supported_versions"] =
            serde_json::json!(["3.0", "bogus", null, "2.0", "3.1", "3.0"]);

        assert_eq!(
            negotiate_handshake(&hello, &server).unwrap()["version"],
            "3.1"
        );

        server["supported_versions"] = serde_json::json!(["bogus", null]);
        assert!(negotiate_handshake(&hello, &server)
            .unwrap_err()
            .contains("valid version"));
    }
}
