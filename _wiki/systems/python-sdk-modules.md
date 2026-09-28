# Python SDK Module Reference

<!-- wiki:type = system -->
<!-- wiki:scope = vcp-sdk -->
<!-- wiki:created = 2026-05-23 -->
<!-- wiki:updated = 2026-09-24 -->
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
| `audit.py` | Core Security (used by VCP/T verification) | Privacy-hashed audit logger (verification and privacy-filter events; export and purge; no hash chain) |
| `messaging.py` | Messaging (L5) | VCP/M inter-agent messaging |
| `metrics.py` | All | Metrics and telemetry |
| `skill_security.py` | All | Skill-level security checks |

(python/src/vcp/ directory listing; VCP-SDK/CLAUDE.md)

## Subdirectory Modules

| Directory | Layer | Contents |
|-----------|-------|----------|
| `identity/` | Identity (L1) | UVC token parsing, namespace resolution, registry encoding |
| `semantics/` | Semantics (L3) | CSM1 grammar, persona composition, trait encoding |
| `adaptation/` | Adaptation (L4) | Context encoding, state tracking |
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

## Rust Counterpart Modules

The Rust `vcp-core` crate (rust/vcp-core/src/) mirrors the Python modules: `identity`, `csm1`, `context`, `transport`, `trust`, `hooks`, `revocation`, `orchestrator`, `composer`, `personal`, `situational`. (rust/vcp-core/src/lib.rs:1–60)

## Provenance

- Sources consulted: `python/src/vcp/` directory listing; `python/src/vcp/types.py:1–80`; `python/src/vcp/bundle.py:1–80`; `VCP-SDK/CLAUDE.md`; `rust/vcp-core/src/lib.rs:1–60`
- Last verified against sources: 2026-05-23; layer coverage, module roles, `VerificationResult` categories and the install command rechecked 2026-09-24 against `types.py`, `injection.py`, `audit.py`, `negotiation.py` and `release/publication-state.json`

## See Also

- [[vcp-sdk:systems/sdk-architecture]] — overall repository structure
- [[vcp-sdk:systems/rust-implementation]] — Rust crate details
- [[vcp-sdk:flows/bundle-sign-verify]] — how these modules chain together
- [[vcp-sdk:systems/webmcp-typescript]] — browser-side bindings
