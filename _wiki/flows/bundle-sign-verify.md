# Bundle Sign and Verify Flow

<!-- wiki:type = flow -->
<!-- wiki:scope = vcp-sdk -->
<!-- wiki:created = 2026-05-23 -->
<!-- wiki:updated = 2026-09-24 -->
<!-- wiki:status = active -->

## Summary

The central VCP/T (Transport layer) operation is bundle signing at creation time and verification before injection. The orchestrator verifies the bundle cryptographically at the orchestration layer, then injects validated text into the model context. LLMs never receive unverified values. (VCP-SDK/CLAUDE.md, "Core insight")

## Key Principle

"Verify at the orchestration layer, inject complete text to the model." The model itself does not do verification — that happens in `orchestrator.py` before anything reaches the LLM. (VCP-SDK/CLAUDE.md, "What This Is")

## Modules Involved

From `python/src/vcp/` (directory listing):

| Module | Role |
|--------|------|
| `bundle.py` | Bundle creation and parsing — assembles `{manifest, content, signature}` |
| `canonicalize.py` | Canonical serialization — ensures deterministic byte sequence for signing |
| `trust.py` | Trust anchor and chain verification |
| `manifest.py` | Manifest structure — metadata about bundle contents |
| `orchestrator.py` | Entry point for verify-then-inject flow |
| `revocation.py` | Checks revocation status before accepting a bundle (fails closed with `REVOCATION_UNAVAILABLE` when no configured source can establish a status) |
| `audit.py` | Records verification and privacy-filter events with salted identifier hashes (no hash chain; the core-profile chain is implemented in the Creed Space platform, not this SDK) |
| `injection.py` | Formats verified bundles for injection into the model context (the injection scan itself runs in `orchestrator.py`) |

## Flow Steps

1. **Create bundle**: `bundle.py` assembles manifest + content + signature
2. **Canonicalize**: `canonicalize.py` produces deterministic byte sequence
3. **Sign**: private key signs canonical form; signature embedded in bundle
4. **Transport**: bundle travels as MCP resource (`vcp://bundle/*`)
5. **Orchestrator receive**: `orchestrator.py` receives bundle at enforcement boundary
6. **Trust verify**: `trust.py` checks the issuer signature and the safety attestation against the configured trust anchors
7. **Revocation check**: `revocation.py` confirms the bundle is not revoked, between attestation and temporal checks
8. **Temporal, replay, budget and scope checks**: `orchestrator.py` applies them in that order
9. **Injection scan**: `orchestrator.py` scans content for prompt-injection patterns
10. **Audit log**: `audit.py` records the verification event (the application supplies the `AuditLogger`; the orchestrator does not call it)
11. **Inject**: `injection.py` formats the validated text for the model context

## Schemas

Bundle manifest validated against `schemas/vcp-manifest-v1.schema.json`. (VCP-Spec/README.md, "Schemas")

## Provenance

- Sources consulted: VCP-SDK/CLAUDE.md, python/src/vcp/ directory listing, VCP-Spec/README.md; `python/src/vcp/orchestrator.py` (verification steps 1-12), `python/src/vcp/audit.py`, `python/src/vcp/injection.py`
- Last verified against sources: 2026-09-24

## See Also

- [[vcp-sdk:systems/sdk-architecture]] — full module inventory
- [[vcp-spec:systems/itsame-architecture]] — layer 2 (Transport) spec context
- [[shared:vcp]] — VCP cross-project concept
