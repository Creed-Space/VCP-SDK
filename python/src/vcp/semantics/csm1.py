"""
VCP/S CSM1 Grammar Parser.

CSM1 (Constitutional Safety Minicode) is a compact encoding for constitutional profiles.

Format (ABNF):
    code = persona level *("+" scope) [":" namespace] ["@" version]
    persona = "N" / "Z" / "G" / "A" / "M" / "D" / "C"
    level = "0" / "1" / "2" / "3" / "4" / "5"
    scope = "F" / "W" / "P" / "E" / "T" / "O" / "V" / "A" / "H" / "S" / "R"
    namespace = 1*8UPALPHA
    version = ( version-component "." version-component "." version-component )
            / "latest" / "canary"
    version-component = "0" / (%x31-39 *2DIGIT)

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

from ..metrics import vcp_csm1_parses_total


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

    @classmethod
    def from_wire_char(cls, char: str) -> Persona:
        """Resolve the case-sensitive single-character wire representation."""
        if len(char) != 1 or char != char.upper():
            raise ValueError(f"Persona wire code must be one uppercase character: {char!r}")
        return cls.from_char(char)

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

    @property
    def focus(self) -> str:
        """Normative persona-resolution focus text."""
        return {
            Persona.NANNY: "Child safety and family-appropriate content",
            Persona.SENTINEL: "Security, privacy, and operational safety",
            Persona.GODPARENT: "Ethical guidance and moral reasoning",
            Persona.AMBASSADOR: "Professional conduct and diplomatic communication",
            Persona.MUSE: "Creativity and artistic expression",
            Persona.MEDIATOR: "Fair resolution and balanced mediation",
            Persona.CUSTOM: "User-defined constitution",
        }[self]

    @property
    def default_adherence(self) -> int:
        """Default adherence level for this persona profile."""
        return {
            Persona.NANNY: 5,
            Persona.SENTINEL: 4,
            Persona.GODPARENT: 4,
            Persona.AMBASSADOR: 3,
            Persona.MUSE: 2,
            Persona.MEDIATOR: 3,
            Persona.CUSTOM: 3,
        }[self]


class Scope(Enum):
    """Canonical VCP/S v2.0 scopes."""

    FAMILY = "F"
    WORK = "W"
    PRIVACY = "P"
    EDUCATION = "E"
    TECHNICAL = "T"
    OFFICIAL = "O"
    VULNERABLE = "V"
    ADULT = "A"
    HEALTHCARE = "H"
    SOCIAL = "S"
    RELIGIOUS = "R"

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
            Scope.FAMILY: "Family-appropriate, child-safe",
            Scope.WORK: "Professional workplace",
            Scope.PRIVACY: "Privacy-focused, data protection",
            Scope.EDUCATION: "Educational context",
            Scope.TECHNICAL: "Developer and technical context",
            Scope.OFFICIAL: "Official and governmental context",
            Scope.VULNERABLE: "Vulnerable populations",
            Scope.ADULT: "Adult-only, mature content",
            Scope.HEALTHCARE: "Healthcare and medical context",
            Scope.SOCIAL: "Social media and community",
            Scope.RELIGIOUS: "Religious and spiritual context",
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
        r"(?P<scopes>(?:\+[FWPETOVAHSR])*)"
        r"(?::(?P<namespace>[A-Z]{1,8}))?"
        r"(?:@(?P<version>(?:(?:0|[1-9][0-9]{0,2})\."
        r"(?:0|[1-9][0-9]{0,2})\.(?:0|[1-9][0-9]{0,2})"
        r"|latest|canary)))?$"
    )

    MIN_LEVEL = 0
    MAX_LEVEL = 5
    MAX_LENGTH = 45

    def __post_init__(self) -> None:
        if not self.MIN_LEVEL <= self.adherence_level <= self.MAX_LEVEL:
            raise ValueError(f"Level must be {self.MIN_LEVEL}-{self.MAX_LEVEL}")
        if len(self.scopes) != len(set(self.scopes)):
            raise ValueError("CSM1 scopes must be unique")
        for left, right in (
            (Scope.FAMILY, Scope.ADULT),
            (Scope.VULNERABLE, Scope.ADULT),
            (Scope.HEALTHCARE, Scope.ADULT),
        ):
            if left in self.scopes and right in self.scopes:
                raise ValueError(
                    f"{left.name.title()} and {right.name.title()} scopes cannot be combined"
                )
        if self.persona is Persona.CUSTOM and not self.namespace:
            raise ValueError("Custom persona requires a namespace")
        if self.namespace is not None and not re.fullmatch(r"[A-Z]{1,8}", self.namespace):
            raise ValueError("Namespace must be 1-8 uppercase letters")
        if self.version is not None and not re.fullmatch(
            r"(?:(?:0|[1-9][0-9]{0,2})\."
            r"(?:0|[1-9][0-9]{0,2})\.(?:0|[1-9][0-9]{0,2})|latest|canary)",
            self.version,
        ):
            raise ValueError("Invalid CSM1 version")
        if len(self.encode()) > self.MAX_LENGTH:
            raise ValueError(f"CSM1 code exceeds maximum length {self.MAX_LENGTH}")

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
            vcp_csm1_parses_total.labels(status="error").inc()
            raise ValueError("CSM1 code cannot be empty")
        if len(raw) > cls.MAX_LENGTH:
            vcp_csm1_parses_total.labels(status="error").inc()
            raise ValueError(f"CSM1 code exceeds maximum length {cls.MAX_LENGTH}")

        match = cls.PATTERN.fullmatch(raw)
        if not match:
            vcp_csm1_parses_total.labels(status="error").inc()
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

        try:
            code = cls(
                persona=persona,
                adherence_level=level,
                scopes=scopes,
                namespace=groups.get("namespace"),
                version=groups.get("version"),
            )
        except ValueError:
            vcp_csm1_parses_total.labels(status="error").inc()
            raise
        vcp_csm1_parses_total.labels(status="ok").inc()
        return code

    def encode(self) -> str:
        """Encode back to CSM1 string.

        Returns:
            CSM1 code string
        """
        result = f"{self.persona.value}{self.adherence_level}"
        if self.scopes:
            result += "+" + "+".join(sorted(s.value for s in self.scopes))
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
