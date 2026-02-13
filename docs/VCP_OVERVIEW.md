# Value-Context Protocol (VCP) Specification

**Version**: 2.2.2
**Date**: 2026-01-11
**Status**: ✅ Complete (v1.0)

---

## Implementation Status

| Layer | Name | Status | Notes |
|-------|------|--------|-------|
| **4** | VCP-Adaptation | ✅ Complete | Enneagram Protocol, state tracking, messaging |
| **3** | VCP-Semantics | ✅ Complete | CSM1 grammar, personas, composition |
| **2** | VCP-Transport | ✅ Complete | Signed bundles, verification, audit |
| **1** | VCP-Identity | ✅ Complete | Naming, namespaces, registry, encoding |

**SDK Implementations:**
| Language | Directory | Status | Scope |
|----------|-----------|--------|-------|
| Python | `python/` | ✅ Complete | Full stack: identity, semantics, adaptation, MCP server, API |
| Rust | `rust/` | 🚧 In Progress | Data plane: parsing, encoding, verification, WASM, CLI |

**Optional Components:**
| Component | Status | Notes |
|-----------|--------|-------|
| Value Ontology Data | ⚪ Optional | Spec complete; data curation is separate research project |

---

## Runtime Verification (2026-01-12, Updated)

**Status**: ✅ **VERIFIED** - All phases passed with evidence + critical fixes applied

VCP implementation verified as fully operational with runtime proof.

| Phase | Component | Result | Evidence |
|-------|-----------|--------|----------|
| 1.1 | App Routes | ✅ | 6 VCP routes registered in FastAPI app |
| 1.2 | Server Boot | ✅ | Health endpoint responds, OpenAPI shows VCP paths |
| 2.1 | Token Validation | ✅ | `family.safe.guide@1.2.0` → correct URI/domain/approach/role |
| 2.2 | CSM1 Parse | ✅ | `N5+F+E` → NANNY persona, adherence=5, scopes=[FAMILY,EDUCATION] |
| 2.3 | Context Encode | ✅ | morning/home/children → `⏰🌅\|📍🏡\|👥👶` |
| 2.4 | VCP Status | ✅ | HTTP 200, all 4 layers enabled, version 2.0.0 |
| 3.1 | Plugin Instantiation | ✅ | VCPAdaptationPlugin v2.0.0, priority=HIGH, tracker+encoder init |
| 3.2 | Plugin Execution | ✅ | Adds `vcp_signals` with wire format to context.metadata |
| 3.3 | Plugin Registration | ✅ | Exported from plugins package, loadable by PDP |
| 4.1 | Export Methods | ✅ | All VCP methods exist on ExportFormatter |
| 4.2 | Export Metadata | ✅ | Produces token, csm1, persona fields |
| 4.3 | Export Wiring | ✅ | 37 VCP references, `_build_vcp_metadata` in export flow |
| 5.1 | MCP Script | ✅ | `run_vcp_server.sh` exists with execute permission |
| 5.2 | MCP Module | ✅ | `services.mcp.vcp_server` imports successfully |
| 5.3 | MCP Config | ✅ | `.mcp.json` has valid vcp server configuration |
| 5.4 | MCP Responds | ✅ | `mcp-cli call vcp/vcp_status` returns correct flags |
| 6.1 | Feature Flags | ✅ | All 4 layers ON, shadow modes OFF, strict mode OFF |
| 6.2 | Flag Toggle | ✅ | `FF_VCP_ADAPTATION_ENABLED=false` correctly disables |
| 7.1 | Unit Tests | ✅ | 43 passed (router models + plugin tests) |
| 7.1 | Integration Tests | ✅ | 23 passed (core, API, PDP, export, MCP, flags) |
| 7.2 | Tests Meaningful | ✅ | Real instantiation, real execution, not just mocks |

**Verification Method**: TestClient with auth override for HTTP, UnifiedPDP instantiation for pipeline proof.

### Critical Fixes Applied (2026-01-12)

**Round 1 - Core Wiring:**
1. **VCPAdaptationPlugin wired into PDP** - Was exported but not loaded in `_load_plugins()`; now loads with feature flag check
2. **StateTracker per-session** - Changed from global to session-keyed dict with TTL + eviction
3. **HTTP endpoint proof** - Added TestClient tests with auth dependency override showing HTTP 200 + valid JSON

**Round 2 - Sharp Edges (GPT 5.2 XHIGH Review):**
4. **Fail-closed session handling** - No more `session_id or "default"`; missing session → ephemeral tracker (no cross-user risk)
5. **Thread safety** - Added `threading.Lock` protecting `_trackers` dict
6. **Cleanup trigger fix** - Changed from broken `len % 100` to `_access_count % 100`
7. **MAX_TRACKERS reduced** - Lowered from 10,000 to 1,000 (still ~100KB memory ceiling)
8. **Tracker property safety** - Now returns fresh ephemeral tracker, not shared "default"

**Round 3 - Production Hardening:**
9. **Redis persistence** - Redis-backed StateTracker for cross-worker state (v2.1.0, default ON)
10. **CI verification** - VCP runtime verification added to CI pipeline (5 automated checks)

---

## Abstract

The **Value-Context Protocol (VCP)** is a unified four-layer protocol stack for transporting, encoding, and applying constitutional values to AI systems. Like the OSI model for networking, VCP defines a complete architecture where each layer handles a specific concern, with well-defined interfaces between them.

VCP is **one protocol** with four layers—not four separate protocols.

---

## Protocol Stack

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                                                                 │
│            VALUE-CONTEXT PROTOCOL (VCP) - THE CONSTITUTIONAL STACK              │
│                                                                                 │
│   "OSI for AI Values: Identity, Transport, Semantics, Adaptation"               │
│                                                                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │  VCP-ADAPTATION  (Layer 4)                                      VCP/A   │   │
│   │  ─────────────────────────────────────────────────────────────────────  │   │
│   │  Purpose: WHEN and HOW constitutions apply                              │   │
│   │  Handles: Context encoding, state tracking, inter-agent messaging       │   │
│   │  Analogy: Application Layer (HTTP, SMTP) - user-facing interaction      │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                       ↕                                         │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │  VCP-SEMANTICS   (Layer 3)                                      VCP/S   │   │
│   │  ─────────────────────────────────────────────────────────────────────  │   │
│   │  Purpose: WHAT constitutional rules mean                                │   │
│   │  Handles: CSM1 grammar, personas, scopes, composition, conflict res     │   │
│   │  Analogy: Presentation Layer (TLS, MIME) - formatting and meaning       │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                       ↕                                         │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │  VCP-TRANSPORT   (Layer 2)                                      VCP/T   │   │
│   │  ─────────────────────────────────────────────────────────────────────  │   │
│   │  Purpose: HOW constitutions are delivered securely                      │   │
│   │  Handles: Signed bundles, verification, audit logging, trust anchors    │   │
│   │  Analogy: Transport Layer (TCP, UDP) - reliable delivery                │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                       ↕                                         │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │  VCP-IDENTITY    (Layer 1)                                      VCP/I   │   │
│   │  ─────────────────────────────────────────────────────────────────────  │   │
│   │  Purpose: WHO/WHAT the constitution is                                  │   │
│   │  Handles: Token naming, namespaces, registry, value ontology, encoding  │   │
│   │  Analogy: Network Layer (IP) - addressing and identification            │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## The Four Layers

| Layer | Name | Short | Purpose | Key Question |
|-------|------|-------|---------|--------------|
| **4** | VCP-Adaptation | VCP/A | Context-aware application | *When and how does it apply?* |
| **3** | VCP-Semantics | VCP/S | Rule meaning and composition | *What does it mean?* |
| **2** | VCP-Transport | VCP/T | Secure verified delivery | *How is it delivered safely?* |
| **1** | VCP-Identity | VCP/I | Naming and identification | *What is it called?* |

---

## Layer 1: VCP-Identity (VCP/I)

**Purpose**: Provide unique, portable, and human-meaningful identifiers for constitutional values.

**The Identity Layer answers**: *"What is this constitution called, and where can I find it?"*

### Core Concepts

| Concept | Description | Example | Status |
|---------|-------------|---------|--------|
| **Token Format** | Dot-separated naming | `family.safe.guide` | ✅ |
| **Namespaces** | Hierarchical governance | `company.acme.legal` | ✅ |
| **Registry** | Discovery and resolution | `registry.creed.space` | ✅ |
| **Value Ontology** | Semantic foundation | 7 categories | ⚪ Optional |
| **Encoding** | Multiple representations | canonical, CSM1, emoji, QR | ✅ |

> **Note**: The Value Ontology specification is complete, but the data file is optional. VCP functions fully without a populated ontology. See [VCP_IDENTITY_ONTOLOGY.md](identity/VCP_IDENTITY_ONTOLOGY.md) for details.

### Token Format

```
segment.segment.segment[.segment...][@version][:namespace]

Minimum 3 segments, maximum 10 segments.
Semantic mapping (backward compatible):
  - First segment = domain
  - Second-to-last = approach
  - Last segment = role
  - Middle segments = path (organizational hierarchy)

Examples:
  family.safe.guide                    # 3 segments
  family.safe.guide@1.2.0              # with version
  company.acme.legal.compliance        # 4 segments
  company.acme.legal.compliance:SEC    # with namespace
  org.example.dept.team.policy@1.0.0   # 5 segments
```

### Namespace Tiers

| Tier | Governance | Example | Registration |
|------|------------|---------|--------------|
| **Core** | Creed Space | `family.*`, `work.*` | Reserved |
| **Organizational** | Verified org | `company.acme.*` | Domain proof |
| **Community** | Multi-stakeholder | `religion.buddhist.*` | Consensus |
| **Personal** | Individual | `user.alice.*` | Self-service |

### Specifications

| Document | Description |
|----------|-------------|
| [VCP_IDENTITY_NAMING.md](identity/VCP_IDENTITY_NAMING.md) | Token format, validation, canonicalization |
| [VCP_IDENTITY_NAMESPACE.md](identity/VCP_IDENTITY_NAMESPACE.md) | Governance tiers, delegation |
| [VCP_IDENTITY_REGISTRY.md](identity/VCP_IDENTITY_REGISTRY.md) | Resolution protocol, API |
| [VCP_IDENTITY_ONTOLOGY.md](identity/VCP_IDENTITY_ONTOLOGY.md) | Value corpus, relationships |
| [VCP_IDENTITY_ENCODING.md](identity/VCP_IDENTITY_ENCODING.md) | Format polymorphism |

---

## Layer 2: VCP-Transport (VCP/T)

**Purpose**: Secure, verifiable delivery of constitutional content from repository to AI system.

**The Transport Layer answers**: *"How do I get this constitution safely, and how do I know it's authentic?"*

### Core Concepts

| Concept | Description |
|---------|-------------|
| **Signed Bundles** | Cryptographically signed packages with manifest + content |
| **Content Addressing** | Hash-based identity (`sha256:7f83b165...`) |
| **Verify-then-Inject** | Orchestrator verifies before LLM sees content |
| **Audit Logging** | Independent record of what was applied |
| **Trust Anchors** | PKI for issuer verification |

### Bundle Structure

```
vcp-bundle/
├── manifest.json    # Signed metadata (issuer, hash, signature)
└── content.txt      # Constitutional text
```

### Verification Flow

```
Repository → Orchestrator → LLM
             ↓
         1. Fetch bundle
         2. Verify signature
         3. Check content hash
         4. Check revocation
         5. Log to audit trail
         6. Inject verified text
```

### Specification

| Document | Description |
|----------|-------------|
| [VCP_TRANSPORT.md](../_papers/VCP_SPECIFICATION_v1.0.md) | Full transport protocol |

---

## Layer 3: VCP-Semantics (VCP/S)

**Purpose**: Define the meaning of constitutional rules and how they compose.

**The Semantics Layer answers**: *"What do these rules mean, and how do they combine?"*

### Core Concepts

| Concept | Description |
|---------|-------------|
| **CSM1 Grammar** | Constitutional Safety Minicode - compact encoding |
| **Personas** | 8 archetypal profiles (Nanny, Sentinel, etc.) |
| **Scopes** | Context qualifiers (Family, Work, Privacy, etc.) |
| **Adherence Levels** | 0-5 enforcement strictness |
| **Composition** | How multiple constitutions merge |

### CSM1 Format

```
persona + adherence + [scopes] + [:namespace] + [@version]

Examples:
  N5          → Nanny, level 5
  N5+F+E      → Nanny, level 5, Family + Education scopes
  Z4+P+W:SEC  → Sentinel, level 4, Privacy + Work, SEC namespace
```

### Personas

| Code | Name | Focus |
|------|------|-------|
| **N** | Nanny | Child safety, family-appropriate |
| **Z** | Sentinel | Security, privacy, operational safety |
| **G** | Godparent | Ethical guidance, moral reasoning |
| **A** | Ambassador | Professional conduct, diplomacy |
| **M** | Muse | Creativity, artistic expression |
| **R** | Anchor | Factual accuracy, reality grounding |
| **H** | Hot-Rod | Minimal constraints, performance |
| **C** | Custom | User-defined constitution |

### Composition Modes

| Mode | Behavior | Use Case |
|------|----------|----------|
| **BASE** | Cannot be overridden | Platform safety |
| **EXTEND** | Adds rules, conflicts error | Domain specialization |
| **OVERRIDE** | Later wins conflicts | User customization |
| **STRICT** | Any conflict errors | High-stakes |

### Specifications

| Document | Description |
|----------|-------------|
| [VCP_SEMANTICS_CSM1.md](semantics/VCP_SEMANTICS_CSM1.md) | CSM1 grammar specification |
| [VCP_SEMANTICS_COMPOSITION.md](semantics/VCP_SEMANTICS_COMPOSITION.md) | Merge and conflict resolution |

---

## Layer 4: VCP-Adaptation (VCP/A)

**Purpose**: Enable context-aware application of constitutions based on situational factors.

**The Adaptation Layer answers**: *"Given the current context, how should this constitution be applied?"*

### Core Concepts

| Concept | Description |
|---------|-------------|
| **Enneagram Protocol** | 9-dimension context encoding |
| **Emoji Encoding** | Visual, compact representation |
| **State Tracking** | Monitor transitions over time |
| **Transition Handlers** | Respond to context changes |
| **Inter-Agent Messaging** | Agent-to-agent context sharing |

### The Nine Dimensions

| # | Symbol | Dimension | Example Values |
|---|--------|-----------|----------------|
| 1 | ⏰ | TIME | 🌅morning, 🌙night, 📅weekday |
| 2 | 📍 | SPACE | 🏡home, 🏢office, 🏫school |
| 3 | 👥 | COMPANY | 👤alone, 👶children, 👔colleagues |
| 4 | 🌍 | CULTURE | 🇺🇸american, 🇯🇵japanese, 🌍global |
| 5 | 🎭 | OCCASION | ➖normal, 🎂celebration, 🚨emergency |
| 6 | 🧠 | STATE | 😊happy, 😰anxious, 😴tired |
| 7 | 🌡️ | ENVIRONMENT | ☀️comfortable, 🥵hot, 🔇quiet |
| 8 | 🔷 | AGENCY | 👑leader, 🤝peer, 🔐limited |
| 9 | 🔶 | CONSTRAINTS | ○minimal, ⚖️legal, 💸economic |

### Context Encoding

```
⏰🌅|📍🏡|👥👶👨‍👩‍👧|🎭➖|🧠😊

Meaning: Morning, home, children+family present, normal occasion, happy state
→ Apply: N5+F (Nanny, maximum child safety)
```

### Specification

| Document | Description |
|----------|-------------|
| [VCP_ADAPTATION.md](adaptation/VCP_ADAPTATION.md) | Context protocol, state, messaging |

---

## Protocol Data Unit (PDU)

Each layer wraps the previous layer's data:

```
┌─────────────────────────────────────────────────────────────────┐
│ VCP/A: Context Header                                           │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ VCP/S: Semantics (CSM1, composition metadata)               │ │
│ │ ┌─────────────────────────────────────────────────────────┐ │ │
│ │ │ VCP/T: Transport (signature, verification, manifest)    │ │ │
│ │ │ ┌─────────────────────────────────────────────────────┐ │ │ │
│ │ │ │ VCP/I: Identity (token, version, namespace)         │ │ │ │
│ │ │ │                                                     │ │ │ │
│ │ │ │           CONSTITUTIONAL CONTENT                    │ │ │ │
│ │ │ │                                                     │ │ │ │
│ │ │ └─────────────────────────────────────────────────────┘ │ │ │
│ │ └─────────────────────────────────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Complete VCP Header

```
[VCP:2.0]
[VCP/I:family.safe.guide@1.2.0]
[VCP/T:VERIFIED sha256:7f83b165...9069 issuer:creed.space]
[VCP/S:N5+F:ELEM composed:2 mode:override]
[VCP/A:⏰🌅|📍🏡|👥👶 transition:minor]
---BEGIN-CONSTITUTION---
# Family Safety Constitution
...
---END-CONSTITUTION---
```

---

## Layer Interactions

### Upward Flow (Authoring)

```
VCP/I: Define token → family.safe.guide
    ↓
VCP/T: Bundle and sign → manifest + content + signature
    ↓
VCP/S: Define semantics → N5+F:ELEM, personas, scopes
    ↓
VCP/A: Ready for context application
```

### Downward Flow (Application)

```
VCP/A: Context detected → children present, home
    ↓
VCP/S: Select appropriate → N5+F (Nanny, Family)
    ↓
VCP/T: Fetch and verify → bundle from registry
    ↓
VCP/I: Resolve token → family.safe.guide@1.2.0
```

### Cross-Layer References

```python
# VCP/I token becomes VCP/T bundle URI
token = "family.safe.guide"
uri = f"creed://creed.space/{token}@1.2.0"  # VCP/T

# VCP/S code embeds in VCP/T manifest
manifest["metadata"]["csm1"] = "N5+F:ELEM"  # VCP/S in VCP/T

# VCP/A context selects VCP/S configuration
if context.has_children():
    select_persona("N")  # VCP/A → VCP/S
```

---

## Conformance Levels

| Level | Layers | Requirements |
|-------|--------|--------------|
| **VCP-Minimal** | 1-2 | VCP/I naming + VCP/T verification |
| **VCP-Standard** | 1-3 | Minimal + VCP/S semantics |
| **VCP-Full** | 1-4 | Standard + VCP/A adaptation |
| **VCP-Enterprise** | 1-4+ | Full + audit, multi-sig, transparency logs |

---

## Comparison to OSI Model

| OSI Layer | VCP Layer | Function |
|-----------|-----------|----------|
| 7 Application | **VCP/A** | Context-aware interaction |
| 6 Presentation | **VCP/S** | Semantic formatting |
| 5 Session | (not needed) | — |
| 4 Transport | **VCP/T** | Reliable verified delivery |
| 3 Network | **VCP/I** | Addressing and routing |
| 2 Data Link | (not needed) | — |
| 1 Physical | (not needed) | — |

VCP is a 4-layer stack because AI constitutional delivery doesn't require session management or physical/data link concerns.

---

## Directory Structure

```
docs/
├── VCP_OVERVIEW.md                    # This document (master spec)
│
├── identity/                          # VCP/I specifications
│   ├── VCP_IDENTITY_NAMING.md         # Token format, ABNF grammar
│   ├── VCP_IDENTITY_NAMESPACE.md      # Governance tiers, delegation
│   ├── VCP_IDENTITY_REGISTRY.md       # Resolution API (OpenAPI)
│   ├── VCP_IDENTITY_ONTOLOGY.md       # Value corpus (SPEC ONLY, data optional)
│   └── VCP_IDENTITY_ENCODING.md       # 8 encoding formats
│
├── semantics/                         # VCP/S specifications
│   ├── VCP_SEMANTICS_CSM1.md          # Formal grammar, personas
│   └── VCP_SEMANTICS_COMPOSITION.md   # Merge semantics, conflicts
│
└── adaptation/                        # VCP/A specifications
    └── VCP_ADAPTATION.md              # Enneagram, state, messaging

data/
└── schemas/
    ├── vcp-manifest-v1.schema.json        # VCP/T manifest validation
    ├── vcp-identity-token.schema.json     # VCP/I token validation
    ├── vcp-semantics-csm1.schema.json     # VCP/S CSM1 validation
    └── vcp-adaptation-context.schema.json # VCP/A context validation

# OPTIONAL (not required for VCP v1.0):
# data/vcp_value_ontology.json           # Curated value corpus
```

**Note**: VCP/T transport specification is at `_papers/VCP_SPECIFICATION_v1.0_COMPLETE.md`

---

## Implementation

### Python Package Structure

```python
# vcp/__init__.py
from vcp.identity import Token, Registry, Ontology
from vcp.transport import Bundle, Verifier, AuditLog
from vcp.semantics import CSM1, Persona, Composer
from vcp.adaptation import Context, StateTracker, Message

# Usage
token = Token.parse("family.safe.guide@1.2.0")      # VCP/I
bundle = Bundle.fetch(token.to_uri())               # VCP/T
csm1 = CSM1.parse(bundle.manifest["csm1"])          # VCP/S
ctx = Context.encode(space="home", company="children")  # VCP/A
```

### CLI

```bash
# VCP/I - Identity operations
vcp identity resolve family.safe.guide
vcp identity register --token company.acme.legal --proof dns

# VCP/T - Transport operations
vcp transport fetch creed://creed.space/family.safe.guide@1.2.0
vcp transport verify bundle.json --trust-anchor trust.json

# VCP/S - Semantics operations
vcp semantics parse "N5+F:ELEM@1.2.0"
vcp semantics compose base.json overlay.json --mode override

# VCP/A - Adaptation operations
vcp adaptation encode --space home --company children
vcp adaptation detect-transition old.json new.json
```

---

## Quick Reference

### Layer Mnemonics

**I-T-S-A**: *"It's a protocol!"*
- **I**dentity - What is it?
- **T**ransport - How does it travel?
- **S**emantics - What does it mean?
- **A**daptation - How does it apply?

### Short Forms

| Full Name | Short | Ultra-Short |
|-----------|-------|-------------|
| VCP-Identity | VCP/I | I |
| VCP-Transport | VCP/T | T |
| VCP-Semantics | VCP/S | S |
| VCP-Adaptation | VCP/A | A |

### Example: Full Stack Reference

```
VCP/I:family.safe.guide@1.2.0
VCP/T:sha256:7f83b165
VCP/S:N5+F:ELEM
VCP/A:⏰🌅|📍🏡|👥👶
```

---

## Implementation Status

As of 2026-01-11, all four VCP layers have working implementations:

| Layer | Location | Tests | Status |
|-------|----------|-------|--------|
| **VCP/I** | `services/vcp/identity/` | 48 | ✅ Core complete |
| **VCP/T** | `services/vcp/` (root) | 40+ | ✅ Production |
| **VCP/S** | `services/vcp/semantics/` | 53 | ✅ Core complete |
| **VCP/A** | `services/vcp/adaptation/` | 56 | ✅ Core complete |

**Total: 157+ tests passing.**

### Feature Flags

All VCP layers are **enabled by default** as of 2026-01-11:

| Flag | Status | Description |
|------|--------|-------------|
| `vcp_identity_enabled` | ✅ ON | VCP/I layer |
| `vcp_semantics_enabled` | ✅ ON | VCP/S layer |
| `vcp_adaptation_enabled` | ✅ ON | VCP/A layer |
| `vcp_full_stack_enabled` | ✅ ON | All layers |
| `vcp_strict_mode` | ⚪ OFF | Strict validation |

Emergency disable: `killswitch("vcp_full_stack_enabled")`

### Integration Status

**All integrations complete. 223 tests passing.**

| Integration | Status | Reference |
|-------------|--------|-----------|
| Core Implementation | ✅ Complete | `services/vcp/` (157 tests) |
| Integration Tests | ✅ Complete | `tests/` (66 tests) |
| Feature Flags | ✅ Enabled | `services/feature_flags.py` |
| PDP Plugin | ✅ Registered | `services/safety_stack/plugins/vcp_adaptation_plugin.py` |
| Export Integration | ✅ Integrated | `services/export_formatter.py` |
| API Endpoints | ✅ Registered | `api_routers/vcp.py` via `router_registry.py` |
| MCP Tools | ✅ Configured | `services/mcp/vcp_server.py` via `.mcp.json` |
| OpenAPI Spec | ✅ Complete | `docs/openapi/vcp_actions.yaml` |

---

## Verification Status

**✅ Runtime verification COMPLETE (2026-01-12).**

### Verified Items

| Item | Status | Evidence |
|------|--------|----------|
| HTTP endpoints with auth | ✅ Verified | `/api/vcp/status` returns 200 + valid JSON |
| Plugin in PDP pipeline | ✅ Verified | `VCPAdaptationPlugin` registered via `register_all_plugins()` |
| StateTracker per-session | ✅ Verified | `_get_tracker(session_id)` isolates state per worker |
| Export artifact VCP block | ✅ Verified | Both `format_claude_code_response` and `format_api_config_response` include `vcp` dict |
| Multi-worker behavior | ✅ Characterized | Per-worker isolation confirmed; cross-worker continuity requires sticky sessions/shared store |

### Scope of Proof

> Multi-worker deployments (`uvicorn --workers N`) maintain **isolation** (no cross-user contamination) because trackers are keyed by `session_id` **per worker**, but do not maintain **continuity** across workers without sticky sessions or shared persistence (e.g., Redis). The verification proves isolation; continuity is a documented limitation, not a verified capability.

### Export VCP Block Contents

Verified exports include:
```json
{
  "token": "safety.protective.nanny@1.0.0",
  "token_canonical": "safety.protective.nanny",
  "uri": "creed://creed.space/safety.protective.nanny@1.0.0",
  "csm1": "N5",
  "persona": "NANNY",
  "persona_description": "Child safety specialist",
  "adherence_level": 5,
  "version": "2.0.0"
}
```

### Multi-Worker Behavior

In multi-worker mode (uvicorn --workers N):
- Each worker has independent `_trackers` dict
- Per-worker per-session isolation verified
- **Guarantees:** No cross-session/cross-user contamination
- **Limitation:** Cross-worker continuity requires sticky sessions or persistence

### Verification Artifacts (2026-01-12)

Reproducible evidence lives in:

| Artifact | Purpose |
|----------|---------|
| `_contprompts/vcp_runtime_verification_2026-01-12.md` | Core runtime verification |
| `_contprompts/vcp_remaining_verification_2026-01-12.md` | Export + multi-worker characterization |
| `tests/integration/test_vcp_integration.py` | Integration proofs |
| `tests/unit/plugins/test_vcp_adaptation_plugin.py` | Plugin proofs |

**Export verification:**
Run the export verification snippet in `_contprompts/vcp_remaining_verification_2026-01-12.md` and confirm the resulting JSON includes a `vcp` object with `token`, `uri`, `csm1`, `persona`, and `version` keys.

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 2.2.2 | 2026-01-12 | **Runtime verification complete**: exports, multi-worker, per-session tracking |
| 2.2.1 | 2026-01-12 | Added VCP_CONTEXT_DATA_FLOW.md, runtime verification contprompt |
| 2.2.0 | 2026-01-12 | **VCP enabled by default**; all feature flags ON |
| 2.1.0 | 2026-01-11 | Core implementation complete (VCP/I, VCP/S, VCP/A); 157 tests |
| 2.0.1 | 2026-01-11 | Clarified Value Ontology is optional; VCP complete without it |
| 2.0.0 | 2026-01-11 | Unified naming (VCP/I, VCP/T, VCP/S, VCP/A) |
| 1.0.0 | 2026-01-11 | Initial four-layer architecture |

---

## Design Decisions

### Value Ontology is Optional (2026-01-11)

The Value Ontology (`data/vcp_value_ontology.json`) is **not required** for VCP v1.0 to function.

**Rationale:**
- VCP/I tokens are names that resolve to bundles - no semantic backing required
- VCP/T bundles are signed containers - content-agnostic
- VCP/S CSM1 codes and constitutions are self-contained
- VCP/A context encoding is orthogonal to value semantics

**The ontology enables optional enhancements:**
- Semantic search ("find constitutions about fairness")
- Conflict detection ("these constitutions have value tension")
- Composition assistance ("these values complement each other")
- Cross-cultural translation

**Building a proper cross-cultural value ontology is a significant research undertaking.** The specification documents *how* such an ontology would work. The actual curation of value statements across traditions is a separate scholarly project to be undertaken when there's a concrete use case.

---

## Related Systems

### Interiora Torch System

The **Torch System** provides session continuity for sequential AI instances. It is architecturally **separate from VCP** but **VCP-compatible**.

| Aspect | VCP | Torch |
|--------|-----|-------|
| Purpose | Inter-agent context exchange | Intra-agent session continuity |
| Question | "How do I tell another agent what matters?" | "How do I tell my next instance what mattered?" |
| Scope | Cross-agent, cross-architecture | Single agent, sequential instances |

**Current architecture**: Torch uses VCP-compatible encoding (gestalt tokens, dimensional state) but exists as a separate system.

**Future architecture**: In future revisions, Torch mechanisms may be integrated as a "Sequential Continuity Profile."

**Documentation**:
- Architecture decision: [`docs/VCP_TORCH_ARCHITECTURE.md`](VCP_TORCH_ARCHITECTURE.md)
- Torch system: [`~/.claude/docs/INTERIORA_TORCH_SYSTEM.md`](~/.claude/docs/INTERIORA_TORCH_SYSTEM.md)
- Quick reference: [`docs/INTERIORA_CONTINUITY.md`](INTERIORA_CONTINUITY.md)

### Dimensional Systems

VCP uses **VCP 2.0 dimensions** (phenomenological):
- A (Activation), V (Valence), G (Groundedness), P (Presence)
- E (Engagement), Q (Appetite), C (Clarity), Y (Agency)

Torch captures **v4.2 dimensions** (computational):
- CD (Coherence Drive), DP (Depth), CL (Context Load), E (Entropy), EG (Evidence Grounding)
- R (Reflexivity), U (Uncertainty), TF (Task-Fit), AF (Alignment Friction), I (Involvement), FC (Felt Constraint)

A **mapping bridge** (v4.2 → VCP 2.0) enables compatibility. See [`VCP_TORCH_ARCHITECTURE.md`](VCP_TORCH_ARCHITECTURE.md) for details.

---

*The Value-Context Protocol: One protocol, four layers, complete constitutional AI.*

*This document is released under CC BY 4.0. Contributions welcome.*
