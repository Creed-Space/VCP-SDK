# Changelog

All notable changes to the VCP SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

Version headings in this file describe repository metadata for source-only
candidates; no registry release or `vX.Y.Z` tag has been published yet (see the
README publication-state note).

### Added
- `vcp-mcp-server` console script and `python/src/vcp/mcp_server.py`, exposing
  the SDK through the `[mcp]` extra with JSON-schema-validated tool inputs.
- Rust `vcp_core::strict_json` and hardened Python `parse_json_strict`
  (duplicate keys, non-finite constants, and overflowing numeric literals such
  as `1e400` are rejected before signatures are considered).
- Shared `parse_rfc3339_utc` helper used by bundle, trust, revocation, and skill
  manifest parsing so nanosecond fractions parse identically on Python 3.10+.
  Timestamps must now match the RFC 3339 grammar (`YYYY-MM-DDTHH:MM:SS[.frac]`
  plus `Z` or `±HH:MM`); looser `fromisoformat` inputs such as date-only values
  or colon-less offsets are rejected.
- WebMCP `registration.ts` cleanup contract and polyfill loader changes;
  `conformance/runners/context_parity.py` now also executes the WebMCP context
  encoder/decoder (`webmcp/scripts/run-context.mjs`), and the coverage manifest
  records those vectors as checked for WebMCP.
- Capability-negotiation fixtures for an invalid identity token
  (`IDENTITY_INVALID`), forward-compatible boolean core-feature flags, and the
  rejection of non-boolean core-feature entries.
- `schemas/vcp-conformance-aggregate-report.schema.json`; updates to the
  manifest v1, messaging v2.0, and CSM-1 schema copies.
- Mutation, fuzz, performance, property, CodeQL, dependency-review, and
  reproducible release/attestation workflows.
- `AuditLogger(privacy_salt=...)` and `AuditLogger.track_exported_path()` so
  operators can make GDPR purges match across process restarts; the default
  per-process salt only covers exports made by the same process.
- `ContextEncoder.encode(..., strict=True)`; unknown situational values now
  raise `ValueError` instead of being dropped (pass `strict=False` for the old
  behaviour).
- Rust live HTTPS transport for online status and CRL revocation checks, with
  rustls hostname verification, public address resolution and pinning, disabled
  redirects, proxies, retries, and decompression, plus bounded headers and bodies.
- Shared Python and Rust online response vectors that bind every decision to the
  requested JTI and issuer.
- Distinct `revocation_unavailable` verification outcomes. They remain
  fail-closed while no longer representing an unconfirmed result as revoked.

### Changed
- `Manifest.from_dict` validates the manifest shape (`vcp_version == "2.0"`,
  UUID `jti`, positive integer `token_count`, supported tokenizer, string
  fields) and `BundleBuilder.with_expires_days` accepts 1 to 90 days only.
- `TokenType.COMPETENCE_ATTESTATION` wire value is now `competence_attestation`
  (Python and TypeScript) and the manifest v2 schema lists it; the schema also
  requires unique `signed_fields` and closed `signers[]` / `stapled_proof`
  objects.
- `ContextEncodeRequest` rejects unknown fields and `DecisionType` is aligned
  across the PDP and enforcement modules.
- `StateTracker` treats EMBODIMENT `🛑` (`emergency_stop`) as an emergency and
  reports personal-state band changes as transitions; the built-in
  `adherence_escalate` and `persona_select` hooks now fire on the events
  `StateTracker` actually emits.
- `RefusalBoundaryPlugin` in `ESCALATE` mode escalates (rather than abstains)
  when no bundle is present; `AdherenceLevelPlugin` requires an integer
  adherence level in 0-5.
- WebMCP `decodeContext` uses vocabulary-based scanning (VS16 preserved, ZWJ
  sequences intact, bare dimension symbols accepted per fixture vep-011);
  `negotiate()` returns `IDENTITY_INVALID` for malformed identity tokens and
  echoes extra boolean core features like the native SDKs; `HookRegistry`,
  `TorchConsumer.receiveTorch`, `computeDecayedIntensity`, and
  `createVCPTools({personas})` validate their inputs.
- WebMCP package renamed from `@vcp/webmcp` to `@creed-space/vcp-sdk` (applied
  in 4.2.0; recorded here because the 4.2.0 entry omitted it).
- Online status responses must echo the requested JTI and issuer. Confirmed
  revocations must include a non-empty reason and a strict RFC 3339 timestamp.
- The Python HTTPS transport now enforces JSON content types, identity encoding,
  and response header limits in parity with Rust.
- Reviewed Rust and release-tooling dependencies are current. The direct
  `base64` 0.23 dependency disables its new `simd-unsafe` default and retains
  only the safe standard-library engine. These updates do not change the SDK's
  public API, wire behavior, package version, or Rust 1.87 minimum.

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
- WebMCP package renamed from `@vcp/webmcp` to `@creed-space/vcp-sdk`; imports
  and the `/polyfill` subpath must be updated.
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
- **TypeScript/WebMCP SDK** (`@vcp/webmcp`, renamed to `@creed-space/vcp-sdk` in 4.2.0) -- Browser-side VCP tool registration via `navigator.modelContext` (Chrome 145+)
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

<!-- No vX.Y.Z tags exist yet; links use the commits that set each version. -->
[Unreleased]: https://github.com/Creed-Space/VCP-SDK/compare/4367ca4...HEAD
[4.2.0]: https://github.com/Creed-Space/VCP-SDK/commit/4367ca4
[4.1.0]: https://github.com/Creed-Space/VCP-SDK/commits/4367ca4/CHANGELOG.md
[4.0.0]: https://github.com/Creed-Space/VCP-SDK/commits/4367ca4/CHANGELOG.md
[3.1.0]: https://github.com/Creed-Space/VCP-SDK/commits/4367ca4/CHANGELOG.md
[1.1.0]: https://github.com/Creed-Space/VCP-SDK/commit/589db58
[1.0.0]: https://github.com/Creed-Space/VCP-SDK/commits/589db58/CHANGELOG.md
