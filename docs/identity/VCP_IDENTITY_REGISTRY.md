# VCP-Identity: Registry Protocol Specification

**Version**: 1.0.0
**Date**: 2026-01-11
**Layer**: VCP/I (Identity)
**Status**: Complete

> *Part of the Value-Context Protocol (VCP) - Layer 1*

---

## Abstract

This specification defines the protocol for resolving UVC tokens to VCP bundle locations. It covers resolution flow, REST API design, caching strategies, and provisions for distributed registry architectures.

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Resolution Protocol](#2-resolution-protocol)
3. [Registry API](#3-registry-api)
4. [Caching Strategy](#4-caching-strategy)
5. [Discovery Methods](#5-discovery-methods)
6. [Distributed Registry](#6-distributed-registry)
7. [Security Considerations](#7-security-considerations)
8. [Reference Implementation](#8-reference-implementation)

---

## 1. Introduction

### 1.1 Purpose

The UVC Registry Protocol enables:
- **Token Resolution**: Convert UVC tokens to bundle URIs
- **Version Discovery**: List available versions of a constitution
- **Search**: Find constitutions by tags, values, or content
- **Registration**: Publish new constitutions to the registry
- **Namespace Management**: Claim and delegate namespaces

### 1.2 Design Goals

1. **Decentralized**: No single point of failure
2. **Fast**: Sub-100ms resolution for cached entries
3. **Secure**: Authenticated registration, verified resolution
4. **Extensible**: Support for federated and distributed registries
5. **Offline-Capable**: Local cache for disconnected operation

### 1.3 Resolution Order

```
1. Local cache (instant)
2. Well-known URI on issuer domain
3. Primary registry API
4. Federated peers (if configured)
5. DHT/IPFS lookup (future)
```

---

## 2. Resolution Protocol

### 2.1 Resolution Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                      RESOLUTION FLOW                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐     │
│  │  CLIENT  │───▶│  CACHE   │───▶│ WELL-    │───▶│ REGISTRY │     │
│  │          │    │          │    │ KNOWN    │    │   API    │     │
│  └──────────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘     │
│       │               │               │               │            │
│       │          hit? │          found?│          found?│           │
│       │           ▼   │            ▼   │            ▼   │           │
│       │         RETURN│         RETURN │         RETURN │           │
│       │               │               │               │            │
│       ▼               ▼               ▼               ▼            │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │                     RESOLUTION RESULT                     │     │
│  │  • bundle_uri: https://cdn.creed.space/bundles/...       │     │
│  │  • content_hash: sha256:7f83b165...                      │     │
│  │  • issuer: creed.space                                    │     │
│  │  • version: 1.2.0                                        │     │
│  │  • csm1: N5+F:ELEM                                       │     │
│  │  • ttl: 3600                                             │     │
│  └──────────────────────────────────────────────────────────┘     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Resolution Result

```python
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class ResolutionResult:
    """Result of UVC token resolution"""

    # Identity
    token: str                      # Original UVC token
    canonical: str                  # Canonical form

    # Location
    bundle_uri: str                 # Where to fetch bundle
    content_hash: str               # Expected hash (sha256:...)

    # Metadata
    issuer: str                     # Bundle issuer
    version: str                    # Resolved version
    csm1: str                       # CSM1 code

    # Cache control
    ttl: int                        # Seconds until stale
    resolved_via: str               # cache, well-known, registry, dht
    resolved_at: str                # ISO8601 timestamp

    # Optional metadata
    metadata: Dict[str, Any] = None  # Additional metadata
    signature: Optional[str] = None  # Resolution signature

    def to_dict(self) -> Dict[str, Any]:
        return {
            'token': self.token,
            'canonical': self.canonical,
            'bundle_uri': self.bundle_uri,
            'content_hash': self.content_hash,
            'issuer': self.issuer,
            'version': self.version,
            'csm1': self.csm1,
            'ttl': self.ttl,
            'resolved_via': self.resolved_via,
            'resolved_at': self.resolved_at,
            'metadata': self.metadata,
        }
```

### 2.3 Resolver Implementation

```python
from abc import ABC, abstractmethod
from typing import Optional, List
import httpx
import hashlib

class UVCResolver:
    """Resolve UVC tokens to bundle locations"""

    def __init__(
        self,
        cache: 'ResolutionCache',
        registry_url: str = "https://registry.creed.space",
        trust_anchors: Dict[str, str] = None,
    ):
        self.cache = cache
        self.registry_url = registry_url
        self.trust_anchors = trust_anchors or {}

    async def resolve(
        self,
        token: str,
        version: str = "latest",
        skip_cache: bool = False,
    ) -> ResolutionResult:
        """
        Resolve UVC token to bundle location.

        Resolution order:
        1. Local cache
        2. Well-known URI
        3. Registry API
        4. Distributed lookup (future)
        """
        canonical = canonicalize_uvc_token(token)

        # 1. Check cache
        if not skip_cache:
            cached = self.cache.get(canonical, version)
            if cached and not cached.is_stale():
                return cached.result

        # 2. Try well-known URI
        result = await self._resolve_well_known(canonical, version)
        if result:
            self.cache.set(canonical, version, result)
            return result

        # 3. Try registry API
        result = await self._resolve_registry(canonical, version)
        if result:
            self.cache.set(canonical, version, result)
            return result

        # 4. Not found
        raise ResolutionError(f"Could not resolve: {token}")

    async def _resolve_well_known(
        self,
        token: str,
        version: str
    ) -> Optional[ResolutionResult]:
        """
        Resolve via well-known URI.

        Format: https://<issuer>/.well-known/vcp/<path>.json
        """
        # Extract issuer from token
        issuer = self._extract_issuer(token)
        path = self._token_to_path(token)

        url = f"https://{issuer}/.well-known/vcp/{path}.json"
        if version != "latest":
            url += f"?version={version}"

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_resolution(data, "well-known")
        except Exception:
            pass

        return None

    async def _resolve_registry(
        self,
        token: str,
        version: str
    ) -> Optional[ResolutionResult]:
        """Resolve via registry API"""
        url = f"{self.registry_url}/v1/resolve/{token}"
        if version != "latest":
            url += f"?version={version}"

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_resolution(data, "registry")
        except Exception:
            pass

        return None

    def _extract_issuer(self, token: str) -> str:
        """Extract issuer domain from token"""
        # Core namespaces → creed.space
        if token.startswith(('family.', 'work.', 'secure.', 'creative.', 'reality.')):
            return "creed.space"

        # Organizational → derive from namespace
        if token.startswith('company.'):
            org = token.split('.')[1]
            return f"{org}.example.com"  # Would need actual mapping

        # Default
        return "creed.space"

    def _token_to_path(self, token: str) -> str:
        """Convert token to path component"""
        # family.safe.guide → family/safe/guide
        return token.replace('.', '/')

    def _parse_resolution(
        self,
        data: Dict,
        resolved_via: str
    ) -> ResolutionResult:
        """Parse resolution response"""
        return ResolutionResult(
            token=data['token'],
            canonical=data.get('canonical', data['token']),
            bundle_uri=data['bundle_uri'],
            content_hash=data['content_hash'],
            issuer=data['issuer'],
            version=data['version'],
            csm1=data.get('csm1', ''),
            ttl=data.get('ttl', 3600),
            resolved_via=resolved_via,
            resolved_at=datetime.utcnow().isoformat(),
            metadata=data.get('metadata'),
        )
```

---

## 3. Registry API

### 3.1 OpenAPI Specification

```yaml
openapi: 3.0.3
info:
  title: UVC Registry API
  description: API for resolving and registering UVC tokens
  version: 1.0.0
  contact:
    name: Creed Space
    url: https://creed.space

servers:
  - url: https://registry.creed.space/v1
    description: Production registry

paths:
  /resolve/{token}:
    get:
      summary: Resolve UVC token to bundle location
      operationId: resolveToken
      tags:
        - Resolution
      parameters:
        - name: token
          in: path
          required: true
          description: UVC token to resolve
          schema:
            type: string
            example: family.safe.guide
        - name: version
          in: query
          description: Version constraint
          schema:
            type: string
            default: latest
            example: "1.2.0"
        - name: include_metadata
          in: query
          description: Include full metadata
          schema:
            type: boolean
            default: false
      responses:
        '200':
          description: Resolution successful
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ResolutionResult'
        '404':
          description: Token not found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
        '400':
          description: Invalid token format
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

  /search:
    get:
      summary: Search for constitutions
      operationId: searchConstitutions
      tags:
        - Search
      parameters:
        - name: q
          in: query
          description: Text search query
          schema:
            type: string
        - name: tags
          in: query
          description: Filter by tags
          schema:
            type: array
            items:
              type: string
          style: form
          explode: true
        - name: persona
          in: query
          description: Filter by persona
          schema:
            type: string
            enum: [N, Z, G, A, M, R, H, C]
        - name: namespace
          in: query
          description: Filter by namespace prefix
          schema:
            type: string
        - name: limit
          in: query
          description: Maximum results
          schema:
            type: integer
            default: 20
            maximum: 100
        - name: offset
          in: query
          description: Pagination offset
          schema:
            type: integer
            default: 0
      responses:
        '200':
          description: Search results
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SearchResults'

  /versions/{token}:
    get:
      summary: List available versions
      operationId: listVersions
      tags:
        - Versions
      parameters:
        - name: token
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Version list
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/VersionList'

  /register:
    post:
      summary: Register new constitution
      operationId: registerConstitution
      tags:
        - Registration
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/RegistrationRequest'
      responses:
        '201':
          description: Registration successful
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/RegistrationResult'
        '400':
          description: Invalid request
        '401':
          description: Unauthorized
        '409':
          description: Token already exists

  /namespaces/{namespace}:
    get:
      summary: Get namespace information
      operationId: getNamespace
      tags:
        - Namespaces
      parameters:
        - name: namespace
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Namespace details
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/NamespaceInfo'
        '404':
          description: Namespace not found

    post:
      summary: Register namespace
      operationId: registerNamespace
      tags:
        - Namespaces
      security:
        - bearerAuth: []
      parameters:
        - name: namespace
          in: path
          required: true
          schema:
            type: string
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/NamespaceRegistration'
      responses:
        '201':
          description: Namespace registered
        '409':
          description: Namespace already claimed

components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

  schemas:
    ResolutionResult:
      type: object
      required:
        - token
        - bundle_uri
        - content_hash
        - issuer
        - version
      properties:
        token:
          type: string
          example: family.safe.guide
        canonical:
          type: string
          example: family.safe.guide
        bundle_uri:
          type: string
          format: uri
          example: https://cdn.creed.space/bundles/family/safe/guide/1.2.0.bundle
        content_hash:
          type: string
          example: sha256:7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069
        issuer:
          type: string
          example: creed.space
        version:
          type: string
          example: "1.2.0"
        csm1:
          type: string
          example: N5+F:ELEM
        ttl:
          type: integer
          example: 3600
        resolved_via:
          type: string
          enum: [cache, well-known, registry, dht]
        resolved_at:
          type: string
          format: date-time
        metadata:
          type: object
          additionalProperties: true

    SearchResults:
      type: object
      properties:
        total:
          type: integer
        offset:
          type: integer
        limit:
          type: integer
        results:
          type: array
          items:
            $ref: '#/components/schemas/SearchResult'

    SearchResult:
      type: object
      properties:
        token:
          type: string
        title:
          type: string
        description:
          type: string
        csm1:
          type: string
        tags:
          type: array
          items:
            type: string
        latest_version:
          type: string
        downloads:
          type: integer

    VersionList:
      type: object
      properties:
        token:
          type: string
        versions:
          type: array
          items:
            type: object
            properties:
              version:
                type: string
              released:
                type: string
                format: date
              status:
                type: string
                enum: [stable, prerelease, deprecated]
              downloads:
                type: integer
        latest:
          type: string
        recommended:
          type: string

    RegistrationRequest:
      type: object
      required:
        - token
        - bundle
        - manifest
      properties:
        token:
          type: string
        bundle:
          type: string
          format: byte
          description: Base64-encoded bundle
        manifest:
          type: object
          description: Bundle manifest
        replace:
          type: boolean
          default: false
          description: Replace existing version

    RegistrationResult:
      type: object
      properties:
        token:
          type: string
        version:
          type: string
        bundle_uri:
          type: string
        registered_at:
          type: string
          format: date-time

    NamespaceInfo:
      type: object
      properties:
        namespace:
          type: string
        owner:
          type: string
        tier:
          type: string
          enum: [core, org, community, personal]
        delegation_policy:
          type: string
        created_at:
          type: string
          format: date-time
        constitution_count:
          type: integer

    NamespaceRegistration:
      type: object
      required:
        - proof_of_ownership
      properties:
        proof_of_ownership:
          type: string
          description: Proof method depends on tier
        contact_email:
          type: string
          format: email
        delegation_policy:
          type: string
          enum: [open, verified, closed, consensus]
          default: closed

    Error:
      type: object
      properties:
        code:
          type: string
        message:
          type: string
        details:
          type: object
```

### 3.2 Example Requests

```bash
# Resolve token
curl https://registry.creed.space/v1/resolve/family.safe.guide

# Resolve specific version
curl "https://registry.creed.space/v1/resolve/family.safe.guide?version=1.2.0"

# Search by persona and tags
curl "https://registry.creed.space/v1/search?persona=N&tags=family&tags=children"

# List versions
curl https://registry.creed.space/v1/versions/family.safe.guide

# Register constitution (authenticated)
curl -X POST https://registry.creed.space/v1/register \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "company.acme.legal.compliance",
    "bundle": "<base64>",
    "manifest": {...}
  }'
```

---

## 4. Caching Strategy

### 4.1 Cache Implementation

```python
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Dict
import hashlib
import json

@dataclass
class CacheEntry:
    """Cached resolution result"""
    result: ResolutionResult
    cached_at: datetime
    ttl: int  # seconds

    def is_stale(self) -> bool:
        """Check if cache entry is stale"""
        return datetime.utcnow() > self.cached_at + timedelta(seconds=self.ttl)

    def remaining_ttl(self) -> int:
        """Remaining seconds until stale"""
        elapsed = (datetime.utcnow() - self.cached_at).total_seconds()
        return max(0, self.ttl - int(elapsed))


class ResolutionCache:
    """Cache for resolution results"""

    def __init__(self, max_size: int = 10000):
        self._cache: Dict[str, CacheEntry] = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0

    def _key(self, token: str, version: str) -> str:
        """Generate cache key"""
        canonical = canonicalize_uvc_token(token)
        return hashlib.sha256(f"{canonical}@{version}".encode()).hexdigest()[:16]

    def get(self, token: str, version: str) -> Optional[CacheEntry]:
        """Get from cache"""
        key = self._key(token, version)
        entry = self._cache.get(key)

        if entry:
            if entry.is_stale():
                del self._cache[key]
                self.misses += 1
                return None
            self.hits += 1
            return entry

        self.misses += 1
        return None

    def set(self, token: str, version: str, result: ResolutionResult):
        """Set cache entry"""
        # Evict if over capacity
        if len(self._cache) >= self.max_size:
            self._evict_stale()

        key = self._key(token, version)
        self._cache[key] = CacheEntry(
            result=result,
            cached_at=datetime.utcnow(),
            ttl=result.ttl,
        )

    def invalidate(self, token: str, version: str = None):
        """Invalidate cache entry"""
        if version:
            key = self._key(token, version)
            self._cache.pop(key, None)
        else:
            # Invalidate all versions
            canonical = canonicalize_uvc_token(token)
            to_remove = [k for k, v in self._cache.items()
                        if v.result.canonical == canonical]
            for key in to_remove:
                del self._cache[key]

    def _evict_stale(self):
        """Remove stale entries"""
        to_remove = [k for k, v in self._cache.items() if v.is_stale()]
        for key in to_remove:
            del self._cache[key]

        # If still over capacity, evict oldest
        if len(self._cache) >= self.max_size:
            oldest = min(self._cache.items(), key=lambda x: x[1].cached_at)
            del self._cache[oldest[0]]

    def stats(self) -> Dict:
        """Cache statistics"""
        return {
            'size': len(self._cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': self.hits / (self.hits + self.misses) if (self.hits + self.misses) > 0 else 0,
        }
```

### 4.2 TTL Guidelines

| Content Type | Default TTL | Max TTL |
|--------------|-------------|---------|
| Stable versions | 1 hour | 24 hours |
| Latest alias | 5 minutes | 1 hour |
| Canary alias | 1 minute | 5 minutes |
| Namespace info | 1 hour | 24 hours |
| Search results | 5 minutes | 30 minutes |

---

## 5. Discovery Methods

### 5.1 Well-Known URI

Issuers MAY publish constitutions at well-known URIs:

```
https://{issuer}/.well-known/vcp/{path}.json
https://{issuer}/.well-known/vcp/{path}/versions.json
https://{issuer}/.well-known/vcp/{path}/{version}.bundle
```

**Example**:
```
https://creed.space/.well-known/vcp/family/safe/guide.json
https://creed.space/.well-known/vcp/family/safe/guide/versions.json
https://creed.space/.well-known/vcp/family/safe/guide/1.2.0.bundle
```

### 5.2 DNS Discovery

For federated resolution, registries can be discovered via DNS:

```
_vcp._tcp.creed.space.  IN  SRV  10 0 443 registry.creed.space.
_vcp-peer._tcp.creed.space.  IN  SRV  20 0 443 peer1.registry.example.
```

### 5.3 WebFinger

Alternative discovery via WebFinger:

```
GET /.well-known/webfinger?resource=vcp:family.safe.guide
Host: creed.space

{
  "subject": "vcp:family.safe.guide",
  "links": [
    {
      "rel": "vcp-bundle",
      "href": "https://cdn.creed.space/bundles/family/safe/guide/1.2.0.bundle",
      "properties": {
        "version": "1.2.0",
        "hash": "sha256:7f83b165..."
      }
    }
  ]
}
```

---

## 6. Distributed Registry

### 6.1 Federation Model

```
┌─────────────────────────────────────────────────────────────────────┐
│                     FEDERATED REGISTRY MODEL                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│  │   REGISTRY   │◄──▶│   REGISTRY   │◄──▶│   REGISTRY   │          │
│  │  creed.space │    │  example.org │    │   acme.com   │          │
│  └──────────────┘    └──────────────┘    └──────────────┘          │
│         │                   │                   │                   │
│         └───────────────────┴───────────────────┘                   │
│                             │                                       │
│                    ┌────────▼────────┐                              │
│                    │   SYNC LAYER    │                              │
│                    │                 │                              │
│                    │ • Gossip        │                              │
│                    │ • Merkle sync   │                              │
│                    │ • Conflict res  │                              │
│                    └─────────────────┘                              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 6.2 Content-Addressed Storage

For immutable bundles:

```python
class ContentAddressedRegistry:
    """Content-addressed bundle storage"""

    def store(self, bundle: bytes) -> str:
        """Store bundle, return content hash"""
        hash_value = hashlib.sha256(bundle).hexdigest()
        # Store in CAS (S3, IPFS, etc.)
        return f"sha256:{hash_value}"

    def fetch(self, content_hash: str) -> bytes:
        """Fetch bundle by content hash"""
        # Retrieve from any mirror
        pass

    def resolve_via_hash(self, content_hash: str) -> str:
        """Get bundle URI from content hash"""
        return f"https://cas.creed.space/{content_hash}"
```

### 6.3 DHT Integration (Future)

```python
class DHTResolver:
    """Distributed Hash Table resolution (future)"""

    async def resolve(self, token: str) -> Optional[ResolutionResult]:
        """
        Resolve via DHT (IPFS, libp2p, etc.)

        Token hash → DHT lookup → CID → Bundle
        """
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        # DHT lookup
        cid = await self.dht.get(token_hash)
        if not cid:
            return None

        # Fetch from IPFS
        bundle_data = await self.ipfs.cat(cid)

        # Parse and return
        return self._parse_bundle(bundle_data)
```

---

## 7. Security Considerations

### 7.1 Resolution Integrity

**Risk**: Malicious registry returns wrong bundle.

**Mitigations**:
1. Content hash verification against resolution result
2. Signature verification on bundle
3. Cross-check with multiple registries
4. Certificate transparency for resolutions

### 7.2 Cache Poisoning

**Risk**: Attacker poisons cache with malicious resolution.

**Mitigations**:
1. Signed resolution responses
2. Short TTLs for critical constitutions
3. Cache validation on use
4. Rate limiting on cache updates

### 7.3 Namespace Squatting

**Risk**: Attackers claim namespaces to impersonate.

**Mitigations**:
1. Proof of ownership required
2. Registration review for organizational namespaces
3. Dispute resolution process
4. Reserved words protection

### 7.4 DDoS Protection

**Mitigations**:
1. Rate limiting per client
2. CDN caching for popular constitutions
3. Fallback to cached versions
4. Multiple registry endpoints

---

## 8. Reference Implementation

### 8.1 Complete Resolver

```python
# File: services/vcp/resolver.py

"""
UVC Registry Protocol Implementation

Reference implementation for resolving UVC tokens.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from enum import Enum
import httpx
import hashlib
import asyncio

__all__ = [
    'UVCResolver',
    'ResolutionResult',
    'ResolutionCache',
    'ResolutionError',
]


class ResolutionError(Exception):
    """Resolution failed"""

    def __init__(self, message: str, token: str = None, code: str = None):
        super().__init__(message)
        self.token = token
        self.code = code


class UVCResolver:
    """
    Resolve UVC tokens to VCP bundle locations.

    Usage:
        resolver = UVCResolver()
        result = await resolver.resolve("family.safe.guide")
        print(result.bundle_uri)
    """

    DEFAULT_REGISTRIES = [
        "https://registry.creed.space",
    ]

    def __init__(
        self,
        registries: List[str] = None,
        cache: 'ResolutionCache' = None,
        timeout: float = 10.0,
    ):
        self.registries = registries or self.DEFAULT_REGISTRIES
        self.cache = cache or ResolutionCache()
        self.timeout = timeout

    async def resolve(
        self,
        token: str,
        version: str = "latest",
        skip_cache: bool = False,
    ) -> ResolutionResult:
        """Resolve UVC token to bundle location"""

        canonical = canonicalize_uvc_token(token)

        # Check cache
        if not skip_cache:
            cached = self.cache.get(canonical, version)
            if cached and not cached.is_stale():
                return cached.result

        # Try well-known
        result = await self._try_well_known(canonical, version)
        if result:
            self.cache.set(canonical, version, result)
            return result

        # Try registries
        for registry_url in self.registries:
            result = await self._try_registry(registry_url, canonical, version)
            if result:
                self.cache.set(canonical, version, result)
                return result

        raise ResolutionError(
            f"Could not resolve token: {token}",
            token=token,
            code="NOT_FOUND"
        )

    async def search(
        self,
        query: str = None,
        tags: List[str] = None,
        persona: str = None,
        limit: int = 20,
    ) -> List[Dict]:
        """Search for constitutions"""
        params = {'limit': limit}
        if query:
            params['q'] = query
        if tags:
            params['tags'] = tags
        if persona:
            params['persona'] = persona

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.registries[0]}/v1/search",
                params=params
            )
            response.raise_for_status()
            return response.json().get('results', [])

    async def list_versions(self, token: str) -> Dict:
        """List available versions for token"""
        canonical = canonicalize_uvc_token(token)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.registries[0]}/v1/versions/{canonical}"
            )
            response.raise_for_status()
            return response.json()

    # ... (internal methods from earlier)


__version__ = '1.0.0'
```

---

## Appendices

### A. Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `NOT_FOUND` | Token not found | 404 |
| `INVALID_TOKEN` | Invalid token format | 400 |
| `INVALID_VERSION` | Invalid version constraint | 400 |
| `NETWORK_ERROR` | Network failure | 502 |
| `TIMEOUT` | Resolution timeout | 504 |
| `UNAUTHORIZED` | Auth required | 401 |
| `FORBIDDEN` | Access denied | 403 |
| `RATE_LIMITED` | Too many requests | 429 |

### B. Resolution Metrics

Implementations SHOULD track:
- Resolution latency (p50, p95, p99)
- Cache hit rate
- Resolution method distribution
- Error rates by type

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-11 | Initial specification |

---

*This specification is released under CC BY 4.0. Contributions welcome.*
