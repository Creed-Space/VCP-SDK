# VCP-SDK Documentation Index

<!-- vcp-document-control
status: Current SDK index
normative-authority: Implementation documentation only, VCP-Spec controls protocol semantics
protocol-version: VCP 3.1 baseline with selected candidate support
last-reviewed: 2026-08-13
owner: VCP-SDK maintainers
evidence-boundary: Navigation and implementation classification only
-->

## Start here

1. [Implementation guide](./VCP_IMPLEMENTATION_GUIDE.md)
2. [Root overview and source install](../README.md)
3. [Compatibility policy](../COMPATIBILITY.md)
4. [Artifact and publication status](../ARTIFACTS.md)
5. [Conformance corpus](../conformance/README.md)
6. [Coordinated release runbook](../release/COORDINATED_RELEASE_RUNBOOK.md)
7. [Generated cross-language feature matrix](./FEATURE_MATRIX.md)
8. [Runtime cancellation, cache, key custody, and observability contracts](./RUNTIME_CONTRACTS.md)

VCP-Spec is the canonical protocol and governance authority. SDK documentation
describes code in this repository and never promotes a draft VEP or candidate
schema into the protocol baseline.

## Package documentation

| Surface | Documentation | Scope |
|:---|:---|:---|
| Python | [`python/README.md`](../python/README.md) | Reference package, optional extras, MCP entry point |
| Rust | [`rust/vcp-core`](../rust/vcp-core/) | Core library, examples, tests, and benches |
| CLI | [`rust/vcp-cli`](../rust/vcp-cli/) | Command-line interface |
| WASM | [`rust/vcp-wasm`](../rust/vcp-wasm/) | Browser-targeted Rust bindings |
| WebMCP | [`webmcp/README.md`](../webmcp/README.md) | Experimental browser tool-registration subset |

All artifacts are source-only candidates until the machine publication-state
record and an authorized registry receipt say otherwise.

## Protocol companions

The `docs/adaptation`, `docs/content`, `docs/context`, `docs/identity`,
`docs/semantics`, and `docs/uvc` directories are implementation companions
carried for developer convenience. Their corresponding accepted VCP-Spec
documents and synchronized schemas control conflicts.

## Archives

- [`archives/host_integrations`](../archives/host_integrations/) contains former
  host adapters, paths, rollout records, and test counts.
- [`archives/adjacent_projects`](../archives/adjacent_projects/) contains Torch,
  Interiora, MillOS, Rewind, and abbreviation-conflicting project records.
- [`archives/vcp_specs_pre_v2.0_2026-03`](../archives/vcp_specs_pre_v2.0_2026-03/)
  preserves superseded protocol lineage.

Archived material has no current package, compatibility, conformance, or
deployment authority.
