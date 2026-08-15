"""Call the asynchronous MCP tool surface with an explicit deadline."""

from __future__ import annotations

import asyncio
import json

from vcp.mcp_server import call_tool, list_tools


async def main() -> None:
    """List tools and run one bounded token-validation request."""
    tools = await asyncio.wait_for(list_tools(), timeout=2.0)
    names = {tool.name for tool in tools}
    if "vcp_validate_token" not in names:
        raise RuntimeError("required MCP tool is unavailable")

    result = await asyncio.wait_for(
        call_tool("vcp_validate_token", {"token": "family.safe.guide@1.2.0"}),
        timeout=2.0,
    )
    if len(result) != 1:
        raise RuntimeError("unexpected MCP response cardinality")
    payload = json.loads(result[0].text)
    if payload.get("valid") is not True:
        raise RuntimeError(f"token validation failed: {payload}")

    print(json.dumps({"tools": sorted(names), "validation": payload}, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
