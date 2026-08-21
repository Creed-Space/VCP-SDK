# Testing Approach

<!-- wiki:type = system -->
<!-- wiki:scope = vcp-sdk -->
<!-- wiki:created = 2026-05-23 -->
<!-- wiki:updated = 2026-08-14 -->
<!-- wiki:status = active -->

## Summary

VCP-SDK uses complementary evidence layers rather than treating one test suite
as proof of the whole distribution. The repository combines implementation
tests, language-neutral conformance vectors, property tests, fuzz targets,
risk-based coverage floors, selective mutation testing, performance envelopes,
package-install smoke tests, schema synchronization, and dependency audits.

## Evidence layers

| Layer | Maintained surface | Principal gate |
|:---|:---|:---|
| Python behavior | Unit, integration, property, and protocol-vector tests under `python/tests/` | `make python`, `make property`, and `make coverage` |
| Rust behavior | Unit, integration, property, examples, CLI, and documentation | `make rust`, `make examples`, and `make packages` |
| WebMCP behavior | Type checks, unit tests, property tests, registration lifecycle, and packed-package import | `make webmcp` |
| Cross-language behavior | 27 JSON fixture files containing 337 tracked cases | `make conformance` |
| Security depth | Critical module statement and branch floors, scheduled mutation lanes, fuzzing, and audits | `make coverage`, `mutation.yml`, `fuzz.yml`, and `make audits` |
| Runtime compatibility | Python 3.10 through 3.14, two Node LTS lines, Rust 1.87 and stable, native OS matrix, WASM | `.github/workflows/ci.yml` |
| Installed artifacts | Wheel, sdist, three Cargo crates, npm tarball, and WASM target | `scripts/verify_artifacts.py` |
| Performance | Smoke envelopes on pull requests and full scheduled probes | `performance.yml` and `scripts/run_performance.py` |

## Conformance model

The conformance corpus is organized by identity, semantics, adaptation,
extensions, interoperability, transport, and security. Each case is classified
as checked, unsupported, or not applicable in `conformance/coverage-manifest.json`.
The aggregate runner executes 16 checked profiles and writes candidate-bound
JSON reports under `conformance/reports/`. Fixture presence by itself is not a
pass.

## Risk-based depth

`scripts/check_critical_coverage.py` enforces separate statement and branch
floors for bundle verification, canonicalization, enforcement, identity tokens,
orchestration, privacy, revocation, and CSM1 parsing. The floors are deliberately
per module so strong aggregate coverage cannot hide a weak security boundary.

Scheduled mutation lanes target privacy, revocation, identity-token, and
canonicalization code. Mutation output is retained as evidence and evaluated by
an explicit policy rather than trusting the mutation runner's process status.
The current regression floors are 75, 63, 82, and 82 percent respectively.
They sit below fresh candidate measurements, fail on unexecuted or timed-out
mutants, and are intended to rise as useful survivor tests are added.
Rust fuzz targets cover CSM1, full contexts, identity scope, canonicalization,
and revocation JSON. Any minimized failure becomes a committed regression case.

## Local commands

```bash
make validate PYTHON="$(command -v python)"
make coverage PYTHON="$(command -v python)"
make property PYTHON="$(command -v python)"
make performance-smoke PYTHON="$(command -v python)"
make python PYTHON="$(command -v python)"
make rust
make webmcp
make examples
make packages
make audits PYTHON="$(command -v python)"
```

`scripts/validate_ecosystem.py` is the integrated three-repository gate. It
records the Demo, Spec, and SDK Git hashes before checking their shared schemas,
public contract, packages, tests, audits, and conformance behavior.

## Evidence limits

Local tests prove only the exact source and environment used. Hosted operating
system matrices, production proxy behavior, accessibility review, cryptographic
review, registry publication, and governance decisions remain distinct gates.

## Provenance

Sources verified on 2026-08-14: `Makefile`; `.github/workflows/ci.yml`;
`.github/workflows/fuzz.yml`; `.github/workflows/mutation.yml`;
`.github/workflows/performance.yml`; `python/pyproject.toml`;
`scripts/check_critical_coverage.py`; `scripts/verify_artifacts.py`;
`conformance/coverage-manifest.json`; `conformance/runners/run_all.py`.

## See Also

* [[vcp-sdk:systems/sdk-architecture]]
* [[vcp-sdk:systems/python-sdk-modules]]
* [[vcp-sdk:systems/rust-implementation]]
* [[vcp-sdk:systems/webmcp-typescript]]
* [[vcp-sdk:flows/bundle-sign-verify]]
