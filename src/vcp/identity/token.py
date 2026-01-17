"""
VCP/I Token parsing and validation.

Token format (ABNF from spec):
    token = segment 2*("." segment) ["@" version] [":" namespace]
    segment = ALPHA *(ALPHA / DIGIT / "-")
    version = 1*DIGIT "." 1*DIGIT "." 1*DIGIT
    namespace = UPALPHA *(UPALPHA / DIGIT)

Minimum 3 segments, no maximum. The first segment is the domain,
the last is the role, and everything in between defines the path.

Examples:
    family.safe.guide                      (3 segments)
    family.safe.guide@1.2.0
    company.acme.legal.compliance          (4 segments)
    company.acme.legal.compliance:SEC
    org.example.dept.team.policy@1.0.0     (5 segments)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Self


@dataclass(frozen=True)
class Token:
    """VCP/I Token with full validation per ABNF grammar.

    Supports variable-length tokens with 3+ segments.
    For backward compatibility, domain/approach/role map to
    first/second-to-last/last segments.
    """

    segments: tuple[str, ...] = field(default_factory=tuple)
    version: str | None = None
    namespace: str | None = None

    # Segment pattern: starts with letter, then letters/digits/hyphens
    SEGMENT_PATTERN = re.compile(r"^[a-z][a-z0-9-]*$")
    VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")
    NAMESPACE_PATTERN = re.compile(r"^[A-Z][A-Z0-9]*$")

    # Full token pattern for parsing
    TOKEN_PATTERN = re.compile(
        r"^(?P<path>[a-z][a-z0-9-]*(?:\.[a-z][a-z0-9-]*){2,})"
        r"(?:@(?P<version>\d+\.\d+\.\d+))?"
        r"(?::(?P<namespace>[A-Z][A-Z0-9]*))?$"
    )

    MAX_LENGTH = 256
    MAX_SEGMENT = 32
    MIN_SEGMENTS = 3
    MAX_SEGMENTS = 10

    def __post_init__(self) -> None:
        """Validate token after construction."""
        if len(self.segments) < self.MIN_SEGMENTS:
            raise ValueError(f"Token requires at least {self.MIN_SEGMENTS} segments, got {len(self.segments)}")
        if len(self.segments) > self.MAX_SEGMENTS:
            raise ValueError(f"Token exceeds maximum {self.MAX_SEGMENTS} segments, got {len(self.segments)}")

    @classmethod
    def parse(cls, raw: str) -> Self:
        """Parse and validate a VCP/I token string.

        Args:
            raw: Token string in format seg1.seg2.seg3[.segN...][@version][:namespace]

        Returns:
            Validated Token instance

        Raises:
            ValueError: If token format is invalid
        """
        if not raw:
            raise ValueError("Token cannot be empty")

        if len(raw) > cls.MAX_LENGTH:
            raise ValueError(f"Token exceeds max length {cls.MAX_LENGTH}: {len(raw)}")

        match = cls.TOKEN_PATTERN.match(raw)
        if not match:
            raise ValueError(f"Invalid VCP/I token format: {raw}")

        groups = match.groupdict()
        path = groups["path"]
        segments = tuple(path.split("."))

        # Validate segment count
        if len(segments) < cls.MIN_SEGMENTS:
            raise ValueError(f"Token requires at least {cls.MIN_SEGMENTS} segments, got {len(segments)}")

        # Validate individual segment lengths
        for i, seg in enumerate(segments):
            if len(seg) > cls.MAX_SEGMENT:
                raise ValueError(f"Segment {i + 1} exceeds max length {cls.MAX_SEGMENT}: {seg}")

        return cls(
            segments=segments,
            version=groups.get("version"),
            namespace=groups.get("namespace"),
        )

    # Backward compatibility properties

    @property
    def domain(self) -> str:
        """First segment (domain/category)."""
        return self.segments[0]

    @property
    def approach(self) -> str:
        """Second-to-last segment (approach/method)."""
        return self.segments[-2]

    @property
    def role(self) -> str:
        """Last segment (role/function)."""
        return self.segments[-1]

    @property
    def path(self) -> tuple[str, ...]:
        """Middle segments between domain and role (may be empty for 3-segment tokens)."""
        if len(self.segments) <= 3:
            return ()
        return self.segments[1:-2]

    @property
    def canonical(self) -> str:
        """Canonical form: all segments joined (no version/namespace)."""
        return ".".join(self.segments)

    @property
    def full(self) -> str:
        """Full form with version and namespace if present."""
        result = self.canonical
        if self.version:
            result += f"@{self.version}"
        if self.namespace:
            result += f":{self.namespace}"
        return result

    @property
    def depth(self) -> int:
        """Number of segments in the token."""
        return len(self.segments)

    def to_uri(self, registry: str = "creed.space") -> str:
        """Convert to VCP/T bundle URI.

        Args:
            registry: Registry hostname (default: creed.space)

        Returns:
            URI in format creed://registry/canonical[@version]
        """
        version_part = f"@{self.version}" if self.version else ""
        return f"creed://{registry}/{self.canonical}{version_part}"

    def with_version(self, version: str) -> Token:
        """Return new token with specified version.

        Args:
            version: Semantic version string (X.Y.Z)

        Returns:
            New Token with version set
        """
        if not self.VERSION_PATTERN.match(version):
            raise ValueError(f"Invalid version format: {version}")

        return Token(
            segments=self.segments,
            version=version,
            namespace=self.namespace,
        )

    def with_namespace(self, namespace: str) -> Token:
        """Return new token with specified namespace.

        Args:
            namespace: Namespace identifier (uppercase alphanumeric)

        Returns:
            New Token with namespace set
        """
        if not self.NAMESPACE_PATTERN.match(namespace):
            raise ValueError(f"Invalid namespace format: {namespace}")

        return Token(
            segments=self.segments,
            version=self.version,
            namespace=namespace,
        )

    def parent(self) -> Token | None:
        """Return parent token (one segment shorter).

        Returns:
            Parent token, or None if already at minimum depth
        """
        if len(self.segments) <= self.MIN_SEGMENTS:
            return None

        return Token(
            segments=self.segments[:-1],
            version=None,  # Parent has no version
            namespace=self.namespace,
        )

    def child(self, segment: str) -> Token:
        """Return child token with additional segment.

        Args:
            segment: New segment to append

        Returns:
            New Token with additional segment
        """
        if not self.SEGMENT_PATTERN.match(segment):
            raise ValueError(f"Invalid segment format: {segment}")

        if len(self.segments) >= self.MAX_SEGMENTS:
            raise ValueError(f"Cannot add segment: max depth {self.MAX_SEGMENTS}")

        return Token(
            segments=(*self.segments, segment),
            version=None,  # Child has no version until specified
            namespace=self.namespace,
        )

    def matches_pattern(self, pattern: str) -> bool:
        """Check if token matches a glob-like pattern.

        Supports:
        - * as wildcard for any single segment
        - ** as wildcard for any number of segments

        Example:
            "family.*.guide" matches "family.safe.guide"
            "company.**" matches "company.acme.legal.compliance"

        Args:
            pattern: Pattern string with optional wildcards

        Returns:
            True if token matches pattern
        """
        parts = pattern.split(".")

        # Handle ** (match any number of segments)
        if "**" in parts:
            idx = parts.index("**")
            prefix = parts[:idx]
            suffix = parts[idx + 1 :]

            # Check prefix matches
            if len(self.segments) < len(prefix) + len(suffix):
                return False

            for i, p in enumerate(prefix):
                if p != "*" and p != self.segments[i]:
                    return False

            # Check suffix matches (from end)
            for i, p in enumerate(suffix):
                if p != "*" and p != self.segments[-(len(suffix) - i)]:
                    return False

            return True

        # Simple pattern: must match segment count
        if len(parts) != len(self.segments):
            return False

        for seg, pat in zip(self.segments, parts, strict=True):
            if pat != "*" and pat != seg:
                return False

        return True

    def is_ancestor_of(self, other: Token) -> bool:
        """Check if this token is an ancestor of another.

        Args:
            other: Token to check

        Returns:
            True if this token's segments are a prefix of other's
        """
        if len(self.segments) >= len(other.segments):
            return False

        return other.segments[: len(self.segments)] == self.segments

    def is_descendant_of(self, other: Token) -> bool:
        """Check if this token is a descendant of another.

        Args:
            other: Token to check

        Returns:
            True if other's segments are a prefix of this token's
        """
        return other.is_ancestor_of(self)

    def __str__(self) -> str:
        return self.full

    def __repr__(self) -> str:
        return f"Token({self.full!r})"

    def __hash__(self) -> int:
        return hash((self.segments, self.version, self.namespace))
