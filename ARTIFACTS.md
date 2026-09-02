# Artifact Canonicality and Packaging

## Source authority

The normative protocol source lives in VCP-Spec. This repository contains SDK
implementations, synchronized schema copies, fixtures, and examples. Generated
archives and compiled output are disposable build products.

## Distribution contracts

| Distribution | Build command | Required contents | Excluded contents |
|:---|:---|:---|:---|
| Python wheel and sdist | `python -m build`, deterministic sdist normalization, then `python -m twine check dist/*` | `vcp` package, reproducible archive metadata, validated package metadata, README, MIT licence | tests, caches, credentials, local environments |
| Rust crates | `make packages` from the repository root | crate sources, manifest, MIT licence | workspace target output and local configuration |
| WebMCP npm package | `npm pack --dry-run` in `webmcp/` | `dist/`, README, MIT licence, package metadata | `src/`, tests, source maps, dependencies |

The checked package manifest is evidence for the exact source tree used to build
it. Publication requires a fresh manifest, checksum, and authorized release
decision.

`scripts/verify_artifacts.py --artifact-dir <empty-directory>` exports the exact
artifacts that passed installation and smoke checks. The release workflow adds
deterministic CycloneDX SBOMs, generates `SHA256SUMS` and
`release-manifest.json` last, compares a second clean build byte for byte, then
attests the delivered files. Python and npm publication jobs download that same
attested directory and never rebuild their distributions.

The verifier runs every public Python example from a clean environment after
installing each wheel and sdist. It also extracts the packaged `vcp-core` crate
and runs the three public Rust quick starts from that archive. The WebMCP packed
test imports the tarball output and exercises registration and cleanup through
the public API. Source-tree imports do not count as installed-artifact evidence.

`vcp-cli` and `vcp-wasm` depend on the same-version `vcp-core` crate. Before that
exact `vcp-core` version exists on crates.io, the package command uses a
command-line `patch.crates-io` entry to resolve `vcp-core` from the local
workspace. Cargo still creates and compiles each publishable archive. After
publishing `vcp-core`, the release owner must run ordinary verified `cargo
package` for both dependent crates before publishing either one. Because the
patch-built archives embed a `Cargo.lock` that records `vcp-core` without a
registry source or checksum, the publish workflow compares the re-packaged
dependent crates with the attested archives file by file, excluding only that
generated `Cargo.lock`; every other byte must be identical.

## Generated paths

The following paths are generated and must remain untracked:

* `python/build/`, `python/dist/`, and Python metadata directories
* `rust/target/` and `rust/vcp-wasm/pkg/`
* `webmcp/dist/` and all `node_modules/` directories

The conformance JSON files are authored fixtures. They are versioned sources,
not generated test output.

## Licence copies

Every independently published package must contain the MIT licence. The root
licence is copied into `python/`, each Rust crate, and `webmcp/`. A release
review confirms that copied texts remain byte-identical.
