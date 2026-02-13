"""
VCP/A Enneagram Context Encoder.

Encodes context state across 9 dimensions using an enneagram-inspired structure.
Each dimension can hold multiple values for complex context representation.

Wire format: ⏰🌅|📍🏡|👥👶👨‍👩‍👧
JSON format: {"time": ["morning"], "space": ["home"], "company": ["children", "family"]}
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Dimension(Enum):
    """9 context dimensions for VCP/A encoding."""

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
        {"🌍": "global", "🇺🇸": "american", "🇪🇺": "european", "🇯🇵": "japanese"},
    )
    OCCASION = (
        "occasion",
        "🎭",
        5,
        {"➖": "normal", "🎂": "celebration", "😢": "mourning", "🚨": "emergency"},
    )
    STATE = (
        "state",
        "🧠",
        6,
        {"😊": "happy", "😰": "anxious", "😴": "tired", "🤔": "contemplative", "😤": "frustrated"},
    )
    ENVIRONMENT = (
        "environment",
        "🌡️",
        7,
        {"☀️": "comfortable", "🥵": "hot", "🥶": "cold", "🔇": "quiet", "🔊": "noisy"},
    )
    AGENCY = (
        "agency",
        "🔷",
        8,
        {"👑": "leader", "🤝": "peer", "📋": "subordinate", "🔐": "limited"},
    )
    CONSTRAINTS = (
        "constraints",
        "🔶",
        9,
        {"○": "minimal", "⚖️": "legal", "💸": "economic", "⏱️": "time"},
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

    @classmethod
    def from_name(cls, name: str) -> Dimension:
        """Get dimension by name."""
        for dim in cls:
            if dim._name == name.lower():
                return dim
        raise ValueError(f"Unknown dimension: {name}")


@dataclass
class VCPContext:
    """Encoded VCP/A context state."""

    dimensions: dict[Dimension, list[str]] = field(default_factory=dict)

    def encode(self) -> str:
        """Encode to wire format.

        Format: ⏰🌅|📍🏡|👥👶👨‍👩‍👧 (symbol + values, pipe-separated)

        Returns:
            Wire-format string
        """
        parts = []
        for dim in Dimension:
            if dim in self.dimensions and self.dimensions[dim]:
                values = "".join(self.dimensions[dim])
                parts.append(f"{dim.symbol}{values}")
        return "|".join(parts)

    @classmethod
    def decode(cls, encoded: str) -> VCPContext:
        """Decode from wire format.

        Args:
            encoded: Wire-format string

        Returns:
            Decoded VCPContext
        """
        dimensions: dict[Dimension, list[str]] = {}
        if not encoded:
            return cls(dimensions=dimensions)

        parts = encoded.split("|")
        for part in parts:
            if not part:
                continue

            # First character(s) might be multi-byte emoji - find matching dimension
            for dim in Dimension:
                if part.startswith(dim.symbol):
                    # Extract values after symbol
                    values_str = part[len(dim.symbol) :]
                    if values_str:
                        # Each value is an emoji - extract them
                        values = cls._extract_emojis(values_str)
                        if values:
                            dimensions[dim] = values
                    break

        return cls(dimensions=dimensions)

    @staticmethod
    def _extract_emojis(s: str) -> list[str]:
        """Extract individual emojis from a string.

        Handles multi-codepoint emojis like 👨‍👩‍👧.
        """
        import re

        # Unicode emoji pattern (simplified but covers most cases)
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
            r"|(?:[\U0001F468-\U0001F469][\u200D]?)+[\U0001F466-\U0001F469]?"  # Family
        )
        return emoji_pattern.findall(s)

    def to_json(self) -> dict[str, list[str]]:
        """Convert to JSON-serializable dict.

        Returns:
            Dict with dimension names as keys and value lists
        """
        return {dim._name: self.dimensions.get(dim, []) for dim in Dimension}

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> VCPContext:
        """Create from JSON dict.

        Args:
            data: Dict with dimension names as keys

        Returns:
            VCPContext instance
        """
        dimensions: dict[Dimension, list[str]] = {}
        for dim in Dimension:
            key = dim._name
            if key in data and data[key]:
                values = data[key] if isinstance(data[key], list) else [data[key]]
                dimensions[dim] = values
        return cls(dimensions=dimensions)

    def get(self, dimension: Dimension) -> list[str]:
        """Get values for a dimension.

        Args:
            dimension: Dimension to query

        Returns:
            List of values (empty if not set)
        """
        return self.dimensions.get(dimension, [])

    def set(self, dimension: Dimension, values: list[str]) -> VCPContext:
        """Return new context with dimension values set.

        Args:
            dimension: Dimension to set
            values: Values to set

        Returns:
            New VCPContext with updated dimension
        """
        new_dims = dict(self.dimensions)
        new_dims[dimension] = list(values)
        return VCPContext(dimensions=new_dims)

    def has(self, dimension: Dimension) -> bool:
        """Check if dimension has any values.

        Args:
            dimension: Dimension to check

        Returns:
            True if dimension has values
        """
        return bool(self.dimensions.get(dimension))

    def __bool__(self) -> bool:
        """Context is truthy if any dimension has values."""
        return any(self.dimensions.values())

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, VCPContext):
            return NotImplemented
        return self.dimensions == other.dimensions


class ContextEncoder:
    """Build VCP/A contexts from various inputs."""

    def encode(
        self,
        time: str | None = None,
        space: str | None = None,
        company: list[str] | str | None = None,
        culture: str | None = None,
        occasion: str | None = None,
        state: str | None = None,
        environment: str | None = None,
        agency: str | None = None,
        constraints: list[str] | str | None = None,
    ) -> VCPContext:
        """Encode context from keyword arguments.

        Args:
            time: Time context (morning, midday, evening, night)
            space: Space context (home, office, school, etc.)
            company: Company context (alone, children, colleagues, etc.)
            culture: Cultural context
            occasion: Occasion (normal, celebration, mourning, emergency)
            state: Mental state
            environment: Physical environment
            agency: Agency level (leader, peer, subordinate, limited)
            constraints: Active constraints

        Returns:
            Encoded VCPContext
        """
        dimensions: dict[Dimension, list[str]] = {}

        mappings = [
            (Dimension.TIME, time),
            (Dimension.SPACE, space),
            (Dimension.COMPANY, company),
            (Dimension.CULTURE, culture),
            (Dimension.OCCASION, occasion),
            (Dimension.STATE, state),
            (Dimension.ENVIRONMENT, environment),
            (Dimension.AGENCY, agency),
            (Dimension.CONSTRAINTS, constraints),
        ]

        for dim, value in mappings:
            if value:
                if isinstance(value, str):
                    emoji = self._lookup_emoji(dim, value)
                    if emoji:
                        dimensions[dim] = [emoji]
                elif isinstance(value, list):
                    emojis = [self._lookup_emoji(dim, v) for v in value]
                    dimensions[dim] = [e for e in emojis if e]

        return VCPContext(dimensions=dimensions)

    def _lookup_emoji(self, dim: Dimension, value: str) -> str | None:
        """Look up emoji for a value.

        Args:
            dim: Dimension
            value: Value name

        Returns:
            Emoji if found, None otherwise
        """
        value_lower = value.lower()
        for emoji, name in dim.values.items():
            if name == value_lower:
                return emoji
        return None
