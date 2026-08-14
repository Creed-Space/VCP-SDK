# Rust Implementation

<!-- wiki:type = system -->
<!-- wiki:scope = vcp-sdk -->
<!-- wiki:created = 2026-05-23 -->
<!-- wiki:updated = 2026-05-23 -->
<!-- wiki:status = active -->

## Summary

The Rust implementation targets high-performance and WASM deployment. It is a Cargo workspace with three crates: `vcp-core` (types and parsing), `vcp-wasm` (WASM bindings for browser), and `vcp-cli` (command-line tool). Current workspace version: 4.2.0 (2021 edition, MIT license). (rust/Cargo.toml; rust/vcp-core/src/lib.rs)

## Workspace Structure

```
rust/
├── Cargo.lock
├── Cargo.toml          # Workspace manifest, version 4.2.0
├── target/
├── vcp-cli/            # CLI tool
├── vcp-core/           # Core types and parsing
│   └── src/
│       ├── lib.rs      # Public module exports + quick-start docs
│       ├── identity.rs  # VCP/I token parsing
│       ├── csm1.rs     # CSM-1 compact codes (e.g. "N5+F+E")
│       ├── context.rs  # Full context wire format
│       ├── transport.rs # Hashing, canonicalization, signing, bundle verification
│       ├── trust.rs    # Trust anchor management
│       ├── hooks.rs    # 6-type hook system for adaptation pipeline
│       ├── revocation.rs # Bundle revocation with SSRF protection
│       ├── orchestrator.rs
│       ├── composer.rs
│       ├── personal.rs  # Personal state dimensions (cognitive, emotional, ...)
│       ├── situational.rs # Situational context (time, space, company, ...)
│       ├── negotiation.rs
│       ├── error.rs    # Error types and verification codes
│       └── extensions/ # VCP-X-* extensions
└── vcp-wasm/           # WASM bindings
    └── src/
        └── lib.rs
```

(rust/ directory listing; rust/vcp-core/src/lib.rs)

## Key Module Purposes (`vcp-core`)

| Module | Purpose |
|--------|---------|
| `identity` | VCP/I token parsing: `VcpToken::parse("family.safe.guide@1.2.0")` |
| `csm1` | CSM-1 compact codes: `Csm1Code::parse("N5+F+E")` returns `Persona::Nanny`, adherence 5, goals Family+Education |
| `transport` | `compute_content_hash(content)` → `"sha256:<hex>"` |
| `personal` | Personal state dimensions (cognitive load, emotional state, etc.) |
| `situational` | Situational context encoding (time, space, company present) |
| `hooks` | 6-type hook system for the adaptation pipeline |
| `revocation` | Bundle revocation checking with SSRF protection (prevents SSRF via revocation endpoint) |

(rust/vcp-core/src/lib.rs:10–43)

## Quick Start (Rust)

```rust
use vcp_core::identity::VcpToken;
use vcp_core::csm1::{Csm1Code, Persona};
use vcp_core::transport::compute_content_hash;

let token = VcpToken::parse("family.safe.guide@1.2.0").unwrap();
assert_eq!(token.domain(), "family");

let code = Csm1Code::parse("N5+F+E").unwrap();
assert_eq!(code.persona, Persona::Nanny);

let hash = compute_content_hash("Be kind to everyone.").unwrap();
assert!(hash.starts_with("sha256:"));
```
(rust/vcp-core/src/lib.rs:26–44)

## WASM Target (`vcp-wasm`)

`vcp-wasm/src/lib.rs` provides WASM bindings for browser-side deployment. This is distinct from `webmcp/` which provides JavaScript tooling for the WebMCP API. The WASM target allows running VCP verification natively in the browser without a server round-trip. [UNVERIFIED: which specific functions are exposed in the WASM bindings — read `vcp-wasm/src/lib.rs` for full detail]

## Relationship to Python SDK

The Rust crates mirror the Python module structure but are independent implementations. Conformance tests in `conformance/` ensure both produce identical results for the same inputs. (VCP-SDK directory listing)

## TypeScript SDK Status

There is NO standalone TypeScript SDK directory in this repo. TypeScript functionality is provided via:
1. `webmcp/` — Web-facing MCP bindings (TypeScript, targets `navigator.modelContext` WebMCP API)
2. `vcp-wasm/` — Rust compiled to WASM, callable from JavaScript/TypeScript

(VCP-SDK/ directory listing — no `typescript/` directory present)

## Provenance

- Sources consulted: `rust/Cargo.toml`; `rust/vcp-core/src/lib.rs:1–60`; `rust/` directory listing; `rust/vcp-core/src/` listing; `rust/vcp-wasm/src/` listing (lib.rs confirmed)
- Last verified against sources: 2026-05-23

## See Also

- [[vcp-sdk:systems/python-sdk-modules]] — Python reference implementation
- [[vcp-sdk:systems/webmcp-typescript]] — JavaScript/TypeScript browser bindings
- [[vcp-sdk:flows/bundle-sign-verify]] — the flow both implementations support
