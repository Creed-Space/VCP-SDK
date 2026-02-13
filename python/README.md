# VCP Python SDK

The Python reference implementation of the Value Context Protocol.

## Installation

```bash
pip install -r requirements.txt
```

## Structure

```
python/
├── pyproject.toml
├── requirements.txt
├── src/
│   ├── vcp/                     # Core VCP library
│   │   ├── identity/            # Identity layer (UVC tokens, namespaces)
│   │   ├── semantics/           # Semantics layer (CSM-1, personas)
│   │   └── adaptation/          # Adaptation layer (context, state)
│   ├── mcp/                     # MCP server for Claude Code
│   └── api/                     # FastAPI router
└── tests/
    ├── conftest.py
    ├── vcp/                     # Core VCP tests
    ├── unit/                    # Unit tests
    └── integration/             # Integration tests
```

## Running Tests

```bash
pytest tests/
```

## MCP Server

```bash
./src/mcp/run_vcp_server.sh
```

## See Also

- [Rust SDK](../rust/) — High-performance parsing, WASM bindings, CLI
- [Specifications](../specs/) — Core protocol specifications
- [Documentation](../docs/) — Full documentation
