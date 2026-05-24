# VCP SDK Architecture

<!-- wiki:type = system -->
<!-- wiki:scope = vcp-sdk -->
<!-- wiki:created = 2026-05-23 -->
<!-- wiki:updated = 2026-05-23 -->
<!-- wiki:status = active -->

## Summary

The VCP SDK is the reference implementation of the VCP protocol. It is structured as three language implementations (Python, Rust, TypeScript) plus conformance tests and integration examples. The Python SDK is the reference; Rust targets high-performance and WASM; TypeScript targets browser-side. (VCP-SDK/README.md header, VCP-Spec/README.md "SDKs" table)

## Repository Layout

```
VCP-SDK/
├── python/          # Reference implementation (Python 3.x, Pydantic, async)
│   ├── src/
│   │   ├── vcp/     # Core library modules
│   │   ├── api/     # FastAPI router
│   │   └── mcp/     # MCP server for Claude Code
│   └── tests/
├── rust/            # High-performance / WASM implementation
├── conformance/     # Cross-language conformance tests
├── examples/        # Runnable usage examples
├── integrations/    # External integration examples (has PDP dependencies)
├── schemas/         # JSON Schema validation files
├── specs/           # Spec subset (or symlinks)
├── webmcp/          # Web-facing MCP bindings
└── website/         # SDK website content
```

(VCP-SDK/CLAUDE.md, "Repository Structure"; VCP-SDK root directory listing)

## Python Core Library (python/src/vcp/)

Key modules in `python/src/vcp/` (directory listing):

| Module | Purpose |
|--------|---------|
| `types.py` | Core type definitions |
| `bundle.py` | Bundle creation and parsing |
| `canonicalize.py` | Canonical serialization for signing |
| `trust.py` | Trust anchor and chain verification |
| `manifest.py` | Bundle manifest handling |
| `orchestrator.py` | Orchestration layer (verify then inject) |
| `enforcement.py` | Policy enforcement |
| `negotiation.py` | Capability negotiation |
| `injection.py` | Injection scanning |
| `privacy.py` | Context opacity and privacy |
| `revocation.py` | Revocation infrastructure |
| `audit.py` | Tamper-evident audit chain |
| `messaging.py` | VCP/M inter-agent messaging |
| `metrics.py` | Metrics and telemetry |
| `skill_security.py` | Skill-level security checks |
| `identity/` | VCP/I layer modules |
| `semantics/` | VCP/S layer modules |
| `adaptation/` | VCP/A layer modules |
| `extensions/` | VCP-X-* extension modules |
| `hooks/` | Lifecycle hooks |

## Code Conventions

(VCP-SDK/CLAUDE.md, "Code Patterns")
- Type hints required on all Python functions
- Pydantic models for data structures
- Async preferred for API/MCP entry points
- Files: `snake_case.py`; Classes: `PascalCase`; Constants: `UPPER_SNAKE_CASE`

## Important Constraints

`integrations/` has dependencies on Creed Space PDP — these are reference examples, not standalone modules. (VCP-SDK/CLAUDE.md, "Important Notes")

What is NOT in this repo:
- Interiora (separate system that uses VCP)
- Bilateral alignment framework (informs design, not implemented here)
- Constitution content (VCP transports constitutions, does not define them)

## Entry Points

```bash
# Install Python SDK
pip install creed-sdk

# Run tests
pytest tests/                     # all
pytest tests/vcp/identity/        # by layer
pytest --cov=src/vcp tests/       # with coverage
```

(VCP-SDK/CLAUDE.md, "Testing")

## Provenance

- Sources consulted: VCP-SDK/CLAUDE.md, VCP-SDK root listing, python/src/vcp/ listing
- Last verified against sources: 2026-05-23

## See Also

- [[vcp-spec:systems/itsame-architecture]] — the spec this SDK implements
- [[vcp-sdk:flows/bundle-sign-verify]] — bundle signing and verification flow
- [[shared:vcp]] — VCP cross-project concept
