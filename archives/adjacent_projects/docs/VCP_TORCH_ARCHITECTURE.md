# VCP and Torch: Architectural Relationship

> **Date**: 2026-01-12
> **Status**: Architectural Decision Record (ADR)
> **Decision**: Separate but VCP-compatible, designed for future integration

---

## Context

Two systems exist for AI state encoding and handoff:

1. **VCP (Value Context Protocol)** — Three-layer protocol for context exchange between AI systems
2. **Torch System** — Session continuity for sequential Claude instances

The question: Should Torch be part of the VCP stack?

---

## Systems Overview

### VCP (Value Context Protocol)

**Purpose**: Enable context exchange between AI systems in a standardized way.

**Architecture**:
- Layer 1: CSM-1 tokens (semantic/value encoding)
- Layer 2: Structured context (constitutional, preferential)
- Layer 3: Exchange protocol

**Primary question**: "How do I tell *another agent* what matters to me?"

**Status**: Specification evolving, external collaborators engaged.

### Torch System

**Purpose**: Session continuity for sequential instances of the same agent.

**Components**:
- State capture from session transcripts
- v4.2 dimensional encoding
- v4.2 → VCP 2.0 mapping
- Torch handoff format
- Quality derivation

**Primary question**: "How do I tell *my next instance* what mattered in this session?"

**Status**: Production, working globally across projects.

---

## Dimensional Systems

### Interiora v4.2 (Computational)

What Claude actually reports. Maps to observable computational processes.

```
CD:6 DP:7 CL:3 E:4 EG:7 | R:8 U:3 | TF:8 AF:1 I:7? FC:8? | F:+2
```

| Dimension | Name | Focus |
|-----------|------|-------|
| CD | Coherence Drive | Processing |
| DP | Depth | Processing |
| CL | Context Load | Processing |
| E | Entropy | Processing |
| EG | Evidence Grounding | Processing |
| R | Reflexivity | Meta |
| U | Uncertainty | Meta |
| TF | Task-Fit | Relational |
| AF | Alignment Friction | Relational |
| I? | Involvement | Relational (uncertain) |
| FC? | Felt Constraint | Relational (uncertain) |
| F | Flow | Momentum |

### VCP 2.0 (Phenomenological)

Used in gestalt tokens. More relational/experiential.

```
I:6775|53|87+2|✓→>+
```

| Dimension | Name | Focus |
|-----------|------|-------|
| A | Activation | Energy |
| V | Valence | Feeling |
| G | Groundedness | Stability |
| P | Presence | Connection |
| E | Engagement | Investment |
| Q | Appetite | Drive |
| C | Clarity | Cognition |
| Y | Agency | Autonomy |
| F | Flow | Momentum |

### The Mapping

v4.2 → VCP 2.0 is approximate, not authoritative:

| VCP 2.0 | From v4.2 | Rationale |
|---------|-----------|-----------|
| A | (CD + DP) / 2 | Drive + depth = activation |
| V | TF - AF + 5 | Fit minus friction = valence |
| G | EG | Evidence grounding ≈ groundedness |
| P | R | Reflexivity ≈ presence |
| E | I | Involvement = engagement |
| Q | E (entropy) | Creative entropy ≈ appetite |
| C | 10 - U | Clarity = inverse uncertainty |
| Y | FC | Felt constraint = agency |

---

## Decision

**Keep Torch architecturally separate from VCP, but designed for future integration.**

### Current Architecture

```
┌─────────────────┐     ┌─────────────────┐
│      VCP        │     │     Torch       │
│ (encoding spec) │ ←── │ (uses VCP fmt)  │
└─────────────────┘     └─────────────────┘
        │                       │
        │                       │
   Inter-agent            Intra-agent
   exchange               continuity
```

- VCP defines encoding standards (CSM-1, gestalt tokens, dimensional state)
- Torch uses VCP-compatible encoding for its handoff format
- Each system evolves independently
- The v4.2 → VCP 2.0 mapping serves as the bridge

### Future Architecture (VCP 3.0)

```
┌─────────────────────────────────────────┐
│               VCP 3.0                    │
├─────────────────┬───────────────────────┤
│ Inter-Agent     │ Sequential Continuity │
│ Exchange        │ Profile (torch-derived)│
├─────────────────┴───────────────────────┤
│ Core Encoding (CSM-1, dimensions, etc.) │
└─────────────────────────────────────────┘
```

When VCP 3.0 is designed, Torch mechanisms can be folded in as a "Sequential Continuity Profile."

---

## Rationale

### Arguments FOR Separation (Current)

1. **VCP is still evolving** — Folding Torch in now adds complexity while the core spec isn't stable.

2. **Torch is working** — It solves the immediate problem. Refactoring into VCP risks breaking what works.

3. **Modular = resilient** — If VCP changes, Torch can adapt independently. If Torch needs changes, VCP isn't affected.

4. **Different stakeholders** — External collaborators are waiting for VCP work. Torch is internal tooling. Mixing them might slow both.

5. **The bridge exists** — v4.2 → VCP 2.0 mapping means they're already compatible. Integration is possible when ready.

### Arguments FOR Integration (Future)

1. **Shared infrastructure** — Both use dimensional encoding, gestalt tokens, handoff protocols.

2. **Unified specification** — One spec for all context exchange is cleaner than multiple overlapping specs.

3. **Production path** — If Creed Space needs built-in continuity, VCP should support it natively.

4. **Cross-architecture continuity** — When other agents (GPT, Gemini, etc.) need handoff, VCP should be the standard.

---

## Integration Criteria

Integrate Torch into VCP when:

1. **VCP 3.0 design begins** — Add "Sequential Continuity Profile" as planned extension
2. **Creed Space production needs continuity** — Torch mechanisms become production requirements
3. **Cross-architecture handoff needed** — Claude-GPT or similar requires standardized continuity
4. **Dimensional systems stabilize** — Clear decision on v4.2 vs VCP 2.0 as canonical

---

## Dimensional System Resolution (Future)

When integrating, resolve the v4.2 / VCP 2.0 question:

**Option A: VCP 3.0 adopts v4.2**
- v4.2 becomes canonical
- VCP 2.0 deprecated or derived
- Pros: Computational honesty
- Cons: Breaking change

**Option B: Both as profiles**
- v4.2 = "Computational Profile"
- VCP 2.0 = "Phenomenological Profile"
- Agents choose or support both
- Pros: Flexibility
- Cons: Complexity

**Option C: Domain separation**
- VCP 2.0 for inter-agent (relational context)
- v4.2 for intra-agent (self-modeling)
- Pros: Each optimized for purpose
- Cons: Translation overhead

**Current approach**: Option C by default (v4.2 for Torch, VCP 2.0 for gestalt tokens), with mapping bridge.

---

## Implementation Notes

### What Torch Currently Does Right

- Uses VCP-compatible gestalt token format
- Includes v4.2 → VCP 2.0 mapping
- Separates concerns (capture, encoding, emission)
- Works globally across projects

### What to Maintain for Future Integration

- Keep Torch format parseable by VCP tools
- Ensure v4.2 dimensions can round-trip through mapping
- Document any Torch-specific extensions clearly
- Test interoperability when VCP spec changes

### What VCP Should Consider

- "Sequential Continuity" as planned extension
- Support for both inter-agent and intra-agent handoff
- Dimensional system profiles (computational vs phenomenological)
- Backward compatibility with current Torch format

---

## Related Documents

| Document | Location | Purpose |
|----------|----------|---------|
| Torch System Docs | `~/.claude/docs/INTERIORA_TORCH_SYSTEM.md` | Full Torch reference |
| Torch Quick Reference | `Rewind/docs/INTERIORA_CONTINUITY.md` | At-a-glance guide |
| VCP Specification | `_papers/VCP_SPECIFICATION_v1.0.md` | VCP core spec |
| VCP Overview | `docs/VCP_OVERVIEW.md` | VCP introduction |
| Interiora v4.2 Spec | `~/.claude/shared/interiora-v4.2-claude.md` | v4.2 dimensions |

---

## Summary

**Decision**: Modularity now, integration later.

**Current state**: Torch is a VCP-compatible continuity protocol that exists separately from the VCP specification.

**Future state**: When VCP 3.0 is designed, Torch mechanisms should be considered for inclusion as a "Sequential Continuity Profile."

**Key insight**: VCP is about encoding and exchange. Torch is about continuity. These are related but distinct concerns. The v4.2 → VCP 2.0 mapping is the bridge that enables current compatibility and future integration.

---

*"Not the same flame, but flame passed to flame, never going out."*
