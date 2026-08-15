# Dependency consolidation review, 2026-08-15

Status: candidate review complete, hosted proof pending
Candidate branch: `codex/dependency-consolidation-20260815`
Base commit: `e6cd8ae12f7608aa2ae6a9238fd1141a69b435e0`

This review records the release-note, compatibility, security, installed-artifact,
and semantic-versioning decisions required by `DEPENDENCY_POLICY.md`. The candidate
combines the five open Dependabot pull requests so that the Rust lockfile and the
GitHub Actions pins receive one coherent validation run.

## Disposition

| PR | Update | Review decision |
|---:|---|---|
| [#69](https://github.com/Creed-Space/VCP-SDK/pull/69) | Rust patch group: regex 1.13.1, serde 1.0.229, serde_json 1.0.151, thiserror 2.0.20, getrandom 0.4.3, clap 4.6.6 | Accept the Dependabot lockfile changes. The releases contain fixes, dependency refreshes, and additive APIs. The SDK uses no newly added API. |
| [#70](https://github.com/Creed-Space/VCP-SDK/pull/70) | ed25519-dalek 2.2.0 to 3.0.0 | Accept. The release moves to Rust 2024 and current signature, digest, and randomness dependencies. Its Rust 1.85 minimum remains below this workspace's Rust 1.87 contract. Existing signing and verification code compiles and passes unchanged. |
| [#71](https://github.com/Creed-Space/VCP-SDK/pull/71) | base64 0.22.1 to 0.23.1 | Accept with an explicit feature restriction. Version 0.23 enables `simd-unsafe` by default, so the direct dependency disables default features and enables only `std`. Repository validation now enforces that security boundary. A separate transitive 0.22.1 instance remains dependency-owned. |
| [#72](https://github.com/Creed-Space/VCP-SDK/pull/72) | pypa/gh-action-pypi-publish 1.13.0 to 1.14.2 | Accept the upstream release's immutable commit. Publication remains environment-protected and authority-gated. The action's Twine, Sigstore, OIDC timeout, and caching updates do not change the workflow inputs. |
| [#73](https://github.com/Creed-Space/VCP-SDK/pull/73) | actions/setup-python 6.3.0 to 7.0.0 | Accept the upstream release's immutable commit. Version 7 migrates the action runtime to ESM without changing documented inputs, outputs, or behavior. |

## Compatibility and semantic-version decision

The Rust source required no API adaptation for ed25519-dalek 3 or base64 0.23.
The complete workspace builds, tests, lints, documents, and packages with the
existing public interfaces. The project minimum remains Rust 1.87. The changes
therefore require no SDK version increment by themselves and belong under the
current Unreleased changelog section.

Hosted Linux, Windows, macOS, Rust 1.87, stable Rust, WASM, Node 22 and 24, and
installed-artifact jobs must pass on the exact consolidation commit before merge.
That hosted requirement is especially important because the local Homebrew Rust
installation cannot prove Rust 1.87 or the absent `wasm32-unknown-unknown` target.

## Security review

`cargo audit` reports no known vulnerability in the candidate lockfile. Strict
Clippy, the complete Rust tests, package verification, repository validation,
and the direct feature tree pass. The direct base64 dependency exposes only
`alloc` and `std`; `simd-unsafe` is absent. GitHub Actions remain pinned to exact
commit SHAs verified against the advertised upstream releases.

The candidate neither enables publication nor supplies any package-registry,
signing, or release-authority credential. Existing fail-closed publication gates
remain unchanged.

## Candidate evidence

- `python3 scripts/validate_repo.py`
- `python3 scripts/check_release_authority.py --version 4.2.0`
- `actionlint`
- `cargo audit --file rust/Cargo.lock`
- `cargo fmt --all -- --check`, from `rust/`
- `make rust`
- `make packages`
- `cargo test --workspace --all-features --locked -q`, from `rust/`
- `python3 -m ruff check scripts`
- `python3 -m ruff format --check scripts`
- `python3 scripts/validate_review_ledger.py`
- `python3 scripts/verify_artifacts.py`: 7 artifacts, 32 checks passed,
  1 unsupported local WASM target, 0 failed

The original Dependabot pull requests are closed as superseded only after this
candidate has passed its exact hosted matrix and reached `main`.

## Post-merge lock reconciliation

The exact-main full ecosystem run found that `rust/fuzz/Cargo.lock` still
resolved ed25519-dalek 2.2 and therefore rejected `cargo check --locked` after
the vcp-core dependency update. The ordinary SDK matrix had passed because the
fuzz workflow's path filter covered selected core source files but omitted
`rust/vcp-core/Cargo.toml`.

The follow-up candidate regenerates the independent fuzz lockfile, verifies it
with `cargo check --locked --manifest-path rust/fuzz/Cargo.toml`, and broadens
the fuzz trigger to every `rust/vcp-core/**` change. Repository validation now
enforces that trigger, preventing dependency changes from bypassing the lockfile
gate again. The failed aggregate receipt is retained as part of the audit trail.

Working if: the merged lockfile contains every reviewed update, the direct
base64 feature boundary cannot drift silently, exact hosted checks pass before
merge, and no publication authority is inferred from dependency maintenance.
