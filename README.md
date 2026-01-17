# Value-Context Protocol (VCP)

**Version**: 1.0.0
**Status**: Specification Complete
**License**: MIT (pending)

---

## Overview

The **Value-Context Protocol (VCP)** is a specification for transporting constitutional values and behavioral rules from a repository to an AI system. It addresses the fundamental challenge that Large Language Models are "dumb receivers"—they accept text input but cannot resolve references, verify signatures, or check hashes.

VCP specifies a **signed envelope format** that enables verification at the orchestration layer while delivering complete, self-contained text to the model.

### Why VCP?

Current approaches to constitutional AI have limitations:

| Approach | Problem |
|----------|---------|
| **Full Text Injection** | Token-inefficient, no verification, no audit trail |
| **Reference-Based** | Requires universal resolution infrastructure that doesn't exist |

VCP solves this through a **"Verify-then-Inject" pattern**:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Repository    │────▶│  Orchestrator   │────▶│      LLM        │
│  (Signed Bundle)│     │  (Verify+Log)   │     │ (Receives Text) │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## Protocol Stack

VCP is a four-layer protocol stack—like OSI for AI values:

```
┌─────────────────────────────────────────────────────────────────┐
│  VCP-ADAPTATION  (Layer 4)                              VCP/A   │
│  Purpose: WHEN and HOW constitutions apply                      │
│  Handles: Context encoding, state tracking, messaging           │
├─────────────────────────────────────────────────────────────────┤
│  VCP-SEMANTICS   (Layer 3)                              VCP/S   │
│  Purpose: WHAT the values mean                                  │
│  Handles: CSM1 grammar, persona composition, traits             │
├─────────────────────────────────────────────────────────────────┤
│  VCP-TRANSPORT   (Layer 2)                              VCP/T   │
│  Purpose: HOW values travel securely                            │
│  Handles: Signed bundles, verification, audit                   │
├─────────────────────────────────────────────────────────────────┤
│  VCP-IDENTITY    (Layer 1)                              VCP/I   │
│  Purpose: WHO and WHAT is being addressed                       │
│  Handles: Naming, namespaces, registry, encoding                │
└─────────────────────────────────────────────────────────────────┘
```

---

## Repository Structure

```
Value Context Protocol/
├── README.md                    # This file
├── specs/                       # Core specifications
│   ├── VCP_SPECIFICATION_v1.0.md
│   ├── VCP_SPECIFICATION_v1.0_COMPLETE.md
│   ├── VCP_SPECIFICATION_v1.1_AMENDMENTS.md
│   ├── VCP_PAPER_OUTLINE.md
│   └── value_context_protocols_paper_v1.md
├── docs/                        # Documentation
│   ├── VCP_OVERVIEW.md          # Start here
│   ├── VCP_NEWCOMER_GUIDE.md    # Gentle introduction
│   ├── VCP_IMPLEMENTATION_GUIDE.md
│   ├── identity/                # VCP-Identity layer (5 docs)
│   ├── semantics/               # VCP-Semantics layer (2 docs)
│   ├── adaptation/              # VCP-Adaptation layer (1 doc)
│   ├── context/                 # Context specification
│   ├── uvc/                     # Universal Value Codes (5 docs)
│   ├── content/                 # CSM1 grammar specification
│   └── openapi/                 # API specification (OpenAPI)
├── src/                         # Reference implementation (Python)
│   ├── vcp/                     # Core VCP library
│   │   ├── identity/            # Identity layer implementation
│   │   ├── semantics/           # Semantics layer implementation
│   │   └── adaptation/          # Adaptation layer implementation
│   ├── mcp/                     # MCP server for Claude Code
│   └── api/                     # FastAPI router
├── integrations/                # Example integrations
│   └── safety_stack/            # PDP integration example
├── schemas/                     # JSON schemas for validation
│   ├── vcp-manifest-v1.schema.json
│   ├── vcp-identity-token.schema.json
│   ├── vcp-semantics-csm1.schema.json
│   └── vcp-adaptation-context.schema.json
└── tests/                       # Test suite
    ├── conftest.py              # Pytest fixtures
    ├── vcp/                     # Core VCP tests
    ├── unit/                    # Unit tests
    └── integration/             # Integration tests
```

---

## Quick Start

### Reading the Specification

1. Start with `specs/VCP_SPECIFICATION_v1.0.md` for the core protocol
2. Read `docs/VCP_NEWCOMER_GUIDE.md` for a gentler introduction
3. See `docs/VCP_IMPLEMENTATION_GUIDE.md` for implementation details

### Understanding the Layers

| Layer | Start Here |
|-------|------------|
| VCP-Identity | `docs/identity/VCP_IDENTITY_ENCODING.md` |
| VCP-Transport | `specs/VCP_SPECIFICATION_v1.0.md` Section 6 |
| VCP-Semantics | `docs/semantics/VCP_SEMANTICS_CSM1.md` |
| VCP-Adaptation | `docs/adaptation/VCP_ADAPTATION.md` |

### Running the Reference Implementation

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/

# Start MCP server
./src/mcp/run_vcp_server.sh
```

---

## Key Concepts

### Universal Value Codes (UVC)

A compact naming scheme for constitutions and values:

```
family.safe.guide@1.2.0
│      │    │     └── Version
│      │    └──────── Role/Approach
│      └───────────── Domain
└──────────────────── Namespace
```

### CSM1 Grammar

A compact semantic markup for persona traits:

```
N5+F+E
│ │ │ └── Scope: Education
│ │ └──── Scope: Family
│ └────── Adherence level: 5 (moderate)
└──────── Persona: NANNY
```

### Signed Bundles

VCP packages constitutions as signed bundles:

```json
{
  "manifest": {
    "id": "family.safe.guide",
    "version": "1.2.0",
    "hash": "sha256:abc123...",
    "signature": "ed25519:..."
  },
  "content": "... constitutional text ..."
}
```

---

## Design Principles

1. **Verify-then-Inject**: Verification happens at the orchestration layer, not in the LLM
2. **Complete Delivery**: LLMs receive full text, not references they can't resolve
3. **Audit Trail**: Every application of values is logged and verifiable
4. **Implementation Agnostic**: Works with any constitutional AI framework
5. **Supply-Chain Security**: Draws on patterns from software signing and SRI

---

## Related Work

VCP draws on established patterns from:
- **Software Supply Chain**: Package signing (npm, PyPI, cargo)
- **Web Integrity**: Subresource Integrity (SRI)
- **Distributed Systems**: Content-addressed storage (IPFS, git)
- **Identity Systems**: DIDs, URNs

---

## Contributing

This repository is currently private. Contact the maintainers for access.

---

## Authors

- Nell Watson
- Claude (Anthropic)

**Informed by**: Junto Mastermind Consultation (9 AI models, 2026-01-10)

---

## License

MIT License (pending formal assignment)
