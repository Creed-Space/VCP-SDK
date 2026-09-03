# Value Context Protocol SDK

Project-maintained implementations and integration libraries for the Value Context
Protocol (VCP).

[![CI](https://github.com/Creed-Space/VCP-SDK/actions/workflows/ci.yml/badge.svg)](https://github.com/Creed-Space/VCP-SDK/actions/workflows/ci.yml)

> **Publication state:** source-only candidate. No PyPI, npm, or crates.io
> release is currently claimed. Candidate names and versions below describe
> repository metadata. See
> [`release/publication-state.json`](release/publication-state.json) for the
> machine-readable gate.

| Candidate distribution | Version | Publication state | Scope |
|:---|:---|:---|:---|
| Python, `value-context-protocol` | 4.2.0 | Source-only | Full project-maintained implementation, complete local Agent Runtime reference, orchestration, hooks, privacy, messaging, and extensions |
| Rust workspace, including `vcp-core` | 4.2.0 | Source-only | Core parsing, transport, orchestration, CLI, and WASM bindings |
| npm, `@creedspace/vcp-sdk` | 4.2.0 | Source-only | Browser and WebMCP integration library |

Package versions use SDK semantic versioning. The published protocol baseline is
VCP v3.1. The repository also implements selected v3.2 candidate amendments and
experimental VEP-0004 behavior. See [COMPATIBILITY.md](COMPATIBILITY.md) before
claiming protocol conformance.

## Repository map

| Path | Purpose |
|:---|:---|
| [`python/`](python/) | Python package and tests |
| [`rust/`](rust/) | Cargo workspace with core, CLI, and WASM crates |
| [`webmcp/`](webmcp/) | TypeScript WebMCP package |
| [`schemas/`](schemas/) | SDK-owned and synchronized JSON Schema copies |
| [`conformance/`](conformance/) | Language-neutral fixtures across protocol layers and extensions |
| [`examples/`](examples/) | Runnable Python examples and deployment configuration |
| [`docs/`](docs/) | Implementation and integration guidance |
| [`website/`](website/) | Archive notice for the retired partial website copy |

The maintained interactive demonstration lives in the separate
[VCP-Demo-Site](https://github.com/Creed-Space/VCP-Demo-Site) repository. The
normative protocol source lives in
[VCP-Spec](https://github.com/Creed-Space/VCP-Spec).

## Agent Runtime Profile candidate

The Python source candidate implements the complete local `observe@0.1.0`, `controlled@0.1.0`, and `accretive@0.1.0` loop. One bounded SituationView leads through contextual Affordances, proof planning, exact preflight, host-owned decision and single-use grant, controlled reversible execution, reconciliation, RunProof, candidate-first accretion, promotion, attributable influence, and revocation.

```python
from vcp.agent import AgentRuntime

async with AgentRuntime.connect(profile="controlled@0.1.0") as runtime:
    situation = (await runtime.bootstrap("Set one local setting and prove it")).require_value()
    options = (await situation.find_affordances(
        effect_ceiling="reversible_write"
    )).require_value()
```

Local mode opens no network and performs only deterministic in-memory reference effects. Policy, grants, review, dispatch, and durable memory remain host authorities. Rust and TypeScript provide strict portable contract facades and no-network orientation. The 24-case Agent Experience harness currently reports zero failures and zero unsupported cases in the local reference scope. The candidate remains unratified, unpublished, undeployed, and independently unreviewed. See [the Agent Runtime guide](docs/VCP_AGENT_RUNTIME_GUIDE.md).

## Python

Python 3.10 or newer is required.

```bash
cd python
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest -q
python -m ruff check src tests
python -m mypy src/vcp
```

The candidate distribution name is `value-context-protocol`; imports use `vcp`:

```python
from vcp.identity import Token
from vcp.semantics.csm1 import CSM1Code

token = Token.parse("family.safe.guide@1.2.0")
code = CSM1Code.parse("N5+F+E")
assert token.canonical == "family.safe.guide"
assert code.encode() == "N5+E+F"
```

For signed-bundle construction and fail-closed verification, run
[`examples/python/02_verify_bundle.py`](examples/python/02_verify_bundle.py).

## Rust

```bash
cd rust
cargo fmt --all -- --check
cargo clippy --workspace --all-targets --all-features -- -D warnings
cargo test --workspace --all-features
RUSTDOCFLAGS='-D warnings' cargo doc --workspace --all-features --no-deps
cargo run -p vcp-cli -- parse-csm1 'N5+F+E'
cargo run -p vcp-core --example parse_token
```

The Rust and Python checkers support live HTTPS status and CRL retrieval. Both
bind decisions to the requested JTI and issuer, reject non-global resolution
sets, pin validated addresses while preserving TLS hostname verification,
disable redirects and transparent decompression, bound responses, and expose an
unavailable decision separately from confirmed revocation. Verification treats
both revoked and unavailable decisions as fail-closed rejection. Shared response
vectors under `conformance/security/` keep the parsers aligned.

## WebMCP

```bash
cd webmcp
npm ci
npm run check
npm test
npm run prepack
npm pack --dry-run
```

The polyfill entry point accepts an application-owned loader only. It never
injects a remote CDN script.

```ts
import { loadPolyfillIfRequested } from '@creedspace/vcp-sdk/polyfill';

await loadPolyfillIfRequested({
  loader: async () => { await import('@mcp-b/global'); },
});
```

## Prerequisites

- Python 3.10 or newer (the locked development environment uses 3.12)
- Rust 1.87 or newer with `rustfmt` and `clippy`
- Node.js 22.12 or newer (CI validates Node 24) and npm

## Conformance and schemas

The fixture corpus currently contains 30 JSON fixtures and 352 cases.
Fixture presence alone does not establish a pass. The vector-level coverage
manifest distinguishes checked, unsupported, and not-applicable behavior. Run
the complete checked gate and repository validator:

```bash
npm ci --ignore-scripts && npm ci --ignore-scripts --prefix webmcp
python3 scripts/validate_repo.py
python3 scripts/generate_conformance_coverage.py --check
python3 conformance/runners/run_all.py
```

The aggregate runner builds the Rust CLI once and runs the packed WebMCP smoke
test, so it needs the Rust and Node toolchains above in addition to Python.

For an exact three-repository candidate set, run the integrated entry point from
this repository. Its header records all three Git hashes before any checks run:

```bash
python3 scripts/validate_ecosystem.py \
  --demo /path/to/VCP-Demo-Site \
  --spec /path/to/VCP-Spec \
  --sdk /path/to/VCP-SDK \
  --python /path/to/validation-venv/bin/python
```

The default `full` mode builds every distribution and runs dependency and secret
audits plus maintained-SDK and Demo coverage. `--mode core` is the shorter
integrated behavior gate without coverage. This helper covers exactly Demo,
Spec, and the maintained SDK. The VCP Inspector
(https://github.com/Creed-Space/VCP-Inspector) and the legacy standalone
`vcp-sdk` PyPI package (https://github.com/Creed-Space/vcp-sdk-python) are
validated separately with their own candidate-bound evidence.

For a coordinated local checkout, compare the SDK schema copies with the exact
Spec candidate:

```bash
python3 scripts/check_schema_sync.py \
  --spec /path/to/VCP-Spec \
  --sdk .

python3 scripts/validate_public_contract.py \
  --demo /path/to/VCP-Demo-Site \
  --spec /path/to/VCP-Spec \
  --sdk .
```

Schema ownership, the intentional messaging-version split, and capability
handshake ownership are documented in [SCHEMA_OWNERSHIP.md](SCHEMA_OWNERSHIP.md).

## Property, fuzz, and performance regression programmes

Deterministic property suites exercise Python parsers, Rust parsers and
classifiers, and WebMCP inputs. Performance probes enforce profile-specific
time, throughput, and memory envelopes across all three distributions:

```bash
make property PYTHON=/path/to/validation-venv/bin/python
make performance-smoke PYTHON=/path/to/validation-venv/bin/python
make performance-full PYTHON=/path/to/validation-venv/bin/python
cargo check --locked --manifest-path rust/fuzz/Cargo.toml
```

Pull requests run bounded fuzz cases and smoke performance probes. Scheduled CI
runs longer fuzz campaigns and the full performance profile. Reproduce any fuzz
failure, minimize it, and commit the input to the relevant corpus before closing
the finding. Performance results under `performance-results/` are generated
evidence and remain outside the source candidate.

## Security

Bundle verification is designed to fail closed for signature, attestation,
revocation, temporal, budget, scope, replay, and hook failures. Review
[`SECURITY.md`](SECURITY.md) for supported versions and private disclosure.

Please do not open public issues for suspected vulnerabilities. Use GitHub
private vulnerability reporting for this repository.

## Release evidence

[`RELEASE_CHECKLIST.md`](RELEASE_CHECKLIST.md) keeps machine validation, human
review, rights and licence review, deployment, and publication authority as
separate gates. A passing local build establishes machine evidence for its exact
candidate hash only.

The detailed process lives in
[`release/COORDINATED_RELEASE_RUNBOOK.md`](release/COORDINATED_RELEASE_RUNBOOK.md).
The repository validates a permanently pending ledger template with all 13
remaining human and publication gates. Copy that template to a controlled
evidence directory before reviewers add identities or decisions.

## Licence

SDK source is licensed under [MIT](LICENSE). The conformance fixture corpus
declares CC BY 4.0 in its own README. Confirm every distributed artifact against
[`ARTIFACTS.md`](ARTIFACTS.md) before publication.
