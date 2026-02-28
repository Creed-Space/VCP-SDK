//! VCP negotiation — hello/ack handshake for capability exchange.
//!
//! The VCP negotiation protocol allows a client and server to agree on
//! which protocol extensions are supported and at what versions.

use std::collections::HashMap;

/// Client's initial hello message in VCP negotiation.
#[derive(Debug, Clone, PartialEq)]
#[cfg_attr(feature = "serde", derive(serde::Serialize, serde::Deserialize))]
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
    /// Create a VCP hello for v3.1.0 with default settings.
    pub fn v3_1() -> Self {
        Self {
            version: "3.1.0".to_string(),
            extensions: HashMap::new(),
            capabilities: HashMap::new(),
        }
    }

    /// Add an extension request.
    pub fn with_extension(mut self, name: impl Into<String>, version: impl Into<String>) -> Self {
        self.extensions.insert(name.into(), version.into());
        self
    }

    /// Add a capability flag.
    pub fn with_capability(mut self, name: impl Into<String>, enabled: bool) -> Self {
        self.capabilities.insert(name.into(), enabled);
        self
    }
}

/// Server's acknowledgment in VCP negotiation.
#[derive(Debug, Clone, PartialEq)]
#[cfg_attr(feature = "serde", derive(serde::Serialize, serde::Deserialize))]
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
pub fn negotiate(hello: &VcpHello, server_capabilities: &HashMap<String, String>) -> VcpAck {
    let mut accepted = HashMap::new();
    let mut rejected = HashMap::new();
    let mut caps = HashMap::new();

    for (ext_name, _requested_version) in &hello.extensions {
        if let Some(server_version) = server_capabilities.get(ext_name) {
            accepted.insert(ext_name.clone(), server_version.clone());
            caps.insert(ext_name.clone(), true);
        } else {
            rejected.insert(ext_name.clone(), "unsupported".to_string());
            caps.insert(ext_name.clone(), false);
        }
    }

    // Merge in server-only capabilities that the client didn't request
    for (cap_name, _cap_version) in server_capabilities {
        if !accepted.contains_key(cap_name) && !rejected.contains_key(cap_name) {
            caps.insert(cap_name.clone(), true);
        }
    }

    // Version negotiation: use v3.1.0 if client requests 3.x, otherwise echo
    let version = if hello.version.starts_with("3.") {
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
        let hello = VcpHello::v3_1()
            .with_extension("personal", ">=1.0")
            .with_extension("relational", ">=1.0");
        let ack = negotiate(&hello, &server_caps());

        assert_eq!(ack.version, "3.1.0");
        assert_eq!(ack.accepted_extensions.len(), 2);
        assert!(ack.rejected_extensions.is_empty());
        assert!(ack.accepted_extensions.contains_key("personal"));
        assert!(ack.accepted_extensions.contains_key("relational"));
    }

    #[test]
    fn test_negotiate_partial_rejection() {
        let hello = VcpHello::v3_1()
            .with_extension("personal", ">=1.0")
            .with_extension("nonexistent", ">=1.0");
        let ack = negotiate(&hello, &server_caps());

        assert_eq!(ack.accepted_extensions.len(), 1);
        assert_eq!(ack.rejected_extensions.len(), 1);
        assert!(ack.rejected_extensions.contains_key("nonexistent"));
    }

    #[test]
    fn test_negotiate_empty_hello() {
        let hello = VcpHello::v3_1();
        let ack = negotiate(&hello, &server_caps());

        assert_eq!(ack.version, "3.1.0");
        assert!(ack.accepted_extensions.is_empty());
        assert!(ack.rejected_extensions.is_empty());
        // Server-only capabilities should still be listed
        assert!(ack.server_capabilities.contains_key("personal"));
    }

    #[test]
    fn test_negotiate_empty_server() {
        let hello = VcpHello::v3_1().with_extension("personal", ">=1.0");
        let ack = negotiate(&hello, &HashMap::new());

        assert_eq!(ack.accepted_extensions.len(), 0);
        assert_eq!(ack.rejected_extensions.len(), 1);
    }

    #[test]
    fn test_vcp_hello_builder() {
        let hello = VcpHello::v3_1()
            .with_extension("personal", ">=1.0")
            .with_capability("streaming", true);
        assert_eq!(hello.version, "3.1.0");
        assert_eq!(hello.extensions.len(), 1);
        assert_eq!(hello.capabilities.get("streaming"), Some(&true));
    }

    #[test]
    fn test_version_negotiation_3x() {
        let hello = VcpHello {
            version: "3.0.0".to_string(),
            extensions: HashMap::new(),
            capabilities: HashMap::new(),
        };
        let ack = negotiate(&hello, &HashMap::new());
        assert_eq!(ack.version, "3.1.0");
    }

    #[test]
    fn test_version_negotiation_non_3x() {
        let hello = VcpHello {
            version: "4.0.0".to_string(),
            extensions: HashMap::new(),
            capabilities: HashMap::new(),
        };
        let ack = negotiate(&hello, &HashMap::new());
        assert_eq!(ack.version, "4.0.0");
    }
}
