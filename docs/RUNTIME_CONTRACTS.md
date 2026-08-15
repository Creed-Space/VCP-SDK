# VCP-SDK runtime contracts

<!-- vcp-document-control
status: Current implementation contract
normative-authority: SDK behavior only; VCP-Spec controls protocol semantics
protocol-version: VCP 3.1 source baseline with labelled candidate behavior
last-reviewed: 2026-08-15
owner: VCP-SDK maintainers
evidence-boundary: Documented project implementation, not deployment approval or independent review
-->

## Cancellation, deadlines, and cleanup

Cancellation is fail closed before authorization. A cancelled verification does
not return a partial success or reusable grant. Network callers set explicit
deadlines; the Python and Rust revocation clients apply bounded request timeouts
and redirect policy. Retrying is the caller's decision and remains bounded by
its deadline, retry budget, replay identifiers, and the selected status code's
retryability.

WebMCP registration returns an idempotent `cleanup()` function. It aborts every
accepted registration and is safe to call repeatedly. Application-owned
`AbortController` signals cancel chat requests and polyfill loading where those
interfaces accept a signal. Cancellation cannot reverse an external side
effect already accepted by another service; such operations need their own
idempotency and recovery contract.

Hook `ABORT` stops the current pipeline. It does not mean “allow with a
warning.” Exceptions and unavailable required evidence map to a stable failure
code and must not expand authority.

## Cache semantics

### Replay caches

Replay entries are keyed by JTI and remain through their validity window.
Capacity exhaustion fails closed. The in-memory cache is process-local and is
not sufficient for horizontally scaled or durable deployments. Applications
must inject a shared, atomic store before relying on replay protection across
workers or restarts.

### Revocation caches

Decision cache keys bind status URI, expected issuer, and JTI. CRL cache keys
bind URI and expected issuer. Entries expire at the earlier of configured TTL
or authoritative freshness. Expired, malformed, misbound, or unavailable
evidence never becomes `not_revoked`. Cache sizes are bounded and deterministic
eviction does not convert an unavailable check into authorization.

The current caches use a monotonic process clock for residence time and
timezone-qualified timestamps for protocol freshness. They are isolated to one
SDK object or process unless the application deliberately provides shared
state. No offline freshness guarantee is claimed.

## Key custody boundary

Core signing functions accept caller-provided key bytes or a signing callback.
The SDK does not claim production key storage. Applications should place key
custody behind a minimal adapter whose operation is `sign(key_id, bytes)` and
whose verification side exposes trusted public keys by immutable identifier.
The adapter may use a macOS Keychain, platform keystore, hardware security
module, or managed key service without exporting private material.

Local raw-key and PEM paths are development and migration surfaces. Production
code should avoid exporting a private key into application memory when its
keystore supports in-place signing. Rotation, revocation, authorization,
availability, audit, recovery, and algorithm policy belong to the deployment.
The SDK never logs keys or signatures as observability labels.

## Observability and privacy

Python metrics are inactive no-ops unless the optional metrics dependency is
installed and collected by the application. Labels are bounded categories and
must not include content, context values, identifiers, keys, signatures,
prompts, network bodies, or personal state. WebMCP's optional `onToolCall` hook
receives only the declared tool name. No SDK surface sends telemetry over the
network by default.

Applications that export metrics or traces own opt-in configuration, endpoint
security, sampling, retention, access control, data residency, and privacy
approval. An observability hook is not permission to add payloads later.

## Failure and retry table

| Category | Default retry view | Authority effect |
|:---|:---|:---|
| `success` | No retry needed | Exact verified operation may proceed |
| `security` | Do not retry unchanged input | Deny and alert according to policy |
| `temporal` | Retry only when a valid future time can change the result | Deny until then |
| `transient` | Bounded retry may be appropriate | Deny while evidence is unavailable |
| `configuration` | Repair trust, scope, schema, or budget first | Deny |

The selected VCP-Spec verification status registry controls exact codes. This
table is orchestration guidance and never authorizes fail open behavior.

## Working signal

These contracts are working when cancellation at each meaningful phase yields
no partial authorization, cache partitions and expiry are exercised in tests,
the same status code appears across Python and Rust, cleanup is idempotent, and
installing no optional metrics dependency produces no telemetry or network
activity.
