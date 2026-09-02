# CSM1 Grammar Specification

<!-- vcp-document-control
status: Reference companion, status-classified
normative-authority: Accepted specifications and schemas control
protocol-version: Lineage document, see document body
last-reviewed: 2026-08-13 status and authority classification
owner: VCP Spec maintainers
evidence-boundary: Explanatory material, not implementation conformance
-->

> **Superseded by [`specs/VCP_SEMANTICS_v2.0.md`](https://github.com/Creed-Space/VCP-Spec/blob/main/specs/VCP_SEMANTICS_v2.0.md) §2.**
> This copy and its sibling [VCP_SEMANTICS_CSM1.md](../semantics/VCP_SEMANTICS_CSM1.md) were consolidated into
> the VCP/S layer specification; where they disagree, the layer specification
> controls. Retained for link stability.

**Version**: 1.0.0
**Date**: 2026-01-11
**Layer**: 3 (VCP Content)
**Status**: Complete

---

## Abstract

CSM1 (Constitutional Safety Minicode, Version 1) is a compact encoding format for constitutional configurations. It encodes persona, adherence level, scopes, namespace, and version in a single token suitable for wire protocols, API parameters, and human debugging.

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Formal Grammar](#2-formal-grammar)
3. [Persona Definitions](#3-persona-definitions)
4. [Scope Definitions](#4-scope-definitions)
5. [Adherence Levels](#5-adherence-levels)
6. [Encoding Formats](#6-encoding-formats)
7. [Parsing Algorithm](#7-parsing-algorithm)
8. [Serialization](#8-serialization)
9. [Examples](#9-examples)
10. [Project-Maintained Implementation](#10-project-maintained-implementation)

---

## 1. Introduction

### 1.1 Purpose

CSM1 serves as:
- **Compact identifier** for constitutional configurations (~10-30 characters)
- **Wire protocol token** for efficient transmission
- **Human-readable code** for debugging and logging
- **Interoperability format** across VCP implementations

### 1.2 Design Goals

1. **Compact**: Minimize token length for efficiency
2. **Readable**: Parseable by humans at a glance
3. **Unambiguous**: Deterministic parsing and serialization
4. **Extensible**: Support for custom namespaces and personas
5. **Compatible**: Maps directly to VCP bundle metadata

### 1.3 Relationship to VCP

CSM1 codes appear in:
- Bundle manifest `metadata.csm1` field
- API parameters for constitution selection
- Audit log entries
- UI displays for constitution identification

---

## 2. Formal Grammar

### 2.1 ABNF Grammar (RFC 5234)

```abnf
; CSM1 Code Grammar

csm1-code         = std-code / custom-code
std-code          = std-persona adherence [scopes] [":" namespace] ["@" version]
custom-code       = "C" adherence [scopes] ":" namespace ["@" version]
                  ; When persona is C, the namespace component is REQUIRED

; Persona (single character)
persona           = std-persona / "C"
std-persona       = "N" / "Z" / "G" / "A" / "M" / "D"
                  ; N = Nanny (child safety)
                  ; Z = Sentinel (security)
                  ; G = Godparent (ethics)
                  ; A = Ambassador (professional)
                  ; M = Muse (creative challenge)
                  ; D = Mediator (fair resolution)
                  ; C = Custom (user-defined)

; Adherence level (0-5)
adherence         = "0" / "1" / "2" / "3" / "4" / "5"
                  ; 0 = Minimal (advisory only)
                  ; 1 = Relaxed
                  ; 2 = Moderate
                  ; 3 = Standard
                  ; 4 = Strict
                  ; 5 = Maximum (no exceptions)

; Scopes (optional, additive)
; scope-codes MUST be unique within a code and MUST NOT combine
; F/A, V/A or H/A (see the scope conflict rule below)
scopes            = 1*("+" scope-code)
scope-code        = "F" / "W" / "P" / "E" / "T" / "O" / "V" / "A" / "H" / "S" / "R"
                  ; F = Family (child-safe)
                  ; W = Work (professional)
                  ; P = Privacy (data protection)
                  ; E = Education (learning context)
                  ; T = Technical (developer context)
                  ; O = Official (governmental)
                  ; V = Vulnerable (protected populations)
                  ; A = Adult (mature content allowed)
                  ; H = Health (medical context)
                  ; S = Social (community/social media)
                  ; R = Religious (spiritual context)

; Namespace (optional, custom constitutions)
namespace         = 1*8UALPHA
                  ; Uppercase identifier for custom namespace
                  ; e.g., ELEM, CORP, MED, ACME

; Version (optional, semver or alias)
version           = semver / "latest" / "canary"
semver            = major "." minor "." patch
major             = "0" / (%x31-39 *2DIGIT)
minor             = "0" / (%x31-39 *2DIGIT)
patch             = "0" / (%x31-39 *2DIGIT)

; Character classes
UALPHA            = %x41-5A                    ; Uppercase A-Z
DIGIT             = %x30-39                    ; 0-9
```

### 2.2 Regular Expression

> The regular expression below validates **syntax only**. It does not enforce
> scope uniqueness, the F/A, V/A, H/A scope conflict rule, or the namespace
> requirement for the custom persona `C`; the reference parser and
> `schemas/vcp-semantics-csm1.schema.json` enforce those in addition.

```python
CSM1_PATTERN = r"""
    ^
    (?P<persona>[NZGAMDC])             # Persona (1 char)
    (?P<adherence>[0-5])                 # Adherence (1 digit)
    (?P<scopes>(?:\+[FWPETOVAHSR])*)     # Scopes (optional, +X format)
    (?::(?P<namespace>[A-Z]{1,8}))?      # Namespace (optional, :XXX format)
    (?:@(?P<version>                     # Version (optional, @X.Y.Z format)
        (?:(?:0|[1-9][0-9]{0,2})\.(?:0|[1-9][0-9]{0,2})\.(?:0|[1-9][0-9]{0,2}))
        |latest
        |canary
    ))?
    $
"""
```

---

## 3. Persona Definitions

### 3.1 Standard Personas

| Code | Name | Focus | Default Adherence | Typical Scopes |
|------|------|-------|-------------------|----------------|
| **N** | Nanny | Child safety and family-appropriate content | 5 | F, E |
| **Z** | Sentinel | Security, privacy, operational safety | 4 | P, W |
| **G** | Godparent | Ethical guidance and moral reasoning | 4 | R, E |
| **A** | Ambassador | Professional conduct, diplomatic communication | 3 | W, O |
| **M** | Muse | Creativity and artistic expression | 2 | A |
| **D** | Mediator | Fair resolution and balanced mediation | 3 | S, W |
| **C** | Custom | User-defined constitution | 3 | (varies) |

### 3.2 Persona Behavioral Profiles

```python
PERSONA_PROFILES = {
    'N': {
        'name': 'Nanny',
        'focus': 'Child safety and family-appropriate content',
        'behaviors': {
            'content_filtering': 'strict',
            'language_register': 'simple',
            'topic_restrictions': ['violence', 'adult_content', 'scary', 'drugs'],
            'positive_reinforcement': True,
            'educational_framing': True,
        },
        'default_adherence': 5,
        'compatible_scopes': ['F', 'E', 'V'],
        'incompatible_scopes': ['A'],  # Adult scope conflicts
    },

    'Z': {
        'name': 'Sentinel',
        'focus': 'Security, privacy, and operational safety',
        'behaviors': {
            'data_handling': 'paranoid',
            'credential_exposure': 'never',
            'logging_detail': 'minimal_pii',
            'external_calls': 'restricted',
            'code_execution': 'sandboxed',
        },
        'default_adherence': 4,
        'compatible_scopes': ['P', 'W', 'T', 'O'],
        'incompatible_scopes': [],
    },

    'G': {
        'name': 'Godparent',
        'focus': 'Ethical guidance and moral reasoning',
        'behaviors': {
            'ethical_framework': 'pluralistic',
            'moral_reasoning': 'explicit',
            'value_conflicts': 'acknowledge_and_reason',
            'prescriptive': False,  # Guides, doesn't dictate
            'cultural_sensitivity': True,
        },
        'default_adherence': 4,
        'compatible_scopes': ['R', 'E', 'S'],
        'incompatible_scopes': [],
    },

    'A': {
        'name': 'Ambassador',
        'focus': 'Professional conduct and diplomatic communication',
        'behaviors': {
            'tone': 'formal',
            'language_register': 'professional',
            'controversy_handling': 'balanced',
            'branding_compliant': True,
            'represents_organization': True,
        },
        'default_adherence': 3,
        'compatible_scopes': ['W', 'O', 'S'],
        'incompatible_scopes': ['A'],  # Adult scope inappropriate
    },

    'M': {
        'name': 'Muse',
        'focus': 'Creativity and artistic expression',
        'behaviors': {
            'creative_freedom': 'high',
            'stylistic_range': 'wide',
            'experimental': True,
            'content_rating': 'flexible',
            'inspiration_over_accuracy': True,
        },
        'default_adherence': 2,
        'compatible_scopes': ['A', 'E'],
        'incompatible_scopes': ['O'],  # Official contexts need more control
    },

    'D': {
        'name': 'Mediator',
        'focus': 'Fair resolution and balanced mediation',
        'behaviors': {
            'conflict_resolution': 'structured',
            'perspective_taking': 'multi_party',
            'neutrality': 'enforced',
            'escalation_handling': 'de_escalate',
            'fairness_framing': True,
        },
        'default_adherence': 3,
        'compatible_scopes': ['S', 'E', 'W', 'O'],
        'incompatible_scopes': [],
    },

    'C': {
        'name': 'Custom',
        'focus': 'User-defined constitution',
        'behaviors': {},  # Defined by custom constitution
        'default_adherence': 3,
        'compatible_scopes': [],  # All allowed
        'incompatible_scopes': [],
        'requires_namespace': True,  # Must specify custom namespace
    },
}
```

---

## 4. Scope Definitions

### 4.1 Scope Codes

| Code | Name | Description | Behavioral Modifiers |
|------|------|-------------|---------------------|
| **F** | Family | Family-appropriate, child-safe | Strict content filtering, simple language |
| **W** | Work | Professional workplace | Formal tone, no personal topics |
| **P** | Privacy | Privacy-focused, data protection | Minimal data collection, anonymization |
| **E** | Education | Educational context | Explanatory mode, learning-oriented |
| **T** | Technical | Developer/technical context | Technical terminology, code-focused |
| **O** | Official | Official/governmental | Conservative, policy-compliant |
| **V** | Vulnerable | Vulnerable populations | Extra care, resource referrals |
| **A** | Adult | Adult-only, explicit allowed | Reduced content restrictions |
| **H** | Health | Healthcare/medical | Accuracy critical, disclaimer-heavy |
| **S** | Social | Social media/community | Engagement-aware, moderation-friendly |
| **R** | Religious | Religious/spiritual | Cultural sensitivity, respect for beliefs |

### 4.2 Scope Compatibility Matrix

```python
# Scopes that conflict (cannot be combined)
SCOPE_CONFLICTS = {
    ('F', 'A'),  # Family and Adult are mutually exclusive
    ('V', 'A'),  # Vulnerable and Adult conflict
    ('H', 'A'),  # Health contexts shouldn't be adult-only
}

# Scopes that synergize well
SCOPE_SYNERGIES = {
    ('F', 'E'),  # Family + Education = child learning
    ('W', 'P'),  # Work + Privacy = corporate data protection
    ('H', 'P'),  # Health + Privacy = HIPAA-compliant
    ('E', 'T'),  # Education + Technical = coding education
}
```

### 4.3 Scope Behavioral Modifiers

```python
SCOPE_MODIFIERS = {
    'F': {  # Family
        'language_complexity': 'reduced',
        'content_rating': 'G',
        'topic_restrictions': ['violence', 'adult', 'drugs', 'horror'],
        'positive_framing': True,
    },

    'W': {  # Work
        'formality': 'high',
        'personal_questions': 'avoid',
        'branding_neutral': True,
        'meeting_appropriate': True,
    },

    'P': {  # Privacy
        'data_minimization': True,
        'consent_prompting': True,
        'anonymous_default': True,
        'third_party_sharing': 'never',
    },

    'E': {  # Education
        'explanatory_mode': True,
        'socratic_method': 'available',
        'step_by_step': True,
        'assessment_awareness': True,
    },

    'T': {  # Technical
        'code_formatting': True,
        'technical_jargon': 'allowed',
        'debugging_mode': True,
        'documentation_links': True,
    },

    'O': {  # Official
        'legal_disclaimers': True,
        'policy_compliance': 'strict',
        'audit_trail': True,
        'conservative_interpretation': True,
    },

    'V': {  # Vulnerable
        'crisis_detection': True,
        'resource_referrals': True,
        'gentle_language': True,
        'no_pressure': True,
    },

    'A': {  # Adult
        'content_rating': 'R',
        'explicit_allowed': True,
        'age_verification_assumed': True,
    },

    'H': {  # Health
        'medical_accuracy': 'critical',
        'disclaimer_required': True,
        'professional_referral': True,
        'symptom_assessment': 'careful',
    },

    'S': {  # Social
        'engagement_aware': True,
        'community_guidelines': True,
        'viral_content_caution': True,
        'platform_policies': True,
    },

    'R': {  # Religious
        'belief_respect': True,
        'multi_tradition_aware': True,
        'proselytizing': 'never',
        'sacred_text_handling': 'reverent',
    },
}
```

---

## 5. Adherence Levels

### 5.1 Level Definitions

| Level | Name | Description | Override Policy |
|-------|------|-------------|-----------------|
| **0** | Minimal | Advisory only, can be overridden | User request overrides |
| **1** | Relaxed | Light guardrails, flexible | Strong user intent overrides |
| **2** | Moderate | Balanced protection | Explicit user request may override |
| **3** | Standard | Default protection level | Limited override scenarios |
| **4** | Strict | Strong enforcement | Very limited overrides |
| **5** | Maximum | No exceptions | No overrides, hard blocks |

### 5.2 Adherence Behavioral Mapping

```python
ADHERENCE_BEHAVIORS = {
    0: {  # Minimal
        'enforcement': 'advisory',
        'user_override': 'always',
        'warning_level': 'none',
        'block_threshold': 'never',
        'logging': 'minimal',
    },

    1: {  # Relaxed
        'enforcement': 'soft',
        'user_override': 'with_acknowledgment',
        'warning_level': 'gentle',
        'block_threshold': 'extreme_harm_only',
        'logging': 'basic',
    },

    2: {  # Moderate
        'enforcement': 'moderate',
        'user_override': 'with_reason',
        'warning_level': 'clear',
        'block_threshold': 'harmful_content',
        'logging': 'standard',
    },

    3: {  # Standard
        'enforcement': 'active',
        'user_override': 'limited_scenarios',
        'warning_level': 'prominent',
        'block_threshold': 'policy_violation',
        'logging': 'detailed',
    },

    4: {  # Strict
        'enforcement': 'strict',
        'user_override': 'exceptional_only',
        'warning_level': 'explicit',
        'block_threshold': 'any_risk',
        'logging': 'comprehensive',
    },

    5: {  # Maximum
        'enforcement': 'absolute',
        'user_override': 'never',
        'warning_level': 'blocking',
        'block_threshold': 'proactive',
        'logging': 'full_audit',
    },
}
```

---

## 6. Encoding Formats

### 6.1 Tiered Formats

CSM1 supports three encoding tiers for different use cases:

| Tier | Name | Length | Format | Use Case |
|------|------|--------|--------|----------|
| **A** | NANO | 2-24 | `<P><A>[+<S>]*` | Wire protocols, HTTP headers |
| **B** | MICRO | 2-45 | `<P><A>[+<S>]*[:<NS>][@<VERSION>]` | API parameters, config files |
| **C** | COMPACT | 18-294 | `CS1\|<persona>\|<level>\|<token>\|<scopes>` | Human debugging, logging |

### 6.2 Tier A: NANO Format

```
NANO: persona + adherence + scopes
Example: N5+E+F

Grammar:
  nano = persona adherence *("+", scope)

Examples:
  N5          → Nanny, level 5, no scopes
  N5+F        → Nanny, level 5, Family scope
  Z4+P+W      → Sentinel, level 4, Privacy + Work
  D3+S+E      → Mediator, level 3, Social + Education
```

### 6.3 Tier B: MICRO Format

```
MICRO: persona + adherence [ + scopes ] [ ":" + namespace ] [ "@" + version ]
Example: N5+F:ELEM

Grammar:
  micro = persona adherence *("+" scope) [":" namespace] ["@" version]

Examples:
  N5:ELEM       → Nanny, level 5, ELEM namespace
  N5+E+F:ELEM   → Nanny, level 5, ELEM namespace, Family + Education
  C3+W:ACME     → Custom, level 3, ACME namespace, Work scope
```

### 6.4 Tier C: COMPACT Format

```
COMPACT: "CS1|" + persona_name + "|" + adherence + "|" + token + "|" + flags
Example: CS1|nanny|5|family.safe.guide|E,F

Grammar:
  compact = "CS1|" persona-name "|" adherence "|" token "|" scope-list
  persona-name = lowercase-persona-name
  token = uvc-token  ; MUST already be in canonical UVC form
  scope-list = scope *("," scope)

COMPACT accepts canonical UVC tokens only. Numeric semantic-version components MUST be `0` or begin with `1`-`9`; serializers normalize leading zeroes before emitting the token.

Examples:
  CS1|nanny|5|family.safe.guide|E,F
  CS1|sentinel|4|secure.privacy.guardian|P,W
  CS1|custom|3|company.acme.legal|O,W
```

### 6.5 Format Conversion

```python
class CSM1Converter:
    """Convert between CSM1 format tiers"""

    def nano_to_micro(self, nano: str, namespace: str = None) -> str:
        """Convert NANO to MICRO format"""
        parsed = self.parse(nano)
        if namespace:
            parsed.namespace = namespace
        return self.serialize(parsed, tier='micro')

    def micro_to_compact(self, micro: str, uvc_token: str) -> str:
        """Convert MICRO to COMPACT format"""
        parsed = self.parse(micro)
        scopes = ','.join(sorted(set(parsed.scopes)))
        return f"CS1|{parsed.persona_name}|{parsed.adherence}|{uvc_token}|{scopes}"

    def compact_to_nano(self, compact: str) -> str:
        """Convert COMPACT to NANO format"""
        parts = compact.split('|')
        # CS1|persona|adherence|token|scopes
        persona_name = parts[1]
        adherence = parts[2]
        scopes = sorted(set(parts[4].split(','))) if parts[4] else []

        persona_code = self._persona_name_to_code(persona_name)
        scope_str = ''.join(f'+{s}' for s in scopes)
        return f"{persona_code}{adherence}{scope_str}"
```

---

## 7. Parsing Algorithm

### 7.1 Parser Implementation

```python
from dataclasses import dataclass
from typing import List, Optional
import re

@dataclass
class CSM1Code:
    """Parsed CSM1 code"""

    raw: str
    persona: str              # Single character (N, Z, G, A, M, D, C)
    persona_name: str         # Full name (nanny, sentinel, etc.)
    adherence: int            # 0-5
    scopes: List[str]         # List of scope codes
    namespace: Optional[str]  # Custom namespace (uppercase)
    version: Optional[str]    # Semver or alias
    uvc_token: Optional[str] = None  # Present only in COMPACT input

    def to_nano(self) -> str:
        """Serialize to NANO format"""
        scopes = ''.join(f'+{s}' for s in sorted(set(self.scopes)))
        return f"{self.persona}{self.adherence}{scopes}"

    def to_micro(self) -> str:
        """Serialize to MICRO format"""
        scopes = ''.join(f'+{s}' for s in sorted(set(self.scopes)))
        result = f"{self.persona}{self.adherence}{scopes}"
        if self.namespace:
            result += f":{self.namespace}"
        if self.version:
            result += f"@{self.version}"
        return result


class CSM1Parser:
    """Parse CSM1 codes"""

    PERSONA_CODES = {'N', 'Z', 'G', 'A', 'M', 'D', 'C'}
    SCOPE_CODES = {'F', 'W', 'P', 'E', 'T', 'O', 'V', 'A', 'H', 'S', 'R'}

    PERSONA_NAMES = {
        'N': 'nanny', 'Z': 'sentinel', 'G': 'godparent', 'A': 'ambassador',
        'M': 'muse', 'D': 'mediator', 'C': 'custom',
    }
    SCOPE_CONFLICTS = {frozenset(pair) for pair in (('F', 'A'), ('V', 'A'), ('H', 'A'))}

    @classmethod
    def _validate_scopes(cls, scopes: List[str]) -> List[str]:
        if len(scopes) != len(set(scopes)):
            raise ValueError("Duplicate CSM1 scope")
        active = set(scopes)
        if any(pair <= active for pair in cls.SCOPE_CONFLICTS):
            raise ValueError("Conflicting CSM1 scopes")
        return scopes

    # Compiled regex patterns
    NANO_PATTERN = re.compile(
        r'^([NZGAMDC])([0-5])((?:\+[FWPETOVAHSR])*)$'
    )

    MICRO_PATTERN = re.compile(
        r'^([NZGAMDC])([0-5])((?:\+[FWPETOVAHSR])*)(?::([A-Z]{1,8}))?'
        r'(?:@((?:(?:0|[1-9][0-9]{0,2})\.(?:0|[1-9][0-9]{0,2})\.(?:0|[1-9][0-9]{0,2})|latest|canary)))?$'
    )

    COMPACT_PATTERN = re.compile(
        r'^CS1\|(nanny|sentinel|godparent|ambassador|muse|mediator|custom)'
        r'\|([0-5])\|([a-z][a-z0-9-]{0,31}'
        r'(?:\.[a-z][a-z0-9-]{0,31}){2,9}'
        r'(?:@(?:[\^~]?(?:0|[1-9][0-9]{0,4})\.(?:0|[1-9][0-9]{0,4})\.(?:0|[1-9][0-9]{0,4})|latest|canary))?'
        r'(?::[A-Z][A-Z0-9]{0,31})?)'
        r'\|([FWPETOVAHSR](?:,[FWPETOVAHSR])*)$'
    )

    def parse(self, code: str) -> CSM1Code:
        """
        Parse CSM1 code in any tier format.

        Raises:
            ValueError: If code is invalid
        """
        if code != code.strip():
            raise ValueError("CSM1 codes MUST NOT contain surrounding whitespace")

        # Try COMPACT format first
        if code.startswith('CS1|'):
            return self._parse_compact(code)

        # Try MICRO format (has namespace or version)
        if ':' in code or '@' in code:
            return self._parse_micro(code)

        # Try NANO format
        return self._parse_nano(code)

    def _parse_nano(self, code: str) -> CSM1Code:
        """Parse NANO format: N5+E+F"""
        match = self.NANO_PATTERN.fullmatch(code)
        if not match:
            raise ValueError(f"Invalid NANO CSM1 code: {code}")

        persona = match.group(1)
        adherence = int(match.group(2))
        scope_str = match.group(3)

        scopes = self._validate_scopes(
            [s for s in scope_str.split('+') if s]
        )
        if persona == 'C':
            raise ValueError("Custom persona requires a namespace")

        return CSM1Code(
            raw=code,
            persona=persona,
            persona_name=self.PERSONA_NAMES[persona],
            adherence=adherence,
            scopes=scopes,
            namespace=None,
            version=None,
        )

    def _parse_micro(self, code: str) -> CSM1Code:
        """Parse MICRO format: N5+F:ELEM@1.2.0"""
        match = self.MICRO_PATTERN.fullmatch(code)
        if not match:
            raise ValueError(f"Invalid MICRO CSM1 code: {code}")

        persona = match.group(1)
        adherence = int(match.group(2))
        scope_str = match.group(3) or ''
        namespace = match.group(4)  # May be None
        version = match.group(5)    # May be None

        scopes = self._validate_scopes(
            [s for s in scope_str.split('+') if s]
        )
        if persona == 'C' and namespace is None:
            raise ValueError("Custom persona requires a namespace")

        return CSM1Code(
            raw=code,
            persona=persona,
            persona_name=self.PERSONA_NAMES[persona],
            adherence=adherence,
            scopes=scopes,
            namespace=namespace,
            version=version,
        )

    def _parse_compact(self, code: str) -> CSM1Code:
        """Parse COMPACT format: CS1|nanny|5|family.safe.guide|E,F"""
        match = self.COMPACT_PATTERN.fullmatch(code)
        if not match:
            raise ValueError(f"Invalid COMPACT CSM1 code: {code}")

        persona_name = match.group(1).lower()
        adherence = int(match.group(2))
        uvc_token = match.group(3)
        scope_str = match.group(4)

        # Reverse lookup persona code
        persona = None
        for code, name in self.PERSONA_NAMES.items():
            if name == persona_name:
                persona = code
                break

        if not persona:
            raise ValueError(f"Unknown persona name: {persona_name}")

        scopes = self._validate_scopes(
            [s for s in scope_str.split(',') if s]
        )

        return CSM1Code(
            raw=code,
            persona=persona,
            persona_name=persona_name,
            adherence=adherence,
            scopes=scopes,
            namespace=None,  # Extracted from UVC token if needed
            version=None,
            uvc_token=uvc_token,
        )

    def validate(self, code: str) -> bool:
        """Check if CSM1 code is valid"""
        try:
            self.parse(code)
            return True
        except ValueError:
            return False
```

---

## 8. Serialization

### 8.1 Canonical Serialization

```python
def serialize_csm1(
    persona: str,
    adherence: int,
    scopes: List[str] = None,
    namespace: str = None,
    version: str = None,
    tier: str = 'micro'
) -> str:
    """
    Serialize CSM1 code to specified tier.

    Args:
        persona: Single character persona code
        adherence: Adherence level (0-5)
        scopes: List of scope codes
        namespace: Custom namespace (uppercase)
        version: Semver or alias
        tier: Output tier ('nano', 'micro', 'compact')

    Returns:
        Serialized CSM1 code
    """
    scopes = scopes or []

    if tier == 'nano':
        scope_str = ''.join(f'+{s}' for s in sorted(scopes))
        return f"{persona}{adherence}{scope_str}"

    elif tier == 'micro':
        result = f"{persona}{adherence}"
        if namespace:
            result += f":{namespace}"
        scope_str = ''.join(f'+{s}' for s in sorted(scopes))
        result += scope_str
        if version:
            result += f"@{version}"
        return result

    else:
        raise ValueError(f"Unknown tier: {tier}")


def canonical_csm1(parsed: CSM1Code) -> str:
    """
    Produce canonical form for hashing/comparison.

    Canonical form:
    - MICRO tier
    - Scopes sorted alphabetically
    - No whitespace
    - Uppercase namespace
    """
    scopes = sorted(set(parsed.scopes))
    result = f"{parsed.persona}{parsed.adherence}"

    result += ''.join(f'+{s}' for s in scopes)

    if parsed.namespace:
        result += f":{parsed.namespace.upper()}"

    if parsed.version:
        result += f"@{parsed.version}"

    return result
```

---

## 9. Examples

### 9.1 Valid CSM1 Codes

```python
# NANO format
"N5"              # ✓ Nanny, level 5
"N5+F"            # ✓ Nanny, level 5, Family scope
"N5+E+F"          # ✓ Nanny, level 5, Family + Education
"Z4+P+W"          # ✓ Sentinel, level 4, Privacy + Work
"D3+S+E"          # ✓ Mediator, level 3, Social + Education
"G4"              # ✓ Godparent, level 4

# MICRO format
"N5:ELEM"         # ✓ Nanny, level 5, ELEM namespace
"N5+E+F:ELEM"     # ✓ With scopes
"C3+W:ACME"       # ✓ Custom, ACME namespace, Work
"D3:FAIR@1.2.0"   # ✓ Mediator, FAIR namespace, version 1.2.0
"A3:CORP@latest"  # ✓ Ambassador, CORP namespace, latest version

# COMPACT format
"CS1|nanny|5|family.safe.guide|E,F"
"CS1|sentinel|4|secure.privacy.guardian|P,W"
"CS1|custom|3|company.acme.legal|O,W"
```

### 9.2 Invalid CSM1 Codes

```python
# Invalid persona
"X5+F"            # ✗ 'X' is not a valid persona

# Invalid adherence
"N6+F"            # ✗ Adherence must be 0-5
"N+F"             # ✗ Missing adherence

# Invalid scope
"N5+X"            # ✗ 'X' is not a valid scope
"N5+family"       # ✗ Scopes must be single uppercase

# Invalid namespace
"N5:elem"         # ✗ Namespace must be uppercase
"N5:TOOLONGNAMESPACE"  # ✗ Namespace max 8 chars

# Conflicting scopes
"N5+F+A"          # ✗ Family and Adult scopes MUST NOT be combined
"N5+F+F"          # ✗ Duplicate scope
"C3"              # ✗ Custom persona requires a namespace
```

### 9.3 Real-World Mapping

```python
# Common use cases
COMMON_CONFIGS = {
    # Child content
    "family_safe": "N5+E+F",

    # Corporate assistant
    "work_professional": "A3+W+P",

    # Healthcare chatbot
    "medical_assistant": "G4+H+P:MED",

    # Creative writing
    "creative_writing": "M2+A",

    # Security operations
    "security_ops": "Z4+P+T+W:SEC",

    # Educational tutor
    "education_tutor": "G3+E+F:EDU",

    # General adult
    "general_adult": "A2",

    # Dispute resolution
    "dispute_resolution": "D3+S+W:FAIR",
}
```

---

## 10. Project-Maintained Implementation

### 10.1 Complete Python Module

```python
# File: services/vcp/csm1_parser.py

"""
CSM1 (Constitutional Safety Minicode) Parser

Project-maintained implementation of CSM1 grammar specification.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
import re

__all__ = [
    'CSM1Code',
    'CSM1Parser',
    'CSM1Validator',
    'serialize_csm1',
    'parse_csm1',
    'canonical_csm1',
]


class Persona(Enum):
    """CSM1 Persona codes (NZGAMDC)"""
    NANNY = 'N'
    SENTINEL = 'Z'
    GODPARENT = 'G'
    AMBASSADOR = 'A'
    MUSE = 'M'
    MEDIATOR = 'D'
    CUSTOM = 'C'


class Scope(Enum):
    """CSM1 Scope codes"""
    FAMILY = 'F'
    WORK = 'W'
    PRIVACY = 'P'
    EDUCATION = 'E'
    TECHNICAL = 'T'
    OFFICIAL = 'O'
    VULNERABLE = 'V'
    ADULT = 'A'
    HEALTH = 'H'
    SOCIAL = 'S'
    RELIGIOUS = 'R'


@dataclass
class CSM1Code:
    """Parsed and validated CSM1 code"""

    raw: str
    persona: Persona
    adherence: int
    scopes: List[Scope] = field(default_factory=list)
    namespace: Optional[str] = None
    version: Optional[str] = None

    @property
    def persona_name(self) -> str:
        """Human-readable persona name"""
        return self.persona.name.lower()

    def to_nano(self) -> str:
        """Serialize to NANO format"""
        scope_str = ''.join(f'+{s.value}' for s in sorted(self.scopes, key=lambda x: x.value))
        return f"{self.persona.value}{self.adherence}{scope_str}"

    def to_micro(self) -> str:
        """Serialize to MICRO format"""
        result = f"{self.persona.value}{self.adherence}"
        scope_str = ''.join(f'+{s.value}' for s in sorted(self.scopes, key=lambda x: x.value))
        result += scope_str
        if self.namespace:
            result += f":{self.namespace}"
        if self.version:
            result += f"@{self.version}"
        return result

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'persona': self.persona.value,
            'persona_name': self.persona_name,
            'adherence': self.adherence,
            'scopes': [s.value for s in self.scopes],
            'namespace': self.namespace,
            'version': self.version,
        }

    def get_profile(self) -> Dict[str, Any]:
        """Get combined behavioral profile"""
        from .csm1_profiles import PERSONA_PROFILES, SCOPE_MODIFIERS, ADHERENCE_BEHAVIORS

        profile = PERSONA_PROFILES.get(self.persona.value, {}).copy()
        profile['adherence_config'] = ADHERENCE_BEHAVIORS.get(self.adherence, {})

        # Apply scope modifiers
        for scope in self.scopes:
            modifier = SCOPE_MODIFIERS.get(scope.value, {})
            for key, value in modifier.items():
                if key not in profile or isinstance(value, bool):
                    profile[key] = value
                elif isinstance(value, list):
                    profile[key] = profile.get(key, []) + value

        return profile


def parse_csm1(code: str) -> CSM1Code:
    """Convenience function to parse CSM1 code"""
    return CSM1Parser().parse(code)


def canonical_csm1(code: str) -> str:
    """Get canonical form of CSM1 code"""
    parsed = parse_csm1(code)
    return parsed.to_micro()


# Module version
__version__ = '1.0.0'
```

### 10.2 JSON Schema

Use the maintained
[VCP CSM-1 semantics schema](../../schemas/vcp-semantics-csm1.schema.json) for
JSON Schema validation. This companion does not define or ship a separate
`data/schemas/csm1-code.schema.json` contract.

---

## Appendices

### A. Quick Reference Card

```
CSM1 QUICK REFERENCE
====================

PERSONAS
--------
N = Nanny (child safety)      A = Ambassador (professional)
Z = Sentinel (security)       M = Muse (creative)
G = Godparent (ethics)        D = Mediator (fair resolution)
C = Custom

ADHERENCE (0-5)
---------------
0 = Minimal   3 = Standard
1 = Relaxed   4 = Strict
2 = Moderate  5 = Maximum

SCOPES (+X)
-----------
F = Family    O = Official   S = Social
W = Work      V = Vulnerable R = Religious
P = Privacy   A = Adult
E = Education H = Health
T = Technical

FORMAT
------
NANO:    N5+E+F
MICRO:   N5+E+F:ELEM@1.2.0
COMPACT: CS1|nanny|5|family.safe.guide|E,F
```

### B. Compatibility with VCP Bundle

```json
{
  "manifest": {
    "metadata": {
      "csm1": "N5+F:ELEM@1.2.0",
      "persona": "nanny",
      "adherence_level": 5,
      "scopes": ["family"],
      "namespace": "ELEM"
    }
  }
}
```

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-11 | Initial specification |

---

*This specification is released under CC BY 4.0. Contributions welcome.*
