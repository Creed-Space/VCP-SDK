"""Access to the exact bundled Agent Runtime Profile candidate schema."""

from __future__ import annotations

import hashlib
import json
from importlib.resources import files
from typing import Any

_SCHEMA_NAME = "vcp-agent-runtime-profile-v0.1.schema.json"


def agent_runtime_schema_bytes() -> bytes:
    resource = files("vcp.agent.schemas").joinpath(_SCHEMA_NAME)
    return resource.read_bytes()


def agent_runtime_schema() -> dict[str, Any]:
    loaded = json.loads(agent_runtime_schema_bytes())
    if not isinstance(loaded, dict):
        raise ValueError("bundled Agent Runtime schema must contain an object")
    return loaded


def agent_runtime_schema_digest() -> str:
    return f"sha256:{hashlib.sha256(agent_runtime_schema_bytes()).hexdigest()}"
