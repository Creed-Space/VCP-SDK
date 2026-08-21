"""Adversarial tests for canonical VCP capability negotiation."""

from __future__ import annotations

from copy import deepcopy

import pytest

from vcp.negotiation import (
    CORE_FEATURE_NAMES,
    MAX_HANDSHAKE_BYTES,
    VCPAck,
    VCPError,
    VCPHello,
    negotiate,
    negotiate_handshake,
)


def _core(**overrides: bool) -> dict[str, bool]:
    result = {name: True for name in CORE_FEATURE_NAMES}
    result.update(overrides)
    return result


def _hello(**overrides: object) -> dict[str, object]:
    result: dict[str, object] = {
        "type": "vcp-hello",
        "version": "3.1",
        "min_version": "1.0",
        "extensions": ["VCP-X-Personal", "VCP-X-Torch"],
    }
    result.update(overrides)
    return result


def _server(**overrides: object) -> dict[str, object]:
    result: dict[str, object] = {
        "supported_versions": ["1.0", "2.0", "3.0", "3.1"],
        "extensions": {
            "VCP-X-Personal": {"decay": True},
            "VCP-X-Consensus": {"method": "schulze"},
        },
        "core_features": _core(),
        "server_id": "server-1",
        "session_id": "session-1",
    }
    result.update(overrides)
    return result


class TestWireHandshake:
    def test_canonical_ack_chooses_highest_mutual_version_and_partitions_extensions(self) -> None:
        result = negotiate_handshake(_hello(), _server())

        assert result == {
            "type": "vcp-ack",
            "version": "3.1",
            "supported": ["VCP-X-Personal"],
            "unsupported": ["VCP-X-Torch"],
            "capabilities": {"VCP-X-Personal": {"decay": True}},
            "core_features": _core(),
            "server_id": "server-1",
            "session_id": "session-1",
        }

    def test_client_order_is_preserved_while_invalid_ids_are_ignored(self) -> None:
        hello = _hello(
            extensions=[
                "junk",
                "VCP-X-Consensus",
                "VCP-X-Personal",
            ]
        )

        result = negotiate_handshake(hello, _server())

        assert result["supported"] == ["VCP-X-Consensus", "VCP-X-Personal"]
        assert result["unsupported"] == []

    def test_unicode_wire_limits_are_counted_in_code_points(self) -> None:
        invalid_but_bounded = "😀" * 128
        client_id = "😀" * 256
        result = negotiate_handshake(
            _hello(extensions=[invalid_but_bounded], client_id=client_id),
            _server(),
        )
        assert result["supported"] == []
        assert result["unsupported"] == []

        with pytest.raises(ValueError, match="client_id"):
            negotiate_handshake(
                _hello(extensions=[], client_id="😀" * 257),
                _server(),
            )

    @pytest.mark.parametrize(
        "extensions",
        [
            ["VCP-X-Personal", "VCP-X-Personal"],
            ["invalid", "invalid"],
        ],
    )
    def test_duplicate_raw_extension_requests_are_rejected(
        self, extensions: list[str]
    ) -> None:
        with pytest.raises(ValueError, match="unique"):
            negotiate_handshake(_hello(extensions=extensions), _server())

    def test_versions_are_compared_numerically_not_lexicographically(self) -> None:
        result = negotiate_handshake(
            _hello(version="10.2", min_version="2.0", extensions=[]),
            _server(supported_versions=["9.10", "10.1", "2.20"]),
        )
        assert result["version"] == "10.1"

    def test_versions_with_huge_components_are_rejected_before_integer_conversion(self) -> None:
        huge = "9" * 4_000
        with pytest.raises(ValueError, match="semver"):
            negotiate_handshake(
                _hello(version=f"{huge}.1", min_version="1.0", extensions=[]),
                _server(supported_versions=["3.1"]),
            )

    def test_negotiated_version_before_3_1_rejects_all_extensions(self) -> None:
        result = negotiate_handshake(
            _hello(version="3.0", min_version="2.0"),
            _server(supported_versions=["2.0", "3.0"]),
        )
        assert result["supported"] == []
        assert result["unsupported"] == ["VCP-X-Personal", "VCP-X-Torch"]
        assert result["capabilities"] == {}

    def test_missing_extension_dependencies_are_signaled_fail_safe(self) -> None:
        hello = _hello(extensions=["VCP-X-Torch", "VCP-X-Intent"])
        server = _server(
            extensions={
                "VCP-X-Torch": {"lineage": True, "degraded": False},
                "VCP-X-Intent": {"inference": True, "personal_signals": True},
            }
        )

        result = negotiate_handshake(hello, server)

        assert result["capabilities"] == {
            "VCP-X-Torch": {"lineage": True, "degraded": True},
            "VCP-X-Intent": {"inference": True, "personal_signals": False},
        }
        assert server["extensions"]["VCP-X-Torch"]["degraded"] is False
        assert server["extensions"]["VCP-X-Intent"]["personal_signals"] is True

    def test_active_dependencies_do_not_force_degraded_capabilities(self) -> None:
        result = negotiate_handshake(
            _hello(
                extensions=[
                    "VCP-X-Relational",
                    "VCP-X-Torch",
                    "VCP-X-Personal",
                    "VCP-X-Intent",
                ]
            ),
            _server(
                extensions={
                    "VCP-X-Relational": {},
                    "VCP-X-Torch": {"lineage": True},
                    "VCP-X-Personal": {},
                    "VCP-X-Intent": {"inference": True},
                }
            ),
        )
        assert result["capabilities"]["VCP-X-Torch"] == {"lineage": True}
        assert result["capabilities"]["VCP-X-Intent"] == {"inference": True}

    @pytest.mark.parametrize(
        "hello",
        [
            [],
            {},
            {"type": "VCP-Hello", "version": "3.1"},
            {"type": "vcp-hello"},
            _hello(version="3.1.0"),
            _hello(version=True),
            _hello(extensions=None),
            _hello(extensions="VCP-X-Personal"),
            _hello(extensions=[7]),
            _hello(extensions=[""]),
            _hello(extensions=["x" * 129]),
            _hello(extensions=[f"VCP-X-{index}" for index in range(257)]),
            _hello(client_id=""),
            _hello(client_id="x" * 257),
            _hello(identity=7),
        ],
    )
    def test_malformed_hello_is_rejected_without_ambiguous_coercion(self, hello: object) -> None:
        with pytest.raises((KeyError, TypeError, ValueError)):
            negotiate_handshake(hello, _server())  # type: ignore[arg-type]

    @pytest.mark.parametrize(
        "server",
        [
            [],
            {},
            _server(supported_versions=[]),
            _server(supported_versions=["3.1.0"]),
            _server(supported_versions=[None, "invalid", True]),
            _server(supported_versions=[f"{index}.0" for index in range(65)]),
            _server(extensions=[]),
            _server(extensions={"personal": {}}),
            _server(extensions={"VCP-X-Personal": True}),
            _server(core_features=[]),
            _server(core_features={name: True for name in CORE_FEATURE_NAMES[:-1]}),
            _server(core_features={**_core(), "future": 1}),
            _server(extensions={f"VCP-X-E{index}": {} for index in range(257)}),
            _server(server_id=""),
            _server(server_id="x" * 257),
            _server(session_id=""),
            _server(session_id="x" * 129),
        ],
    )
    def test_malformed_server_config_is_rejected(self, server: object) -> None:
        with pytest.raises((TypeError, ValueError)):
            negotiate_handshake(_hello(), server)  # type: ignore[arg-type]

    def test_server_registry_and_version_count_boundaries_are_inclusive(self) -> None:
        longest_id = "VCP-X-" + "A" * 122
        versions = [f"{index}.0" for index in range(64)]
        result = negotiate_handshake(
            _hello(version="63.0", extensions=[longest_id]),
            _server(
                supported_versions=versions,
                extensions={longest_id: {}},
            ),
        )
        assert result["version"] == "63.0"
        assert result["supported"] == [longest_id]

        with pytest.raises(ValueError, match="server extensions"):
            negotiate_handshake(
                _hello(extensions=[]),
                _server(extensions={longest_id + "A": {}}),
            )

    def test_no_mutual_version_returns_stable_sorted_error(self) -> None:
        result = negotiate_handshake(
            _hello(version="2.0", min_version="1.0"),
            _server(supported_versions=["10.0", "3.1", "3.1"]),
        )
        assert result == {
            "type": "vcp-error",
            "code": "VERSION_UNSUPPORTED",
            "message": "No mutually supported VCP version",
            "supported_versions": ["3.1", "10.0"],
            "retry_after": None,
        }

    def test_reversed_client_range_returns_fail_closed_version_error(self) -> None:
        result = negotiate_handshake(_hello(version="2.0", min_version="3.0"), _server())
        assert result["type"] == "vcp-error"
        assert result["code"] == "VERSION_UNSUPPORTED"

    def test_invalid_identity_returns_structured_error(self) -> None:
        result = negotiate_handshake(_hello(identity="not-a-token"), _server())
        assert result == {
            "type": "vcp-error",
            "code": "IDENTITY_INVALID",
            "message": "The supplied VCP/I identity token is invalid",
            "retry_after": None,
        }

    def test_valid_identity_allows_negotiation(self) -> None:
        server = _server(core_features={**_core(), "future_feature": False})
        result = negotiate_handshake(_hello(identity="family.safe.guide@1.2.0"), server)
        assert result["type"] == "vcp-ack"
        assert result["core_features"]["future_feature"] is False

    def test_inputs_and_result_capabilities_are_isolated_from_mutation(self) -> None:
        hello = _hello(extensions=["VCP-X-Personal"])
        server = _server()
        expected_hello = deepcopy(hello)
        expected_server = deepcopy(server)

        result = negotiate_handshake(hello, server)
        result["capabilities"]["VCP-X-Personal"]["decay"] = False

        assert hello == expected_hello
        assert server == expected_server
        assert server["extensions"]["VCP-X-Personal"]["decay"] is True  # type: ignore[index]

    def test_non_json_values_and_wire_resource_exhaustion_are_rejected(self) -> None:
        with pytest.raises(TypeError, match="JSON serializable"):
            negotiate_handshake(_hello(opaque=object()), _server())
        with pytest.raises(ValueError, match="64 KiB"):
            negotiate_handshake(_hello(padding="x" * MAX_HANDSHAKE_BYTES), _server())


class TestMessageObjects:
    def test_hello_roundtrip_defaults_and_snapshot(self) -> None:
        raw = {
            "type": "vcp-hello",
            "version": "3.1",
            "extensions": ["VCP-X-Personal"],
            "client_id": "client-1",
        }
        hello = VCPHello.from_dict(raw)
        raw["extensions"].append("VCP-X-Torch")

        assert hello.to_dict() == {
            "type": "vcp-hello",
            "version": "3.1",
            "extensions": ["VCP-X-Personal"],
            "identity": None,
            "min_version": "1.0",
            "client_id": "client-1",
        }

    def test_hello_object_validates_range_identity_and_client_id(self) -> None:
        with pytest.raises(ValueError, match="min_version"):
            VCPHello("2.0", min_version="3.0")
        with pytest.raises(ValueError, match="identity"):
            VCPHello("3.1", identity=7)  # type: ignore[arg-type]
        with pytest.raises(ValueError, match="client_id"):
            VCPHello("3.1", client_id="")
        with pytest.raises(ValueError, match="VCP-Hello"):
            VCPHello.from_dict({"type": "wrong", "version": "3.1"})

    def test_ack_roundtrip_and_legacy_aliases(self) -> None:
        ack = VCPAck(
            version="3.1",
            supported=["VCP-X-Personal"],
            unsupported=["VCP-X-Torch"],
            capabilities={"VCP-X-Personal": {"decay": True}},
            core_features=_core(),
        )
        restored = VCPAck.from_dict(ack.to_dict())
        assert restored.active_extensions == ["VCP-X-Personal"]
        assert restored.rejected_extensions == ["VCP-X-Torch"]

    def test_ack_rejects_overlap_and_capability_leakage(self) -> None:
        with pytest.raises(ValueError, match="disjoint"):
            VCPAck("3.1", ["VCP-X-Personal"], ["VCP-X-Personal"], {}, _core())
        with pytest.raises(ValueError, match="only for supported"):
            VCPAck("3.1", [], [], {"VCP-X-Personal": {}}, _core())
        with pytest.raises(ValueError, match="VCP-Ack"):
            VCPAck.from_dict({"type": "wrong"})

    def test_error_serialization_omits_absent_supported_versions(self) -> None:
        assert VCPError("INTERNAL_ERROR", "failed").to_dict() == {
            "type": "vcp-error",
            "code": "INTERNAL_ERROR",
            "message": "failed",
            "retry_after": None,
        }

    def test_object_wrapper_filters_disabled_extensions(self) -> None:
        result = negotiate(
            VCPHello("3.1", ["VCP-X-Personal", "VCP-X-Torch"]),
            {"VCP-X-Personal": {"decay": True}, "VCP-X-Torch": False},
        )
        assert isinstance(result, VCPAck)
        assert result.supported == ["VCP-X-Personal"]
        assert result.unsupported == ["VCP-X-Torch"]

    def test_object_wrapper_returns_error_and_rejects_malformed_capabilities(self) -> None:
        error = negotiate(VCPHello("1.0"), {}, supported_versions=["2.0"])
        assert isinstance(error, VCPError)
        with pytest.raises(ValueError, match="booleans or capability objects"):
            negotiate(VCPHello("3.1"), {"VCP-X-Personal": 1})  # type: ignore[dict-item]
        with pytest.raises(TypeError, match="VCPHello"):
            negotiate({}, {})  # type: ignore[arg-type]
        with pytest.raises(TypeError, match="server_capabilities"):
            negotiate(VCPHello("3.1"), [])  # type: ignore[arg-type]
        with pytest.raises(ValueError, match="non-empty"):
            negotiate(VCPHello("3.1"), {}, supported_versions=[])
        with pytest.raises(ValueError, match="core_features"):
            negotiate(VCPHello("3.1"), {}, core_features={})

    def test_object_wrapper_accepts_boolean_true_capability(self) -> None:
        result = negotiate(
            VCPHello("3.1", ["VCP-X-Personal"]),
            {"VCP-X-Personal": True},
        )
        assert isinstance(result, VCPAck)
        assert result.capabilities == {"VCP-X-Personal": {}}
