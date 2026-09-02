"""Adversarial tests for exact VCP Inter-Agent Messaging v2.0 validation."""

from __future__ import annotations

import base64
import json
import math
import uuid
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from typing import Any

import pytest
import rfc8785

from vcp.messaging import (
    PROTOCOL_VERSION,
    VALID_TYPES,
    VcpMessage,
    check_version_compatibility,
    create_message,
    message_from_dict,
    message_to_dict,
    sign_message,
    validate_message,
    verify_message,
)

VALID_UUID7 = "019502a4-7e5c-7000-8000-000000000001"
VALID_REF = "creed://creed.space/family.safe.guide@1.2.0"


def _payload(message_type: str) -> dict[str, Any]:
    payloads: dict[str, dict[str, Any]] = {
        "context_share": {
            "context": "⏰🌅|📍🏡",
            "constitution_ref": VALID_REF,
        },
        "constitution_announce": {
            "constitution_ref": VALID_REF,
            "manifest_hash": "sha256:" + "a" * 64,
        },
        "constraint_propagate": {
            "constraints": [
                {
                    "type": "topic_block",
                    "value": ["weapons"],
                    "source_constitution_ref": VALID_REF,
                }
            ],
            "propagation_mode": "merge",
        },
        "escalation": {
            "severity": "info",
            "reason": "policy conflict",
            "context": "⏰🌅",
            "requires_ack": False,
        },
    }
    return deepcopy(payloads[message_type])


def _message(message_type: str = "context_share", **overrides: Any) -> VcpMessage:
    values: dict[str, Any] = {
        "vcp_message": "2.0",
        "type": message_type,
        "message_id": VALID_UUID7,
        "sender": "agent://test.local/sender",
        "recipient": "agent://test.local/receiver",
        "timestamp": "2026-02-15T10:30:00Z",
        "payload": _payload(message_type),
        "signature": None,
    }
    values.update(overrides)
    return VcpMessage(**values)


def _errors(message_type: str = "context_share", **overrides: Any) -> list[str]:
    return validate_message(_message(message_type, **overrides))


class TestEnvelope:
    def test_create_generates_valid_uuid7_utc_message_without_aliasing_payload(self) -> None:
        payload = _payload("context_share")
        message = create_message("context_share", "sender", "recipient", payload)
        payload["context"] = "mutated"

        assert uuid.UUID(message.message_id).version == 7
        assert message.timestamp.endswith("Z")
        assert message.payload["context"] == "⏰🌅|📍🏡"
        assert validate_message(message) == []

    def test_uuid7_generation_is_unique_under_concurrency(self) -> None:
        def generate(_: int) -> str:
            return create_message("context_share", "s", "r", _payload("context_share")).message_id

        with ThreadPoolExecutor(max_workers=16) as pool:
            identifiers = list(pool.map(generate, range(1_000)))
        assert len(set(identifiers)) == len(identifiers)
        assert all(uuid.UUID(identifier).version == 7 for identifier in identifiers)

    @pytest.mark.parametrize("message_type", sorted(VALID_TYPES))
    def test_each_normative_payload_type_is_accepted(self, message_type: str) -> None:
        assert validate_message(_message(message_type)) == []

    @pytest.mark.parametrize(
        ("field", "value", "fragment"),
        [
            ("vcp_message", "2.1", "vcp_message"),
            ("vcp_message", 2.0, "vcp_message"),
            ("type", "", "type"),
            ("type", "unknown", "type"),
            ("message_id", "not-a-uuid", "UUIDv7"),
            ("message_id", str(uuid.uuid4()), "UUIDv7"),
            ("message_id", VALID_UUID7.upper(), "UUIDv7"),
            ("sender", "", "sender"),
            ("sender", "x" * 2049, "sender"),
            ("recipient", "", "recipient"),
            ("recipient", "x" * 2049, "recipient"),
            ("payload", [], "payload"),
            ("timestamp", "not-a-date", "timestamp"),
            ("timestamp", "2026-02-15 10:30:00Z", "timestamp"),
            ("timestamp", "2026-02-15T10:30:00+00:00", "timestamp"),
            ("timestamp", "2026-02-15T10:30:00-00:00", "timestamp"),
            ("timestamp", "2026-02-30T10:30:00Z", "timestamp"),
            ("timestamp", "2026-02-15T10:30:00.1234567890Z", "timestamp"),
        ],
    )
    def test_malformed_envelope_fields_are_rejected(
        self, field: str, value: object, fragment: str
    ) -> None:
        assert any(fragment in error for error in _errors(**{field: value}))

    def test_envelope_length_boundaries_are_inclusive(self) -> None:
        assert _errors(sender="x" * 2048, recipient="y" * 2048) == []

    @pytest.mark.parametrize("fraction_digits", range(1, 10))
    def test_timestamp_accepts_every_supported_fractional_precision(
        self, fraction_digits: int
    ) -> None:
        fraction = "123456789"[:fraction_digits]
        assert _errors(timestamp=f"2026-02-15T10:30:00.{fraction}Z") == []

    def test_validator_rejects_wrong_runtime_object_type(self) -> None:
        with pytest.raises(TypeError, match="VcpMessage"):
            validate_message({})  # type: ignore[arg-type]

    @pytest.mark.parametrize(
        "signature",
        [
            "AAAA",
            "base64:***",
            "base64:AAAA",
            "base64:" + base64.b64encode(b"x" * 65).decode(),
            7,
        ],
    )
    def test_malformed_signatures_are_rejected(self, signature: object) -> None:
        assert any("signature" in error for error in _errors(signature=signature))

    def test_signature_requires_canonical_standard_base64(self) -> None:
        canonical = base64.b64encode(b"x" * 64).decode("ascii")
        assert _errors(signature=f"base64:{canonical}") == []

        replacements = {"A": "B", "Q": "R", "g": "h", "w": "x"}
        noncanonical = canonical[:-3] + replacements[canonical[-3]] + "=="
        assert base64.b64decode(noncanonical, validate=True) == b"x" * 64
        assert any(
            "canonical standard base64" in error
            for error in _errors(signature=f"base64:{noncanonical}")
        )


class TestContextShare:
    def test_fractional_personal_state_and_bounds_are_valid(self) -> None:
        payload = _payload("context_share")
        payload["personal_state"] = {
            "cognitive": 1,
            "emotional": {"valence": 4.5, "arousal": 9},
            "energy": 5.25,
            "urgency": 3,
            "body": {"pain": 1, "comfort": 9},
        }
        assert _errors(payload=payload) == []

    def test_partial_and_empty_personal_state_are_valid(self) -> None:
        for state in ({}, {"energy": 4.5}, {"body": {}}):
            payload = _payload("context_share")
            payload["personal_state"] = state
            assert _errors(payload=payload) == []

    @pytest.mark.parametrize("value", [True, 0, 9.01, math.inf, math.nan, "5"])
    def test_personal_state_rejects_non_numeric_and_out_of_range_values(
        self, value: object
    ) -> None:
        payload = _payload("context_share")
        payload["personal_state"] = {"energy": value}
        assert any("number from 1 to 9" in error for error in _errors(payload=payload))

    @pytest.mark.parametrize(
        "personal_state",
        [
            [],
            {"unknown": 5},
            {"emotional": []},
            {"emotional": {"valence": 5}},
            {"body": {"temperature": 5}},
        ],
    )
    def test_personal_state_rejects_malformed_shapes(self, personal_state: object) -> None:
        payload = _payload("context_share")
        payload["personal_state"] = personal_state
        assert _errors(payload=payload)

    def test_context_and_constitution_reference_boundaries(self) -> None:
        payload = _payload("context_share")
        payload["context"] = "x" * 8192
        assert _errors(payload=payload) == []
        for bad_context in ("", "x" * 8193, 7):
            payload["context"] = bad_context
            assert any("payload.context" in error for error in _errors(payload=payload))
        payload = _payload("context_share")
        payload["constitution_ref"] = "http://example.test/not-creed"
        assert any("constitution_ref" in error for error in _errors(payload=payload))

    def test_missing_and_unknown_payload_fields_are_rejected(self) -> None:
        assert any("context is required" in error for error in _errors(payload={}))
        payload = _payload("context_share")
        payload["extension"] = True
        assert any("unknown field" in error for error in _errors(payload=payload))


class TestConstitutionAnnounce:
    def test_scope_boundary_and_empty_arrays_are_valid(self) -> None:
        payload = _payload("constitution_announce")
        payload["scope"] = {
            "model_families": [f"model-{index}" for index in range(50)],
            "purposes": [],
            "environments": ["production", "testing"],
        }
        assert _errors("constitution_announce", payload=payload) == []

    @pytest.mark.parametrize(
        ("field", "value"),
        [
            ("model_families", ["bad_model"]),
            ("model_families", ["x"] * 51),
            ("model_families", ["same", "same"]),
            ("purposes", ["Uppercase"]),
            ("purposes", ["x" * 257]),
            ("environments", ["preview"]),
            ("environments", ["testing", "testing"]),
            ("environments", "testing"),
        ],
    )
    def test_scope_rejects_invalid_patterns_duplicates_and_resource_excess(
        self, field: str, value: object
    ) -> None:
        payload = _payload("constitution_announce")
        payload["scope"] = {field: value}
        assert _errors("constitution_announce", payload=payload)

    def test_manifest_hash_and_scope_shape_are_strict(self) -> None:
        for invalid in ("sha256:" + "A" * 64, "sha256:123", 7):
            payload = _payload("constitution_announce")
            payload["manifest_hash"] = invalid
            errors = _errors("constitution_announce", payload=payload)
            assert any("manifest_hash" in error for error in errors)
        for scope in ([], {"unknown": []}):
            payload = _payload("constitution_announce")
            payload["scope"] = scope
            assert _errors("constitution_announce", payload=payload)


class TestConstraintPropagation:
    def test_constraint_count_boundaries_are_enforced(self) -> None:
        constraint = _payload("constraint_propagate")["constraints"][0]
        payload = {
            "constraints": [deepcopy(constraint) for _ in range(100)],
            "propagation_mode": "override",
        }
        assert _errors("constraint_propagate", payload=payload) == []
        payload["constraints"].append(deepcopy(constraint))
        errors = _errors("constraint_propagate", payload=payload)
        assert any("1 to 100" in error for error in errors)

    @pytest.mark.parametrize(
        "payload",
        [
            {"constraints": [], "propagation_mode": "merge"},
            {"constraints": [7], "propagation_mode": "merge"},
            {
                "constraints": [{"type": "", "value": None, "source_constitution_ref": VALID_REF}],
                "propagation_mode": "merge",
            },
            {
                "constraints": [
                    {"type": "x" * 129, "value": None, "source_constitution_ref": VALID_REF}
                ],
                "propagation_mode": "merge",
            },
            {
                "constraints": [{"type": "topic", "source_constitution_ref": VALID_REF}],
                "propagation_mode": "merge",
            },
            {
                "constraints": [
                    {
                        "type": "topic",
                        "value": True,
                        "source_constitution_ref": "bad",
                    }
                ],
                "propagation_mode": "merge",
            },
            {
                "constraints": [
                    {
                        "type": "topic",
                        "value": True,
                        "source_constitution_ref": VALID_REF,
                        "extra": True,
                    }
                ],
                "propagation_mode": "merge",
            },
            {"constraints": [], "propagation_mode": "replace"},
        ],
    )
    def test_malformed_constraint_payloads_are_rejected(self, payload: dict[str, Any]) -> None:
        assert _errors("constraint_propagate", payload=payload)


class TestEscalation:
    def test_text_length_boundaries_are_inclusive(self) -> None:
        payload = _payload("escalation")
        payload.update(reason="x" * 4096, context="y" * 8192, blocked_action="z" * 1024)
        assert _errors("escalation", payload=payload) == []

    @pytest.mark.parametrize(
        ("field", "value"),
        [
            ("severity", "fatal"),
            ("reason", ""),
            ("reason", "x" * 4097),
            ("context", ""),
            ("context", "x" * 8193),
            ("blocked_action", "x" * 1025),
            ("requires_ack", 1),
        ],
    )
    def test_invalid_escalation_values_are_rejected(self, field: str, value: object) -> None:
        payload = _payload("escalation")
        payload[field] = value
        assert _errors("escalation", payload=payload)

    @pytest.mark.parametrize("severity", ["critical", "emergency"])
    def test_high_severity_requires_acknowledgement(self, severity: str) -> None:
        payload = _payload("escalation")
        payload.update(severity=severity, requires_ack=False)
        assert any("requires_ack" in error for error in _errors("escalation", payload=payload))


class TestSerializationAndSigning:
    @pytest.fixture
    def keypair(self) -> tuple[bytes, bytes]:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

        private_key = Ed25519PrivateKey.generate()
        return private_key.private_bytes_raw(), private_key.public_key().public_bytes_raw()

    def test_roundtrip_is_json_safe_and_does_not_share_payload_state(self) -> None:
        original = _message()
        encoded = message_to_dict(original)
        restored = message_from_dict(json.loads(json.dumps(encoded)))
        encoded["payload"]["context"] = "changed"
        restored.payload["context"] = "restored change"

        assert original.payload["context"] == "⏰🌅|📍🏡"
        assert restored.message_id == original.message_id

    def test_exact_v2_decoder_rejects_wrong_shape_missing_and_unknown_fields(self) -> None:
        with pytest.raises(TypeError, match="object"):
            message_from_dict([])  # type: ignore[arg-type]
        with pytest.raises(KeyError):
            message_from_dict({"vcp_message": "2.0"})
        data = message_to_dict(_message())
        data["future_field"] = True
        with pytest.raises(ValueError, match="unknown fields"):
            message_from_dict(data)

    def test_signature_roundtrip_uses_rfc8785_canonical_bytes(
        self, keypair: tuple[bytes, bytes]
    ) -> None:
        secret, public = keypair
        message = _message()
        message.payload["fraction"] = 1e-7
        signed = sign_message(message, secret)
        signature = base64.b64decode(signed.signature[7:])  # type: ignore[index]

        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

        canonical = rfc8785.dumps(message_to_dict(message))
        Ed25519PublicKey.from_public_bytes(public).verify(signature, canonical)
        assert verify_message(signed, public)

    def test_signature_rejects_tampering_wrong_keys_and_malformed_material(
        self, keypair: tuple[bytes, bytes]
    ) -> None:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

        secret, public = keypair
        signed = sign_message(_message(), secret)
        signed.payload["context"] = "tampered"
        assert not verify_message(signed, public)
        signed = sign_message(_message(), secret)
        wrong = Ed25519PrivateKey.generate().public_key().public_bytes_raw()
        assert not verify_message(signed, wrong)

        canonical = signed.signature[7:]  # type: ignore[index]
        replacements = {"A": "B", "Q": "R", "g": "h", "w": "x"}
        noncanonical = canonical[:-3] + replacements[canonical[-3]] + "=="
        assert base64.b64decode(noncanonical, validate=True) == base64.b64decode(canonical)
        signed.signature = f"base64:{noncanonical}"
        assert not verify_message(signed, public)
        assert not verify_message(_message(signature=None), public)
        assert not verify_message(_message(signature="not-base64"), public)
        assert not verify_message(_message(signature="base64:AAAA"), public)
        assert not verify_message(signed, b"short")

    def test_signing_rejects_invalid_secret_or_noncanonical_payload(self) -> None:
        with pytest.raises(ValueError):
            sign_message(_message(), b"short")
        message = _message()
        message.payload["value"] = math.nan
        with pytest.raises((TypeError, ValueError)):
            sign_message(message, b"x" * 32)


@pytest.mark.parametrize(
    ("received", "minimum", "expected"),
    [
        ("2.0", "2.0", True),
        ("2.99", "2.0", True),
        ("2.0.1", "2.9", True),
        ("3.0", "2.0", False),
        ("2", "2.0", False),
        ("2.x", "2.0", False),
        ("9" * 5_000 + ".0", "2.0", False),
        (None, "2.0", False),
    ],
)
def test_version_compatibility_is_total_for_malformed_inputs(
    received: object, minimum: str, expected: bool
) -> None:
    assert check_version_compatibility(received, minimum) is expected  # type: ignore[arg-type]


def test_protocol_constant_matches_exact_validator() -> None:
    assert PROTOCOL_VERSION == "2.0"
