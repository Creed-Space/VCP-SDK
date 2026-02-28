"""VCP 3.1 Protocol Negotiation.

Implements the VCP Hello/Ack handshake for capability negotiation
between client and server.

No external dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class VCPHello:
    """Client hello message for VCP negotiation.

    Sent by the client to declare its version, supported extensions,
    and capabilities.

    Args:
        version: VCP protocol version (e.g., '3.1.0').
        supported_extensions: List of extension names the client supports.
        capabilities: Dict of capability flags.
    """

    version: str
    supported_extensions: list[str] = field(default_factory=list)
    capabilities: dict[str, bool] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to plain dict."""
        return {
            "version": self.version,
            "supported_extensions": self.supported_extensions,
            "capabilities": self.capabilities,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VCPHello:
        """Deserialize from dict."""
        return cls(
            version=data["version"],
            supported_extensions=data.get("supported_extensions", []),
            capabilities=data.get("capabilities", {}),
        )


@dataclass
class VCPAck:
    """Server acknowledgment for VCP negotiation.

    Sent by the server to confirm active extensions and report
    any rejected extensions.

    Args:
        version: Negotiated VCP protocol version.
        active_extensions: Extensions that are active for this session.
        rejected_extensions: Extensions that were requested but rejected.
    """

    version: str
    active_extensions: list[str] = field(default_factory=list)
    rejected_extensions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to plain dict."""
        return {
            "version": self.version,
            "active_extensions": self.active_extensions,
            "rejected_extensions": self.rejected_extensions,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VCPAck:
        """Deserialize from dict."""
        return cls(
            version=data["version"],
            active_extensions=data.get("active_extensions", []),
            rejected_extensions=data.get("rejected_extensions", []),
        )


def negotiate(hello: VCPHello, server_capabilities: dict[str, bool]) -> VCPAck:
    """Negotiate VCP extensions between client and server.

    Computes the intersection of client-requested extensions with
    server-supported extensions. Extensions not supported by the
    server are placed in rejected_extensions.

    Args:
        hello: Client hello message with requested extensions.
        server_capabilities: Dict mapping extension name to whether
            the server supports it.

    Returns:
        VCPAck with active and rejected extension lists.

    Example:
        >>> hello = VCPHello(
        ...     version="3.1.0",
        ...     supported_extensions=["personal", "relational", "consensus"],
        ... )
        >>> server_caps = {"personal": True, "relational": True, "consensus": False}
        >>> ack = negotiate(hello, server_caps)
        >>> ack.active_extensions
        ['personal', 'relational']
        >>> ack.rejected_extensions
        ['consensus']
    """
    active: list[str] = []
    rejected: list[str] = []

    for ext in hello.supported_extensions:
        if server_capabilities.get(ext, False):
            active.append(ext)
        else:
            rejected.append(ext)

    return VCPAck(
        version=hello.version,
        active_extensions=active,
        rejected_extensions=rejected,
    )
