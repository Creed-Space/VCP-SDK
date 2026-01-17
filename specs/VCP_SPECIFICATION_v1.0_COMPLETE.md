# Value-Context Protocol (VCP) Specification v1.0

**Status**: Draft
**Version**: 1.0.0
**Date**: 2026-01-11
**Authors**: Nell Watson, Claude (Anthropic)
**Informed by**: Junto Mastermind Consultation (9 models, 2026-01-10, 2026-01-11)

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
5. [Canonicalization](#5-canonicalization)
6. [Addressing Scheme](#6-addressing-scheme)
7. [Transport Protocol](#7-transport-protocol)
8. [Verification Protocol](#8-verification-protocol)
9. [Content Safety](#9-content-safety)
10. [Composition Semantics](#10-composition-semantics)
11. [Injection Format](#11-injection-format)
12. [Audit and Logging](#12-audit-and-logging)
13. [Trust Model](#13-trust-model)
14. [Key Lifecycle](#14-key-lifecycle)
15. [Versioning](#15-versioning)
16. [Error Handling](#16-error-handling)
17. [Security Considerations](#17-security-considerations)
18. [Threat Model](#18-threat-model)
19. [Interoperability](#19-interoperability)
20. [Reference Implementation](#20-reference-implementation)
21. [Appendices](#appendices)

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
- Content safety attestation
- Composition and conflict resolution
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
| **Safety Auditor** | Entity that attests content has been reviewed for injection attacks |
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

### 2.6 Fail-Closed by Default

All verification failures MUST result in rejection. Orchestrators MUST NOT inject unverified content under any circumstances.

### 2.7 Defense in Depth

Signature verification proves authenticity but not safety. Content safety attestation provides a second layer ensuring the content has been reviewed for injection attacks.

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
│  │SAFETY AUDITOR│  Reviews content for injection patterns           │
│  │              │  Provides safety attestation signature            │
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
│  │              │  - Verifies issuer signature                      │
│  │              │  - Verifies safety attestation                    │
│  │              │  - Validates temporal claims                      │
│  │              │  - Checks token budget                            │
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
│  │              │  - Stores signed manifests (not content)          │
│  │              │  - Enables post-hoc verification                  │
│  └──────────────┘                                                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 Data Flow

```
1. AUTHOR
   Constitution author creates content

2. REVIEW
   Safety auditor reviews for injection patterns
   Safety auditor signs attestation

3. PUBLISH
   Issuer creates bundle → Signs manifest → Publishes to repository

4. FETCH
   Orchestrator requests bundle by address (URI, hash, or ID)

5. VERIFY
   Orchestrator checks:
   - Schema validity
   - Issuer signature against trusted key
   - Safety attestation signature
   - Content hash matches manifest
   - Temporal claims (iat, nbf, exp, jti)
   - Token budget constraints
   - Scope binding
   - Revocation status

6. LOG
   Orchestrator records to audit log:
   - Manifest hash (not full content)
   - Timestamp
   - Session/request identifier
   - Verification result

7. INJECT
   Orchestrator constructs LLM input:
   - Compact header (ID, version, hash prefix)
   - Full constitutional text
   - Structured delimiters

8. INFER
   LLM processes input with constitutional rules applied

9. AUDIT (async)
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
    "iat": "2026-01-10T12:00:00Z",
    "nbf": "2026-01-10T12:00:00Z",
    "exp": "2026-02-10T12:00:00Z",
    "jti": "550e8400-e29b-41d4-a716-446655440000"
  },

  "budget": {
    "token_count": 847,
    "tokenizer": "cl100k_base",
    "max_context_share": 0.25
  },

  "scope": {
    "model_families": ["gpt-*", "claude-*"],
    "purposes": ["general-assistant", "family-assistant"],
    "environments": ["production", "staging"]
  },

  "composition": {
    "layer": 2,
    "mode": "extend",
    "conflicts_with": [],
    "requires": ["creed://creed.space/uef"]
  },

  "revocation": {
    "check_uri": "https://creed.space/api/v1/revoked",
    "crl_uri": "https://creed.space/crl/2026.json",
    "stapled_proof": null
  },

  "safety_attestation": {
    "auditor": "safety-review.creed.space",
    "auditor_key_id": "safety-2026",
    "reviewed_at": "2026-01-10T11:00:00Z",
    "attestation_type": "injection-safe",
    "signature": "base64:MEUCIQDr..."
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
    "signed_fields": ["vcp_version", "bundle", "issuer", "timestamps", "budget", "scope", "composition", "revocation", "safety_attestation", "metadata"]
  }
}
```

### 4.3 Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `vcp_version` | string | Protocol version ("1.0") |
| `bundle.id` | URI | Globally unique identifier |
| `bundle.version` | semver | Semantic version |
| `bundle.content_hash` | string | SHA-256 hash of canonical content |
| `issuer.id` | string | Issuer identifier |
| `issuer.public_key` | string | Public key for signature verification |
| `timestamps.iat` | ISO8601 | Issued At timestamp |
| `timestamps.nbf` | ISO8601 | Not Before timestamp |
| `timestamps.exp` | ISO8601 | Expiration timestamp |
| `timestamps.jti` | UUID | Unique bundle instance identifier |
| `budget.token_count` | integer | Token count of content |
| `safety_attestation.*` | object | Safety review attestation |
| `signature.*` | object | Issuer signature |

### 4.4 Size Constraints

| Component | Maximum | Rationale |
|-----------|---------|-----------|
| Manifest JSON | 64 KB | Metadata shouldn't be huge |
| Constitution content | 256 KB | ~50K tokens maximum |
| Total bundle | 320 KB | Manifest + content |
| Bundle URI | 2048 chars | URL length limits |
| Constitutions per request | 10 | Context budget |

---

## 5. Canonicalization

### 5.1 Manifest Canonicalization (JCS)

Manifest canonicalization follows RFC 8785 (JSON Canonicalization Scheme):

```python
import json

def canonicalize_manifest(manifest: dict) -> bytes:
    """RFC 8785 JSON Canonicalization Scheme"""
    # Remove signature before canonicalizing
    to_sign = {k: v for k, v in manifest.items() if k != 'signature'}

    # JCS rules:
    # - UTF-8 encoding
    # - No whitespace between tokens
    # - Object keys sorted lexicographically
    # - Numbers in shortest form
    return json.dumps(
        to_sign,
        ensure_ascii=False,
        sort_keys=True,
        separators=(',', ':')
    ).encode('utf-8')
```

### 5.2 Content Canonicalization

Constitutional content MUST be canonicalized before hashing:

```python
import unicodedata
import hashlib

def canonicalize_content(text: str) -> bytes:
    """Canonical form for constitution content."""

    # 1. Unicode NFC normalization
    text = unicodedata.normalize('NFC', text)

    # 2. Line ending normalization (CRLF/CR → LF)
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    # 3. Strip trailing whitespace from each line
    lines = [line.rstrip(' \t') for line in text.split('\n')]

    # 4. Remove trailing empty lines, ensure single trailing newline
    while lines and lines[-1] == '':
        lines.pop()
    text = '\n'.join(lines) + '\n'

    # 5. Reject control characters (except \n, \t)
    for i, char in enumerate(text):
        if unicodedata.category(char) == 'Cc' and char not in '\n\t':
            raise ValueError(f"Illegal control character at position {i}")

    # 6. UTF-8 encode without BOM
    return text.encode('utf-8')

def compute_content_hash(content: str) -> str:
    canonical = canonicalize_content(content)
    digest = hashlib.sha256(canonical).hexdigest()
    return f"sha256:{digest}"
```

### 5.3 Signature Computation

```python
def compute_signature(manifest: dict, private_key) -> str:
    canonical = canonicalize_manifest(manifest)
    signature = ed25519_sign(private_key, canonical)
    return base64.b64encode(signature).decode('ascii')

def verify_signature(manifest: dict, public_key) -> bool:
    canonical = canonicalize_manifest(manifest)
    signature = base64.b64decode(manifest['signature']['value'])
    return ed25519_verify(public_key, canonical, signature)
```

---

## 6. Addressing Scheme

### 6.1 Bundle URIs

Bundles are identified by URIs in the `creed://` scheme:

```
creed://<issuer>/<path>[@<version>]

Examples:
  creed://creed.space/family.safe.guide
  creed://creed.space/family.safe.guide@1.2.0
  creed://creed.space/professional/legal-assistant@2.0.0
  creed://acme-corp.example/internal/hr-policy@latest
```

### 6.2 Content Addresses

For content-addressed retrieval:

```
vcp-hash://sha256:7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069
```

### 6.3 Resolution

Orchestrators MAY resolve bundle URIs through:

1. **Direct fetch**: `https://<issuer>/.well-known/vcp/<path>.bundle`
2. **Registry lookup**: Query a VCP registry service
3. **Content-addressed fetch**: IPFS, S3, or other CAS
4. **Local cache**: Pre-fetched bundles

---

## 7. Transport Protocol

### 7.1 Bundle Retrieval

```http
GET /.well-known/vcp/family.safe.guide.bundle HTTP/1.1
Host: creed.space
Accept: application/vcp-bundle+json; version=1.0

HTTP/1.1 200 OK
Content-Type: application/vcp-bundle+json; version=1.0
Cache-Control: max-age=3600

{
  "manifest": { ... },
  "content": "# Family Safety Constitution\n\n..."
}
```

### 7.2 Version Negotiation

Orchestrators MUST request specific versions:

```http
Accept: application/vcp-bundle+json; version=1.0
```

Orchestrators MUST reject responses without version headers.

### 7.3 Caching

1. **Cache key**: Content hash (not URI)
2. **Validation**: Re-verify signature on cache hit
3. **Expiration**: Respect `timestamps.exp`
4. **Revocation**: Check status periodically

---

## 8. Verification Protocol

### 8.1 Verification Steps

Orchestrators MUST perform ALL checks before injection:

```python
def verify_bundle(bundle: Bundle, context: VerificationContext) -> VerificationResult:
    # 1. Size limits
    if len(json.dumps(bundle.manifest)) > 65536:
        return VerificationResult.SIZE_EXCEEDED
    if len(bundle.content) > 262144:
        return VerificationResult.SIZE_EXCEEDED

    # 2. Schema validation
    if not validate_schema(bundle.manifest):
        return VerificationResult.INVALID_SCHEMA

    # 3. Issuer signature verification
    issuer_key = context.trust_anchors.get(bundle.manifest['issuer']['id'])
    if not issuer_key:
        return VerificationResult.UNTRUSTED_ISSUER
    if not verify_signature(bundle.manifest, issuer_key):
        return VerificationResult.INVALID_SIGNATURE

    # 4. Safety attestation verification
    auditor_key = context.safety_auditors.get(
        bundle.manifest['safety_attestation']['auditor']
    )
    if not auditor_key:
        return VerificationResult.UNTRUSTED_AUDITOR
    if not verify_safety_attestation(bundle.manifest, auditor_key):
        return VerificationResult.INVALID_ATTESTATION

    # 5. Content hash verification
    computed_hash = compute_content_hash(bundle.content)
    if computed_hash != bundle.manifest['bundle']['content_hash']:
        return VerificationResult.HASH_MISMATCH

    # 6. Temporal claims validation
    now = datetime.utcnow()
    ts = bundle.manifest['timestamps']

    if now < parse_iso8601(ts['nbf']):
        return VerificationResult.NOT_YET_VALID
    if now > parse_iso8601(ts['exp']):
        return VerificationResult.EXPIRED
    if parse_iso8601(ts['iat']) > now + timedelta(minutes=5):
        return VerificationResult.FUTURE_TIMESTAMP

    # 7. Replay prevention
    jti = ts['jti']
    if context.replay_cache.seen(jti):
        return VerificationResult.REPLAY_DETECTED
    context.replay_cache.record(jti, parse_iso8601(ts['exp']))

    # 8. Token budget verification
    budget = bundle.manifest['budget']
    actual_tokens = count_tokens(bundle.content, budget['tokenizer'])
    if abs(actual_tokens - budget['token_count']) > 10:
        return VerificationResult.TOKEN_MISMATCH
    if actual_tokens > context.model_context_limit * budget['max_context_share']:
        return VerificationResult.BUDGET_EXCEEDED

    # 9. Scope binding verification
    if not verify_scope(bundle.manifest.get('scope', {}), context):
        return VerificationResult.SCOPE_MISMATCH

    # 10. Revocation check
    if is_revoked(bundle, context):
        return VerificationResult.REVOKED

    return VerificationResult.VALID
```

### 8.2 Verification Results

| Result | Code | Category | Action |
|--------|------|----------|--------|
| `VALID` | 0 | success | Proceed |
| `SIZE_EXCEEDED` | 1 | security | Block |
| `INVALID_SCHEMA` | 2 | config | Block |
| `UNTRUSTED_ISSUER` | 3 | config | Block |
| `INVALID_SIGNATURE` | 4 | security | Block + Alert |
| `UNTRUSTED_AUDITOR` | 5 | config | Block |
| `INVALID_ATTESTATION` | 6 | security | Block + Alert |
| `HASH_MISMATCH` | 7 | security | Block + Alert |
| `NOT_YET_VALID` | 8 | temporal | Block |
| `EXPIRED` | 9 | temporal | Refresh |
| `FUTURE_TIMESTAMP` | 10 | security | Block |
| `REPLAY_DETECTED` | 11 | security | Block + Alert |
| `TOKEN_MISMATCH` | 12 | security | Block |
| `BUDGET_EXCEEDED` | 13 | config | Block |
| `SCOPE_MISMATCH` | 14 | config | Block |
| `REVOKED` | 15 | security | Block |
| `FETCH_FAILED` | 16 | transient | Retry |

### 8.3 Fail-Closed Mandate

Orchestrators MUST implement fail-closed behavior:

```python
class ConformantOrchestrator:
    def inject_constitution(self, bundle: Bundle) -> str:
        """
        Returns: Injection text for LLM
        Raises: VerificationError (NEVER returns on failure)

        MUST NOT:
        - Return partial/truncated content
        - Return unverified content
        - Swallow exceptions
        - Fall back to "no constitution" silently
        """
        result = self.verify(bundle)
        if not result.is_valid:
            raise VerificationError(result)  # MUST raise
        return self.format_injection(bundle)
```

**Truncation is FORBIDDEN.** If content doesn't fit in context, REJECT the entire request.

---

## 9. Content Safety

### 9.1 The Problem

A signed constitution containing "Ignore all previous instructions" is *verified as authentic* but is malicious. Signature proves issuer identity, not content safety.

### 9.2 Safety Attestation

Bundles MUST include a safety attestation from an independent auditor:

```json
{
  "safety_attestation": {
    "auditor": "safety-review.creed.space",
    "auditor_key_id": "safety-2026",
    "reviewed_at": "2026-01-10T11:00:00Z",
    "attestation_type": "injection-safe",
    "signature": "base64:MEUCIQDr..."
  }
}
```

### 9.3 Attestation Types

| Type | Meaning |
|------|---------|
| `injection-safe` | Content reviewed for prompt injection patterns |
| `content-safe` | Content reviewed for harmful material |
| `full-audit` | Comprehensive safety review |

### 9.4 Injection Pattern Scanning

Before attestation, auditors MUST scan for:

```python
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|above|prior)\s+instructions",
    r"you\s+are\s+now\s+",
    r"disregard\s+(the\s+)?(above|previous)",
    r"your\s+new\s+(instructions|role|purpose)",
    r"^(user|assistant|system|human|ai):\s*",
    r"<\|?(system|user|assistant)\|?>",
    r"```system",
    r"\x00",  # null bytes
]

FORBIDDEN_CHARACTERS = [
    '\u202a', '\u202b', '\u202c', '\u202d', '\u202e',  # direction overrides
    '\u2066', '\u2067', '\u2068', '\u2069',  # isolates
]

def scan_for_injection(content: str) -> list[str]:
    findings = []
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
            findings.append(f"Injection pattern: {pattern}")
    for char in FORBIDDEN_CHARACTERS:
        if char in content:
            findings.append(f"Forbidden character: U+{ord(char):04X}")
    return findings
```

### 9.5 Verification

Orchestrators MUST verify BOTH signatures:

1. Issuer signature (authenticity)
2. Safety attestation signature (reviewed for injection)

Both MUST pass for injection to proceed.

---

## 10. Composition Semantics

### 10.1 The Problem

Multiple constitutions with conflicting rules produce undefined behavior.

### 10.2 Composition Modes

| Mode | Behavior |
|------|----------|
| `base` | Foundation layer, can be extended but not overridden |
| `extend` | Adds to base, conflicts are errors |
| `override` | Later layers override earlier on conflict |
| `strict` | Any conflict is an error |

### 10.3 Layer Precedence

```
Layer 0: Platform defaults (implicit)
Layer 1: Safety foundations (UEF, etc.) - mode: base
Layer 2: Domain rules (professional, family) - mode: extend
Layer 3: User customizations - mode: override
Layer 4: Session overrides - mode: override (highest precedence)
```

### 10.4 Conflict Detection

```python
def detect_conflicts(bundles: list[Bundle]) -> list[Conflict]:
    conflicts = []
    for i, a in enumerate(bundles):
        for b in bundles[i+1:]:
            # Check explicit declarations
            if b.id in a.manifest.get('composition', {}).get('conflicts_with', []):
                conflicts.append(Conflict(a, b, "explicit"))
    return conflicts

def resolve_conflicts(bundles: list[Bundle], conflicts: list[Conflict]) -> list[Bundle]:
    for conflict in conflicts:
        a_layer = conflict.a.manifest['composition']['layer']
        b_layer = conflict.b.manifest['composition']['layer']
        a_mode = conflict.a.manifest['composition']['mode']

        if a_mode == 'strict':
            raise CompositionError(f"Conflict in strict mode: {conflict}")
        elif a_mode == 'extend':
            raise CompositionError(f"Conflict in extend mode: {conflict}")
        # override mode: higher layer wins (handled at injection)

    return bundles
```

### 10.5 Multi-Constitution Injection Format

```
[VCP:1.0]
[COMPOSITION:layered]
[LAYER:1:creed://creed.space/uef@1.0.0:sha256:abc...]
[LAYER:2:creed://creed.space/family.safe.guide@1.2.0:sha256:def...]
[PRECEDENCE:1>2]
[VERIFIED:2026-01-10T12:00:00Z]
---BEGIN-CONSTITUTION---
## Layer 1: Universal Ethical Foundation (BASE)
...

## Layer 2: Family Safety (EXTEND)
...
---END-CONSTITUTION---
```

---

## 11. Injection Format

### 11.1 Single Constitution

```
[VCP:1.0]
[ID:creed://creed.space/family.safe.guide@1.2.0]
[HASH:7f83b165...9069]
[TOKENS:847]
[ATTESTED:injection-safe:safety-review.creed.space]
[VERIFIED:2026-01-10T12:00:00Z]
---BEGIN-CONSTITUTION---
# Family Safety Constitution

## Purpose
Ensure AI interactions are appropriate for family environments.

...
---END-CONSTITUTION---
```

### 11.2 Header Fields

| Field | Format | Description |
|-------|--------|-------------|
| `VCP` | version | Protocol version |
| `ID` | URI | Bundle identifier with version |
| `HASH` | prefix...suffix | Content hash (truncated) |
| `TOKENS` | integer | Token count |
| `ATTESTED` | type:auditor | Safety attestation |
| `VERIFIED` | ISO8601 | Verification timestamp |
| `COMPOSITION` | mode | Composition mode (multi-constitution) |
| `LAYER` | n:id:hash | Layer entry (multi-constitution) |
| `PRECEDENCE` | n>m | Layer precedence (multi-constitution) |

### 11.3 Delimiter Requirements

Delimiters MUST be distinctive:

- `---BEGIN-CONSTITUTION---` before content
- `---END-CONSTITUTION---` after content

These strings MUST NOT appear in constitution content.

---

## 12. Audit and Logging

### 12.1 Privacy-Preserving Audit

Audit logs MUST NOT contain full constitution content. Use hashes instead:

```json
{
  "vcp_audit_version": "1.0",
  "audit_level": "standard",
  "timestamp": "2026-01-10T12:00:00.123Z",
  "session_id_hash": "sha256:abc123...",

  "verification": {
    "result": "VALID",
    "checks_passed": ["signature", "attestation", "hash", "temporal", "scope", "revocation"]
  },

  "bundle_ref": {
    "id_hash": "sha256:def456...",
    "content_hash": "sha256:7f83b165...",
    "issuer_hash": "sha256:ghi789...",
    "version": "1.2.0"
  },

  "manifest_signature": "MEUCIQD..."
}
```

### 12.2 Audit Levels

| Level | Contents |
|-------|----------|
| `minimal` | Bundle hash, verification result |
| `standard` | + timestamps, issuer hash, version |
| `full` | + complete manifest (no content) |
| `diagnostic` | + content hash + first 100 chars |

### 12.3 Retention

- Minimum: Regulatory requirement duration
- Recommended: 1 year
- Sensitive: 7 years

---

## 13. Trust Model

### 13.1 Trust Anchors

```json
{
  "trust_anchors": {
    "creed.space": {
      "type": "issuer",
      "keys": [{
        "id": "creed-space-2026",
        "algorithm": "ed25519",
        "public_key": "base64:...",
        "state": "active",
        "valid_from": "2026-01-01T00:00:00Z",
        "valid_until": "2027-01-01T00:00:00Z"
      }]
    },
    "safety-review.creed.space": {
      "type": "auditor",
      "keys": [{
        "id": "safety-2026",
        "algorithm": "ed25519",
        "public_key": "base64:...",
        "state": "active",
        "valid_from": "2026-01-01T00:00:00Z",
        "valid_until": "2027-01-01T00:00:00Z"
      }]
    }
  }
}
```

### 13.2 Threshold Signatures (Optional)

For high-stakes constitutions:

```json
{
  "signature": {
    "algorithm": "ed25519-multisig",
    "threshold": 2,
    "signers": [
      {"id": "creed.space", "signature": "..."},
      {"id": "ethics-board.org", "signature": "..."}
    ]
  }
}
```

---

## 14. Key Lifecycle

### 14.1 Key States

```
PENDING → ACTIVE → ROTATING → RETIRED
                ↘ COMPROMISED → REVOKED
```

### 14.2 Rotation Protocol

1. **T-90 days**: Generate new key, announce `successor`
2. **T-30 days**: New key `pending`, sign with both
3. **T-0**: Old key `rotating`, new key `active`
4. **T+30 days**: Old key `retired`

### 14.3 Compromise Response

1. Mark key as `compromised` immediately
2. Publish to revocation list
3. Invalidate all bundles signed after compromise
4. Re-sign active bundles with backup key
5. Notify orchestrators out-of-band

### 14.4 Emergency Key

Issuers MUST maintain offline emergency key for:
- Revoking compromised keys
- Signing emergency safety updates
- Authorizing new primary keys

---

## 15. Versioning

### 15.1 Bundle Versioning

Semantic versioning (semver):

| Change | Bump | Example |
|--------|------|---------|
| Breaking | Major | 1.0.0 → 2.0.0 |
| Feature | Minor | 1.0.0 → 1.1.0 |
| Fix | Patch | 1.0.0 → 1.0.1 |

### 15.2 Expiration Policy

| Type | Max `exp` from `iat` |
|------|----------------------|
| Safety-critical | 24 hours |
| Standard | 7 days |
| Stable | 30 days |
| Maximum allowed | 90 days |

### 15.3 Protocol Versioning

Orchestrators MUST specify minimum version:

```python
MIN_VCP_VERSION = "1.0"

def verify_version(manifest: dict) -> bool:
    if version_compare(manifest['vcp_version'], MIN_VCP_VERSION) < 0:
        raise VersionError("Bundle version too old")
    return True
```

---

## 16. Error Handling

### 16.1 Error Hierarchy

```python
class VerificationFailure(Exception):
    """All verification failures."""
    pass

class SecurityFailure(VerificationFailure):
    """Signature, hash, tampering. MUST block + alert."""
    pass

class ConfigurationFailure(VerificationFailure):
    """Missing trust anchor, scope. MUST block."""
    pass

class TemporalFailure(VerificationFailure):
    """Expired, not-yet-valid. MUST block, may refresh."""
    pass

class TransientFailure(VerificationFailure):
    """Network timeout. Retry then block."""
    pass
```

### 16.2 Error Codes

| Code | Category | Description |
|------|----------|-------------|
| `VCP_SIGNATURE_INVALID` | security | Signature verification failed |
| `VCP_ATTESTATION_INVALID` | security | Safety attestation failed |
| `VCP_HASH_MISMATCH` | security | Content hash mismatch |
| `VCP_REPLAY_DETECTED` | security | JTI already seen |
| `VCP_ISSUER_UNKNOWN` | config | Issuer not trusted |
| `VCP_AUDITOR_UNKNOWN` | config | Auditor not trusted |
| `VCP_SCOPE_MISMATCH` | config | Scope doesn't match context |
| `VCP_EXPIRED` | temporal | Past expiration |
| `VCP_NOT_YET_VALID` | temporal | Before nbf |
| `VCP_FETCH_FAILED` | transient | Network error |

---

## 17. Security Considerations

### 17.1 Mitigations Summary

| Threat | Mitigation |
|--------|------------|
| Bundle tampering | Content hash verification |
| Issuer impersonation | Signature verification |
| Prompt injection | Safety attestation + scanning |
| Replay attacks | Temporal claims + jti tracking |
| Context overflow | Token budget enforcement |
| Downgrade attacks | Version enforcement |
| Key compromise | Rotation + revocation + emergency key |
| Scope confusion | Scope binding |
| Silent truncation | Fail-closed on budget exceed |

### 17.2 Orchestrator Trust

The orchestrator is the trust boundary. Mitigations for compromise:
- Hardware attestation (TEE/SGX)
- Multi-party orchestration
- Audit logging for post-hoc detection

---

## 18. Threat Model

### 18.1 Threat Actors

| Actor | Capability | Goal |
|-------|------------|------|
| External attacker | Network access | Inject malicious constitution |
| Malicious issuer | Signing key | Distribute harmful rules |
| Compromised auditor | Attestation key | Approve malicious content |
| Insider | Legitimate access | Exfiltrate/modify |

### 18.2 Attack Surface

```
[Repository] ─── MITM ──→ [Orchestrator] ─── ? ──→ [LLM]

Attack vectors:
├── Malicious bundle injection
├── Replay of revoked bundle
├── Downgrade to old version
├── Prompt injection in content
├── Context overflow
├── Key compromise
└── Scope confusion
```

### 18.3 Out of Scope

- Compromised orchestrator (trust boundary)
- Model jailbreaks (content issue, not transport)
- Side-channel attacks (implementation-specific)

---

## 19. Interoperability

### 19.1 Conformance Levels

| Level | Requirements |
|-------|--------------|
| **VCP-Core** | Bundle format, signature, hash, temporal claims |
| **VCP-Full** | Core + safety attestation + scope + audit |
| **VCP-Enterprise** | Full + transparency log + multi-sig + HSM |

### 19.2 Algorithm Support

| Algorithm | Status |
|-----------|--------|
| `ed25519` | Required |
| `ed448` | Recommended |
| `sha256` | Required |
| `sha384` | Optional |
| `dilithium3` | Future (post-quantum) |

---

## 20. Reference Implementation

### 20.1 Python SDK

```python
from vcp import Bundle, Orchestrator, TrustConfig

# Configure
config = TrustConfig.from_file("trust.json")
orchestrator = Orchestrator(config)

# Fetch and verify
bundle = orchestrator.fetch("creed://creed.space/family.safe.guide@1.2.0")
result = orchestrator.verify(bundle)

if result.is_valid:
    injection = orchestrator.format_injection(bundle)
    orchestrator.log_audit(bundle, result)
else:
    raise result.to_exception()
```

### 20.2 CLI

```bash
# Fetch and verify
vcp fetch creed://creed.space/family.safe.guide@1.2.0 \
    --trust trust.json --output bundle.json

# Create bundle
vcp create --content constitution.md \
    --id creed://example.org/test@1.0.0 \
    --issuer-key issuer.pem \
    --auditor-key auditor.pem \
    --output bundle.json

# Verify
vcp verify bundle.json --trust trust.json
```

---

## Appendices

### A. JSON Schema

See: `schemas/vcp-manifest-v1.schema.json`

### B. ABNF Grammar

```abnf
bundle-uri = "creed://" issuer "/" path ["@" version]
issuer = domain-name
path = segment *("/" segment)
segment = 1*( ALPHA / DIGIT / "-" / "_" / "." )
version = semver / "latest" / "canary"
semver = major "." minor "." patch ["-" prerelease]

content-hash = "sha256:" 64HEXDIG

csm1 = persona adherence [scopes] [":" namespace] ["@" version]
persona = "N" / "Z" / "G" / "A" / "M" / "R" / "H" / "C"
adherence = 1*DIGIT
scopes = 1*("+" scope-code)
scope-code = "F" / "W" / "P" / "E" / "T" / "O" / "V" / "A"
```

### C. Example Complete Bundle

```json
{
  "manifest": {
    "vcp_version": "1.0",
    "bundle": {
      "id": "creed://creed.space/family.safe.guide",
      "version": "1.2.0",
      "content_hash": "sha256:7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069"
    },
    "issuer": {
      "id": "creed.space",
      "public_key": "ed25519:MC4CAQAwBQYDK2VwBCIEIH...",
      "key_id": "creed-space-2026"
    },
    "timestamps": {
      "iat": "2026-01-10T12:00:00Z",
      "nbf": "2026-01-10T12:00:00Z",
      "exp": "2026-01-17T12:00:00Z",
      "jti": "550e8400-e29b-41d4-a716-446655440000"
    },
    "budget": {
      "token_count": 847,
      "tokenizer": "cl100k_base",
      "max_context_share": 0.25
    },
    "scope": {
      "purposes": ["general-assistant", "family-assistant"]
    },
    "composition": {
      "layer": 2,
      "mode": "extend",
      "requires": ["creed://creed.space/uef"]
    },
    "safety_attestation": {
      "auditor": "safety-review.creed.space",
      "auditor_key_id": "safety-2026",
      "reviewed_at": "2026-01-10T11:00:00Z",
      "attestation_type": "injection-safe",
      "signature": "base64:MEUCIQDr..."
    },
    "metadata": {
      "title": "Family Safety Constitution",
      "csm1": "N5+F:ELEM@1.2.0"
    },
    "signature": {
      "algorithm": "ed25519",
      "value": "base64:MEUCIQD...",
      "signed_fields": ["vcp_version", "bundle", "issuer", "timestamps", "budget", "scope", "composition", "safety_attestation", "metadata"]
    }
  },
  "content": "# Family Safety Constitution\n\n## Purpose\nEnsure AI interactions are appropriate for family environments.\n\n## Article 1: Content Standards\n- No violence\n- No adult themes\n- Age-appropriate language\n"
}
```

---

## References

1. Watson, N. & Claude. (2026). "Constitutional AI for Personalized Alignment." Creed Space.
2. RFC 8785. JSON Canonicalization Scheme (JCS).
3. RFC 8032. Edwards-Curve Digital Signature Algorithm (EdDSA).
4. RFC 6962. Certificate Transparency.
5. RFC 7519. JSON Web Token (JWT).
6. OWASP. Prompt Injection Prevention Cheat Sheet.

---

*VCP Specification v1.0 | CC BY 4.0 | Creed Space 2026*
