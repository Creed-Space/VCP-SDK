"""
MCP server for VCP (Value Context Protocol) operations.

Exposes VCP tools via Model Context Protocol, allowing any MCP-compatible
agent to validate tokens, parse CSM1 codes, and encode context.

Tools:
- vcp_validate_token: Validate a VCP/I token string
- vcp_parse_csm1: Parse a CSM1 constitutional code
- vcp_encode_context: Encode context dimensions to VCP/A format
- vcp_status: Get VCP feature flag status
"""

import json
import logging
from typing import Any

from jsonschema import Draft202012Validator
from mcp.server import Server
from mcp.types import (
    CallToolRequestParams,
    CallToolResult,
    ContentBlock,
    ListToolsResult,
    TextContent,
    Tool,
)

logger = logging.getLogger(__name__)


_MULTI_VALUE_DIMENSIONS = frozenset({"company", "culture", "constraints"})
_DIMENSION_DESCRIPTIONS = {
    "time": "Time of day context",
    "space": "Physical space context",
    "company": "Who is present",
    "culture": "Communication style (not nationality)",
    "occasion": "Current occasion/event type",
    "agency": "Agency/authority level",
    "system_context": "Computing environment",
}


def _situational_input_properties() -> dict[str, Any]:
    """JSON Schema properties for every situational dimension (VCP/A §2.2)."""
    from vcp.adaptation.context import SituationalDimension

    properties: dict[str, Any] = {}
    for dim in SituationalDimension:
        name = dim._name
        if dim.is_free_form:
            properties[name] = {"type": "string", "pattern": "^[^:]+:[^:]+$"}
            continue
        names = list(dim.values.values())
        single: dict[str, Any] = {"type": "string", "enum": names}
        if name in _MULTI_VALUE_DIMENSIONS:
            schema: dict[str, Any] = {
                "oneOf": [
                    single,
                    {"type": "array", "items": single, "uniqueItems": True},
                ]
            }
        else:
            schema = dict(single)
        if name in _DIMENSION_DESCRIPTIONS:
            schema["description"] = _DIMENSION_DESCRIPTIONS[name]
        properties[name] = schema
    return properties


def _situational_value_summary() -> str:
    from vcp.adaptation.context import SituationalDimension

    lines = []
    for dim in SituationalDimension:
        if dim.is_free_form:
            lines.append(f"- {dim._name}: compound tie:function value")
        else:
            lines.append(f"- {dim._name}: {', '.join(dim.values.values())}")
    return "\n".join(lines)


async def list_tools() -> list[Tool]:
    """List available VCP tools."""
    return [
        Tool(
            name="vcp_validate_token",
            description="""Validate a VCP/I identity token string.

Parses the token according to the VCP/I grammar, then applies the VCP/I
semantic rules: the first segment must be a listed namespace prefix
(family, work, secure, creative, reality, company, school, ngo, religion,
culture, community, user), a Core token has exactly three segments, and no
segment is a reserved word. Returns its components:
- domain: Value domain (e.g., 'family', 'company')
- namespace_tier: core, org, community or personal
- approach: Constitutional approach (e.g., 'safe', 'balanced')
- role: Functional role (e.g., 'guide', 'guardian')
- version: Semantic version (optional)
- namespace: Namespace tier (optional)

Example tokens:
- family.safe.guide
- family.safe.guide@1.2.0
- company.acme.legal:SEC""",
            input_schema={
                "type": "object",
                "properties": {
                    "token": {
                        "type": "string",
                        "description": "VCP token (e.g., family.safe.guide@1.2.0)",
                    },
                },
                "required": ["token"],
                "additionalProperties": False,
            },
        ),
        Tool(
            name="vcp_parse_csm1",
            description="""Parse a CSM-1 constitutional code (NANO, MICRO or COMPACT tier).

A CSM-1 (Constitutional Safety Minicode) code is a one-line encoding for constitutional profiles:
- Persona: N(anny), Z(sentinel), G(odparent), A(mbassador), M(use), D(mediator), C(ustom)
- Level: 0-5 adherence level
- Scopes: F(amily), W(ork), E(ducation), H(ealth), etc.

Example codes:
- N5+F+E: Nanny persona, level 5, Family+Education scopes
- Z3+P: Sentinel persona, level 3, Privacy scope
- G4:ELEM: Godparent persona, level 4, ELEM namespace
- CS1|nanny|5|family.safe.guide|E,F: COMPACT tier, Nanny persona, level 5,
  constitution family.safe.guide, Education+Family scopes""",
            input_schema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "CSM1 code (e.g., N5+F+E)",
                    },
                },
                "required": ["code"],
                "additionalProperties": False,
            },
        ),
        Tool(
            name="vcp_encode_context",
            description="""Encode context dimensions to VCP/A format.

Encodes contextual state across the 9 baseline situational dimensions, the 4
experimental VEP-0004 situational dimensions and the 5 personal-state
dimensions. Situational values are the VCP/A §2.2 names:
"""
            + _situational_value_summary()
            + """
- personal state: cognitive_state, emotional_tone, energy_level,
  perceived_urgency, body_signals (each with optional intensity 1-5)

Returns wire format (emoji-based) and JSON format.""",
            input_schema={
                "type": "object",
                "properties": {
                    **_situational_input_properties(),
                    **{
                        name: {
                            "oneOf": [
                                {"type": "string", "minLength": 1},
                                {
                                    "type": "object",
                                    "properties": {
                                        "value": {"type": "string", "minLength": 1},
                                        "intensity": {
                                            "type": "integer",
                                            "minimum": 1,
                                            "maximum": 5,
                                        },
                                    },
                                    "required": ["value"],
                                    "additionalProperties": False,
                                },
                            ],
                        }
                        for name in (
                            "cognitive_state",
                            "emotional_tone",
                            "energy_level",
                            "perceived_urgency",
                            "body_signals",
                        )
                    },
                },
                "additionalProperties": False,
            },
        ),
        Tool(
            name="vcp_status",
            description="""Get VCP feature flag status.

Returns the current state of all VCP feature flags:
- vcp_identity_enabled: VCP/I layer active
- vcp_semantics_enabled: VCP/S layer active
- vcp_adaptation_enabled: VCP/A layer active
- vcp_full_stack_enabled: VCP/I, VCP/S and VCP/A all enabled
- vcp_strict_mode: Strict validation mode""",
            input_schema={
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        ),
    ]


async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    tools = {tool.name: tool for tool in await list_tools()}
    if name not in tools:
        raise ValueError(f"Unknown tool: {name}")
    errors = sorted(
        Draft202012Validator(tools[name].input_schema).iter_errors(arguments),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        raise ValueError(f"Invalid arguments for {name}: {errors[0].message}")

    if name == "vcp_validate_token":
        return await _handle_validate_token(arguments)
    if name == "vcp_parse_csm1":
        return await _handle_parse_csm1(arguments)
    if name == "vcp_encode_context":
        return await _handle_encode_context(arguments)
    if name == "vcp_status":
        return await _handle_status(arguments)
    raise AssertionError(f"No dispatcher for registered tool: {name}")


async def _handle_validate_token(arguments: dict[str, Any]) -> list[TextContent]:
    """Handle vcp_validate_token tool call."""
    from vcp import Token

    token_str = arguments.get("token", "")

    from vcp.identity.namespace import TokenValidationError, validate_token_semantics

    try:
        token = Token.parse(token_str)
    except ValueError as e:
        result: dict[str, Any] = {"valid": False, "error": str(e)}
    else:
        try:
            tier = validate_token_semantics(token)
        except TokenValidationError as e:
            result = {
                "valid": False,
                "syntax_valid": True,
                "error": str(e),
                "error_code": e.code,
            }
        else:
            result = {
                "valid": True,
                "canonical": token.canonical,
                "domain": token.domain,
                "approach": token.approach,
                "role": token.role,
                "version": token.version,
                "namespace": token.namespace,
                "namespace_tier": tier.value,
                "uri": token.to_uri(),
            }

    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def _handle_parse_csm1(arguments: dict[str, Any]) -> list[TextContent]:
    """Handle vcp_parse_csm1 tool call."""
    from vcp import CSM1Code

    code_str = arguments.get("code", "")

    try:
        code = CSM1Code.parse(code_str)
        result = {
            "valid": True,
            "persona": code.persona.name,
            "persona_description": code.persona.description,
            "adherence_level": code.adherence_level,
            "scopes": [s.name for s in code.scopes],
            "namespace": code.namespace,
            "version": code.version,
            "uvc_token": code.uvc_token,
            # MICRO when the code has a MICRO form; otherwise COMPACT (a custom
            # persona identified by its constitution token alone).
            "encoded": str(code),
        }
    except ValueError as e:
        result = {"valid": False, "error": str(e)}

    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def _handle_encode_context(arguments: dict[str, Any]) -> list[TextContent]:
    """Handle vcp_encode_context tool call."""
    from vcp import ContextEncoder

    def personal_state(name: str) -> tuple[str, int] | str | None:
        value = arguments.get(name)
        if isinstance(value, dict):
            raw_value = value.get("value", "")
            intensity = value.get("intensity")
            if not isinstance(raw_value, str):
                raise ValueError(f"{name}.value must be a string")
            if intensity is None:
                return raw_value
            if not isinstance(intensity, int) or isinstance(intensity, bool):
                raise ValueError(f"{name}.intensity must be an integer")
            return (raw_value, intensity)
        if value is None or isinstance(value, str):
            return value
        raise ValueError(f"{name} must be a string or value/intensity object")

    encoder = ContextEncoder()
    context = encoder.encode(
        # Situational (VCP v3.2, 13 dims)
        time=arguments.get("time"),
        space=arguments.get("space"),
        company=arguments.get("company"),
        culture=arguments.get("culture"),
        occasion=arguments.get("occasion"),
        environment=arguments.get("environment"),
        agency=arguments.get("agency"),
        constraints=arguments.get("constraints"),
        system_context=arguments.get("system_context"),
        # VEP-0004
        embodiment=arguments.get("embodiment"),
        proximity=arguments.get("proximity"),
        relationship=arguments.get("relationship"),
        formality=arguments.get("formality"),
        # Personal state (R-line)
        cognitive_state=personal_state("cognitive_state"),
        emotional_tone=personal_state("emotional_tone"),
        energy_level=personal_state("energy_level"),
        perceived_urgency=personal_state("perceived_urgency"),
        body_signals=personal_state("body_signals"),
    )

    result = {
        "wire_format": context.encode(),
        "json_format": context.to_json(),
        "dimensions_set": [
            *(dim._name for dim in context.situational),
            *(dim._name for dim in context.personal),
        ],
    }

    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def _handle_status(_arguments: dict[str, Any]) -> list[TextContent]:
    """Handle vcp_status tool call."""
    from vcp import __version__

    result = {
        "vcp_identity_enabled": True,
        "vcp_semantics_enabled": True,
        "vcp_adaptation_enabled": True,
        "vcp_full_stack_enabled": True,
        "vcp_strict_mode": True,
        "version": __version__,
    }

    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def _list_tools_adapter(_context: Any, _params: Any) -> ListToolsResult:
    """Adapt the local tool catalog to the MCP 2 low-level server API."""
    return ListToolsResult(tools=await list_tools())


async def _call_tool_adapter(_context: Any, params: CallToolRequestParams) -> CallToolResult:
    """Adapt a validated MCP request to the local dispatcher."""
    try:
        result = await call_tool(params.name, params.arguments or {})
        content: list[ContentBlock] = list(result)
        return CallToolResult(content=content)
    except (TypeError, ValueError) as exc:
        error: list[ContentBlock] = [TextContent(type="text", text=json.dumps({"error": str(exc)}))]
        return CallToolResult(content=error, is_error=True)


mcp: Server[Any] = Server(
    "vcp",
    on_list_tools=_list_tools_adapter,
    on_call_tool=_call_tool_adapter,
)


async def main() -> None:
    """Run the MCP server."""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await mcp.run(read_stream, write_stream, mcp.create_initialization_options())


def run() -> None:
    """Run the stdio MCP server from the installed console entry point."""
    import asyncio

    asyncio.run(main())


if __name__ == "__main__":
    run()
