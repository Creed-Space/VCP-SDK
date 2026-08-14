# VCP-SDK Implementation Guide

<!-- vcp-document-control
status: Current implementation companion
normative-authority: VCP-Spec controls protocol semantics
protocol-version: VCP 3.1 baseline with explicit candidate and experimental surfaces
last-reviewed: 2026-08-13
owner: VCP-SDK maintainers
evidence-boundary: Source implementation guidance, not publication or deployment proof
-->

## Source boundary

VCP-SDK contains portable Python, Rust, CLI, WASM, and WebMCP source candidates.
It excludes the former Creed Space host application and cross-project Interiora
bridges. Select an exact Spec and SDK commit pair before using schemas or making
a conformance claim.

## Source installation

From an immutable SDK checkout:

```bash
python -m pip install ./python
npm --prefix webmcp ci
npm --prefix webmcp run build
cargo build --manifest-path rust/Cargo.toml --workspace
```

Registry commands remain invalid until names are ratified and publication
receipts are recorded in `release/publication-state.json`.

## Trust pipeline

Treat every token, manifest, bundle, context value, and metadata object as
untrusted. A safe integration applies bounded parsing, schema selection,
canonicalization, integrity checks, trust-anchor policy, signature checks,
temporal claims, replay defense, audience and scope checks, region policy,
revocation, privacy projection, and host authorization before model or tool use.

Required security-service unavailability produces a fail-closed decision. The
caller may distinguish transient unavailability from confirmed invalidity using
stable result codes, while neither condition reaches the governed action.

## Implementation surfaces

| Surface | Location | Claim boundary |
|:---|:---|:---|
| Python | `python/src/vcp` | Reference implementation, optional server and MCP extras |
| Rust | `rust/vcp-core` | Core parsing, verification, orchestration, context, and extension support |
| CLI | `rust/vcp-cli` | Selected file and token operations |
| WASM | `rust/vcp-wasm` | Supported exports under the documented browser target |
| WebMCP | `webmcp` | Browser-facing subset using `document.modelContext`; not the full protocol |
| Conformance | `conformance` | Only suites marked checked in the generated coverage report |

## WebMCP lifecycle

`registerVCPTools` detects `document.modelContext` first. An isolated deprecated
Navigator fallback exists for older hosts. Registration is asynchronous, partial
failures are reported by name, and one caller-owned cleanup function aborts every
accepted registration through its shared AbortSignal. Server-side rendering and
absent APIs return an explicit unavailable result.

## Verification

Use `make validate` for repository contracts and the language-specific commands
documented in the root Makefile. Package tests run again against built wheel,
sdist, crate, CLI, WASM, and npm tarball candidates before release. A source-tree
pass does not establish installed-artifact behavior.

Machine-readable conformance output reports `passed`, `failed`, `unsupported`,
and `not_applicable`. Fixture presence and total test counts are excluded from
conformance claims.

## Host responsibilities

The host owns consent, purpose limitation, trust-anchor configuration, network
policy, provider credentials, spending controls, model and tool injection,
logging, retention, monitoring, incident response, and rollback. Those controls
need deployment evidence in the host repository.
