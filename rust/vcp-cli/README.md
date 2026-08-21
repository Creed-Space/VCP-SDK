# vcp-cli

`vcp-cli` exposes the project-maintained VCP Rust implementation as a command-line tool
for parsing, canonicalization, hashing, verification, conformance fixtures,
and selected extension operations.

**Publication state:** source-only candidate, version 4.2.0. No crates.io
availability is claimed.

## Build and inspect

```bash
cargo build --manifest-path rust/Cargo.toml -p vcp-cli
cargo run --manifest-path rust/Cargo.toml -p vcp-cli -- --help
cargo run --manifest-path rust/Cargo.toml -p vcp-cli -- \
  parse-token family.safe.guide@1.2.0
cargo run --manifest-path rust/Cargo.toml -p vcp-cli -- \
  parse-uri creed://creed.space/family.safe.guide@1.2.0
```

The CLI writes successful command results to standard output and diagnostics
to standard error. A successful command exits `0`; invalid input, failed
verification, or an I/O error exits `1`; argument parsing follows clap and
exits `2`. Commands never overwrite input files.

The automation contract and complete generated help snapshot are validated by
the workspace tests. Machine consumers should prefer commands whose documented
output is JSON. Human-oriented parse commands may include explanatory lines in
addition to JSON until a future, semver-reviewed uniform output mode is added.

## Security and compatibility

The CLI is a thin interface to `vcp-core`. It does not provide production key
custody, trust-anchor provisioning, or durable replay storage. See
[security policy](https://github.com/Creed-Space/VCP-SDK/blob/main/SECURITY.md) and
[compatibility policy](https://github.com/Creed-Space/VCP-SDK/blob/main/COMPATIBILITY.md).

## Licence

MIT. See [repository licence](https://github.com/Creed-Space/VCP-SDK/blob/main/LICENSE).
