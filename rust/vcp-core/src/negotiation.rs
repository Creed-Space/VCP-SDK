//! VCP negotiation — hello/ack handshake for capability exchange.
//!
//! The VCP negotiation protocol allows a client and server to agree on
//! which protocol extensions are supported and at what versions.

use std::collections::HashMap;
use std::hash::BuildHasher;

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
}
