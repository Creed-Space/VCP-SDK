# Changelog

All notable changes to the VCP SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Python: Hook system (`hooks/` module with types, registry, executor, built-in hooks)
- Python: Revocation checking (`revocation.py` with online + CRL support, SSRF protection, caching)
- Python: Inter-agent messaging v1.2 envelope support (`messaging.py`)
- Rust: Hook system (`hooks.rs` with registry and chain executor)
- Rust: Trust anchor management (`trust.rs` with `TrustAnchor`, `TrustConfig`)
- Rust: Full transport layer (content canonicalization, manifest signing/verification, bundle verification)
- Language-agnostic conformance test suite (`conformance/`)
- Runnable examples for Python and Rust (`examples/`)

### Changed
- Personas updated from NZGAMRHC to NZGAMDC (Anchor/HotRod replaced by Mediator)
- Python SDK version bumped to 2.0.0 for VCP/I, VCP/S, VCP/A layer additions

### Fixed
- Resolved mypy type-check failures in Python SDK
- Resolved CI lint and formatting failures across Python, Rust, and JSON schema validation
- Resolved clippy warnings in Rust SDK

## [1.1.0] - 2026-01-18

### Added
- **VCP Specification v1.1** -- R-line (Line 8) for real-time personal state in CSM-1 tokens
- **Rust SDK** (`vcp-core`, `vcp-wasm`, `vcp-cli`) -- High-performance parsing with `no_std` support and WASM bindings
- **TypeScript/WebMCP SDK** (`@vcp/webmcp`) -- Browser-side VCP tool registration via `navigator.modelContext` (Chrome 145+)
- MCP-B polyfill for non-Chrome browsers
- Five WebMCP tools: `vcp_chat`, `vcp_build_token`, `vcp_parse_token`, `vcp_transmission_summary`, `vcp_list_personas`
- JSON Schema definitions for all protocol layers

### Changed
- Restructured repository for polyglot SDK support (Python, Rust, TypeScript)
- CSM-1 token format extended from 7 lines to 8 lines (R-line addition)

## [1.0.0] - 2026-01-11

### Added
- **VCP Specification v1.0** -- Complete protocol specification
- **Python SDK** -- Reference implementation with identity resolution, CSM-1 encoding, context management, and LLM integration
- Four-layer protocol stack: VCP/I (Identity), VCP/T (Transport), VCP/S (Semantics), VCP/A (Adaptation)
- Universal Value Codes (UVC) naming scheme
- Signed bundle format with Ed25519 signatures and SHA-256 content hashes
- Three-tier privacy architecture (public/consent/private)
- Six built-in personas (Muse, Sentinel, Godparent, Ambassador, Anchor, Nanny)
- VCP Demo site with interactive playground
- Academic paper draft
- MIT LICENSE, CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md
- CI workflow (Python lint/test, Rust build/test, TypeScript type check, schema validation)
- GitHub issue templates (Bug Report, Feature Request, Spec Amendment)
- Pull request template
- Dependabot configuration for all package ecosystems
- Comprehensive README with architecture diagrams, quick-start guides, and full documentation index

[Unreleased]: https://github.com/Creed-Space/VCP-SDK/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/Creed-Space/VCP-SDK/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/Creed-Space/VCP-SDK/releases/tag/v1.0.0
