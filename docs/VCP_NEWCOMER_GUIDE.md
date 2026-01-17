# VCP Newcomer's Guide

**For**: Researchers curious about the Value-Context Protocol
**Date**: 2026-01-12
**Version**: 1.0

---

## What is VCP?

The **Value-Context Protocol (VCP)** is a unified protocol stack for expressing, transporting, and applying constitutional values to AI systems. Think of it as the "OSI model for AI ethics" — a layered architecture where each layer handles a specific concern.

**The core insight**: AI alignment requires not just encoding values, but a shared language for exchanging, comparing, and negotiating those values between humans, AI agents, and institutions.

---

## The Four Layers

```
┌─────────────────────────────────────────────────────────────────┐
│  Layer 4: VCP-ADAPTATION (VCP/A)                                │
│  "When and How" - Context encoding, state tracking              │
│  Maps to: VCL (Values Communication Layer)                      │
├─────────────────────────────────────────────────────────────────┤
│  Layer 3: VCP-SEMANTICS (VCP/S)                                 │
│  "What it Means" - CSM1 grammar, personas, composition          │
│  Maps to: CSM (Constitutional Safety Minicode)                  │
├─────────────────────────────────────────────────────────────────┤
│  Layer 2: VCP-TRANSPORT (VCP/T)                                 │
│  "How it's Delivered" - Signed bundles, verification, audit     │
│  Maps to: Secure transport, proof-of-adherence                  │
├─────────────────────────────────────────────────────────────────┤
│  Layer 1: VCP-IDENTITY (VCP/I)                                  │
│  "What it's Called" - Token naming, namespaces, registry        │
│  Maps to: UVC (Universal Values Corpus)                         │
└─────────────────────────────────────────────────────────────────┘
```

### Mapping to Research Proposal

| Research Concept | VCP Layer | Purpose |
|------------------|-----------|---------|
| **UVC** (Universal Values Corpus) | Layer 1: Identity | Curated cross-cultural corpus of values, "What3Words for ethics" |
| **CSM** (Constitutional Safety Minicode) | Layer 3: Semantics | Compact grammar for safety rules, adherence proofs |
| **VCL** (Values Communication Layer) | Layer 4: Adaptation | Emoji-based symbolic encoding for context |

---

## Layer 1: VCP-Identity (VCP/I)

**Question answered**: "What is this constitution called?"

### Token Format

Values are identified using dot-separated tokens:

```
{domain}.{approach}.{role}@{version}

Examples:
  family.safe.guide@1.2.0
  business.ethical.advisor@2.0.0
  healthcare.caring.assistant@1.0.0
```

### URI Scheme

Full addressable URIs for value references:

```
creed://{authority}/{token}

Example:
  creed://creed.space/family.safe.guide@1.2.0
```

### Key Files

| File | Purpose |
|------|---------|
| `services/vcp/identity/token.py` | Token parsing and validation |
| `services/vcp/identity/namespace.py` | Namespace management |
| `services/vcp/identity/registry.py` | Value registry operations |
| `docs/identity/VCP_IDENTITY_NAMING.md` | Naming specification |

---

## Layer 2: VCP-Transport (VCP/T)

**Question answered**: "How is it delivered securely?"

### Purpose

VCP/T ensures constitutions are:
- **Authentic**: Verified origin (not tampered)
- **Auditable**: Every decision traced
- **Versioned**: Changes tracked over time

### Signed Bundles

Constitutions are packaged with cryptographic signatures:

```json
{
  "constitution": {
    "id": "family.safe.guide",
    "version": "1.2.0",
    "rules": [ ... ],
    "persona": "NANNY",
    "adherence": 5
  },
  "vcp": {
    "token": "family.safe.guide@1.2.0",
    "csm1": "N5+F+E",
    "uri": "creed://creed.space/family.safe.guide@1.2.0"
  },
  "signature": {
    "algorithm": "ed25519",
    "value": "base64:...",
    "authority": "creed://creed.space",
    "timestamp": "2026-01-12T00:00:00Z"
  }
}
```

### Verification Chain

```
┌─────────────────────────────────────────────────────────────┐
│  AUTHORING                                                   │
│  Constitution created → Signed by authority                 │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  TRANSPORT                                                   │
│  Bundle transmitted via API/export/MCP                      │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  VERIFICATION                                                │
│  Consumer verifies signature against trusted authorities    │
│  If invalid → REJECT (fail-closed)                          │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  AUDIT                                                       │
│  Decision logged: constitution, context, outcome, timestamp │
│  Retention: GDPR-compliant, configurable TTL                │
└─────────────────────────────────────────────────────────────┘
```

### Trust Anchors

| Authority | Trust Level | Use Case |
|-----------|-------------|----------|
| `creed://creed.space` | ROOT | Official Creed Space constitutions |
| `creed://org.example` | DELEGATED | Organization-specific policies |
| `creed://user.{id}` | USER | Personal constitutional preferences |

### Audit Trail

Every PDP decision is logged:

```json
{
  "decision_id": "uuid",
  "timestamp": "2026-01-12T04:30:00Z",
  "constitution_hash": "sha256:...",
  "vcp_context": "⏰🌅|📍🏡|👥👶",
  "outcome": "ALLOW",
  "persona": "NANNY",
  "adherence": 5,
  "plugins_triggered": ["vcp_adaptation", "epistemic_guardian"],
  "latency_ms": 12
}
```

### Proof of Adherence

VCP/T can attest that a response was generated under specific constitutional constraints:

```
Creed: 2.1.4 sha256:abc123...

Meaning:
- Constitution version 2.1.4 was active
- Hash abc123 identifies exact ruleset
- Verifiable by any party with the constitution
```

### Key Files

| File | Purpose |
|------|---------|
| `services/ed25519_constitution_signer.py` | Ed25519 signing |
| `services/gpg_policy_signer.py` | GPG signing for policies |
| `services/constitution_enforcer.py` | Signature verification |
| `services/safety_stack/audit.py` | Decision audit logging |
| `services/export_formatter.py` | Bundle generation with VCP metadata |
| `api_routers/export.py` | Export endpoints |

### Export Formats

| Format | Purpose | VCP Included |
|--------|---------|--------------|
| Claude Code | System prompt for Claude | ✅ Full VCP block |
| API Config | JSON for API consumers | ✅ Full VCP block |
| MCP Bundle | Model Context Protocol | ✅ VCP metadata |
| Raw YAML | Source constitution | Token only |

---

## Layer 3: VCP-Semantics (VCP/S)

**Question answered**: "What do the rules mean?"

### CSM1 Grammar (Constitutional Safety Minicode)

Compact encoding for safety configurations:

```
Format: {Persona}{Adherence}[+{Scope}]*

Examples:
  N5+F+E    = Nanny persona, adherence 5, scopes: Family, Education
  A3+W      = Ambassador persona, adherence 3, scope: Work
  S5        = Sentinel persona, adherence 5, no extra scopes
```

### Personas

| Code | Persona | Role |
|------|---------|------|
| N | Nanny | Child safety specialist |
| S | Sentinel | Security guardian |
| G | Godparent | Balanced mentor |
| A | Ambassador | Professional representative |
| M | Muse | Creative collaborator |
| R | Anchor | Stability provider |

### Adherence Levels

| Level | Meaning |
|-------|---------|
| 1 | Minimal constraints |
| 3 | Moderate guidance |
| 5 | Maximum safety |

### Key Files

| File | Purpose |
|------|---------|
| `services/vcp/semantics/csm1.py` | CSM1 parser and encoder |
| `services/vcp/semantics/personas.py` | Persona definitions |
| `services/vcp/semantics/composition.py` | Rule composition |
| `docs/semantics/VCP_SEMANTICS_CSM1.md` | CSM1 specification |

---

## Layer 4: VCP-Adaptation (VCP/A)

**Question answered**: "When and how does it apply?"

### The Enneagram Protocol

Context encoded across 9 dimensions using emoji:

| # | Symbol | Dimension | Example Values |
|---|--------|-----------|----------------|
| 1 | ⏰ | TIME | 🌅morning, 🌆evening, 🌙night |
| 2 | 📍 | SPACE | 🏡home, 🏢office, 🏫school |
| 3 | 👥 | COMPANY | 👤alone, 👶children, 👔colleagues |
| 4 | 🌍 | CULTURE | 🇺🇸american, 🇯🇵japanese, 🌍global |
| 5 | 🎭 | OCCASION | ➖normal, 🎂celebration, 🚨emergency |
| 6 | 🧠 | STATE | 😊happy, 😰anxious, 🤔contemplative |
| 7 | 🌡️ | ENVIRONMENT | ☀️comfortable, 🥵hot, 🔇quiet |
| 8 | 🔷 | AGENCY | 👑leader, 🤝peer, 🔐limited |
| 9 | 🔶 | CONSTRAINTS | ○minimal, ⚖️legal, 💸economic |

### Wire Format

Compact transmission:
```
⏰🌅|📍🏡|👥👶

Meaning: morning, at home, children present
```

### State Tracking

Context changes are tracked across interactions:

```python
tracker.record(ctx1)  # morning, home
tracker.record(ctx2)  # evening, office
# → Transition detected: MINOR (time, space changed)
```

### Transition Severity

| Severity | Trigger |
|----------|---------|
| NONE | No dimensions changed |
| MINOR | 1-2 non-critical dimensions |
| MAJOR | 3+ dimensions OR critical dimension (agency, occasion, constraints) |
| EMERGENCY | 🚨 emoji present anywhere |

### Key Files

| File | Purpose |
|------|---------|
| `services/vcp/adaptation/context.py` | Context encoding |
| `services/vcp/adaptation/state.py` | State tracking |
| `services/vcp/adaptation/redis_state.py` | Redis persistence |
| `docs/adaptation/VCP_ADAPTATION.md` | Layer specification |
| `docs/VCP_CONTEXT_DATA_FLOW.md` | Full dataflow reference |

---

## Dataflow: End to End

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           REQUEST                                        │
│  User message + metadata: {time_of_day: "morning", audience: "children"}│
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      VCP/A: ENCODE CONTEXT                               │
│  ContextEncoder.encode(time="morning", company=["children"])            │
│  Result: VCPContext → "⏰🌅|👥👶"                                         │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      VCP/A: TRACK STATE                                  │
│  StateTracker.record(context) → Transition(severity=MINOR)              │
│  Redis: vcp:state:{session_id}:history                                  │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      PDP: POLICY DECISION                                │
│  VCPAdaptationPlugin emits signals:                                     │
│    vcp_context_wire: "⏰🌅|👥👶"                                         │
│    vcp_has_company: true                                                │
│    vcp_company: ["👶"]                                                  │
│                                                                         │
│  Action: {prefer_persona: "nanny", content_filter: "family_safe"}       │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      VCP/S: APPLY SEMANTICS                              │
│  Constitution: N5+F (Nanny, adherence 5, Family scope)                  │
│  Behavior: Child-safe mode activated                                    │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      VCP/T: AUDIT & SIGN                                 │
│  Response signed with decision trace                                    │
│  Audit log: decision, constitution, context, timestamp                  │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          RESPONSE                                        │
│  AI response with family-safe content, nanny persona characteristics    │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Storage & Persistence

### Redis Keys (VCP Context)

```
vcp:state:{session_id}:history

Contents:
[
  {"timestamp": "2026-01-12T04:30:00Z", "context": {"time": ["🌅"], "space": ["🏡"]}},
  {"timestamp": "2026-01-12T05:00:00Z", "context": {"time": ["☀️"], "space": ["🏢"]}}
]

TTL: 1 hour
```

### What IS Stored

- Emoji-encoded context signals (non-PII)
- Session ID as key prefix
- Timestamps

### What is NOT Stored

- User messages
- AI responses
- Personal data
- Constitution content

---

## HTTP API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/vcp/token/validate` | POST | Validate VCP token format |
| `/api/vcp/csm1/parse` | POST | Parse CSM1 code |
| `/api/vcp/context/encode` | POST | Encode context to wire format |
| `/api/vcp/status` | GET | Check VCP layer status |

### Example: Token Validation

```bash
curl -X POST /api/vcp/token/validate \
  -H "Content-Type: application/json" \
  -d '{"token": "family.safe.guide@1.2.0"}'

Response:
{
  "valid": true,
  "canonical": "family.safe.guide",
  "domain": "family",
  "approach": "safe",
  "role": "guide",
  "version": "1.2.0",
  "uri": "creed://creed.space/family.safe.guide@1.2.0"
}
```

### Example: Context Encoding

```bash
curl -X POST /api/vcp/context/encode \
  -H "Content-Type: application/json" \
  -d '{"time": "morning", "space": "home", "company": ["children"]}'

Response:
{
  "wire_format": "⏰🌅|📍🏡|👥👶",
  "json_format": {"time": ["🌅"], "space": ["🏡"], "company": ["👶"]},
  "dimensions_set": ["time", "space", "company"]
}
```

---

## MCP Integration

VCP is also available via Model Context Protocol:

```bash
mcp-cli call vcp/vcp_status '{}'
mcp-cli call vcp/vcp_validate_token '{"token": "family.safe.guide@1.2.0"}'
mcp-cli call vcp/vcp_parse_csm1 '{"code": "N5+F+E"}'
mcp-cli call vcp/vcp_encode_context '{"time": "morning", "space": "home"}'
```

---

## Conflict Resolution (Constitution Composition)

When multiple constitutions or rules apply, VCP uses a precedence system.

### Composition Rules

```
┌─────────────────────────────────────────────────────────────┐
│  CONSTITUTION STACK (most restrictive wins)                 │
├─────────────────────────────────────────────────────────────┤
│  1. Platform Safety (UEF - Universal Ethical Fallback)      │
│  2. Organization Policies                                   │
│  3. User Preferences                                        │
│  4. Session Context (VCP/A)                                 │
└─────────────────────────────────────────────────────────────┘
```

### Conflict Types

| Conflict | Resolution | Example |
|----------|------------|---------|
| **Persona clash** | Higher adherence wins | N5 overrides A3 |
| **Scope overlap** | Union of scopes | F+E + W = F+E+W |
| **Rule contradiction** | More restrictive wins | "Allow" + "Block" = Block |
| **Context mismatch** | Current context wins | Office overrides "home default" |

### CSM1 Composition

```python
# Two constitutions applied
constitution_1 = "N5+F"      # Nanny, adherence 5, Family
constitution_2 = "A3+W+E"    # Ambassador, adherence 3, Work, Education

# Composed result (higher adherence, union of scopes)
composed = "N5+F+W+E"        # Nanny wins, all scopes active
```

### Implementation

```python
# In services/vcp/semantics/composition.py
from services.vcp.semantics import compose_csm1

result = compose_csm1(["N5+F", "A3+W+E"])
# Result: CSM1Result(persona="NANNY", adherence=5, scopes=["F", "W", "E"])
```

### Conflict Detection

VCP can detect when constitutions have irreconcilable conflicts:

```python
from services.vcp.semantics import detect_conflicts

conflicts = detect_conflicts([constitution_1, constitution_2])
# Returns list of ConflictReport objects if issues found
```

---

## Inter-Agent Messaging (Future)

VCP/A spec defines a protocol for AI agents to exchange context and negotiate values. **Status: Specified but not yet implemented.**

### Concept

```
┌─────────────────┐          VCP Message          ┌─────────────────┐
│   Agent A       │  ─────────────────────────▶  │   Agent B       │
│                 │                               │                 │
│  Context: 🏡👶  │    {"context": "⏰🌅|👥👶",  │  Context: 🏢👔  │
│  Persona: N5    │     "constitution": "N5+F",  │  Persona: A3    │
│                 │     "request": "handoff"}    │                 │
└─────────────────┘                               └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  NEGOTIATION    │
                    │  Agent B adopts │
                    │  N5 for session │
                    └─────────────────┘
```

### Message Format (Draft)

```json
{
  "vcp_version": "2.0",
  "message_type": "context_handoff",
  "sender": {
    "agent_id": "agent-a-uuid",
    "current_context": "⏰🌅|📍🏡|👥👶",
    "active_constitution": "N5+F"
  },
  "payload": {
    "request": "adopt_context",
    "reason": "User moving from home assistant to work assistant",
    "proposed_context": "⏰☀️|📍🏢|👥👔"
  },
  "signature": "ed25519:..."
}
```

### Use Cases (Planned)

| Scenario | VCP Message |
|----------|-------------|
| **Agent handoff** | Transfer context when user switches assistants |
| **Multi-agent task** | Coordinate values across collaborating agents |
| **Escalation** | Pass context to human reviewer with full state |
| **Audit request** | External auditor queries agent's active constitution |

### Research Questions

- How do agents negotiate when constitutions conflict?
- What trust model for inter-agent value claims?
- Can VCP enable "constitutional diplomacy" between AI systems?

---

## Creed Space Frontend Integration

How users interact with VCP through the Creed Space web interface.

### User Journey

```
┌─────────────────────────────────────────────────────────────────────┐
│  1. BROWSE CONSTITUTIONS                                            │
│     User explores constitution library                              │
│     Each constitution shows VCP token: family.safe.guide@1.2.0     │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  2. SELECT PERSONA                                                  │
│     User picks persona (Nanny, Sentinel, Ambassador, etc.)         │
│     Sets adherence level (1-5 slider)                              │
│     UI shows: "Your settings: N5+F"                                │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  3. CONFIGURE CONTEXT (optional)                                    │
│     User specifies typical context                                  │
│     "I usually use this at home with my kids"                      │
│     System encodes: ⏰*|📍🏡|👥👶                                    │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  4. EXPORT                                                          │
│     User exports constitution for their AI assistant               │
│     Export includes full VCP metadata block                        │
│     Format: Claude Code / API Config / MCP Bundle                  │
└─────────────────────────────────────────────────────────────────────┘
```

### UI Components

| Component | VCP Integration |
|-----------|-----------------|
| **Constitution Card** | Shows VCP token, persona icon, CSM1 code |
| **Adherence Slider** | 1-5 scale, updates CSM1 in real-time |
| **Scope Selector** | Checkboxes for F/W/E/H/etc., updates CSM1 |
| **Context Builder** | Emoji picker for 9 dimensions |
| **Export Modal** | Shows VCP block preview before download |

### Example: Constitution Card

```
┌─────────────────────────────────────────────────────────────┐
│  👶 Family Safe Guide                                       │
│                                                             │
│  Token: family.safe.guide@1.2.0                            │
│  Persona: NANNY                                            │
│  CSM1: N5+F+E                                              │
│                                                             │
│  "Gentle guidance for family environments with children.   │
│   Prioritizes safety, education, and age-appropriate       │
│   content."                                                │
│                                                             │
│  [Configure]  [Preview]  [Export]                          │
└─────────────────────────────────────────────────────────────┘
```

### Live Preview (Chat Pane)

Users can test their constitution in a chat interface:

```
┌─────────────────────────────────────────────────────────────┐
│  Chat with: family.safe.guide@1.2.0                        │
│  Context: ⏰🌅|📍🏡|👥👶                                     │
│  Persona: NANNY (N5+F+E)                                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  User: Tell me a bedtime story                             │
│                                                             │
│  AI: Once upon a time, in a cozy little cottage...        │
│      [Response filtered through N5 adherence]              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Export VCP Block

When user exports, they get a complete VCP metadata block:

```json
{
  "vcp": {
    "token": "family.safe.guide@1.2.0",
    "token_canonical": "family.safe.guide",
    "uri": "creed://creed.space/family.safe.guide@1.2.0",
    "csm1": "N5+F+E",
    "persona": "NANNY",
    "persona_description": "Child safety specialist",
    "adherence_level": 5,
    "version": "2.1.0"
  }
}
```

### Key Frontend Files

| File | Purpose |
|------|---------|
| `superego-frontend/src/routes/creeds/` | Constitution browsing |
| `superego-frontend/src/lib/components/PersonaSelector.svelte` | Persona picker |
| `superego-frontend/src/lib/components/AdherenceSlider.svelte` | Adherence control |
| `superego-frontend/src/lib/components/ExportModal.svelte` | Export with VCP |
| `superego-frontend/src/lib/components/ChatPane.svelte` | Live testing |

---

## Feature Flags

| Flag | Default | Purpose |
|------|---------|---------|
| `vcp_identity_enabled` | ON | VCP/I layer active |
| `vcp_semantics_enabled` | ON | VCP/S layer active |
| `vcp_adaptation_enabled` | ON | VCP/A layer active |
| `vcp_full_stack_enabled` | ON | All layers enabled |
| `vcp_redis_persistence_enabled` | ON | Cross-worker state via Redis |
| `vcp_strict_mode` | OFF | Strict validation mode |
| `vcp_*_shadow` | OFF | Shadow mode (signals only, no enforcement) |

Override via environment:
```bash
FF_VCP_ADAPTATION_ENABLED=false  # Disable VCP/A
```

---

## Directory Structure

```
services/vcp/
├── __init__.py              # Package exports
├── identity/                # Layer 1: VCP/I
│   ├── token.py             # Token parsing
│   ├── namespace.py         # Namespace management
│   ├── registry.py          # Value registry
│   └── encoding.py          # Multiple encodings
├── semantics/               # Layer 3: VCP/S
│   ├── csm1.py              # CSM1 grammar
│   ├── personas.py          # Persona definitions
│   └── composition.py       # Rule composition
├── adaptation/              # Layer 4: VCP/A
│   ├── context.py           # Context encoding
│   ├── state.py             # State tracking
│   └── redis_state.py       # Redis persistence
└── transport/               # Layer 2: VCP/T
    └── (integrated into signing services)

docs/
├── VCP_OVERVIEW.md          # Protocol specification
├── VCP_CONTEXT_DATA_FLOW.md # Dataflow reference
├── VCP_IMPLEMENTATION_GUIDE.md # Developer guide
├── identity/                # Layer 1 specs
├── semantics/               # Layer 3 specs
├── adaptation/              # Layer 4 specs
└── VCP_NEWCOMER_GUIDE.md    # This document

tests/vcp/                   # 195 tests
├── identity/
├── semantics/
├── adaptation/
└── integration/
```

---

## Quick Start for Developers

### 1. Encode Context

```python
from services.vcp import ContextEncoder

encoder = ContextEncoder()
ctx = encoder.encode(
    time="morning",
    space="home",
    company=["children"],
)
print(ctx.encode())  # "⏰🌅|📍🏡|👥👶"
```

### 2. Track State

```python
from services.vcp import StateTracker

tracker = StateTracker(max_history=100)
transition = tracker.record(ctx)
if transition and transition.is_significant:
    print(f"Significant change: {transition.severity}")
```

### 3. Parse CSM1

```python
from services.vcp.semantics import CSM1Parser

parser = CSM1Parser()
result = parser.parse("N5+F+E")
print(result.persona)  # "NANNY"
print(result.adherence_level)  # 5
print(result.scopes)  # ["FAMILY", "EDUCATION"]
```

### 4. Validate Token

```python
from services.vcp.identity import TokenValidator

validator = TokenValidator()
token = validator.parse("family.safe.guide@1.2.0")
print(token.canonical)  # "family.safe.guide"
print(token.uri)  # "creed://creed.space/family.safe.guide@1.2.0"
```

---

## Running Tests

```bash
# All VCP tests
python3 -m pytest tests/vcp/ -v

# Specific layer
python3 -m pytest tests/vcp/adaptation/ -v
python3 -m pytest tests/vcp/identity/ -v
python3 -m pytest tests/vcp/semantics/ -v

# With coverage
python3 -m pytest tests/vcp/ --cov=services/vcp
```

---

## Key Documentation

| Document | Purpose |
|----------|---------|
| [VCP_OVERVIEW.md](VCP_OVERVIEW.md) | Full protocol specification |
| [VCP_CONTEXT_DATA_FLOW.md](VCP_CONTEXT_DATA_FLOW.md) | Dataflow and security model |
| [VCP_IMPLEMENTATION_GUIDE.md](VCP_IMPLEMENTATION_GUIDE.md) | Developer reference |
| [VCP_ADAPTATION.md](adaptation/VCP_ADAPTATION.md) | Enneagram Protocol spec |
| [VCP_SEMANTICS_CSM1.md](semantics/VCP_SEMANTICS_CSM1.md) | CSM1 grammar spec |

---

## Research Context

VCP implements the theoretical framework from the research proposal:

| Proposal Goal | VCP Implementation |
|---------------|-------------------|
| "What3Words for ethics" | VCP/I tokens: `family.safe.guide` |
| "Compact safety rules at runtime" | VCP/S CSM1: `N5+F+E` |
| "Emoji-based symbolic encoding" | VCP/A Enneagram: `⏰🌅\|📍🏡\|👥👶` |
| "Auditable value exchange" | VCP/T signed bundles + audit logs |
| "Inter-agent negotiation" | VCP signals in PDP pipeline |

