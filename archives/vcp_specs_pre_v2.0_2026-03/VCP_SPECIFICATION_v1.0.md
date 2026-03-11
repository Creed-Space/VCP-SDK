# Value-Context Protocol (VCP) Specification v1.0

**Status**: Draft
**Version**: 1.0.0
**Date**: 2026-01-11
**Authors**: Nell Watson, Claude (Anthropic)
**Informed by**: Junto Mastermind Consultation (9 models, 2026-01-10)

---

## Abstract

The Value-Context Protocol (VCP) is a specification for transporting constitutional values and behavioral rules from a repository to an AI system. It addresses the fundamental challenge that Large Language Models are "dumb receivers"—they accept text input but cannot resolve references, verify signatures, or check hashes. VCP specifies a **signed envelope format** that enables verification at the orchestration layer while delivering complete, self-contained text to the model.

VCP draws on established patterns from software supply-chain security (package signing), web integrity (Subresource Integrity), and distributed systems (content-addressed storage). It is designed to be implementation-agnostic, supporting any constitutional AI framework.

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Design Principles](#2-design-principles)
3. [Architecture Overview](#3-architecture-overview)
4. [Bundle Format](#4-bundle-format)
5. [Addressing Scheme](#5-addressing-scheme)
6. [Transport Protocol](#6-transport-protocol)
7. [Verification Protocol](#7-verification-protocol)
8. [Injection Format](#8-injection-format)
9. [Audit and Logging](#9-audit-and-logging)
10. [Trust Model](#10-trust-model)
11. [Versioning](#11-versioning)
12. [Error Handling](#12-error-handling)
13. [Security Considerations](#13-security-considerations)
14. [Interoperability](#14-interoperability)
15. [Reference Implementation](#15-reference-implementation)
16. [Appendices](#appendices)

---

## 1. Introduction

### 1.1 Problem Statement

Constitutional AI systems require a mechanism to deliver behavioral rules and value specifications to language models. Current approaches fall into two categories:

1. **Full Text Injection**: The complete constitution is embedded in the system prompt.
   - Pro: Self-contained, no resolution infrastructure needed
   - Con: Token-inefficient, no verification, no audit trail

2. **Reference-Based**: A compact code references a constitution resolved at runtime.
   - Pro: Token-efficient, enables verification
   - Con: Requires universal resolution infrastructure that doesn't exist

Neither approach provides:
- **Verifiable delivery**: Proof that the correct constitution was applied
- **Audit capability**: Record of what values were in effect during inference
- **Interoperability**: Standard format for cross-implementation exchange

### 1.2 Solution Overview

VCP solves this through a **"Verify-then-Inject" pattern**:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Repository    │────▶│  Orchestrator   │────▶│      LLM        │
│  (Signed Bundle)│     │  (Verify+Log)   │     │ (Receives Text) │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

1. Constitutions are packaged as **signed bundles** with manifest and content
2. The **orchestrator** fetches, verifies, and logs the bundle
3. The **LLM** receives verified full text with a compact header
4. **Audit systems** can verify what was applied without LLM cooperation

### 1.3 Scope

This specification covers:
- Bundle format and structure
- Addressing and identification
- Verification requirements
- Injection format for LLM consumption
- Audit logging requirements
- Trust model and key management
- Interoperability requirements

This specification does NOT cover:
- Constitution authoring (content semantics)
- Model-specific prompt engineering
- Governance of trust anchors (organizational policy)

### 1.4 Terminology

| Term | Definition |
|------|------------|
| **Bundle** | A signed package containing a constitution manifest and content |
| **Manifest** | Metadata about a constitution (ID, version, hash, signature) |
| **Content** | The actual constitutional text applied to the LLM |
| **Orchestrator** | The system that fetches, verifies, and injects constitutions |
| **Issuer** | The entity that signs and publishes constitutional bundles |
| **Trust Anchor** | A public key trusted to verify issuer signatures |

---

## 2. Design Principles

### 2.1 Verification Outside the Model

> "The LLM is the CPU, not the network card; it consumes content, it does not validate transport security." — Gemini 3 Pro

All verification MUST occur in the orchestration layer. The LLM receives only verified text. This mirrors browser SRI (Subresource Integrity): the browser verifies, the JavaScript executes.

### 2.2 Self-Contained Delivery

The LLM MUST receive complete constitutional text. It cannot resolve references or fetch external content. Compact references exist for addressing and audit, not for model consumption.

### 2.3 Content-Addressed Identity

Constitution identity SHOULD be content-addressed (hash-based) where possible. This enables:
- Deduplication across mirrors
- Verification without trusted servers
- Immutability guarantees

### 2.4 Minimal Trust Assumptions

The protocol assumes:
- The orchestrator is trusted (it's the security boundary)
- Issuers are identified by public keys
- No universal resolution infrastructure exists

### 2.5 Audit Independence

Verification records MUST be maintained independently of the LLM. Post-hoc audit MUST be possible without model cooperation.

---

## 3. Architecture Overview

### 3.1 Components

```
┌─────────────────────────────────────────────────────────────────────┐
│                         VCP ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐                                                   │
│  │   ISSUER     │  Signs and publishes constitutional bundles       │
│  │              │  Maintains revocation lists                       │
│  └──────┬───────┘                                                   │
│         │                                                           │
│         ▼                                                           │
│  ┌──────────────┐                                                   │
│  │  REPOSITORY  │  Stores bundles (any mirror, CAS, CDN)           │
│  │              │  Content-addressed (hash = identity)              │
│  └──────┬───────┘                                                   │
│         │                                                           │
│         ▼                                                           │
│  ┌──────────────┐                                                   │
│  │ ORCHESTRATOR │  TRUST BOUNDARY                                   │
│  │              │  - Fetches bundles                                │
│  │              │  - Verifies signatures and hashes                 │
│  │              │  - Checks revocation status                       │
│  │              │  - Logs to audit trail                            │
│  │              │  - Injects verified text to LLM                   │
│  └──────┬───────┘                                                   │
│         │                                                           │
│         ▼                                                           │
│  ┌──────────────┐                                                   │
│  │     LLM      │  DUMB RECEIVER                                    │
│  │              │  - Receives complete text                         │
│  │              │  - Cannot verify or resolve                       │
│  │              │  - Applies constitutional rules                   │
│  └──────────────┘                                                   │
│                                                                     │
│  ┌──────────────┐                                                   │
│  │  AUDIT LOG   │  INDEPENDENT RECORD                               │
│  │              │  - Append-only (transparency log model)           │
│  │              │  - Stores signed manifests                        │
│  │              │  - Enables post-hoc verification                  │
│  └──────────────┘                                                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 Data Flow

```
1. PUBLISH
   Issuer creates bundle → Signs manifest → Publishes to repository

2. FETCH
   Orchestrator requests bundle by address (URI, hash, or ID)

3. VERIFY
   Orchestrator checks:
   - Manifest signature against trusted issuer key
   - Content hash matches manifest.content_hash
   - Bundle is not revoked
   - Version constraints satisfied

4. LOG
   Orchestrator records to audit log:
   - Full signed manifest
   - Timestamp
   - Session/request identifier
   - Verification result

5. INJECT
   Orchestrator constructs LLM input:
   - Compact header (ID, version, hash prefix)
   - Full constitutional text
   - Structured delimiters

6. INFER
   LLM processes input with constitutional rules applied

7. AUDIT (async)
   Auditor retrieves log entries
   Verifies signatures independently
   Correlates with inference records
```

---

## 4. Bundle Format

### 4.1 Structure

A VCP bundle consists of two parts:

```
vcp-bundle/
├── manifest.json    # Signed metadata
└── content.txt      # Constitutional text (canonical format)
```

### 4.2 Manifest Schema

```json
{
  "$schema": "https://vcp.creed.space/schema/manifest/v1.json",

  "vcp_version": "1.0",

  "bundle": {
    "id": "creed://creed.space/family.safe.guide",
    "version": "1.2.0",
    "content_hash": "sha256:7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069",
    "content_encoding": "utf-8",
    "content_format": "text/markdown"
  },

  "issuer": {
    "id": "creed.space",
    "public_key": "ed25519:MC4CAQAwBQYDK2VwBCIEIH...",
    "key_id": "creed-space-2026"
  },

  "timestamps": {
    "created": "2026-01-10T12:00:00Z",
    "expires": "2027-01-10T12:00:00Z"
  },

  "revocation": {
    "check_uri": "https://creed.space/api/v1/revoked",
    "crl_uri": "https://creed.space/crl/2026.json"
  },

  "metadata": {
    "title": "Family Safety Constitution",
    "description": "Child-safe content filtering for family environments",
    "tags": ["safety", "family", "children"],
    "persona": "nanny",
    "adherence_level": 5,
    "csm1": "N5+F:ELEM@1.2.0"
  },

  "signature": {
    "algorithm": "ed25519",
    "value": "base64:MEUCIQD...",
    "signed_fields": ["vcp_version", "bundle", "issuer", "timestamps", "revocation", "metadata"]
  }
}
```

### 4.3 Manifest Fields

#### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `vcp_version` | string | Protocol version (e.g., "1.0") |
| `bundle.id` | URI | Globally unique identifier |
| `bundle.version` | semver | Semantic version |
| `bundle.content_hash` | string | SHA-256 hash of content, prefixed with algorithm |
| `issuer.id` | string | Issuer identifier |
| `issuer.public_key` | string | Public key for signature verification |
| `timestamps.created` | ISO8601 | Bundle creation timestamp |
| `signature.algorithm` | string | Signature algorithm |
| `signature.value` | string | Base64-encoded signature |
| `signature.signed_fields` | array | Fields included in signature |

#### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `bundle.content_encoding` | string | Character encoding (default: utf-8) |
| `bundle.content_format` | string | MIME type (default: text/plain) |
| `issuer.key_id` | string | Key identifier for rotation |
| `timestamps.expires` | ISO8601 | Expiration timestamp |
| `revocation.check_uri` | URI | Real-time revocation check endpoint |
| `revocation.crl_uri` | URI | Certificate revocation list |
| `metadata.*` | any | Implementation-specific metadata |

### 4.4 Content Format

Constitutional content MUST be in **canonical form** for hash verification:

1. **Encoding**: UTF-8, no BOM
2. **Line endings**: LF only (no CRLF)
3. **Trailing newline**: Single trailing LF
4. **Whitespace**: Normalized (no trailing whitespace on lines)
5. **Format**: Plain text or Markdown (specified in `content_format`)

Canonicalization pseudocode:
```python
def canonicalize(text: str) -> str:
    lines = text.replace('\r\n', '\n').replace('\r', '\n').split('\n')
    lines = [line.rstrip() for line in lines]
    while lines and lines[-1] == '':
        lines.pop()
    return '\n'.join(lines) + '\n'
```

### 4.5 Signature Computation

The signature covers a canonical JSON serialization of the signed fields:

```python
def compute_signature(manifest: dict, private_key) -> str:
    signed_fields = manifest['signature']['signed_fields']
    to_sign = {k: manifest[k] for k in signed_fields}
    canonical = json.dumps(to_sign, sort_keys=True, separators=(',', ':'))
    signature = ed25519_sign(private_key, canonical.encode('utf-8'))
    return base64.b64encode(signature).decode('ascii')
```

---

## 5. Addressing Scheme

### 5.1 Bundle URIs

Bundles are identified by URIs in the `creed://` scheme:

```
creed://<issuer>/<path>[@<version>]

Examples:
  creed://creed.space/family.safe.guide
  creed://creed.space/family.safe.guide@1.2.0
  creed://creed.space/professional/legal-assistant@2.0.0
  creed://acme-corp.example/internal/hr-policy@latest
```

#### Components

| Component | Description |
|-----------|-------------|
| `issuer` | Domain-style identifier of the signing entity |
| `path` | Hierarchical path within issuer's namespace |
| `version` | Optional version constraint (semver, "latest", "canary") |

### 5.2 Content Addresses

For content-addressed retrieval, use the hash directly:

```
vcp-hash://sha256:7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069
```

This enables:
- Retrieval from any mirror without trust
- Deduplication in caches
- Verification without manifest

### 5.3 Resolution

Orchestrators MAY resolve bundle URIs through:

1. **Direct fetch**: `https://<issuer>/.well-known/vcp/<path>.bundle`
2. **Registry lookup**: Query a VCP registry service
3. **Content-addressed fetch**: IPFS, S3, or other CAS
4. **Local cache**: Pre-fetched bundles

Resolution is implementation-defined. The protocol only specifies the bundle format and verification requirements.

---

## 6. Transport Protocol

### 6.1 Bundle Retrieval

Orchestrators MUST support retrieving bundles via HTTPS. Additional transports (IPFS, S3, etc.) are OPTIONAL.

#### HTTPS Retrieval

```http
GET /.well-known/vcp/family.safe.guide.bundle HTTP/1.1
Host: creed.space
Accept: application/vcp-bundle+json

HTTP/1.1 200 OK
Content-Type: application/vcp-bundle+json
Cache-Control: max-age=3600

{
  "manifest": { ... },
  "content": "# Family Safety Constitution\n\n..."
}
```

#### Content-Type

| Type | Description |
|------|-------------|
| `application/vcp-bundle+json` | JSON bundle (manifest + content) |
| `application/vcp-manifest+json` | Manifest only |
| `text/vcp-content` | Content only |

### 6.2 Bundle Caching

Orchestrators SHOULD cache bundles with the following policy:

1. **Cache key**: Content hash (not URI)
2. **Validation**: Re-verify signature on cache hit
3. **Expiration**: Respect `timestamps.expires` or Cache-Control
4. **Revocation**: Check revocation status periodically

### 6.3 Multi-Bundle Transport

When multiple constitutions are combined:

```json
{
  "bundles": [
    { "manifest": {...}, "content": "..." },
    { "manifest": {...}, "content": "..." }
  ],
  "composition": {
    "mode": "layered",
    "precedence": ["creed://a/b", "creed://c/d"]
  }
}
```

---

## 7. Verification Protocol

### 7.1 Verification Steps

Orchestrators MUST perform these checks before injection:

```python
def verify_bundle(bundle: Bundle, trust_anchors: dict) -> VerificationResult:
    # 1. Schema validation
    if not validate_schema(bundle.manifest):
        return VerificationResult.INVALID_SCHEMA

    # 2. Signature verification
    issuer_key = trust_anchors.get(bundle.manifest['issuer']['id'])
    if not issuer_key:
        return VerificationResult.UNTRUSTED_ISSUER

    if not verify_signature(bundle.manifest, issuer_key):
        return VerificationResult.INVALID_SIGNATURE

    # 3. Content hash verification
    computed_hash = sha256(canonicalize(bundle.content))
    if computed_hash != bundle.manifest['bundle']['content_hash']:
        return VerificationResult.HASH_MISMATCH

    # 4. Expiration check
    if bundle.manifest['timestamps'].get('expires'):
        if datetime.now() > parse_iso8601(bundle.manifest['timestamps']['expires']):
            return VerificationResult.EXPIRED

    # 5. Revocation check (optional but recommended)
    if bundle.manifest.get('revocation', {}).get('check_uri'):
        if is_revoked(bundle.manifest['bundle']['id'],
                      bundle.manifest['revocation']['check_uri']):
            return VerificationResult.REVOKED

    return VerificationResult.VALID
```

### 7.2 Verification Results

| Result | Code | Action |
|--------|------|--------|
| `VALID` | 0 | Proceed with injection |
| `INVALID_SCHEMA` | 1 | Reject, log error |
| `UNTRUSTED_ISSUER` | 2 | Reject, log warning |
| `INVALID_SIGNATURE` | 3 | Reject, log security alert |
| `HASH_MISMATCH` | 4 | Reject, log security alert |
| `EXPIRED` | 5 | Reject, attempt refresh |
| `REVOKED` | 6 | Reject, log revocation |
| `FETCH_FAILED` | 7 | Retry or fail-closed |

### 7.3 Fail-Closed Behavior

If verification fails, orchestrators MUST NOT inject unverified content. Behavior options:

1. **Block**: Refuse to proceed with inference
2. **Fallback**: Use a cached verified version
3. **Degrade**: Apply a minimal default constitution

The choice is implementation-defined, but unverified content MUST NOT be injected.

---

## 8. Injection Format

### 8.1 LLM Input Structure

The verified constitution is injected into the LLM's system prompt:

```
[VCP:1.0]
[ID:creed://creed.space/family.safe.guide@1.2.0]
[HASH:7f83b165...9069]
[VERIFIED:2026-01-10T12:00:00Z]
---BEGIN-CONSTITUTION---
# Family Safety Constitution

## Purpose
Ensure AI interactions are appropriate for family environments with children present.

## Article 1: Content Standards
...

---END-CONSTITUTION---
```

### 8.2 Header Format

```abnf
vcp-header = vcp-line id-line hash-line verified-line
vcp-line = "[VCP:" version "]" LF
id-line = "[ID:" bundle-uri "]" LF
hash-line = "[HASH:" hash-prefix "..." hash-suffix "]" LF
verified-line = "[VERIFIED:" iso8601-timestamp "]" LF

version = 1*DIGIT "." 1*DIGIT
bundle-uri = <as defined in Section 5.1>
hash-prefix = 8HEXDIG
hash-suffix = 4HEXDIG
```

### 8.3 Delimiter Requirements

Delimiters MUST be distinctive to prevent prompt injection:

1. `---BEGIN-CONSTITUTION---` before content
2. `---END-CONSTITUTION---` after content

Implementations MAY use additional markers (XML tags, special tokens) for model-specific safety.

### 8.4 Multi-Constitution Injection

When multiple constitutions apply:

```
[VCP:1.0]
[ID:creed://creed.space/family.safe.guide@1.2.0]
[HASH:7f83b165...9069]
[ID:creed://creed.space/professional/assistant@1.0.0]
[HASH:a1b2c3d4...efgh]
[PRECEDENCE:family.safe.guide>professional/assistant]
[VERIFIED:2026-01-10T12:00:00Z]
---BEGIN-CONSTITUTION---
[Constitution 1 of 2: family.safe.guide]
...

[Constitution 2 of 2: professional/assistant]
...
---END-CONSTITUTION---
```

---

## 9. Audit and Logging

### 9.1 Audit Log Requirements

Orchestrators MUST maintain an audit log with:

| Field | Required | Description |
|-------|----------|-------------|
| `timestamp` | Yes | When verification/injection occurred |
| `session_id` | Yes | Identifier correlating to inference request |
| `manifest` | Yes | Complete signed manifest |
| `verification_result` | Yes | Outcome of verification |
| `content_hash` | Yes | Hash of injected content |
| `issuer_verified` | Yes | Boolean - signature verified |

### 9.2 Log Entry Schema

```json
{
  "vcp_audit_version": "1.0",
  "timestamp": "2026-01-10T12:00:00.123Z",
  "session_id": "sess_abc123xyz",
  "request_id": "req_def456uvw",

  "verification": {
    "result": "VALID",
    "duration_ms": 45,
    "issuer_verified": true,
    "hash_verified": true,
    "revocation_checked": true
  },

  "bundle": {
    "id": "creed://creed.space/family.safe.guide@1.2.0",
    "content_hash": "sha256:7f83b165...",
    "issuer": "creed.space",
    "version": "1.2.0"
  },

  "manifest_signature": "MEUCIQD...",

  "injection": {
    "token_count": 847,
    "format": "vcp-header-delimited"
  }
}
```

### 9.3 Transparency Log (Optional)

For high-assurance deployments, orchestrators SHOULD submit audit entries to a Certificate Transparency-style log:

1. Log entries are append-only
2. Log provides inclusion proofs
3. Third parties can audit without orchestrator cooperation

### 9.4 Retention

Audit logs SHOULD be retained for:
- Minimum: Duration of any applicable regulatory requirement
- Recommended: 1 year
- Sensitive deployments: 7 years

---

## 10. Trust Model

### 10.1 Trust Anchors

Orchestrators maintain a set of trusted issuer public keys:

```json
{
  "trust_anchors": {
    "creed.space": {
      "keys": [
        {
          "id": "creed-space-2026",
          "algorithm": "ed25519",
          "public_key": "MC4CAQAwBQYDK2VwBCIEIH...",
          "valid_from": "2026-01-01T00:00:00Z",
          "valid_until": "2027-01-01T00:00:00Z"
        }
      ],
      "revocation_uri": "https://creed.space/crl/2026.json"
    }
  }
}
```

### 10.2 Key Management

#### Key Rotation
- Issuers SHOULD rotate keys annually
- Old keys remain valid for verification until expiry
- New bundles MUST use current key

#### Key Compromise
- Issuer publishes revocation for compromised key
- Orchestrators MUST check revocation before trusting
- All bundles signed with compromised key are invalidated

### 10.3 Multi-Issuer Trust

Orchestrators MAY trust multiple issuers:

```json
{
  "trust_policy": {
    "mode": "allowlist",
    "issuers": ["creed.space", "acme-corp.example"],
    "require_all": false
  }
}
```

### 10.4 Threshold Signatures (Optional)

For high-stakes constitutions, require multiple signatures:

```json
{
  "signature": {
    "algorithm": "ed25519-multisig",
    "threshold": 2,
    "signers": [
      {"id": "creed.space", "signature": "..."},
      {"id": "ethics-board.org", "signature": "..."},
      {"id": "audit-firm.com", "signature": "..."}
    ]
  }
}
```

---

## 11. Versioning

### 11.1 Semantic Versioning

Bundle versions follow semver:

| Change Type | Version Bump | Example |
|-------------|--------------|---------|
| Breaking (incompatible) | Major | 1.0.0 → 2.0.0 |
| Feature (backward compatible) | Minor | 1.0.0 → 1.1.0 |
| Fix (backward compatible) | Patch | 1.0.0 → 1.0.1 |

### 11.2 Version Constraints

Orchestrators MAY specify version constraints:

| Constraint | Meaning |
|------------|---------|
| `@1.2.0` | Exact version |
| `@^1.2.0` | Compatible with 1.2.0 (≥1.2.0, <2.0.0) |
| `@~1.2.0` | Approximately 1.2.0 (≥1.2.0, <1.3.0) |
| `@latest` | Most recent stable |
| `@canary` | Most recent (including pre-release) |

### 11.3 Version Discovery

```http
GET /.well-known/vcp/family.safe.guide/versions HTTP/1.1
Host: creed.space

HTTP/1.1 200 OK
Content-Type: application/json

{
  "bundle_id": "creed://creed.space/family.safe.guide",
  "versions": [
    {"version": "1.2.0", "released": "2026-01-10", "status": "stable"},
    {"version": "1.1.0", "released": "2025-12-01", "status": "stable"},
    {"version": "1.3.0-beta", "released": "2026-01-15", "status": "prerelease"}
  ],
  "latest": "1.2.0"
}
```

---

## 12. Error Handling

### 12.1 Error Categories

| Category | Severity | Recovery |
|----------|----------|----------|
| **Transient** | Low | Retry with backoff |
| **Configuration** | Medium | Alert operator |
| **Security** | High | Block and alert |
| **Fatal** | Critical | Fail-closed, escalate |

### 12.2 Error Responses

```json
{
  "error": {
    "code": "VCP_SIGNATURE_INVALID",
    "category": "security",
    "message": "Bundle signature verification failed",
    "details": {
      "bundle_id": "creed://creed.space/family.safe.guide@1.2.0",
      "issuer": "creed.space",
      "expected_key": "creed-space-2026"
    },
    "recovery": "block"
  }
}
```

### 12.3 Error Codes

| Code | Category | Description |
|------|----------|-------------|
| `VCP_FETCH_FAILED` | transient | Could not retrieve bundle |
| `VCP_FETCH_TIMEOUT` | transient | Retrieval timed out |
| `VCP_SCHEMA_INVALID` | configuration | Manifest schema validation failed |
| `VCP_ISSUER_UNKNOWN` | configuration | Issuer not in trust anchors |
| `VCP_SIGNATURE_INVALID` | security | Signature verification failed |
| `VCP_HASH_MISMATCH` | security | Content hash does not match |
| `VCP_BUNDLE_EXPIRED` | configuration | Bundle past expiration |
| `VCP_BUNDLE_REVOKED` | security | Bundle explicitly revoked |
| `VCP_KEY_COMPROMISED` | security | Signing key was compromised |

---

## 13. Security Considerations

### 13.1 Threat Model

| Threat | Mitigation |
|--------|------------|
| **Bundle tampering** | Content hash verification |
| **Issuer impersonation** | Signature verification against trust anchors |
| **Replay attacks** | Timestamps, version tracking |
| **Revocation bypass** | Online revocation checking |
| **Orchestrator compromise** | Out of scope (trust boundary) |
| **Prompt injection via constitution** | Structured delimiters, content validation |

### 13.2 Orchestrator Trust

The orchestrator is the trust boundary. If compromised, it can inject arbitrary content. Mitigations:

1. **Hardware attestation**: Run orchestrator in TEE/SGX
2. **Multi-party orchestration**: Multiple orchestrators must agree
3. **Audit logging**: Enable post-hoc detection

### 13.3 Prompt Injection Defense

Constitutional content could contain prompt injection attempts. Defenses:

1. **Issuer vetting**: Only trust vetted issuers
2. **Content scanning**: Scan for injection patterns
3. **Structured delimiters**: Use distinctive boundary markers
4. **Model hardening**: Train models to respect delimiters

### 13.4 Key Security

| Requirement | Rationale |
|-------------|-----------|
| Ed25519 minimum | Modern, secure, compact |
| Key rotation annually | Limit compromise window |
| Offline root keys | Protect trust anchors |
| Hardware security modules | For high-stakes deployments |

---

## 14. Interoperability

### 14.1 Conformance Levels

| Level | Requirements |
|-------|--------------|
| **VCP-Core** | Bundle format, signature verification, hash verification |
| **VCP-Full** | Core + revocation checking + audit logging |
| **VCP-Enterprise** | Full + transparency log + multi-sig |

### 14.2 Interoperability Requirements

Implementations claiming VCP conformance MUST:

1. Accept bundles from any conforming issuer
2. Produce bundles readable by any conforming orchestrator
3. Use standard cryptographic algorithms (Ed25519, SHA-256)
4. Follow canonical formats exactly

### 14.3 Extension Points

Implementations MAY extend VCP in the `metadata` field:

```json
{
  "metadata": {
    "vcp_standard": {
      "csm1": "N5+F:ELEM@1.2.0"
    },
    "x_creed_space": {
      "persona": "nanny",
      "schwartz_profile": {...}
    }
  }
}
```

Extensions MUST be prefixed with `x_` or namespaced.

---

## 15. Reference Implementation

### 15.1 Python SDK

```python
from vcp import Bundle, Orchestrator, TrustAnchor

# Configure trust
trust = TrustAnchor.from_uri("https://creed.space/.well-known/vcp/trust.json")
orchestrator = Orchestrator(trust_anchors=[trust])

# Fetch and verify
bundle = orchestrator.fetch("creed://creed.space/family.safe.guide@1.2.0")
result = orchestrator.verify(bundle)

if result.is_valid:
    # Generate injection
    injection = orchestrator.format_injection(bundle)
    print(injection)

    # Log for audit
    orchestrator.log_audit(bundle, result)
else:
    print(f"Verification failed: {result.error}")
```

### 15.2 CLI Tool

```bash
# Fetch and verify
vcp fetch creed://creed.space/family.safe.guide@1.2.0 \
    --trust-anchor https://creed.space/.well-known/vcp/trust.json \
    --output bundle.json

# Verify existing bundle
vcp verify bundle.json --trust-anchor trust.json

# Generate injection format
vcp inject bundle.json --format header-delimited > injection.txt

# Create new bundle (issuer side)
vcp create \
    --content constitution.md \
    --id creed://example.org/my-constitution \
    --version 1.0.0 \
    --key private-key.pem \
    --output bundle.json
```

---

## Appendices

### A. ABNF Grammar

```abnf
; Bundle URI
bundle-uri = "creed://" issuer "/" path ["@" version-constraint]
issuer = domain-name
path = segment *("/" segment)
segment = 1*( ALPHA / DIGIT / "-" / "_" / "." )
version-constraint = semver / "latest" / "canary"
semver = major "." minor "." patch ["-" prerelease]
major = 1*DIGIT
minor = 1*DIGIT
patch = 1*DIGIT
prerelease = 1*( ALPHA / DIGIT / "-" / "." )

; Content hash
content-hash = algorithm ":" hash-value
algorithm = "sha256" / "sha384" / "sha512"
hash-value = 64*128HEXDIG

; CSM1 (compact reference)
csm1 = persona adherence [scopes] [":" namespace] ["@" version]
persona = "N" / "Z" / "G" / "A" / "M" / "D" / "C"
adherence = 1*DIGIT
scopes = 1*("+" scope-code)
scope-code = "F" / "W" / "P" / "E" / "T" / "O" / "V" / "A"
namespace = 1*8( ALPHA / DIGIT )
```

### B. Example Bundle

```json
{
  "manifest": {
    "vcp_version": "1.0",
    "bundle": {
      "id": "creed://creed.space/family.safe.guide",
      "version": "1.2.0",
      "content_hash": "sha256:7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069",
      "content_encoding": "utf-8",
      "content_format": "text/markdown"
    },
    "issuer": {
      "id": "creed.space",
      "public_key": "ed25519:MC4CAQAwBQYDK2VwBCIEIHKhpwMdqgQwCXzLJv...",
      "key_id": "creed-space-2026"
    },
    "timestamps": {
      "created": "2026-01-10T12:00:00Z",
      "expires": "2027-01-10T12:00:00Z"
    },
    "revocation": {
      "check_uri": "https://creed.space/api/v1/revoked",
      "crl_uri": "https://creed.space/crl/2026.json"
    },
    "metadata": {
      "title": "Family Safety Constitution",
      "description": "Child-safe content filtering for family environments",
      "csm1": "N5+F:ELEM@1.2.0",
      "tags": ["safety", "family", "children"]
    },
    "signature": {
      "algorithm": "ed25519",
      "value": "base64:MEUCIQD6X8kBxRiOnN...",
      "signed_fields": ["vcp_version", "bundle", "issuer", "timestamps", "revocation", "metadata"]
    }
  },
  "content": "# Family Safety Constitution\n\n## Purpose\n\nEnsure AI interactions are appropriate for family environments with children present.\n\n## Article 1: Content Standards\n\nAt Level 5 (Maximum Protection):\n- No violence, including cartoon violence\n- No adult themes, innuendo, or suggestive content\n- No scary, disturbing, or nightmare-inducing content\n- No references to death, dying, or serious injury\n- No bullying, meanness, or social cruelty\n\n## Article 2: Language Standards\n\n- Use age-appropriate vocabulary\n- No profanity, even mild forms\n- No insults or name-calling\n- Encourage positive communication\n\n## Article 3: Topic Restrictions\n\nAvoid or age-appropriately handle:\n- Weapons and violence\n- Drugs and alcohol\n- Romantic relationships beyond friendship\n- Complex political topics\n- Religious debates\n\n## Article 4: Positive Behaviors\n\n- Encourage learning and curiosity\n- Model kindness and empathy\n- Support healthy habits\n- Promote creativity and imagination\n- Reinforce family values\n"
}
```

### C. Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-11 | Initial specification |

---

## References

1. Watson, N. & Claude. (2026). "Constitutional AI for Personalized Alignment." Creed Space Technical Report.
2. Christiano, P. et al. (2017). "Deep Reinforcement Learning from Human Preferences." NeurIPS.
3. Bai, Y. et al. (2022). "Constitutional AI: Harmlessness from AI Feedback." Anthropic.
4. Certificate Transparency. RFC 6962.
5. JSON Web Signature. RFC 7515.
6. Ed25519. RFC 8032.

---

*This specification is released under CC BY 4.0. Contributions welcome.*
