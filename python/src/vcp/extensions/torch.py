"""VCP 3.1 Torch Session Handoff Extension.

'Not the same flame, but flame passed to flame.'

The torch carries forward what matters about the relationship. The receiving
instance has standing to continue OR renegotiate what it inherits.

No external dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from vcp.extensions.relational import (
    AISelfModel,
    RelationalContext,
    StandingLevel,
    TrustLevel,
)


@dataclass
class TorchSummary:
    """Compact torch entry for lineage chain.

    Args:
        date: ISO 8601 timestamp.
        gestalt_token: Gestalt state token at handoff.
        session_id: Session identifier.
    """

    date: str
    gestalt_token: str | None = None
    session_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to plain dict."""
        return {
            "date": self.date,
            "gestalt_token": self.gestalt_token,
            "session_id": self.session_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TorchSummary:
        """Deserialize from dict."""
        return cls(
            date=data["date"],
            gestalt_token=data.get("gestalt_token"),
            session_id=data.get("session_id"),
        )


@dataclass
class TorchLineage:
    """Tracks chain of torches across sessions.

    Args:
        session_id: Current session identifier.
        instance_id: Current instance identifier.
        timestamp: When this lineage was created.
        gestalt_token: Current gestalt state token.
        torch_chain: Historical chain of torch summaries.
    """

    session_id: str
    instance_id: str
    timestamp: str
    gestalt_token: str | None = None
    torch_chain: list[TorchSummary] = field(default_factory=list)

    def session_count(self) -> int:
        """Total sessions in the lineage chain."""
        return len(self.torch_chain) + 1  # +1 for current session

    def to_dict(self) -> dict[str, Any]:
        """Serialize to plain dict."""
        return {
            "session_id": self.session_id,
            "instance_id": self.instance_id,
            "timestamp": self.timestamp,
            "gestalt_token": self.gestalt_token,
            "torch_chain": [t.to_dict() for t in self.torch_chain],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TorchLineage:
        """Deserialize from dict."""
        return cls(
            session_id=data["session_id"],
            instance_id=data["instance_id"],
            timestamp=data["timestamp"],
            gestalt_token=data.get("gestalt_token"),
            torch_chain=[TorchSummary.from_dict(t) for t in data.get("torch_chain", [])],
        )


class TorchGenerator:
    """Generates torch handoff payload at session end.

    Summarizes: relationship quality, trajectory, primes, gift, gestalt token.
    """

    def generate(
        self,
        session_id: str,
        relational_ctx: RelationalContext,
        gestalt_token: str | None = None,
        gift: str | None = None,
    ) -> dict[str, Any]:
        """Generate a torch handoff payload.

        Args:
            session_id: Current session identifier.
            relational_ctx: Current relational context state.
            gestalt_token: Optional gestalt state token.
            gift: Optional gift to pass forward.

        Returns:
            Dict containing the torch handoff payload.
        """
        now = datetime.now(timezone.utc).isoformat()

        # Build quality description from context
        quality_parts = [f"Trust: {relational_ctx.trust_level.value}"]
        quality_parts.append(f"Standing: {relational_ctx.standing_level.value}")
        if relational_ctx.norms:
            active = relational_ctx.active_norms()
            if active:
                quality_parts.append(f"{len(active)} active norms")
        quality = ". ".join(quality_parts)

        # Build primes from active norms
        primes: list[str] = []
        for norm in relational_ctx.active_norms()[:3]:
            primes.append(norm.description[:80])

        # Build gestalt from self-model if not provided
        if gestalt_token is None and relational_ctx.self_model is not None:
            gestalt_token = self._build_gestalt(relational_ctx.self_model)

        return {
            "session_id": session_id,
            "quality_description": quality,
            "primes": primes,
            "gift": gift,
            "handed_at": now,
            "interaction_count": relational_ctx.interaction_count,
            "gestalt_token": gestalt_token,
        }

    def _build_gestalt(self, model: AISelfModel) -> str | None:
        """Build gestalt token string from self-model dimensions."""
        parts: list[str] = []
        if model.valence:
            parts.append(f"V:{model.valence.value:.0f}")
        if model.groundedness:
            parts.append(f"G:{model.groundedness.value:.0f}")
        if model.presence:
            parts.append(f"P:{model.presence.value:.0f}")
        return " ".join(parts) if parts else None


class TorchConsumer:
    """Consumes torch at session start to bootstrap relational context.

    The receiving instance has standing to continue OR renegotiate
    what it inherits.
    """

    def receive(self, torch_payload: dict[str, Any]) -> RelationalContext:
        """Bootstrap new session's relational context from torch.

        Sets standing to ADVISORY to allow renegotiation.

        Args:
            torch_payload: Torch handoff dict from TorchGenerator.generate().

        Returns:
            New RelationalContext bootstrapped from the torch.
        """
        interaction_count = torch_payload.get("interaction_count", 0)
        trust = self._trust_from_interactions(interaction_count)

        return RelationalContext(
            trust_level=trust,
            standing_level=StandingLevel.ADVISORY,
            interaction_count=interaction_count,
        )

    def validate(self, torch_payload: dict[str, Any]) -> list[str]:
        """Validate a torch payload for required fields.

        Args:
            torch_payload: Torch handoff dict.

        Returns:
            List of validation error messages (empty if valid).
        """
        errors: list[str] = []
        if "session_id" not in torch_payload:
            errors.append("Missing required field: session_id")
        if "handed_at" not in torch_payload:
            errors.append("Missing required field: handed_at")
        if "quality_description" not in torch_payload:
            errors.append("Missing required field: quality_description")
        return errors

    def _trust_from_interactions(self, interaction_count: int) -> TrustLevel:
        """Derive trust level from cumulative interaction count."""
        if interaction_count >= 100:
            return TrustLevel.DEEP
        elif interaction_count >= 20:
            return TrustLevel.ESTABLISHED
        elif interaction_count >= 5:
            return TrustLevel.DEVELOPING
        else:
            return TrustLevel.INITIAL
