"""Contract tests for the packaged VCP MCP 2 tool surface."""

from __future__ import annotations

import asyncio
import json

import pytest
from mcp.types import CallToolRequestParams

from vcp import mcp_server


@pytest.fixture(scope="module")
def server_module():
    return mcp_server


def test_encode_context_schema_matches_all_supported_dimensions(server_module) -> None:
    tools = {tool.name: tool for tool in asyncio.run(server_module.list_tools())}
    schema = tools["vcp_encode_context"].input_schema
    properties = schema["properties"]

    assert schema["additionalProperties"] is False
    assert "state" not in properties
    assert set(properties) == {
        "time",
        "space",
        "company",
        "culture",
        "occasion",
        "environment",
        "agency",
        "constraints",
        "system_context",
        "embodiment",
        "proximity",
        "relationship",
        "formality",
        "cognitive_state",
        "emotional_tone",
        "energy_level",
        "perceived_urgency",
        "body_signals",
    }


def test_encode_context_handles_extended_and_intensity_dimensions(server_module) -> None:
    response = asyncio.run(
        server_module._handle_encode_context(
            {
                "time": "morning",
                "system_context": "testing",
                "relationship": "colleague:professional",
                "cognitive_state": {"value": "focused", "intensity": 4},
            }
        )
    )
    payload = json.loads(response[0].text)

    assert payload["wire_format"] == "⏰🌅|📡🧪|🪢colleague:professional‖🧠focused:4"
    assert payload["dimensions_set"] == [
        "time",
        "system_context",
        "relationship",
        "cognitive_state",
    ]


def test_status_reports_installed_sdk_version(server_module) -> None:
    from vcp import __version__

    response = asyncio.run(server_module._handle_status({}))
    assert json.loads(response[0].text)["version"] == __version__


def test_mcp_2_adapters_list_and_call_tools(server_module) -> None:
    listed = asyncio.run(server_module._list_tools_adapter(None, None))
    assert {tool.name for tool in listed.tools} == {
        "vcp_validate_token",
        "vcp_parse_csm1",
        "vcp_encode_context",
        "vcp_status",
    }

    called = asyncio.run(
        server_module._call_tool_adapter(
            None,
            CallToolRequestParams(
                name="vcp_validate_token",
                arguments={"token": "family.safe.guide@1.2.0"},
            ),
        )
    )
    assert called.is_error is False
    assert json.loads(called.content[0].text)["valid"] is True


def test_mcp_2_adapter_marks_unknown_tool_as_error(server_module) -> None:
    called = asyncio.run(
        server_module._call_tool_adapter(
            None,
            CallToolRequestParams(name="unknown", arguments={}),
        )
    )
    assert called.is_error is True
    assert "Unknown tool" in json.loads(called.content[0].text)["error"]


def test_mcp_2_adapter_rejects_arguments_outside_tool_schema(server_module) -> None:
    called = asyncio.run(
        server_module._call_tool_adapter(
            None,
            CallToolRequestParams(
                name="vcp_encode_context",
                arguments={"cognitive_state": {"value": "focused", "intensity": True}},
            ),
        )
    )
    assert called.is_error is True
    assert "Invalid arguments" in json.loads(called.content[0].text)["error"]
