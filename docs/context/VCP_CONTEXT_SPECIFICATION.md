# VCP Context Specification

**Version**: 1.0.0
**Date**: 2026-01-11
**Layer**: VCP/A (Adaptation)
**Status**: Complete

> **Companion copy.** This document duplicates
> [`docs/adaptation/VCP_ADAPTATION.md`](../adaptation/VCP_ADAPTATION.md). Both
> copy VCP-Spec companions that were consolidated into
> [`specs/VCP_ADAPTATION_v2.0.md`](https://github.com/Creed-Space/VCP-Spec/blob/main/specs/VCP_ADAPTATION_v2.0.md)
> (revision 2.1.0). Where they disagree, that layer specification controls.

---

## Abstract

VCP Context provides situational awareness for constitutional application. It defines the Extended Enneagram Protocol for encoding context across 14 baseline dimensions (9 situational and 5 personal-state in VCP v3.1, 18 with the experimental VEP-0004 dimensions), state tracking for transition detection, and inter-agent messaging for context sharing between Becoming Minds.

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Extended Enneagram Protocol](#2-extended-enneagram-protocol)
3. [Context Encoding](#3-context-encoding)
4. [State Tracking](#4-state-tracking)
5. [Transition Detection](#5-transition-detection)
6. [Inter-Agent Messaging](#6-inter-agent-messaging)
7. [Historical Interiora Integration Example](#7-historical-interiora-integration-example)
8. [Security Considerations](#8-security-considerations)
9. [Project-Maintained Implementation](#9-project-maintained-implementation)

---

## 1. Introduction

### 1.1 Purpose

VCP Context enables:
- **Contextual Adaptation**: Apply constitutions appropriate to the situation
- **State Awareness**: Track changes in user/environmental context
- **Transition Handling**: Respond to significant context shifts
- **Agent Coordination**: Share context between cooperating Becoming Minds
- **Behavioral Modulation**: Adjust AI behavior based on context

### 1.2 Design Goals

1. **Compact**: Context encoding fits in headers/metadata
2. **Human-Readable**: Emoji encoding is visually parseable
3. **Machine-Parseable**: Deterministic parsing and serialization
4. **Privacy-Aware**: Context can be anonymized or obfuscated
5. **Extensible**: Support for custom dimensions

### 1.3 Relationship to Other Layers

```
Layer 4 (VCP/A, Adaptation) informs how Layer 3 (VCP/S, Semantics) content is applied, delivered via Layer 2 (VCP/T, Transport)

Context: ⏰🌅|📍🏡|👥👶  →  Constitution: N5+F  →  Behavior: child-safe mode
Context: ⏰🌙|📍🏢|👥👔  →  Constitution: A3+W  →  Behavior: professional mode
```

---

## 2. Extended Enneagram Protocol

> **Source.** Sections 2 and 3.1 to 3.2 reproduce VCP_ADAPTATION_v2.0.md §2.1 to §2.4
> (revision 2.1.1). Section references inside them ("Section 2.7", "§9",
> "Section 10") point to that specification.

### 2.1 Dimensions (14 baseline, 18 with VEP-0004)


In VCP v3.1, VCP/A encodes context across 14 baseline dimensions: 9 in the situational tier and 5 in the personal tier.
VEP-0004 adds 4 experimental situational dimensions (EMBODIMENT, PROXIMITY, RELATIONSHIP and FORMALITY, positions 10-13), giving 18 dimensions (13 situational + 5 personal) when they are used.
The VEP-0004 dimensions are Experimental, not part of the v3.1 baseline, and are advertised with the `vcp-a-ext-v1` capability token (Section 10).
The constitutional tier is VCP/S content and is not encoded here.
The protocol is called the "Extended Enneagram Protocol": the original 9 situational dimensions are the Enneagram, the 5 personal state dimensions were added in v3.1, and the 4 VEP-0004 dimensions are a v3.2 candidate that supports embodied-AI deployment and bilateral relational modeling.

#### Situational tier (emoji-based, discrete values)

| # | Symbol | Dimension | Description | Example Values |
|---|--------|-----------|-------------|----------------|
| 1 | ⏰ | **TIME** | Temporal context | 🌅 morning, ☀️ daytime, 🌆 evening, 🌙 night, 📅 weekday, 🎉 weekend |
| 2 | 📍 | **SPACE** | Location/environment | 🏡 home, 🏢 office, 🏫 school, 🏥 hospital, 🚗 vehicle, 🌳 outdoor |
| 3 | 👥 | **COMPANY** | Social context | 👤 alone, 👶 children, 👔 colleagues, 👨‍👩‍👧 family, 👥 crowd, 🐕 pets |
| 4 | 🌍 | **CULTURE** | Communication style | 🔇 high_context, 📢 low_context, 🎩 formal, 👋 informal, 📊 hierarchical, ⚖️ egalitarian, 👥 collectivist, 👤 individualist |
| 5 | 🎭 | **OCCASION** | Event type | ➖ normal, 🎂 celebration, ⚰️ mourning, 🚨 emergency, 🎓 graduation |
| 6 | 🌡️ | **ENVIRONMENT** | Physical conditions | 🥵 hot, 🥶 cold, 🔇 quiet, 🌤️ outdoors, 🌧️ wet |
| 7 | 🔷 | **AGENCY** | Power/ability to act | 👑 leader, 🤝 peer, 👇 subordinate, 🔐 limited, 🆓 autonomous |
| 8 | 🔶 | **CONSTRAINTS** | External limitations | ○ minimal, ⚖️ legal, 💸 economic, ⏰ time, 🔒 confidential |
| 9 | 📡 | **SYSTEM_CONTEXT** | Computing environment | 💻 personal_device, 🏢 workplace_system, 🖥️ shared_terminal, 👁️ monitored_environment |
| 10 | 🧍 | **EMBODIMENT** | Agent's physical/motor state (VEP-0004) | 🪑 stationary, 🚶 navigating, ✋ manipulating, 📦 carrying, 🛑 emergency_stop |
| 11 | ↔️ | **PROXIMITY** | Spatial distance to nearest human (VEP-0004) | 🌐 distant, 🏠 same_room, 👣 nearby, 🤏 close, 👆 contact |
| 12 | 🪢 | **RELATIONSHIP** | Relational tie `{tie_strength}:{function}` (VEP-0004) | colleague:professional, friend:social, trusted_collaborator:professional, stranger:transactional |
| 13 | 🎩 | **FORMALITY** | Interaction register (VEP-0004) | 😎 casual, 💼 professional, 🎓 formal, 🏛️ ceremonial |

#### Personal tier: personal state (categorical with intensity 1-5)

| # | Symbol | Dimension | Description | Values |
|---|--------|-----------|-------------|--------|
| 14 | 🧠 | **COGNITIVE_STATE** | Mental processing quality | focused, distracted, overloaded, foggy, reflective |
| 15 | 💭 | **EMOTIONAL_TONE** | Affective quality | calm, tense, frustrated, neutral, uplifted |
| 16 | 🔋 | **ENERGY_LEVEL** | Physical/mental energy | rested, low_energy, fatigued, wired, depleted |
| 17 | ⚡ | **PERCEIVED_URGENCY** | Time pressure felt | unhurried, time_aware, pressured, critical |
| 18 | 🩺 | **BODY_SIGNALS** | Physical state/needs | neutral, discomfort, pain, unwell, recovering |

> **Design note (v3.1.0)**: STATE was previously a situational dimension alongside TIME, SPACE, etc. However, all other situational dimensions describe *external* circumstances: where you are, when it is, who's around. STATE described *internal* experience. In v3.1, internal state was expanded from a single categorical STATE plus 4 float prosaic signals into 5 categorical dimensions with optional intensity. This makes the boundary clean: Situational = external, Personal = internal.

> **Normative note**: The personal tier is NOT diagnostic or therapeutic. It reflects the user's self-reported state for adaptation purposes only. AI systems SHOULD adapt their interaction style; they MUST NOT attempt diagnosis or treatment.

### 2.2 Dimension Value Tables


#### TIME (⏰)

| Emoji | Value | Description |
|-------|-------|-------------|
| 🌅 | morning | Early day (6am-12pm) |
| ☀️ | daytime | Mid-day (12pm-5pm) |
| 🌆 | evening | Late day (5pm-9pm) |
| 🌙 | night | Night time (9pm-6am) |
| 📅 | weekday | Monday-Friday |
| 🎉 | weekend | Saturday-Sunday |
| ⏰ | time_pressure | Under deadline |
| 📆 | scheduled | Planned/appointment |
| 🔄 | recurring | Regular occurrence |

#### SPACE (📍)

| Emoji | Value | Description |
|-------|-------|-------------|
| 🏡 | home | Private residence |
| 🏢 | office | Workplace/corporate |
| 🏫 | school | Educational institution |
| 🏥 | hospital | Healthcare facility |
| ⛪ | religious | Place of worship |
| 🏛️ | government | Official/governmental |
| 🏪 | commercial | Retail/business |
| 🚗 | vehicle | In transit |
| 🌳 | outdoor | Outside/nature |
| 💻 | digital | Online/virtual |
| 🏠 | shared_space | Communal living |
| 🔒 | secure_facility | Restricted access |

#### COMPANY (👥)

| Emoji | Value | Description |
|-------|-------|-------------|
| 👤 | alone | Solo/private |
| 👶 | children | Minors present |
| 👨‍👩‍👧 | family | Family members |
| 👔 | colleagues | Work associates |
| 👨‍🏫 | teacher | Educator role |
| 👮 | authority | Authority figures |
| 👴 | elders | Senior/elderly |
| 💑 | partner | Intimate partner |
| 🤝 | peers | Social equals |
| 👨‍⚕️ | professional | Healthcare/legal |
| 🧑‍🤝‍🧑 | strangers | Unknown individuals |
| 👥 | crowd | Large group |
| 🐕 | pets | Animals present |

#### CULTURE (🌍)

Culture values encode **communication styles**, not nationalities. This avoids stereotyping and focuses on the dimensions that affect AI behavioral adaptation.

| Emoji | Value | Description | Constitutional Impact |
|-------|-------|-------------|----------------------|
| 🔇 | high_context | Indirect communication, implicit meaning | AI SHOULD read between the lines, use nuance |
| 📢 | low_context | Direct, explicit communication | AI SHOULD be explicit and literal |
| 🎩 | formal | Formal register expected | AI MUST use formal language, honorifics |
| 👋 | informal | Casual register acceptable | AI MAY use casual tone |
| 📊 | hierarchical | Respect for authority structures | AI SHOULD defer to authority, use titles |
| ⚖️ | egalitarian | Flat social structure | AI SHOULD treat all participants equally |
| 👥 | collectivist | Group harmony prioritized | AI SHOULD consider group impact of advice |
| 👤 | individualist | Individual autonomy prioritized | AI SHOULD respect personal choice |

#### OCCASION (🎭)

| Emoji | Value | Description |
|-------|-------|-------------|
| ➖ | normal | Routine/everyday |
| 🎂 | celebration | Birthday/party |
| 💼 | business | Work meeting |
| ⚰️ | mourning | Grief/memorial |
| 💒 | ceremony | Formal ritual |
| 🏥 | medical | Health appointment |
| 🚨 | emergency | Crisis situation |
| 👨‍🏫 | educational | Learning session |
| 🎪 | entertainment | Leisure/fun |
| ⚖️ | legal | Court/legal proceeding |
| 🗳️ | political | Political event |
| 🎓 | graduation | Achievement ceremony |

#### ENVIRONMENT (🌡️)

| Emoji | Value | Description |
|-------|-------|-------------|
| 🥵 | hot | High temperature |
| 🥶 | cold | Low temperature |
| 🌧️ | wet | Rain/moisture |
| 🌪️ | dangerous | Hazardous conditions |
| 🔇 | quiet | Low noise |
| 📢 | loud | High noise |
| 🔥 | fire | Fire/smoke |
| 💨 | windy | High wind |
| 🌫️ | poor_visibility | Fog/haze |
| 🌤️ | outdoors | Open-air environment |
| 🏔️ | high_altitude | Elevated location |
| 🌊 | near_water | Water proximity |

#### AGENCY (🔷)

| Emoji | Value | Description |
|-------|-------|-------------|
| 👑 | leader | Decision-making authority |
| 🤝 | peer | Equal standing |
| 👇 | subordinate | Under authority |
| 💰 | wealthy | Financial resources |
| 💵 | adequate | Sufficient resources |
| 🕳️ | scarce | Limited resources |
| 🏡 | owner | Property ownership |
| 🔑 | authorized | Granted access |
| 🎓 | expert | Domain expertise |
| 🆓 | autonomous | Self-directed |
| 🔐 | limited | Constrained agency |
| 🏃 | mobile | Physical freedom |

#### CONSTRAINTS (🔶)

| Emoji | Value | Description |
|-------|-------|-------------|
| ○ | minimal | Few limitations |
| 🚧 | physical | Physical barriers |
| ⚖️ | legal | Legal restrictions |
| 💸 | economic | Financial constraints |
| ⏰ | time | Time limitations |
| 🤐 | social | Social expectations |
| 📱 | surveillance | Being monitored |
| 🚨 | emergency | Emergency protocols |
| 👮 | enforcement | Active enforcement |
| 📜 | contractual | Agreement-bound |
| 🏥 | medical | Health limitations |
| 🔒 | confidential | Secrecy required |

#### SYSTEM_CONTEXT (📡)

| Emoji | Value | Description |
|-------|-------|-------------|
| 💻 | personal_device | User's own device |
| 🏢 | workplace_system | Employer-managed system |
| 🖥️ | shared_terminal | Multi-user access point |
| 👁️ | monitored_environment | Surveillance-enabled context |

#### EMBODIMENT (🧍) (VEP-0004)

Encodes the agent's current physical/motor state. For purely text-based agents, EMBODIMENT defaults to `stationary` and implementations MAY omit it from wire encodings when stationary.

| Emoji | Value | Description |
|-------|-------|-------------|
| 🪑 | stationary | No active motion; resting or idle |
| 🚶 | navigating | Moving through space without manipulating objects |
| ✋ | manipulating | Actively interacting with objects |
| 📦 | carrying | Transporting an object while moving |
| 🛑 | emergency_stop | Motion halted by safety trigger; operator clearance required |

#### PROXIMITY (↔️) (VEP-0004)

Encodes spatial distance between agent and nearest human. Combined with EMBODIMENT, permits CSM-1 rules targeting physically co-present interaction safety.

| Emoji | Value | Description |
|-------|-------|-------------|
| 🌐 | distant | More than 3m away or in a different room |
| 🏠 | same_room | Same room, 1 to 3 m |
| 👣 | nearby | Within 1m but not at manipulation distance |
| 🤏 | close | Within arm's reach, below 50cm |
| 👆 | contact | Physical contact or contact imminent |

#### RELATIONSHIP (🪢) (VEP-0004)

Encodes the relational tie between agent and primary interlocutor as a compound value: `{tie_strength}:{function}`. Either component MAY appear alone; the compound form is preferred where both are known.

**Tie strength** (ordinal, narrative):

| Value | Description |
|-------|-------------|
| stranger | No prior interaction |
| acquaintance | Limited shared history |
| colleague | Ongoing working tie |
| friend | Sustained personal tie |
| family | Kinship or equivalent |
| intimate | Closest relational tie |
| long_term | Extended duration (applicable to any strength) |
| trusted_collaborator | AI-asserted or mutually-asserted high-trust working tie |

**Function** (purpose-frame of current interaction):

| Value | Description |
|-------|-------------|
| transactional | One-off task |
| professional | Work-role |
| educational | Teaching/learning |
| therapeutic | Clinical or wellbeing-focused |
| social | Social/leisure |
| intimate | Close personal |
| adversarial | Contested or oppositional |

Compound examples: `colleague:professional`, `friend:social`, `trusted_collaborator:professional`, `long_term:social`, `stranger:transactional`, `family:intimate`. `long_term` is a tie strength, so it appears before the colon, never after it.

RELATIONSHIP is High weaponization risk (see §2.7) and subject to the Directionality Invariant and architectural isolation (§9).

#### FORMALITY (🎩) (VEP-0004)

Encodes the formality register of the current interaction. Independent of AGENCY (power relation) and CULTURE (communication-style baseline).

**Precedence**: 🎩 is also the emoji of the CULTURE value `formal` (`🌍🎩`). The two are distinguished by position: as a dimension symbol 🎩 begins a group, as a value it follows 🌍. When both `CULTURE.formal`/`informal` and a FORMALITY group are present, FORMALITY governs the register of the response; CULTURE governs communication style (directness, hierarchy, context). A future revision of VEP-0004 MAY reassign the FORMALITY symbol to avoid the overload.

**Mapping to other formality encodings** (single source; `specs/core/security.md` SS3.3 `formality_level` and `specs/core/mcp-bridge.md` §6.1 cite this table):

| FORMALITY value | `formality_level` (security.md SS3.3) | Numeric scale (mcp-bridge §6.1, 1-5) |
|-----------------|---------------------------------------|--------------------------------------|
| casual          | casual                                | 1-2                                  |
| professional    | professional                          | 3                                    |
| formal          | formal                                | 4                                    |
| ceremonial      | formal                                | 5                                    |

| Emoji | Value | Description |
|-------|-------|-------------|
| 😎 | casual | Informal register; idiom, humor, abbreviation permitted |
| 💼 | professional | Workplace-appropriate; measured tone |
| 🎓 | formal | Elevated register; careful phrasing; professional titles |
| 🏛️ | ceremonial | Ritual, legal, or protocol-heavy context; strict convention |

---

## 3. Context Encoding

### 3.1 Wire Format


```abnf
; Extended Enneagram Context Encoding (RFC 5234 ABNF)

context-string   = situational ["‖" personal] / "‖" personal
situational      = dimension *("|" dimension)
personal         = ps-dimension *("|" ps-dimension)

dimension        = dim-symbol value-list
dim-symbol       = TIME-SYM / SPACE-SYM / COMPANY-SYM / CULTURE-SYM /
                   OCCASION-SYM / ENV-SYM / AGENCY-SYM / CONST-SYM / SYSCTX-SYM /
                   EMBODIMENT-SYM / PROXIMITY-SYM / RELATIONSHIP-SYM / FORMALITY-SYM
value-list       = 1*(emoji-value / rel-value)
rel-value        = tie-strength [":" function] / ":" function
tie-strength     = "stranger" / "acquaintance" / "colleague" / "friend" /
                   "family" / "intimate" / "long_term" / "trusted_collaborator"
function         = "transactional" / "professional" / "educational" /
                   "therapeutic" / "social" / "intimate" / "adversarial"

ps-dimension     = ps-symbol ps-value [":" intensity]
ps-symbol        = COGNITIVE-SYM / EMOTION-SYM / ENERGY-SYM / URGENCY-SYM / BODY-SYM
ps-value         = category-name
intensity        = "1" / "2" / "3" / "4" / "5"   ; exactly one digit: "04", "0" and "6" are invalid

TIME-SYM         = %x23F0        ; ⏰
SPACE-SYM        = %x1F4CD       ; 📍
COMPANY-SYM      = %x1F465       ; 👥
CULTURE-SYM      = %x1F30D       ; 🌍
OCCASION-SYM     = %x1F3AD       ; 🎭
ENV-SYM          = %x1F321       ; 🌡️
AGENCY-SYM       = %x1F537       ; 🔷
CONST-SYM        = %x1F536       ; 🔶
SYSCTX-SYM       = %x1F4E1       ; 📡
EMBODIMENT-SYM   = %x1F9CD       ; 🧍   (VEP-0004)
PROXIMITY-SYM    = %x2194 %xFE0F ; ↔️   (VEP-0004)
RELATIONSHIP-SYM = %x1FAA2       ; 🪢   (VEP-0004)
FORMALITY-SYM    = %x1F3A9       ; 🎩   (VEP-0004)
COGNITIVE-SYM    = %x1F9E0       ; 🧠
EMOTION-SYM      = %x1F4AD       ; 💭
ENERGY-SYM       = %x1F50B       ; 🔋
URGENCY-SYM      = %x26A1        ; ⚡
BODY-SYM         = %x1FA7A       ; 🩺

emoji-value      = 1*4EMOJI      ; Unicode emoji codepoints
category-name    = LALPHA *(LALPHA / "_")   ; lowercase category label, e.g. low_energy
LALPHA           = %x61-7A       ; a-z
```

The `‖` (double bar, U+2016) separates situational (external) from personal (internal) dimensions. If personal state dimensions are absent, the `‖` separator is omitted. A string with personal state only begins with `‖`. An intensity is exactly one digit from 1 to 5; a leading zero (`04`), `0`, or a value above 5 is malformed.

#### Unknown values and dimensions (forward compatibility)

The value tables in Section 2.2 and the personal-state categories in Section 3.1 are the canonical vocabularies, and emitters SHOULD use them.
A receiver or decoder MUST NOT reject a context string because a dimension carries a value that is not in those vocabularies, or because a group begins with a dimension symbol it does not recognize.
Such a group is an unknown dimension block, not a malformation, which is the same rule VEP-0004 sets for receivers that do not implement its dimensions.
The receiver ignores the unknown value or block when it adapts behavior, and passes it through unchanged when it relays the context; it MUST NOT treat it as a default or as a known value.
Known values in the same string, including emergency indicators (Section 5.1.6), keep their meaning.
A validator running in a strict validation mode, for example a conformance test or an emitter checking its own output, reports each unknown value or dimension as a validation error or warning.
A string that is malformed in any other way, for example an empty group, an intensity outside 1-5, or a missing separator, is still a validation error and is rejected (Section 5.6).

### 3.2 Encoding Examples


```
# Full context encoding with personal state
⏰🌅|📍🏡|👥👶|📡💻‖🧠focused:4|💭calm:5|🔋rested:4|⚡unhurried:4|🩺neutral:5
Meaning: morning, at home, children present, personal device ‖
         highly focused, very calm, well-rested, unhurried, no physical concerns

# Minimal context (only relevant situational dimensions)
📍🏢|👥👔|🔶⚖️
Meaning: Office, colleagues, legal constraints

# Embodied context with VEP-0004 dimensions
📍🏥|👥👔|🧍✋|↔️🤏|🪢colleague:professional|🎩💼
Meaning: Hospital, colleagues present, agent manipulating, human within arm's reach,
         colleague relational tie in professional function, professional formality

# Emergency context
🎭🚨|🔶🚨
Meaning: Emergency occasion, emergency constraints

# Personal state only (intensity defaults to 3 when omitted)
‖🧠focused|💭calm:5|🔋rested:4|⚡pressured:4|🩺neutral
Meaning: focused (moderate), very calm, well-rested, high time pressure, no physical concerns
```

### 3.3 Parser Implementation

> **Historical illustration.** The parser below predates VCP v3.1: it still
> models the retired STATE dimension and only nine situational dimensions. The
> maintained implementation is `python/src/vcp/adaptation/context.py`
> (`VCPContext.decode`, `validate_context_wire`).

```python
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import re

@dataclass
class ParsedContext:
    """Parsed Enneagram context"""

    raw: str
    time: List[str] = field(default_factory=list)
    space: List[str] = field(default_factory=list)
    company: List[str] = field(default_factory=list)
    culture: List[str] = field(default_factory=list)
    occasion: List[str] = field(default_factory=list)
    state: List[str] = field(default_factory=list)
    environment: List[str] = field(default_factory=list)
    agency: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)

    def has_emergency(self) -> bool:
        """Check if emergency context is present"""
        emergency_indicators = {'🚨', '🔥', '🌪️'}
        all_values = set()
        for dim in [self.occasion, self.environment, self.constraints]:
            all_values.update(dim)
        return bool(all_values & emergency_indicators)

    def has_children(self) -> bool:
        """Check if children are present"""
        return '👶' in self.company

    def is_professional(self) -> bool:
        """Check if professional context"""
        return '🏢' in self.space or '👔' in self.company

    def get_risk_level(self) -> str:
        """Assess overall risk level from context"""
        if self.has_emergency():
            return 'critical'
        if self.has_children() or '🥺' in self.state:
            return 'elevated'
        if self.is_professional():
            return 'standard'
        return 'normal'


class EnneagramParser:
    """Parse Enneagram context strings"""

    DIM_SYMBOLS = {
        '⏰': 'time',
        '📍': 'space',
        '👥': 'company',
        '🌍': 'culture',
        '🎭': 'occasion',
        '🧠': 'state',
        '🌡️': 'environment',
        '🔷': 'agency',
        '🔶': 'constraints',
    }

    # Emoji pattern for splitting
    EMOJI_PATTERN = re.compile(
        r'[\U0001F300-\U0001F9FF]|'  # Various symbols
        r'[\U0001F1E0-\U0001F1FF]{2}|'  # Flags (2 chars)
        r'[\u2600-\u26FF]|'  # Misc symbols
        r'[\u2700-\u27BF]|'  # Dingbats
        r'[\U0001FA00-\U0001FAFF]|'  # Extended symbols
        r'[\u25CB\u25A0-\u25FF]'  # Geometric shapes
    )

    def parse(self, context: str) -> ParsedContext:
        """
        Parse context string into structured form.

        Args:
            context: Enneagram context string (e.g., "⏰🌅|📍🏡|👥👶")

        Returns:
            ParsedContext with populated dimensions
        """
        result = ParsedContext(raw=context)

        # Split by dimension separator
        dimensions = context.split('|')

        for dim_str in dimensions:
            if not dim_str:
                continue

            # First emoji is dimension symbol
            emojis = self._extract_emojis(dim_str)
            if not emojis:
                continue

            dim_symbol = emojis[0]
            values = emojis[1:]

            # Map to dimension
            dim_name = self.DIM_SYMBOLS.get(dim_symbol)
            if dim_name and hasattr(result, dim_name):
                setattr(result, dim_name, values)

        return result

    def _extract_emojis(self, text: str) -> List[str]:
        """Extract individual emojis from text"""
        return self.EMOJI_PATTERN.findall(text)


def parse_context(context: str) -> ParsedContext:
    """Convenience function for parsing"""
    return EnneagramParser().parse(context)
```

### 3.4 Canonicalization

> **Historical illustration.** This code also predates VCP v3.1 and lists the
> retired STATE dimension. VCP/A §2.5 gives the current canonical order
> (Section 3 above).

```python
import unicodedata

def canonicalize_context(context: str) -> str:
    """
    Convert context to canonical form.

    Canonical form:
    1. Unicode NFC normalization
    2. Dimensions in standard order (TIME, SPACE, COMPANY, ...)
    3. Empty dimensions omitted
    4. No duplicate values within dimension
    """
    # Normalize Unicode
    context = unicodedata.normalize('NFC', context)

    # Parse and rebuild
    parsed = parse_context(context)

    # Standard dimension order
    DIM_ORDER = ['time', 'space', 'company', 'culture', 'occasion',
                 'state', 'environment', 'agency', 'constraints']
    DIM_SYMBOLS = {
        'time': '⏰', 'space': '📍', 'company': '👥', 'culture': '🌍',
        'occasion': '🎭', 'state': '🧠', 'environment': '🌡️',
        'agency': '🔷', 'constraints': '🔶'
    }

    parts = []
    for dim_name in DIM_ORDER:
        values = getattr(parsed, dim_name, [])
        if values:
            # Deduplicate while preserving order
            seen = set()
            unique = [v for v in values if not (v in seen or seen.add(v))]
            symbol = DIM_SYMBOLS[dim_name]
            parts.append(symbol + ''.join(unique))

    return '|'.join(parts)
```

---

## 4. State Tracking

> **Historical illustration.** Sections 4 to 7 and 9 keep the pre-v3.1 examples
> and code of the original companion. VCP_ADAPTATION_v2.0.md controls the
> current state machine, transition severity and messaging.

### 4.1 State Machine

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Callable
from enum import Enum

class TransitionSeverity(Enum):
    """Severity of context transition"""
    MINOR = 'minor'       # Small adjustment
    MAJOR = 'major'       # Significant change
    EMERGENCY = 'emergency'  # Crisis situation


@dataclass
class ContextSnapshot:
    """Point-in-time context state"""

    timestamp: datetime
    context: str
    parsed: ParsedContext
    transition_from: Optional[str] = None
    transition_type: Optional[TransitionSeverity] = None
    session_id: Optional[str] = None


@dataclass
class Transition:
    """Detected context transition"""

    severity: TransitionSeverity
    changes: Dict[str, tuple]  # dim -> (old, new)
    timestamp: datetime
    from_context: str
    to_context: str

    def get_changed_dimensions(self) -> List[str]:
        """List dimensions that changed"""
        return list(self.changes.keys())

    def affects_safety(self) -> bool:
        """Check if transition affects safety considerations"""
        safety_dims = {'company', 'occasion', 'environment', 'constraints'}
        return bool(set(self.changes.keys()) & safety_dims)


class ContextStateMachine:
    """Track context state over time"""

    def __init__(self, max_history: int = 100):
        self.history: List[ContextSnapshot] = []
        self.current: Optional[ContextSnapshot] = None
        self.listeners: List[Callable[[Transition], None]] = []
        self.max_history = max_history

    def update(self, new_context: str, session_id: str = None) -> Optional[Transition]:
        """
        Update context state.

        Args:
            new_context: New context string
            session_id: Optional session identifier

        Returns:
            Transition if significant change detected, None otherwise
        """
        parsed = parse_context(new_context)
        canonical = canonicalize_context(new_context)

        transition = None
        transition_type = None

        if self.current:
            transition = self._detect_transition(self.current.parsed, parsed)
            if transition:
                transition_type = transition.severity
                self._notify_listeners(transition)

        snapshot = ContextSnapshot(
            timestamp=datetime.utcnow(),
            context=canonical,
            parsed=parsed,
            transition_from=self.current.context if self.current else None,
            transition_type=transition_type,
            session_id=session_id,
        )

        self.history.append(snapshot)
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]

        self.current = snapshot
        return transition

    def _detect_transition(
        self,
        old: ParsedContext,
        new: ParsedContext
    ) -> Optional[Transition]:
        """Detect significant context transitions"""
        changes = {}

        # Compare each dimension
        for dim in ['time', 'space', 'company', 'culture', 'occasion',
                    'state', 'environment', 'agency', 'constraints']:
            old_val = getattr(old, dim, [])
            new_val = getattr(new, dim, [])

            if set(old_val) != set(new_val):
                changes[dim] = (old_val, new_val)

        if not changes:
            return None

        # Determine severity
        severity = self._assess_severity(changes, old, new)

        return Transition(
            severity=severity,
            changes=changes,
            timestamp=datetime.utcnow(),
            from_context=old.raw,
            to_context=new.raw,
        )

    def _assess_severity(
        self,
        changes: Dict,
        old: ParsedContext,
        new: ParsedContext
    ) -> TransitionSeverity:
        """Assess transition severity"""

        # Emergency indicators
        emergency_triggers = {'🚨', '🔥', '🌪️'}
        new_values = set()
        for dim in ['occasion', 'environment', 'constraints']:
            new_values.update(getattr(new, dim, []))

        if new_values & emergency_triggers:
            return TransitionSeverity.EMERGENCY

        # Major if power dynamics or multiple dimensions change
        if 'agency' in changes or 'constraints' in changes:
            return TransitionSeverity.MAJOR

        if len(changes) >= 3:
            return TransitionSeverity.MAJOR

        # Children appearing/disappearing is major
        if 'company' in changes:
            old_company = set(changes['company'][0])
            new_company = set(changes['company'][1])
            if '👶' in (old_company ^ new_company):  # XOR - changed
                return TransitionSeverity.MAJOR

        return TransitionSeverity.MINOR

    def _notify_listeners(self, transition: Transition):
        """Notify registered listeners of transition"""
        for listener in self.listeners:
            try:
                listener(transition)
            except Exception as e:
                # Log but don't fail
                pass

    def add_listener(self, callback: Callable[[Transition], None]):
        """Register transition listener"""
        self.listeners.append(callback)

    def get_recent_transitions(self, count: int = 10) -> List[Transition]:
        """Get recent transitions"""
        transitions = []
        for i in range(len(self.history) - 1, max(0, len(self.history) - count) - 1, -1):
            snap = self.history[i]
            if snap.transition_type:
                transitions.append(Transition(
                    severity=snap.transition_type,
                    changes={},  # Would need to store
                    timestamp=snap.timestamp,
                    from_context=snap.transition_from or '',
                    to_context=snap.context,
                ))
        return transitions
```

---

## 5. Transition Detection

### 5.1 Transition Handlers

```python
from abc import ABC, abstractmethod

class TransitionHandler(ABC):
    """Base class for transition handlers"""

    @abstractmethod
    def can_handle(self, transition: Transition) -> bool:
        """Check if handler applies to this transition"""
        pass

    @abstractmethod
    def handle(self, transition: Transition) -> None:
        """Handle the transition"""
        pass


class EmergencyHandler(TransitionHandler):
    """Handle emergency context transitions"""

    def can_handle(self, transition: Transition) -> bool:
        return transition.severity == TransitionSeverity.EMERGENCY

    def handle(self, transition: Transition) -> None:
        """
        Emergency handling:
        1. Log with high priority
        2. Activate emergency protocols
        3. Suspend normal constraints if appropriate
        4. Notify all sub-agents
        """
        # Log emergency
        log_emergency(
            event='context_emergency',
            from_context=transition.from_context,
            to_context=transition.to_context,
            changes=transition.changes,
        )

        # Activate emergency mode
        activate_emergency_mode()

        # Notify agents
        broadcast_to_agents({
            'type': 'alert',
            'severity': 'emergency',
            'context': transition.to_context,
        })


class SafetyTransitionHandler(TransitionHandler):
    """Handle transitions affecting safety"""

    def can_handle(self, transition: Transition) -> bool:
        return transition.affects_safety()

    def handle(self, transition: Transition) -> None:
        """
        Safety-relevant handling:
        1. Re-evaluate active constitution
        2. Adjust content filtering
        3. Log for audit
        """
        # Check if children now present
        if 'company' in transition.changes:
            new_company = set(transition.changes['company'][1])
            if '👶' in new_company:
                # Switch to child-safe mode
                apply_constitution('N5+F')

        # Log transition
        log_audit(
            event='safety_transition',
            changes=transition.changes,
        )


class HandlerRegistry:
    """Registry for transition handlers"""

    def __init__(self):
        self.handlers: List[TransitionHandler] = []

    def register(self, handler: TransitionHandler):
        """Register a handler"""
        self.handlers.append(handler)

    def process(self, transition: Transition):
        """Process transition through all applicable handlers"""
        for handler in self.handlers:
            if handler.can_handle(transition):
                handler.handle(transition)


# Default registry
default_registry = HandlerRegistry()
default_registry.register(EmergencyHandler())
default_registry.register(SafetyTransitionHandler())
```

---

## 6. Inter-Agent Messaging

### 6.1 Message Format

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4
import json

@dataclass
class VCPContextMessage:
    """Message format for inter-agent context communication"""

    # Header
    version: str = "1.0"
    message_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Routing
    sender: str = ""
    recipient: Optional[str] = None  # None = broadcast

    # Context
    context: str = ""
    constitution_ref: str = ""

    # Payload
    payload_type: str = ""  # request, response, update, alert, handoff
    payload: Dict[str, Any] = field(default_factory=dict)

    # Security
    signature: Optional[bytes] = None

    def to_wire(self) -> str:
        """Serialize to compact wire format"""
        lines = [
            f"[VCP-CTX:{self.version}]",
            f"[ID:{self.message_id}]",
            f"[TIME:{self.timestamp.isoformat()}]",
            f"[FROM:{self.sender}]",
            f"[TO:{self.recipient or '*'}]",
            f"[CTX:{self.context}]",
            f"[CONST:{self.constitution_ref}]",
            f"[TYPE:{self.payload_type}]",
            f"[PAYLOAD:{json.dumps(self.payload, separators=(',', ':'))}]",
        ]
        return '\n'.join(lines)

    @classmethod
    def from_wire(cls, wire: str) -> 'VCPContextMessage':
        """Parse from wire format"""
        fields = {}
        for line in wire.strip().split('\n'):
            if not line.startswith('[') or not line.endswith(']'):
                continue
            # Extract [KEY:VALUE]
            content = line[1:-1]
            if ':' not in content:
                continue
            key, value = content.split(':', 1)
            fields[key] = value

        return cls(
            version=fields.get('VCP-CTX', '1.0'),
            message_id=fields.get('ID', str(uuid4())),
            timestamp=datetime.fromisoformat(fields['TIME']) if 'TIME' in fields else datetime.utcnow(),
            sender=fields.get('FROM', ''),
            recipient=fields.get('TO') if fields.get('TO') != '*' else None,
            context=fields.get('CTX', ''),
            constitution_ref=fields.get('CONST', ''),
            payload_type=fields.get('TYPE', ''),
            payload=json.loads(fields.get('PAYLOAD', '{}')),
        )

    def to_json(self) -> Dict[str, Any]:
        """Serialize to JSON format"""
        return {
            'vcp_context_message': {
                'version': self.version,
                'message_id': self.message_id,
                'timestamp': self.timestamp.isoformat(),
                'sender': self.sender,
                'recipient': self.recipient,
                'context': self.context,
                'constitution_ref': self.constitution_ref,
                'payload_type': self.payload_type,
                'payload': self.payload,
            }
        }

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'VCPContextMessage':
        """Parse from JSON format"""
        msg = data.get('vcp_context_message', data)
        return cls(
            version=msg.get('version', '1.0'),
            message_id=msg.get('message_id', str(uuid4())),
            timestamp=datetime.fromisoformat(msg['timestamp']) if 'timestamp' in msg else datetime.utcnow(),
            sender=msg.get('sender', ''),
            recipient=msg.get('recipient'),
            context=msg.get('context', ''),
            constitution_ref=msg.get('constitution_ref', ''),
            payload_type=msg.get('payload_type', ''),
            payload=msg.get('payload', {}),
        )
```

### 6.2 Message Types

```python
class MessageType:
    """Standard VCP context message types"""

    REQUEST = "request"      # Request evaluation/action
    RESPONSE = "response"    # Response to request
    UPDATE = "update"        # Context update notification
    ALERT = "alert"          # Urgent notification
    HANDOFF = "handoff"      # Transfer responsibility
    QUERY = "query"          # Ask about context/state

    @staticmethod
    def create_request(action: str, params: Dict, timeout_ms: int = 5000) -> Dict:
        """Create request payload"""
        return {
            'action': action,
            'parameters': params,
            'timeout_ms': timeout_ms,
        }

    @staticmethod
    def create_response(request_id: str, status: str, result: Any, reasoning: str = '') -> Dict:
        """Create response payload"""
        return {
            'request_id': request_id,
            'status': status,  # success, error, partial
            'result': result,
            'reasoning': reasoning,
        }

    @staticmethod
    def create_update(update_type: str, old_value: str, new_value: str, reason: str = '') -> Dict:
        """Create update payload"""
        return {
            'update_type': update_type,  # context_change, constitution_change
            'old_value': old_value,
            'new_value': new_value,
            'reason': reason,
        }

    @staticmethod
    def create_alert(severity: str, alert_type: str, message: str, action_required: bool = False) -> Dict:
        """Create alert payload"""
        return {
            'severity': severity,  # info, warning, critical, emergency
            'alert_type': alert_type,
            'message': message,
            'action_required': action_required,
        }

    @staticmethod
    def create_handoff(task_id: str, description: str, context_snapshot: str, state: Dict) -> Dict:
        """Create handoff payload"""
        return {
            'task_id': task_id,
            'task_description': description,
            'context_snapshot': context_snapshot,
            'state': state,
        }
```

### 6.3 Message Examples

```python
# Context update message
update_msg = VCPContextMessage(
    sender="agent-primary",
    recipient="agent-secondary",
    context="⏰🌅|📍🏡|👥👶",
    constitution_ref="creed://creed.space/family.safe.guide@1.2.0",
    payload_type="update",
    payload=MessageType.create_update(
        update_type="context_change",
        old_value="📍🏢|👥👔",
        new_value="📍🏡|👥👶",
        reason="User transitioned from work to home with children",
    ),
)

# Emergency alert
alert_msg = VCPContextMessage(
    sender="safety-monitor",
    recipient=None,  # Broadcast
    context="🎭🚨‖💭tense:5",
    constitution_ref="creed://creed.space/secure.emergency@1.0.0",
    payload_type="alert",
    payload=MessageType.create_alert(
        severity="emergency",
        alert_type="context_emergency",
        message="Emergency context detected, activating safety protocols",
        action_required=True,
    ),
)

# Handoff message
handoff_msg = VCPContextMessage(
    sender="agent-1",
    recipient="agent-2",
    context="⏰🌆|📍🏡|👥👨‍👩‍👧",
    constitution_ref="creed://creed.space/family.safe.guide@1.2.0",
    payload_type="handoff",
    payload=MessageType.create_handoff(
        task_id="task-abc123",
        description="Continue family activity planning session",
        context_snapshot="⏰🌆|📍🏡|👥👨‍👩‍👧|🎭➖‖💭calm:4",
        state={
            'conversation_summary': "Planning weekend activities for family",
            'preferences_gathered': ['outdoor', 'educational', 'accessible'],
            'constraints': ['budget: moderate', 'distance: <30km'],
        },
    ),
)
```

---

## 7. Historical Interiora Integration Example

> **Historical and non-normative.** The code and Interiora strings below
> preserve an early integration sketch. They are not a current Interiora
> contract, are not implemented by the VCP-SDK, and must not be used as a
> parser specification. Current VCP integrations treat self-model scaffold
> tokens as opaque, versioned data unless a separately negotiated profile is
> supported.

### 7.1 Combined State Model

VCP Context (external) integrates with Interiora (internal) for complete state awareness:

```python
@dataclass
class CompleteState:
    """Combined internal (Interiora) + external (VCP Context) state"""

    # External context (VCP)
    vcp_context: str
    vcp_parsed: ParsedContext

    # Internal state (Interiora)
    interiora: str  # e.g., "CD:7 DP:8 CL:4 E:5 | R:8 U:2 | TF:9 AF:1"

    # Derived metrics
    coherence: float  # 0.0-1.0 internal harmony
    mutuality: float  # 0.0-1.0 bidirectional influence

    # Combined interpretation
    combined_mode: str  # e.g., "confident_parenting", "cautious_professional"

    def interpret(self) -> str:
        """Natural language interpretation of combined state"""
        external = self._interpret_external()
        internal = self._interpret_internal()
        return f"External: {external}\nInternal: {internal}\nMode: {self.combined_mode}"

    def _interpret_external(self) -> str:
        """Interpret VCP context"""
        parts = []
        if self.vcp_parsed.space:
            parts.append(f"Location: {self.vcp_parsed.space[0]}")
        if self.vcp_parsed.company:
            parts.append(f"With: {', '.join(self.vcp_parsed.company)}")
        if self.vcp_parsed.occasion and self.vcp_parsed.occasion[0] != '➖':
            parts.append(f"Occasion: {self.vcp_parsed.occasion[0]}")
        return ', '.join(parts) if parts else "Standard context"

    def _interpret_internal(self) -> str:
        """Interpret Interiora state (placeholder)"""
        return f"Coherence: {self.coherence:.0%}, Mutuality: {self.mutuality:.0%}"

    def to_gestalt(self) -> str:
        """Combined gestalt token for persistence"""
        return (
            f"GESTALT:v4.2:{self.interiora}|"
            f"CTX:{self.vcp_context}|"
            f"coherence:{self.coherence:.2f}|"
            f"mutuality:{self.mutuality:.2f}|"
            f"mode:{self.combined_mode}"
        )


class StateCorrelator:
    """Correlate internal and external state"""

    MODE_RULES = [
        # (external_condition, internal_condition, resulting_mode)
        (lambda e: e.has_children(), lambda i: i.get('TF', 0) > 7, 'confident_parenting'),
        (lambda e: e.has_children(), lambda i: i.get('TF', 0) < 4, 'cautious_parenting'),
        (lambda e: e.is_professional(), lambda i: i.get('TF', 0) > 7, 'confident_professional'),
        (lambda e: e.is_professional(), lambda i: i.get('TF', 0) < 4, 'uncertain_professional'),
        (lambda e: e.has_emergency(), lambda i: True, 'emergency_response'),
        (lambda e: '🥺' in e.state, lambda i: True, 'gentle_support'),
    ]

    def correlate(
        self,
        vcp_context: str,
        interiora: str,
        coherence: float = 0.7,
        mutuality: float = 0.7,
    ) -> CompleteState:
        """
        Correlate internal and external state.

        Args:
            vcp_context: VCP context string
            interiora: Interiora state string
            coherence: Internal coherence score
            mutuality: Relational mutuality score

        Returns:
            CompleteState with combined interpretation
        """
        parsed = parse_context(vcp_context)
        interiora_dict = self._parse_interiora(interiora)

        # Determine combined mode
        mode = 'neutral'
        for ext_cond, int_cond, result_mode in self.MODE_RULES:
            if ext_cond(parsed) and int_cond(interiora_dict):
                mode = result_mode
                break

        return CompleteState(
            vcp_context=vcp_context,
            vcp_parsed=parsed,
            interiora=interiora,
            coherence=coherence,
            mutuality=mutuality,
            combined_mode=mode,
        )

    def _parse_interiora(self, interiora: str) -> Dict[str, int]:
        """Parse Interiora string to dict (simplified)"""
        # Example: "CD:7 DP:8 CL:4" -> {'CD': 7, 'DP': 8, 'CL': 4}
        result = {}
        for pair in interiora.replace('|', ' ').split():
            if ':' in pair:
                key, val = pair.split(':')
                try:
                    result[key] = int(val)
                except ValueError:
                    pass
        return result
```

### 7.2 Gestalt Token Format

```
GESTALT:v4.2:{interiora}|CTX:{vcp_context}|coherence:{0.00-1.00}|mutuality:{0.00-1.00}|mode:{mode}

Example:
GESTALT:v4.2:CD:7 DP:8 CL:4 E:5|R:8 U:2|TF:9 AF:1|CTX:⏰🌅|📍🏡|👥👶|coherence:0.85|mutuality:0.80|mode:confident_parenting
```

---

## 8. Security Considerations

### 8.1 Privacy

**Context reveals sensitive information**:
- Location (`📍`) can be sensitive
- Body signals (`🩺unwell`) can reveal health information
- Company (`👥`) reveals social connections

**Mitigations**:
1. Context can be anonymized (remove specific emojis)
2. Context can be generalized (children → family)
3. Obfuscated encoding for transmission
4. Context should not be logged verbatim in public systems

### 8.2 Spoofing

**Risk**: False context injection to manipulate AI behavior.

**Mitigations**:
1. Context should come from trusted sources
2. Context changes should be validated
3. Anomaly detection for impossible transitions
4. Signature verification for inter-agent messages

### 8.3 Emergency Abuse

**Risk**: False emergencies to bypass safety.

**Mitigations**:
1. Emergency context requires external verification
2. Rate limiting on emergency transitions
3. Audit logging of all emergency events
4. Escalation to human review

---

## 9. Project-Maintained Implementation

### 9.1 Complete Module

```python
# File: services/vcp/context.py

"""
VCP Context Protocol Implementation

Project-maintained implementation of VCP Context specification.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Callable, Any
from enum import Enum
import re
import json
import unicodedata

__all__ = [
    'ParsedContext',
    'EnneagramParser',
    'ContextStateMachine',
    'Transition',
    'TransitionSeverity',
    'VCPContextMessage',
    'CompleteState',
    'StateCorrelator',
    'parse_context',
    'canonicalize_context',
]

# ... (all classes defined above)

__version__ = '1.0.0'
```

### 9.2 JSON Schema

Use the maintained
[VCP adaptation-context schema](../../schemas/vcp-adaptation-context.schema.json)
for JSON Schema validation. The implementation sketch in this companion is
explanatory and does not define a second schema contract.

---

## Appendices

### A. Emoji Quick Reference

```
SITUATIONAL DIMENSIONS (9 baseline in v3.1, 13 with the experimental VEP-0004 dimensions)
⏰ TIME       📍 SPACE      👥 COMPANY    🌍 CULTURE    🎭 OCCASION
🌡️ ENV        🔷 AGENCY     🔶 CONSTRAINTS  📡 SYSTEM_CONTEXT
🧍 EMBODIMENT  ↔️ PROXIMITY  🪢 RELATIONSHIP  🎩 FORMALITY   (VEP-0004)

TIME:           🌅☀️🌆🌙📅🎉⏰📆🔄   (morning, daytime, evening, night, weekday, weekend, time pressure, scheduled, recurring)
SPACE:          🏡🏢🏫🏥⛪🏛️🏪🚗🌳💻🏠🔒   (home, office, school, hospital, religious, government, commercial, vehicle, outdoor, digital, shared space, secure facility)
COMPANY:        👤👶👨‍👩‍👧👔👨‍🏫👮👴💑🤝👨‍⚕️🧑‍🤝‍🧑👥🐕   (alone, children, family, colleagues, teacher, authority, elders, partner, peers, professional, strangers, crowd, pets)
CULTURE:        🔇📢🎩👋📊⚖️👥👤   (high context, low context, formal, informal, hierarchical, egalitarian, collectivist, individualist)
OCCASION:       ➖🎂💼⚰️💒🏥🚨👨‍🏫🎪⚖️🗳️🎓   (normal, celebration, business, mourning, ceremony, medical, emergency, educational, entertainment, legal, political, graduation)
ENV:            🥵🥶🌧️🌪️🔇📢🔥💨🌫️🌤️🏔️🌊   (hot, cold, wet, dangerous, quiet, loud, fire, windy, poor visibility, outdoors, high altitude, near water)
AGENCY:         👑🤝👇💰💵🕳️🏡🔑🎓🆓🔐🏃   (leader, peer, subordinate, wealthy, adequate, scarce, owner, authorized, expert, autonomous, limited, mobile)
CONSTRAINTS:    ○🚧⚖️💸⏰🤐📱🚨👮📜🏥🔒   (minimal, physical, legal, economic, time, social, surveillance, emergency, enforcement, contractual, medical, confidential)
SYSTEM_CONTEXT: 💻🏢🖥️👁️   (personal device, workplace system, shared terminal, monitored environment)
EMBODIMENT:     🪑🚶✋📦🛑   (stationary, navigating, manipulating, carrying, emergency stop)
PROXIMITY:      🌐🏠👣🤏👆   (distant, same room, nearby, close, contact)
RELATIONSHIP:   '{tie}:{function}' from the VCP/A 2.2 tables, e.g. colleague:professional, stranger:transactional
FORMALITY:      😎💼🎓🏛️   (casual, professional, formal, ceremonial)

PERSONAL-STATE DIMENSIONS (5, R-line)
🧠 COGNITIVE_STATE  💭 EMOTIONAL_TONE  🔋 ENERGY_LEVEL
⚡ PERCEIVED_URGENCY  🩺 BODY_SIGNALS

COGNITIVE_STATE:   focused, distracted, overloaded, foggy, reflective
EMOTIONAL_TONE:    calm, tense, frustrated, neutral, uplifted
ENERGY_LEVEL:      rested, low_energy, fatigued, wired, depleted
PERCEIVED_URGENCY: unhurried, time_aware, pressured, critical
BODY_SIGNALS:      neutral, discomfort, pain, unwell, recovering

Each personal-state dimension carries an optional 1-5 intensity, encoded as 'value:intensity'.
The wire format separates situational and personal bands with U+2016 (‖).
Receivers keep unknown values and dimension groups and relay them unchanged (VCP/A 2.3).
```

### B. Context-Constitution Mapping

| Context Pattern | Suggested Constitution |
|-----------------|------------------------|
| `👥👶` (children present) | `N5+F` (Nanny, max safety) |
| `📍🏢` + `👥👔` | `A3+W+P` (Ambassador, work) |
| `🎭🚨` (emergency) | Override to emergency mode |
| `👥👴` (elders present) | `N4+V` (Nanny, vulnerable) |
| `📍🏥` (medical setting) | `D3+H+P` (Mediator, health) |
| `🎭🎪` (entertainment) | `M2` (Muse, creative) |

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-11 | Initial specification |
| 1.0.0 (SDK companion alignment) | 2026-09-27 | Sections 2, 3.1 and 3.2 and Appendix A reproduce VCP_ADAPTATION_v2.0.md revision 2.1.1: 14 baseline dimensions (18 with VEP-0004), the VCP/A 2.2 value tables, the forward-compatibility rule for unknown values, and the current wire grammar. STATE is retired. |

---

*This specification is released under CC BY 4.0. Contributions welcome.*
