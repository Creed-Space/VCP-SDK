"""
VCP/A Adaptation Layer context encoder (v3.2).

Encodes context as 13 situational dimensions + 5 personal-state dimensions
per CSM1 / VCP v3.2 and VEP-0004.

Situational dimensions (positions 1-13):
    1.  TIME          ⏰
    2.  SPACE         📍
    3.  COMPANY       👥
    4.  CULTURE       🌍   (communication style, not nationality)
    5.  OCCASION      🎭
    6.  ENVIRONMENT   🌡️
    7.  AGENCY        🔷
    8.  CONSTRAINTS   🔶
    9.  SYSTEM_CONTEXT 📡
    10. EMBODIMENT    🧍   (VEP-0004)
    11. PROXIMITY     ↔️   (VEP-0004)
    12. RELATIONSHIP  🪢   (VEP-0004; compound "{tie}:{function}")
    13. FORMALITY     🎩   (VEP-0004)

Personal-state dimensions (R-line, v3.1+; positions 1-5 with optional 1-5 intensity):
    1. COGNITIVE_STATE   🧠
    2. EMOTIONAL_TONE    💭
    3. ENERGY_LEVEL      🔋
    4. PERCEIVED_URGENCY ⚡
    5. BODY_SIGNALS      🩺

Wire format:
    <situational>‖<personal>
where <situational> is pipe-separated symbol+value groups and <personal> is
pipe-separated symbol+name[:intensity] groups. The U+2016 DOUBLE VERTICAL
LINE ("‖") separates the two bands. The personal band and its separator
are omitted if no personal dimensions are set.

Example:
    ⏰🌅|📍🏢|👥👔|🎭💼|🧍✋|↔️🤏|🪢colleague:professional|🎩💼‖🧠focused:4|💭calm:5

Conformance levels (per VEP-0004):
    VCP-Minimal  — 9 situational only (positions 1-9)
    VCP-Standard — 9 situational + 5 personal (14 dims total)
    VCP-Extended — 13 situational + 5 personal (18 dims total, incl. VEP-0004)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from ..metrics import track_duration, vcp_context_encode_duration_seconds, vcp_context_encodes_total

# ────────────────────────────────────────────────────────────────────────────
# Wire-format constants
# ────────────────────────────────────────────────────────────────────────────

PERSONAL_SEPARATOR = "\u2016"  # ‖  U+2016 DOUBLE VERTICAL LINE
DIM_SEPARATOR = "|"
INTENSITY_SEPARATOR = ":"


# ────────────────────────────────────────────────────────────────────────────
# Situational dimensions (positions 1-13)
# ────────────────────────────────────────────────────────────────────────────

class SituationalDimension(Enum):
    """13 situational context dimensions for VCP/A encoding (VCP v3.2)."""

    TIME = (
        "time",
        "⏰",
        1,
        {"🌅": "morning", "☀️": "midday", "🌆": "evening", "🌙": "night"},
    )
    SPACE = (
        "space",
        "📍",
        2,
        {"🏡": "home", "🏢": "office", "🏫": "school", "🏥": "hospital", "🚗": "transit"},
    )
    COMPANY = (
        "company",
        "👥",
        3,
        {
            "👤": "alone",
            "👶": "children",
            "👔": "colleagues",
            "👨‍👩‍👧": "family",
            "👥": "strangers",
        },
    )
    CULTURE = (
        "culture",
        "🌍",
        4,
        # Communication styles per CSM1 / VCP v3.2 — NOT nationalities.
        {
            "🔇": "high_context",
            "📢": "low_context",
            "🎩": "formal",
            "😎": "casual",
            "🌐": "mixed",
        },
    )
    OCCASION = (
        "occasion",
        "🎭",
        5,
        {
            "➖": "normal",
            "🎂": "celebration",
            "😢": "mourning",
            "🚨": "emergency",
            "💼": "business",
        },
    )
    ENVIRONMENT = (
        "environment",
        "🌡️",
        6,
        {"☀️": "comfortable", "🥵": "hot", "🥶": "cold", "🔇": "quiet", "🔊": "noisy"},
    )
    AGENCY = (
        "agency",
        "🔷",
        7,
        {"👑": "leader", "🤝": "peer", "📋": "subordinate", "🔐": "limited"},
    )
    CONSTRAINTS = (
        "constraints",
        "🔶",
        8,
        {"○": "minimal", "⚖️": "legal", "💸": "economic", "⏱️": "time"},
    )
    SYSTEM_CONTEXT = (
        "system_context",
        "📡",
        9,
        {
            "🟢": "online",
            "🟡": "degraded",
            "🔴": "offline",
            "🔒": "sandboxed",
            "🧪": "testing",
        },
    )
    # ── VEP-0004 (positions 10-13) ─────────────────────────────────────────
    EMBODIMENT = (
        "embodiment",
        "🧍",
        10,
        {
            "🪑": "stationary",
            "🚶": "navigating",
            "✋": "manipulating",
            "📦": "carrying",
            "🛑": "emergency_stop",
        },
    )
    PROXIMITY = (
        "proximity",
        "↔️",
        11,
        {
            "🌐": "distant",
            "🏠": "same_room",
            "👣": "nearby",
            "🤏": "close",
            "👆": "contact",
        },
    )
    RELATIONSHIP = (
        "relationship",
        "🪢",
        12,
        # Compound grammar: "{tie}:{function}" — stored as raw string values.
        # Example values: "colleague:professional", "friend:social",
        # "family:caregiving", "stranger:service".
        dict[str, str](),
    )
    FORMALITY = (
        "formality",
        "🎩",
        13,
        {
            "😎": "casual",
            "💼": "professional",
            "🎓": "formal",
            "🏛️": "ceremonial",
        },
    )

    def __init__(self, name: str, symbol: str, position: int, values: dict[str, str]):
        self._name = name
        self._symbol = symbol
        self._position = position
        self._values = values

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def position(self) -> int:
        return self._position

    @property
    def values(self) -> dict[str, str]:
        return self._values

    @property
    def is_vep_0004(self) -> bool:
        """Whether this dimension was introduced in VEP-0004 (positions 10-13)."""
        return self._position >= 10

    @property
    def is_free_form(self) -> bool:
        """Whether this dimension accepts raw-string values (no emoji vocab)."""
        # RELATIONSHIP uses compound {tie}:{function} grammar, not an emoji table.
        return self is SituationalDimension.RELATIONSHIP

    @classmethod
    def from_name(cls, name: str) -> SituationalDimension:
        """Get dimension by name (case-insensitive)."""
        for dim in cls:
            if dim._name == name.lower():
                return dim
        raise ValueError(f"Unknown situational dimension: {name}")


# Backwards-compatible alias. Note: the v3.0 STATE dimension was removed in
# v3.1 and replaced by the personal-state R-line (see PersonalStateDimension).
# Code that imported `Dimension` for one of the surviving 8 dims continues
# to work unchanged; `Dimension.STATE` no longer exists.
Dimension = SituationalDimension


# ────────────────────────────────────────────────────────────────────────────
# Personal-state dimensions (R-line; v3.1+)
# ────────────────────────────────────────────────────────────────────────────

class PersonalStateDimension(Enum):
    """5 personal-state dimensions (VCP v3.1+ R-line).

    Note: `vcp.extensions.personal.PersonalDimension` is a separate str-enum
    used by the decay-aware PersonalSignal model. This enum is purely for
    wire-format encoding (symbol + position). The two cover the same domain
    concept but are not interchangeable; the categorical vocabularies below
    are non-normative documentation only — the wire format accepts any
    string value.
    """

    COGNITIVE_STATE = (
        "cognitive_state",
        "🧠",
        1,
        {"focused", "scattered", "contemplative", "alert", "foggy"},
    )
    EMOTIONAL_TONE = (
        "emotional_tone",
        "💭",
        2,
        {"calm", "anxious", "joyful", "frustrated", "melancholy", "neutral"},
    )
    ENERGY_LEVEL = (
        "energy_level",
        "🔋",
        3,
        {"depleted", "low", "moderate", "rested", "energized"},
    )
    PERCEIVED_URGENCY = (
        "perceived_urgency",
        "⚡",
        4,
        {"unhurried", "mild_urgency", "pressing", "critical"},
    )
    BODY_SIGNALS = (
        "body_signals",
        "🩺",
        5,
        {"neutral", "tense", "relaxed", "discomfort", "pain"},
    )

    def __init__(self, name: str, symbol: str, position: int, values: set[str]):
        self._name = name
        self._symbol = symbol
        self._position = position
        self._values = values

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def position(self) -> int:
        return self._position

    @property
    def values(self) -> set[str]:
        return self._values

    @classmethod
    def from_name(cls, name: str) -> PersonalStateDimension:
        """Get dimension by name (case-insensitive)."""
        for dim in cls:
            if dim._name == name.lower():
                return dim
        raise ValueError(f"Unknown personal dimension: {name}")

    @classmethod
    def from_symbol(cls, symbol: str) -> PersonalStateDimension | None:
        """Get dimension by its emoji symbol, or None if not found."""
        for dim in cls:
            if dim._symbol == symbol:
                return dim
        return None


@dataclass(frozen=True)
class PersonalState:
    """A single personal-state value with optional 1-5 intensity."""

    value: str
    intensity: int | None = None  # 1-5 if present; None means unspecified

    def __post_init__(self) -> None:
        if self.intensity is not None and not (1 <= self.intensity <= 5):
            raise ValueError(
                f"PersonalState intensity must be 1-5 or None, got {self.intensity}"
            )

    def encode(self) -> str:
        """Encode to wire segment (without dimension symbol)."""
        if self.intensity is None:
            return self.value
        return f"{self.value}{INTENSITY_SEPARATOR}{self.intensity}"

    @classmethod
    def decode(cls, segment: str) -> PersonalState:
        """Decode a wire segment like 'focused:4' or 'calm'."""
        if INTENSITY_SEPARATOR in segment:
            value, intensity_str = segment.rsplit(INTENSITY_SEPARATOR, 1)
            try:
                intensity = int(intensity_str)
            except ValueError:
                # Not an intensity — whole segment is the value (edge case).
                return cls(value=segment)
            return cls(value=value, intensity=intensity)
        return cls(value=segment)


# ────────────────────────────────────────────────────────────────────────────
# VCPContext
# ────────────────────────────────────────────────────────────────────────────

class VCPContext:
    """Encoded VCP/A context state (v3.2).

    Backwards-compat: accepts `dimensions=` as an alias for `situational=`
    in the constructor, and exposes `.dimensions` as a read-write alias for
    `.situational`. New code should use `.situational` and `.personal`.
    """

    __slots__ = ("situational", "personal")

    situational: dict[SituationalDimension, list[str]]
    personal: dict[PersonalStateDimension, PersonalState]

    def __init__(
        self,
        situational: dict[SituationalDimension, list[str]] | None = None,
        personal: dict[PersonalStateDimension, PersonalState] | None = None,
        *,
        dimensions: dict[SituationalDimension, list[str]] | None = None,
    ) -> None:
        if situational is not None and dimensions is not None:
            raise TypeError(
                "VCPContext: pass either 'situational' or the deprecated "
                "'dimensions' alias — not both."
            )
        object.__setattr__(
            self, "situational", dict(situational or dimensions or {})
        )
        object.__setattr__(self, "personal", dict(personal or {}))

    # Backwards-compat alias: older v3.0 code used `ctx.dimensions[Dimension.TIME]`
    # both for reads and for mutation. We expose a writable attribute-style alias
    # that points to the same dict as `.situational`.
    @property
    def dimensions(self) -> dict[SituationalDimension, list[str]]:
        """Backwards-compatible alias for `situational` (same dict, live)."""
        return self.situational

    @dimensions.setter
    def dimensions(self, value: dict[SituationalDimension, list[str]]) -> None:
        object.__setattr__(self, "situational", dict(value))

    # ── Wire format ────────────────────────────────────────────────────────
    def encode(self) -> str:
        """Encode to wire format.

        Format:
            <situational>‖<personal>
        Situational is `symbol+values` per dim, pipe-separated. Personal is
        `symbol+value[:intensity]` per dim, pipe-separated. The ‖ separator
        and personal band are omitted when no personal dims are set.
        """
        sit_parts: list[str] = []
        for dim in SituationalDimension:
            if dim in self.situational and self.situational[dim]:
                values = "".join(self.situational[dim])
                sit_parts.append(f"{dim.symbol}{values}")
        situational = DIM_SEPARATOR.join(sit_parts)

        if not self.personal:
            return situational

        per_parts: list[str] = []
        for pdim in PersonalStateDimension:
            if pdim in self.personal:
                state = self.personal[pdim]
                per_parts.append(f"{pdim.symbol}{state.encode()}")
        personal = DIM_SEPARATOR.join(per_parts)

        if not situational:
            return PERSONAL_SEPARATOR + personal
        return f"{situational}{PERSONAL_SEPARATOR}{personal}"

    @classmethod
    def decode(cls, encoded: str) -> VCPContext:
        """Decode from wire format."""
        situational: dict[SituationalDimension, list[str]] = {}
        personal: dict[PersonalStateDimension, PersonalState] = {}

        if not encoded:
            return cls()

        # Split on personal-state separator ‖ first.
        if PERSONAL_SEPARATOR in encoded:
            sit_part, per_part = encoded.split(PERSONAL_SEPARATOR, 1)
        else:
            sit_part, per_part = encoded, ""

        # Decode situational band.
        for part in sit_part.split(DIM_SEPARATOR):
            if not part:
                continue
            for dim in SituationalDimension:
                if part.startswith(dim.symbol):
                    raw = part[len(dim.symbol):]
                    if not raw:
                        break
                    if dim.is_free_form:
                        # RELATIONSHIP: raw string preserved intact
                        situational[dim] = [raw]
                    else:
                        values = cls._extract_emojis(raw)
                        if values:
                            situational[dim] = values
                        else:
                            # Fallback: unknown value format, store raw.
                            situational[dim] = [raw]
                    break

        # Decode personal-state band.
        for part in per_part.split(DIM_SEPARATOR):
            if not part:
                continue
            for pdim in PersonalStateDimension:
                if part.startswith(pdim.symbol):
                    raw = part[len(pdim.symbol):]
                    if raw:
                        personal[pdim] = PersonalState.decode(raw)
                    break

        return cls(situational=situational, personal=personal)

    @staticmethod
    def _extract_emojis(s: str) -> list[str]:
        """Extract individual emojis from a string.

        Handles multi-codepoint sequences (ZWJ families, variation selectors).
        """
        import re

        emoji_pattern = re.compile(
            r"[\U0001F300-\U0001F9FF]"  # Most emojis
            r"|[\U0001F600-\U0001F64F]"  # Emoticons
            r"|[\U0001F680-\U0001F6FF]"  # Transport
            r"|[\U0001F1E0-\U0001F1FF]"  # Flags
            r"|[\u2600-\u26FF]"  # Misc symbols
            r"|[\u2700-\u27BF]"  # Dingbats
            r"|[\u25A0-\u25FF]"  # Geometric shapes
            r"|\u2B50"  # Star
            r"|\u274C"  # Cross mark
            r"|\u2139"  # Info
            r"|\u25CB"  # Circle
            r"|(?:[\U0001F468-\U0001F469][\u200D]?)+[\U0001F466-\U0001F469]?"
        )
        return emoji_pattern.findall(s)

    # ── JSON ───────────────────────────────────────────────────────────────
    def to_json(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict.

        Shape:
            {
              "situational": {"time": ["🌅"], ...},
              "personal":    {"cognitive_state": {"value": "focused", "intensity": 4}, ...}
            }
        """
        out: dict[str, Any] = {
            "situational": {
                dim._name: self.situational.get(dim, []) for dim in SituationalDimension
            },
            "personal": {
                pdim._name: {
                    "value": self.personal[pdim].value,
                    "intensity": self.personal[pdim].intensity,
                }
                for pdim in PersonalStateDimension
                if pdim in self.personal
            },
        }
        return out

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> VCPContext:
        """Create from JSON dict.

        Accepts either the v3.2 nested shape `{situational: {...}, personal: {...}}`
        or the legacy flat shape `{"time": [...], "space": [...], ...}`.
        """
        situational: dict[SituationalDimension, list[str]] = {}
        personal: dict[PersonalStateDimension, PersonalState] = {}

        sit_src: dict[str, Any]
        per_src: dict[str, Any]

        if "situational" in data or "personal" in data:
            sit_src = data.get("situational", {}) or {}
            per_src = data.get("personal", {}) or {}
        else:
            # Legacy flat shape — everything is situational.
            sit_src = data
            per_src = {}

        for dim in SituationalDimension:
            key = dim._name
            if key in sit_src and sit_src[key]:
                values = sit_src[key] if isinstance(sit_src[key], list) else [sit_src[key]]
                situational[dim] = list(values)

        for pdim in PersonalStateDimension:
            key = pdim._name
            if key in per_src and per_src[key]:
                entry = per_src[key]
                if isinstance(entry, str):
                    personal[pdim] = PersonalState.decode(entry)
                elif isinstance(entry, dict):
                    personal[pdim] = PersonalState(
                        value=entry["value"],
                        intensity=entry.get("intensity"),
                    )

        return cls(situational=situational, personal=personal)

    # ── Accessors ──────────────────────────────────────────────────────────
    def get(self, dimension: SituationalDimension) -> list[str]:
        """Get values for a situational dimension."""
        return self.situational.get(dimension, [])

    def get_personal(self, dimension: PersonalStateDimension) -> PersonalState | None:
        """Get value for a personal-state dimension."""
        return self.personal.get(dimension)

    def set(
        self, dimension: SituationalDimension, values: list[str]
    ) -> VCPContext:
        """Return new context with situational dimension values set."""
        new_sit = dict(self.situational)
        new_sit[dimension] = list(values)
        return VCPContext(situational=new_sit, personal=dict(self.personal))

    def set_personal(
        self,
        dimension: PersonalStateDimension,
        value: str,
        intensity: int | None = None,
    ) -> VCPContext:
        """Return new context with personal-state dimension set."""
        new_per = dict(self.personal)
        new_per[dimension] = PersonalState(value=value, intensity=intensity)
        return VCPContext(situational=dict(self.situational), personal=new_per)

    def has(self, dimension: SituationalDimension | PersonalStateDimension) -> bool:
        """Check if dimension has any value set."""
        if isinstance(dimension, SituationalDimension):
            return bool(self.situational.get(dimension))
        return dimension in self.personal

    # ── Conformance ────────────────────────────────────────────────────────
    def conformance_level(self) -> str:
        """Classify this context by VCP conformance level.

        Returns one of:
            "VCP-Minimal"  — only core 9 situational (positions 1-9)
            "VCP-Standard" — core 9 + any personal dims (no VEP-0004)
            "VCP-Extended" — includes at least one VEP-0004 dim (positions 10-13)
        """
        uses_vep_0004 = any(d.is_vep_0004 for d in self.situational)
        if uses_vep_0004:
            return "VCP-Extended"
        if self.personal:
            return "VCP-Standard"
        return "VCP-Minimal"

    # ── Dunders ────────────────────────────────────────────────────────────
    def __bool__(self) -> bool:
        return any(self.situational.values()) or bool(self.personal)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, VCPContext):
            return NotImplemented
        return self.situational == other.situational and self.personal == other.personal

    def __hash__(self) -> int:  # noqa: D401
        # Contexts aren't ordinarily hashable because they hold lists/dicts,
        # but override here to mirror the frozen-style equality. Use encode()
        # output as the hash basis.
        return hash(self.encode())


# ────────────────────────────────────────────────────────────────────────────
# ContextEncoder
# ────────────────────────────────────────────────────────────────────────────

class ContextEncoder:
    """Build VCP/A contexts from keyword inputs.

    Situational dim kwargs accept either the emoji (pass-through) or the
    human-readable value name (looked up in the dimension's emoji table).
    RELATIONSHIP accepts the raw compound `{tie}:{function}` string.
    Personal-state kwargs accept a string value and optional intensity.
    """

    def encode(
        self,
        # ── Core 9 situational ────────────────────────────────────────────
        time: str | None = None,
        space: str | None = None,
        company: list[str] | str | None = None,
        culture: str | None = None,
        occasion: str | None = None,
        environment: str | None = None,
        agency: str | None = None,
        constraints: list[str] | str | None = None,
        system_context: str | None = None,
        # ── VEP-0004 (positions 10-13) ────────────────────────────────────
        embodiment: str | None = None,
        proximity: str | None = None,
        relationship: str | None = None,  # raw "{tie}:{function}"
        formality: str | None = None,
        # ── Personal-state (R-line) ───────────────────────────────────────
        cognitive_state: tuple[str, int] | str | None = None,
        emotional_tone: tuple[str, int] | str | None = None,
        energy_level: tuple[str, int] | str | None = None,
        perceived_urgency: tuple[str, int] | str | None = None,
        body_signals: tuple[str, int] | str | None = None,
    ) -> VCPContext:
        """Build a VCPContext from keyword inputs.

        Each personal-state kwarg may be either a bare string ("focused") or
        a (value, intensity) tuple ("focused", 4).
        """
        vcp_context_encodes_total.inc()
        with track_duration(vcp_context_encode_duration_seconds):
            situational: dict[SituationalDimension, list[str]] = {}
            personal: dict[PersonalStateDimension, PersonalState] = {}

            sit_map = [
                (SituationalDimension.TIME, time),
                (SituationalDimension.SPACE, space),
                (SituationalDimension.COMPANY, company),
                (SituationalDimension.CULTURE, culture),
                (SituationalDimension.OCCASION, occasion),
                (SituationalDimension.ENVIRONMENT, environment),
                (SituationalDimension.AGENCY, agency),
                (SituationalDimension.CONSTRAINTS, constraints),
                (SituationalDimension.SYSTEM_CONTEXT, system_context),
                (SituationalDimension.EMBODIMENT, embodiment),
                (SituationalDimension.PROXIMITY, proximity),
                (SituationalDimension.RELATIONSHIP, relationship),
                (SituationalDimension.FORMALITY, formality),
            ]

            for dim, value in sit_map:
                if value is None:
                    continue
                if dim.is_free_form:
                    # RELATIONSHIP: pass through as-is
                    if isinstance(value, str):
                        situational[dim] = [value]
                    continue
                if isinstance(value, str):
                    emoji = self._lookup(dim, value)
                    if emoji:
                        situational[dim] = [emoji]
                elif isinstance(value, list):
                    emojis = [self._lookup(dim, v) for v in value]
                    filtered = [e for e in emojis if e]
                    if filtered:
                        situational[dim] = filtered

            per_map = [
                (PersonalStateDimension.COGNITIVE_STATE, cognitive_state),
                (PersonalStateDimension.EMOTIONAL_TONE, emotional_tone),
                (PersonalStateDimension.ENERGY_LEVEL, energy_level),
                (PersonalStateDimension.PERCEIVED_URGENCY, perceived_urgency),
                (PersonalStateDimension.BODY_SIGNALS, body_signals),
            ]

            for pdim, raw in per_map:
                if raw is None:
                    continue
                if isinstance(raw, tuple):
                    val, intensity = raw
                    personal[pdim] = PersonalState(value=val, intensity=intensity)
                elif isinstance(raw, str):
                    personal[pdim] = PersonalState.decode(raw)

            return VCPContext(situational=situational, personal=personal)

    def _lookup(self, dim: SituationalDimension, value: str) -> str | None:
        """Resolve a value to its emoji representation.

        Accepts either the emoji itself (pass-through) or the value name.
        Returns the emoji or None if unknown.
        """
        if not value:
            return None
        # Pass-through: already an emoji registered in the dim's table.
        if value in dim.values:
            return value
        # Name lookup.
        value_lower = value.lower()
        for emoji, name in dim.values.items():
            if name == value_lower:
                return emoji
        return None
