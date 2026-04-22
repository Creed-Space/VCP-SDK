# Changelog

All notable changes to the VCP SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.2.0] - 2026-04-22

### Added
- **VCP v3.2 / VEP-0004 adaptation layer** — `vcp.adaptation.context` (Python), `src/extensions/context.ts` (TypeScript), `vcp_core::situational` + `vcp_core::context` (Rust) now implement the full 18-dimension v3.2 context model:
  - 13 situational dimensions (positions 1-13): time, space, company, culture, occasion, environment, agency, constraints, system_context, **embodiment** (VEP-0004, pos 10), **proximity** (VEP-0004, pos 11), **relationship** (VEP-0004, pos 12), **formality** (VEP-0004, pos 13).
  - 5 personal-state dimensions on the R-line: cognitive_state, emotional_tone, energy_level, perceived_urgency, body_signals — each an optional `{value, intensity 1-5}`.
  - Wire-format band separator `‖` (U+2016 DOUBLE VERTICAL LINE) between situational and personal halves.
  - RELATIONSHIP is free-form: its value is a compound `{tie}:{function}` string (e.g. `colleague:professional`), not a closed emoji vocabulary.
- **Conformance classification** — `conformance_level()` method on `VCPContext` / `FullContext` (Python + TypeScript + Rust) returns `VCP-Minimal` (core 9 only), `VCP-Standard` (core + R-line), or `VCP-Extended` (any VEP-0004 dim).
- **VEP-0004 conformance fixtures** — `conformance/adaptation/context_encoding_extended.json` with 12 test vectors covering each VEP-0004 dimension in isolation, the canonical 18-dim example, VS16 parser-compatibility (↔️ qualified vs bare), and the Extended-over-Standard precedence rule.
- **JSON Schema v3.2** — `schemas/vcp-adaptation-context.schema.json` upgraded from v2 to v3.2 with nested `parsed.situational` / `parsed.personal` shape, `conformance_level` enum field, and per-dimension value definitions.

### Changed
- **CULTURE values** are now communication styles per CSM-1 (high_context, low_context, formal, casual, mixed), not nationalities. The nationality vocabulary was never in spec and is rejected by the v3.2 encoders.
- Python `VCPContext` refactored from a plain `@dataclass` to a class with `__slots__` and backwards-compatible `dimensions=` constructor kwarg (aliases `situational=`).
- Python exports `SituationalDimension` and `PersonalStateDimension` from `vcp.adaptation`; `Dimension` remains as a backwards-compat alias for `SituationalDimension`.
- Rust `FullContext::situational` is now a 13-dimension `SituationalContext`; the enum gains `Embodiment`, `Proximity`, `Relationship`, `Formality` variants and a `position()` accessor. `ConformanceLevel` is re-exported at the crate root.

### Removed
- The deprecated VCP v3.0 **STATE** dimension (removed in v3.1; SYSTEM_CONTEXT occupies position 9 and the prior STATE enum value is no longer exposed).

## [4.1.0] - 2026-04-06

### Added
- **PDP Enforcement Module** (`vcp/enforcement.py`) — Standalone policy enforcement for VCP bundles without requiring a full safety stack. Includes `PDPPlugin` interface, `PDPEnforcer` orchestrator, and three built-in plugins: `RefusalBoundaryPlugin`, `AdherenceLevelPlugin`, `BundleExpiryPlugin`.
- **Purge Handler Registration** — `AuditLogger.register_purge_handler()` lets external sinks (Redis, database) register GDPR purge logic. Warns if `log_callback` is set without a handler.

### Fixed
- **GDPR Purge Persistence Gap** — `purge_by_session()` now scrubs exported JSON files (not just in-memory entries), with thread-safe file rewriting and tombstone receipts that include file-level evidence.
- **`datetime.utcnow()` Deprecation** — All remaining instances replaced with `datetime.now(timezone.utc)` across source and test files.
- **Thread Safety** — `export_json()` path tracking and `_purge_exported_files()` now run inside `self._lock`, closing TOCTOU race conditions.

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
- **TypeScript/WebMCP SDK** (`@creed-space/vcp-sdk`) -- Browser-side VCP tool registration via `navigator.modelContext` (Chrome 145+)
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

[4.2.0]: https://github.com/Creed-Space/VCP-SDK/compare/v4.1.0...v4.2.0
[4.1.0]: https://github.com/Creed-Space/VCP-SDK/compare/v4.0.0...v4.1.0
[4.0.0]: https://github.com/Creed-Space/VCP-SDK/compare/v3.1.0...v4.0.0
[Unreleased]: https://github.com/Creed-Space/VCP-SDK/compare/v4.2.0...HEAD
[3.1.0]: https://github.com/Creed-Space/VCP-SDK/compare/v1.1.0...v3.1.0
[1.1.0]: https://github.com/Creed-Space/VCP-SDK/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/Creed-Space/VCP-SDK/releases/tag/v1.0.0
