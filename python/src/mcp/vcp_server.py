"""
MCP server for VCP (Value-Context Protocol) operations.

Exposes VCP tools via Model Context Protocol, allowing any MCP-compatible
agent to validate tokens, parse CSM1 codes, and encode context.

Tools:
- vcp_validate_token: Validate a VCP/I token string
- vcp_parse_csm1: Parse a CSM1 constitutional code
- vcp_encode_context: Encode context dimensions to VCP/A format
- vcp_status: Get VCP feature flag status
"""

import logging

from mcp.server import Server
from mcp.types import TextContent, Tool

logger = logging.getLogger(__name__)

# Create MCP server
mcp = Server("vcp")


@mcp.list_tools()
async def list_tools():
    """List available VCP tools."""
    return [
        Tool(
            name="vcp_validate_token",
            description="""Validate a VCP/I identity token string.

Parses the token according to VCP/I grammar and returns its components:
- domain: Value domain (e.g., 'family', 'company')
- approach: Constitutional approach (e.g., 'safe', 'balanced')
- role: Functional role (e.g., 'guide', 'guardian')
- version: Semantic version (optional)
- namespace: Namespace tier (optional)

Example tokens:
- family.safe.guide
- family.safe.guide@1.2.0
- company.acme.legal:SEC""",
            inputSchema={
                "type": "object",
                "properties": {
                    "token": {
                        "type": "string",
                        "description": "VCP token (e.g., family.safe.guide@1.2.0)",
                    },
                },
                "required": ["token"],
            },
        ),
        Tool(
            name="vcp_parse_csm1",
            description="""Parse a CSM1 constitutional code.

CSM1 (Constitutional Semantics Mark 1) is a compact encoding for constitutional profiles:
- Persona: N(anny), Z(sentinel), G(odparent), A(mbassador), M(use), R(anchor), H(otrod), C(ustom)
- Level: 0-5 adherence level
- Scopes: F(amily), W(ork), E(ducation), H(ealth), etc.

Example codes:
- N5+F+E: Nanny persona, level 5, Family+Education scopes
- Z3+P: Sentinel persona, level 3, Privacy scope
- G4:ELEM: Godparent persona, level 4, ELEM namespace""",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "CSM1 code (e.g., N5+F+E)",
                    },
                },
                "required": ["code"],
            },
        ),
        Tool(
            name="vcp_encode_context",
            description="""Encode context dimensions to VCP/A format.

Encodes contextual state across 9 dimensions:
- time: morning, midday, evening, night
- space: home, office, school, hospital, transit
- company: alone, children, colleagues, family, strangers
- culture: global, american, european, japanese
- occasion: normal, celebration, mourning, emergency
- state: happy, anxious, tired, contemplative, frustrated
- environment: comfortable, hot, cold, quiet, noisy
- agency: leader, peer, subordinate, limited
- constraints: minimal, legal, economic, time

Returns wire format (emoji-based) and JSON format.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "time": {
                        "type": "string",
                        "enum": ["morning", "midday", "evening", "night"],
                        "description": "Time of day context",
                    },
                    "space": {
                        "type": "string",
                        "enum": ["home", "office", "school", "hospital", "transit"],
                        "description": "Physical space context",
                    },
                    "company": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Who is present (alone, children, colleagues, family)",
                    },
                    "occasion": {
                        "type": "string",
                        "enum": ["normal", "celebration", "mourning", "emergency"],
                        "description": "Current occasion/event type",
                    },
                    "state": {
                        "type": "string",
                        "enum": ["happy", "anxious", "tired", "contemplative", "frustrated"],
                        "description": "Mental/emotional state",
                    },
                    "agency": {
                        "type": "string",
                        "enum": ["leader", "peer", "subordinate", "limited"],
                        "description": "Agency/authority level",
                    },
                },
            },
        ),
        Tool(
            name="vcp_status",
            description="""Get VCP feature flag status.

Returns the current state of all VCP feature flags:
- vcp_identity_enabled: VCP/I layer active
- vcp_semantics_enabled: VCP/S layer active
- vcp_adaptation_enabled: VCP/A layer active
- vcp_full_stack_enabled: All layers active
- vcp_strict_mode: Strict validation mode""",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@mcp.call_tool()
async def call_tool(name: str, arguments: dict):
    """Handle tool calls."""
    import json

    if name == "vcp_validate_token":
        return await _handle_validate_token(arguments)
    elif name == "vcp_parse_csm1":
        return await _handle_parse_csm1(arguments)
    elif name == "vcp_encode_context":
        return await _handle_encode_context(arguments)
    elif name == "vcp_status":
        return await _handle_status(arguments)
    else:
        return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]


async def _handle_validate_token(arguments: dict):
    """Handle vcp_validate_token tool call."""
    import json

    from vcp import Token

    token_str = arguments.get("token", "")

    try:
        token = Token.parse(token_str)
        result = {
            "valid": True,
            "canonical": token.canonical,
            "domain": token.domain,
            "approach": token.approach,
            "role": token.role,
            "version": token.version,
            "namespace": token.namespace,
            "uri": token.to_uri(),
        }
    except ValueError as e:
        result = {"valid": False, "error": str(e)}

    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def _handle_parse_csm1(arguments: dict):
    """Handle vcp_parse_csm1 tool call."""
    import json

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
            "encoded": code.encode(),
        }
    except ValueError as e:
        result = {"valid": False, "error": str(e)}

    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def _handle_encode_context(arguments: dict):
    """Handle vcp_encode_context tool call."""
    import json

    from vcp import ContextEncoder

    encoder = ContextEncoder()
    context = encoder.encode(
        time=arguments.get("time"),
        space=arguments.get("space"),
        company=arguments.get("company"),
        culture=arguments.get("culture"),
        occasion=arguments.get("occasion"),
        state=arguments.get("state"),
        environment=arguments.get("environment"),
        agency=arguments.get("agency"),
        constraints=arguments.get("constraints"),
    )

    result = {
        "wire_format": context.encode(),
        "json_format": context.to_json(),
        "dimensions_set": [dim._name for dim in context.dimensions.keys()],
    }

    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def _handle_status(arguments: dict):
    """Handle vcp_status tool call."""
    import json

    try:
        from services.feature_flags import is_feature_enabled
    except ImportError:
        def is_feature_enabled(flag: str) -> bool:  # type: ignore[misc]
            return True

    result = {
        "vcp_identity_enabled": is_feature_enabled("vcp_identity_enabled"),
        "vcp_semantics_enabled": is_feature_enabled("vcp_semantics_enabled"),
        "vcp_adaptation_enabled": is_feature_enabled("vcp_adaptation_enabled"),
        "vcp_full_stack_enabled": is_feature_enabled("vcp_full_stack_enabled"),
        "vcp_strict_mode": is_feature_enabled("vcp_strict_mode"),
        "version": "2.0.0",
    }

    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def main():
    """Run the MCP server."""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await mcp.run(read_stream, write_stream, mcp.create_initialization_options())


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
