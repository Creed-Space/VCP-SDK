# VCP Production Integration Plan

**Version**: 1.0.0
**Date**: 2026-01-11
**Status**: Ready for Implementation

---

## Executive Summary

**Question**: Is VCP ready for testing in Creed Space?

**Answer**: **Yes, with conditions.**

- **VCP/T (Transport)** is already production-ready (`services/vcp/`)
- **VCP/I, VCP/S, VCP/A** need implementation but architecture supports them
- Modular integration is straightforward using existing patterns

**Effort Estimate**:
| Layer | Status | Implementation | Testing |
|-------|--------|----------------|---------|
| VCP/I | Spec complete | 2-3 days | 1 day |
| VCP/T | **DONE** | — | — |
| VCP/S | Spec complete | 3-4 days | 2 days |
| VCP/A | Spec complete | 4-5 days | 2 days |
| Integration | — | 2-3 days | 2 days |
| **Total** | | **~2 weeks** | |

---

## Current State Analysis

### What Already Exists

```
services/vcp/                    # VCP/T - COMPLETE
├── __init__.py                  # Public API (69 lines)
├── types.py                     # Type definitions (154 lines)
├── bundle.py                    # Bundle + Manifest (451 lines)
├── orchestrator.py              # 11-step verification (281 lines)
├── injection.py                 # 3 injection formats (209 lines)
├── trust.py                     # Trust anchors
├── canonicalize.py              # Hash computation
├── audit.py                     # Audit logging
└── manifest.py                  # Re-exports
```

**Key insight**: VCP/T already has:
- Ed25519 signatures ✓
- Content hash verification ✓
- Temporal claims (iat/nbf/exp) ✓
- Replay detection (JTI) ✓
- Scope binding ✓
- `CompositionMode` enum (BASE/EXTEND/OVERRIDE/STRICT) ✓

### What Needs Implementation

| Layer | Module | Key Classes | Integration Point |
|-------|--------|-------------|-------------------|
| **VCP/I** | `services/vcp/identity/` | `Token`, `Registry`, `Namespace` | Bundle ID resolution |
| **VCP/S** | `services/vcp/semantics/` | `CSM1Parser`, `Composer`, `PersonaConfig` | Manifest metadata |
| **VCP/A** | `services/vcp/adaptation/` | `ContextEncoder`, `StateTracker`, `TransitionHandler` | PDP context |

---

## Modular Architecture

### Design Principles

1. **Feature-flagged**: Each layer independently toggleable
2. **Shadow mode**: Compute results without enforcing
3. **Plugin-based**: Integrate via existing plugin system
4. **Hot-swappable**: Update without restart
5. **Reversible**: Clean removal path

### Feature Flag Design

```python
# data/feature_flags.json additions
{
    "vcp_identity_enabled": false,      # VCP/I
    "vcp_identity_shadow": true,        # Shadow mode
    "vcp_semantics_enabled": false,     # VCP/S
    "vcp_semantics_shadow": true,
    "vcp_adaptation_enabled": false,    # VCP/A
    "vcp_adaptation_shadow": true,
    "vcp_full_stack_enabled": false,    # All layers
    "vcp_strict_mode": false            # Fail on any VCP error
}
```

### Module Structure

```
services/vcp/
├── __init__.py                  # Existing - extend exports
├── types.py                     # Existing - extend types
├── bundle.py                    # Existing
├── orchestrator.py              # Existing - extend
├── injection.py                 # Existing
├── trust.py                     # Existing
├── audit.py                     # Existing
│
├── identity/                    # NEW - VCP/I
│   ├── __init__.py
│   ├── token.py                 # Token parsing/validation
│   ├── registry.py              # Registry client
│   ├── namespace.py             # Namespace governance
│   ├── encoding.py              # Format polymorphism
│   └── ontology.py              # Value corpus (optional)
│
├── semantics/                   # NEW - VCP/S
│   ├── __init__.py
│   ├── csm1.py                  # CSM1 grammar parser
│   ├── persona.py               # Persona definitions
│   ├── scope.py                 # Scope handling
│   ├── composer.py              # Constitution composition
│   └── conflict.py              # Conflict resolution
│
└── adaptation/                  # NEW - VCP/A
    ├── __init__.py
    ├── context.py               # Enneagram encoder
    ├── state.py                 # State tracking
    ├── transition.py            # Transition handlers
    ├── messaging.py             # Inter-agent protocol
    └── interiora.py             # Interiora bridge
```

---

## Integration Points

### 1. VCP/I → VCP/T Integration

**Location**: `services/vcp/bundle.py` line ~135

```python
# Current
bundle_info = BundleInfo(
    id="family.safe.guide",  # Hardcoded string
    version="1.2.0",
    content_hash=hash,
)

# Enhanced with VCP/I
from services.vcp.identity import Token

token = Token.parse("family.safe.guide@1.2.0")
token.validate()  # Raises if invalid
bundle_info = BundleInfo(
    id=token.canonical,
    version=token.version,
    content_hash=hash,
)
```

### 2. VCP/S → VCP/T Integration

**Location**: `services/vcp/types.py` - extend `Composition`

```python
# Current
@dataclass
class Composition:
    layer: int = 2
    mode: CompositionMode = CompositionMode.EXTEND
    conflicts_with: list[str] = field(default_factory=list)
    requires: list[str] = field(default_factory=list)

# Enhanced with VCP/S
@dataclass
class Composition:
    layer: int = 2
    mode: CompositionMode = CompositionMode.EXTEND
    conflicts_with: list[str] = field(default_factory=list)
    requires: list[str] = field(default_factory=list)
    # NEW: VCP/S fields
    csm1_code: str | None = None           # e.g., "N5+F:ELEM"
    persona: str | None = None              # e.g., "nanny"
    scopes: list[str] = field(default_factory=list)  # e.g., ["family", "education"]
    adherence_level: int = 3                # 0-5
```

### 3. VCP/A → PDP Integration

**Location**: `services/safety_stack/pdp.py` - new plugin

```python
# New plugin: services/safety_stack/plugins/vcp_adaptation_plugin.py

from services.vcp.adaptation import ContextEncoder, StateTracker

class VCPAdaptationPlugin(SafetyPlugin):
    """VCP/A context adaptation for PDP decisions."""

    def __init__(self):
        self.encoder = ContextEncoder()
        self.tracker = StateTracker()

    async def evaluate(self, context: DecisionContext) -> PluginResult:
        if not is_feature_enabled("vcp_adaptation_enabled"):
            return PluginResult.skip()

        # Encode current context
        vcp_context = self.encoder.encode(
            time=context.timestamp,
            space=context.environment,
            company=context.audience,
            state=context.user_state,
        )

        # Check for transitions
        transition = self.tracker.detect_transition(
            previous=context.previous_context,
            current=vcp_context,
        )

        # Return signals (shadow mode: signals only, no enforcement)
        if is_feature_enabled("vcp_adaptation_shadow"):
            return PluginResult(
                signals={"vcp_context": vcp_context, "transition": transition},
                concerns=[],
            )

        # Active mode: apply context-aware modifications
        return PluginResult(
            signals={"vcp_context": vcp_context, "transition": transition},
            modifications=self._compute_modifications(vcp_context, transition),
        )
```

---

## Implementation Phases

### Phase 1: Foundation (Days 1-3)

**Goal**: VCP/I token parsing and validation

```python
# services/vcp/identity/token.py

import re
from dataclasses import dataclass

@dataclass(frozen=True)
class Token:
    """VCP/I Token with variable-depth support (3-10 segments)."""

    segments: tuple[str, ...]
    version: str | None = None
    namespace: str | None = None

    # ABNF: token = segment 2*9("." segment) ["@" version] [":" namespace]
    TOKEN_PATTERN = re.compile(
        r"^(?P<path>[a-z][a-z0-9-]*(?:\.[a-z][a-z0-9-]*){2,9})"
        r"(?:@(?P<version>\d+\.\d+\.\d+))?"
        r"(?::(?P<namespace>[A-Z][A-Z0-9]*))?$"
    )

    @classmethod
    def parse(cls, raw: str) -> "Token":
        """Parse and validate a VCP/I token."""
        match = cls.TOKEN_PATTERN.match(raw)
        if not match:
            raise ValueError(f"Invalid VCP/I token: {raw}")
        groups = match.groupdict()
        return cls(
            segments=tuple(groups["path"].split(".")),
            version=groups.get("version"),
            namespace=groups.get("namespace"),
        )

    @property
    def domain(self) -> str:
        """First segment."""
        return self.segments[0]

    @property
    def approach(self) -> str:
        """Second-to-last segment."""
        return self.segments[-2]

    @property
    def role(self) -> str:
        """Last segment."""
        return self.segments[-1]

    @property
    def depth(self) -> int:
        """Number of segments."""
        return len(self.segments)

    @property
    def canonical(self) -> str:
        """Canonical form without version/namespace."""
        return ".".join(self.segments)

    def to_uri(self, registry: str = "creed.space") -> str:
        """Convert to VCP/T URI."""
        version = f"@{self.version}" if self.version else ""
        return f"creed://{registry}/{self.canonical}{version}"
```

**Tests**:
```python
# tests/vcp/test_identity.py
def test_token_parsing():
    t = Token.parse("family.safe.guide@1.2.0")
    assert t.domain == "family"
    assert t.approach == "safe"
    assert t.role == "guide"
    assert t.version == "1.2.0"
    assert t.depth == 3

def test_four_segment_token():
    t = Token.parse("company.acme.legal.compliance")
    assert t.domain == "company"
    assert t.approach == "legal"
    assert t.role == "compliance"
    assert t.depth == 4

def test_invalid_token():
    with pytest.raises(ValueError):
        Token.parse("invalid")
```

### Phase 2: Semantics (Days 4-7)

**Goal**: CSM1 parser and composition engine

```python
# services/vcp/semantics/csm1.py

from dataclasses import dataclass
from enum import Enum

class Persona(Enum):
    NANNY = "N"
    SENTINEL = "Z"
    GODPARENT = "G"
    AMBASSADOR = "A"
    MUSE = "M"
    ANCHOR = "R"
    HOTROD = "H"
    CUSTOM = "C"

@dataclass
class CSM1Code:
    """Parsed CSM1 code."""

    persona: Persona
    adherence_level: int  # 0-5
    scopes: list[str]
    namespace: str | None = None
    version: str | None = None

    # Pattern: persona + level + [scopes] + [:namespace] + [@version]
    # Example: N5+F+E:ELEM@1.2.0

    @classmethod
    def parse(cls, raw: str) -> "CSM1Code":
        """Parse CSM1 code string."""
        # Implementation follows ABNF grammar from spec
        ...

    def applies_to_scope(self, context_scope: str) -> bool:
        """Check if this code applies to a given scope."""
        if not self.scopes:
            return True  # No scope restriction
        return context_scope in self.scopes
```

### Phase 3: Adaptation (Days 8-12)

**Goal**: Context encoding and state tracking

```python
# services/vcp/adaptation/context.py

from dataclasses import dataclass
from enum import Enum

class Dimension(Enum):
    TIME = ("⏰", 1)
    SPACE = ("📍", 2)
    COMPANY = ("👥", 3)
    CULTURE = ("🌍", 4)
    OCCASION = ("🎭", 5)
    STATE = ("🧠", 6)
    ENVIRONMENT = ("🌡️", 7)
    AGENCY = ("🔷", 8)
    CONSTRAINTS = ("🔶", 9)

@dataclass
class VCPContext:
    """Encoded VCP/A context."""

    dimensions: dict[Dimension, list[str]]

    def encode(self) -> str:
        """Encode to wire format."""
        parts = []
        for dim in Dimension:
            if dim in self.dimensions:
                values = self.dimensions[dim]
                parts.append(f"{dim.value[0]}{''.join(values)}")
        return "|".join(parts)

    @classmethod
    def decode(cls, encoded: str) -> "VCPContext":
        """Decode from wire format."""
        ...

# services/vcp/adaptation/state.py

class StateTracker:
    """Track context state and detect transitions."""

    def __init__(self):
        self._history: list[VCPContext] = []
        self._handlers: dict[str, TransitionHandler] = {}

    def detect_transition(
        self,
        previous: VCPContext | None,
        current: VCPContext
    ) -> Transition:
        """Detect transition type between states."""
        if previous is None:
            return Transition(type="initial", severity="none")

        delta = self._compute_delta(previous, current)

        if delta.emergency_dimensions:
            return Transition(type="emergency", severity="critical", delta=delta)
        elif delta.major_dimensions:
            return Transition(type="major", severity="high", delta=delta)
        elif delta.minor_dimensions:
            return Transition(type="minor", severity="low", delta=delta)
        else:
            return Transition(type="none", severity="none")
```

### Phase 4: Integration (Days 13-15)

**Goal**: Wire everything together with feature flags

```python
# services/vcp/__init__.py - extended exports

from .identity import Token, Registry, Namespace
from .semantics import CSM1Code, Persona, Composer
from .adaptation import VCPContext, StateTracker, Transition

__all__ = [
    # Existing exports...

    # VCP/I
    "Token",
    "Registry",
    "Namespace",

    # VCP/S
    "CSM1Code",
    "Persona",
    "Composer",

    # VCP/A
    "VCPContext",
    "StateTracker",
    "Transition",
]
```

---

## Shadow Mode Operation

### How Shadow Mode Works

```
┌─────────────────────────────────────────────────────────────────┐
│                     SHADOW MODE FLOW                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Request → [VCP/A Plugin] → [PDP Stages] → Response            │
│                  │                                              │
│                  ↓                                              │
│            ┌─────────────┐                                      │
│            │   SHADOW    │ ← Computes VCP signals               │
│            │   LOGGING   │ ← Records what WOULD happen          │
│            │             │ ← Does NOT modify response           │
│            └─────────────┘                                      │
│                  │                                              │
│                  ↓                                              │
│            logs/vcp_shadow.log                                  │
│            ├── context: ⏰🌅|📍🏡|👥👶                           │
│            ├── would_apply: N5+F                                │
│            ├── transition: minor                                │
│            └── timestamp: 2026-01-11T14:30:00Z                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Shadow Mode Benefits

1. **Risk-free testing**: See VCP decisions without affecting users
2. **A/B comparison**: Compare VCP decisions vs current behavior
3. **Performance profiling**: Measure VCP overhead before activation
4. **Gradual rollout**: Shadow → 1% users → 10% → 100%

---

## Removal Path

If VCP needs to be removed:

### Quick Disable (seconds)

```python
# Runtime killswitch
from services.feature_flags import killswitch
killswitch("vcp_full_stack_enabled")
killswitch("vcp_identity_enabled")
killswitch("vcp_semantics_enabled")
killswitch("vcp_adaptation_enabled")
```

### Environment Disable (no code change)

```bash
export FF_VCP_FULL_STACK_ENABLED=false
export FF_VCP_IDENTITY_ENABLED=false
export FF_VCP_SEMANTICS_ENABLED=false
export FF_VCP_ADAPTATION_ENABLED=false
```

### Clean Removal (if permanent)

```bash
# 1. Disable via flags (ensure no traffic)
# 2. Remove plugin registration
# 3. Delete module directories
rm -rf services/vcp/identity/
rm -rf services/vcp/semantics/
rm -rf services/vcp/adaptation/

# 4. Remove from __init__.py exports
# 5. Remove feature flags from data/feature_flags.json
```

---

## Testing Strategy

### Unit Tests

```
tests/vcp/
├── identity/
│   ├── test_token.py          # Token parsing
│   ├── test_namespace.py      # Namespace validation
│   └── test_registry.py       # Registry client
├── semantics/
│   ├── test_csm1.py           # CSM1 parsing
│   ├── test_persona.py        # Persona configs
│   └── test_composer.py       # Composition
└── adaptation/
    ├── test_context.py        # Context encoding
    ├── test_state.py          # State tracking
    └── test_transition.py     # Transitions
```

### Integration Tests

```python
# tests/integration/test_vcp_full_stack.py

async def test_vcp_full_flow():
    """Test complete VCP stack from token to injection."""

    # VCP/I: Parse token
    token = Token.parse("family.safe.guide@1.2.0")

    # VCP/T: Build and verify bundle
    bundle = BundleBuilder() \
        .set_id(token.canonical) \
        .set_version(token.version) \
        .set_content(constitution_text) \
        .sign(issuer_key) \
        .build()

    result = orchestrator.verify(bundle, context)
    assert result.is_valid

    # VCP/S: Parse semantics
    csm1 = CSM1Code.parse(bundle.manifest.composition.csm1_code)
    assert csm1.persona == Persona.NANNY

    # VCP/A: Apply context
    vcp_context = ContextEncoder().encode(space="home", company=["children"])
    assert csm1.applies_to_scope("family")
```

### Shadow Mode Tests

```python
async def test_shadow_mode_no_side_effects():
    """Verify shadow mode doesn't modify responses."""

    # Enable shadow mode
    set_flag("vcp_adaptation_enabled", True)
    set_flag("vcp_adaptation_shadow", True)

    # Process request
    response_with_vcp = await process_request(request)

    # Disable VCP
    set_flag("vcp_adaptation_enabled", False)

    # Process same request
    response_without_vcp = await process_request(request)

    # Responses should be identical
    assert response_with_vcp == response_without_vcp
```

---

## Rollout Plan

### Week 1: Development

| Day | Task |
|-----|------|
| 1 | VCP/I Token implementation |
| 2 | VCP/I Namespace validation |
| 3 | VCP/I Registry client (stub) |
| 4 | VCP/S CSM1 parser |
| 5 | VCP/S Composition engine |

### Week 2: Integration

| Day | Task |
|-----|------|
| 6 | VCP/A Context encoder |
| 7 | VCP/A State tracker |
| 8 | VCP/A PDP plugin |
| 9 | Integration tests |
| 10 | Shadow mode testing |

### Week 3: Rollout

| Stage | Scope | Duration |
|-------|-------|----------|
| Shadow | 100% traffic, 0% enforcement | 3 days |
| Canary | 1% users, full enforcement | 2 days |
| Gradual | 10% → 50% → 100% | 5 days |

---

## Metrics to Track

### Correctness

- VCP/I token parse success rate
- VCP/S CSM1 parse success rate
- VCP/A context encoding accuracy

### Performance

- VCP/I token parse latency (target: <1ms)
- VCP/S composition latency (target: <5ms)
- VCP/A context encode latency (target: <2ms)
- Total VCP overhead (target: <10ms, <1% of request time)

### Business

- Constitution resolution success rate
- Context transition frequency
- Shadow mode divergence rate

---

## Success Criteria

VCP is production-ready when:

1. **Functional**
   - [ ] VCP/I tokens validate against ABNF grammar
   - [ ] VCP/S CSM1 codes parse deterministically
   - [ ] VCP/A contexts encode/decode losslessly
   - [ ] Full stack integration tests pass

2. **Performance**
   - [ ] Total overhead <10ms p99
   - [ ] No memory leaks under load
   - [ ] Shadow mode has zero response impact

3. **Operational**
   - [ ] Feature flags work correctly
   - [ ] Killswitch disables in <1 second
   - [ ] Logs capture VCP decisions
   - [ ] Metrics dashboard exists

4. **Quality**
   - [ ] >90% test coverage
   - [ ] No high/critical security findings
   - [ ] Documentation complete

---

## Appendix: Existing Code Reuse

### From `services/minicode_service.py`

May already have CSM1-like encoding. Check for reuse:

```python
# Potential overlap with VCP/S
from services.minicode_service import encode_constitution, decode_constitution
```

### From `services/wefa_service.py`

WeFA already does context adaptation. VCP/A should complement:

```python
# VCP/A can feed into WeFA
wefa_weights = wefa_service.compute_weights(
    constitution=bundle,
    context=vcp_context,  # VCP/A provides this
)
```

### From `services/safety_stack/vcp_bridge.py`

Already handles cross-system VCP state:

```python
# Extend for VCP/A
from services.safety_stack.vcp_bridge import VCPBridge
bridge = VCPBridge()
bridge.share_context(vcp_context)  # Share with other agents
```

---

*Ready for implementation. Start with Phase 1 (VCP/I) in shadow mode.*
