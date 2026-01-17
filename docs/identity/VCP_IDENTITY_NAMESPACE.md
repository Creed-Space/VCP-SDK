# VCP-Identity: Namespace Governance Specification

**Version**: 1.0.0
**Date**: 2026-01-11
**Layer**: VCP/I (Identity)
**Status**: Complete

> *Part of the Value-Context Protocol (VCP) - Layer 1*

---

## Abstract

This specification defines governance rules for UVC namespaces - who can create tokens, how namespaces are registered, and delegation policies.

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Namespace Tiers](#2-namespace-tiers)
3. [Registration Protocol](#3-registration-protocol)
4. [Proof of Ownership](#4-proof-of-ownership)
5. [Delegation Rules](#5-delegation-rules)
6. [Dispute Resolution](#6-dispute-resolution)
7. [Security Considerations](#7-security-considerations)

---

## 1. Introduction

### 1.1 Purpose

Namespace governance ensures:
- **Authenticity**: Organizational namespaces belong to verified entities
- **Non-collision**: No two entities claim the same namespace
- **Accountability**: Namespace owners are contactable
- **Flexibility**: Multiple governance models for different use cases

### 1.2 Governance Principles

1. **Minimal Centralization**: Core namespaces only; everything else is delegated
2. **Proof-Based**: Registration requires verifiable proof
3. **Dispute Process**: Clear resolution for conflicts
4. **Expiration**: Namespaces require renewal to prevent squatting

---

## 2. Namespace Tiers

### 2.1 Tier Overview

| Tier | Prefixes | Governance | Registration | Example |
|------|----------|------------|--------------|---------|
| **Core** | `family`, `work`, `secure`, `creative`, `reality` | Creed Space stewardship | Reserved | `family.safe.guide` |
| **Organizational** | `company`, `school`, `ngo` | Delegated to org | Verified ownership | `company.acme.legal` |
| **Community** | `religion`, `culture`, `community` | Community consensus | Multi-stakeholder | `religion.buddhist.meditation` |
| **Personal** | `user` | Individual control | Self-service | `user.alice.personal` |

### 2.2 Core Tier

**Governance**: Creed Space maintains exclusive stewardship.

**Characteristics**:
- Reserved namespaces, not available for registration
- Universal semantics (same meaning everywhere)
- Backward compatibility guaranteed
- Governed by Creed Space advisory board

**Reserved Prefixes**:
```python
CORE_NAMESPACES = {
    'family',    # Family/child-safe contexts
    'work',      # Professional/workplace contexts
    'secure',    # Security/privacy contexts
    'creative',  # Artistic/creative contexts
    'reality',   # Factual/grounded contexts
}
```

### 2.3 Organizational Tier

**Governance**: Delegated to verified organizations.

**Registration Requirements**:
1. Domain ownership verification (DNS TXT or HTTPS)
2. Contact email at verified domain
3. Acceptance of terms of service
4. Annual renewal

**Sub-prefixes**:
| Prefix | Entity Type | Proof Type |
|--------|-------------|------------|
| `company` | For-profit business | Domain ownership |
| `school` | Educational institution | .edu domain or accreditation |
| `ngo` | Non-profit organization | 501(c)(3) or equivalent |

### 2.4 Community Tier

**Governance**: Multi-stakeholder community consensus.

**Registration Requirements**:
1. Three or more stewards (multi-sig)
2. Community charter defining governance
3. Public deliberation process
4. Annual steward rotation option

**Sub-prefixes**:
| Prefix | Scope | Governance |
|--------|-------|------------|
| `religion` | Religious traditions | Recognized religious bodies |
| `culture` | Cultural/regional | Cultural organizations |
| `community` | Interest groups | Community-defined |

### 2.5 Personal Tier

**Governance**: Individual control.

**Registration Requirements**:
1. Email verification
2. Username uniqueness check
3. Terms acceptance
4. No special characters (except `-`, `_`)

---

## 3. Registration Protocol

### 3.1 Registration Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                     REGISTRATION FLOW                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐                                                   │
│  │  REQUESTOR   │  1. Submit registration request                   │
│  └──────┬───────┘                                                   │
│         │                                                           │
│         ▼                                                           │
│  ┌──────────────┐                                                   │
│  │  REGISTRY    │  2. Validate namespace format                     │
│  │              │  3. Check availability                            │
│  │              │  4. Verify proof of ownership                     │
│  └──────┬───────┘                                                   │
│         │                                                           │
│         ▼                                                           │
│  ┌──────────────┐                                                   │
│  │ VERIFICATION │  5. DNS/email/multi-sig verification              │
│  └──────┬───────┘                                                   │
│         │                                                           │
│         ▼                                                           │
│  ┌──────────────┐                                                   │
│  │  ISSUANCE    │  6. Generate namespace key                        │
│  │              │  7. Record in registry                            │
│  │              │  8. Return credentials                            │
│  └──────────────┘                                                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 Registration Request

```python
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class NamespaceRegistrationRequest:
    """Request to register a namespace"""

    # Required
    namespace: str              # e.g., "company.acme"
    requestor_id: str           # Identity of requestor
    contact_email: str          # Contact email
    proof_type: str             # "dns", "https", "multisig", "email"
    proof_data: str             # Proof-specific data

    # Optional
    delegation_policy: str = "closed"  # "open", "verified", "closed"
    charter_url: Optional[str] = None  # For community namespaces
    stewards: list = None              # For multi-sig namespaces


@dataclass
class NamespaceRegistrationResponse:
    """Response to registration request"""

    status: str                 # "approved", "pending", "rejected"
    namespace: str
    namespace_key: Optional[str]  # Signing key for namespace
    expiry: Optional[datetime]    # Registration expiry
    renewal_url: str
    reason: Optional[str]       # If rejected
```

### 3.3 Registration API

```yaml
paths:
  /v1/namespaces/register:
    post:
      summary: Register a namespace
      requestBody:
        content:
          application/json:
            schema:
              type: object
              required:
                - namespace
                - contact_email
                - proof_type
                - proof_data
              properties:
                namespace:
                  type: string
                  example: "company.acme"
                contact_email:
                  type: string
                  format: email
                proof_type:
                  type: string
                  enum: ["dns", "https", "multisig", "email"]
                proof_data:
                  type: string
                delegation_policy:
                  type: string
                  enum: ["open", "verified", "closed", "consensus"]
                  default: "closed"
      responses:
        201:
          description: Registration approved
        202:
          description: Pending verification
        400:
          description: Invalid request
        409:
          description: Namespace already claimed
```

---

## 4. Proof of Ownership

### 4.1 DNS Verification

**For**: Organizational namespaces (`company.*`, `school.*`, `ngo.*`)

**Process**:
1. Requestor claims `company.acme`
2. Registry provides verification token: `vcp-verify=abc123xyz`
3. Requestor adds DNS TXT record: `_vcp.acme.com TXT "vcp-verify=abc123xyz"`
4. Registry verifies DNS record
5. Namespace approved

```python
import dns.resolver

class DNSVerifier:
    """Verify domain ownership via DNS TXT record"""

    def verify(self, domain: str, expected_token: str) -> bool:
        """
        Check for VCP verification TXT record.

        Looks for: _vcp.{domain} TXT "vcp-verify={token}"
        """
        try:
            answers = dns.resolver.resolve(f'_vcp.{domain}', 'TXT')
            for rdata in answers:
                txt = str(rdata).strip('"')
                if txt == f"vcp-verify={expected_token}":
                    return True
        except dns.resolver.NXDOMAIN:
            pass
        except dns.resolver.NoAnswer:
            pass
        return False
```

### 4.2 HTTPS Verification

**For**: Organizational namespaces (alternative to DNS)

**Process**:
1. Requestor claims `company.acme`
2. Registry provides verification file content
3. Requestor hosts file at: `https://acme.com/.well-known/vcp-verify.txt`
4. Registry fetches and verifies

```python
import httpx

class HTTPSVerifier:
    """Verify domain ownership via HTTPS file"""

    async def verify(self, domain: str, expected_token: str) -> bool:
        """
        Check for VCP verification file.

        Expects: https://{domain}/.well-known/vcp-verify.txt
        Content: vcp-verify={token}
        """
        url = f"https://{domain}/.well-known/vcp-verify.txt"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
                if response.status_code == 200:
                    content = response.text.strip()
                    return content == f"vcp-verify={expected_token}"
        except Exception:
            pass
        return False
```

### 4.3 Multi-Signature Verification

**For**: Community namespaces

**Process**:
1. Define steward list (minimum 3)
2. Each steward signs registration request
3. Threshold signatures verified (e.g., 3-of-5)
4. Namespace approved

```python
from dataclasses import dataclass
from typing import List

@dataclass
class MultiSigProof:
    """Multi-signature proof of community ownership"""

    stewards: List[str]         # Public keys of stewards
    threshold: int              # Required signatures
    signatures: List[str]       # Collected signatures
    message: str                # What was signed

    def is_valid(self) -> bool:
        """Check if threshold is met with valid signatures"""
        valid_count = 0
        for i, sig in enumerate(self.signatures):
            if sig and verify_signature(self.stewards[i], self.message, sig):
                valid_count += 1
        return valid_count >= self.threshold
```

### 4.4 Email Verification

**For**: Personal namespaces

**Process**:
1. User requests `user.alice`
2. Confirmation email sent to provided address
3. User clicks verification link
4. Namespace approved

---

## 5. Delegation Rules

### 5.1 Delegation Policies

| Policy | Description | Example |
|--------|-------------|---------|
| **open** | Anyone can create sub-namespaces | `community.gaming.*` |
| **verified** | Sub-namespace requires verification | `company.acme.*` |
| **closed** | Only owner can create | `user.alice.*` |
| **consensus** | Community vote required | `religion.buddhist.*` |

### 5.2 Delegation Grant

```python
@dataclass
class DelegationGrant:
    """Grant to create sub-namespaces"""

    parent_namespace: str       # e.g., "company.acme"
    child_segment: str          # e.g., "legal" (for company.acme.legal)
    grantee: str                # Who receives delegation
    policy: str                 # Delegation policy for child
    expiry: datetime
    signed_by: str              # Parent namespace key

    def full_namespace(self) -> str:
        return f"{self.parent_namespace}.{self.child_segment}"
```

### 5.3 Delegation API

```yaml
paths:
  /v1/namespaces/{namespace}/delegate:
    post:
      summary: Delegate sub-namespace
      security:
        - namespaceKey: []
      parameters:
        - name: namespace
          in: path
          required: true
          schema:
            type: string
      requestBody:
        content:
          application/json:
            schema:
              type: object
              required:
                - child_segment
                - grantee
              properties:
                child_segment:
                  type: string
                  example: "legal"
                grantee:
                  type: string
                  description: Grantee public key or email
                policy:
                  type: string
                  enum: ["open", "verified", "closed"]
                  default: "closed"
                expiry_days:
                  type: integer
                  default: 365
```

---

## 6. Dispute Resolution

### 6.1 Dispute Types

| Type | Description | Resolution |
|------|-------------|------------|
| **Squatting** | Namespace claimed by non-owner | Proof of legitimate claim |
| **Trademark** | Namespace infringes trademark | Legal documentation |
| **Abandonment** | Namespace unused, blocking others | Grace period, then release |
| **Impersonation** | Misleading namespace | Review and possible revocation |

### 6.2 Dispute Process

```
1. FILING
   - Complainant submits dispute form
   - Provides evidence of claim
   - Pays dispute filing fee (refundable if valid)

2. REVIEW
   - Registry reviews within 14 days
   - Current holder notified
   - Response period: 14 days

3. INVESTIGATION
   - Evidence from both parties reviewed
   - Third-party mediator if needed
   - Decision within 30 days

4. RESOLUTION
   - Namespace transferred, or
   - Dispute rejected, or
   - Compromise reached
```

### 6.3 Dispute API

```python
@dataclass
class DisputeRequest:
    """Request to dispute a namespace"""

    namespace: str              # Disputed namespace
    complainant: str            # Who is filing
    dispute_type: str           # squatting, trademark, etc.
    evidence: List[str]         # URLs to evidence
    claim_statement: str        # Why complainant has right
    requested_outcome: str      # What complainant wants


@dataclass
class DisputeStatus:
    """Status of a dispute"""

    dispute_id: str
    namespace: str
    status: str                 # filed, under_review, decided
    filed_date: datetime
    decision: Optional[str]
    decision_date: Optional[datetime]
```

---

## 7. Security Considerations

### 7.1 Namespace Key Security

- Keys are Ed25519 (same as VCP bundle signing)
- Key rotation supported with 30-day overlap
- Compromised keys can be revoked via email verification
- Hardware security module recommended for high-value namespaces

### 7.2 Squatting Prevention

- Annual renewal required
- Grace period before release: 90 days
- High-value namespaces may have stricter requirements
- Reserved words cannot be registered

### 7.3 Impersonation Prevention

- Organizational namespaces require domain proof
- Similar-looking namespaces may be flagged
- Unicode normalization prevents homograph attacks

---

## Appendices

### A. Reserved Words

These cannot be used as namespace segments:

```python
RESERVED_WORDS = {
    # System
    'system', 'admin', 'root', 'internal', 'api', 'test',

    # VCP-specific
    'vcp', 'uvc', 'creed', 'bundle', 'manifest',

    # Common abuse targets
    'official', 'verified', 'authentic', 'real',
}
```

### B. Namespace Expiry Policy

| Tier | Initial Term | Renewal | Grace Period |
|------|--------------|---------|--------------|
| Core | Permanent | N/A | N/A |
| Organizational | 1 year | Annual | 90 days |
| Community | 1 year | Annual | 90 days |
| Personal | Permanent | N/A | Deletion after 2 years inactivity |

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-11 | Initial specification |

---

*This specification is released under CC BY 4.0. Contributions welcome.*
