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
