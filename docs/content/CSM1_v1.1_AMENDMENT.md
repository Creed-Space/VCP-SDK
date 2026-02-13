# CSM-1 Format Amendment v1.1

**Status**: Draft
**Version**: 1.1.0
**Date**: 2026-02-13
**Layer**: 3 (VCP Content)
**Amends**: CSM1 Grammar Specification v1.0.0

---

## Summary

This amendment adds **Line 8 — Personal State (R-line)** to the CSM-1 token format, codifying the personal state encoding introduced in VCP Context Specification v3.1.

The R-line enables real-time transmission of user cognitive, emotional, and physical state as categorical dimensions with intensity values, allowing AI systems to adapt responses to the user's current condition.

---

## Change: Add Line 8 — Personal State (R-line)

### Position

The R-line is appended as the 8th line of the CSM-1 token, after the S-line (private markers).

### Complete CSM-1 v1.1 Token Format

```
Line 1: VCP:<version>:<profile-id>          Header
Line 2: C:<constitution>@<version>          Constitution reference
Line 3: P:<persona>:<adherence>             Persona and adherence level
Line 4: G:<goal>:<experience>:<style>       Goal context
Line 5: X:<constraints>                     Constraint flags (emoji-encoded)
Line 6: F:<flags>                           Public behavioral flags
Line 7: S:<private-markers>                 Private markers (stripped before transmission)
Line 8: R:<personal-state>                  Personal state dimensions (NEW)
```

### R-line Format

```abnf
r-line          = "R:" personal-state
personal-state  = "none" / dimension *( "|" dimension )

dimension       = emoji value ":" intensity [ ":" extended ]
emoji           = cognitive-emoji / emotional-emoji / energy-emoji / urgency-emoji / body-emoji

cognitive-emoji = %x1F9E0                ; U+1F9E0 BRAIN
emotional-emoji = %x1F4AD                ; U+1F4AD THOUGHT BALLOON
energy-emoji    = %x1F50B                ; U+1F50B BATTERY
urgency-emoji   = %x26A1                 ; U+26A1  HIGH VOLTAGE
body-emoji      = %x1FA7A                ; U+1FA7A STETHOSCOPE

value           = cognitive-value / emotional-value / energy-value / urgency-value / body-value
cognitive-value = "focused" / "distracted" / "overloaded" / "foggy" / "reflective"
emotional-value = "calm" / "tense" / "frustrated" / "neutral" / "uplifted"
energy-value    = "rested" / "low_energy" / "fatigued" / "wired" / "depleted"
urgency-value   = "unhurried" / "time_aware" / "pressured" / "critical"
body-value      = "neutral" / "discomfort" / "pain" / "unwell" / "recovering"

intensity       = "1" / "2" / "3" / "4" / "5"
extended        = 1*( ALPHA / "_" )      ; Optional sub-signal (e.g., "migraine")
```

### Dimensions

| Emoji | Dimension | Allowed Values | Purpose |
|-------|-----------|---------------|---------|
| `🧠` | `cognitive_state` | focused, distracted, overloaded, foggy, reflective | Mental bandwidth available for complex responses |
| `💭` | `emotional_tone` | calm, tense, frustrated, neutral, uplifted | Emotional register for response calibration |
| `🔋` | `energy_level` | rested, low_energy, fatigued, wired, depleted | Physical/mental energy for pacing and depth |
| `⚡` | `perceived_urgency` | unhurried, time_aware, pressured, critical | Time pressure for response conciseness |
| `🩺` | `body_signals` | neutral, discomfort, pain, unwell, recovering | Physical state for accommodation |

### Intensity Scale

| Value | Meaning |
|-------|---------|
| 1 | Barely noticeable / background signal |
| 2 | Mild / slightly affecting |
| 3 | Moderate / default if omitted (fail-open) |
| 4 | Strong / significantly affecting |
| 5 | Dominant / primary factor in current state |

**Fail-open default**: If intensity is omitted, parsers MUST treat it as `3` (moderate). This ensures partial tokens remain functional.

### Extended Sub-signals

The optional third field after a second colon provides specific context:

```
🩺unwell:4:migraine       → body_signals = unwell, intensity 4, cause: migraine
🧠overloaded:5:deadline   → cognitive_state = overloaded, intensity 5, cause: deadline
🔋depleted:4:insomnia     → energy_level = depleted, intensity 4, cause: insomnia
```

Extended sub-signals are informational. Parsers MAY use them for richer adaptation but MUST NOT require them.

### Privacy Classification

The R-line is classified as **Layer 3 (Personal State)** data:

- **Within the user's VCP agent**: Full R-line is available for local decision-making
- **Platform transmission**: R-line is included only if the user has explicitly consented to personal state sharing
- **Default**: R-line is STRIPPED before transmission (same privacy model as S-line private markers)
- **Constraint flags**: If R-line is stripped, derived constraint flags (e.g., `⚡var` for variable energy) MAY appear in the X-line instead

### Examples

**Full R-line**:
```
R:🧠focused:4|💭calm:3|🔋rested:2|⚡unhurried:1|🩺neutral:1
```

**Partial R-line** (only reporting dimensions that matter):
```
R:🧠overloaded:5|⚡pressured:4
```

**With extended sub-signal**:
```
R:🩺unwell:4:migraine|🔋depleted:3|💭tense:3
```

**No personal state**:
```
R:none
```

**Complete CSM-1 v1.1 token**:
```
VCP:1.0:user-alice-daily
C:family.safe.guide@1.2.0
P:G:3
G:learn_guitar:beginner:visual
X:🔇:💰low:⚡var
F:time_limited|noise_restricted
S:🔒housing|🔒health
R:🧠focused:4|💭calm:3|🔋low_energy:2|⚡time_aware:3
```

---

## Backward Compatibility

### Requirement

Parsers MUST accept 7-line tokens (no R-line = no personal state declared).

### Parser Behavior

| Input | Interpretation |
|-------|----------------|
| 8-line token with valid R-line | Parse personal state normally |
| 7-line token (no R-line) | Personal state is `null` / not declared |
| 8-line token with `R:none` | Personal state explicitly declared as absent |
| R-line with unknown dimension emoji | Skip unknown dimension, parse remainder |
| R-line with unknown value | Treat as opaque string, log warning |

### Serializer Behavior

| State | Output |
|-------|--------|
| Personal state present | Emit R-line with declared dimensions |
| Personal state empty | Emit `R:none` |
| Personal state null (not declared) | Omit R-line entirely (7-line token) |

---

## Relationship to VCP Context Specification v3.1

The R-line is the CSM-1 wire encoding of VCP Context Layer 3 (Personal State). The mapping is:

| VCP Context Dimension | R-line Emoji | R-line Field |
|----------------------|-------------|--------------|
| `COGNITIVE_STATE` | `🧠` | `cognitive_state` |
| `EMOTIONAL_TONE` | `💭` | `emotional_tone` |
| `ENERGY_LEVEL` | `🔋` | `energy_level` |
| `PERCEIVED_URGENCY` | `⚡` | `perceived_urgency` |
| `BODY_SIGNALS` | `🩺` | `body_signals` |

The categorical values and intensity scale are identical between the context specification and the R-line encoding.

---

## Signal Decay

Personal state dimensions are subject to signal decay as defined in VCP Context Specification v3.1 §2.5. When a dimension's signal has decayed below threshold:

- The dimension SHOULD be omitted from the R-line
- If retained, the intensity SHOULD be reduced to reflect decay
- Stale signals (>30 minutes without refresh) MUST NOT be transmitted at original intensity

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.1.0 | 2026-02-13 | Initial R-line amendment |
