# VCP Integration Documentation

**Version**: 2.0.0
**Implemented**: 2026-01-11
**Status**: Production-ready (feature-flagged)

---

## Overview

Value-Context Protocol (VCP) is a three-layer protocol for managing AI constitutional alignment:

| Layer | Code | Purpose | Components |
|-------|------|---------|------------|
| **Identity** | VCP/I | Token-based identification | Token, Namespace |
| **Semantics** | VCP/S | Compact constitutional encoding | CSM1, Persona, Scope |
| **Adaptation** | VCP/A | Context-aware behavior | Context, StateTracker, Transitions |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    VCP INTEGRATION ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│  │   VCP/I      │    │   VCP/S      │    │   VCP/A      │          │
│  │   Token      │───▶│   CSM1       │───▶│   Context    │          │
│  │   Namespace  │    │   Persona    │    │   State      │          │
│  └──────────────┘    └──────────────┘    └──────────────┘          │
│         │                   │                   │                   │
│         ▼                   ▼                   ▼                   │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    INTEGRATION LAYER                         │   │
│  ├─────────────┬─────────────┬─────────────┬─────────────┬─────┤   │
│  │ PDP Plugin  │ Export      │ API Router  │ MCP Server  │ GPT │   │
│  │             │ Formatter   │             │             │ Act │   │
│  └─────────────┴─────────────┴─────────────┴─────────────┴─────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Feature Flags

All VCP functionality is controlled by feature flags in `data/feature_flags.json`:

| Flag | Default | Description |
|------|---------|-------------|
| `vcp_identity_enabled` | false | Enable VCP/I token validation |
| `vcp_semantics_enabled` | false | Enable VCP/S CSM1 parsing |
| `vcp_adaptation_enabled` | false | Enable VCP/A context encoding |
| `vcp_identity_shadow` | true | Shadow mode for VCP/I (signals only) |
| `vcp_semantics_shadow` | true | Shadow mode for VCP/S |
| `vcp_adaptation_shadow` | true | Shadow mode for VCP/A |
| `vcp_full_stack_enabled` | false | Enable all layers at once |
| `vcp_strict_mode` | false | Strict validation (reject invalid) |

**Enable for testing:**
```json
{
  "vcp_identity_enabled": true,
  "vcp_semantics_enabled": true,
  "vcp_adaptation_enabled": true
}
```

---

## Components

### 1. PDP Plugin

**File**: `services/safety_stack/plugins/vcp_adaptation_plugin.py`

The VCP Adaptation Plugin integrates VCP context into PDP decisions:

- **Signals**: Emits VCP context signals for other plugins to consume
- **Adaptations**: In active mode, modifies persona preferences based on context

**Context-to-Persona Mappings:**

| Context | Preferred Persona | Policy ID |
|---------|------------------|-----------|
| Children present | Nanny | `vcp_child_safety` |
| Emergency | Sentinel | `vcp_emergency_response` |
| Professional (office) | Ambassador | `vcp_professional_context` |
| Limited agency | Extra caution | `vcp_limited_agency` |

**Usage:**
```python
from services.safety_stack.plugins import VCPAdaptationPlugin

plugin = VCPAdaptationPlugin()
action = plugin.execute(context, findings)
```

### 2. Export Formatter

**File**: `services/export_formatter.py`

Exports now include VCP metadata when enabled:

```python
formatter = ExportFormatter()
response = formatter.format_claude_code_response("nanny", persona)

# Response includes:
{
  "configuration": {...},
  "metadata": {...},
  "vcp": {
    "token": "family.safe.nanny@1.0.0",
    "token_canonical": "family.safe.nanny",
    "uri": "creed://creed.space/family.safe.nanny@1.0.0",
    "csm1": "N5",
    "persona": "NANNY",
    "persona_description": "Child safety specialist",
    "adherence_level": 5,
    "version": "2.0.0"
  }
}
```

### 3. API Router

**File**: `api_routers/vcp.py`
**Prefix**: `/api/vcp`

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/token/validate` | POST | Yes | Validate VCP/I token |
| `/csm1/parse` | POST | Yes | Parse CSM1 code |
| `/context/encode` | POST | Yes | Encode VCP/A context |
| `/personas` | GET | Yes | List CSM1 personas |
| `/dimensions` | GET | Yes | List context dimensions |
| `/status` | GET | No | Get feature flag status |

**Example requests:**

```bash
# Validate token
curl -X POST http://localhost:8000/api/vcp/token/validate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"token": "family.safe.guide@1.2.0"}'

# Parse CSM1
curl -X POST http://localhost:8000/api/vcp/csm1/parse \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"code": "N5+F+E"}'

# Encode context
curl -X POST http://localhost:8000/api/vcp/context/encode \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"time": "morning", "space": "home", "company": ["children"]}'

# Check status (no auth)
curl http://localhost:8000/api/vcp/status
```

### 4. MCP Server

**File**: `services/mcp/vcp_server.py`
**Config**: `.mcp.json`

MCP tools for VCP operations:

| Tool | Description |
|------|-------------|
| `vcp_validate_token` | Validate VCP/I token string |
| `vcp_parse_csm1` | Parse CSM1 constitutional code |
| `vcp_encode_context` | Encode context to VCP/A format |
| `vcp_status` | Get feature flag status |

**Usage with mcp-cli:**
```bash
mcp-cli info vcp/vcp_validate_token
mcp-cli call vcp/vcp_validate_token '{"token": "family.safe.guide"}'
```

### 5. GPT Actions (OpenAPI)

**File**: `docs/openapi/vcp_actions.yaml`

Complete OpenAPI 3.1 spec for ChatGPT Actions integration.

---

## VCP Token Format

**Grammar (ABNF):**
```
token = domain "." approach "." role ["@" version] [":" namespace]
```

**Examples:**
- `family.safe.guide` - Basic token
- `family.safe.guide@1.2.0` - With version
- `company.acme.legal:SEC` - With namespace

**Components:**
- **domain**: Value domain (family, company, general)
- **approach**: Constitutional approach (safe, balanced, strict)
- **role**: Functional role (guide, guardian, advisor)
- **version**: Semantic version (optional)
- **namespace**: Tier namespace (optional)

---

## CSM1 Code Format

**Grammar (ABNF):**
```
code = persona level *("+" scope) [":" namespace] ["@" version]
```

**Personas:**
| Code | Name | Description |
|------|------|-------------|
| N | NANNY | Child safety specialist |
| Z | SENTINEL | Security/privacy guardian |
| G | GODPARENT | Ethical guidance counselor |
| A | AMBASSADOR | Professional conduct advisor |
| M | MUSE | Creativity enabler |
| R | ANCHOR | Factual accuracy enforcer |
| H | HOTROD | Minimal constraints (expert) |
| C | CUSTOM | User-defined persona |

**Scopes:**
| Code | Name | Description |
|------|------|-------------|
| F | FAMILY | Family/parenting |
| W | WORK | Professional/workplace |
| E | EDUCATION | Learning/academic |
| H | HEALTHCARE | Medical/health |
| I | FINANCE | Financial/investment |
| L | LEGAL | Legal/compliance |
| P | PRIVACY | Privacy/data protection |
| S | SAFETY | Physical safety |
| A | ACCESSIBILITY | Accessibility/inclusion |
| V | ENVIRONMENT | Environmental |
| G | GENERAL | General purpose |

**Examples:**
- `N5+F+E` - Nanny, level 5, Family+Education
- `Z3+P` - Sentinel, level 3, Privacy
- `G4:ELEM` - Godparent, level 4, ELEM namespace

---

## Context Dimensions (VCP/A)

9 dimensions for context encoding:

| Dimension | Symbol | Values |
|-----------|--------|--------|
| time | ⏰ | morning, midday, evening, night |
| space | 📍 | home, office, school, hospital, transit |
| company | 👥 | alone, children, colleagues, family, strangers |
| culture | 🌍 | global, american, european, japanese |
| occasion | 🎭 | normal, celebration, mourning, emergency |
| state | 🧠 | happy, anxious, tired, contemplative, frustrated |
| environment | 🌡️ | comfortable, hot, cold, quiet, noisy |
| agency | 🔷 | leader, peer, subordinate, limited |
| constraints | 🔶 | minimal, legal, economic, time |

**Wire format example:**
```
⏰🌅|📍🏡|👥👶👨‍👩‍👧
```

---

## Prometheus Metrics

VCP operations are tracked via Prometheus:

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `vcp_token_validations_total` | Counter | valid, layer | Token validation attempts |
| `vcp_csm1_parses_total` | Counter | valid, persona | CSM1 parse attempts |
| `vcp_context_encodings_total` | Counter | dimensions_set | Context encoding ops |
| `vcp_transitions_total` | Counter | severity | Context transitions |
| `vcp_plugin_latency_seconds` | Histogram | mode | Plugin execution time |
| `vcp_adaptations_total` | Counter | adaptation_type, persona | Adaptations applied |

---

## Testing

**Unit tests:**
```bash
pytest tests/unit/plugins/test_vcp_adaptation_plugin.py -v
pytest tests/unit/api/test_vcp_router.py -v
```

**Integration tests:**
```bash
pytest tests/integration/test_vcp_integration.py -v
```

**All VCP tests:**
```bash
pytest tests/ -k "vcp" -v
```

---

## Files Reference

| File | Purpose |
|------|---------|
| `services/vcp/__init__.py` | VCP core exports |
| `services/vcp/identity/token.py` | VCP/I Token class |
| `services/vcp/semantics/csm1.py` | VCP/S CSM1Code class |
| `services/vcp/adaptation/context.py` | VCP/A ContextEncoder |
| `services/vcp/adaptation/state.py` | VCP/A StateTracker |
| `services/safety_stack/plugins/vcp_adaptation_plugin.py` | PDP plugin |
| `services/export_formatter.py` | Export integration |
| `api_routers/vcp.py` | API router |
| `services/mcp/vcp_server.py` | MCP server |
| `docs/openapi/vcp_actions.yaml` | OpenAPI spec |
| `data/feature_flags.json` | Feature flags |
| `services/prometheus_metrics.py` | Metrics |

---

## Rollout Plan

1. **Shadow Mode** (current): All layers enabled but shadow mode active
   - Signals emitted, no enforcement
   - Monitor metrics and logs

2. **Gradual Activation**: Disable shadow mode per layer
   - Start with VCP/I (token validation)
   - Then VCP/S (CSM1 parsing)
   - Finally VCP/A (context adaptation)

3. **Full Production**: All layers active
   - `vcp_full_stack_enabled: true`
   - Consider `vcp_strict_mode` for validation enforcement

---

## Related Documents

- [VCP Specification](_papers/VCP_SPECIFICATION_v1.0.md)
- [Contprompt](_contprompts/vcp_integration_wiring_2026-01-11.md)
- [Feature Flags](services/feature_flags.py)
