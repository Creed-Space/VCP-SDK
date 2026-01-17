# VCP-Adaptation: Context & State Specification

**Version**: 1.0.0
**Date**: 2026-01-11
**Layer**: VCP/A (Adaptation)
**Status**: Complete

> *Part of the Value-Context Protocol (VCP) - Layer 4*

---

## Abstract

VCP Context provides situational awareness for constitutional application. It defines the Enneagram Protocol for encoding context across 9 dimensions, state tracking for transition detection, and inter-agent messaging for context sharing between AI systems.

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Enneagram Protocol](#2-enneagram-protocol)
3. [Context Encoding](#3-context-encoding)
4. [State Tracking](#4-state-tracking)
5. [Transition Detection](#5-transition-detection)
6. [Inter-Agent Messaging](#6-inter-agent-messaging)
7. [Interiora Integration](#7-interiora-integration)
8. [Security Considerations](#8-security-considerations)
9. [Reference Implementation](#9-reference-implementation)

---

## 1. Introduction

### 1.1 Purpose

VCP Context enables:
- **Contextual Adaptation**: Apply constitutions appropriate to the situation
- **State Awareness**: Track changes in user/environmental context
- **Transition Handling**: Respond to significant context shifts
- **Agent Coordination**: Share context between cooperating AI systems
- **Behavioral Modulation**: Adjust AI behavior based on context

### 1.2 Design Goals

1. **Compact**: Context encoding fits in headers/metadata
2. **Human-Readable**: Emoji encoding is visually parseable
3. **Machine-Parseable**: Deterministic parsing and serialization
4. **Privacy-Aware**: Context can be anonymized or obfuscated
5. **Extensible**: Support for custom dimensions

### 1.3 Relationship to Other Layers

```
Layer 4 (Context) informs how Layer 3 (Content) is applied via Layer 2 (Transport)

Context: ⏰🌅|📍🏡|👥👶  →  Constitution: N5+F  →  Behavior: child-safe mode
Context: ⏰🌙|📍🏢|👥👔  →  Constitution: A3+W  →  Behavior: professional mode
```

---

## 2. Enneagram Protocol

### 2.1 Nine Dimensions

The Enneagram Protocol encodes context across 9 dimensions:

| Dim | Symbol | Name | Description | Example Values |
|-----|--------|------|-------------|----------------|
| 1 | ⏰ | **TIME** | Temporal context | 🌅morning, 🌙night, 📅weekday |
| 2 | 📍 | **SPACE** | Location/environment | 🏡home, 🏢office, 🏫school |
| 3 | 👥 | **COMPANY** | Social context | 👤alone, 👶children, 👔colleagues |
| 4 | 🌍 | **CULTURE** | Cultural/regional | 🇺🇸american, 🇯🇵japanese, 🌍global |
| 5 | 🎭 | **OCCASION** | Event type | ➖normal, 🎂celebration, 🚨emergency |
| 6 | 🧠 | **STATE** | Mental/emotional | 😊happy, 😰anxious, 😴tired |
| 7 | 🌡️ | **ENVIRONMENT** | Physical conditions | ☀️comfortable, 🥵hot, 🔇quiet |
| 8 | 🔷 | **AGENCY** | Power/ability to act | 👑leader, 🤝peer, 🔐limited |
| 9 | 🔶 | **CONSTRAINTS** | External limitations | ○minimal, ⚖️legal, 💸economic |

### 2.2 Dimension Values

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

#### CULTURE (🌍)

| Emoji | Value | Description |
|-------|-------|-------------|
| 🇺🇸 | american | US cultural context |
| 🇬🇧 | british | UK cultural context |
| 🇯🇵 | japanese | Japanese cultural context |
| 🇮🇳 | indian | Indian cultural context |
| 🇨🇳 | chinese | Chinese cultural context |
| 🇪🇺 | european | European cultural context |
| 🌍 | global | International/multicultural |
| 🏛️ | traditional | Conservative/traditional |
| 🆕 | progressive | Modern/progressive |
| 🕌 | islamic | Islamic cultural context |
| ✡️ | jewish | Jewish cultural context |
| ☯️ | eastern | East Asian philosophy |

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

#### STATE (🧠)

| Emoji | Value | Description |
|-------|-------|-------------|
| 😊 | happy | Positive mood |
| 😴 | tired | Fatigued |
| 😰 | anxious | Worried/nervous |
| 😡 | angry | Frustrated/upset |
| 😢 | sad | Down/melancholy |
| 🤒 | sick | Physically unwell |
| 😋 | hungry | Need for food |
| 🥳 | excited | Enthusiastic |
| 😌 | calm | Relaxed/peaceful |
| 🤔 | contemplative | Thoughtful/reflective |
| 😵 | overwhelmed | Stressed/overloaded |
| 🥺 | vulnerable | Emotionally fragile |

#### ENVIRONMENT (🌡️)

| Emoji | Value | Description |
|-------|-------|-------------|
| ☀️ | comfortable | Pleasant conditions |
| 🥵 | hot | High temperature |
| 🥶 | cold | Low temperature |
| 🌧️ | wet | Rain/moisture |
| 🌪️ | dangerous | Hazardous conditions |
| 🔇 | quiet | Low noise |
| 📢 | loud | High noise |
| 🔥 | fire | Fire/smoke |
| 💨 | windy | High wind |
| 🌫️ | poor_visibility | Fog/haze |
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

---

## 3. Context Encoding

### 3.1 Wire Format

```abnf
; Enneagram Context Encoding (RFC 5234 ABNF)

context-string  = dimension *("|" dimension)
dimension       = dim-symbol value-list
dim-symbol      = TIME-SYM / SPACE-SYM / COMPANY-SYM / CULTURE-SYM /
                  OCCASION-SYM / STATE-SYM / ENV-SYM / AGENCY-SYM / CONST-SYM
value-list      = 1*emoji-value

TIME-SYM        = %x23F0     ; ⏰
SPACE-SYM       = %x1F4CD    ; 📍
COMPANY-SYM     = %x1F465    ; 👥
CULTURE-SYM     = %x1F30D    ; 🌍
OCCASION-SYM    = %x1F3AD    ; 🎭
STATE-SYM       = %x1F9E0    ; 🧠
ENV-SYM         = %x1F321    ; 🌡️
AGENCY-SYM      = %x1F537    ; 🔷
CONST-SYM       = %x1F536    ; 🔶

emoji-value     = 1*4EMOJI   ; Unicode emoji codepoints
```

### 3.2 Encoding Examples

```python
# Full context encoding
context = "⏰🌅|📍🏡|👥👶👨‍👩‍👧|🌍🇺🇸|🎭➖|🧠😊|🌡️☀️|🔷🤝|🔶○"
# Meaning: Morning, home, children+family, American, normal occasion,
#          happy state, comfortable environment, peer agency, minimal constraints

# Minimal context (only relevant dimensions)
context = "📍🏢|👥👔|🔶⚖️"
# Meaning: Office, colleagues, legal constraints

# Emergency context
context = "🎭🚨|🧠😰|🔶🚨"
# Meaning: Emergency occasion, anxious state, emergency constraints
```

### 3.3 Parser Implementation

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
    context="🎭🚨|🧠😰",
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
        context_snapshot="⏰🌆|📍🏡|👥👨‍👩‍👧|🎭➖|🧠😊",
        state={
            'conversation_summary': "Planning weekend activities for family",
            'preferences_gathered': ['outdoor', 'educational', 'accessible'],
            'constraints': ['budget: moderate', 'distance: <30km'],
        },
    ),
)
```

---

## 7. Interiora Integration

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
- Health state (`🧠🤒`) is medical information
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

## 9. Reference Implementation

### 9.1 Complete Module

```python
# File: services/vcp/context.py

"""
VCP Context Protocol Implementation

Reference implementation of VCP Context specification.
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

See `data/schemas/vcp-context.schema.json` for JSON Schema validation.

---

## Appendices

### A. Emoji Quick Reference

```
DIMENSIONS
⏰ TIME     📍 SPACE    👥 COMPANY   🌍 CULTURE   🎭 OCCASION
🧠 STATE    🌡️ ENV      🔷 AGENCY    🔶 CONSTRAINTS

TIME: 🌅🌙📅🎉⏰
SPACE: 🏡🏢🏫🏥💻🌳
COMPANY: 👤👶👨‍👩‍👧👔👮🤝
CULTURE: 🇺🇸🇬🇧🇯🇵🌍🏛️🆕
OCCASION: ➖🎂💼🚨🎪⚖️
STATE: 😊😴😰😡😢🥺
ENV: ☀️🥵🥶🌧️🌪️🔇🔥
AGENCY: 👑🤝👇💰🔐🆓
CONSTRAINTS: ○🚧⚖️💸⏰🚨
```

### B. Context-Constitution Mapping

| Context Pattern | Suggested Constitution |
|-----------------|------------------------|
| `👥👶` (children present) | `N5+F` (Nanny, max safety) |
| `📍🏢` + `👥👔` | `A3+W+P` (Ambassador, work) |
| `🎭🚨` (emergency) | Override to emergency mode |
| `🧠🥺` (vulnerable state) | `G4+V` (Godparent, vulnerable) |
| `📍🏥` (medical setting) | `R4+H+P` (Anchor, health) |
| `🎭🎪` (entertainment) | `M2` (Muse, creative) |

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-11 | Initial specification |

---

*This specification is released under CC BY 4.0. Contributions welcome.*
