# vcp-wasm

`vcp-wasm` provides browser-targeted WebAssembly bindings for selected
`vcp-core` parsing and encoding operations used by the VCP Demo.

**Publication state:** published, version 4.2.0 on crates.io as `vcp-wasm`.
The generated WebAssembly package is not published to npm.

## Build from source

```bash
rustup target add wasm32-unknown-unknown
cargo build --manifest-path rust/Cargo.toml \
  -p vcp-wasm --target wasm32-unknown-unknown
```

The crate targets `wasm32-unknown-unknown` and uses `wasm-bindgen`. It is an
integration surface rather than a complete protocol implementation. Native
network revocation and application-owned security controls remain outside this
package.

Browser compatibility is bounded by the tested candidate in
[compatibility policy](https://github.com/Creed-Space/VCP-SDK/blob/main/COMPATIBILITY.md). Real browser behavior must
be tested against packaged bytes; a native Rust test does not establish browser
or Content Security Policy compatibility.

## Security

Treat input as untrusted, bound payload sizes before crossing the JavaScript to
WebAssembly boundary, and avoid placing private context or key material in
browser-visible memory. Report suspected vulnerabilities through
[security policy](https://github.com/Creed-Space/VCP-SDK/blob/main/SECURITY.md).

## Licence

MIT. See [repository licence](https://github.com/Creed-Space/VCP-SDK/blob/main/LICENSE).
