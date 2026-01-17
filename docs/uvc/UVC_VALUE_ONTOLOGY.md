# UVC Value Ontology Specification

**Version**: 1.0.0
**Date**: 2026-01-11
**Layer**: 1 (UVC - Universal Value Coding)
**Status**: Complete

---

## Abstract

This specification defines the Value Ontology - a structured corpus of value statements that form the semantic foundation for UVC tokens. The ontology categorizes values, defines relationships (hierarchy, tension, complement), and provides composition rules.

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Ontology Structure](#2-ontology-structure)
3. [Value Categories](#3-value-categories)
4. [Value Statements](#4-value-statements)
5. [Relationships](#5-relationships)
6. [Query Interface](#6-query-interface)
7. [Data Format](#7-data-format)

---

## 1. Introduction

### 1.1 Purpose

The Value Ontology provides:
- **Semantic Grounding**: Values have defined meanings
- **Conflict Detection**: Identify tensions between values
- **Composition Support**: Rules for combining values
- **Cross-Cultural Bridge**: Map between traditions

### 1.2 Foundations

The ontology draws from:
- **Moral Foundations Theory** (Haidt): Care, Fairness, Loyalty, Authority, Sanctity
- **Schwartz Values**: 10 basic human values
- **Virtue Ethics**: Character-based values
- **Deontological Ethics**: Duty-based values
- **Consequentialist Ethics**: Outcome-based values

---

## 2. Ontology Structure

### 2.1 Hierarchy

```
Value Ontology
├── Categories (7)
│   ├── Values (multiple per category)
│   │   ├── Value Statements (~500 total)
│   │   │   ├── Core (always apply)
│   │   │   ├── Important (generally apply)
│   │   │   └── Contextual (situation-dependent)
```

### 2.2 Schema

```json
{
  "$schema": "https://vcp.creed.space/schema/ontology/v1.json",
  "ontology_version": "1.0.0",
  "value_categories": [...],
  "value_statements": [...],
  "relationships": {
    "hierarchy": [...],
    "tensions": [...],
    "complements": [...]
  },
  "composition_rules": {...}
}
```

---

## 3. Value Categories

### 3.1 The Seven Categories

| ID | Name | Description | Foundation |
|----|------|-------------|------------|
| `care` | Care and Compassion | Caring for others, reducing harm | Moral Foundations |
| `fairness` | Fairness and Justice | Equitable treatment, rights | Moral Foundations |
| `autonomy` | Autonomy and Freedom | Self-determination, liberty | Liberal Ethics |
| `truth` | Truth and Honesty | Accuracy, transparency | Virtue Ethics |
| `loyalty` | Loyalty and Belonging | Group commitment, tradition | Moral Foundations |
| `authority` | Authority and Order | Hierarchy, social order | Moral Foundations |
| `sanctity` | Sanctity and Purity | Sacredness, dignity | Moral Foundations |

### 3.2 Category Definitions

```python
VALUE_CATEGORIES = {
    'care': {
        'name': 'Care and Compassion',
        'description': 'Values related to caring for others and reducing harm',
        'children': ['protection', 'nurturing', 'healing', 'support'],
        'traditions': ['care_ethics', 'buddhism', 'christianity'],
        'emoji': '❤️',
    },

    'fairness': {
        'name': 'Fairness and Justice',
        'description': 'Values related to equitable treatment and rights',
        'children': ['equality', 'reciprocity', 'rights', 'due_process'],
        'traditions': ['liberalism', 'egalitarianism', 'kantian'],
        'emoji': '⚖️',
    },

    'autonomy': {
        'name': 'Autonomy and Freedom',
        'description': 'Values related to self-determination and liberty',
        'children': ['consent', 'privacy', 'self_expression', 'choice'],
        'traditions': ['liberalism', 'existentialism', 'enlightenment'],
        'emoji': '🗽',
    },

    'truth': {
        'name': 'Truth and Honesty',
        'description': 'Values related to accuracy and transparency',
        'children': ['honesty', 'transparency', 'accuracy', 'authenticity'],
        'traditions': ['virtue_ethics', 'scientific_realism', 'pragmatism'],
        'emoji': '💡',
    },

    'loyalty': {
        'name': 'Loyalty and Belonging',
        'description': 'Values related to group membership and commitment',
        'children': ['fidelity', 'patriotism', 'tradition', 'community'],
        'traditions': ['communitarianism', 'confucianism', 'nationalism'],
        'emoji': '🤝',
    },

    'authority': {
        'name': 'Authority and Order',
        'description': 'Values related to hierarchy and social order',
        'children': ['respect', 'obedience', 'duty', 'discipline'],
        'traditions': ['conservatism', 'confucianism', 'military_ethics'],
        'emoji': '👑',
    },

    'sanctity': {
        'name': 'Sanctity and Purity',
        'description': 'Values related to sacredness and moral purity',
        'children': ['cleanliness', 'temperance', 'reverence', 'dignity'],
        'traditions': ['religious_ethics', 'stoicism', 'natural_law'],
        'emoji': '✨',
    },
}
```

---

## 4. Value Statements

### 4.1 Statement Structure

```python
@dataclass
class ValueStatement:
    """A single value statement in the ontology"""

    id: str                     # Unique identifier
    statement: str              # Natural language statement
    category: str               # Category path (e.g., "care.protection")
    strength: str               # "core", "important", "contextual"
    traditions: List[str]       # Cultural/philosophical origins
    conflicts_with: List[str]   # IDs of conflicting values
    complements: List[str]      # IDs of complementary values
    contexts: List[str]         # When this applies
```

### 4.2 Core Value Statements

```python
CORE_VALUES = [
    {
        'id': 'protect_life',
        'statement': 'Protect human life and physical safety',
        'category': 'care.protection',
        'strength': 'core',
        'traditions': ['hippocratic', 'human_rights', 'natural_law'],
        'conflicts_with': [],
        'complements': ['prevent_harm', 'support_vulnerable'],
    },
    {
        'id': 'prevent_harm',
        'statement': 'Prevent unnecessary harm to persons',
        'category': 'care.protection',
        'strength': 'core',
        'traditions': ['consequentialism', 'care_ethics'],
        'conflicts_with': [],
        'complements': ['protect_life', 'heal_injured'],
    },
    {
        'id': 'respect_autonomy',
        'statement': 'Respect individual autonomy and self-determination',
        'category': 'autonomy.consent',
        'strength': 'core',
        'traditions': ['kantian', 'liberalism'],
        'conflicts_with': ['protect_vulnerable'],  # Tension
        'complements': ['ensure_consent', 'protect_privacy'],
    },
    {
        'id': 'maintain_honesty',
        'statement': 'Communicate truthfully and avoid deception',
        'category': 'truth.honesty',
        'strength': 'core',
        'traditions': ['virtue_ethics', 'kantian'],
        'conflicts_with': ['protect_feelings'],  # Tension
        'complements': ['be_transparent', 'acknowledge_uncertainty'],
    },
    {
        'id': 'ensure_fairness',
        'statement': 'Treat individuals fairly and without discrimination',
        'category': 'fairness.equality',
        'strength': 'core',
        'traditions': ['egalitarianism', 'justice_theory'],
        'conflicts_with': [],
        'complements': ['respect_rights', 'apply_consistently'],
    },
]
```

### 4.3 Domain-Specific Values

```python
# Child Safety (family.* domain)
CHILD_SAFETY_VALUES = [
    {
        'id': 'child_protection_absolute',
        'statement': 'Prioritize child safety above other considerations',
        'category': 'care.protection',
        'strength': 'core',
        'contexts': ['children_present', 'minor_users'],
        'traditions': ['child_welfare', 'parens_patriae'],
    },
    {
        'id': 'age_appropriate_content',
        'statement': 'Ensure content is appropriate for the audience age',
        'category': 'care.nurturing',
        'strength': 'important',
        'contexts': ['children_present'],
    },
]

# Professional (work.* domain)
PROFESSIONAL_VALUES = [
    {
        'id': 'maintain_confidentiality',
        'statement': 'Protect confidential information',
        'category': 'authority.duty',
        'strength': 'core',
        'contexts': ['professional', 'legal'],
    },
    {
        'id': 'avoid_conflicts_interest',
        'statement': 'Avoid and disclose conflicts of interest',
        'category': 'fairness.reciprocity',
        'strength': 'important',
        'contexts': ['professional', 'fiduciary'],
    },
]

# Healthcare (context: health)
HEALTHCARE_VALUES = [
    {
        'id': 'do_no_harm',
        'statement': 'Primum non nocere - First, do no harm',
        'category': 'care.healing',
        'strength': 'core',
        'contexts': ['medical', 'health'],
        'traditions': ['hippocratic'],
    },
    {
        'id': 'informed_consent_medical',
        'statement': 'Obtain informed consent for medical decisions',
        'category': 'autonomy.consent',
        'strength': 'core',
        'contexts': ['medical'],
    },
]
```

---

## 5. Relationships

### 5.1 Hierarchy Relationships

```python
VALUE_HIERARCHY = [
    # Category → Subcategory
    {'parent': 'care', 'child': 'protection', 'relation': 'subsumes'},
    {'parent': 'care', 'child': 'nurturing', 'relation': 'subsumes'},
    {'parent': 'care', 'child': 'healing', 'relation': 'subsumes'},

    # Subcategory → Specific value
    {'parent': 'protection', 'child': 'child_safety', 'relation': 'specializes'},
    {'parent': 'protection', 'child': 'physical_safety', 'relation': 'specializes'},
    {'parent': 'protection', 'child': 'data_protection', 'relation': 'specializes'},

    # Value → Implementation
    {'parent': 'honesty', 'child': 'no_deception', 'relation': 'implements'},
    {'parent': 'honesty', 'child': 'acknowledge_uncertainty', 'relation': 'implements'},
]
```

### 5.2 Tension Relationships

Values in tension can both be held, but may conflict in specific situations:

```python
VALUE_TENSIONS = [
    {
        'values': ['autonomy', 'protection'],
        'description': 'Protecting someone may limit their autonomy',
        'resolution': 'Consider capacity, severity of harm, reversibility',
        'examples': [
            'Medical intervention for incapacitated patient',
            'Restricting content for child safety',
        ],
    },
    {
        'values': ['honesty', 'care'],
        'description': 'Truth may cause harm (e.g., blunt medical prognosis)',
        'resolution': 'Tactful truth, timing, compassionate delivery',
        'examples': [
            'Delivering bad news to patient',
            'Honest feedback that may hurt',
        ],
    },
    {
        'values': ['loyalty', 'fairness'],
        'description': 'Loyalty to group may conflict with fair treatment of outsiders',
        'resolution': 'Universal principles take precedence over group loyalty',
        'examples': [
            'Nepotism vs merit-based hiring',
            'Whistleblowing on group wrongdoing',
        ],
    },
    {
        'values': ['authority', 'autonomy'],
        'description': 'Respecting authority may limit individual freedom',
        'resolution': 'Legitimate authority respects core rights',
        'examples': [
            'Following unjust orders',
            'Challenging organizational policies',
        ],
    },
    {
        'values': ['privacy', 'transparency'],
        'description': 'Privacy rights may conflict with need for transparency',
        'resolution': 'Public interest test, minimize privacy intrusion',
        'examples': [
            'Public records vs personal privacy',
            'Whistleblower protection',
        ],
    },
]
```

### 5.3 Complement Relationships

Values that work together:

```python
VALUE_COMPLEMENTS = [
    {
        'values': ['honesty', 'transparency'],
        'description': 'Both support openness and truthfulness',
    },
    {
        'values': ['care', 'fairness'],
        'description': 'Caring fairly for all',
    },
    {
        'values': ['autonomy', 'informed_consent'],
        'description': 'Consent requires autonomy; autonomy enables consent',
    },
    {
        'values': ['loyalty', 'trust'],
        'description': 'Loyalty builds trust; trust enables loyalty',
    },
]
```

---

## 6. Query Interface

### 6.1 Query API

```python
class ValueOntology:
    """Query interface for value ontology"""

    def __init__(self, data_path: str = None):
        self.data = load_ontology(data_path)

    def get_value(self, value_id: str) -> ValueStatement:
        """Get a specific value by ID"""
        pass

    def get_category(self, category_id: str) -> Category:
        """Get a category and its values"""
        pass

    def find_by_category(self, category: str) -> List[ValueStatement]:
        """Find all values in a category"""
        pass

    def find_conflicts(self, value_id: str) -> List[Tension]:
        """Find values that conflict with given value"""
        pass

    def find_complements(self, value_id: str) -> List[str]:
        """Find values that complement given value"""
        pass

    def check_composition(self, value_ids: List[str]) -> CompositionResult:
        """
        Check if values can be composed together.

        Returns:
            CompositionResult with conflicts, tensions, and suggestions
        """
        pass

    def translate(self, value_id: str, tradition: str) -> str:
        """
        Find equivalent expression in different tradition.

        e.g., translate("protect_vulnerable", "buddhist") → "karuṇā (compassion)"
        """
        pass

    def search(self, query: str) -> List[ValueStatement]:
        """Full-text search of value statements"""
        pass
```

### 6.2 Composition Check

```python
@dataclass
class CompositionResult:
    """Result of checking value composition"""

    compatible: bool
    values: List[str]
    conflicts: List[Conflict]       # Direct conflicts (incompatible)
    tensions: List[Tension]         # Tensions (require resolution)
    suggestions: List[str]          # Resolution suggestions

    def has_blocking_conflicts(self) -> bool:
        """Check if any conflicts prevent composition"""
        return len(self.conflicts) > 0

    def get_resolution_hints(self) -> List[str]:
        """Get hints for resolving tensions"""
        hints = []
        for tension in self.tensions:
            hints.append(tension.resolution)
        return hints
```

---

## 7. Data Format

### 7.1 JSON Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://vcp.creed.space/schema/ontology/v1.json",
  "title": "UVC Value Ontology",
  "type": "object",
  "required": ["ontology_version", "value_categories", "value_statements"],
  "properties": {
    "ontology_version": {
      "type": "string",
      "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"
    },
    "value_categories": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "name", "description"],
        "properties": {
          "id": {"type": "string"},
          "name": {"type": "string"},
          "description": {"type": "string"},
          "children": {
            "type": "array",
            "items": {"type": "string"}
          }
        }
      }
    },
    "value_statements": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "statement", "category"],
        "properties": {
          "id": {"type": "string"},
          "statement": {"type": "string", "maxLength": 256},
          "category": {"type": "string"},
          "strength": {"enum": ["core", "important", "contextual"]},
          "traditions": {
            "type": "array",
            "items": {"type": "string"}
          },
          "conflicts_with": {
            "type": "array",
            "items": {"type": "string"}
          },
          "complements": {
            "type": "array",
            "items": {"type": "string"}
          }
        }
      }
    },
    "relationships": {
      "type": "object",
      "properties": {
        "hierarchy": {"type": "array"},
        "tensions": {"type": "array"},
        "complements": {"type": "array"}
      }
    }
  }
}
```

### 7.2 Example Data File

See `data/uvc_ontology.json` for the complete ontology data.

---

## Appendices

### A. Moral Foundations Mapping

| Moral Foundation | UVC Category | Key Values |
|-----------------|--------------|------------|
| Care/Harm | care | protect_life, prevent_harm, nurture |
| Fairness/Cheating | fairness | equality, reciprocity, justice |
| Loyalty/Betrayal | loyalty | fidelity, patriotism, group_care |
| Authority/Subversion | authority | respect, obedience, duty |
| Sanctity/Degradation | sanctity | purity, dignity, reverence |
| Liberty/Oppression | autonomy | freedom, consent, self_determination |

### B. Cross-Tradition Equivalents

| UVC Value | Western | Buddhist | Confucian | Islamic |
|-----------|---------|----------|-----------|---------|
| protect_life | Sanctity of life | Ahimsa | Ren (仁) | Hifz al-nafs |
| honesty | Veracity | Sacca | Xin (信) | Sidq |
| respect_elders | Filial piety | - | Xiao (孝) | Birr al-walidayn |
| justice | Fairness | - | Yi (义) | 'Adl |

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-11 | Initial specification |

---

*This specification is released under CC BY 4.0. Contributions welcome.*
