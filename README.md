<div align="center">

# Value-Context Protocol (VCP) SDK

**The open standard for portable, adaptive, and verifiable AI context.**

[![Specification](https://img.shields.io/badge/spec-v1.1-blue?style=flat-square)](./specs/VCP_SPECIFICATION_v1.0_COMPLETE.md)
[![Python SDK](https://img.shields.io/badge/python-1.0.0-3776AB?style=flat-square&logo=python&logoColor=white)](./python/)
[![Rust SDK](https://img.shields.io/badge/rust-0.1.0-DEA584?style=flat-square&logo=rust&logoColor=white)](./rust/)
[![TypeScript SDK](https://img.shields.io/badge/typescript-0.1.0-3178C6?style=flat-square&logo=typescript&logoColor=white)](./webmcp/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat-square)](./LICENSE)

[Overview](#overview) · [Quick Start](#quick-start) · [Architecture](#architecture) · [SDKs](#sdks) · [Documentation](#documentation) · [Contributing](#contributing)

</div>

---

> **See also:** [ValueContextProtocol.org](https://www.valuecontextprotocol.org) — Interactive demos, documentation, and playground

---

## Overview

The **Value-Context Protocol (VCP)** is an open specification for transporting constitutional values, behavioral rules, and personal context from a repository to an AI system. It solves a fundamental problem: Large Language Models are **dumb receivers** — they accept text input but cannot resolve references, verify signatures, or check hashes.

VCP provides a **signed envelope format** that enables verification at the orchestration layer while delivering complete, self-contained text to the model.

### The Problem

| Current Approach | Limitation |
|:---|:---|
| **Full text injection** | Token-inefficient, no verification, no audit trail |
| **Reference-based** | Requires universal resolution infrastructure that doesn't exist |
| **Platform-specific** | Context locked to one service; users repeat preferences everywhere |

### The VCP Solution

VCP introduces a **Verify-then-Inject** pattern:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Repository    │────▶│  Orchestrator   │────▶│      LLM        │
│  (Signed Bundle)│     │  (Verify + Log) │     │ (Receives Text) │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

1. Constitutions are packaged as **signed bundles** with manifest, content, and cryptographic proofs
2. The **orchestrator** fetches, verifies signatures and hashes, and logs the transaction
3. The **LLM** receives verified full text with a compact header — no resolution needed
4. **Audit systems** can independently verify what values were applied, without LLM cooperation

### Three Core Properties

| Property | Description |
|:---|:---|
| **Portability** | Define context once — every compatible service receives it automatically |
| **Adaptation** | Context profiles shift with situation: work mode at the office, personal mode at home |
| **Liveness** | Real-time personal state (energy, focus, urgency) modulates AI responses moment-to-moment |

> **Design philosophy:** Share *influence* without sharing *information*. VCP shapes AI behavior through contextual flags while protecting the underlying personal data.

---

## Quick Start

### Python (Reference Implementation)

```bash
cd python
pip install -r requirements.txt
```

```python
from vcp.identity import IdentityToken
from vcp.semantics.csm1 import CSM1Token
from vcp.transport import SignedBundle

# Parse a CSM-1 compact token
token = CSM1Token.parse("""
VCP:1.0:user-alice-daily
C:family.safe.guide@1.2.0
P:G:3
G:learn_guitar:beginner:visual
X:🔇:💰low:⚡var
F:time_limited|noise_restricted
S:🔒housing|🔒health
R:🧠focused:4|💭calm:3|🔋low_energy:2
""")

# Verify a signed bundle
bundle = SignedBundle.load("family.safe.guide@1.2.0")
assert bundle.verify()  # Checks signature + hash integrity
```

```bash
pytest tests/  # Run the test suite
```

### Rust (High-Performance / WASM)

```bash
cd rust
cargo build
cargo test
```

```rust
use vcp_core::csm1::CSM1Token;
use vcp_core::identity::IdentityToken;

let token = CSM1Token::parse(raw_token)?;
let identity = token.identity();
let constitution = token.constitution();
```

**Crates:**

| Crate | Purpose |
|:---|:---|
| `vcp-core` | Identity, CSM-1 parsing, context management, transport — `no_std` compatible |
| `vcp-wasm` | Browser bindings via `wasm-bindgen` for client-side VCP |
| `vcp-cli` | Command-line tool: `vcp parse`, `vcp encode`, `vcp verify` |

### TypeScript / WebMCP (Browser)

```bash
cd webmcp
npm install
npm run build
```

```typescript
import { registerVCPTools } from '@vcp/webmcp';

// Register VCP tools with the browser's WebMCP API (Chrome 145+)
registerVCPTools({
  tokenEncoder: myEncoder,
  tokenParser: myParser,
});
// AI agents can now discover: vcp_chat, vcp_build_token,
// vcp_parse_token, vcp_transmission_summary, vcp_list_personas
```

Includes MCP-B polyfill support for non-Chrome browsers.

---

## Architecture

### Four-Layer Protocol Stack

VCP is a four-layer protocol stack — like OSI, but for AI values:

```
┌─────────────────────────────────────────────────────────────────────┐
│  Layer 4 — VCP/A  ADAPTATION                                       │
│  WHEN and HOW constitutions apply                                   │
│  Context encoding · State tracking · Messaging · Deterministic hooks│
├─────────────────────────────────────────────────────────────────────┤
│  Layer 3 — VCP/S  SEMANTICS                                        │
│  WHAT the values mean                                               │
│  CSM-1 grammar · Persona composition · Traits · Personal state      │
├─────────────────────────────────────────────────────────────────────┤
│  Layer 2 — VCP/T  TRANSPORT                                        │
│  HOW values travel securely                                         │
│  Signed bundles · Hash verification · Audit logging                 │
├─────────────────────────────────────────────────────────────────────┤
│  Layer 1 — VCP/I  IDENTITY                                         │
│  WHO and WHAT is being addressed                                    │
│  Naming · Namespaces · Registry · Encoding                          │
└─────────────────────────────────────────────────────────────────────┘
```

### Three-Timescale Context Model

VCP operates across three temporal scales, each with distinct update frequency and enforcement characteristics:

```
┌──────────────────────────────────────────────────────────────┐
│  CONSTITUTIONAL RULES          Rarely change · Hard limits   │
│  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  │
│  SITUATIONAL CONTEXT      Per-session · Role & environment   │
│  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  │
│  PERSONAL STATE         Moment-to-moment · Energy & focus    │
└──────────────────────────────────────────────────────────────┘
```

**Key invariant:** Personal state modulates *expression*, never safety boundaries. A user being stressed may change the AI's tone — it must never weaken constitutional rules.

### Privacy Architecture

| Level | Behavior | Examples |
|:---|:---|:---|
| **Public** | Always shared | Goals, experience level, learning style |
| **Consent** | Shared with explicit permission | Location context, health indicators |
| **Private** | Never transmitted; influences AI locally | Raw emotional state, sensitive constraints |

---

## Key Concepts

### Universal Value Codes (UVC)

A hierarchical naming scheme for constitutions and values:

```
family.safe.guide@1.2.0
│      │    │     └── Semantic version
│      │    └──────── Role / approach
│      └───────────── Domain
└──────────────────── Namespace
```

### CSM-1 Token Format (v1.1)

Compact State Message — an 8-line token encoding complete user context in approximately 200 bytes:

```
VCP:1.0:user-alice-daily          ← Protocol version + session ID
C:family.safe.guide@1.2.0        ← Constitution reference
P:G:3                             ← Persona + generation level
G:learn_guitar:beginner:visual    ← Goal + skill level + learning style
X:🔇:💰low:⚡var                  ← Environmental constraints
F:time_limited|noise_restricted   ← Active flags
S:🔒housing|🔒health              ← Shielded (private) topics
R:🧠focused:4|💭calm:3|🔋low:2   ← Real-time personal state (v1.1)
```

Line 8 (R-line) is new in v1.1 — see [`docs/content/CSM1_v1.1_AMENDMENT.md`](./docs/content/CSM1_v1.1_AMENDMENT.md).

### Signed Bundles

Constitutions are packaged as cryptographically signed bundles:

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

The orchestrator verifies the signature and hash before injecting the content into the LLM's context window.

### Personas

Six built-in personas define distinct interaction styles:

| Persona | Style | Use Case |
|:---|:---|:---|
| **Muse** | Creative, exploratory | Brainstorming, ideation |
| **Sentinel** | Cautious, protective | Safety-critical contexts |
| **Godparent** | Nurturing, patient | Learning, mentorship |
| **Ambassador** | Professional, diplomatic | Business, formal communication |
| **Anchor** | Grounding, stabilizing | Emotional support, crisis |
| **Nanny** | Structured, rule-following | Children, constrained environments |

### Deterministic Hooks

VCP 3.1 introduces rules at three enforcement tiers:

| Tier | Behavior | Override |
|:---|:---|:---|
| **Constitutional** | Hard rules, always enforced | Cannot be overridden |
| **Situational** | Active in specific contexts | Context-dependent activation |
| **Personal** | Advisory user preferences | Soft influence on behavior |

Hooks provide **deterministic reliability** where probabilistic model behavior falls short.

---

## SDKs

| Language | Directory | Version | Status | Targets |
|:---|:---|:---|:---|:---|
| **Python** | [`python/`](./python/) | 1.0.0 | Stable | Reference implementation, LLM integration, server-side |
| **Rust** | [`rust/`](./rust/) | 0.1.0 | Beta | High-performance parsing, WASM/browser, embedded, CLI |
| **TypeScript** | [`webmcp/`](./webmcp/) | 0.1.0 | Beta | Browser-side tool registration via `navigator.modelContext` |

All SDKs implement the same core protocol and pass shared conformance tests against the JSON schemas in [`schemas/`](./schemas/).

---

## Documentation

### Specifications

| Document | Description |
|:---|:---|
| [`specs/VCP_SPECIFICATION_v1.0_COMPLETE.md`](./specs/VCP_SPECIFICATION_v1.0_COMPLETE.md) | Full protocol specification |
| [`specs/VCP_SPECIFICATION_v1.1_AMENDMENTS.md`](./specs/VCP_SPECIFICATION_v1.1_AMENDMENTS.md) | v1.1 amendments (R-line, personal state) |
| [`specs/value_context_protocols_paper_v1.md`](./specs/value_context_protocols_paper_v1.md) | Academic paper |

### Guides

| Document | Audience |
|:---|:---|
| [`docs/VCP_NEWCOMER_GUIDE.md`](./docs/VCP_NEWCOMER_GUIDE.md) | New to VCP — start here |
| [`docs/VCP_OVERVIEW.md`](./docs/VCP_OVERVIEW.md) | Technical overview |
| [`docs/VCP_IMPLEMENTATION_GUIDE.md`](./docs/VCP_IMPLEMENTATION_GUIDE.md) | SDK implementors |

### Layer Documentation

| Layer | Documentation |
|:---|:---|
| VCP/I — Identity | [`docs/identity/`](./docs/identity/) |
| VCP/T — Transport | [`specs/VCP_SPECIFICATION_v1.0.md`](./specs/VCP_SPECIFICATION_v1.0.md) §6 |
| VCP/S — Semantics | [`docs/semantics/`](./docs/semantics/) |
| VCP/A — Adaptation | [`docs/adaptation/`](./docs/adaptation/) |

### Schemas

| Schema | Validates |
|:---|:---|
| [`schemas/vcp-manifest-v1.schema.json`](./schemas/vcp-manifest-v1.schema.json) | Bundle manifests |
| [`schemas/vcp-identity-token.schema.json`](./schemas/vcp-identity-token.schema.json) | Identity tokens |
| [`schemas/vcp-semantics-csm1.schema.json`](./schemas/vcp-semantics-csm1.schema.json) | CSM-1 tokens |
| [`schemas/vcp-adaptation-context.schema.json`](./schemas/vcp-adaptation-context.schema.json) | Adaptation context |

### API Reference

OpenAPI specification: [`docs/openapi/`](./docs/openapi/)

---

## Design Principles

1. **Verify-then-Inject** — Verification happens at the orchestration layer, not in the LLM
2. **Complete Delivery** — LLMs receive full text, not references they can't resolve
3. **Audit Trail** — Every application of values is logged and independently verifiable
4. **Implementation Agnostic** — Works with any constitutional AI framework or model provider
5. **Supply-Chain Security** — Draws on patterns from package signing (npm, PyPI, cargo) and Subresource Integrity
6. **Privacy by Design** — Share influence without sharing information; users control disclosure at three granularity levels
7. **Bilateral Symmetry** — Users declare personal state; AI maintains its own self-model. Mutual understanding without privileged access.

---

## Integrations

VCP is designed to work with existing infrastructure:

| Integration | Status | Description |
|:---|:---|:---|
| **Model Context Protocol (MCP)** | Native | VCP tools register as MCP-compatible resources |
| **WebMCP (Chrome 145+)** | Stable | Browser-native AI tool discovery via `navigator.modelContext` |
| **REST API** | Stable | Standard HTTP endpoints for token exchange |
| **GPT Actions** | Compatible | Export VCP artifacts as OpenAI-compatible actions |

---

## Demo

Explore VCP interactively at **[ValueContextProtocol.org](https://www.valuecontextprotocol.org)** — build tokens, test personas, and see the protocol in action.

The demo source lives in [`vcp-demo/`](./vcp-demo/).

---

## Repository Structure

```
VCP-SDK/
├── specs/                 # Core protocol specifications
│   ├── VCP_SPECIFICATION_v1.0.md
│   ├── VCP_SPECIFICATION_v1.0_COMPLETE.md
│   ├── VCP_SPECIFICATION_v1.1_AMENDMENTS.md
│   └── value_context_protocols_paper_v1.md
├── docs/                  # Documentation and guides
│   ├── VCP_OVERVIEW.md
│   ├── VCP_NEWCOMER_GUIDE.md
│   ├── VCP_IMPLEMENTATION_GUIDE.md
│   ├── identity/          # VCP/I layer docs
│   ├── semantics/         # VCP/S layer docs
│   ├── adaptation/        # VCP/A layer docs
│   ├── context/           # Context specification
│   ├── uvc/               # Universal Value Codes
│   ├── content/           # CSM-1 grammar + amendments
│   └── openapi/           # API specification
├── schemas/               # JSON Schema definitions
├── python/                # Python SDK (stable)
│   ├── src/vcp/           # Core library
│   └── tests/             # Test suite
├── rust/                  # Rust SDK (beta)
│   ├── vcp-core/          # Core parsing library
│   ├── vcp-wasm/          # WASM bindings
│   └── vcp-cli/           # CLI tool
├── webmcp/                # TypeScript/WebMCP SDK (beta)
├── integrations/          # Example integrations
├── vcp-demo/              # Interactive demo site
├── website/               # Project website
├── CONTRIBUTING.md        # Contribution guidelines
├── CODE_OF_CONDUCT.md     # Community standards
├── SECURITY.md            # Vulnerability disclosure
└── LICENSE                # MIT License
```

---

## Related Work

VCP draws on established patterns from:

- **Software Supply Chain** — Package signing (npm, PyPI, cargo)
- **Web Integrity** — Subresource Integrity (SRI), Content Security Policy
- **Distributed Systems** — Content-addressed storage (IPFS, git)
- **Identity Systems** — Decentralized Identifiers (DIDs), URNs
- **Constitutional AI** — Anthropic's Constitutional AI, OpenAI system prompts

---

## Contributing

We welcome contributions. See [CONTRIBUTING.md](./CONTRIBUTING.md) for development setup, coding standards, and pull request guidelines.

Please read our [Code of Conduct](./CODE_OF_CONDUCT.md) before participating.

---

## Security

If you discover a security vulnerability, please follow our [Security Policy](./SECURITY.md) for responsible disclosure. Do **not** open a public issue for security concerns.

---

## License

This project is licensed under the [MIT License](./LICENSE).

---

## Authors

- **Nell Watson** — Creator & Lead
- **Elena Ajayi**
- **Filip Alimpic**
- **Awwab Mahdi**
- **Blake Wells**
- **Claude** (Anthropic)

Built by **[Creed Space](https://creedspace.com)** — the platform for constitutional AI governance.

Informed by a Junto Mastermind Consultation of 9 AI models (2026-01-10).

---

<div align="center">

*Context that travels with you.*

[Website](https://www.valuecontextprotocol.org) · [Documentation](./docs/) · [Specification](./specs/) · [Playground](https://www.valuecontextprotocol.org/playground)

</div>
