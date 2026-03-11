# Changelog

All notable changes to the VCP SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.0.0] - 2026-03-08

### Added
- **VCP v2.0 Specification Support** — Protocol version bumped from 1.0/1.2 to 2.0 across all SDKs
- **Extended Token Types** — New enums for refusal boundaries, testimony, creed adoption, and compliance attestation tokens
- **VCP/M Messaging v2.0** — Inter-agent messaging updated from v1.2 to v2.0 with context field trust model, escalation-transition severity alignment, and version negotiation
- **JSON Schema v2** — New `vcp-manifest-v2.schema.json` and `vcp-messaging-v2.0.schema.json`
- **Version Negotiation** — Python SDK adds `check_version_compatibility()` for major/minor version handling
- Python: Hook system, revocation checking, inter-agent messaging (previously unreleased)
- Rust: Hook system, trust anchor management, full transport layer (previously unreleased)
- Language-agnostic conformance test suite and runnable examples (previously unreleased)

### Changed
- `vcp_version` in bundle manifests changed from `"1.0"` to `"2.0"`
- `vcp_message` in inter-agent messages changed from `"1.2"` to `"2.0"`
- Personas updated from NZGAMRHC to NZGAMDC (previously unreleased)
- Python SDK version bumped to 4.0.0
- Rust SDK versions bumped to 4.0.0

### Fixed
- Resolved mypy type-check failures in Python SDK (previously unreleased)
- Resolved CI lint and formatting failures (previously unreleased)
- Resolved clippy warnings in Rust SDK (previously unreleased)

## [3.1.0] - 2026-02-28

### Added
- **Extension modules** for all 4 VCP v3.1 extensions:
  - Personal State — signal declaration, exponential/linear decay, lifecycle tracking
  - Relational Context — AI self-model, trust levels, standing, bias detection
  - Constitutional Consensus — Schulze method voting, pairwise matrix, strongest paths
  - Session Handoff (Torch) — generation, consumption, lineage tracking
- **Capability Negotiation** — VCP-Hello/VCP-Ack handshake protocol
- **53 conformance test vectors** across 5 categories (personal, relational, consensus, torch, negotiation)
- **Cross-SDK conformance CI** — GitHub Actions workflow testing Python, TypeScript, and Rust
- Python, TypeScript, and Rust implementations with full parity

### Changed
- Ballot model standardized to grouped `rankings: list[list[str]]` format across all SDKs
- Python LifecycleState enum uses `SET`/`STALE` (replaces `FRESH`/`BASELINE`)

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

[4.0.0]: https://github.com/Creed-Space/VCP-SDK/compare/v3.1.0...v4.0.0
[Unreleased]: https://github.com/Creed-Space/VCP-SDK/compare/v4.0.0...HEAD
[3.1.0]: https://github.com/Creed-Space/VCP-SDK/compare/v1.1.0...v3.1.0
[1.1.0]: https://github.com/Creed-Space/VCP-SDK/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/Creed-Space/VCP-SDK/releases/tag/v1.0.0
