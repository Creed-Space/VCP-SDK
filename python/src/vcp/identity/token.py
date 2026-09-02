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
import unicodedata
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Self


MAX_RAW_TOKEN_LENGTH = 4096
MAX_IDENTITY_URI_LENGTH = 518
_DOMAIN_LABEL_PATTERN = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?$")
_NUMERIC_VERSION_PATTERN = re.compile(
    r"(?P<prefix>[\^~]?)(?P<major>[0-9]{1,5})\."
    r"(?P<minor>[0-9]{1,5})\.(?P<patch>[0-9]{1,5})"
    r"(?P<prerelease>-[a-zA-Z0-9.-]+)?"
)


def _glob_match(parts: tuple[str, ...], segments: tuple[str, ...]) -> bool:
    """Match dotted glob ``parts`` against ``segments``.

    ``*`` matches exactly one segment; ``**`` matches zero or more segments
    and may appear more than once in a pattern.
    """
    if not parts:
        return not segments
    head, rest = parts[0], parts[1:]
    if head == "**":
        return any(_glob_match(rest, segments[i:]) for i in range(len(segments) + 1))
    if not segments:
        return False
    if head != "*" and head != segments[0]:
        return False
    return _glob_match(rest, segments[1:])


def _canonical_version(version: str) -> str:
    """Normalize numeric selectors while preserving alias selectors."""
    match = _NUMERIC_VERSION_PATTERN.fullmatch(version)
    if match is None:
        return version
    return (
        f"{match['prefix']}{int(match['major'])}."
        f"{int(match['minor'])}.{int(match['patch'])}"
        f"{(match['prerelease'] or '').lower()}"
    )


def _validate_registry_domain(registry: object) -> str:
    """Return a normalized DNS registry name or fail closed."""
    if not isinstance(registry, str) or not registry or len(registry) > 253:
        raise ValueError("registry must be a valid domain name")
    labels = registry.split(".")
    if not any(character.isascii() and character.isalpha() for character in registry) or any(
        _DOMAIN_LABEL_PATTERN.fullmatch(label) is None for label in labels
    ):
        raise ValueError("registry must be a valid domain name")
    return registry.lower()


def canonicalize_token(raw: str) -> str:
    """Return the validated canonical identity-token representation.

    Canonicalization is intentionally separate from strict parsing. It applies
    Unicode NFKC, removes whitespace, lowercases the token path and version,
    collapses dot runs, normalizes numeric semantic-version components, and
    preserves the required uppercase namespace suffix.
    """
    if not isinstance(raw, str) or not raw:
        raise ValueError("Token cannot be empty")
    if len(raw) > MAX_RAW_TOKEN_LENGTH:
        raise ValueError(f"Raw token exceeds max length {MAX_RAW_TOKEN_LENGTH}")
    normalized = unicodedata.normalize("NFKC", raw).strip()
    normalized = re.sub(r"\s+", "", normalized)

    namespace: str | None = None
    if ":" in normalized:
        normalized, namespace = normalized.rsplit(":", 1)
        namespace = namespace.upper()

    version: str | None = None
    if "@" in normalized:
        normalized, version = normalized.rsplit("@", 1)
        version = version.lower()
        prefix = version[:1] if version.startswith(("^", "~")) else ""
        numeric = version[1:] if prefix else version
        match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)(-[a-z0-9.-]+)?", numeric)
        if match:
            major, minor, patch, prerelease = match.groups()
            version = f"{prefix}{int(major)}.{int(minor)}.{int(patch)}{prerelease or ''}"

    path = re.sub(r"\.+", ".", normalized.lower()).strip(".")
    candidate = path
    if version is not None:
        candidate += f"@{version}"
    if namespace is not None:
        candidate += f":{namespace}"
    return Token.parse(candidate).full


def uri_to_canonical(uri: str) -> str:
    """Convert a strict VCP/I URI to its canonical token representation."""
    return Token.from_uri(uri).full


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
    VERSION_PATTERN = re.compile(
        r"^(?:[\^~]?[0-9]{1,5}\.[0-9]{1,5}\.[0-9]{1,5}"
        r"(?:-[a-zA-Z0-9.-]+)?|latest|canary)$"
    )
    NAMESPACE_PATTERN = re.compile(r"^[A-Z][A-Z0-9]{0,31}$")

    # Full token pattern for parsing
    TOKEN_PATTERN = re.compile(
        r"^(?P<path>[a-z][a-z0-9-]*(?:\.[a-z][a-z0-9-]*){2,})"
        r"(?:@(?P<version>(?:[\^~]?[0-9]{1,5}\.[0-9]{1,5}\.[0-9]{1,5}"
        r"(?:-[a-zA-Z0-9.-]+)?|latest|canary)))?"
        r"(?::(?P<namespace>[A-Z][A-Z0-9]{0,31}))?$"
    )

    MAX_LENGTH = 256
    MAX_SEGMENT = 32
    MIN_SEGMENTS = 3
    MAX_SEGMENTS = 10

    def __post_init__(self) -> None:
        """Validate token after construction."""
        if len(self.segments) < self.MIN_SEGMENTS:
            raise ValueError(
                f"Token requires at least {self.MIN_SEGMENTS} segments, got {len(self.segments)}"
            )
        if len(self.segments) > self.MAX_SEGMENTS:
            raise ValueError(
                f"Token exceeds maximum {self.MAX_SEGMENTS} segments, got {len(self.segments)}"
            )
        for index, segment in enumerate(self.segments, start=1):
            if not self.SEGMENT_PATTERN.fullmatch(segment):
                raise ValueError(f"Invalid segment {index}: {segment}")
            if len(segment) > self.MAX_SEGMENT:
                raise ValueError(
                    f"Segment {index} exceeds max length {self.MAX_SEGMENT}: {segment}"
                )
        if self.version is not None and not self.VERSION_PATTERN.fullmatch(self.version):
            raise ValueError(f"Invalid version format: {self.version}")
        if self.version is not None:
            object.__setattr__(self, "version", _canonical_version(self.version))
        if self.namespace is not None and not self.NAMESPACE_PATTERN.fullmatch(self.namespace):
            raise ValueError(f"Invalid namespace format: {self.namespace}")
        if len(self.full) > self.MAX_LENGTH:
            raise ValueError(f"Token exceeds max length {self.MAX_LENGTH}: {len(self.full)}")

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
        if not isinstance(raw, str) or not raw:
            raise ValueError("Token cannot be empty")

        if len(raw) > cls.MAX_LENGTH:
            raise ValueError(f"Token exceeds max length {cls.MAX_LENGTH}: {len(raw)}")

        match = cls.TOKEN_PATTERN.fullmatch(raw)
        if not match:
            raise ValueError(f"Invalid VCP/I token format: {raw}")

        groups = match.groupdict()
        path = groups["path"]
        segments = tuple(path.split("."))

        # Validate segment count
        if len(segments) < cls.MIN_SEGMENTS:
            raise ValueError(
                f"Token requires at least {cls.MIN_SEGMENTS} segments, got {len(segments)}"
            )

        # Validate individual segment lengths
        for i, seg in enumerate(segments):
            if len(seg) > cls.MAX_SEGMENT:
                raise ValueError(f"Segment {i + 1} exceeds max length {cls.MAX_SEGMENT}: {seg}")

        return cls(
            segments=segments,
            version=groups.get("version"),
            namespace=groups.get("namespace"),
        )

    @classmethod
    def canonicalize(cls, raw: str) -> str:
        """Canonicalize and validate a potentially non-canonical token."""
        return canonicalize_token(raw)

    @classmethod
    def from_uri(cls, raw: str) -> Self:
        """Parse a bounded VCP/I URI into a validated canonical token.

        ``creed://`` requires a DNS issuer and accepts the canonical dotted
        token path or the legacy slash-separated path. ``vcp://`` carries only
        a dotted token path. Namespaces, URL decorations, percent escapes,
        non-ASCII data, and ambiguous mixed separators are rejected.
        """
        if not isinstance(raw, str) or not raw or len(raw) > MAX_IDENTITY_URI_LENGTH:
            raise ValueError(
                f"Identity URI must contain 1 to {MAX_IDENTITY_URI_LENGTH} ASCII characters"
            )
        if (
            not raw.isascii()
            or any(
                character.isspace() or ord(character) < 32 or ord(character) == 127
                for character in raw
            )
            or any(forbidden in raw for forbidden in ("?", "#", "%", "\\"))
        ):
            raise ValueError("Identity URI contains forbidden or non-ASCII characters")

        allow_legacy_slashes = False
        if raw.startswith("creed://"):
            rest = raw.removeprefix("creed://")
            issuer, separator, identity = rest.partition("/")
            if not separator or not issuer or not identity:
                raise ValueError("creed identity URI requires an issuer and path")
            _validate_registry_domain(issuer)
            allow_legacy_slashes = True
        elif raw.startswith("vcp://"):
            identity = raw.removeprefix("vcp://")
        else:
            raise ValueError("Identity URI scheme must be creed:// or vcp://")

        if not identity or ":" in identity:
            raise ValueError("Identity URI path is empty or contains a namespace")

        path, marker, version = identity.partition("@")
        if "/" in path:
            if (
                not allow_legacy_slashes
                or "." in path
                or path.startswith("/")
                or path.endswith("/")
                or "//" in path
            ):
                raise ValueError("Identity URI has an ambiguous slash path")
            path = path.replace("/", ".")
        candidate = path + (f"@{version}" if marker else "")
        return cls.parse(candidate)

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
        return f"creed://{_validate_registry_domain(registry)}/{self.canonical}{version_part}"

    def with_version(self, version: str) -> Token:
        """Return new token with specified version.

        Args:
            version: Semantic version string (X.Y.Z)

        Returns:
            New Token with version set
        """
        if not self.VERSION_PATTERN.fullmatch(version):
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
        if not self.NAMESPACE_PATTERN.fullmatch(namespace):
            raise ValueError(f"Invalid namespace format: {namespace}")

        return Token(
            segments=self.segments,
            version=self.version,
            namespace=namespace,
        )

    @property
    def version_constraint(self) -> str:
        """Classify the token's version selector using schema terminology."""
        if self.version is None:
            return "none"
        if self.version in {"latest", "canary"}:
            return "alias"
        if self.version.startswith("^"):
            return "compatible"
        if self.version.startswith("~"):
            return "approximate"
        return "exact"

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
        if not self.SEGMENT_PATTERN.fullmatch(segment):
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

        # Handle ** (match any number of segments, possibly several times)
        if "**" in parts:
            return _glob_match(tuple(parts), self.segments)

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
