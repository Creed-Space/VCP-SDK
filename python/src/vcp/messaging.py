"""
VCP Inter-Agent Messaging v1.2 envelope support.

Implements the message envelope format defined in the VCP Inter-Agent
Messaging Specification v1.2. Supports four message types:

- context_share: Share Enneagram context with peer agents
- constitution_announce: Announce active constitutions
- constraint_propagate: Propagate constraints to child agents
- escalation: Escalate safety concerns to parent agents

Signing follows RFC 8785 (JSON Canonicalization Scheme) with Ed25519,
consistent with VCP v1.0 manifest signing.
"""
from __future__ import annotations

import base64
import json
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

# Protocol version for v1.2 messages.
PROTOCOL_VERSION = "1.2"

# Valid message types per the spec.
VALID_TYPES = frozenset({
    "context_share",
    "constitution_announce",
    "constraint_propagate",
    "escalation",
})

# Severities that require acknowledgment.
ACK_REQUIRED_SEVERITIES = frozenset({"critical", "emergency"})

# Valid escalation severities.
VALID_SEVERITIES = frozenset({"info", "warning", "critical", "emergency"})

# UUID v4 pattern (we accept both v4 and v7 for flexibility).
_UUID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


@dataclass
class VcpMessage:
    """VCP v1.2 message envelope.

    Attributes:
        vcp_message: Protocol version. Must be "1.2".
        type: Message type (context_share, constitution_announce,
              constraint_propagate, escalation).
        message_id: UUIDv7 (preferred) or UUIDv4 identifier for deduplication.
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
        message_id=str(uuid.uuid4()),
        sender=sender,
        recipient=recipient,
        timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        payload=payload,
    )


def validate_message(msg: VcpMessage) -> list[str]:
    """Validate a message against the v1.2 spec.

    Returns a list of error strings. An empty list means the message is valid.

    Args:
        msg: The VcpMessage to validate.

    Returns:
        List of validation error descriptions.
    """
    errors: list[str] = []

    # vcp_message version check.
    if msg.vcp_message != PROTOCOL_VERSION:
        errors.append(
            f"vcp_message must be '{PROTOCOL_VERSION}', got '{msg.vcp_message}'"
        )

    # Type check.
    if not msg.type:
        errors.append("type is required")
    elif msg.type not in VALID_TYPES:
        errors.append(
            f"type must be one of {sorted(VALID_TYPES)}, got '{msg.type}'"
        )

    # message_id format (UUID).
    if not msg.message_id:
        errors.append("message_id is required")
    elif not _UUID_PATTERN.match(msg.message_id):
        errors.append(f"message_id is not a valid UUID: '{msg.message_id}'")

    # sender must be non-empty.
    if not msg.sender:
        errors.append("sender is required")

    # recipient must be non-empty.
    if not msg.recipient:
        errors.append("recipient is required")

    # timestamp must be valid ISO 8601.
    if not msg.timestamp:
        errors.append("timestamp is required")
    else:
        try:
            _parse_timestamp(msg.timestamp)
        except ValueError:
            errors.append(f"timestamp is not valid ISO 8601: '{msg.timestamp}'")

    # payload must be a dict.
    if not isinstance(msg.payload, dict):
        errors.append("payload must be an object")

    # Type-specific payload validation.
    if msg.type == "escalation" and isinstance(msg.payload, dict):
        severity = msg.payload.get("severity")
        if severity and severity in ACK_REQUIRED_SEVERITIES:
            if msg.payload.get("requires_ack") is not True:
                errors.append(
                    f"requires_ack must be true for severity '{severity}'"
                )

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
        "payload": msg.payload,
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
    return VcpMessage(
        vcp_message=data["vcp_message"],
        type=data["type"],
        message_id=data["message_id"],
        sender=data["sender"],
        recipient=data["recipient"],
        timestamp=data["timestamp"],
        payload=data["payload"],
        signature=data.get("signature"),
    )


def sign_message(msg: VcpMessage, secret_key: bytes) -> VcpMessage:
    """Sign a message's envelope using Ed25519.

    The signature covers the RFC 8785 canonical form of the full message
    envelope excluding the ``signature`` field, consistent with VCP v1.0
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

    canonical = json.dumps(
        to_sign,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")

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
        payload=msg.payload,
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

    canonical = json.dumps(
        to_verify,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")

    sig_value = msg.signature
    if sig_value.startswith("base64:"):
        sig_value = sig_value[7:]
    sig_bytes = base64.b64decode(sig_value)

    try:
        pub = Ed25519PublicKey.from_public_bytes(public_key)
        pub.verify(sig_bytes, canonical)
        return True
    except InvalidSignature:
        return False


def _parse_timestamp(ts: str) -> datetime:
    """Parse an ISO 8601 timestamp string.

    Args:
        ts: ISO 8601 string (must include timezone or end with Z).

    Returns:
        datetime object.

    Raises:
        ValueError: If the string cannot be parsed.
    """
    # Handle Z suffix for fromisoformat (Python <3.11 compat).
    cleaned = ts.replace("Z", "+00:00")
    return datetime.fromisoformat(cleaned)
