# Generated VCP SDK feature matrix

<!-- vcp-document-control
status: Generated current candidate summary
normative-authority: Implementation evidence only
protocol-version: VCP 3.1 baseline with candidate extensions identified per row
last-reviewed: 2026-08-15
owner: VCP-SDK maintainers
evidence-boundary: Same-programme runner coverage, not independent interoperability or certification
-->

This file is generated from `conformance/coverage-manifest.json`. Run
`python3 scripts/generate_feature_matrix.py` to update it.

**Claim boundary:** Statuses summarize same-programme candidate runners. They do not establish independent interoperability, certification, publication, or deployment support.

| Feature suite | Version | Maturity | Cases | Python | Rust | WebMCP |
|:---|:---|:---|---:|:---|:---|:---|
| adaptation/context_encoding | 3.2.0 | conformance-candidate | 9 | full | full | full |
| adaptation/context_encoding_extended | 3.2.0 | conformance-candidate | 12 | full | full | full |
| adaptation/messaging | 2.0.0 | conformance-candidate | 41 | full | unsupported | not_applicable |
| adaptation/state_machine | 1.0.0 | conformance-candidate | 14 | full | unsupported | not_applicable |
| extensions/capability_negotiation | 2.0.0 | conformance-candidate | 16 | full | full | full |
| extensions/competence | 1.0.0 | conformance-candidate | 5 | full | unsupported | not_applicable |
| extensions/consensus_voting | 1.0.0 | conformance-candidate | 8 | full | full | not_applicable |
| extensions/personal_state | 1.0.0 | conformance-candidate | 16 | full | full | full |
| extensions/relational_context | 1.0.0 | conformance-candidate | 17 | full | full | full |
| extensions/stateless_mcp | 0.1.0-draft | draft | 3 | unsupported | unsupported | unsupported |
| extensions/torch_handoff | 1.0.0 | conformance-candidate | 7 | full | full | not_applicable |
| extensions/welfare | 0.1.0-draft | draft | 3 | unsupported | unsupported | unsupported |
| identity/token_canonicalization | 1.0.0 | conformance-candidate | 10 | full | full | not_applicable |
| identity/token_parsing | 1.0.0 | conformance-candidate | 33 | full | full | not_applicable |
| interop/complete_bundle | 1.0.0 | conformance-candidate | 2 | full | full | not_applicable |
| interop/cross_impl_roundtrip | 1.0.0 | conformance-candidate | 5 | full | full | not_applicable |
| security/revocation-crl-responses | 1.0.0 | conformance-candidate | 10 | full | full | not_applicable |
| security/revocation-responses | 1.0.0 | conformance-candidate | 8 | full | full | not_applicable |
| semantics/composition | 1.0.0 | conformance-candidate | 10 | full | full | not_applicable |
| semantics/csm1_encoding | 1.0.0 | conformance-candidate | 10 | full | full | not_applicable |
| semantics/csm1_parsing | 1.0.0 | conformance-candidate | 29 | full | full | not_applicable |
| semantics/persona_resolution | 1.0.0 | conformance-candidate | 18 | full | full | not_applicable |
| transport/bundle_verification | 1.0.0 | conformance-candidate | 8 | full | full | not_applicable |
| transport/content_canonicalization | 1.0.0 | conformance-candidate | 18 | full | full | not_applicable |
| transport/content_hashing | 1.0.0 | conformance-candidate | 13 | full | full | not_applicable |
| transport/manifest_canonicalization | 1.0.0 | conformance-candidate | 8 | full | full | not_applicable |
| transport/signature_verification | 1.0.0 | conformance-candidate | 9 | full | full | not_applicable |

`full` means every applicable case in the declared local runner is checked.
`partial` means some applicable cases are checked. `not_applicable` means
the fixture does not exercise that package surface. These labels never infer
feature parity merely from the presence of a package.
