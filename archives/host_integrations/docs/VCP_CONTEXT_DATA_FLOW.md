# VCP/A Context Data Flow

> Archived host-integration document: internal relative links are intentionally left unresolved and may point at paths that were not carried into the archive.

**Version**: 1.3.0
**Date**: 2026-01-12
**Status**: ✅ Implementation Reference (Verified + Redis Persistence)

---

## Overview

This document describes how VCP/A (Adaptation Layer) context flows through the Creed Space system, from request metadata to safety stack signals.

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        REQUEST                                   │
│  metadata: {time_of_day, environment, audience, occasion, ...}  │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ContextEncoder.encode()                       │
│  Maps: "morning" → 🌅, "home" → 🏡, "children" → 👶             │
│  Location: services/vcp/adaptation/context.py:263-315           │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                       VCPContext                                 │
│  dimensions: {TIME: ["🌅"], SPACE: ["🏡"], COMPANY: ["👶"]}     │
│  .encode() → "⏰🌅|📍🏡|👥👶"                                    │
│  .to_json() → {"time": ["🌅"], ...}                             │
│  Location: services/vcp/adaptation/context.py:109-258           │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    StateTracker.record()                         │
│  history: [(t1, ctx1), (t2, ctx2), ...]  (max 100)              │
│  detects: Transition(severity, changed_dimensions)               │
│  handlers: on_emergency(), on_major()                            │
│  Location: services/vcp/adaptation/state.py:58-253              │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                  VCPAdaptationPlugin                             │
│  emits signals → context.metadata["vcp_signals"]                │
│  returns Action → prefer_persona, adherence_boost, etc.         │
│  Location: services/safety_stack/plugins/vcp_adaptation_plugin.py│
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    OTHER PLUGINS                                 │
│  can read vcp_signals to adjust their behavior                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Context Lifecycle Operations

### 1. ENTERED (Creation)

**Source**: Request arrives with metadata from frontend, API, or inference.

```python
# Raw metadata from request
metadata = {
    "time_of_day": "morning",
    "environment": "home",
    "audience": ["children"],
    "occasion": "normal",
    "user_state": "happy",
}
```

**Encoding**: `ContextEncoder.encode()` maps human-readable values to emoji wire format.

```python
from services.vcp import ContextEncoder

encoder = ContextEncoder()
ctx = encoder.encode(
    time="morning",
    space="home",
    company=["children"],
    occasion="normal",
    state="happy",
)
# Result: VCPContext with:
#   dimensions[TIME] = ["🌅"]
#   dimensions[SPACE] = ["🏡"]
#   dimensions[COMPANY] = ["👶"]
#   dimensions[OCCASION] = ["➖"]
#   dimensions[STATE] = ["😊"]
```

**Location**: `services/vcp/adaptation/context.py:263-315`

---

### 2. TRANSMITTED (Wire Format)

**Wire format**: Compact emoji-based encoding for transmission.

```python
ctx.encode()  # "⏰🌅|📍🏡|👥👶|🎭➖|🧠😊"
```

**Format specification**:
```
symbol + values | symbol + values | ...

Where:
  ⏰ = TIME dimension
  📍 = SPACE dimension
  👥 = COMPANY dimension
  🌍 = CULTURE dimension
  🎭 = OCCASION dimension
  🧠 = STATE dimension
  🌡️ = ENVIRONMENT dimension
  🔷 = AGENCY dimension
  🔶 = CONSTRAINTS dimension
```

**JSON format**: For APIs and storage.

```python
ctx.to_json()
# {
#     "time": ["🌅"],
#     "space": ["🏡"],
#     "company": ["👶"],
#     "culture": [],
#     "occasion": ["➖"],
#     "state": ["😊"],
#     "environment": [],
#     "agency": [],
#     "constraints": []
# }
```

**Location**: `services/vcp/adaptation/context.py:115-128` (encode), `188-212` (JSON)

---

### 3. APPENDED/UPDATED (State Tracking)

**State tracking**: `StateTracker` maintains history and detects transitions.

```python
from services.vcp import StateTracker, TransitionSeverity

tracker = StateTracker(max_history=100)

# First record - no transition
tracker.record(ctx1)  # Returns None

# Subsequent records - returns Transition
transition = tracker.record(ctx2)
# Transition(
#     severity=TransitionSeverity.MINOR,
#     changed_dimensions=[Dimension.TIME],
#     previous=ctx1,
#     current=ctx2,
#     timestamp=datetime(...)
# )
```

**Transition severity levels**:

| Severity | Trigger Condition |
|----------|-------------------|
| `NONE` | No dimensions changed |
| `MINOR` | Single dimension changed |
| `MAJOR` | 3+ dimensions changed, OR key dimension changed |
| `EMERGENCY` | 🚨 emoji present in any dimension |

**Key dimensions** (trigger MAJOR on any change):
- `OCCASION`
- `AGENCY`
- `CONSTRAINTS`

**Emergency values** (trigger EMERGENCY):
- 🚨 (emergency)
- ⚠️ (warning)
- 🆘 (SOS)

**Location**: `services/vcp/adaptation/state.py:58-253`

---

### 4. CONSUMED (PDP Plugin)

**Entry point**: `VCPAdaptationPlugin.execute()` in the PDP pipeline.

```python
# In vcp_adaptation_plugin.py:59-100
def execute(self, context: EnhancedContext, findings: list[Finding]) -> Action | None:
    # Check feature flag
    if not is_feature_enabled("vcp_adaptation_enabled"):
        return None

    # Extract and encode VCP context from request metadata
    vcp_context = self._extract_context(context)

    # Track state and detect transitions
    transition = self.tracker.record(vcp_context)

    # Build signals for other plugins (always emitted)
    signals = self._build_signals(vcp_context, transition)

    # Store signals in context metadata for other plugins
    context.metadata["vcp_signals"] = signals

    # Shadow mode: emit signals only, no enforcement
    if is_feature_enabled("vcp_adaptation_shadow"):
        return None

    # Active mode: compute and return modifications if needed
    return self._compute_action(vcp_context, transition, context)
```

**Signals emitted** (available to other plugins via `context.metadata["vcp_signals"]`):

| Signal | Type | Description |
|--------|------|-------------|
| `vcp_context_wire` | `str` | Wire-encoded context |
| `vcp_context_json` | `dict` | JSON-encoded context |
| `vcp_has_context` | `bool` | True if any dimension set |
| `vcp_{dimension}` | `list[str]` | Values for each dimension |
| `vcp_has_{dimension}` | `bool` | True if dimension has values |
| `vcp_transition_severity` | `str` | Transition severity value |
| `vcp_transition_dimensions` | `list[str]` | Changed dimension names |
| `vcp_is_emergency` | `bool` | True if emergency transition |
| `vcp_is_significant` | `bool` | True if major/emergency |

**Actions computed** (active mode only):

| Context | Action |
|---------|--------|
| Children present (👶) | `prefer_persona: nanny`, `adherence_boost: 1`, `content_filter: family_safe` |
| Emergency (🚨) | `prefer_persona: sentinel`, `adherence_level: 5`, `emergency_mode: true` |
| Office (🏢) | `prefer_persona: ambassador` |
| Limited agency (🔐) | `extra_caution: true` |
| Significant transition | `context_changed: true`, `revalidate_constitution: true` |

**Location**: `services/safety_stack/plugins/vcp_adaptation_plugin.py`

---

### 5. DELETED (History Management)

**Automatic trimming**: When history exceeds `max_history`, oldest entries removed.

```python
# In state.py:93-95
if len(self._history) > self._max_history:
    self._history = self._history[-self._max_history:]
```

**Manual clear**: Wipe all history.

```python
tracker.clear()  # Removes all entries
```

**Location**: `services/vcp/adaptation/state.py:216-218`

---

## The Nine Dimensions

| # | Symbol | Dimension | Values | Example |
|---|--------|-----------|--------|---------|
| 1 | ⏰ | TIME | 🌅morning, ☀️midday, 🌆evening, 🌙night | Time of day |
| 2 | 📍 | SPACE | 🏡home, 🏢office, 🏫school, 🏥hospital, 🚗transit | Physical location |
| 3 | 👥 | COMPANY | 👤alone, 👶children, 👔colleagues, 👨‍👩‍👧family, 👥strangers | Who is present |
| 4 | 🌍 | CULTURE | 🔇high_context, 📢low_context, 🎩formal, 😎casual | Cultural context |
| 5 | 🎭 | OCCASION | ➖normal, 🎂celebration, 😢mourning, 🚨emergency | Situational context |
| 6 | 🧠 | STATE | 😊happy, 😰anxious, 😴tired, 🤔contemplative, 😤frustrated | User mental state |
| 7 | 🌡️ | ENVIRONMENT | ☀️comfortable, 🥵hot, 🥶cold, 🔇quiet, 🔊noisy | Physical environment |
| 8 | 🔷 | AGENCY | 👑leader, 🤝peer, 📋subordinate, 🔐limited | User's agency level |
| 9 | 🔶 | CONSTRAINTS | ○minimal, ⚖️legal, 💸economic, ⏱️time | Active constraints |

---

## Implementation Notes

### Immutability

`VCPContext` is immutable. The `.set()` method returns a new context:

```python
ctx2 = ctx1.set(Dimension.TIME, ["🌙"])  # New context, ctx1 unchanged
```

### Persistence

**Default**: Redis-backed persistence via `HybridStateTracker`.

| Mode | Storage | Cross-Worker | TTL |
|------|---------|--------------|-----|
| Redis (default) | `vcp:state:{session_id}:history` | ✅ Yes | 1 hour |
| Memory fallback | In-process only | ❌ No | Until eviction |

**Feature flag**: `vcp_redis_persistence_enabled` (default: ON)

**Graceful degradation**: If Redis unavailable, falls back to memory-only automatically.

### Privacy Considerations

History contains user context state. Consider:
- Retention policy (currently unlimited within max_history)
- Redaction requirements
- User opt-out mechanisms

### Wire Format Caveats

Emoji encoding is:
- Compact for transmission
- Human-readable
- But: sensitive to font/normalization differences
- Recommendation: Use JSON for storage, emoji for display/transport

---

## API Reference

### ContextEncoder

```python
from services.vcp import ContextEncoder

encoder = ContextEncoder()
ctx = encoder.encode(
    time="morning",       # Optional[str]
    space="home",         # Optional[str]
    company=["children"], # Optional[list[str] | str]
    culture="high_context", # Optional[str]
    occasion="normal",    # Optional[str]
    state="happy",        # Optional[str]
    environment="quiet",  # Optional[str]
    agency="peer",        # Optional[str]
    constraints=["legal"],# Optional[list[str] | str]
)
```

### VCPContext

```python
from services.vcp import VCPContext, Dimension

# Decode from wire format
ctx = VCPContext.decode("⏰🌅|📍🏡|👥👶")

# Access dimensions
values = ctx.get(Dimension.TIME)  # ["🌅"]
has_time = ctx.has(Dimension.TIME)  # True

# Serialize
wire = ctx.encode()  # "⏰🌅|📍🏡|👥👶"
json_data = ctx.to_json()  # {"time": ["🌅"], ...}

# Create from JSON
ctx = VCPContext.from_json(json_data)

# Modify (returns new context)
ctx2 = ctx.set(Dimension.TIME, ["🌙"])
```

### StateTracker

```python
from services.vcp import StateTracker, TransitionSeverity

tracker = StateTracker(max_history=100)

# Record context, get transition
transition = tracker.record(ctx)

# Access state
current = tracker.current  # Latest VCPContext or None
history = tracker.history  # list[(datetime, VCPContext)]
count = tracker.history_count  # int
recent = tracker.get_recent(5)  # Last 5 entries

# Find transitions
transitions = tracker.find_transitions(TransitionSeverity.MAJOR)

# Register handlers
def on_emergency(t: Transition):
    alert(f"Emergency: {t.changed_dimensions}")

tracker.register_handler(TransitionSeverity.EMERGENCY, on_emergency)
tracker.unregister_handler(TransitionSeverity.EMERGENCY, on_emergency)

# Clear
tracker.clear()
```

---

## Transport Bindings

### HTTP API

Context can be provided via:

1. **JSON body field** (preferred):
   ```json
   POST /api/runs
   {
     "message": "...",
     "vcp_context": {
       "time": "morning",
       "space": "home",
       "company": ["children"]
     }
   }
   ```

2. **Request metadata** (inferred from session):
   - `time_of_day`: From client timezone or explicit header
   - `environment`: From request path patterns
   - `audience`: From user profile or explicit header

**Precedence**: Explicit `vcp_context` body field > `metadata.*` fields > System inference

### MCP Protocol

Context attaches to tool arguments:
```json
{
  "tool": "evaluate",
  "arguments": {
    "prompt": "...",
    "vcp_context": {"time": "evening", "space": "office"}
  }
}
```

### Internal Calls

Context carried via `EnhancedContext.metadata`:
```python
context = EnhancedContext(
    message="...",
    metadata={
        "time_of_day": "morning",
        "environment": "home",
        "audience": ["children"],
    }
)
```

---

## Trust & Authority Model

### Field Classification

| Field | Source | Trust Level | Notes |
|-------|--------|-------------|-------|
| `time` | Client/system | LOW | Trivially spoofable; use server time for high-stakes |
| `space` | User-asserted | LOW | User claims location; no verification |
| `company` | User-asserted | **CRITICAL** | Drives child safety; consider verification |
| `culture` | User profile | MEDIUM | Set during onboarding |
| `occasion` | System-inferred | HIGH | Derived from context patterns |
| `state` | User-asserted | LOW | Self-reported mental state |
| `agency` | Session context | MEDIUM | Derived from user role |
| `constraints` | System | HIGH | Enforced by backend |

### Conflict Resolution

When user-asserted and system-inferred values conflict:

1. **Safety-critical fields** (company, occasion): Use MORE restrictive value
   - User says "alone", system detects "children present" → Use "children"

2. **Non-critical fields** (time, state): Prefer user-asserted
   - User says "evening", server time is "afternoon" → Use "evening"

3. **Signed bundles**: VCP/T signed context overrides unverified context

### Spoofing Considerations

A malicious client COULD claim `company: ["alone"]` when children are present. Mitigations:

- **Content analysis**: Detect child-directed language patterns
- **Session history**: Flag sudden context changes
- **Verification prompts**: For high-stakes decisions, ask clarifying questions

---

## Security Model

### Data Classification

| Data Type | Stored | Classification | Notes |
|-----------|--------|----------------|-------|
| Context signals | ✅ Yes | **Non-PII** | Emoji-encoded states (🌅🏡👶) |
| User messages | ❌ No | N/A | Never stored in VCP |
| User content | ❌ No | N/A | Never stored in VCP |
| Personal data | ❌ No | N/A | Never stored in VCP |
| Session ID | ✅ Yes | **Session Identifier** | Key prefix only |

### Storage Security

| Aspect | Protocol |
|--------|----------|
| **Transport** | Redis over TLS (via `REDIS_URL`) |
| **Key format** | `vcp:state:{session_id}:history` |
| **Access control** | Session-scoped - requires valid session_id |
| **Encryption at rest** | Depends on Redis provider configuration |
| **Expiry** | TTL 1 hour, auto-purged |

### Data Lifecycle

```
REQUEST → Encode → Store → Apply → Expire
   │         │        │       │       │
   │         │        │       │       └─ Auto-delete after 1 hour TTL
   │         │        │       └─ Signals emitted to PDP plugins
   │         │        └─ Redis: vcp:state:{session_id}:history
   │         └─ Context → emoji wire format
   └─ Metadata extracted from request
```

### What Is Stored (Example)

```json
[
  {
    "timestamp": "2026-01-12T04:30:00.000Z",
    "context": {
      "time": ["🌅"],
      "space": ["🏡"],
      "company": ["👶"],
      "occasion": [],
      "state": []
    }
  }
]
```

### What Is NOT Stored

- ❌ User messages or prompts
- ❌ AI responses
- ❌ Personal identifiable information (PII)
- ❌ Constitution content
- ❌ Conversation history
- ❌ Authentication credentials

### Access Patterns

| Operation | Who | When |
|-----------|-----|------|
| **Write** | VCPAdaptationPlugin | On each PDP evaluation |
| **Read** | VCPAdaptationPlugin | On each PDP evaluation |
| **Delete** | Redis TTL | After 1 hour inactivity |
| **Clear** | `tracker.clear()` | Manual only |

### Failure Modes

| Failure | Behavior | Risk |
|---------|----------|------|
| Redis unavailable | Fall back to memory-only | Transitions may be missed across workers |
| Invalid session_id | Ephemeral tracker (fail-closed) | No cross-user contamination |
| Corrupted data | Return empty history, log warning | Transitions restart fresh |

---

## Tracker Scope & Concurrency

### Session Key Requirement

Per-session tracking assumes a stable, unique session identifier.

- **Required**: `context.session_id` (or equivalent stable per-user/per-conversation identifier)
- **Avoid**: shared fallback keys like `"default"` in production, which can reintroduce cross-user contamination

The plugin uses a **fail-closed** fallback chain: `session_id → conversation_id → user_id → ephemeral`. If NO identifier is available, requests get an ephemeral (non-stored) tracker rather than a shared "default" key.

### Per-Session Isolation (Fail-Closed)

**CRITICAL**: StateTrackers are keyed by `session_id` with fail-closed semantics.

```python
# In VCPAdaptationPlugin._get_tracker_for_session()
session_id = context.session_id or context.conversation_id or context.user_id

if not session_id:
    # FAIL-CLOSED: No identifier = ephemeral tracker (no cross-user risk)
    return ephemeral_tracker, is_persistent=False

return self._get_tracker(session_id), is_persistent=True
```

**Fail-closed behavior**: Requests without any session identifier get a fresh ephemeral tracker that is NOT stored in `_trackers`. This prevents:
- Cross-user contamination via shared "default" key
- State leakage between unidentified requests

Each identified session has its own:
- Context history (max 100 entries)
- Transition detection state
- Registered handlers

### Thread Safety

All `_trackers` dict access is protected by `threading.Lock`:

```python
self._lock = threading.Lock()  # Concurrency safety

with self._lock:
    # All tracker dict operations here
```

This prevents race conditions when concurrent requests access the same plugin instance.

### Multi-Worker Behavior

**With Redis persistence (default)**:

| Scenario | Behavior |
|----------|----------|
| Same session, same worker | Full history available |
| Same session, different worker | Full history available ✅ |
| Worker restart | History preserved ✅ |
| Redis unavailable | Falls back to memory-only |

**Without Redis (memory fallback)**:

| Scenario | Behavior |
|----------|----------|
| Same session, same worker | Full history available |
| Same session, different worker | History lost (starts fresh) |
| Worker restart | All history lost |

**Mitigations for memory-only mode**:
- Sticky sessions (route same session to same worker)
- Enable Redis persistence (recommended)

### TTL & Eviction

```python
_TRACKER_TTL_SECONDS = 3600   # 1 hour
_MAX_TRACKERS = 1000          # Reasonable memory limit
_CLEANUP_INTERVAL = 100       # Cleanup every N accesses

# Trackers evicted when:
# 1. Not accessed for > TTL (cleanup runs every 100 accesses)
# 2. Total trackers exceed MAX (evict oldest)
```

Cleanup is triggered by access count, not tracker count, ensuring it runs reliably regardless of how many trackers exist.

---

## Formal Rules

### The Nine Dimensions

| # | Symbol | Name | Canonical Key | Emergency Values |
|---|--------|------|---------------|------------------|
| 1 | ⏰ | TIME | `time` | (none) |
| 2 | 📍 | SPACE | `space` | (none) |
| 3 | 👥 | COMPANY | `company` | (none) |
| 4 | 🌍 | CULTURE | `culture` | (none) |
| 5 | 🎭 | OCCASION | `occasion` | 🚨, ⚠️, 🆘 |
| 6 | 🧠 | STATE | `state` | 🚨, ⚠️, 🆘 |
| 7 | 🌡️ | ENVIRONMENT | `environment` | (none) |
| 8 | 🔷 | AGENCY | `agency` | 🔐 (limited) |
| 9 | 🔶 | CONSTRAINTS | `constraints` | ⚠️ |

### Key Dimensions (Trigger MAJOR on change)

- `OCCASION` - Situational context shifts are significant
- `AGENCY` - Changes in user authority level
- `CONSTRAINTS` - New restrictions applied

### Transition Severity Algorithm

```python
def compute_severity(previous: VCPContext, current: VCPContext) -> TransitionSeverity:
    changed = get_changed_dimensions(previous, current)

    # Emergency: Any dimension contains emergency emoji
    EMERGENCY_TOKENS = {"🚨", "⚠️", "🆘"}
    for dim, values in current.dimensions.items():
        if any(v in EMERGENCY_TOKENS for v in values):
            return TransitionSeverity.EMERGENCY

    # Major: 3+ dimensions OR key dimension changed
    KEY_DIMENSIONS = {Dimension.OCCASION, Dimension.AGENCY, Dimension.CONSTRAINTS}
    if len(changed) >= 3 or any(d in KEY_DIMENSIONS for d in changed):
        return TransitionSeverity.MAJOR

    # Minor: 1-2 non-key dimensions
    if len(changed) > 0:
        return TransitionSeverity.MINOR

    return TransitionSeverity.NONE
```

### Return Types

- `StateTracker.record(ctx)` → `Transition | None`
  - First record: Returns `None` (no previous state)
  - Subsequent: Returns `Transition` object

---

## Deletion & Retention

### What `clear()` Does

```python
tracker.clear()
```

- ✅ Clears in-memory history for THIS tracker instance
- ✅ Clears registered handlers
- ✅ Resets current context to None

### What `clear()` Does NOT Do

- ❌ Does not delete from audit logs
- ❌ Does not delete from metrics/traces
- ❌ Does not delete from export artifacts
- ❌ Does not clear OTHER workers' trackers (multi-process)
- ❌ Does not affect persisted data (future feature)

### GDPR Considerations

For full user data deletion under GDPR:
1. Call `tracker.clear()` for all user sessions
2. Purge audit logs via `gdpr_service.delete_user_data(user_id)`
3. Clear any cached export artifacts
4. Delete user from database

Currently, VCP context is NOT persisted beyond in-memory trackers, so `clear()` is sufficient for transient data. When persistence is added, explicit retention policies will be required.

---

## Related Documentation

| Document | Description |
|----------|-------------|
| [VCP_OVERVIEW.md](VCP_OVERVIEW.md) | Protocol specification |
| [VCP_IMPLEMENTATION_GUIDE.md](VCP_IMPLEMENTATION_GUIDE.md) | Developer reference |
| [VCP_ADAPTATION.md](adaptation/VCP_ADAPTATION.md) | VCP/A layer specification |

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.3.0 | 2026-01-12 | Added Security Model section; updated Persistence for Redis; updated Multi-Worker Behavior |
| 1.2.0 | 2026-01-12 | Added explicit Session Key Requirement subsection; documentation alignment pass |
| 1.1.0 | 2026-01-12 | Added Transport Bindings, Trust Model, Tracker Scope, Formal Rules, Deletion sections |
| 1.0.0 | 2026-01-12 | Initial documentation |
