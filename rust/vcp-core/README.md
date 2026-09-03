# vcp-core

`vcp-core` is the Rust reference library for Value Context Protocol identity,
CSM-1, context, transport, trust, revocation, orchestration, and selected
extension behavior.

**Publication state:** published, version 4.2.0 on crates.io
(`cargo add vcp-core@4.2.0`). The canonical publication record carries the
registry receipt.

## Use from this workspace

```toml
[dependencies]
vcp-core = { path = "../VCP-SDK/rust/vcp-core" }
```

```rust
use vcp_core::{Csm1Code, VcpToken};

let identity = VcpToken::parse("family.safe.guide@1.2.0")?;
let profile = Csm1Code::parse("N5+F+E")?;
assert_eq!(identity.domain(), "family");
assert_eq!(profile.encode(), "N5+E+F");
# Ok::<(), vcp_core::VcpError>(())
```

## Compatibility and features

The minimum supported Rust version is 1.87. The crate has no optional feature
flags in this candidate. Native builds include the bounded HTTPS revocation
transport. `wasm32-unknown-unknown` consumers should use the sibling
`vcp-wasm` crate for the supported browser-facing surface.

Protocol compatibility and implementation coverage are recorded in
[compatibility policy](https://github.com/Creed-Space/VCP-SDK/blob/main/COMPATIBILITY.md) and
[conformance coverage manifest](https://github.com/Creed-Space/VCP-SDK/blob/main/conformance/coverage-manifest.json).
The VCP-Spec repository controls protocol semantics.

## Security

Verification is relative to caller-provided trust anchors and policy. Network
policy, durable replay state, key custody, audit retention, and deployment
monitoring remain application responsibilities. Report suspected
vulnerabilities using the private route in
[security policy](https://github.com/Creed-Space/VCP-SDK/blob/main/SECURITY.md).

## Licence

MIT. See [repository licence](https://github.com/Creed-Space/VCP-SDK/blob/main/LICENSE).
