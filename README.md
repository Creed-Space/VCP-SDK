<div align="center">

# VCP SDK — Official SDK for the Value Context Protocol

**Multi-language SDK for VCP v3.1 — parse tokens, encode context, negotiate capabilities, and implement all 6 protocol layers.**

[![CI](https://github.com/Creed-Space/VCP-SDK/actions/workflows/ci.yml/badge.svg)](https://github.com/Creed-Space/VCP-SDK/actions/workflows/ci.yml)
[![Python SDK](https://img.shields.io/badge/python-4.0.0-3776AB?style=flat-square&logo=python&logoColor=white)](./python/)
[![TypeScript SDK](https://img.shields.io/badge/typescript-4.0.0-3178C6?style=flat-square&logo=typescript&logoColor=white)](./webmcp/)
[![Rust SDK](https://img.shields.io/badge/rust-4.0.0-DEA584?style=flat-square&logo=rust&logoColor=white)](./rust/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat-square)](./LICENSE)

[Spec](https://github.com/Creed-Space/VCP-Spec) · [Inspector](https://inspector.valuecontextprotocol.org/) · [Website](https://valuecontextprotocol.org/)

</div>

---

## Overview

The **Value-Context Protocol (VCP)** is an open specification for transporting constitutional values, behavioral rules, and personal context to AI systems. The VCP SDK provides production-ready implementations in Python, TypeScript, and Rust with full cross-language parity.

VCP v3.1 defines six protocol layers spanning identity, transport, semantics, adaptation, messaging, and economic governance. Layers 5 and 6 (VCP/M and VCP/E) enable inter-agent communication and fiduciary constraint management.

---

## Features (v3.1)

### Core Layers (1-4)
- **VCP/I (Identity)** — Token parsing, naming, namespace management
- **VCP/T (Transport)** — Signed bundles with Ed25519 signatures and SHA-256 content hashes
- **VCP/S (Semantics)** — CSM-1 grammar, personas, composition rules
- **VCP/A (Adaptation)** — Context encoding, state tracking, deterministic hooks

### Extension Layers (5-6)
| Layer | Description |
|:---|:---|
| **VCP/M (Messaging)** | Inter-agent message types: context_share, constitution_announce, constraint_propagate, escalation with severity levels |
| **VCP/E (Economic Governance)** | Fiduciary constraints, authorization gaps (capability, accountability, compatibility), transaction governance |

### Protocol
- **Capability Negotiation** — VCP-Hello/VCP-Ack handshake protocol for feature discovery
- **53 conformance test vectors** across 5 categories (personal, relational, consensus, torch, negotiation)
- **Cross-SDK conformance CI** — GitHub Actions testing Python, TypeScript, and Rust in lockstep

---

## SDK Languages

| Language | Directory | Install | Status |
|:---|:---|:---|:---|
| **Python** | [`python/`](./python/) | `pip install vcp-sdk` | Stable |
| **TypeScript** | [`webmcp/`](./webmcp/) | `npm install @creed-space/vcp-sdk` | Stable |
| **Rust** | [`rust/`](./rust/) | `cargo add vcp-core` | Stable |

All SDKs implement the same core protocol and validate against shared conformance test vectors in [`conformance/`](./conformance/).

---

## Quick Start

### Python

```bash
pip install vcp-sdk
```

```python
from vcp.semantics.csm1 import CSM1Token
from vcp.extensions.personal_state import PersonalStateManager
from vcp.extensions.consensus import SchulzeVoting

# Parse a CSM-1 token
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

# Capability negotiation
from vcp.negotiation import VCPHello, VCPAck
hello = VCPHello(extensions=["personal_state", "relational", "consensus", "torch"])
```

### TypeScript

```bash
npm install @creed-space/vcp-sdk
```

```typescript
import { parseCSM1, VCPHello } from '@creed-space/vcp-sdk';

// Parse a CSM-1 token
const token = parseCSM1(rawToken);
console.log(token.constitution); // "family.safe.guide@1.2.0"

// Negotiate capabilities
const hello = new VCPHello({
  extensions: ['personal_state', 'relational', 'consensus', 'torch']
});
```

### Rust

```bash
cargo add vcp-core
```

```rust
use vcp_core::csm1::CSM1Token;
use vcp_core::negotiation::VCPHello;

let token = CSM1Token::parse(raw_token)?;
let identity = token.identity();
let constitution = token.constitution();

// Negotiate capabilities
let hello = VCPHello::new(&["personal_state", "relational", "consensus", "torch"]);
```

---

## Conformance

The `conformance/` directory contains **53 test vectors** across 5 categories:

| Category | Vectors | Description |
|:---|:---|:---|
| Personal State | 12 | Decay curves, lifecycle transitions, signal declaration |
| Relational Context | 11 | Trust levels, standing, self-model, bias detection |
| Constitutional Consensus | 10 | Schulze voting, pairwise matrices, strongest paths |
| Session Handoff (Torch) | 10 | Generation, consumption, lineage verification |
| Capability Negotiation | 10 | VCP-Hello/VCP-Ack handshake, extension discovery |

Run conformance tests:
```bash
# Python
cd python && pytest tests/conformance/

# TypeScript
cd webmcp && npm test -- --grep conformance

# Rust
cd rust && cargo test conformance
```

---

## Architecture

### Six-Layer Protocol Stack (I-T-S-A-M-E)

```
┌─────────────────────────────────────────────────────────────────────┐
│  Layer 6 — VCP/E  ECONOMIC GOVERNANCE                              │
│  WHO PAYS and WHO AUTHORIZES                                        │
│  Fiduciary constraints · Capability gaps · Accountability · Compat  │
├─────────────────────────────────────────────────────────────────────┤
│  Layer 5 — VCP/M  MESSAGING                                        │
│  WHO TALKS                                                          │
│  Context sharing · Constitution announce · Constraint propagate    │
│  Escalation with severity levels · Delivery semantics              │
├─────────────────────────────────────────────────────────────────────┤
│  Layer 4 — VCP/A  ADAPTATION                                       │
│  WHEN and HOW constitutions apply                                   │
│  Context encoding · State tracking · Transition detection           │
├─────────────────────────────────────────────────────────────────────┤
│  Layer 3 — VCP/S  SEMANTICS                                        │
│  WHAT the values mean                                               │
│  CSM-1 grammar · Persona composition · Traits                       │
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

**Mnemonic**: **I-T-S-A-M-E** ("It's-a me!")

---

## Documentation

### Protocol Specification

**[Creed-Space/VCP-Spec](https://github.com/Creed-Space/VCP-Spec)** — Specification, schemas, governance, and protocol docs.

### SDK Guides

| Document | Audience |
|:---|:---|
| [`docs/VCP_IMPLEMENTATION_GUIDE.md`](./docs/VCP_IMPLEMENTATION_GUIDE.md) | SDK implementors |
| [`docs/VCP_INTEGRATION.md`](./docs/VCP_INTEGRATION.md) | Integration guide |
| [`docs/VCP_NEWCOMER_GUIDE.md`](./docs/VCP_NEWCOMER_GUIDE.md) | Getting started |

---

## Contributing

We welcome contributions across all three SDKs, the specification, and documentation. See [CONTRIBUTING.md](./CONTRIBUTING.md) for development setup, coding standards, and pull request guidelines.

For specification changes, see [GOVERNANCE.md](./GOVERNANCE.md) for the VCP Enhancement Proposal (VEP) process.

Please read our [Code of Conduct](./CODE_OF_CONDUCT.md) before participating.

---

## Security

If you discover a security vulnerability, please follow our [Security Policy](./SECURITY.md) for responsible disclosure. Do **not** open a public issue for security concerns.

---

## License

This project is licensed under the [MIT License](./LICENSE).

---

## Authors

Nell Watson, Elena Ajayi, Filip Alimpic, Awwab Mahdi, Blake Wells, Claude (Anthropic)

A **[Creed Space](https://creedspace.com)** project.

---

<div align="center">

*Context that travels with you.*

[Website](https://valuecontextprotocol.org/) · [Spec](https://github.com/Creed-Space/VCP-Spec) · [Inspector](https://inspector.valuecontextprotocol.org/) · [Documentation](./docs/)

</div>
