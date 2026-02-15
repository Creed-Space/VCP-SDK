"""Tests for VCP Inter-Agent Messaging v1.2 envelope support."""
from __future__ import annotations

import json
import uuid

import pytest

from vcp.messaging import (
    PROTOCOL_VERSION,
    VALID_TYPES,
    VcpMessage,
    create_message,
    message_from_dict,
    message_to_dict,
    validate_message,
)


# ── Fixtures ──────────────────────────────────────────────


def _valid_payload() -> dict:
    return {
        "context": "\u23f0\U0001f305|\U0001f4cd\U0001f3e1",
        "constitution_ref": "creed://creed.space/family.safe.guide@1.2.0",
    }


def _valid_message(**overrides) -> VcpMessage:
    defaults = dict(
        vcp_message="1.2",
        type="context_share",
        message_id=str(uuid.uuid4()),
        sender="agent://test.local/sender",
        recipient="agent://test.local/receiver",
        timestamp="2026-02-15T10:30:00Z",
        payload=_valid_payload(),
        signature=None,
    )
    defaults.update(overrides)
    return VcpMessage(**defaults)


# ── create_message ────────────────────────────────────────


class TestCreateMessage:
    def test_generates_valid_message(self) -> None:
        msg = create_message(
            type="context_share",
            sender="agent://a/s",
            recipient="agent://a/r",
            payload=_valid_payload(),
        )
        errors = validate_message(msg)
        assert errors == [], f"Expected valid message, got errors: {errors}"

    def test_auto_generates_uuid(self) -> None:
        msg = create_message(
            type="context_share",
            sender="s",
            recipient="r",
            payload={},
        )
        # Should be a valid UUID (v4).
        parsed = uuid.UUID(msg.message_id)
        assert parsed.version == 4

    def test_auto_generates_timestamp(self) -> None:
        msg = create_message(
            type="context_share",
            sender="s",
            recipient="r",
            payload={},
        )
        assert msg.timestamp.endswith("Z")
        # Should be parseable ISO 8601.
        from datetime import datetime

        cleaned = msg.timestamp.replace("Z", "+00:00")
        dt = datetime.fromisoformat(cleaned)
        assert dt is not None

    def test_sets_protocol_version(self) -> None:
        msg = create_message(
            type="escalation",
            sender="s",
            recipient="r",
            payload={},
        )
        assert msg.vcp_message == PROTOCOL_VERSION


# ── validate_message ──────────────────────────────────────


class TestValidateMessage:
    def test_valid_message_returns_empty_errors(self) -> None:
        msg = _valid_message()
        assert validate_message(msg) == []

    def test_missing_type_returns_error(self) -> None:
        msg = _valid_message(type="")
        errors = validate_message(msg)
        assert any("type" in e for e in errors)

    def test_invalid_type_returns_error(self) -> None:
        msg = _valid_message(type="not_a_real_type")
        errors = validate_message(msg)
        assert any("type must be one of" in e for e in errors)

    def test_invalid_vcp_message_version(self) -> None:
        msg = _valid_message(vcp_message="2.0")
        errors = validate_message(msg)
        assert any("vcp_message must be" in e for e in errors)

    def test_invalid_message_id_format(self) -> None:
        msg = _valid_message(message_id="not-a-uuid")
        errors = validate_message(msg)
        assert any("message_id" in e for e in errors)

    def test_missing_sender(self) -> None:
        msg = _valid_message(sender="")
        errors = validate_message(msg)
        assert any("sender" in e for e in errors)

    def test_missing_recipient(self) -> None:
        msg = _valid_message(recipient="")
        errors = validate_message(msg)
        assert any("recipient" in e for e in errors)

    def test_invalid_timestamp(self) -> None:
        msg = _valid_message(timestamp="not-a-date")
        errors = validate_message(msg)
        assert any("timestamp" in e for e in errors)

    def test_escalation_critical_requires_ack(self) -> None:
        msg = _valid_message(
            type="escalation",
            payload={
                "severity": "critical",
                "reason": "test",
                "context": "test",
                "requires_ack": False,
            },
        )
        errors = validate_message(msg)
        assert any("requires_ack" in e for e in errors)

    def test_escalation_info_does_not_require_ack(self) -> None:
        msg = _valid_message(
            type="escalation",
            payload={
                "severity": "info",
                "reason": "test",
                "context": "test",
                "requires_ack": False,
            },
        )
        errors = validate_message(msg)
        # Should NOT have any requires_ack error for info severity.
        assert not any("requires_ack" in e for e in errors)


# ── Serialization roundtrip ───────────────────────────────


class TestSerialization:
    def test_roundtrip_without_signature(self) -> None:
        original = _valid_message()
        d = message_to_dict(original)
        restored = message_from_dict(d)
        assert restored.vcp_message == original.vcp_message
        assert restored.type == original.type
        assert restored.message_id == original.message_id
        assert restored.sender == original.sender
        assert restored.recipient == original.recipient
        assert restored.timestamp == original.timestamp
        assert restored.payload == original.payload
        assert restored.signature is None

    def test_roundtrip_with_signature(self) -> None:
        original = _valid_message(signature="base64:AAAA")
        d = message_to_dict(original)
        restored = message_from_dict(d)
        assert restored.signature == "base64:AAAA"

    def test_json_roundtrip(self) -> None:
        original = _valid_message()
        json_str = json.dumps(message_to_dict(original))
        d = json.loads(json_str)
        restored = message_from_dict(d)
        assert restored.message_id == original.message_id

    def test_from_dict_with_extra_fields_does_not_crash(self) -> None:
        d = message_to_dict(_valid_message())
        d["extra_field"] = "should be ignored"
        # Should not raise -- extra fields are silently ignored.
        restored = message_from_dict(d)
        assert restored.vcp_message == "1.2"

    def test_to_dict_omits_signature_when_none(self) -> None:
        msg = _valid_message(signature=None)
        d = message_to_dict(msg)
        assert "signature" not in d

    def test_to_dict_includes_signature_when_present(self) -> None:
        msg = _valid_message(signature="base64:ABC123")
        d = message_to_dict(msg)
        assert d["signature"] == "base64:ABC123"


# ── Broadcast ─────────────────────────────────────────────


class TestBroadcast:
    def test_broadcast_recipient(self) -> None:
        msg = create_message(
            type="constitution_announce",
            sender="agent://cluster.prod/safety-monitor",
            recipient="broadcast",
            payload={
                "constitution_ref": "creed://creed.space/enterprise.compliance@2.0.1",
                "manifest_hash": "sha256:" + "a" * 64,
            },
        )
        assert msg.recipient == "broadcast"
        assert validate_message(msg) == []


# ── All message types ─────────────────────────────────────


class TestAllMessageTypes:
    def test_all_valid_types_pass_validation(self) -> None:
        for msg_type in VALID_TYPES:
            msg = _valid_message(type=msg_type)
            # For escalation, add requires_ack if needed.
            if msg_type == "escalation":
                msg = _valid_message(
                    type=msg_type,
                    payload={
                        "severity": "info",
                        "reason": "test",
                        "context": "test",
                        "requires_ack": False,
                    },
                )
            errors = validate_message(msg)
            assert errors == [], f"Type {msg_type} failed: {errors}"


# ── Ed25519 signing (conditional on cryptography availability) ──


class TestSigning:
    @pytest.fixture
    def ed25519_keypair(self):
        """Generate an Ed25519 keypair using the cryptography library."""
        try:
            from cryptography.hazmat.primitives.asymmetric.ed25519 import (
                Ed25519PrivateKey,
            )
        except ImportError:
            pytest.skip("cryptography library not available")

        private_key = Ed25519PrivateKey.generate()
        secret_bytes = private_key.private_bytes_raw()
        public_bytes = private_key.public_key().public_bytes_raw()
        return secret_bytes, public_bytes

    def test_sign_and_verify_roundtrip(self, ed25519_keypair) -> None:
        from vcp.messaging import sign_message, verify_message

        secret, public = ed25519_keypair
        msg = _valid_message()
        signed = sign_message(msg, secret)
        assert signed.signature is not None
        assert signed.signature.startswith("base64:")
        assert verify_message(signed, public)

    def test_verify_fails_with_wrong_key(self, ed25519_keypair) -> None:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import (
            Ed25519PrivateKey,
        )
        from vcp.messaging import sign_message, verify_message

        secret, _ = ed25519_keypair
        msg = _valid_message()
        signed = sign_message(msg, secret)

        # Use a different key for verification.
        wrong_key = Ed25519PrivateKey.generate().public_key().public_bytes_raw()
        assert not verify_message(signed, wrong_key)

    def test_verify_returns_false_without_signature(self, ed25519_keypair) -> None:
        from vcp.messaging import verify_message

        _, public = ed25519_keypair
        msg = _valid_message(signature=None)
        assert not verify_message(msg, public)
