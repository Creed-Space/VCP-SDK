//! # vcp-core
//!
//! Core types and parsing for the **Value Context Protocol (VCP)**.
//!
//! VCP is a protocol for expressing and transmitting human values,
//! context, and personal state between AI systems so they can
//! adapt their behaviour accordingly.
//!
//! ## Modules
//!
//! | Module | Purpose |
//! |--------|---------|
//! | [`identity`] | VCP/I token parsing (`family.safe.guide@1.2.0`) |
//! | [`csm1`] | CSM-1 compact codes and 8-line tokens |
//! | [`personal`] | Personal state dimensions (cognitive, emotional, ...) |
//! | [`situational`] | Situational context (time, space, company, ...) |
//! | [`context`] | Full context wire format (situational + personal) |
//! | [`transport`] | Content hashing, canonicalization, signing, bundle verification |
//! | [`trust`] | Trust anchor management for issuers and auditors |
//! | [`hooks`] | Hook system for the adaptation pipeline (6 hook types) |
//! | [`revocation`] | Bundle revocation checking with SSRF protection |
//! | [`error`] | Error types and verification codes |
//!
//! ## Quick Start
//!
//! ```rust
//! use vcp_core::identity::VcpToken;
//! use vcp_core::csm1::{Csm1Code, Persona};
//! use vcp_core::context::FullContext;
//! use vcp_core::transport::compute_content_hash;
//!
//! // Parse a VCP identity token.
//! let token = VcpToken::parse("family.safe.guide@1.2.0").unwrap();
//! assert_eq!(token.domain(), "family");
//!
//! // Parse a CSM-1 compact code.
//! let code = Csm1Code::parse("N5+F+E").unwrap();
//! assert_eq!(code.persona, Persona::Nanny);
//! assert_eq!(code.encode(), "N5+F+E");
//!
//! // Hash constitution content.
//! let hash = compute_content_hash("Be kind to everyone.").unwrap();
//! assert!(hash.starts_with("sha256:"));
//! ```

#![warn(clippy::all, clippy::pedantic)]
#![allow(clippy::module_name_repetitions)]
#![allow(clippy::must_use_candidate)]

pub mod composer;
pub mod context;
pub mod csm1;
pub mod error;
pub mod hooks;
pub mod identity;
pub mod orchestrator;
pub mod personal;
pub mod revocation;
pub mod situational;
pub mod transport;
pub mod trust;

// Re-export commonly used types at crate root.
pub use context::FullContext;
pub use csm1::{Csm1Code, Csm1Token, Persona, Scope};
pub use error::{VcpError, VcpResult};
pub use hooks::{
    ChainResult, Hook, HookAction, HookExecutor, HookHandler, HookInput, HookRegistry, HookResult,
    HookScope, HookType,
};
pub use identity::VcpToken;
pub use personal::{PersonalDimension, PersonalState};
pub use revocation::{RevocationChecker, RevocationStatus};
pub use situational::SituationalContext;
pub use transport::{
    compute_content_hash, sign_manifest, verify_content_hash, verify_manifest_signature,
};
pub use trust::{TrustAnchor, TrustConfig};

// Orchestrator and composition engine.
pub use composer::{Composer, CompositionMode, CompositionResult, Conflict, Constitution};
pub use orchestrator::{Orchestrator, ReplayCache, VerificationContext};
