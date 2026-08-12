"""Contract tests for the VCP MCP tool surface."""

from __future__ import annotations

import asyncio
import importlib.util
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest


class _Tool:
    def __init__(self, name: str, description: str, **kwargs: Any) -> None:
        self.name = name
        self.description = description
        self._input_schema = kwargs["inputSchema"]

    def __getattr__(self, name: str) -> Any:
        if name == "inputSchema":
            return self._input_schema
        raise AttributeError(name)


@dataclass
class _TextContent:
    type: str
    text: str


class _Server:
    def __init__(self, _name: str) -> None:
        pass

    def list_tools(self):
        return lambda function: function

    def call_tool(self):
        return lambda function: function


@pytest.fixture(scope="module")
def mcp_server():
    server_module = ModuleType("mcp.server")
    server_module.Server = _Server  # type: ignore[attr-defined]
    types_module = ModuleType("mcp.types")
    types_module.TextContent = _TextContent  # type: ignore[attr-defined]
    types_module.Tool = _Tool  # type: ignore[attr-defined]

    previous_server = sys.modules.get("mcp.server")
    previous_types = sys.modules.get("mcp.types")
    sys.modules["mcp.server"] = server_module
    sys.modules["mcp.types"] = types_module
    try:
        source = Path(__file__).parents[2] / "src" / "mcp" / "vcp_server.py"
        spec = importlib.util.spec_from_file_location("vcp_sdk_mcp_server", source)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        yield module
    finally:
        if previous_server is None:
            sys.modules.pop("mcp.server", None)
        else:
            sys.modules["mcp.server"] = previous_server
        if previous_types is None:
            sys.modules.pop("mcp.types", None)
        else:
            sys.modules["mcp.types"] = previous_types


def test_encode_context_schema_matches_all_supported_dimensions(mcp_server) -> None:
    tools = {tool.name: tool for tool in asyncio.run(mcp_server.list_tools())}
    schema = tools["vcp_encode_context"].inputSchema
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


def test_encode_context_handles_extended_and_intensity_dimensions(mcp_server) -> None:
    response = asyncio.run(
        mcp_server._handle_encode_context(
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


def test_status_reports_installed_sdk_version(mcp_server) -> None:
    from vcp import __version__

    response = asyncio.run(mcp_server._handle_status({}))
    assert json.loads(response[0].text)["version"] == __version__
