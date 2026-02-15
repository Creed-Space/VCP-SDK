# VCP SDK Examples

Runnable examples demonstrating the VCP SDK across Python and Rust.

## Python

```bash
# Install the SDK in editable mode
cd python && pip install -e .

# Run individual examples
python ../examples/python/01_parse_token.py
python ../examples/python/02_verify_bundle.py
python ../examples/python/03_compose.py
python ../examples/python/04_context_encoding.py
python ../examples/python/05_full_pipeline.py
```

| Example | Demonstrates |
|---------|-------------|
| `01_parse_token.py` | VCP/I token parsing, properties, pattern matching |
| `02_verify_bundle.py` | Bundle creation, trust config, orchestrator verification |
| `03_compose.py` | Composing multiple constitutions with conflict detection |
| `04_context_encoding.py` | VCP/A Enneagram context encoding and decoding |
| `05_full_pipeline.py` | End-to-end: parse, verify, and inject into model context |

## Rust

```bash
# Build and run from the vcp-core crate
cd rust/vcp-core

cargo run --example parse_token
cargo run --example verify_bundle
cargo run --example sign_and_verify
```

| Example | Demonstrates |
|---------|-------------|
| `parse_token.rs` | VCP/I token parsing and component access |
| `verify_bundle.rs` | Content hashing and hash verification |
| `sign_and_verify.rs` | Ed25519 manifest signing and verification |

**Note:** Rust examples require `ed25519-dalek` and `rand` dependencies (already included in `vcp-core`).
