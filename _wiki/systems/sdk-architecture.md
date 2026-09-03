# VCP SDK Architecture

<!-- wiki:type = system -->
<!-- wiki:scope = vcp-sdk -->
<!-- wiki:created = 2026-05-23 -->
<!-- wiki:updated = 2026-08-14 -->
<!-- wiki:status = active -->

## Summary

VCP-SDK is the implementation repository for the Value Context Protocol. It
contains a full Python reference package, a Rust workspace for native, CLI, and
WASM use, a focused TypeScript WebMCP package, synchronized schema copies, and a
language-neutral conformance corpus. Normative protocol text belongs in
VCP-Spec; the maintained interactive application belongs in VCP-Demo-Site.

## Maintained repository surfaces

| Path | Responsibility |
|:---|:---|
| `python/src/vcp/` | Reference protocol models, canonicalization, verification, trust, revocation, orchestration, hooks, privacy, messaging, MCP server, and extensions |
| `rust/vcp-core/` | Native core types, parsing, transport, orchestration, revocation, negotiation, and extension behavior |
| `rust/vcp-cli/` | Command-line parsing, signing, verification, and conformance adapters |
| `rust/vcp-wasm/` | Browser-compatible WASM bindings over `vcp-core` |
| `webmcp/` | TypeScript WebMCP tools, explicit registration lifecycle, hooks, polyfill loading boundary, and supported extensions |
| `schemas/` | SDK-owned schemas and reviewed copies synchronized from VCP-Spec |
| `conformance/` | Authored fixtures, 16 profile runners, coverage classification, and aggregate reports |
| `examples/` | Executable integration examples and deployment configuration samples |
| `scripts/` | Repository, schema, ecosystem, package, performance, coverage, and release-evidence validators |
| `archives/` | Retired adjacent projects and host-specific integrations preserved with archive metadata |
| `website/` | Archive notice for the retired partial website copy |

The deleted `python/src/api/`, legacy `python/src/mcp/`, root `integrations/`, and
partial website implementation are not maintained SDK entry points. Their useful
history is preserved under `archives/`; production code must not import it.

## Distribution boundaries

The three candidate distribution families all use SDK version 4.2.0, while the
published protocol baseline remains VCP v3.1. Selected v3.2 amendments and
experimental VEP behavior are labelled separately and require negotiation or
governance approval.

* Python distribution: `value-context-protocol`, imported as `vcp`.
* Rust distributions: `vcp-core`, `vcp-cli`, and `vcp-wasm`.
* npm distribution: `@creedspace/vcp-sdk`, a WebMCP subset rather than a full
  general TypeScript implementation.

No public registry publication is currently claimed. Source metadata and local
package builds are candidate evidence only.

## Trust boundaries

The SDK performs canonicalization, signature and hash verification, temporal
validation, revocation checks, replay-policy integration, scope enforcement,
hook enforcement, and fail-closed orchestration. Integrators still own trusted
key provisioning, durable replay storage, outbound network policy, audit
retention, service monitoring, and authorization decisions.

Online revocation clients validate destinations before connection, reject
non-global resolution sets, pin validated addresses while retaining TLS hostname
verification, disable redirects and transparent decompression, bound response
sizes, bind responses to the requested issuer and JTI, and distinguish confirmed
revocation from dependency unavailability.

## Schema and protocol ownership

VCP-Spec owns normative protocol schemas. `SCHEMA_OWNERSHIP.md` records which
copies are synchronized, which SDK schemas are implementation-specific, and the
intentional VCP/M version split. `scripts/check_schema_sync.py` compares an exact
Spec and SDK checkout; `scripts/validate_public_contract.py` checks public names,
versions, exports, protocol labels, and Demo guidance across all three projects.

## Release architecture

Release evidence is candidate-bound. Build, test, audit, conformance, package,
human review, rights review, governance approval, and publication authorization
remain separate gates. The repository's release ledger template records those
decisions without pretending that source authorship confers registry authority.

## Provenance

Sources verified on 2026-08-14: `README.md`; `ARTIFACTS.md`;
`COMPATIBILITY.md`; `SCHEMA_OWNERSHIP.md`; `RELEASE_CHECKLIST.md`; root directory
inventory; `python/src/vcp/`; `rust/Cargo.toml`; `webmcp/package.json`;
`conformance/coverage-manifest.json`.

## See Also

* [[vcp-sdk:systems/testing-approach]]
* [[vcp-sdk:systems/python-sdk-modules]]
* [[vcp-sdk:systems/rust-implementation]]
* [[vcp-sdk:systems/webmcp-typescript]]
* [[vcp-sdk:flows/bundle-sign-verify]]
