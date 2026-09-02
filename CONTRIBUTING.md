# Contributing to VCP-SDK

Contributions are welcome. Protocol changes start in VCP-Spec; implementation
changes belong here.

## Development setup

Use an isolated environment for each package.

### Python

```bash
cd python
python3 -m venv .venv
. .venv/bin/activate
python -m pip install 'pip==26.2.1'
python -m pip install --require-hashes --requirement requirements-dev.lock
python -m pip install --no-deps --editable .
python -m ruff check src tests
python -m mypy src/vcp
python -m pytest -q
```

Regenerate the development lock only when dependency inputs change:

```bash
python -m pip install 'pip==26.2.1' 'uv==0.12.4'
uv pip compile pyproject.toml \
  --extra dev --extra server --extra mcp \
  --universal \
  --output-file requirements-dev.lock \
  --generate-hashes
```

### Rust

```bash
cd rust
cargo fmt --all -- --check
cargo clippy --workspace --all-targets --all-features -- -D warnings
cargo test --workspace --all-features
RUSTDOCFLAGS='-D warnings' cargo doc --workspace --all-features --no-deps
```

### WebMCP

```bash
cd webmcp
npm ci
npm run check
npm test
npm run prepack
npm pack --dry-run
```

### Repository contracts

```bash
npm ci --ignore-scripts
make validate PYTHON="$(command -v python)"
make schema-sync SPEC=/path/to/VCP-Spec PYTHON="$(command -v python)"
make property PYTHON="$(command -v python)"
make performance-smoke PYTHON="$(command -v python)"
cargo check --locked --manifest-path rust/fuzz/Cargo.toml
```

Property suites use deterministic seeds and committed settings. When a fuzz
target finds a failure, reproduce and minimize the input, add it to the target's
committed corpus, and add a focused regression assertion. Do not raise a
performance envelope merely to make a regression green. Record the measured
candidate, environment, before and after results, and an evidence-based reason
for any envelope change.

## Change requirements

* Add regression tests for changed behavior.
* Update public documentation and compatibility notes with API or wire changes.
* Keep package and protocol version claims separate.
* Never hand-edit generated package output.
* Preserve fail-closed behavior for security-sensitive failures.
* Use Conventional Commits and keep each pull request coherent.
* Run the checks for every affected distribution.

Specification syntax, schema, or semantics changes require the VEP process in
VCP-Spec. Copy an accepted schema here only through the synchronization procedure
in [SCHEMA_OWNERSHIP.md](SCHEMA_OWNERSHIP.md).

## Pull request evidence

Include the candidate hash, exact commands run, test outcomes, package manifest
review, dependency audit result, and any remaining human or publication gates.
Maintainer review and hosted CI remain required before merge.
