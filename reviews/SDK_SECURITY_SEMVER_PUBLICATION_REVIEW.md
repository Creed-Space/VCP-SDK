# VCP-SDK security, semver, and publication review

This worksheet covers K044, K045, K046, and the SDK portions of X017 and X018.
Complete it against the exact candidate manifest identified in the coordinated
review ledger. Keep the completed report in the controlled release evidence
directory when it contains private findings or reviewer information.

## Candidate identity

| Field | Value |
|---|---|
| SDK commit | |
| SDK working-tree SHA-256 | |
| Combined candidate SHA-256 | |
| Candidate-manifest SHA-256 | |
| Python version | |
| Rust version | |
| WebMCP version | |
| Protocol baseline and amendment maturity | |
| Reviewer | |
| Reviewer independence statement | |
| Review start and completion | |

Stop if any value differs from the coordinated ledger.

## K045: independent signature, revocation, and scope review

### A. Signature and canonicalization

Review at least:

1. Algorithm allowlists and rejection of missing, unknown, downgraded, or
   mismatched algorithms.
2. Key identifier resolution, issuer binding, namespace ownership, key-use
   restrictions, and duplicate-key behavior.
3. Canonical JSON and byte-level signing input across Python, Rust, and WebMCP.
4. Unicode normalization, duplicate members, number handling, map ordering,
   omitted defaults, and parser differential behavior.
5. Signature length, encoding, malformed key, malformed signature, and
   multi-signature threshold behavior.
6. Time validity, clock boundaries, expiration, future issuance, and replay
   identifiers.
7. Error-category stability and whether callers can distinguish policy failure,
   invalid proof, and transient dependency failure.
8. Secret-key lifetime, accidental logging, memory copies, examples, and test
   fixture isolation.

Required adversarial probes:

| Probe | Expected result | Evidence |
|---|---|---|
| Change one signed field | Signature rejection | |
| Reorder semantically equivalent input before canonicalization | Identical canonical bytes or explicit rejection | |
| Supply unsupported algorithm | Fail closed | |
| Supply wrong issuer key | Fail closed | |
| Duplicate key identifier | Deterministic rejection | |
| Invalid threshold or duplicate signer | Fail closed | |
| Expired and not-yet-valid token | Correct distinct failure | |
| Cross-language shared vectors | Identical decisions | |

### B. Revocation transport and policy

Trace the whole path from manifest configuration to final verifier decision.
Review both Python and Rust.

1. HTTPS-only URI policy, prohibited credentials, fragments, nonstandard ports,
   malformed hosts, and IP literals.
2. Complete DNS resolution before connection. Reject the entire result set when
   any address is private or reserved.
3. Address pinning between validation and connection, while preserving TLS SNI
   and hostname verification.
4. Disabled proxies, redirects, retries, referrers, transparent decompression,
   and ambient resolver behavior.
5. Connection and total timeouts, header count, aggregate header bytes,
   content-length checks, streamed body cap, JSON object requirement, content
   type, and content encoding.
6. Binding of online responses and CRLs to exact issuer and JTI.
7. Strict timestamp parsing, freshness, cache key composition, cache TTL,
   eviction, and stale-data rejection.
8. Fallback ordering between online status and CRL. Verify that a failed source
   cannot silently become a clear decision.
9. Distinction among `not_revoked`, `revoked`, and `unavailable`. Confirmed
   revocation and unavailable infrastructure must remain separate in telemetry,
   while policy rejects unavailable status where revocation is required.
10. DNS-rebinding, mixed public/private answers, timeout, malformed JSON,
    compressed response, header overflow, body overflow, issuer mismatch, JTI
    mismatch, contradictory fields, and CRL freshness tests.

Required live-network review uses an isolated test domain and controlled DNS.
Do not point probes at internal addresses or production services. Mock transport
tests establish code behavior but do not establish real resolver, TLS, or proxy
behavior on every supported platform.

### C. Scope and glob enforcement

Review:

1. Default-deny behavior for missing, empty, unknown, and malformed scopes.
2. Exact resource, tool, extension, and operation matching.
3. Wildcard grammar, separator semantics, anchoring, escaping, repeated
   wildcards, and pathological input complexity.
4. Case sensitivity and Unicode normalization.
5. URL, path, namespace, and identifier canonicalization before matching.
6. Deny precedence, ambiguous overlap, delegation or attenuation, and
   privilege-escalation paths.
7. Cross-language parity and compatibility with published examples.
8. Audit events for allow, deny, malformed policy, and resource-limit outcomes.

Property tests and bounded fuzzing are supporting evidence. The reviewer should
also construct adversarial examples from the grammar and attempt to disprove
the intended authorization boundary.

### D. Findings and decision

| Finding ID | Severity | Surface | Reproduction or trace | Required remediation | Disposition |
|---|---|---|---|---|---|
| | | | | | |

Decision: pending

Required ledger evidence kind: `independent-security-report` for K045. The same
report may support X017 only when it also addresses the normative protocol and
the reviewer is independent for both scopes.

## K046: semantic versioning decision

Compare the last published SDK contract with the candidate. Include serialized
error codes, enum exhaustiveness, default policy, public types, package exports,
documented behavior, and operational assumptions.

### Compatibility worksheet

| Change | Additive source API? | Runtime behavior changed? | Serialized contract changed? | Existing callers may fail? | Required migration |
|---|---|---|---|---|---|
| Distinct revocation-unavailable outcome | | | | | |
| Live Rust HTTPS revocation transport | | | | | |
| Fail-closed configured-source behavior | | | | | |
| Response issuer and JTI binding | | | | | |
| Response and transport resource bounds | | | | | |
| New conformance, property, and performance suites | | | | | |

Decision options:

1. Major release when exhaustive enum matching, serialized error codes,
   defaults, or previously accepted input can break existing callers.
2. Minor release only when the public API is additive, existing documented
   valid behavior remains valid, and compatibility tests demonstrate that old
   callers continue to function.
3. Patch release only for a defect correction with no new public behavior or
   compatibility burden.

Default safe recommendation: choose a major release if
`REVOCATION_UNAVAILABLE`, verification code 17, or fail-closed behavior can be
observed by existing callers. Choose a minor release only after the reviewer
demonstrates that these are additive refinements to an already documented
three-state and fail-closed contract. A patch release is not recommended for
this change set.

Record:

| Field | Decision |
|---|---|
| Chosen version | |
| Compatibility evidence | |
| Required migration note | |
| Deprecation policy | |
| Maintainer and timestamp | |

Required ledger evidence kind: `semver-decision`.

## K044: signed publication

K044 is an authorized publication action. Preparing commands or packages does
not close it.

### Prepublication checks

1. X015, X016, X017, D042, S030, S031, S032, S033, K045, and K046 have approved
   decisions for the exact candidate.
2. Machine acceptance is fresh for the same clean commits.
3. Package versions match K046 and are consistent across metadata, imports,
   lock files, docs, and changelog.
4. Package contents contain only intended files, licences, notices, schemas,
   types, and runtime assets.
5. Rebuilt artifact hashes match the reviewed inventories or have an approved
   reproducibility explanation.
6. Signing identity, protected build environment, registry accounts, MFA, and
   recovery owners are confirmed.
7. No credential is copied into a repository, environment file, evidence log,
   or shell history.

### Artifact inventory

| Ecosystem | Package | Version | Artifact | SHA-256 | Signature or attestation | Registry receipt |
|---|---|---|---|---|---|---|
| Python | `value-context-protocol` | | wheel | | | |
| Python | `value-context-protocol` | | sdist | | | |
| Rust | `vcp-core` | | crate | | | |
| Rust | `vcp-cli` | | crate | | | |
| Rust | `vcp-wasm` | | crate | | | |
| npm | `@creedspace/vcp-sdk` | | tarball | | | |

Publish `vcp-core` before verifying and publishing dependent Rust crates. Verify
every registry result from a new environment with exact versions and no local
overrides. Compare installed package metadata and files with the reviewed
artifact.

Required ledger evidence kinds: `artifact-signature` and `registry-receipt`.

## SDK portion of X018

From fresh environments:

1. Install all published packages by exact version.
2. Import or execute the documented entry point.
3. Run a sign-and-verify example with a newly generated test key.
4. Run shared canonicalization and conformance examples.
5. Verify allowed scope, denied scope, confirmed revocation, clear revocation,
   and unavailable revocation behavior.
6. Confirm package licences, notices, type information, and exported names.
7. Record registry-resolved URLs, checksums, timestamps, and environment
   versions.

Required ledger evidence kind: `production-smoke-report` under X018.

## Attestation

I reviewed the candidate and evidence identified above. I disclosed relevant
conflicts and did not infer runtime, legal, governance, or publication evidence
from machine tests alone.

| Field | Value |
|---|---|
| Decision | pending |
| Reviewer identity | |
| Attestation method | |
| Attestation value | |
| Timestamp | |
