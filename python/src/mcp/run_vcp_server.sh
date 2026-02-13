#!/bin/bash
# Run VCP MCP server
cd "$(dirname "$0")/../.."
exec python3 -m services.mcp.vcp_server
