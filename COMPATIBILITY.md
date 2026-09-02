# Version and Compatibility Policy

VCP uses separate version domains. An SDK release number does not declare a new
protocol release.

| Surface | Repository status | Compatibility meaning |
|:---|:---|:---|
| Core specification | v3.1 source baseline | Mutable source reference; immutable normative release remains open |
| v3.2 amendments | Pre-release | Candidate behavior requiring governance approval |
| VEP-0004 | Experimental | Extended adaptation dimensions requiring negotiation |
| Python SDK | 4.2.0, `value-context-protocol` | Project-maintained implementation with selected v3.2 candidate support |
| Rust SDK | 4.2.0 workspace, `vcp-core` | Core, CLI, and WASM implementation with selected v3.2 candidate support |
| WebMCP SDK | 4.2.0, `@creed-space/vcp-sdk` | Browser integration subset, not a full protocol implementation |
| Demo | 0.1.0 application | Demonstration release, not conformance evidence |

## Candidate runtime matrix

The source candidate declares the following compatibility window. CI is the
acceptance authority for each row; metadata alone is not proof.

| Surface | Declared candidate support | Required evidence |
|:---|:---|:---|
| Python | CPython 3.10 through 3.14 | Full suite on Ubuntu for every version; Python 3.12 smoke on macOS and Windows |
| Python extras | core, server, MCP, Redis, metrics, and combined | Clean install and import smoke for every surface |
| Python dependency bounds | Declared direct minima and latest compatible resolution | Direct-minimum test job plus normal latest-resolution jobs |
| Node | 22.12 or later in Node 22 LTS; Node 24 LTS | Type check, unit tests, packed artifact import, and audit on both majors |
| Rust | MSRV 1.87 and current stable | Workspace test at MSRV and stable; stable lint, docs, and packages |
| Native operating systems | Ubuntu 24.04, macOS 15, Windows 2025 | Python and Rust matrix jobs |
| WASM | `wasm32-unknown-unknown` for `vcp-wasm` | Explicit target build using the stable toolchain |
| WebMCP | Compatible Chromium implementations exposing the experimental `document.modelContext` API | Packed package and browser lifecycle checks; generic Demo flows use a broader browser matrix |

Outbound revocation checks use the platform trust store and explicitly require
TLS 1.2 or later. Applications may impose a higher floor, but they must not
weaken this minimum. Certificate and hostname verification remain enabled.

No `no_std`, WASI, alternative Python implementation, Node 20, or non-Chromium
WebMCP support is claimed by this candidate.

## Python 3.10 retirement

Python 3.10 remains supported through 31 October 2026. The recommended next
minimum is Python 3.11, effective no earlier than the first semver-reviewed SDK
release after that date. The release review must confirm downstream usage,
dependency support, classifiers, Ruff and mypy targets, CI, and migration notes
before changing `requires-python`. Until that decision is recorded, Python 3.10
remains a required green job.

## Dependency-bound policy

Runtime dependencies use explicit direct lower bounds. CI checks two distinct
resolutions:

1. Normal installers select the latest compatible dependency graph.
2. `scripts/lower_bound_requirements.py` pins every declared direct runtime
   minimum and runs the package suite against those minima.

Transitive minima remain controlled by each direct dependency's metadata. A
direct-minimum pass must not be described as a fully minimized transitive lock.
When a declared minimum no longer works, repair support or raise the bound in a
semver-reviewed change rather than allowing CI to select newer packages
silently.

## Messaging and capability negotiation

The Spec repository owns the normative VCP/M v1.2 schema and the capability
handshake schema. This SDK also carries an implementation-candidate messaging
v2.0 schema. Consumers must negotiate the messaging major version. VCP/M v1.2
and v2.0 payloads are not silently interchangeable.

The SDK implements capability-negotiation behavior but does not vendor a second
copy of the Spec-owned handshake schema. Changes to handshake syntax start in
VCP-Spec and are consumed here only after review.

## Compatibility rules

1. Normative changes require the VEP process and an explicit protocol release.
2. SDK patch and minor releases may repair defects without changing the wire
   protocol. Fail-closed changes still require migration notes.
3. Experimental behavior must be capability-negotiated and labelled.
4. Conformance applies to an exact Spec and SDK commit pair. A green build in one
   repository is insufficient.
5. Release notes state both package versions and the supported protocol baseline.
6. Common schema copies must pass `scripts/check_schema_sync.py` against the
   selected Spec checkout.
7. Public package names, versions, exports, protocol labels, and Demo guidance
   must pass `scripts/validate_public_contract.py` against the selected Demo and
   Spec checkouts. The integrated ecosystem validator runs this automatically.

## Revocation migration note

The unreleased revocation transport adds verification result code `17`, exposed
as `REVOCATION_UNAVAILABLE` in Python and `RevocationUnavailable` in Rust. It is
a fail-closed rejection with the transient category. Code `15` remains reserved
for a confirmed revocation.

Online status services must echo the requested `jti` and `issuer`. A response
claiming revocation must also provide a non-empty reason and a timezone-qualified
RFC 3339 `revoked_at`. Integrators should treat this as a behavior change and
must complete the semver review in the coordinated release ledger before
publishing packages.

## CSM-1 encoding tiers

The Python, Rust and WebMCP implementations support the NANO and MICRO CSM-1
tiers. The COMPACT tier (`CS1|<persona>|<level>|<token>|<scopes>`, VCP/S §2.8)
is not implemented in this repository: parsers reject COMPACT input. The
standalone `vcp-sdk` package and VCP-Inspector parse COMPACT.
