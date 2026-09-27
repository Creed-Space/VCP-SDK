# VCP-SDK Wiki Log

## [2026-05-23] bootstrap | Initial wiki creation
Pages created: systems/sdk-architecture, flows/bundle-sign-verify
Sources ingested: VCP-SDK/CLAUDE.md, VCP-SDK root listing, python/src/vcp/ directory listing, VCP-Spec/README.md (SDK table)
Note: rust/ and webmcp/ directories exist but were not read in depth — only Python SDK is covered. Rust and TypeScript implementation details are [UNVERIFIED] beyond version numbers from VCP-Spec/README.md.

## [2026-05-23] expand | 4 additional pages covering Python modules, Rust, WebMCP, testing
Pages created: systems/python-sdk-modules, systems/rust-implementation, systems/webmcp-typescript, systems/testing-approach
Sources ingested: python/src/vcp/types.py:1-80; python/src/vcp/bundle.py:1-80; rust/Cargo.toml; rust/vcp-core/src/lib.rs:1-60; rust/ directory listing; webmcp/package.json; webmcp/src/ listing; python/tests/vcp/ listing; conformance/ listing; VCP-SDK/CLAUDE.md
Key finding: There is NO general TypeScript SDK — webmcp/ is specifically navigator.modelContext tool registration. TypeScript use cases are served by vcp-wasm (Rust→WASM) or the Python SDK.
Coverage expanded from 2 → 6 pages.

## [2026-08-14] catchup | Architecture and testing truth reconciliation
Pages updated: systems/sdk-architecture, systems/testing-approach
Sources ingested: current repository inventory; README.md; ARTIFACTS.md;
COMPATIBILITY.md; SCHEMA_OWNERSHIP.md; Makefile; CI, fuzz, mutation, and
performance workflows; Python, Rust, WebMCP, conformance, coverage, artifact,
and ecosystem validators.
Key corrections: removed stale claims that deleted API, MCP, integrations, and
website code remain maintained; documented the archived boundaries, 16-profile
checked conformance model, risk-based coverage, mutation and fuzz programmes,
installed-artifact checks, runtime matrix, and candidate-bound release gates.

## [2026-09-27] update | Canon reconciliation with VCP-Spec
Pages updated: systems/python-sdk-modules, systems/rust-implementation,
systems/webmcp-typescript, systems/sdk-architecture, systems/testing-approach,
flows/bundle-sign-verify
Sources ingested: VCP-Spec canon/2026-09-27-reconcile (VCP/A §2.1 to §2.3,
VCP/I §3.4.1 and §4.2, VCP/S §2.6.1, core audit §3.1 and §6, mcp-bridge §1.2);
python/src/vcp/audit.py, identity/, adaptation/context.py, semantics/csm1.py,
mcp_server.py; rust/vcp-core identity, csm1, situational, personal;
rust/vcp-wasm/src/lib.rs; webmcp/src/identity.ts, extensions/context.ts, tools.ts.
Key changes: 14 baseline dimensions (18 with VEP-0004) and the VCP/A §2.2
vocabularies; unknown values tolerated and unknown dimension groups passed
through; audit default `minimal` with the keyed `hmac-sha256:` hash; five Core
identity prefixes with semantic validation; scope H named Health; MCP revision
caveat for the tools-only MCP server.

## [2026-09-27] update | Canon round 3: pseudonyms and intensity
Pages updated: systems/python-sdk-modules
Sources ingested: /home/claude/vcp/pseudonym_decision.md; VCP-Spec bc743e6
(VCP/A §2.3 personal-only form and one-digit intensity); python/src/vcp/identity/registry.py.
Key changes: pseudonymous identities under user.anon-<hex> and user.pseudo-<hex>;
the registry rejects unlisted prefixes; intensity is exactly one digit 1-5.

## [2026-09-27] update | Canon round 4: review fixes
Pages updated: systems/webmcp-typescript, systems/testing-approach
Sources ingested: /home/claude/vcp/subsignal_decision.md; VCP-Spec 05c3a98
(VCP/A §2.3 repeated dimensions, mixed groups, sub-signals).
Key changes: vcp_chat default constitution work.professional.assistant; context
strings carry no sub-signal (the Rust R-line form is value:intensity:extended);
repeated dimensions are malformed; conformance inventory 250 vectors.
