"""
VCP Trust Module

Manages trust anchors for issuers and auditors.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


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

    def is_valid(self, at_time: datetime | None = None) -> bool:
        """Check if anchor is valid at the given time."""
        at_time = at_time or datetime.utcnow()
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
            valid_from=datetime.fromisoformat(data["valid_from"].rstrip("Z")),
            valid_until=datetime.fromisoformat(data["valid_until"].rstrip("Z")),
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
        now = datetime.utcnow()

        for anchor in anchors:
            if key_id and anchor.key_id != key_id:
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
        now = datetime.utcnow()

        for anchor in anchors:
            if key_id and anchor.key_id != key_id:
                continue
            if anchor.is_valid(now):
                return anchor

        return None

    def add_issuer(self, issuer_id: str, anchor: TrustAnchor) -> None:
        """Add a trusted issuer key."""
        if issuer_id not in self.issuers:
            self.issuers[issuer_id] = []
        self.issuers[issuer_id].append(anchor)

    def add_auditor(self, auditor_id: str, anchor: TrustAnchor) -> None:
        """Add a trusted auditor key."""
        if auditor_id not in self.auditors:
            self.auditors[auditor_id] = []
        self.auditors[auditor_id].append(anchor)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TrustConfig":
        """Create TrustConfig from dictionary."""
        config = cls()

        for entity_id, entity_data in data.get("trust_anchors", {}).items():
            entity_type = entity_data.get("type", "issuer")
            for key_data in entity_data.get("keys", []):
                key_data["type"] = entity_type
                anchor = TrustAnchor.from_dict(entity_id, key_data)
                if entity_type == "auditor":
                    config.add_auditor(entity_id, anchor)
                else:
                    config.add_issuer(entity_id, anchor)

        return config

    @classmethod
    def from_json(cls, json_str: str) -> "TrustConfig":
        """Create TrustConfig from JSON string."""
        return cls.from_dict(json.loads(json_str))

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
                        "valid_from": a.valid_from.isoformat() + "Z",
                        "valid_until": a.valid_until.isoformat() + "Z",
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
                        "valid_from": a.valid_from.isoformat() + "Z",
                        "valid_until": a.valid_until.isoformat() + "Z",
                    }
                    for a in anchors
                ],
            }

        return result
