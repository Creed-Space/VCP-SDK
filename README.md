# VCP SDK

**Version**: 1.1.0
**Status**: Specification Complete | Python SDK Complete | Rust SDK In Progress
**License**: MIT (pending)

> **See also**: [VCP Demo Site](https://vcp-demo.onrender.com) — Interactive demos and documentation website

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

## SDK Languages

| Language | Directory | Status | Use Case |
|----------|-----------|--------|----------|
| **Python** | [`python/`](./python/) | Complete | Reference implementation, LLM integration, persona logic |
| **Rust** | [`rust/`](./rust/) | In Progress | High-performance parsing, WASM/browser, embedded, CLI tooling |
| **TypeScript (WebMCP)** | [`webmcp/`](./webmcp/) | Complete | Browser-side tool registration via `navigator.modelContext` (Chrome 145+) |

### Python SDK

Full VCP implementation with identity resolution, CSM-1 encoding, context management, and LLM integration.

```bash
cd python
pip install -r requirements.txt
pytest tests/
```

### Rust SDK (`vcp-core`)

Data-plane implementation for parsing, encoding, and verification. Targets `no_std` compatibility and WASM via `wasm-bindgen`.

```bash
cd rust
cargo build
cargo test
```

**Crates**:
- `vcp-core` — Identity, CSM-1, context, transport (core library)
- `vcp-wasm` — Browser bindings via wasm-bindgen
- `vcp-cli` — Command-line tool (`vcp parse`, `vcp encode`, `vcp verify`)

### WebMCP SDK (`@vcp/webmcp`)

TypeScript package for registering VCP tools with the browser's WebMCP API (`navigator.modelContext`). Enables AI agents to discover and call VCP capabilities on any website.

```bash
cd webmcp
npm install
npm run check  # typecheck
npm run build  # compile to dist/
```

**Features**:
- 5 tools: `vcp_chat`, `vcp_build_token`, `vcp_parse_token`, `vcp_transmission_summary`, `vcp_list_personas`
- Agent activity indicator via `webmcp:tool-call` events
- MCP-B polyfill support for non-Chrome browsers
- Framework-agnostic with dependency injection for token encoding/parsing

See [`webmcp/README.md`](./webmcp/README.md) for full documentation.

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
VCP-SDK/
├── README.md                    # This file
├── specs/                       # Core specifications (shared)
│   ├── VCP_SPECIFICATION_v1.0.md
│   ├── VCP_SPECIFICATION_v1.0_COMPLETE.md
│   ├── VCP_SPECIFICATION_v1.1_AMENDMENTS.md
│   └── ...
├── docs/                        # Documentation (shared)
│   ├── VCP_OVERVIEW.md
│   ├── VCP_NEWCOMER_GUIDE.md
│   ├── VCP_IMPLEMENTATION_GUIDE.md
│   ├── identity/                # VCP-Identity layer
│   ├── semantics/               # VCP-Semantics layer
│   ├── adaptation/              # VCP-Adaptation layer
│   ├── context/                 # Context specification
│   ├── uvc/                     # Universal Value Codes
│   ├── content/                 # CSM1 grammar + amendments
│   └── openapi/                 # API specification
├── schemas/                     # JSON schemas (shared)
│   ├── vcp-manifest-v1.schema.json
│   ├── vcp-identity-token.schema.json
│   ├── vcp-semantics-csm1.schema.json
│   └── vcp-adaptation-context.schema.json
├── python/                      # Python SDK
│   ├── pyproject.toml
│   ├── requirements.txt
│   ├── src/vcp/                 # Core library
│   └── tests/                   # Test suite
├── rust/                        # Rust SDK
│   ├── Cargo.toml               # Workspace root
│   ├── vcp-core/                # Core parsing library
│   ├── vcp-wasm/                # WASM bindings
│   └── vcp-cli/                 # CLI tool
├── integrations/                # Example integrations
│   └── safety_stack/
└── LICENSE
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

### CSM-1 Token Format (v1.1)

8-line compact state message:

```
VCP:1.0:user-alice-daily
C:family.safe.guide@1.2.0
P:G:3
G:learn_guitar:beginner:visual
X:🔇:💰low:⚡var
F:time_limited|noise_restricted
S:🔒housing|🔒health
R:🧠focused:4|💭calm:3|🔋low_energy:2
```

Line 8 (R-line) is new in v1.1 — see `docs/content/CSM1_v1.1_AMENDMENT.md`.

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
