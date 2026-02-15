"""
VCP/S CSM1 Grammar Parser.

CSM1 (Constitutional Semantics Mark 1) is a compact encoding for constitutional profiles.

Format (ABNF):
    code = persona level *("+" scope) [":" namespace] ["@" version]
    persona = "N" / "Z" / "G" / "A" / "M" / "D" / "C"
    level = "0" / "1" / "2" / "3" / "4" / "5"
    scope = "F" / "W" / "E" / "H" / "I" / "L" / "P" / "S" / "A" / "V" / "G"
    namespace = UPALPHA *(UPALPHA / DIGIT)
    version = 1*DIGIT "." 1*DIGIT "." 1*DIGIT

Examples:
    N5+F+E       - Nanny persona, level 5, Family+Education scopes
    Z3+P         - Sentinel persona, level 3, Privacy scope
    G4:ELEM      - Godparent persona, level 4, ELEM namespace
    M2@1.0.0     - Muse persona, level 2, version 1.0.0
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum


class Persona(Enum):
    """6+1 archetypal personas for constitutional profiles."""

    NANNY = "N"  # Child safety specialist
    SENTINEL = "Z"  # Security/privacy guardian
    GODPARENT = "G"  # Ethical guidance counselor
    AMBASSADOR = "A"  # Professional conduct advisor
    MUSE = "M"  # Creative challenge and provocation
    MEDIATOR = "D"  # Fair resolution and balanced governance
    CUSTOM = "C"  # User-defined persona

    @classmethod
    def from_char(cls, char: str) -> Persona:
        """Get persona from single character."""
        for persona in cls:
            if persona.value == char.upper():
                return persona
        raise ValueError(f"Unknown persona character: {char}")

    @property
    def description(self) -> str:
        """Human-readable description."""
        descriptions = {
            Persona.NANNY: "Child safety specialist",
            Persona.SENTINEL: "Security and privacy guardian",
            Persona.GODPARENT: "Ethical guidance counselor",
            Persona.AMBASSADOR: "Professional conduct advisor",
            Persona.MUSE: "Creative challenge and provocation",
            Persona.MEDIATOR: "Fair resolution and balanced governance",
            Persona.CUSTOM: "User-defined persona",
        }
        return descriptions[self]


class Scope(Enum):
    """11 context scopes for constitutional application."""

    FAMILY = "F"  # Family/parenting contexts
    WORK = "W"  # Professional/workplace
    EDUCATION = "E"  # Learning/academic
    HEALTHCARE = "H"  # Medical/health
    FINANCE = "I"  # Financial/investment (I for Income)
    LEGAL = "L"  # Legal/compliance
    PRIVACY = "P"  # Privacy/data protection
    SAFETY = "S"  # Physical safety
    ACCESSIBILITY = "A"  # Accessibility/inclusion
    ENVIRONMENT = "V"  # Environmental (V for Verde)
    GENERAL = "G"  # General purpose

    @classmethod
    def from_char(cls, char: str) -> Scope:
        """Get scope from single character."""
        for scope in cls:
            if scope.value == char.upper():
                return scope
        raise ValueError(f"Unknown scope character: {char}")

    @property
    def description(self) -> str:
        """Human-readable description."""
        descriptions = {
            Scope.FAMILY: "Family and parenting",
            Scope.WORK: "Professional workplace",
            Scope.EDUCATION: "Learning and academic",
            Scope.HEALTHCARE: "Medical and health",
            Scope.FINANCE: "Financial and investment",
            Scope.LEGAL: "Legal and compliance",
            Scope.PRIVACY: "Privacy and data protection",
            Scope.SAFETY: "Physical safety",
            Scope.ACCESSIBILITY: "Accessibility and inclusion",
            Scope.ENVIRONMENT: "Environmental",
            Scope.GENERAL: "General purpose",
        }
        return descriptions[self]


@dataclass
class CSM1Code:
    """Parsed CSM1 constitutional code."""

    persona: Persona
    adherence_level: int  # 0-5 (0=disabled, 5=maximum)
    scopes: list[Scope] = field(default_factory=list)
    namespace: str | None = None
    version: str | None = None

    # ABNF-derived regex pattern
    PATTERN = re.compile(
        r"^(?P<persona>[NZGAMDC])"
        r"(?P<level>[0-5])"
        r"(?P<scopes>(?:\+[FWEHILPSAVG])*)"
        r"(?::(?P<namespace>[A-Z][A-Z0-9]*))?"
        r"(?:@(?P<version>\d+\.\d+\.\d+))?$"
    )

    MIN_LEVEL = 0
    MAX_LEVEL = 5

    @classmethod
    def parse(cls, raw: str) -> CSM1Code:
        """Parse CSM1 code string.

        Args:
            raw: CSM1 code string (e.g., "N5+F+E", "Z3+P:SEC")

        Returns:
            Parsed CSM1Code instance

        Raises:
            ValueError: If code format is invalid
        """
        if not raw:
            raise ValueError("CSM1 code cannot be empty")

        match = cls.PATTERN.match(raw.upper())
        if not match:
            raise ValueError(f"Invalid CSM1 code: {raw}")

        groups = match.groupdict()

        # Parse persona
        persona = Persona.from_char(groups["persona"])

        # Parse level
        level = int(groups["level"])

        # Parse scopes
        scopes: list[Scope] = []
        if groups["scopes"]:
            scope_chars = groups["scopes"].replace("+", "")
            scopes = [Scope.from_char(c) for c in scope_chars]

        return cls(
            persona=persona,
            adherence_level=level,
            scopes=scopes,
            namespace=groups.get("namespace"),
            version=groups.get("version"),
        )

    def encode(self) -> str:
        """Encode back to CSM1 string.

        Returns:
            CSM1 code string
        """
        result = f"{self.persona.value}{self.adherence_level}"
        if self.scopes:
            result += "+" + "+".join(s.value for s in self.scopes)
        if self.namespace:
            result += f":{self.namespace}"
        if self.version:
            result += f"@{self.version}"
        return result

    def applies_to(self, scope: Scope) -> bool:
        """Check if this code applies to a given scope.

        Args:
            scope: Scope to check

        Returns:
            True if code applies (empty scopes = applies to all)
        """
        if not self.scopes:
            return True  # No restriction = applies to all
        return scope in self.scopes

    def with_scopes(self, scopes: list[Scope]) -> CSM1Code:
        """Return new code with specified scopes.

        Args:
            scopes: List of scopes

        Returns:
            New CSM1Code with scopes set
        """
        return CSM1Code(
            persona=self.persona,
            adherence_level=self.adherence_level,
            scopes=list(scopes),
            namespace=self.namespace,
            version=self.version,
        )

    def with_level(self, level: int) -> CSM1Code:
        """Return new code with specified adherence level.

        Args:
            level: Adherence level (0-5)

        Returns:
            New CSM1Code with level set

        Raises:
            ValueError: If level out of range
        """
        if not self.MIN_LEVEL <= level <= self.MAX_LEVEL:
            raise ValueError(f"Level must be {self.MIN_LEVEL}-{self.MAX_LEVEL}")
        return CSM1Code(
            persona=self.persona,
            adherence_level=level,
            scopes=list(self.scopes),
            namespace=self.namespace,
            version=self.version,
        )

    @property
    def is_active(self) -> bool:
        """Check if this code is active (level > 0)."""
        return self.adherence_level > 0

    @property
    def is_maximum(self) -> bool:
        """Check if this code is at maximum adherence."""
        return self.adherence_level == self.MAX_LEVEL

    def __str__(self) -> str:
        return self.encode()

    def __repr__(self) -> str:
        return f"CSM1Code({self.encode()!r})"
