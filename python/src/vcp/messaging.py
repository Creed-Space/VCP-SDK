"""
VCP Inter-Agent Messaging v2.0 envelope support.

Implements the message envelope format defined in the VCP Inter-Agent
Messaging Specification v2.0. Supports four message types:

- context_share: Share Enneagram context with peer agents
- constitution_announce: Announce active constitutions
- constraint_propagate: Propagate constraints to child agents
- escalation: Escalate safety concerns to parent agents

Signing follows RFC 8785 (JSON Canonicalization Scheme) with Ed25519,
consistent with VCP v2.0 manifest signing.
"""

from __future__ import annotations

import base64
import binascii
import math
import re
import secrets
import time
import uuid
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import rfc8785

# Protocol version for v2.0 messages.
PROTOCOL_VERSION = "2.0"

# Valid message types per the spec.
VALID_TYPES = frozenset(
    {
        "context_share",
        "constitution_announce",
        "constraint_propagate",
        "escalation",
    }
)

# Severities that require acknowledgment.
ACK_REQUIRED_SEVERITIES = frozenset({"critical", "emergency"})

# Valid escalation severities.
VALID_SEVERITIES = frozenset({"info", "warning", "critical", "emergency"})

_TIMESTAMP_PATTERN = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
    r"(?:\.[0-9]{1,9})?Z$"
)
_CONTENT_HASH_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")
_SIGNATURE_PATTERN = re.compile(r"^base64:[A-Za-z0-9+/]{85}[AQgw]==$")
_VERSION_PATTERN = re.compile(r"^[0-9]+\.[0-9]+(?:\.[0-9]+)?$")
_CREED_URI_PATTERN = re.compile(r"^creed://[a-z0-9.-]+/[a-zA-Z0-9._/@-]+$")
_MODEL_FAMILY_PATTERN = re.compile(r"^[a-zA-Z0-9*-]+$")
_PURPOSE_PATTERN = re.compile(r"^[a-z0-9-]+$")
_ENVIRONMENTS = frozenset({"production", "staging", "development", "testing"})


def _decode_canonical_signature(value: Any) -> bytes | None:
    """Decode one canonical standard-base64 Ed25519 signature."""
    if not isinstance(value, str) or _SIGNATURE_PATTERN.fullmatch(value) is None:
        return None
    encoded = value[7:]
    try:
        decoded = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError):
        return None
    if len(decoded) != 64 or base64.b64encode(decoded).decode("ascii") != encoded:
        return None
    return decoded


def _uuid7() -> str:
    """Generate an RFC 9562 UUIDv7 on every supported Python version."""
    unix_ms = time.time_ns() // 1_000_000
    if unix_ms >= 1 << 48:
        raise OverflowError("current time is outside the UUIDv7 timestamp range")
    value = unix_ms << 80
    value |= 0x7 << 76
    value |= secrets.randbits(12) << 64
    value |= 0b10 << 62
    value |= secrets.randbits(62)
    return str(uuid.UUID(int=value))


@dataclass
class VcpMessage:
    """VCP v2.0 message envelope.

    Attributes:
        vcp_message: Protocol version. Must be "2.0".
        type: Message type (context_share, constitution_announce,
              constraint_propagate, escalation).
        message_id: UUIDv7 identifier for deduplication.
        sender: Agent identifier (URI or opaque string).
        recipient: Target agent identifier, or "broadcast".
        timestamp: ISO 8601 UTC timestamp of message creation.
        payload: Type-specific payload object.
        signature: Optional Ed25519 signature of the canonical message.
    """

    vcp_message: str
    type: str
    message_id: str
    sender: str
    recipient: str
    timestamp: str
    payload: dict[str, Any]
    signature: str | None = None


def create_message(
    type: str,
    sender: str,
    recipient: str,
    payload: dict[str, Any],
) -> VcpMessage:
    """Create a new VCP message with auto-generated ID and timestamp.

    Args:
        type: Message type (one of VALID_TYPES).
        sender: Sender agent identifier.
        recipient: Recipient agent identifier, or "broadcast".
        payload: Type-specific payload dict.

    Returns:
        A new VcpMessage with generated message_id and timestamp.
    """
    return VcpMessage(
        vcp_message=PROTOCOL_VERSION,
        type=type,
        message_id=_uuid7(),
        sender=sender,
        recipient=recipient,
        timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        payload=deepcopy(payload),
    )


def validate_message(msg: VcpMessage) -> list[str]:
    """Validate a message against the v2.0 spec.

    Returns a list of error strings. An empty list means the message is valid.

    Args:
        msg: The VcpMessage to validate.

    Returns:
        List of validation error descriptions.
    """
    if not isinstance(msg, VcpMessage):
        raise TypeError("msg must be a VcpMessage")
    errors: list[str] = []

    # vcp_message version check.
    if not isinstance(msg.vcp_message, str) or msg.vcp_message != PROTOCOL_VERSION:
        errors.append(f"vcp_message must be '{PROTOCOL_VERSION}', got '{msg.vcp_message}'")

    # Type check.
    if not isinstance(msg.type, str) or not msg.type:
        errors.append("type is required")
    elif msg.type not in VALID_TYPES:
        errors.append(f"type must be one of {sorted(VALID_TYPES)}, got '{msg.type}'")

    # message_id format (UUID).
    if not isinstance(msg.message_id, str) or not msg.message_id:
        errors.append("message_id is required")
    else:
        try:
            parsed_id = uuid.UUID(msg.message_id)
        except (ValueError, AttributeError):
            parsed_id = None
        if (
            parsed_id is None
            or parsed_id.version != 7
            or str(parsed_id) != msg.message_id
        ):
            errors.append(f"message_id is not a valid UUIDv7: '{msg.message_id}'")

    # sender must be non-empty.
    if not isinstance(msg.sender, str) or not msg.sender or len(msg.sender) > 2048:
        errors.append("sender must be a non-empty string of at most 2048 characters")

    # recipient must be non-empty.
    if not isinstance(msg.recipient, str) or not msg.recipient or len(msg.recipient) > 2048:
        errors.append("recipient must be a non-empty string of at most 2048 characters")

    # timestamp must be valid ISO 8601.
    if not isinstance(msg.timestamp, str) or not msg.timestamp:
        errors.append("timestamp is required")
    else:
        try:
            _parse_timestamp(msg.timestamp)
        except ValueError:
            errors.append(f"timestamp is not valid ISO 8601: '{msg.timestamp}'")

    # payload must be a dict.
    if not isinstance(msg.payload, dict):
        errors.append("payload must be an object")
    elif isinstance(msg.type, str) and msg.type in VALID_TYPES:
        errors.extend(_validate_payload(msg.type, msg.payload))

    if msg.signature is not None:
        if _decode_canonical_signature(msg.signature) is None:
            errors.append(
                "signature must contain exactly 64 Ed25519 bytes in canonical standard base64"
            )

    return errors


def _is_creed_uri(value: Any) -> bool:
    if (
        not isinstance(value, str)
        or len(value) > 2048
        or _CREED_URI_PATTERN.fullmatch(value) is None
    ):
        return False
    return True


def _required(payload: dict[str, Any], fields: set[str], errors: list[str]) -> None:
    for field_name in sorted(fields - payload.keys()):
        errors.append(f"payload.{field_name} is required")


def _unknown(payload: dict[str, Any], fields: set[str], errors: list[str]) -> None:
    for field_name in sorted(payload.keys() - fields):
        errors.append(f"payload contains unknown field '{field_name}'")


def _bounded_state_value(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and (not isinstance(value, float) or math.isfinite(value))
        and 1 <= value <= 9
    )


def _validate_personal_state(value: Any) -> list[str]:
    if not isinstance(value, dict):
        return ["payload.personal_state must be an object"]
    errors: list[str] = []
    allowed = {"cognitive", "emotional", "energy", "urgency", "body"}
    _unknown(value, allowed, errors)
    for field_name in ("cognitive", "energy", "urgency"):
        if field_name in value and not _bounded_state_value(value[field_name]):
            errors.append(f"payload.personal_state.{field_name} must be a number from 1 to 9")
    for field_name, required in (("emotional", True), ("body", False)):
        if field_name not in value:
            continue
        nested = value[field_name]
        if not isinstance(nested, dict):
            errors.append(f"payload.personal_state.{field_name} must be an object")
            continue
        nested_fields = {"valence", "arousal"} if required else {"pain", "comfort"}
        if required:
            _required(nested, nested_fields, errors)
        _unknown(nested, nested_fields, errors)
        for dimension, state_value in nested.items():
            if dimension in nested_fields and not _bounded_state_value(state_value):
                errors.append(
                    f"payload.personal_state.{field_name}.{dimension} "
                    "must be a number from 1 to 9"
                )
    return errors


def _validate_payload(message_type: str, payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if message_type == "context_share":
        allowed = {"context", "constitution_ref", "personal_state"}
        _required(payload, {"context", "constitution_ref"}, errors)
        _unknown(payload, allowed, errors)
        if "context" in payload and (
            not isinstance(payload["context"], str)
            or not payload["context"]
            or len(payload["context"]) > 8192
        ):
            errors.append("payload.context must be a non-empty string of at most 8192 characters")
        if "constitution_ref" in payload and not _is_creed_uri(payload["constitution_ref"]):
            errors.append("payload.constitution_ref must be a valid creed:// URI")
        if "personal_state" in payload:
            errors.extend(_validate_personal_state(payload["personal_state"]))
    elif message_type == "constitution_announce":
        allowed = {"constitution_ref", "manifest_hash", "scope"}
        _required(payload, {"constitution_ref", "manifest_hash"}, errors)
        _unknown(payload, allowed, errors)
        if "constitution_ref" in payload and not _is_creed_uri(payload["constitution_ref"]):
            errors.append("payload.constitution_ref must be a valid creed:// URI")
        if (
            "manifest_hash" in payload
            and (
                not isinstance(payload["manifest_hash"], str)
                or _CONTENT_HASH_PATTERN.fullmatch(payload["manifest_hash"]) is None
            )
        ):
            errors.append("payload.manifest_hash must be a lowercase sha256 digest")
        if "scope" in payload:
            scope = payload["scope"]
            scope_fields = {"model_families", "purposes", "environments"}
            if not isinstance(scope, dict):
                errors.append("payload.scope must be an object")
            else:
                _unknown(scope, scope_fields, errors)
                patterns = {
                    "model_families": _MODEL_FAMILY_PATTERN,
                    "purposes": _PURPOSE_PATTERN,
                }
                for field_name, field_value in scope.items():
                    if field_name not in scope_fields:
                        continue
                    if not isinstance(field_value, list) or len(field_value) > 50:
                        errors.append(
                            f"payload.scope.{field_name} must be an array of at most 50 strings"
                        )
                        continue
                    if any(
                        not isinstance(item, str)
                        or not item
                        or len(item) > 256
                        for item in field_value
                    ):
                        errors.append(
                            f"payload.scope.{field_name} entries must be strings "
                            "of 1 to 256 characters"
                        )
                        continue
                    if len(field_value) != len(set(field_value)):
                        errors.append(f"payload.scope.{field_name} entries must be unique")
                    if field_name == "environments":
                        if any(item not in _ENVIRONMENTS for item in field_value):
                            errors.append(
                                "payload.scope.environments contains an unsupported environment"
                            )
                    elif any(patterns[field_name].fullmatch(item) is None for item in field_value):
                        errors.append(f"payload.scope.{field_name} contains an invalid entry")
    elif message_type == "constraint_propagate":
        allowed = {"constraints", "propagation_mode"}
        _required(payload, allowed, errors)
        _unknown(payload, allowed, errors)
        constraints = payload.get("constraints")
        if not isinstance(constraints, list) or not constraints or len(constraints) > 100:
            errors.append("payload.constraints must be an array of 1 to 100 entries")
        else:
            for index, constraint in enumerate(constraints):
                prefix = f"payload.constraints[{index}]"
                fields = {"type", "value", "source_constitution_ref"}
                if not isinstance(constraint, dict):
                    errors.append(f"{prefix} must be an object")
                    continue
                for field_name in sorted(fields - constraint.keys()):
                    errors.append(f"{prefix}.{field_name} is required")
                for field_name in sorted(constraint.keys() - fields):
                    errors.append(f"{prefix} contains unknown field '{field_name}'")
                if "type" in constraint and (
                    not isinstance(constraint["type"], str)
                    or not constraint["type"]
                    or len(constraint["type"]) > 128
                ):
                    errors.append(f"{prefix}.type must be a string of 1 to 128 characters")
                if "source_constitution_ref" in constraint and not _is_creed_uri(
                    constraint["source_constitution_ref"]
                ):
                    errors.append(f"{prefix}.source_constitution_ref must be a creed:// URI")
        if payload.get("propagation_mode") not in {"merge", "override"}:
            errors.append("payload.propagation_mode must be 'merge' or 'override'")
    elif message_type == "escalation":
        allowed = {"severity", "reason", "context", "blocked_action", "requires_ack"}
        required = {"severity", "reason", "context", "requires_ack"}
        _required(payload, required, errors)
        _unknown(payload, allowed, errors)
        severity = payload.get("severity")
        if not isinstance(severity, str) or severity not in VALID_SEVERITIES:
            errors.append(f"severity must be one of {sorted(VALID_SEVERITIES)}, got '{severity}'")
        bounds = {"reason": (1, 4096), "context": (1, 8192), "blocked_action": (0, 1024)}
        for field_name, (minimum, maximum) in bounds.items():
            if field_name not in payload:
                continue
            value = payload[field_name]
            if (
                not isinstance(value, str)
                or len(value) < minimum
                or len(value) > maximum
            ):
                errors.append(
                    f"payload.{field_name} must contain {minimum} to {maximum} characters"
                )
        if "requires_ack" in payload and not isinstance(payload["requires_ack"], bool):
            errors.append("payload.requires_ack must be a boolean")
        if severity in ACK_REQUIRED_SEVERITIES and payload.get("requires_ack") is not True:
            errors.append(f"requires_ack must be true for severity '{severity}'")
    return errors


def message_to_dict(msg: VcpMessage) -> dict[str, Any]:
    """Serialize a message to a JSON-compatible dict.

    Args:
        msg: The VcpMessage to serialize.

    Returns:
        Dict suitable for JSON serialization.
    """
    d: dict[str, Any] = {
        "vcp_message": msg.vcp_message,
        "type": msg.type,
        "message_id": msg.message_id,
        "sender": msg.sender,
        "recipient": msg.recipient,
        "timestamp": msg.timestamp,
        "payload": deepcopy(msg.payload),
    }
    if msg.signature is not None:
        d["signature"] = msg.signature
    return d


def message_from_dict(data: dict[str, Any]) -> VcpMessage:
    """Deserialize a message from a dict.

    Args:
        data: Dict with message fields.

    Returns:
        VcpMessage instance.

    Raises:
        KeyError: If a required field is missing.
    """
    if not isinstance(data, dict):
        raise TypeError("message data must be an object")
    allowed = {
        "vcp_message",
        "type",
        "message_id",
        "sender",
        "recipient",
        "timestamp",
        "payload",
        "signature",
    }
    unknown = data.keys() - allowed
    if unknown:
        raise ValueError(f"message contains unknown fields: {', '.join(sorted(unknown))}")
    return VcpMessage(
        vcp_message=data["vcp_message"],
        type=data["type"],
        message_id=data["message_id"],
        sender=data["sender"],
        recipient=data["recipient"],
        timestamp=data["timestamp"],
        payload=deepcopy(data["payload"]),
        signature=data.get("signature"),
    )


def sign_message(msg: VcpMessage, secret_key: bytes) -> VcpMessage:
    """Sign a message's envelope using Ed25519.

    The signature covers the RFC 8785 canonical form of the full message
    envelope excluding the ``signature`` field, consistent with VCP v2.0
    manifest canonicalization.

    Args:
        msg: The message to sign.
        secret_key: Ed25519 secret key bytes (32 bytes).

    Returns:
        A new VcpMessage with the ``signature`` field set.

    Raises:
        ImportError: If ``ed25519`` is not available.
    """
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    # Build the dict to sign (everything except 'signature').
    to_sign = message_to_dict(msg)
    to_sign.pop("signature", None)

    canonical = rfc8785.dumps(to_sign)

    private_key = Ed25519PrivateKey.from_private_bytes(secret_key)
    sig_bytes = private_key.sign(canonical)
    sig_b64 = base64.b64encode(sig_bytes).decode("ascii")

    return VcpMessage(
        vcp_message=msg.vcp_message,
        type=msg.type,
        message_id=msg.message_id,
        sender=msg.sender,
        recipient=msg.recipient,
        timestamp=msg.timestamp,
        payload=deepcopy(msg.payload),
        signature=f"base64:{sig_b64}",
    )


def verify_message(msg: VcpMessage, public_key: bytes) -> bool:
    """Verify a message's Ed25519 signature.

    Args:
        msg: The signed message.
        public_key: Ed25519 public key bytes (32 bytes).

    Returns:
        True if the signature is valid, False otherwise.
    """
    if not msg.signature:
        return False

    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

    to_verify = message_to_dict(msg)
    to_verify.pop("signature", None)

    try:
        canonical = rfc8785.dumps(to_verify)
    except (TypeError, ValueError):
        return False

    sig_bytes = _decode_canonical_signature(msg.signature)
    if sig_bytes is None:
        return False

    try:
        pub = Ed25519PublicKey.from_public_bytes(public_key)
        pub.verify(sig_bytes, canonical)
        return True
    except (InvalidSignature, TypeError, ValueError):
        return False


def check_version_compatibility(received: str, minimum: str = "2.0") -> bool:
    """Check if the received VCP version is compatible per spec Section 4.5.

    Major version difference = reject (incompatible).
    Minor difference (sender newer) = accept (ignore unknown fields).
    Minor difference (sender older) = accept (use defaults for missing fields).

    Args:
        received: The version string from the incoming message (e.g. "2.0").
        minimum: The minimum version required (default "2.0").

    Returns:
        True if versions are compatible, False if major version mismatch.
    """

    def _parse_ver(v: str) -> tuple[int, int]:
        if not isinstance(v, str) or _VERSION_PATTERN.fullmatch(v) is None:
            raise ValueError("version must contain numeric major and minor components")
        parts = v.split(".")
        return int(parts[0]), int(parts[1])

    try:
        recv_major, _ = _parse_ver(received)
        min_major, _ = _parse_ver(minimum)
    except (TypeError, ValueError):
        return False

    # Major version mismatch = reject
    if recv_major != min_major:
        return False

    # Same major version: minor differences are tolerated
    return True


def _parse_timestamp(ts: str) -> datetime:
    """Parse an ISO 8601 timestamp string.

    Args:
        ts: ISO 8601 string (must include timezone or end with Z).

    Returns:
        datetime object.

    Raises:
        ValueError: If the string cannot be parsed.
    """
    if not isinstance(ts, str) or _TIMESTAMP_PATTERN.fullmatch(ts) is None:
        raise ValueError("timestamp must be an RFC 3339 UTC value ending in Z")
    # Python 3.10 rejects otherwise valid RFC 3339 fractions longer than six
    # digits. Normalize only the parser input to its microsecond precision;
    # the validated wire value remains unchanged on the message.
    cleaned = ts[:-1]
    if "." in cleaned:
        seconds, fraction = cleaned.split(".", 1)
        cleaned = f"{seconds}.{fraction[:6].ljust(6, '0')}"
    cleaned += "+00:00"
    parsed = datetime.fromisoformat(cleaned)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("timestamp must include a UTC offset")
    if parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise ValueError("timestamp must be UTC")
    return parsed
