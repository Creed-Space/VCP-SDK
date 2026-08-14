"""Cross-layer integration tests that run entirely inside VCP-SDK."""

from __future__ import annotations

import asyncio
import json

from mcp.types import CallToolRequestParams

from vcp import (
    ContextEncoder,
    CSM1Code,
    Dimension,
    Persona,
    StateTracker,
    Token,
    TransitionSeverity,
)
from vcp.mcp_server import _call_tool_adapter


def test_public_cross_layer_exports_are_available() -> None:
    assert all((Token, CSM1Code, ContextEncoder, StateTracker, Persona, Dimension))


def test_identity_and_semantics_parse_together() -> None:
    token = Token.parse("family.safe.guide@1.0.0")
    code = CSM1Code.parse("N5+F+E")

    assert token.domain == "family"
    assert token.role == "guide"
    assert code.persona is Persona.NANNY
    assert code.encode() == "N5+E+F"


def test_every_current_persona_roundtrips() -> None:
    for code_char, persona in {
        "N": Persona.NANNY,
        "Z": Persona.SENTINEL,
        "G": Persona.GODPARENT,
        "A": Persona.AMBASSADOR,
        "M": Persona.MUSE,
        "D": Persona.MEDIATOR,
    }.items():
        assert CSM1Code.parse(f"{code_char}3").persona is persona
    assert CSM1Code.parse("C3:ACME").persona is Persona.CUSTOM


def test_context_encoding_and_state_tracking_integrate() -> None:
    encoder = ContextEncoder()
    tracker = StateTracker()

    first = encoder.encode(time="morning", space="home")
    assert tracker.record(first) is None

    second = encoder.encode(time="evening", space="office")
    transition = tracker.record(second)
    assert transition is not None
    assert transition.changed_dimensions


def test_emergency_context_elevates_transition_severity() -> None:
    encoder = ContextEncoder()
    tracker = StateTracker()

    tracker.record(encoder.encode(time="morning"))
    transition = tracker.record(encoder.encode(occasion="emergency"))

    assert transition is not None
    assert transition.severity is TransitionSeverity.EMERGENCY


def test_mcp_adapter_uses_the_same_identity_parser() -> None:
    result = asyncio.run(
        _call_tool_adapter(
            None,
            CallToolRequestParams(
                name="vcp_validate_token",
                arguments={"token": "family.safe.guide@1.0.0"},
            ),
        )
    )

    assert result.is_error is False
    payload = json.loads(result.content[0].text)
    assert payload["canonical"] == "family.safe.guide"
