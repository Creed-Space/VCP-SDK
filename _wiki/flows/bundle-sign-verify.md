# Bundle Sign and Verify Flow

<!-- wiki:type = flow -->
<!-- wiki:scope = vcp-sdk -->
<!-- wiki:created = 2026-05-23 -->
<!-- wiki:updated = 2026-05-23 -->
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
| `revocation.py` | Checks revocation status before accepting a bundle |
| `audit.py` | Appends to tamper-evident audit chain on each operation |
| `injection.py` | Injection scanning — checks for injection attacks in bundle content |

## Flow Steps

1. **Create bundle**: `bundle.py` assembles manifest + content + signature
2. **Canonicalize**: `canonicalize.py` produces deterministic byte sequence
3. **Sign**: private key signs canonical form; signature embedded in bundle
4. **Transport**: bundle travels as MCP resource (`vcp://bundle/*`)
5. **Orchestrator receive**: `orchestrator.py` receives bundle at enforcement boundary
6. **Revocation check**: `revocation.py` verifies token not revoked
7. **Trust verify**: `trust.py` checks signature against trust anchor chain
8. **Injection scan**: `injection.py` scans content for injection attacks
9. **Audit log**: `audit.py` records operation on tamper-evident chain
10. **Inject**: validated text injected into model context

## Schemas

Bundle manifest validated against `schemas/vcp-manifest-v1.schema.json`. (VCP-Spec/README.md, "Schemas")

## Provenance

- Sources consulted: VCP-SDK/CLAUDE.md, python/src/vcp/ directory listing, VCP-Spec/README.md
- Last verified against sources: 2026-05-23

## See Also

- [[vcp-sdk:systems/sdk-architecture]] — full module inventory
- [[vcp-spec:systems/itsame-architecture]] — layer 2 (Transport) spec context
- [[shared:vcp]] — VCP cross-project concept
