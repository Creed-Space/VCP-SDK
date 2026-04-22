# CLAUDE.md - Value Context Protocol

## What This Is

The **Value Context Protocol (VCP)** is a specification for transporting constitutional values to AI systems. It solves the problem that LLMs are "dumb receivers" - they can't verify signatures, resolve references, or check hashes.

**Core insight**: Verify at the orchestration layer, inject complete text to the model.

---

## Architecture (6 Layers — I-T-S-A-M-E)

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 6: VCP-ECONOMIC GOV │  WHO PAYS — governance         │
│  ─────────────────────────────────────────────────────────  │
│  Fiduciary constraints, authorization gaps, transactions    │
├─────────────────────────────────────────────────────────────┤
│  Layer 5: VCP-MESSAGING    │  WHO TALKS — inter-agent       │
│  ─────────────────────────────────────────────────────────  │
│  Message types, escalation severity, delivery semantics     │
├─────────────────────────────────────────────────────────────┤
│  Layer 4: VCP-ADAPTATION   │  WHEN values apply             │
│  ─────────────────────────────────────────────────────────  │
│  Context encoding, state tracking, inter-agent messaging    │
├─────────────────────────────────────────────────────────────┤
│  Layer 3: VCP-SEMANTICS    │  WHAT values mean              │
│  ─────────────────────────────────────────────────────────  │
│  CSM1 grammar, persona composition, trait encoding          │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: VCP-TRANSPORT    │  HOW values travel securely    │
│  ─────────────────────────────────────────────────────────  │
│  Signed bundles, verification, audit logging                │
├─────────────────────────────────────────────────────────────┤
│  Layer 1: VCP-IDENTITY     │  WHO/WHAT is addressed         │
│  ─────────────────────────────────────────────────────────  │
│  UVC naming, namespaces, registry, encoding                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Quick Reference

### Key Concepts

| Concept | Example | Purpose |
|---------|---------|---------|
| **UVC Token** | `family.safe.guide@1.2.0` | Addresses a constitution |
| **CSM1** | `N5+F+E` | Encodes persona (NANNY, adherence 5, Family+Education) |
| **Bundle** | `{manifest, content, signature}` | Signed constitution package |
| **Context** | `⏰🌅\|📍🏡\|👥👶` | Encoded situational context |

### File Navigation

| Need | Go To |
|------|-------|
| **Understand VCP** | `docs/VCP_OVERVIEW.md` → `docs/VCP_NEWCOMER_GUIDE.md` |
| **Full specification** | `specs/VCP_SPECIFICATION_v1.0.md` |
| **Identity/naming** | `docs/identity/VCP_IDENTITY_ENCODING.md` |
| **Semantics/CSM1** | `docs/semantics/VCP_SEMANTICS_CSM1.md` |
| **Adaptation/context** | `docs/adaptation/VCP_ADAPTATION.md` |
| **UVC naming scheme** | `docs/uvc/UVC_NAMING_SPECIFICATION.md` |
| **JSON schemas** | `schemas/vcp-*.schema.json` |
| **Reference impl** | `src/vcp/` |

---

## Repository Structure

```
Value Context Protocol/
├── specs/           # Core specifications (start here for deep understanding)
├── docs/            # Documentation by layer
│   ├── identity/    # VCP-Identity (Layer 1) - 5 docs
│   ├── semantics/   # VCP-Semantics (Layer 3) - 2 docs
│   ├── adaptation/  # VCP-Adaptation (Layer 4) - 1 doc
│   ├── context/     # Context specification
│   ├── uvc/         # Universal Value Codes - 5 docs
│   ├── content/     # CSM1 grammar
│   └── openapi/     # API spec (OpenAPI/Swagger)
├── src/             # Reference implementation (Python)
│   ├── vcp/         # Core library
│   ├── mcp/         # MCP server for Claude Code
│   └── api/         # FastAPI router
├── integrations/    # Example integrations (has external dependencies)
├── schemas/         # JSON Schema validation files
└── tests/           # Test suite
```

---

## Development

### Setup

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
uv sync

# Run tests
pytest tests/
```

### Code Patterns

**Python style:**
- Type hints required on all functions
- Pydantic models for data structures
- Async where appropriate (especially API/MCP)

**Naming conventions:**
- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions/variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`

### Testing

```bash
# All tests
pytest tests/

# Specific layer
pytest tests/vcp/identity/
pytest tests/vcp/semantics/
pytest tests/vcp/adaptation/

# With coverage
pytest --cov=src/vcp tests/
```

---

## Important Notes

### Dependencies

The code in `src/vcp/` is designed to be standalone, but:

1. **`integrations/safety_stack/`** - Has dependencies on Creed Space PDP. These are **reference examples**, not standalone modules.

2. **Some tests** may reference Creed Space fixtures. The `tests/conftest.py` provides basic fixtures for standalone testing.

### What's NOT in this repo

- **Interiora** (AI self-modeling scaffold) - Separate system that uses VCP
- **Bilateral alignment framework** - Philosophy/framework that informs VCP design
- **Constitution content** - VCP transports constitutions, doesn't define them

### Versioning

- Specification version: **v1.0** (with v1.1 amendments)
- Implementation version: Follow semver in `pyproject.toml`

---

## Authors

- Nell Watson
- Claude (Anthropic)

Informed by Junto Mastermind Consultation (9 AI models, 2026-01-10)

---

## Questions?

If something is unclear:
1. Check `docs/VCP_NEWCOMER_GUIDE.md` first
2. Read the relevant layer documentation
3. Look at tests for usage examples
4. Check `specs/VCP_SPECIFICATION_v1.0.md` for authoritative answers
