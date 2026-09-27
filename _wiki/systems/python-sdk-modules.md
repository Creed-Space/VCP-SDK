# Python SDK Module Reference

<!-- wiki:type = system -->
<!-- wiki:scope = vcp-sdk -->
<!-- wiki:created = 2026-05-23 -->
<!-- wiki:updated = 2026-09-27 -->
<!-- wiki:status = active -->

## Summary

The Python SDK (`python/src/vcp/`) is the reference implementation of VCP. It covers five of the six protocol layers (VCP/I, T, S and A, plus VCP/M through `messaging.py`); there is no VCP/E implementation. It provides types, signing, verification, enforcement, and inter-agent messaging. Pydantic models throughout; async for API/MCP entry points. (VCP-SDK/CLAUDE.md "Code Patterns"; python/src/vcp/ directory listing)

## Core Modules

| Module | Layer | Role |
|--------|-------|------|
| `types.py` | All | Core enums and dataclasses: `VerificationResult`, `CompositionMode`, `AttestationType`, `TokenType`, `Manifest`, `Budget`, `Scope`, etc. |
| `bundle.py` | Transport (L2) | Bundle creation, parsing, manifest construction |
| `canonicalize.py` | Transport (L2) | Canonical serialization for signing (deterministic JSON) |
| `trust.py` | Transport (L2) | Trust anchor and chain verification |
| `manifest.py` | Transport (L2) | Bundle manifest handling |
| `orchestrator.py` | All | Orchestrator: verify-then-inject pipeline, including the prompt-injection scan |
| `enforcement.py` | Semantics (L3) | Policy enforcement against constitution |
| `negotiation.py` | Core (capability negotiation) | Capability negotiation between agents |
| `injection.py` | Transport (L2) | Formats verified bundles for LLM injection |
| `privacy.py` | Core Security | Context opacity and privacy controls |
| `revocation.py` | Core Security (used by VCP/T verification) | Revocation infrastructure with SSRF protection |
| `audit.py` | Core Security (used by VCP/T verification) | Audit logger (verification and privacy-filter events; export and purge; no hash chain). Default level `minimal`; identifiers pseudonymized with the keyed `hmac-sha256:` hash of core audit §6 |
| `messaging.py` | Messaging (L5) | VCP/M inter-agent messaging |
| `metrics.py` | All | Metrics and telemetry |
| `skill_security.py` | All | Skill-level security checks |

(python/src/vcp/ directory listing; VCP-SDK/CLAUDE.md)

## Subdirectory Modules

| Directory | Layer | Contents |
|-----------|-------|----------|
| `identity/` | Identity (L1) | UVC token parsing (`Token.parse`, syntax only), semantic validation (`Token.validate`: listed prefix, three-segment Core tokens, no reserved words), namespace tiers, registry |
| `semantics/` | Semantics (L3) | CSM-1 grammar (scope H is `Scope.HEALTH`, with `HEALTHCARE` as a deprecated alias), persona composition, trait encoding |
| `adaptation/` | Adaptation (L4) | Context encoding over 14 baseline dimensions (9 situational + 5 personal in v3.1, 18 with the experimental VEP-0004 dimensions), VCP/A §2.2 vocabularies, tolerant decoding with `validate_context_wire` for strict checks, state tracking and the emergency indicator set |
| `extensions/` | VCP-X-* | Extension modules |
| `hooks/` | All | Lifecycle hooks for the adaptation pipeline |

(python/src/vcp/ directory listing)

## Key Types (`types.py`)

### VerificationResult Enum

18 result codes (0-17) in five categories (types.py:11-59):

| Category | Codes |
|----------|-------|
| success | `VALID` |
| security | `INVALID_SIGNATURE`, `INVALID_ATTESTATION`, `HASH_MISMATCH`, `FUTURE_TIMESTAMP`, `REPLAY_DETECTED`, `TOKEN_MISMATCH`, `SIZE_EXCEEDED`, `REVOKED` |
| temporal | `NOT_YET_VALID`, `EXPIRED` |
| transient | `FETCH_FAILED`, `REVOCATION_UNAVAILABLE` |
| configuration | `INVALID_SCHEMA`, `UNTRUSTED_ISSUER`, `UNTRUSTED_AUDITOR`, `BUDGET_EXCEEDED`, `SCOPE_MISMATCH` |

### CompositionMode Enum

Four modes for multi-constitution scenarios (types.py:62-68):
- `BASE` — foundational layer
- `EXTEND` — additive to base
- `OVERRIDE` — replaces conflicting clauses
- `STRICT` — no additional constraints allowed

### Manifest Dataclass (`bundle.py`)

Core manifest fields (bundle.py:30–44):
- `vcp_version`, `bundle` (BundleInfo), `issuer`, `timestamps`, `budget`, `safety_attestation`, `signature`
- Optional: `scope`, `composition`, `revocation`, `metadata`
- Serialized via `to_dict()` to canonical dict for signing

## Entry Points

```bash
python -m pip install value-context-protocol==4.2.0    # install
pytest tests/            # all tests
pytest tests/vcp/identity/   # by layer
pytest --cov=src/vcp tests/  # with coverage
```
(VCP-SDK/CLAUDE.md "Testing")

## Protocol alignment (27 September 2026)

The unreleased tree follows the VCP-Spec canon reconciliation of 27 September 2026 (see `CHANGELOG.md` [Unreleased] and the migration note in `COMPATIBILITY.md`):

- **Audit**: `AuditLogger` defaults to `AuditLevel.MINIMAL` (audit level, verification result, bundle ID hash and content hash only). Identifiers use `hmac-sha256:` plus 32 hex characters of HMAC-SHA256 under `K_audit`: the operator key passed as `audit_key` (at least 32 bytes), otherwise a per-process random key. `log_callback`, the return value and `get_entries()` carry only the fields permitted at the entry's level.
- **Identity**: core prefixes are `family`, `work`, `secure`, `creative` and `reality`; organizational `company`, `school`, `ngo`; community `religion`, `culture`, `community`; personal `user`. `Token.parse` accepts any syntactically valid token; `Token.validate` and the MCP `vcp_validate_token` tool reject unlisted prefixes (VCP/I §3.4.1).
- **Adaptation**: every situational vocabulary and the personal-state categories equal the VCP/A §2.2 and §3.1 tables and the synchronized schema enums. Decoders keep unknown values raw and pass unknown dimension groups through; malformed strings are rejected.
- **Semantics**: scope H is named Health.

## MCP server and MCP revisions

`vcp-mcp-server` (`mcp_server.py`, `[mcp]` extra, `mcp>=2`) is a tools-only server: `vcp_validate_token`, `vcp_parse_csm1`, `vcp_encode_context` and `vcp_status`. It does not implement the VCP/MCP bridge of VCP-Spec `specs/core/mcp-bridge.md`. That bridge targets MCP revisions up to and including 2025-11-25 and relies on the `initialize` handshake and Sampling. MCP 2026-07-28 removed `initialize`, deprecated Sampling and replaced server-initiated elicitation with Multi Round-Trip Requests; VEP-0005 (Draft, v3.3 candidate) is the adaptation path.

## Rust Counterpart Modules

The Rust `vcp-core` crate (rust/vcp-core/src/) mirrors the Python modules: `identity`, `csm1`, `context`, `transport`, `trust`, `hooks`, `revocation`, `orchestrator`, `composer`, `personal`, `situational`. (rust/vcp-core/src/lib.rs:1–60)

## Provenance

- Sources consulted: `python/src/vcp/` directory listing; `python/src/vcp/types.py:1–80`; `python/src/vcp/bundle.py:1–80`; `VCP-SDK/CLAUDE.md`; `rust/vcp-core/src/lib.rs:1–60`
- Last verified against sources: 2026-05-23; layer coverage, module roles, `VerificationResult` categories and the install command rechecked 2026-09-24 against `types.py`, `injection.py`, `audit.py`, `negotiation.py` and `release/publication-state.json`; audit, identity, adaptation, semantics and MCP rows rechecked 2026-09-27 against `audit.py`, `identity/`, `adaptation/context.py`, `semantics/csm1.py`, `mcp_server.py` and VCP-Spec `specs/core/mcp-bridge.md` §1.2

## See Also

- [[vcp-sdk:systems/sdk-architecture]] — overall repository structure
- [[vcp-sdk:systems/rust-implementation]] — Rust crate details
- [[vcp-sdk:flows/bundle-sign-verify]] — how these modules chain together
- [[vcp-sdk:systems/webmcp-typescript]] — browser-side bindings
