"""Tests for VCP 3.1 Protocol Negotiation."""

from __future__ import annotations

from vcp.negotiation import VCPAck, VCPHello, negotiate


class TestVCPHello:
    """Tests for VCPHello dataclass."""

    def test_basic(self) -> None:
        hello = VCPHello(version="3.1.0")
        assert hello.version == "3.1.0"
        assert hello.supported_extensions == []
        assert hello.capabilities == {}

    def test_with_extensions(self) -> None:
        hello = VCPHello(
            version="3.1.0",
            supported_extensions=["personal", "relational"],
            capabilities={"decay": True, "torch": True},
        )
        assert len(hello.supported_extensions) == 2
        assert hello.capabilities["decay"] is True

    def test_to_dict(self) -> None:
        hello = VCPHello(
            version="3.1.0",
            supported_extensions=["personal"],
        )
        d = hello.to_dict()
        assert d["version"] == "3.1.0"
        assert d["supported_extensions"] == ["personal"]

    def test_from_dict(self) -> None:
        data = {
            "version": "3.1.0",
            "supported_extensions": ["consensus"],
            "capabilities": {"voting": True},
        }
        hello = VCPHello.from_dict(data)
        assert hello.version == "3.1.0"
        assert hello.supported_extensions == ["consensus"]

    def test_from_dict_defaults(self) -> None:
        hello = VCPHello.from_dict({"version": "3.0.0"})
        assert hello.supported_extensions == []
        assert hello.capabilities == {}


class TestVCPAck:
    """Tests for VCPAck dataclass."""

    def test_basic(self) -> None:
        ack = VCPAck(version="3.1.0")
        assert ack.active_extensions == []
        assert ack.rejected_extensions == []

    def test_to_dict(self) -> None:
        ack = VCPAck(
            version="3.1.0",
            active_extensions=["personal"],
            rejected_extensions=["consensus"],
        )
        d = ack.to_dict()
        assert d["active_extensions"] == ["personal"]
        assert d["rejected_extensions"] == ["consensus"]

    def test_from_dict(self) -> None:
        data = {
            "version": "3.1.0",
            "active_extensions": ["relational"],
        }
        ack = VCPAck.from_dict(data)
        assert ack.active_extensions == ["relational"]
        assert ack.rejected_extensions == []


class TestNegotiate:
    """Tests for negotiate function."""

    def test_all_supported(self) -> None:
        hello = VCPHello(
            version="3.1.0",
            supported_extensions=["personal", "relational"],
        )
        server_caps = {"personal": True, "relational": True}
        ack = negotiate(hello, server_caps)
        assert ack.version == "3.1.0"
        assert ack.active_extensions == ["personal", "relational"]
        assert ack.rejected_extensions == []

    def test_partial_support(self) -> None:
        hello = VCPHello(
            version="3.1.0",
            supported_extensions=["personal", "relational", "consensus"],
        )
        server_caps = {"personal": True, "relational": True, "consensus": False}
        ack = negotiate(hello, server_caps)
        assert ack.active_extensions == ["personal", "relational"]
        assert ack.rejected_extensions == ["consensus"]

    def test_none_supported(self) -> None:
        hello = VCPHello(
            version="3.1.0",
            supported_extensions=["consensus", "torch"],
        )
        server_caps = {"personal": True}
        ack = negotiate(hello, server_caps)
        assert ack.active_extensions == []
        assert ack.rejected_extensions == ["consensus", "torch"]

    def test_empty_extensions(self) -> None:
        hello = VCPHello(version="3.1.0")
        ack = negotiate(hello, {"personal": True})
        assert ack.active_extensions == []
        assert ack.rejected_extensions == []

    def test_empty_server_caps(self) -> None:
        hello = VCPHello(
            version="3.1.0",
            supported_extensions=["personal"],
        )
        ack = negotiate(hello, {})
        assert ack.active_extensions == []
        assert ack.rejected_extensions == ["personal"]

    def test_preserves_version(self) -> None:
        hello = VCPHello(version="3.0.0", supported_extensions=["personal"])
        ack = negotiate(hello, {"personal": True})
        assert ack.version == "3.0.0"

    def test_server_disabled_extension(self) -> None:
        """Extension explicitly disabled on server side."""
        hello = VCPHello(
            version="3.1.0",
            supported_extensions=["personal"],
        )
        server_caps = {"personal": False}
        ack = negotiate(hello, server_caps)
        assert ack.active_extensions == []
        assert ack.rejected_extensions == ["personal"]

    def test_order_preserved(self) -> None:
        """Client extension order is preserved in output."""
        hello = VCPHello(
            version="3.1.0",
            supported_extensions=["torch", "consensus", "personal"],
        )
        server_caps = {"torch": True, "consensus": True, "personal": True}
        ack = negotiate(hello, server_caps)
        assert ack.active_extensions == ["torch", "consensus", "personal"]
