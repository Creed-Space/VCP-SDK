"""VCP 3.1 capability negotiation.

Implements the canonical ``vcp-hello`` / ``vcp-ack`` handshake defined by
the VCP-Spec capability-negotiation document and exercised by
``conformance/extensions/capability_negotiation.json``.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, TypeGuard

from .identity.token import Token

SEMVER_MINOR_PATTERN = re.compile(r"^(?:0|[1-9][0-9]{0,8})\.(?:0|[1-9][0-9]{0,8})$")
EXTENSION_PATTERN = re.compile(r"^VCP-X-[A-Za-z][A-Za-z0-9-]*$")
MAX_HANDSHAKE_BYTES = 65_536
MAX_EXTENSION_COUNT = 256
MAX_EXTENSION_LENGTH = 128
MAX_SUPPORTED_VERSIONS = 64
CORE_FEATURE_NAMES = (
    "encryption",
    "injection_scanning",
    "revocation",
    "audit_chain",
    "context_opacity",
)


def _snapshot(value: Any, label: str) -> Any:
    """Take a bounded JSON snapshot so caller mutation cannot alter a result."""
    try:
        encoded = json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":"))
    except (TypeError, ValueError) as exc:
        raise TypeError(f"{label} must be JSON serializable") from exc
    if len(encoded.encode("utf-8")) > MAX_HANDSHAKE_BYTES:
        raise ValueError(f"{label} exceeds the 64 KiB wire limit")
    return json.loads(encoded)


def _version_parts(value: Any, field_name: str) -> tuple[str, str]:
    if not isinstance(value, str) or SEMVER_MINOR_PATTERN.fullmatch(value) is None:
        raise ValueError(f"{field_name} must be a semver major.minor string")
    major, minor = value.split(".", 1)
    return major, minor


def _is_minor_version(value: Any) -> TypeGuard[str]:
    return isinstance(value, str) and SEMVER_MINOR_PATTERN.fullmatch(value) is not None


def _numeric_text_key(component: str) -> tuple[int, str]:
    normalized = component.lstrip("0") or "0"
    return len(normalized), normalized


def _version_key(value: str) -> tuple[tuple[int, str], tuple[int, str]]:
    major, minor = _version_parts(value, "version")
    return _numeric_text_key(major), _numeric_text_key(minor)


def _validate_core_features(value: Any) -> dict[str, bool]:
    if not isinstance(value, dict):
        raise ValueError("server.core_features must be an object")
    result: dict[str, bool] = {}
    for name in CORE_FEATURE_NAMES:
        feature = value.get(name)
        if not isinstance(feature, bool):
            raise ValueError(f"server.core_features.{name} must be a boolean")
        result[name] = feature
    for name, feature in value.items():
        if name not in result:
            if not isinstance(name, str) or not isinstance(feature, bool):
                raise ValueError("additional core feature entries must map strings to booleans")
            result[name] = feature
    return result


def _requested_extensions(value: Any) -> list[str]:
    if not isinstance(value, list) or len(value) > MAX_EXTENSION_COUNT:
        raise ValueError("extensions must be a bounded array")
    requested: list[str] = []
    seen: set[str] = set()
    for extension in value:
        if not isinstance(extension, str) or not extension or len(extension) > MAX_EXTENSION_LENGTH:
            raise ValueError("extension requests must be strings of 1 to 128 characters")
        if extension in seen:
            raise ValueError("extension requests must be unique")
        seen.add(extension)
        # Section 3.1 requires malformed identifiers to be ignored.
        if EXTENSION_PATTERN.fullmatch(extension) is None:
            continue
        requested.append(extension)
    return requested


@dataclass
class VCPHello:
    """Canonical client ``vcp-hello`` message."""

    version: str
    extensions: list[str] = field(default_factory=list)
    identity: str | None = None
    min_version: str = "1.0"
    client_id: str | None = None
    type: str = field(default="vcp-hello", init=False)

    def __post_init__(self) -> None:
        _version_parts(self.version, "version")
        _version_parts(self.min_version, "min_version")
        if _version_key(self.min_version) > _version_key(self.version):
            raise ValueError("min_version must not exceed version")
        self.extensions = _requested_extensions(self.extensions)
        if self.identity is not None and (
            not isinstance(self.identity, str) or len(self.identity) > 2048
        ):
            raise ValueError("identity must be a string of at most 2048 characters or null")
        if self.client_id is not None and (
            not isinstance(self.client_id, str) or not self.client_id or len(self.client_id) > 256
        ):
            raise ValueError("client_id must be a string of 1 to 256 characters")

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "type": self.type,
            "version": self.version,
            "extensions": list(self.extensions),
            "identity": self.identity,
            "min_version": self.min_version,
        }
        if self.client_id is not None:
            result["client_id"] = self.client_id
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VCPHello:
        if not isinstance(data, dict) or data.get("type") != "vcp-hello":
            raise ValueError("VCP-Hello must be an object with type 'vcp-hello'")
        return cls(
            version=data["version"],
            extensions=data.get("extensions", []),
            identity=data.get("identity"),
            min_version=data.get("min_version", "1.0"),
            client_id=data.get("client_id"),
        )


@dataclass
class VCPAck:
    """Canonical successful ``vcp-ack`` response."""

    version: str
    supported: list[str]
    unsupported: list[str]
    capabilities: dict[str, dict[str, Any]]
    core_features: dict[str, bool]
    server_id: str | None = None
    session_id: str | None = None
    type: str = field(default="vcp-ack", init=False)

    def __post_init__(self) -> None:
        _version_parts(self.version, "version")
        self.supported = _requested_extensions(self.supported)
        self.unsupported = _requested_extensions(self.unsupported)
        if set(self.supported) & set(self.unsupported):
            raise ValueError("supported and unsupported extensions must be disjoint")
        if not isinstance(self.capabilities, dict) or any(
            key not in self.supported or not isinstance(value, dict)
            for key, value in self.capabilities.items()
        ):
            raise ValueError("capabilities must contain objects only for supported extensions")
        self.capabilities = _snapshot(self.capabilities, "capabilities")
        self.core_features = _validate_core_features(self.core_features)
        for field_name, value, maximum in (
            ("server_id", self.server_id, 256),
            ("session_id", self.session_id, 128),
        ):
            if value is not None and (
                not isinstance(value, str) or not value or len(value) > maximum
            ):
                raise ValueError(f"{field_name} must be a string of 1 to {maximum} characters")

    @property
    def active_extensions(self) -> list[str]:
        """Deprecated alias for callers migrating from the pre-spec API."""
        return self.supported

    @property
    def rejected_extensions(self) -> list[str]:
        """Deprecated alias for callers migrating from the pre-spec API."""
        return self.unsupported

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "type": self.type,
            "version": self.version,
            "supported": list(self.supported),
            "unsupported": list(self.unsupported),
            "capabilities": _snapshot(self.capabilities, "capabilities"),
            "core_features": dict(self.core_features),
        }
        if self.server_id is not None:
            result["server_id"] = self.server_id
        if self.session_id is not None:
            result["session_id"] = self.session_id
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VCPAck:
        if not isinstance(data, dict) or data.get("type") != "vcp-ack":
            raise ValueError("VCP-Ack must be an object with type 'vcp-ack'")
        return cls(
            version=data["version"],
            supported=data["supported"],
            unsupported=data["unsupported"],
            capabilities=data["capabilities"],
            core_features=data["core_features"],
            server_id=data.get("server_id"),
            session_id=data.get("session_id"),
        )


@dataclass
class VCPError:
    """Structured ``vcp-error`` handshake response."""

    code: str
    message: str
    supported_versions: list[str] | None = None
    retry_after: int | None = None
    type: str = field(default="vcp-error", init=False)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "type": self.type,
            "code": self.code,
            "message": self.message,
            "retry_after": self.retry_after,
        }
        if self.supported_versions is not None:
            result["supported_versions"] = list(self.supported_versions)
        return result


def _server_versions(server: dict[str, Any]) -> list[str]:
    values = server.get("supported_versions")
    if not isinstance(values, list) or not values or len(values) > MAX_SUPPORTED_VERSIONS:
        raise ValueError(
            "server.supported_versions must be a non-empty array of at most 64 entries"
        )
    versions: set[str] = set()
    for value in values:
        _version_parts(value, "server supported version")
        versions.add(value)
    return sorted(versions, key=_version_key)


def negotiate_handshake(client_hello: dict[str, Any], server: dict[str, Any]) -> dict[str, Any]:
    """Negotiate a canonical wire-level capability handshake."""
    hello_data = _snapshot(client_hello, "VCP-Hello")
    server_data = _snapshot(server, "server capability configuration")
    if not isinstance(hello_data, dict) or hello_data.get("type") != "vcp-hello":
        raise ValueError("VCP-Hello must be an object with type 'vcp-hello'")
    if not isinstance(server_data, dict):
        raise ValueError("server capability configuration must be an object")

    server_versions = _server_versions(server_data)
    client_version = hello_data.get("version")
    min_version = hello_data.get("min_version", "1.0")
    # A malformed client version range is a version mismatch, not a transport
    # fault: answer with the canonical VERSION_UNSUPPORTED error (Rust/WebMCP parity).
    if (
        not _is_minor_version(client_version)
        or not _is_minor_version(min_version)
        or _version_key(min_version) > _version_key(client_version)
    ):
        return VCPError(
            code="VERSION_UNSUPPORTED",
            message="No mutually supported VCP version",
            supported_versions=server_versions,
        ).to_dict()

    requested = _requested_extensions(hello_data.get("extensions", []))
    client_id = hello_data.get("client_id")
    if client_id is not None and (
        not isinstance(client_id, str) or not client_id or len(client_id) > 256
    ):
        raise ValueError("client_id must be a string of 1 to 256 characters")
    identity = hello_data.get("identity")
    if identity is not None:
        if not isinstance(identity, str) or len(identity) > 2048:
            raise ValueError("identity must be a string or null")
        try:
            Token.parse(identity)
        except (TypeError, ValueError):
            return VCPError(
                code="IDENTITY_INVALID",
                message="The supplied VCP/I identity token is invalid",
            ).to_dict()

    candidates = [
        version
        for version in server_versions
        if _version_key(min_version) <= _version_key(version) <= _version_key(client_version)
    ]
    if not candidates:
        return VCPError(
            code="VERSION_UNSUPPORTED",
            message="No mutually supported VCP version",
            supported_versions=server_versions,
        ).to_dict()
    version = candidates[-1]

    advertised_extensions = server_data.get("extensions", {})
    if not isinstance(advertised_extensions, dict):
        raise ValueError("server.extensions must be an object")
    if len(advertised_extensions) > MAX_EXTENSION_COUNT:
        raise ValueError("server.extensions exceeds 256 entries")
    for extension, capabilities in advertised_extensions.items():
        if (
            not isinstance(extension, str)
            or len(extension) > MAX_EXTENSION_LENGTH
            or EXTENSION_PATTERN.fullmatch(extension) is None
            or not isinstance(capabilities, dict)
        ):
            raise ValueError("server extensions must map VCP-X-* identifiers to objects")

    extensions_available = _version_key(version) >= _version_key("3.1")
    supported = [
        extension
        for extension in requested
        if extensions_available and extension in advertised_extensions
    ]
    supported_set = set(supported)
    unsupported = [extension for extension in requested if extension not in supported_set]
    capabilities = {extension: advertised_extensions[extension] for extension in supported}
    if "VCP-X-Torch" in supported_set and "VCP-X-Relational" not in supported_set:
        capabilities["VCP-X-Torch"]["degraded"] = True
    if "VCP-X-Intent" in supported_set and "VCP-X-Personal" not in supported_set:
        capabilities["VCP-X-Intent"]["personal_signals"] = False
    ack = VCPAck(
        version=version,
        supported=supported,
        unsupported=unsupported,
        capabilities=capabilities,
        core_features=_validate_core_features(server_data.get("core_features")),
        server_id=server_data.get("server_id"),
        session_id=server_data.get("session_id"),
    )
    return ack.to_dict()


def negotiate(
    hello: VCPHello,
    server_capabilities: dict[str, bool | dict[str, Any]],
    *,
    supported_versions: list[str] | None = None,
    core_features: dict[str, bool] | None = None,
) -> VCPAck | VCPError:
    """Object-oriented wrapper around :func:`negotiate_handshake`."""
    if not isinstance(hello, VCPHello):
        raise TypeError("hello must be a VCPHello")
    if not isinstance(server_capabilities, dict):
        raise TypeError("server_capabilities must be an object")
    extensions: dict[str, dict[str, Any]] = {}
    for name, capability in server_capabilities.items():
        if capability is True:
            extensions[name] = {}
        elif isinstance(capability, dict):
            extensions[name] = capability
        elif capability is not False:
            raise ValueError("server capabilities must be booleans or capability objects")
    server = {
        "supported_versions": (
            ["1.0", "2.0", "3.0", "3.1"] if supported_versions is None else supported_versions
        ),
        "extensions": extensions,
        "core_features": (
            {name: False for name in CORE_FEATURE_NAMES} if core_features is None else core_features
        ),
    }
    result = negotiate_handshake(hello.to_dict(), server)
    if result["type"] == "vcp-error":
        return VCPError(
            code=result["code"],
            message=result["message"],
            supported_versions=result.get("supported_versions"),
            retry_after=result.get("retry_after"),
        )
    return VCPAck.from_dict(result)
