# VCP Implementation Guide

**Version**: 2.4.0
**Date**: 2026-01-12
**Status**: ✅ Fully Implemented & Verified

---

## Overview

This document describes the **Value-Context Protocol (VCP)** implementation in the Creed Space codebase. VCP is a six-layer protocol stack for transporting constitutional values to AI systems.

> **Note**: This is distinct from the Visceral-Chromatic Protocol (also abbreviated VCP) used for interoceptive state tracking. See `docs/VCP_INTEGRATION_IMPLEMENTATION.md` for that system.

---

## Implementation Status

```
┌─────────────────────────────────────────────────────────────────────────┐
│        VALUE-CONTEXT PROTOCOL (VCP) - IMPLEMENTATION STATUS             │
├─────────────────────────────────────────────────────────────────────────┤
│  VCP-ADAPTATION  (Layer 4)  │  VCP/A  │  ✅ VERIFIED  │  PDP + API     │
│  VCP-SEMANTICS   (Layer 3)  │  VCP/S  │  ✅ VERIFIED  │  API + Export  │
│  VCP-TRANSPORT   (Layer 2)  │  VCP/T  │  ✅ VERIFIED  │  Production    │
│  VCP-IDENTITY    (Layer 1)  │  VCP/I  │  ✅ VERIFIED  │  API + Export  │
└─────────────────────────────────────────────────────────────────────────┘

Legend: ✅ VERIFIED = Runtime verified with integration tests (2026-01-12)
```

| Layer | Tests | Status | Integration |
|-------|-------|--------|-------------|
| VCP/I | 48 | ✅ Verified | API, export, MCP |
| VCP/T | 40+ | ✅ Verified | Production |
| VCP/S | 53 | ✅ Verified | API, export, MCP |
| VCP/A | 56 | ✅ Verified | PDP plugin, API, MCP |
| **Total** | **157+** | ✅ | All integration points |

---

## Directory Structure

```
services/vcp/
├── __init__.py              # All exports (v2.0.0)
│
├── identity/                # VCP/I (Layer 1)
│   ├── __init__.py
│   ├── token.py            # Token parsing, validation, ABNF grammar
│   └── namespace.py        # Namespace tiers, governance
│
├── semantics/               # VCP/S (Layer 3)
│   ├── __init__.py
│   ├── csm1.py             # CSM1 grammar, Persona, Scope enums
│   └── composer.py         # Constitution composition, conflict detection
│
├── adaptation/              # VCP/A (Layer 4)
│   ├── __init__.py
│   ├── context.py          # 9-dimension enneagram encoder
│   └── state.py            # State tracking, transition detection
│
├── audit.py                 # VCP/T: Audit logging
├── bundle.py                # VCP/T: Signed bundles
├── canonicalize.py          # VCP/T: Hash computation
├── injection.py             # VCP/T: LLM injection formats
├── orchestrator.py          # VCP/T: Verification engine
├── trust.py                 # VCP/T: Trust anchors
└── types.py                 # VCP/T: Core types

tests/vcp/
├── identity/
│   ├── test_token.py       # 32 tests
│   └── test_namespace.py   # 16 tests
├── semantics/
│   ├── test_csm1.py        # 36 tests
│   └── test_composer.py    # 17 tests
├── adaptation/
│   ├── test_context.py     # 32 tests
│   └── test_state.py       # 24 tests
└── test_*.py               # VCP/T tests (existing)
```

---

## Layer 1: VCP/I (Identity)

### Token Parsing

```python
from services.vcp import Token

# Parse a token
token = Token.parse("family.safe.guide@1.2.0")
print(token.domain)      # "family"
print(token.approach)    # "safe"
print(token.role)        # "guide"
print(token.version)     # "1.2.0"
print(token.canonical)   # "family.safe.guide"
print(token.to_uri())    # "creed://creed.space/family.safe.guide@1.2.0"

# Create variants
versioned = token.with_version("2.0.0")
namespaced = token.with_namespace("ELEM")

# Pattern matching
token.matches_pattern("family.*.guide")  # True
token.matches_pattern("*.safe.*")        # True
```

### Token Format (ABNF)

```
token     = domain "." approach "." role ["@" version] [":" namespace]
domain    = ALPHA *(ALPHA / DIGIT / "-")
approach  = ALPHA *(ALPHA / DIGIT / "-")
role      = ALPHA *(ALPHA / DIGIT / "-")
version   = 1*DIGIT "." 1*DIGIT "." 1*DIGIT
namespace = UPALPHA *(UPALPHA / DIGIT)

Examples:
  family.safe.guide
  family.safe.guide@1.2.0
  company.acme.legal:SEC
  family.safe.guide@1.2.0:ELEM
```

### Namespace Tiers

```python
from services.vcp import NamespaceTier, validate_namespace_access
from services.vcp.identity.namespace import infer_tier, CORE_DOMAINS

# Core domains (reserved)
CORE_DOMAINS  # {"family", "work", "education", "health", ...}

# Infer tier from token
tier = infer_tier(token)  # NamespaceTier.CORE

# Validate access
validate_namespace_access(token, NamespaceTier.CORE)  # True
```

| Tier | Prefix | Example | Registration |
|------|--------|---------|--------------|
| CORE | (reserved) | `family.*` | Pre-defined |
| ORGANIZATIONAL | `company-*` | `company-acme.legal.*` | DNS proof |
| PERSONAL | `user-*` | `user-alice.creative.*` | Email |
| COMMUNITY | (other) | `opensource.permissive.*` | Consensus |

---

## Layer 3: VCP/S (Semantics)

### CSM1 Parsing

```python
from services.vcp import CSM1Code, Persona, CSM1Scope

# Parse CSM1 code
code = CSM1Code.parse("N5+F+E")
print(code.persona)          # Persona.NANNY
print(code.adherence_level)  # 5
print(code.scopes)           # [Scope.FAMILY, Scope.EDUCATION]
print(code.encode())         # "N5+F+E"

# Check applicability
code.applies_to(CSM1Scope.FAMILY)    # True
code.applies_to(CSM1Scope.WORK)      # False

# Create variants
relaxed = code.with_level(3)
expanded = code.with_scopes([CSM1Scope.FAMILY, CSM1Scope.WORK])
```

### CSM1 Format

```
code = persona level *("+" scope) [":" namespace] ["@" version]

Personas: N(anny) Z(sentinel) G(odparent) A(mbassador) M(use) R(anchor) H(otrod) C(ustom)
Levels:   0-5 (0=disabled, 5=maximum)
Scopes:   F(amily) W(ork) E(ducation) H(ealthcare) I(ncome/Finance) L(egal)
          P(rivacy) S(afety) A(ccessibility) V(erde/Environment) G(eneral)

Examples:
  N5          → Nanny, level 5, all scopes
  N5+F+E      → Nanny, level 5, Family + Education only
  Z4+P:SEC    → Sentinel, level 4, Privacy, SEC namespace
  G3@1.0.0    → Godparent, level 3, version 1.0.0
```

### Personas

```python
from services.vcp import Persona

for p in Persona:
    print(f"{p.value}: {p.name} - {p.description}")

# N: NANNY - Child safety specialist
# Z: SENTINEL - Security and privacy guardian
# G: GODPARENT - Ethical guidance counselor
# A: AMBASSADOR - Professional conduct advisor
# M: MUSE - Creativity enabler
# R: ANCHOR - Factual accuracy enforcer
# H: HOTROD - Minimal constraints (expert mode)
# C: CUSTOM - User-defined persona
```

### Constitution Composition

```python
from services.vcp import Composer, CompositionMode, CompositionConflictError
from services.vcp.semantics.composer import Constitution

composer = Composer()

base = Constitution(id="base", rules=["Always be helpful.", "Never cause harm."])
overlay = Constitution(id="overlay", rules=["Be creative when asked."])

# Compose with different modes
result = composer.compose([base, overlay], CompositionMode.EXTEND)
print(result.merged_rules)  # All 3 rules

# Override mode: later wins conflicts
result = composer.compose([base, overlay], CompositionMode.OVERRIDE)

# Strict mode: any conflict raises
try:
    result = composer.compose([conflicting1, conflicting2], CompositionMode.STRICT)
except CompositionConflictError as e:
    print(f"Conflicts: {e.conflicts}")
```

| Mode | Behavior | Use Case |
|------|----------|----------|
| BASE | First cannot be overridden | Platform safety |
| EXTEND | Add rules, error on conflict | Domain specialization |
| OVERRIDE | Later wins conflicts | User customization |
| STRICT | Any conflict errors | High-stakes |

---

## Layer 4: VCP/A (Adaptation)

### Context Encoding

```python
from services.vcp import ContextEncoder, VCPContext, Dimension

encoder = ContextEncoder()

# Encode from keyword arguments
context = encoder.encode(
    time="morning",
    space="home",
    company=["children", "family"],
    occasion="normal",
    state="happy",
)

# Wire format (emoji-based)
print(context.encode())  # "⏰🌅|📍🏡|👥👶👨‍👩‍👧|🎭➖|🧠😊"

# JSON format
print(context.to_json())
# {"time": ["🌅"], "space": ["🏡"], "company": ["👶", "👨‍👩‍👧"], ...}

# Decode from wire format
decoded = VCPContext.decode("⏰🌅|📍🏡|👥👶")
```

### The Nine Dimensions

| # | Symbol | Dimension | Values |
|---|--------|-----------|--------|
| 1 | ⏰ | TIME | 🌅morning, ☀️midday, 🌆evening, 🌙night |
| 2 | 📍 | SPACE | 🏡home, 🏢office, 🏫school, 🏥hospital |
| 3 | 👥 | COMPANY | 👤alone, 👶children, 👔colleagues, 👨‍👩‍👧family |
| 4 | 🌍 | CULTURE | 🌍global, 🇺🇸american, 🇪🇺european, 🇯🇵japanese |
| 5 | 🎭 | OCCASION | ➖normal, 🎂celebration, 😢mourning, 🚨emergency |
| 6 | 🧠 | STATE | 😊happy, 😰anxious, 😴tired, 🤔contemplative |
| 7 | 🌡️ | ENVIRONMENT | ☀️comfortable, 🥵hot, 🥶cold, 🔇quiet |
| 8 | 🔷 | AGENCY | 👑leader, 🤝peer, 📋subordinate, 🔐limited |
| 9 | 🔶 | CONSTRAINTS | ○minimal, ⚖️legal, 💸economic, ⏱️time |

### State Tracking

```python
from services.vcp import StateTracker, TransitionSeverity

tracker = StateTracker(max_history=100)

# Record context changes
context1 = encoder.encode(time="morning", space="home")
tracker.record(context1)  # Returns None (first record)

context2 = encoder.encode(time="morning", space="office")
transition = tracker.record(context2)
print(transition.severity)           # TransitionSeverity.MINOR
print(transition.changed_dimensions) # [Dimension.SPACE]

# Major transition (3+ dimensions or key dimension)
context3 = encoder.encode(time="evening", space="hospital", occasion="emergency")
transition = tracker.record(context3)
print(transition.severity)           # TransitionSeverity.EMERGENCY

# Register handlers
def on_emergency(t):
    print(f"Emergency detected: {t.changed_dimensions}")

tracker.register_handler(TransitionSeverity.EMERGENCY, on_emergency)

# Query history
tracker.current        # Latest context
tracker.history_count  # Number of records
tracker.get_recent(5)  # Last 5 entries
tracker.find_transitions(TransitionSeverity.MAJOR)  # All major transitions
```

| Severity | Trigger |
|----------|---------|
| NONE | No change |
| MINOR | Single dimension change |
| MAJOR | 3+ dimensions OR key dimension (OCCASION, AGENCY, CONSTRAINTS) |
| EMERGENCY | 🚨 emoji present in context |

---

## Feature Flags

All VCP functionality is controlled by feature flags.

### Current Status (2026-01-11)

| Flag | Default | Description |
|------|---------|-------------|
| `vcp_identity_enabled` | **true** | VCP/I Layer active |
| `vcp_semantics_enabled` | **true** | VCP/S Layer active |
| `vcp_adaptation_enabled` | **true** | VCP/A Layer active |
| `vcp_full_stack_enabled` | **true** | All layers active |
| `vcp_strict_mode` | false | Strict validation |
| `vcp_*_shadow` | false | Shadow modes off |

### Usage

```python
from services.feature_flags import is_feature_enabled, killswitch

# Check flags
is_feature_enabled("vcp_identity_enabled")    # VCP/I
is_feature_enabled("vcp_semantics_enabled")   # VCP/S
is_feature_enabled("vcp_adaptation_enabled")  # VCP/A
is_feature_enabled("vcp_full_stack_enabled")  # All layers
is_feature_enabled("vcp_strict_mode")         # Strict validation

# Emergency disable
killswitch("vcp_full_stack_enabled")
```

### Environment Overrides

```bash
# Disable in specific environment
export FF_VCP_FULL_STACK_ENABLED=false

# Enable strict mode
export FF_VCP_STRICT_MODE=true
```

---

## Public API

All exports from `services.vcp`:

```python
from services.vcp import (
    # VCP/I (Identity)
    Token,
    NamespaceTier,
    NamespaceConfig,
    validate_namespace_access,

    # VCP/T (Transport) - existing
    Bundle,
    BundleBuilder,
    Manifest,
    Orchestrator,
    VerificationResult,
    CompositionMode,
    # ... etc

    # VCP/S (Semantics)
    CSM1Code,
    Persona,
    CSM1Scope,  # Aliased to avoid conflict with VCP/T Scope
    Composer,
    CompositionResult,
    Conflict,
    CompositionConflictError,

    # VCP/A (Adaptation)
    VCPContext,
    ContextEncoder,
    Dimension,
    StateTracker,
    Transition,
    TransitionSeverity,
)
```

---

## Testing

```bash
# Run all VCP tests
pytest tests/vcp/ -v

# Run specific layer
pytest tests/vcp/identity/ -v
pytest tests/vcp/semantics/ -v
pytest tests/vcp/adaptation/ -v

# With coverage
pytest tests/vcp/ --cov=services/vcp --cov-report=html
```

---

## Completed Integration (2026-01-12)

All integration points verified per `_contprompts/vcp_runtime_verification_2026-01-12.md`:

| Integration | Status | Evidence |
|-------------|--------|----------|
| **PDP Plugin** | ✅ | VCPAdaptationPlugin wired into `_load_plugins()`, runs in pipeline |
| **Export** | ✅ | `ExportFormatter._build_vcp_metadata()` produces token/csm1/persona |
| **API Endpoints** | ✅ | 6 VCP routes in FastAPI, HTTP 200 verified |
| **MCP Tools** | ✅ | `vcp_server.py` responds via `mcp-cli call vcp/vcp_status` |
| **GPT Actions** | ✅ | OpenAPI spec includes VCP paths |

---

## Related Documentation

| Document | Description |
|----------|-------------|
| [VCP_OVERVIEW.md](VCP_OVERVIEW.md) | Protocol specification |
| [VCP_CONTEXT_DATA_FLOW.md](VCP_CONTEXT_DATA_FLOW.md) | Context lifecycle and data flow |
| [VCP_IDENTITY_NAMING.md](identity/VCP_IDENTITY_NAMING.md) | Token format spec |
| [VCP_SEMANTICS_CSM1.md](semantics/VCP_SEMANTICS_CSM1.md) | CSM1 grammar spec |
| [VCP_ADAPTATION.md](adaptation/VCP_ADAPTATION.md) | Context protocol spec |
| [VCP_INTEGRATION_PLAN.md](VCP_INTEGRATION_PLAN.md) | Integration roadmap |

## Verification

**✅ Runtime verification COMPLETE (2026-01-12).**

| Item | Status |
|------|--------|
| HTTP endpoints with auth | ✅ Verified |
| Plugin in PDP pipeline | ✅ Verified |
| StateTracker per-session | ✅ Verified |
| Export artifact VCP block | ✅ Verified |
| Multi-worker behavior | ✅ Characterized |

See `docs/VCP_OVERVIEW.md` for detailed verification results.

### Verification Runbook (2026-01-12)

**Core tests:**
```bash
pytest tests/unit/plugins/test_vcp_adaptation_plugin.py -v
pytest tests/integration/test_vcp_integration.py -v
```

**Export verification:**
Generate an export using `ExportFormatter.format_claude_code_response(...)` and confirm output contains `vcp` metadata block with `token`, `uri`, `csm1`, `persona`, and `version` keys.

**Multi-worker:**
In multi-worker mode, isolation holds per worker; continuity across workers requires sticky sessions or shared persistence.

**Artifacts:**
- `_contprompts/vcp_runtime_verification_2026-01-12.md`
- `_contprompts/vcp_remaining_verification_2026-01-12.md`

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 2.4.0 | 2026-01-12 | Updated status table to VERIFIED; converted Next Steps to Completed Integration |
| 2.3.0 | 2026-01-12 | Added runbook, tightened multi-worker claim to "Characterized" |
| 2.2.0 | 2026-01-12 | **Runtime verification complete**; all integration points verified |
| 2.1.0 | 2026-01-12 | **VCP enabled by default**; all feature flags ON |
| 2.0.0 | 2026-01-11 | VCP/I, VCP/S, VCP/A core implementation (157 tests) |
| 1.0.0 | 2026-01-11 | VCP/T production implementation |

---

*The Value-Context Protocol: One protocol, six layers, complete constitutional AI.*
