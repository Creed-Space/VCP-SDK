"""
VCP Trust Module

Manages trust anchors for issuers and auditors.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .canonicalize import parse_json_strict

_ANCHOR_TYPES = frozenset({"issuer", "auditor"})
_ANCHOR_STATES = frozenset({"active", "rotating", "retired", "compromised"})


def _parse_utc_datetime(value: Any, field_name: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be an RFC 3339 string")
    normalized = f"{value[:-1]}+00:00" if value.endswith("Z") else value
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field_name} must include a timezone")
    return parsed.astimezone(timezone.utc)


def _format_utc_datetime(value: datetime, field_name: str) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass
class TrustAnchor:
    """A trusted public key for an issuer or auditor."""

    id: str
    key_id: str
    algorithm: str
    public_key: str
    anchor_type: str  # "issuer" or "auditor"
    valid_from: datetime
    valid_until: datetime
    state: str = "active"  # active, rotating, retired, compromised

    def __post_init__(self) -> None:
        for field_name, value in (
            ("id", self.id),
            ("key_id", self.key_id),
            ("algorithm", self.algorithm),
            ("public_key", self.public_key),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string")
        if self.anchor_type not in _ANCHOR_TYPES:
            raise ValueError("anchor_type must be 'issuer' or 'auditor'")
        if self.state not in _ANCHOR_STATES:
            raise ValueError(f"Unknown trust anchor state: {self.state!r}")
        for date_field_name, date_value in (
            ("valid_from", self.valid_from),
            ("valid_until", self.valid_until),
        ):
            if (
                not isinstance(date_value, datetime)
                or date_value.tzinfo is None
                or date_value.utcoffset() is None
            ):
                raise ValueError(f"{date_field_name} must be timezone-aware")
        if self.valid_from > self.valid_until:
            raise ValueError("valid_from must not be after valid_until")

    def is_valid(self, at_time: datetime | None = None) -> bool:
        """Check if anchor is valid at the given time."""
        at_time = at_time or datetime.now(timezone.utc)
        if (
            not isinstance(at_time, datetime)
            or at_time.tzinfo is None
            or at_time.utcoffset() is None
        ):
            raise ValueError("at_time must be timezone-aware")
        if self.state not in ("active", "rotating"):
            return False
        return self.valid_from <= at_time <= self.valid_until

    @classmethod
    def from_dict(cls, entity_id: str, data: dict[str, Any]) -> "TrustAnchor":
        """Create TrustAnchor from dictionary."""
        return cls(
            id=entity_id,
            key_id=data["id"],
            algorithm=data["algorithm"],
            public_key=data["public_key"],
            anchor_type=data.get("type", "issuer"),
            valid_from=_parse_utc_datetime(data["valid_from"], "valid_from"),
            valid_until=_parse_utc_datetime(data["valid_until"], "valid_until"),
            state=data.get("state", "active"),
        )


@dataclass
class TrustConfig:
    """Configuration for trusted issuers and auditors."""

    issuers: dict[str, list[TrustAnchor]] = field(default_factory=dict)
    auditors: dict[str, list[TrustAnchor]] = field(default_factory=dict)

    def get_issuer_key(self, issuer_id: str, key_id: str | None = None) -> TrustAnchor | None:
        """
        Get trust anchor for an issuer.

        Args:
            issuer_id: Issuer identifier
            key_id: Optional specific key ID

        Returns:
            TrustAnchor if found and valid, None otherwise
        """
        anchors = self.issuers.get(issuer_id, [])
        now = datetime.now(timezone.utc)

        for anchor in anchors:
            if key_id is not None and anchor.key_id != key_id:
                continue
            if anchor.is_valid(now):
                return anchor

        return None

    def get_auditor_key(self, auditor_id: str, key_id: str | None = None) -> TrustAnchor | None:
        """
        Get trust anchor for an auditor.

        Args:
            auditor_id: Auditor identifier
            key_id: Optional specific key ID

        Returns:
            TrustAnchor if found and valid, None otherwise
        """
        anchors = self.auditors.get(auditor_id, [])
        now = datetime.now(timezone.utc)

        for anchor in anchors:
            if key_id is not None and anchor.key_id != key_id:
                continue
            if anchor.is_valid(now):
                return anchor

        return None

    def add_issuer(self, issuer_id: str, anchor: TrustAnchor) -> None:
        """Add a trusted issuer key."""
        self._validate_add(issuer_id, anchor, "issuer")
        if issuer_id not in self.issuers:
            self.issuers[issuer_id] = []
        self.issuers[issuer_id].append(anchor)

    def add_auditor(self, auditor_id: str, anchor: TrustAnchor) -> None:
        """Add a trusted auditor key."""
        self._validate_add(auditor_id, anchor, "auditor")
        if auditor_id not in self.auditors:
            self.auditors[auditor_id] = []
        self.auditors[auditor_id].append(anchor)

    def _validate_add(self, entity_id: str, anchor: TrustAnchor, expected_type: str) -> None:
        if not isinstance(entity_id, str) or not entity_id.strip():
            raise ValueError("Trust anchor entity ID must be a non-empty string")
        if not isinstance(anchor, TrustAnchor):
            raise TypeError("anchor must be a TrustAnchor")
        if anchor.id != entity_id:
            raise ValueError("Trust anchor id must match its configuration entity ID")
        if anchor.anchor_type != expected_type:
            raise ValueError(f"Cannot add a {anchor.anchor_type} anchor as an {expected_type}")
        other = self.auditors if expected_type == "issuer" else self.issuers
        if entity_id in other:
            raise ValueError(f"Trust entity {entity_id!r} cannot be both issuer and auditor")
        collection = self.issuers if expected_type == "issuer" else self.auditors
        if any(existing.key_id == anchor.key_id for existing in collection.get(entity_id, [])):
            raise ValueError(f"Duplicate trust anchor key_id: {anchor.key_id!r}")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TrustConfig":
        """Create TrustConfig from dictionary."""
        if not isinstance(data, dict):
            raise ValueError("Trust configuration must be an object")
        config = cls()

        anchors_data = data.get("trust_anchors", {})
        if not isinstance(anchors_data, dict):
            raise ValueError("trust_anchors must be an object")
        for entity_id, entity_data in anchors_data.items():
            if not isinstance(entity_id, str) or not entity_id:
                raise ValueError("Trust anchor entity IDs must be non-empty strings")
            if not isinstance(entity_data, dict):
                raise ValueError(f"Trust anchor {entity_id!r} must be an object")
            entity_type = entity_data.get("type", "issuer")
            if entity_type not in _ANCHOR_TYPES:
                raise ValueError(f"Unknown trust anchor type: {entity_type!r}")
            keys = entity_data.get("keys", [])
            if not isinstance(keys, list):
                raise ValueError(f"Trust anchor {entity_id!r} keys must be an array")
            for key_data in keys:
                if not isinstance(key_data, dict):
                    raise ValueError(f"Trust anchor {entity_id!r} key must be an object")
                anchor = TrustAnchor.from_dict(entity_id, {**key_data, "type": entity_type})
                if entity_type == "auditor":
                    config.add_auditor(entity_id, anchor)
                else:
                    config.add_issuer(entity_id, anchor)

        return config

    @classmethod
    def from_json(cls, json_str: str) -> "TrustConfig":
        """Create TrustConfig from JSON string."""
        data = parse_json_strict(json_str)
        if not isinstance(data, dict):
            raise ValueError("Trust configuration JSON must contain an object")
        return cls.from_dict(data)

    @classmethod
    def from_file(cls, path: str) -> "TrustConfig":
        """Create TrustConfig from JSON file."""
        with open(path, encoding="utf-8") as f:
            return cls.from_json(f.read())

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result: dict[str, Any] = {"trust_anchors": {}}

        for issuer_id, anchors in self.issuers.items():
            result["trust_anchors"][issuer_id] = {
                "type": "issuer",
                "keys": [
                    {
                        "id": a.key_id,
                        "algorithm": a.algorithm,
                        "public_key": a.public_key,
                        "state": a.state,
                        "valid_from": _format_utc_datetime(a.valid_from, "valid_from"),
                        "valid_until": _format_utc_datetime(a.valid_until, "valid_until"),
                    }
                    for a in anchors
                ],
            }

        for auditor_id, anchors in self.auditors.items():
            result["trust_anchors"][auditor_id] = {
                "type": "auditor",
                "keys": [
                    {
                        "id": a.key_id,
                        "algorithm": a.algorithm,
                        "public_key": a.public_key,
                        "state": a.state,
                        "valid_from": _format_utc_datetime(a.valid_from, "valid_from"),
                        "valid_until": _format_utc_datetime(a.valid_until, "valid_until"),
                    }
                    for a in anchors
                ],
            }

        return result
