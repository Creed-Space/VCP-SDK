# UVC Naming Specification

**Version**: 1.0.0
**Date**: 2026-01-11
**Layer**: 1 (UVC - Universal Value Coding)
**Status**: Complete

---

## Abstract

This specification defines the naming format for Universal Value Codes (UVC) - unique, human-readable identifiers for constitutional values and behavioral rules. UVC tokens provide a portable, namespace-governed addressing scheme that works across implementations and organizations.

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Token Format](#2-token-format)
3. [Formal Grammar](#3-formal-grammar)
4. [Validation Rules](#4-validation-rules)
5. [Canonicalization](#5-canonicalization)
6. [Examples](#6-examples)
7. [Security Considerations](#7-security-considerations)
8. [Reference Implementation](#8-reference-implementation)

---

## 1. Introduction

### 1.1 Purpose

UVC tokens serve as:
- **Unique identifiers** for constitutional values
- **Human-readable names** for discoverability
- **Namespace-governed** addresses for organizational control
- **Version-aware** references for evolution

### 1.2 Design Goals

1. **Readable**: `family.safe.guide` is self-documenting
2. **Hierarchical**: Supports organizational namespaces
3. **Portable**: Works across implementations
4. **Versionable**: Supports semantic versioning
5. **Compact**: Efficient for wire protocols

---

## 2. Token Format

### 2.1 Simple Token

```
domain.approach.role

Examples:
  family.safe.guide
  work.professional.assistant
  secure.privacy.guardian
```

| Component | Description | Constraints |
|-----------|-------------|-------------|
| `domain` | Value domain (family, work, secure) | 1-32 lowercase alpha |
| `approach` | Approach within domain | 1-32 lowercase alpha |
| `role` | Specific role/function | 1-32 lowercase alpha |

### 2.2 Hierarchical Token

```
namespace.segment.segment...

Examples:
  company.acme.legal.compliance
  religion.buddhist.meditation
  culture.japanese.formal
  user.alice.personal
```

| Component | Description | Constraints |
|-----------|-------------|-------------|
| `namespace` | Governance tier (company, religion, user) | See §2.3 |
| `segment` | Path within namespace | 1-32 lowercase alphanumeric + hyphen |

### 2.3 Namespace Prefixes

| Prefix | Governance | Examples |
|--------|------------|----------|
| `family` | Creed Space core | `family.safe.guide` |
| `work` | Creed Space core | `work.professional.assistant` |
| `secure` | Creed Space core | `secure.privacy.guardian` |
| `creative` | Creed Space core | `creative.artistic.muse` |
| `reality` | Creed Space core | `reality.factual.anchor` |
| `company.<org>` | Organizational | `company.acme.legal` |
| `school.<org>` | Educational | `school.mit.research` |
| `ngo.<org>` | Non-profit | `ngo.redcross.humanitarian` |
| `religion.<tradition>` | Religious | `religion.buddhist.mindfulness` |
| `culture.<region>` | Cultural | `culture.japanese.formal` |
| `community.<name>` | Community | `community.gaming.esports` |
| `user.<username>` | Personal | `user.alice.private` |

### 2.4 Versioned Token

```
token@version

Examples:
  family.safe.guide@1.2.0
  work.professional.assistant@latest
  company.acme.legal@2.0.0-beta
```

| Version Format | Description |
|----------------|-------------|
| `X.Y.Z` | Semantic version (exact) |
| `^X.Y.Z` | Compatible with X.Y.Z |
| `~X.Y.Z` | Approximately X.Y.Z |
| `latest` | Most recent stable |
| `canary` | Most recent (including pre-release) |

---

## 3. Formal Grammar

### 3.1 ABNF Grammar (RFC 5234)

```abnf
; UVC Token Grammar (Updated 2026-01-12: Variable-depth support)

uvc-token         = token-path ["@" version] [":" namespace-suffix]

; Token path: minimum 3 segments, maximum 10 segments
token-path        = segment 2*9("." segment)

; Each segment: lowercase letters, digits, hyphens
segment           = LALPHA *31(LALPHA / DIGIT / "-")

; Semantic interpretation (backward compatible):
;   - First segment = domain
;   - Second-to-last segment = approach
;   - Last segment = role
;   - Middle segments = path (organizational hierarchy)
;
; Examples:
;   3 segments: family.safe.guide (domain=family, approach=safe, role=guide)
;   4 segments: company.acme.legal.compliance (domain=company, path=[acme], approach=legal, role=compliance)
;   5 segments: org.example.dept.team.policy (domain=org, path=[example,dept], approach=team, role=policy)

; Namespace suffix (optional, uppercase)
namespace-suffix  = UALPHA *31(UALPHA / DIGIT)

; Namespace governance (determined by first segment):
;   Core: family, work, secure, creative, reality, education, health, finance, legal
;   Organizational: company.*, school.*, ngo.*
;   Community: religion.*, culture.*, community.*
;   Personal: user.*

; Version constraints
version           = exact-version / compat-version / approx-version / alias-version
exact-version     = semver
compat-version    = "^" semver
approx-version    = "~" semver
alias-version     = "latest" / "canary"

semver            = major "." minor "." patch ["-" prerelease]
major             = 1*5DIGIT
minor             = 1*5DIGIT
patch             = 1*5DIGIT
prerelease        = 1*(ALPHA / DIGIT / "." / "-")

; Core rules
LALPHA            = %x61-7A                    ; lowercase a-z
DIGIT             = %x30-39                    ; 0-9
ALPHA             = %x41-5A / %x61-7A          ; A-Z / a-z
```

### 3.2 Regular Expression (for validation)

```python
# Complete UVC token regex
UVC_TOKEN_PATTERN = r"""
    ^
    (?:
        # Core namespace (simple token)
        (?:family|work|secure|creative|reality)
        \.
        [a-z]{1,32}
        \.
        [a-z]{1,32}
    |
        # Organizational namespace
        (?:company|school|ngo)
        \.
        [a-z0-9-]{1,32}
        (?:\.[a-z0-9-]{1,32})+
    |
        # Community namespace
        (?:religion|culture|community)
        \.
        [a-z0-9-]{1,32}
        (?:\.[a-z0-9-]{1,32})+
    |
        # Personal namespace
        user
        \.
        [a-z0-9_-]{1,32}
        (?:\.[a-z0-9-]{1,32})*
    )
    # Optional version
    (?:
        @
        (?:
            [\^~]?
            [0-9]{1,5}
            \.
            [0-9]{1,5}
            \.
            [0-9]{1,5}
            (?:-[a-zA-Z0-9.-]+)?
        |
            latest
        |
            canary
        )
    )?
    $
"""
```

---

## 4. Validation Rules

### 4.1 Structural Rules

```python
class UVCValidationRules:
    """Validation rules for UVC tokens"""

    RULES = {
        # Length constraints
        'max_total_length': 128,       # Maximum total token length
        'max_segments': 8,              # Maximum hierarchy depth
        'max_segment_length': 32,       # Maximum single segment length

        # Character constraints
        'allowed_segment_chars': r'^[a-z0-9-]+$',
        'segment_start_char': r'^[a-z]',    # Must start with letter
        'segment_end_char': r'[a-z0-9]$',   # Must end with letter or digit

        # Structural constraints
        'no_consecutive_dots': True,
        'no_leading_dot': True,
        'no_trailing_dot': True,
        'no_consecutive_hyphens': True,
        'no_leading_hyphen': True,
        'no_trailing_hyphen': True,

        # Reserved words (cannot be used as segments)
        'reserved_words': [
            'system', 'admin', 'root', 'null', 'undefined',
            'true', 'false', 'none', 'void', 'default',
            'api', 'internal', 'private', 'public', 'test'
        ],
    }
```

### 4.2 Validation Algorithm

```python
from dataclasses import dataclass
from enum import Enum
import re
import unicodedata

class ValidationError(Enum):
    NONE = 0
    TOO_LONG = 1
    TOO_MANY_SEGMENTS = 2
    SEGMENT_TOO_LONG = 3
    INVALID_CHARACTERS = 4
    INVALID_START_CHAR = 5
    INVALID_END_CHAR = 6
    CONSECUTIVE_DOTS = 7
    CONSECUTIVE_HYPHENS = 8
    RESERVED_WORD = 9
    INVALID_NAMESPACE = 10
    INVALID_VERSION = 11
    EMPTY_SEGMENT = 12

@dataclass
class ValidationResult:
    valid: bool
    error: ValidationError
    message: str
    position: int = -1

class UVCTokenValidator:
    """Validate UVC tokens against specification"""

    CORE_NAMESPACES = {'family', 'work', 'secure', 'creative', 'reality'}
    ORG_PREFIXES = {'company', 'school', 'ngo'}
    COMMUNITY_PREFIXES = {'religion', 'culture', 'community'}
    PERSONAL_PREFIX = 'user'

    RESERVED_WORDS = {
        'system', 'admin', 'root', 'null', 'undefined',
        'true', 'false', 'none', 'void', 'default',
        'api', 'internal', 'private', 'public', 'test'
    }

    def validate(self, token: str) -> ValidationResult:
        """Validate a UVC token"""

        # Handle versioned tokens
        base_token = token
        version = None
        if '@' in token:
            parts = token.split('@', 1)
            base_token = parts[0]
            version = parts[1]

        # Basic length check
        if len(token) > 128:
            return ValidationResult(False, ValidationError.TOO_LONG,
                f"Token exceeds maximum length (128): {len(token)}")

        # Split into segments
        segments = base_token.split('.')

        if len(segments) > 8:
            return ValidationResult(False, ValidationError.TOO_MANY_SEGMENTS,
                f"Too many segments (max 8): {len(segments)}")

        # Check for empty segments (consecutive dots)
        for i, seg in enumerate(segments):
            if not seg:
                return ValidationResult(False, ValidationError.EMPTY_SEGMENT,
                    f"Empty segment at position {i}", i)

        # Validate each segment
        for i, segment in enumerate(segments):
            result = self._validate_segment(segment, i)
            if not result.valid:
                return result

        # Validate namespace structure
        result = self._validate_namespace(segments)
        if not result.valid:
            return result

        # Validate version if present
        if version:
            result = self._validate_version(version)
            if not result.valid:
                return result

        return ValidationResult(True, ValidationError.NONE, "Valid")

    def _validate_segment(self, segment: str, position: int) -> ValidationResult:
        """Validate a single segment"""

        if len(segment) > 32:
            return ValidationResult(False, ValidationError.SEGMENT_TOO_LONG,
                f"Segment '{segment}' exceeds maximum length (32)", position)

        if not re.match(r'^[a-z0-9-]+$', segment):
            return ValidationResult(False, ValidationError.INVALID_CHARACTERS,
                f"Segment '{segment}' contains invalid characters", position)

        if not segment[0].isalpha():
            return ValidationResult(False, ValidationError.INVALID_START_CHAR,
                f"Segment '{segment}' must start with letter", position)

        if segment[-1] == '-':
            return ValidationResult(False, ValidationError.INVALID_END_CHAR,
                f"Segment '{segment}' cannot end with hyphen", position)

        if '--' in segment:
            return ValidationResult(False, ValidationError.CONSECUTIVE_HYPHENS,
                f"Segment '{segment}' has consecutive hyphens", position)

        if segment in self.RESERVED_WORDS:
            return ValidationResult(False, ValidationError.RESERVED_WORD,
                f"Segment '{segment}' is a reserved word", position)

        return ValidationResult(True, ValidationError.NONE, "Valid")

    def _validate_namespace(self, segments: list) -> ValidationResult:
        """Validate namespace structure"""

        first = segments[0]

        # Core namespace (simple token)
        if first in self.CORE_NAMESPACES:
            if len(segments) != 3:
                return ValidationResult(False, ValidationError.INVALID_NAMESPACE,
                    f"Core namespace '{first}' requires exactly 3 segments")
            return ValidationResult(True, ValidationError.NONE, "Valid")

        # Organizational namespace
        if first in self.ORG_PREFIXES:
            if len(segments) < 3:
                return ValidationResult(False, ValidationError.INVALID_NAMESPACE,
                    f"Organizational namespace '{first}' requires at least 3 segments")
            return ValidationResult(True, ValidationError.NONE, "Valid")

        # Community namespace
        if first in self.COMMUNITY_PREFIXES:
            if len(segments) < 3:
                return ValidationResult(False, ValidationError.INVALID_NAMESPACE,
                    f"Community namespace '{first}' requires at least 3 segments")
            return ValidationResult(True, ValidationError.NONE, "Valid")

        # Personal namespace
        if first == self.PERSONAL_PREFIX:
            if len(segments) < 2:
                return ValidationResult(False, ValidationError.INVALID_NAMESPACE,
                    "Personal namespace 'user' requires at least 2 segments")
            return ValidationResult(True, ValidationError.NONE, "Valid")

        return ValidationResult(False, ValidationError.INVALID_NAMESPACE,
            f"Unknown namespace prefix: '{first}'")

    def _validate_version(self, version: str) -> ValidationResult:
        """Validate version string"""

        # Alias versions
        if version in ('latest', 'canary'):
            return ValidationResult(True, ValidationError.NONE, "Valid")

        # Strip compatibility prefixes
        clean_version = version.lstrip('^~')

        # Semver pattern
        semver_pattern = r'^[0-9]{1,5}\.[0-9]{1,5}\.[0-9]{1,5}(-[a-zA-Z0-9.-]+)?$'
        if not re.match(semver_pattern, clean_version):
            return ValidationResult(False, ValidationError.INVALID_VERSION,
                f"Invalid version format: '{version}'")

        return ValidationResult(True, ValidationError.NONE, "Valid")
```

---

## 5. Canonicalization

### 5.1 Canonical Form

UVC tokens have a single canonical form for consistent hashing and comparison:

```python
import unicodedata
import re

def canonicalize_uvc_token(token: str) -> str:
    """
    Convert UVC token to canonical form.

    Canonical form is:
    1. Unicode NFKC normalized
    2. Lowercase
    3. Whitespace stripped
    4. Single dots (no consecutive)
    5. Trailing whitespace removed from segments

    Args:
        token: Input UVC token (may be non-canonical)

    Returns:
        Canonical form of token

    Raises:
        ValueError: If token cannot be canonicalized
    """

    # Step 1: Unicode NFKC normalization
    # Converts compatibility characters to canonical equivalents
    token = unicodedata.normalize('NFKC', token)

    # Step 2: Convert to lowercase
    token = token.lower()

    # Step 3: Strip leading/trailing whitespace
    token = token.strip()

    # Step 4: Normalize whitespace within token
    # Remove any spaces that might have been inserted
    token = re.sub(r'\s+', '', token)

    # Step 5: Collapse multiple consecutive dots
    token = re.sub(r'\.+', '.', token)

    # Step 6: Remove leading/trailing dots
    token = token.strip('.')

    # Step 7: Handle version part separately
    if '@' in token:
        base, version = token.rsplit('@', 1)
        # Normalize version (strip redundant zeros)
        version = _normalize_version(version)
        token = f"{base}@{version}"

    return token

def _normalize_version(version: str) -> str:
    """Normalize version string"""

    if version in ('latest', 'canary'):
        return version

    # Preserve compatibility prefix
    prefix = ''
    if version.startswith('^') or version.startswith('~'):
        prefix = version[0]
        version = version[1:]

    # Parse semver
    match = re.match(r'^(\d+)\.(\d+)\.(\d+)(-.*)?$', version)
    if not match:
        return prefix + version

    major, minor, patch, prerelease = match.groups()

    # Strip leading zeros (except for '0')
    major = str(int(major))
    minor = str(int(minor))
    patch = str(int(patch))

    result = f"{major}.{minor}.{patch}"
    if prerelease:
        result += prerelease.lower()

    return prefix + result
```

### 5.2 Equality

Two tokens are equal if their canonical forms are identical:

```python
def tokens_equal(token1: str, token2: str) -> bool:
    """Check if two UVC tokens are semantically equal"""
    return canonicalize_uvc_token(token1) == canonicalize_uvc_token(token2)
```

### 5.3 Hashing

For content addressing and caching:

```python
import hashlib

def hash_uvc_token(token: str) -> str:
    """
    Compute content hash of UVC token.

    Uses SHA-256 of canonical form.
    """
    canonical = canonicalize_uvc_token(token)
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()
```

---

## 6. Examples

### 6.1 Valid Tokens

```python
# Core namespace (simple)
"family.safe.guide"           # ✓ Valid
"work.professional.assistant" # ✓ Valid
"secure.privacy.guardian"     # ✓ Valid
"creative.artistic.muse"      # ✓ Valid
"reality.factual.anchor"      # ✓ Valid

# Organizational namespace
"company.acme.legal.compliance"        # ✓ Valid
"company.acme-corp.hr.policies"        # ✓ Valid
"school.mit.research.ethics"           # ✓ Valid
"ngo.red-cross.humanitarian.disaster"  # ✓ Valid

# Community namespace
"religion.buddhist.meditation.mindfulness"  # ✓ Valid
"culture.japanese.business.formal"          # ✓ Valid
"community.gaming.esports.fair-play"        # ✓ Valid

# Personal namespace
"user.alice.personal"          # ✓ Valid
"user.bob-123.work.assistant"  # ✓ Valid

# Versioned tokens
"family.safe.guide@1.2.0"      # ✓ Valid (exact)
"family.safe.guide@^1.2.0"     # ✓ Valid (compatible)
"family.safe.guide@~1.2.0"     # ✓ Valid (approximate)
"family.safe.guide@latest"     # ✓ Valid (alias)
"family.safe.guide@2.0.0-beta" # ✓ Valid (prerelease)
```

### 6.2 Invalid Tokens

```python
# Too few segments for core namespace
"family.safe"                  # ✗ Invalid (needs 3 segments)

# Invalid characters
"family.Safe.guide"            # ✗ Invalid (uppercase)
"family.safe_guide"            # ✗ Invalid (underscore in core)
"family.safe guide"            # ✗ Invalid (space)

# Structural errors
"..family.safe.guide"          # ✗ Invalid (leading dots)
"family.safe.guide.."          # ✗ Invalid (trailing dots)
"family..safe.guide"           # ✗ Invalid (consecutive dots)

# Reserved words
"family.system.guide"          # ✗ Invalid (reserved word)
"company.acme.admin.policies"  # ✗ Invalid (reserved word)

# Too long
"family.this-is-a-very-long-segment-that-exceeds-limit.guide"  # ✗ Invalid

# Invalid version
"family.safe.guide@abc"        # ✗ Invalid (not semver)
"family.safe.guide@1.2"        # ✗ Invalid (incomplete semver)
```

### 6.3 Canonicalization Examples

```python
# Whitespace normalization
"  family.safe.guide  " → "family.safe.guide"

# Case normalization
"Family.Safe.Guide" → "family.safe.guide"

# Dot normalization
"family..safe.guide" → "family.safe.guide"

# Version normalization
"family.safe.guide@01.02.03" → "family.safe.guide@1.2.3"
"family.safe.guide@1.2.3-BETA" → "family.safe.guide@1.2.3-beta"
```

---

## 7. Security Considerations

### 7.1 Namespace Squatting

**Risk**: Malicious actors could register namespaces to impersonate organizations.

**Mitigation**: Organizational namespaces require proof of ownership (see UVC_NAMESPACE_GOVERNANCE.md).

### 7.2 Homograph Attacks

**Risk**: Similar-looking characters could create confusing tokens.

```python
# Example homograph attack
"company.аcme.legal"  # Uses Cyrillic 'а' instead of Latin 'a'
```

**Mitigation**:
1. NFKC normalization converts lookalikes to canonical form
2. Only ASCII lowercase letters allowed in segments
3. Visual inspection of registered tokens

### 7.3 Reserved Word Bypass

**Risk**: Attackers might try variants of reserved words.

**Mitigation**:
1. Validation after canonicalization
2. Reserved word list checked against normalized form
3. Substring matching for critical words (e.g., `admin`, `system`)

### 7.4 Length Attacks

**Risk**: Extremely long tokens could cause DoS.

**Mitigation**:
1. Hard limit of 128 characters total
2. Maximum 8 segments
3. Maximum 32 characters per segment

---

## 8. Reference Implementation

### 8.1 Python Module

```python
# File: core/services/uvc_parser.py

"""
UVC Token Parser and Validator

Reference implementation of UVC naming specification.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, List
import re
import unicodedata

__all__ = [
    'UVCToken',
    'UVCTokenParser',
    'UVCTokenValidator',
    'ValidationResult',
    'canonicalize_uvc_token',
    'parse_uvc_token',
]

@dataclass
class UVCToken:
    """Parsed UVC token"""

    raw: str                    # Original input
    canonical: str              # Canonical form
    segments: List[str]         # Path segments
    namespace_type: str         # 'core', 'org', 'community', 'personal'
    namespace: str              # Full namespace prefix
    version: Optional[str]      # Version constraint if present
    version_constraint: str     # 'exact', 'compatible', 'approximate', 'alias'

    def to_uri(self, issuer: str = "creed.space") -> str:
        """Convert to VCP bundle URI"""
        path = '.'.join(self.segments)
        uri = f"creed://{issuer}/{path}"
        if self.version:
            uri += f"@{self.version}"
        return uri

    def __str__(self) -> str:
        return self.canonical

    def __hash__(self) -> int:
        return hash(self.canonical)

    def __eq__(self, other) -> bool:
        if isinstance(other, UVCToken):
            return self.canonical == other.canonical
        if isinstance(other, str):
            return self.canonical == canonicalize_uvc_token(other)
        return False


class UVCTokenParser:
    """Parse UVC tokens into structured form"""

    CORE_NAMESPACES = frozenset({'family', 'work', 'secure', 'creative', 'reality'})
    ORG_PREFIXES = frozenset({'company', 'school', 'ngo'})
    COMMUNITY_PREFIXES = frozenset({'religion', 'culture', 'community'})

    def parse(self, token: str) -> UVCToken:
        """
        Parse a UVC token string into structured form.

        Raises:
            ValueError: If token is invalid
        """
        # Validate first
        validator = UVCTokenValidator()
        result = validator.validate(token)
        if not result.valid:
            raise ValueError(f"Invalid UVC token: {result.message}")

        # Canonicalize
        canonical = canonicalize_uvc_token(token)

        # Extract version
        version = None
        version_constraint = 'none'
        base_token = canonical

        if '@' in canonical:
            base_token, version = canonical.rsplit('@', 1)
            if version in ('latest', 'canary'):
                version_constraint = 'alias'
            elif version.startswith('^'):
                version_constraint = 'compatible'
                version = version[1:]
            elif version.startswith('~'):
                version_constraint = 'approximate'
                version = version[1:]
            else:
                version_constraint = 'exact'

        # Parse segments
        segments = base_token.split('.')

        # Determine namespace type
        first = segments[0]
        if first in self.CORE_NAMESPACES:
            namespace_type = 'core'
            namespace = first
        elif first in self.ORG_PREFIXES:
            namespace_type = 'org'
            namespace = '.'.join(segments[:2])
        elif first in self.COMMUNITY_PREFIXES:
            namespace_type = 'community'
            namespace = '.'.join(segments[:2])
        elif first == 'user':
            namespace_type = 'personal'
            namespace = '.'.join(segments[:2])
        else:
            raise ValueError(f"Unknown namespace: {first}")

        return UVCToken(
            raw=token,
            canonical=canonical,
            segments=segments,
            namespace_type=namespace_type,
            namespace=namespace,
            version=version,
            version_constraint=version_constraint,
        )


def parse_uvc_token(token: str) -> UVCToken:
    """Convenience function to parse UVC token"""
    return UVCTokenParser().parse(token)


# Additional exports
__version__ = '1.0.0'
```

### 8.2 JSON Schema

See `data/schemas/uvc-token.schema.json` for JSON Schema validation.

---

## Appendices

### A. Reserved Words (Complete List)

```python
RESERVED_WORDS = {
    # System terms
    'system', 'admin', 'root', 'internal', 'private', 'public',

    # Programming terms
    'null', 'undefined', 'true', 'false', 'none', 'void',

    # Infrastructure terms
    'api', 'test', 'debug', 'staging', 'production', 'default',

    # VCP-specific terms
    'vcp', 'uvc', 'csm', 'bundle', 'manifest', 'creed',
}
```

### B. Namespace Governance Summary

| Tier | Registration | Governance |
|------|--------------|------------|
| Core | Reserved | Creed Space stewardship |
| Organizational | Verified ownership | Delegated to organization |
| Community | Community consensus | Multi-stakeholder |
| Personal | Self-service | Individual control |

See UVC_NAMESPACE_GOVERNANCE.md for full governance specification.

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-11 | Initial specification |

---

*This specification is released under CC BY 4.0. Contributions welcome.*
