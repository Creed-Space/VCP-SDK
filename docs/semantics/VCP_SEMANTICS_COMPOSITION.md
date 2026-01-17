# VCP-Semantics: Constitution Composition Specification

**Version**: 1.0.0
**Date**: 2026-01-11
**Layer**: VCP/S (Semantics)
**Status**: Complete

> *Part of the Value-Context Protocol (VCP) - Layer 3*

---

## Abstract

This specification defines how multiple constitutions are composed into a coherent behavioral policy. It covers composition modes, layer precedence, conflict detection, and merge semantics.

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Composition Modes](#2-composition-modes)
3. [Layer Precedence](#3-layer-precedence)
4. [Conflict Detection](#4-conflict-detection)
5. [Merge Semantics](#5-merge-semantics)
6. [Resolution Strategies](#6-resolution-strategies)
7. [Examples](#7-examples)
8. [Reference Implementation](#8-reference-implementation)

---

## 1. Introduction

### 1.1 Purpose

Constitution Composition enables:
- **Layered Rules**: Platform defaults + domain rules + user customizations
- **Conflict Resolution**: Deterministic handling of rule conflicts
- **Extensibility**: Build on base constitutions without modification
- **Override Control**: Fine-grained control over which rules take precedence

### 1.2 Use Cases

1. **Platform + Domain**: Creed Space defaults + industry-specific rules
2. **Base + Custom**: Standard constitution + organization customizations
3. **Parent + Child**: Family rules + individual child preferences
4. **Emergency Override**: Normal rules + emergency context rules

### 1.3 Design Principles

1. **Explicit over Implicit**: Composition mode must be declared
2. **Fail-Safe**: Conflicts in strict mode fail rather than silently merge
3. **Auditable**: Composition steps are logged
4. **Reversible**: Can trace back to source constitutions

---

## 2. Composition Modes

### 2.1 Mode Definitions

```python
from enum import Enum

class CompositionMode(Enum):
    """
    How constitutions compose with each other.

    BASE: Foundation that cannot be overridden (strongest)
    EXTEND: Adds rules, conflicts are errors
    OVERRIDE: Later layers override earlier (common)
    STRICT: Any conflict is an error
    """

    BASE = "base"
    EXTEND = "extend"
    OVERRIDE = "override"
    STRICT = "strict"
```

### 2.2 Mode Behaviors

| Mode | On Conflict | On Add | On Remove | Use Case |
|------|-------------|--------|-----------|----------|
| **BASE** | Error | Allowed | Not allowed | Platform safety rules |
| **EXTEND** | Error | Allowed | Not allowed | Add domain-specific |
| **OVERRIDE** | Later wins | Allowed | Allowed | User customization |
| **STRICT** | Error | Allowed | Not allowed | High-stakes contexts |

### 2.3 Mode Declaration

In constitution manifest:

```json
{
  "manifest": {
    "composition": {
      "mode": "extend",
      "base_ref": "creed://creed.space/family.safe.guide@1.2.0",
      "conflict_strategy": "fail"
    }
  }
}
```

---

## 3. Layer Precedence

### 3.1 Standard Layers

```
Layer 4: Session Override  (highest precedence)
         ↑
Layer 3: User Customization
         ↑
Layer 2: Domain Rules
         ↑
Layer 1: Safety Foundations
         ↑
Layer 0: Platform Defaults (lowest precedence)
```

### 3.2 Layer Definitions

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class ConstitutionLayer:
    """A constitution with its layer information"""

    constitution: 'Constitution'
    layer: int                      # 0-4
    mode: CompositionMode
    source: str                     # Where this came from

    @staticmethod
    def platform_defaults() -> 'ConstitutionLayer':
        """Layer 0: Platform defaults"""
        return ConstitutionLayer(
            constitution=load_platform_defaults(),
            layer=0,
            mode=CompositionMode.BASE,
            source="platform",
        )

    @staticmethod
    def safety_foundation(ref: str) -> 'ConstitutionLayer':
        """Layer 1: Safety foundations (UEF, etc.)"""
        return ConstitutionLayer(
            constitution=load_constitution(ref),
            layer=1,
            mode=CompositionMode.BASE,
            source=ref,
        )

    @staticmethod
    def domain_rules(ref: str) -> 'ConstitutionLayer':
        """Layer 2: Domain-specific rules"""
        return ConstitutionLayer(
            constitution=load_constitution(ref),
            layer=2,
            mode=CompositionMode.EXTEND,
            source=ref,
        )

    @staticmethod
    def user_customization(ref: str) -> 'ConstitutionLayer':
        """Layer 3: User customizations"""
        return ConstitutionLayer(
            constitution=load_constitution(ref),
            layer=3,
            mode=CompositionMode.OVERRIDE,
            source=ref,
        )

    @staticmethod
    def session_override(constitution: 'Constitution') -> 'ConstitutionLayer':
        """Layer 4: Session-specific overrides"""
        return ConstitutionLayer(
            constitution=constitution,
            layer=4,
            mode=CompositionMode.OVERRIDE,
            source="session",
        )
```

### 3.3 Precedence Rules

1. **Higher layer wins** (in OVERRIDE mode)
2. **BASE layers cannot be overridden** (errors if attempted)
3. **Within same layer**, last applied wins
4. **STRICT mode** rejects any conflicts regardless of layer

---

## 4. Conflict Detection

### 4.1 What Constitutes a Conflict

```python
@dataclass
class ConflictType(Enum):
    """Types of conflicts between constitutions"""

    # Direct conflicts
    EXPLICIT = "explicit"           # One declares conflict with other
    CONTRADICTORY = "contradictory" # Rules directly contradict
    OVERRIDE_BASE = "override_base" # Attempting to override BASE mode

    # Semantic conflicts
    VALUE_TENSION = "value_tension" # Values in tension (from ontology)
    SCOPE_MISMATCH = "scope_mismatch" # Incompatible scopes

    # Structural conflicts
    VERSION_INCOMPATIBLE = "version_incompatible"
    CIRCULAR_DEPENDENCY = "circular_dependency"


@dataclass
class Conflict:
    """Detected conflict between constitutions"""

    type: ConflictType
    constitution_a: str
    constitution_b: str
    rule_a: Optional[str]
    rule_b: Optional[str]
    description: str
    resolution_hint: Optional[str]
```

### 4.2 Conflict Detection Algorithm

```python
class ConflictDetector:
    """Detect conflicts between constitutions"""

    def __init__(self, value_ontology: 'ValueOntology' = None):
        self.ontology = value_ontology or load_default_ontology()

    def detect(self, constitutions: List['Constitution']) -> List[Conflict]:
        """
        Detect all conflicts between constitutions.

        Checks:
        1. Explicit conflict declarations
        2. Value ontology tensions
        3. Rule contradictions (semantic analysis)
        4. Mode violations (override BASE)
        """
        conflicts = []

        for i, a in enumerate(constitutions):
            for b in constitutions[i+1:]:
                conflicts.extend(self._check_pair(a, b))

        return conflicts

    def _check_pair(
        self,
        a: 'Constitution',
        b: 'Constitution'
    ) -> List[Conflict]:
        """Check for conflicts between two constitutions"""
        conflicts = []

        # 1. Explicit conflict declarations
        if b.id in a.manifest.get('conflicts_with', []):
            conflicts.append(Conflict(
                type=ConflictType.EXPLICIT,
                constitution_a=a.id,
                constitution_b=b.id,
                rule_a=None,
                rule_b=None,
                description=f"{a.id} explicitly declares conflict with {b.id}",
                resolution_hint="These constitutions cannot be combined",
            ))

        # 2. Value ontology conflicts
        a_values = self._extract_values(a)
        b_values = self._extract_values(b)

        for av in a_values:
            for bv in b_values:
                if self.ontology.conflicts(av, bv):
                    conflicts.append(Conflict(
                        type=ConflictType.VALUE_TENSION,
                        constitution_a=a.id,
                        constitution_b=b.id,
                        rule_a=av,
                        rule_b=bv,
                        description=f"Value tension: {av} conflicts with {bv}",
                        resolution_hint=self.ontology.get_resolution(av, bv),
                    ))

        # 3. Mode violations
        if a.mode == CompositionMode.BASE and b.mode == CompositionMode.OVERRIDE:
            # Check if b attempts to override a's rules
            for rule in b.rules:
                if self._overrides_rule(rule, a):
                    conflicts.append(Conflict(
                        type=ConflictType.OVERRIDE_BASE,
                        constitution_a=a.id,
                        constitution_b=b.id,
                        rule_a=None,
                        rule_b=rule.id,
                        description=f"Cannot override BASE constitution rule",
                        resolution_hint="Remove override or change BASE constitution",
                    ))

        # 4. Scope conflicts
        if not self._scopes_compatible(a.scopes, b.scopes):
            conflicts.append(Conflict(
                type=ConflictType.SCOPE_MISMATCH,
                constitution_a=a.id,
                constitution_b=b.id,
                rule_a=None,
                rule_b=None,
                description=f"Incompatible scopes: {a.scopes} vs {b.scopes}",
                resolution_hint="Remove conflicting scope",
            ))

        return conflicts

    def _extract_values(self, constitution: 'Constitution') -> List[str]:
        """Extract value IDs from constitution"""
        values = []
        for rule in constitution.rules:
            values.extend(rule.get('values', []))
        return values

    def _scopes_compatible(self, scopes_a: List[str], scopes_b: List[str]) -> bool:
        """Check if scope lists are compatible"""
        INCOMPATIBLE_PAIRS = {
            frozenset({'F', 'A'}),  # Family and Adult
            frozenset({'V', 'A'}),  # Vulnerable and Adult
        }

        combined = set(scopes_a) | set(scopes_b)
        for pair in INCOMPATIBLE_PAIRS:
            if pair <= combined:
                return False
        return True

    def _overrides_rule(self, new_rule, base_constitution) -> bool:
        """Check if new rule overrides a base constitution rule"""
        for base_rule in base_constitution.rules:
            if new_rule.id == base_rule.id:
                return True
            if new_rule.topic == base_rule.topic and new_rule.action != base_rule.action:
                return True
        return False
```

---

## 5. Merge Semantics

### 5.1 Merge Algorithm

```python
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class MergedConstitution:
    """Result of merging multiple constitutions"""

    # Merged content
    rules: List['Rule'] = field(default_factory=list)
    values: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Provenance
    sources: List[str] = field(default_factory=list)
    layers_applied: List[int] = field(default_factory=list)

    # Merge info
    conflicts_resolved: List['Conflict'] = field(default_factory=list)
    merge_log: List[str] = field(default_factory=list)


class ConstitutionMerger:
    """Merge multiple constitutions according to composition rules"""

    def __init__(self, conflict_detector: ConflictDetector = None):
        self.detector = conflict_detector or ConflictDetector()

    def merge(
        self,
        layers: List[ConstitutionLayer],
        strict: bool = False,
    ) -> MergedConstitution:
        """
        Merge constitution layers into single effective constitution.

        Args:
            layers: List of constitution layers (will be sorted by layer)
            strict: If True, any conflict raises error

        Returns:
            MergedConstitution with all rules merged

        Raises:
            CompositionError: If conflicts in strict mode or BASE violated
        """
        # Sort by layer
        sorted_layers = sorted(layers, key=lambda l: l.layer)

        # Initialize result
        merged = MergedConstitution()

        for layer in sorted_layers:
            const = layer.constitution
            mode = layer.mode

            # Log
            merged.merge_log.append(
                f"Applying {const.id} at layer {layer.layer} mode={mode.value}"
            )

            if mode == CompositionMode.BASE:
                self._apply_base(merged, const, layer)

            elif mode == CompositionMode.EXTEND:
                self._apply_extend(merged, const, layer, strict)

            elif mode == CompositionMode.OVERRIDE:
                self._apply_override(merged, const, layer, strict)

            elif mode == CompositionMode.STRICT:
                self._apply_strict(merged, const, layer)

            merged.sources.append(const.id)
            merged.layers_applied.append(layer.layer)

        return merged

    def _apply_base(
        self,
        merged: MergedConstitution,
        const: 'Constitution',
        layer: ConstitutionLayer
    ):
        """Apply BASE constitution (cannot be overridden)"""
        for rule in const.rules:
            # Mark rule as base (cannot be removed or overridden)
            rule_copy = rule.copy()
            rule_copy.metadata['_base'] = True
            rule_copy.metadata['_source'] = const.id
            merged.rules.append(rule_copy)

        merged.values.extend(const.values)
        merged.merge_log.append(f"  Added {len(const.rules)} BASE rules")

    def _apply_extend(
        self,
        merged: MergedConstitution,
        const: 'Constitution',
        layer: ConstitutionLayer,
        strict: bool
    ):
        """Apply EXTEND constitution (adds rules, conflicts are errors)"""

        # Check for conflicts with existing rules
        conflicts = self._check_conflicts(merged, const)

        if conflicts:
            if strict:
                raise CompositionError(
                    f"Conflicts in EXTEND mode: {conflicts[0].description}"
                )
            # In non-strict, log but continue
            merged.conflicts_resolved.extend(conflicts)
            merged.merge_log.append(f"  Warning: {len(conflicts)} conflicts detected")

        # Add new rules (don't replace existing)
        for rule in const.rules:
            if not self._rule_exists(merged, rule):
                rule_copy = rule.copy()
                rule_copy.metadata['_source'] = const.id
                merged.rules.append(rule_copy)

        merged.values.extend(const.values)
        merged.merge_log.append(f"  Extended with {len(const.rules)} rules")

    def _apply_override(
        self,
        merged: MergedConstitution,
        const: 'Constitution',
        layer: ConstitutionLayer,
        strict: bool
    ):
        """Apply OVERRIDE constitution (later wins)"""

        for rule in const.rules:
            # Check if overriding a BASE rule
            base_rule = self._find_base_rule(merged, rule)
            if base_rule:
                raise CompositionError(
                    f"Cannot override BASE rule: {base_rule.id}"
                )

            # Remove any existing rule with same ID/topic
            merged.rules = [r for r in merged.rules if not self._rules_conflict(r, rule)]

            # Add new rule
            rule_copy = rule.copy()
            rule_copy.metadata['_source'] = const.id
            merged.rules.append(rule_copy)

        # Override values (union with dedup)
        merged.values = list(set(merged.values) | set(const.values))
        merged.merge_log.append(f"  Applied {len(const.rules)} overriding rules")

    def _apply_strict(
        self,
        merged: MergedConstitution,
        const: 'Constitution',
        layer: ConstitutionLayer
    ):
        """Apply STRICT constitution (any conflict is error)"""

        # Check for any conflicts
        conflicts = self._check_conflicts(merged, const)
        if conflicts:
            raise CompositionError(
                f"Conflict in STRICT mode: {conflicts[0].description}"
            )

        # Add all rules
        for rule in const.rules:
            rule_copy = rule.copy()
            rule_copy.metadata['_source'] = const.id
            merged.rules.append(rule_copy)

        merged.values.extend(const.values)
        merged.merge_log.append(f"  Strictly added {len(const.rules)} rules")

    def _check_conflicts(
        self,
        merged: MergedConstitution,
        const: 'Constitution'
    ) -> List[Conflict]:
        """Check for conflicts between merged state and new constitution"""
        # Create pseudo-constitution from merged state
        pseudo = Constitution(
            id='_merged',
            rules=merged.rules,
            values=merged.values,
        )
        return self.detector.detect([pseudo, const])

    def _rule_exists(self, merged: MergedConstitution, rule: 'Rule') -> bool:
        """Check if equivalent rule already exists"""
        for existing in merged.rules:
            if existing.id == rule.id:
                return True
        return False

    def _find_base_rule(
        self,
        merged: MergedConstitution,
        rule: 'Rule'
    ) -> Optional['Rule']:
        """Find BASE rule that would be overridden"""
        for existing in merged.rules:
            if existing.metadata.get('_base') and self._rules_conflict(existing, rule):
                return existing
        return None

    def _rules_conflict(self, rule_a: 'Rule', rule_b: 'Rule') -> bool:
        """Check if two rules conflict"""
        return rule_a.id == rule_b.id or (
            rule_a.topic == rule_b.topic and
            rule_a.action != rule_b.action
        )
```

---

## 6. Resolution Strategies

### 6.1 Built-in Strategies

```python
class ConflictResolutionStrategy(Enum):
    """Strategies for resolving conflicts"""

    FAIL = "fail"                   # Raise error
    FIRST_WINS = "first_wins"       # Keep first rule
    LAST_WINS = "last_wins"         # Keep last rule
    HIGHER_LAYER = "higher_layer"   # Higher layer wins
    STRICTER = "stricter"           # More restrictive wins
    PERMISSIVE = "permissive"       # More permissive wins
    MANUAL = "manual"               # Require explicit resolution


class ConflictResolver:
    """Resolve conflicts according to strategy"""

    def resolve(
        self,
        conflict: Conflict,
        strategy: ConflictResolutionStrategy,
        context: Dict = None,
    ) -> 'Resolution':
        """
        Resolve a conflict using specified strategy.

        Returns which rule to keep and why.
        """
        if strategy == ConflictResolutionStrategy.FAIL:
            raise CompositionError(f"Conflict: {conflict.description}")

        if strategy == ConflictResolutionStrategy.FIRST_WINS:
            return Resolution(
                winner=conflict.constitution_a,
                loser=conflict.constitution_b,
                reason="First constitution wins (FIRST_WINS strategy)",
            )

        if strategy == ConflictResolutionStrategy.LAST_WINS:
            return Resolution(
                winner=conflict.constitution_b,
                loser=conflict.constitution_a,
                reason="Last constitution wins (LAST_WINS strategy)",
            )

        if strategy == ConflictResolutionStrategy.STRICTER:
            # Compare strictness based on adherence levels or rule content
            stricter = self._compare_strictness(
                conflict.rule_a, conflict.rule_b
            )
            return Resolution(
                winner=stricter,
                loser=conflict.constitution_a if stricter == conflict.constitution_b else conflict.constitution_b,
                reason="Stricter rule wins (STRICTER strategy)",
            )

        if strategy == ConflictResolutionStrategy.MANUAL:
            raise ManualResolutionRequired(conflict)

        raise ValueError(f"Unknown strategy: {strategy}")

    def _compare_strictness(self, rule_a, rule_b) -> str:
        """Compare which rule is stricter"""
        # Implementation depends on rule structure
        # Generally: more restrictions = stricter
        pass
```

### 6.2 Custom Resolution

```python
@dataclass
class CustomResolution:
    """Custom conflict resolution defined in constitution"""

    conflict_pattern: str           # Pattern to match conflicts
    resolution_action: str          # What to do
    resolved_rule: Optional['Rule'] # If creating new rule
    rationale: str


class ConstitutionWithResolutions:
    """Constitution that includes conflict resolution rules"""

    def __init__(self, constitution: 'Constitution'):
        self.constitution = constitution
        self.resolutions = self._extract_resolutions()

    def _extract_resolutions(self) -> List[CustomResolution]:
        """Extract resolution rules from constitution metadata"""
        resolutions = []
        for res_spec in self.constitution.manifest.get('conflict_resolutions', []):
            resolutions.append(CustomResolution(
                conflict_pattern=res_spec['pattern'],
                resolution_action=res_spec['action'],
                resolved_rule=res_spec.get('rule'),
                rationale=res_spec.get('rationale', ''),
            ))
        return resolutions

    def resolve(self, conflict: Conflict) -> Optional['Resolution']:
        """Try to resolve conflict using custom resolutions"""
        for res in self.resolutions:
            if self._matches_pattern(conflict, res.conflict_pattern):
                return self._apply_resolution(conflict, res)
        return None
```

---

## 7. Examples

### 7.1 Simple Extension

```python
# Base: Family safety rules
base = ConstitutionLayer.safety_foundation(
    "creed://creed.space/family.safe.guide@1.2.0"
)

# Extension: Educational context
extension = ConstitutionLayer.domain_rules(
    "creed://creed.space/education.learning@1.0.0"
)

# Merge
merger = ConstitutionMerger()
result = merger.merge([base, extension])

# Result: All base rules + education rules added
# No conflicts because EXTEND mode doesn't override
```

### 7.2 User Override

```python
# Base safety
safety = ConstitutionLayer.safety_foundation(
    "creed://creed.space/uef@1.0.0"  # Universal Ethics Foundation
)

# Domain rules
domain = ConstitutionLayer.domain_rules(
    "creed://creed.space/work.professional@1.0.0"
)

# User customization (allows more creativity)
user = ConstitutionLayer.user_customization(
    "user://alice/work.creative@1.0.0"  # Relaxes some work rules
)

# Merge
result = merger.merge([safety, domain, user])

# Result:
# - Safety rules (BASE) remain
# - Domain rules extended
# - User rules override domain where they conflict
# - Safety rules CANNOT be overridden
```

### 7.3 Conflict Resolution

```python
# Two constitutions with conflicting rules
const_a = load_constitution("family.strict")  # No violent content
const_b = load_constitution("education.history")  # May discuss historical violence

# Detect conflicts
conflicts = detector.detect([const_a, const_b])
# Conflict: violence rule conflicts

# Resolution strategy
resolution = resolver.resolve(
    conflicts[0],
    strategy=ConflictResolutionStrategy.STRICTER
)
# Result: family.strict rule wins (stricter)

# Or with custom resolution in constitution:
const_b_manifest = {
    "conflict_resolutions": [
        {
            "pattern": "topic:violence",
            "action": "qualify",
            "rule": {
                "topic": "violence",
                "action": "allow",
                "conditions": ["educational_context", "historical_accuracy"]
            },
            "rationale": "Historical education may discuss violence in context"
        }
    ]
}
```

### 7.4 Multi-Layer Composition

```json
{
  "composition": {
    "layers": [
      {
        "ref": "creed://creed.space/uef@1.0.0",
        "layer": 1,
        "mode": "base",
        "description": "Universal Ethics Foundation"
      },
      {
        "ref": "creed://creed.space/family.safe.guide@1.2.0",
        "layer": 1,
        "mode": "base",
        "description": "Family safety rules"
      },
      {
        "ref": "creed://company.acme/internal.policies@2.0.0",
        "layer": 2,
        "mode": "extend",
        "description": "Company-specific policies"
      },
      {
        "ref": "user://alice/personal.preferences@1.0.0",
        "layer": 3,
        "mode": "override",
        "description": "User preferences"
      }
    ],
    "conflict_strategy": "higher_layer",
    "strict": false
  }
}
```

---

## 8. Reference Implementation

### 8.1 Complete Module

```python
# File: services/vcp/composition.py

"""
Constitution Composition Implementation

Reference implementation for merging constitutions.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional

__all__ = [
    'CompositionMode',
    'ConstitutionLayer',
    'ConflictDetector',
    'ConstitutionMerger',
    'MergedConstitution',
    'Conflict',
    'ConflictType',
    'CompositionError',
]


class CompositionError(Exception):
    """Composition failed due to conflict or mode violation"""

    def __init__(self, message: str, conflict: 'Conflict' = None):
        super().__init__(message)
        self.conflict = conflict


# ... (all classes from above)


def merge_constitutions(
    constitutions: List[str],
    modes: List[str] = None,
    strict: bool = False,
) -> MergedConstitution:
    """
    Convenience function to merge constitutions by URI.

    Args:
        constitutions: List of constitution URIs
        modes: List of composition modes (default: all EXTEND)
        strict: If True, any conflict raises error

    Returns:
        MergedConstitution
    """
    modes = modes or ['extend'] * len(constitutions)

    layers = []
    for i, (uri, mode) in enumerate(zip(constitutions, modes)):
        const = load_constitution(uri)
        layers.append(ConstitutionLayer(
            constitution=const,
            layer=i,
            mode=CompositionMode(mode),
            source=uri,
        ))

    merger = ConstitutionMerger()
    return merger.merge(layers, strict=strict)


__version__ = '1.0.0'
```

---

## Appendices

### A. Composition Matrix

| Mode A | Mode B | Result | Conflict? |
|--------|--------|--------|-----------|
| BASE | BASE | Error | Yes (duplicate base) |
| BASE | EXTEND | A + B rules | Only if explicit conflict |
| BASE | OVERRIDE | A preserved, B additions | If B tries to override A |
| EXTEND | EXTEND | A + B rules | If rules contradict |
| EXTEND | OVERRIDE | A + B (B wins conflicts) | No |
| OVERRIDE | OVERRIDE | B wins conflicts | No |

### B. Error Codes

| Code | Description |
|------|-------------|
| `CONFLICT_BASE_OVERRIDE` | Attempted to override BASE constitution |
| `CONFLICT_EXPLICIT` | Explicit conflict declaration |
| `CONFLICT_VALUE_TENSION` | Value ontology tension |
| `CONFLICT_SCOPE_MISMATCH` | Incompatible scopes |
| `CONFLICT_STRICT_MODE` | Any conflict in STRICT mode |
| `CIRCULAR_DEPENDENCY` | Constitution references itself |

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-11 | Initial specification |

---

*This specification is released under CC BY 4.0. Contributions welcome.*
