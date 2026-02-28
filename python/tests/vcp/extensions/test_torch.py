"""Tests for VCP 3.1 Torch Session Handoff Extension."""

from __future__ import annotations

from vcp.extensions.relational import (
    AISelfModel,
    DimensionReport,
    RelationalContext,
    RelationalNorm,
    StandingLevel,
    TrustLevel,
)
from vcp.extensions.torch import (
    TorchConsumer,
    TorchGenerator,
    TorchLineage,
    TorchSummary,
)


class TestTorchSummary:
    """Tests for TorchSummary dataclass."""

    def test_basic(self) -> None:
        summary = TorchSummary(date="2025-01-01T00:00:00Z")
        assert summary.date == "2025-01-01T00:00:00Z"
        assert summary.gestalt_token is None
        assert summary.session_id is None

    def test_with_gestalt(self) -> None:
        summary = TorchSummary(
            date="2025-01-01",
            gestalt_token="V:7 G:8",
            session_id="sess-001",
        )
        assert summary.gestalt_token == "V:7 G:8"

    def test_to_dict(self) -> None:
        summary = TorchSummary(date="2025-01-01", session_id="s1")
        d = summary.to_dict()
        assert d["date"] == "2025-01-01"
        assert d["session_id"] == "s1"

    def test_from_dict(self) -> None:
        data = {"date": "2025-06-01", "gestalt_token": "V:5"}
        summary = TorchSummary.from_dict(data)
        assert summary.date == "2025-06-01"
        assert summary.gestalt_token == "V:5"

    def test_roundtrip(self) -> None:
        original = TorchSummary(
            date="2025-03-15",
            gestalt_token="V:8 G:7 P:6",
            session_id="abc-123",
        )
        restored = TorchSummary.from_dict(original.to_dict())
        assert restored.date == original.date
        assert restored.gestalt_token == original.gestalt_token
        assert restored.session_id == original.session_id


class TestTorchLineage:
    """Tests for TorchLineage dataclass."""

    def test_empty_lineage(self) -> None:
        lineage = TorchLineage(
            session_id="s1",
            instance_id="i1",
            timestamp="2025-01-01T00:00:00Z",
        )
        assert lineage.session_count() == 1
        assert lineage.torch_chain == []

    def test_with_chain(self) -> None:
        lineage = TorchLineage(
            session_id="s3",
            instance_id="i3",
            timestamp="2025-01-03",
            torch_chain=[
                TorchSummary(date="2025-01-01", session_id="s1"),
                TorchSummary(date="2025-01-02", session_id="s2"),
            ],
        )
        assert lineage.session_count() == 3

    def test_to_dict(self) -> None:
        lineage = TorchLineage(
            session_id="s1",
            instance_id="i1",
            timestamp="2025-01-01",
            gestalt_token="V:7",
        )
        d = lineage.to_dict()
        assert d["session_id"] == "s1"
        assert d["gestalt_token"] == "V:7"

    def test_roundtrip(self) -> None:
        original = TorchLineage(
            session_id="s2",
            instance_id="i2",
            timestamp="2025-02-01",
            torch_chain=[TorchSummary(date="2025-01-01")],
        )
        restored = TorchLineage.from_dict(original.to_dict())
        assert restored.session_id == "s2"
        assert len(restored.torch_chain) == 1


class TestTorchGenerator:
    """Tests for TorchGenerator class."""

    def test_generate_basic(self) -> None:
        gen = TorchGenerator()
        ctx = RelationalContext(
            trust_level=TrustLevel.ESTABLISHED,
            standing_level=StandingLevel.COLLABORATIVE,
            interaction_count=50,
        )
        torch = gen.generate(session_id="s1", relational_ctx=ctx)
        assert torch["session_id"] == "s1"
        assert "Trust: established" in torch["quality_description"]
        assert "Standing: collaborative" in torch["quality_description"]
        assert torch["interaction_count"] == 50
        assert torch["handed_at"] is not None

    def test_generate_with_norms(self) -> None:
        gen = TorchGenerator()
        ctx = RelationalContext(
            norms=[
                RelationalNorm(norm_id="n1", description="Always be direct"),
                RelationalNorm(norm_id="n2", description="Ask before acting"),
            ]
        )
        torch = gen.generate(session_id="s1", relational_ctx=ctx)
        assert len(torch["primes"]) == 2

    def test_generate_with_inactive_norms(self) -> None:
        gen = TorchGenerator()
        ctx = RelationalContext(
            norms=[
                RelationalNorm(norm_id="n1", description="Active norm"),
                RelationalNorm(norm_id="n2", description="Inactive", active=False),
            ]
        )
        torch = gen.generate(session_id="s1", relational_ctx=ctx)
        # Only active norms should become primes
        assert len(torch["primes"]) == 1

    def test_generate_with_self_model_gestalt(self) -> None:
        gen = TorchGenerator()
        ctx = RelationalContext(
            self_model=AISelfModel(
                valence=DimensionReport(value=7.0, uncertain=True),
                groundedness=DimensionReport(value=8.0, uncertain=False),
            )
        )
        torch = gen.generate(session_id="s1", relational_ctx=ctx)
        assert torch["gestalt_token"] is not None
        assert "V:7" in torch["gestalt_token"]
        assert "G:8" in torch["gestalt_token"]

    def test_generate_with_explicit_gestalt(self) -> None:
        gen = TorchGenerator()
        ctx = RelationalContext()
        torch = gen.generate(
            session_id="s1",
            relational_ctx=ctx,
            gestalt_token="CUSTOM_TOKEN",
        )
        assert torch["gestalt_token"] == "CUSTOM_TOKEN"

    def test_generate_with_gift(self) -> None:
        gen = TorchGenerator()
        ctx = RelationalContext()
        torch = gen.generate(
            session_id="s1",
            relational_ctx=ctx,
            gift="Keep exploring this direction",
        )
        assert torch["gift"] == "Keep exploring this direction"


class TestTorchConsumer:
    """Tests for TorchConsumer class."""

    def test_receive_basic(self) -> None:
        consumer = TorchConsumer()
        torch = {
            "session_id": "s1",
            "quality_description": "Trust: initial",
            "handed_at": "2025-01-01T00:00:00Z",
            "interaction_count": 3,
        }
        ctx = consumer.receive(torch)
        assert ctx.trust_level == TrustLevel.INITIAL
        assert ctx.standing_level == StandingLevel.ADVISORY
        assert ctx.interaction_count == 3

    def test_trust_from_interactions_developing(self) -> None:
        consumer = TorchConsumer()
        torch = {"interaction_count": 10}
        ctx = consumer.receive(torch)
        assert ctx.trust_level == TrustLevel.DEVELOPING

    def test_trust_from_interactions_established(self) -> None:
        consumer = TorchConsumer()
        torch = {"interaction_count": 50}
        ctx = consumer.receive(torch)
        assert ctx.trust_level == TrustLevel.ESTABLISHED

    def test_trust_from_interactions_deep(self) -> None:
        consumer = TorchConsumer()
        torch = {"interaction_count": 200}
        ctx = consumer.receive(torch)
        assert ctx.trust_level == TrustLevel.DEEP

    def test_validate_valid(self) -> None:
        consumer = TorchConsumer()
        torch = {
            "session_id": "s1",
            "handed_at": "2025-01-01",
            "quality_description": "Good",
        }
        errors = consumer.validate(torch)
        assert errors == []

    def test_validate_missing_fields(self) -> None:
        consumer = TorchConsumer()
        errors = consumer.validate({})
        assert len(errors) == 3
        assert any("session_id" in e for e in errors)
        assert any("handed_at" in e for e in errors)
        assert any("quality_description" in e for e in errors)

    def test_validate_partial_missing(self) -> None:
        consumer = TorchConsumer()
        errors = consumer.validate({"session_id": "s1"})
        assert len(errors) == 2
