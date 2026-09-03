"""Guard every persona vocabulary in the repository against the CSM-1 registry."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

CANONICAL_PERSONAS = frozenset(
    {"nanny", "sentinel", "godparent", "ambassador", "muse", "mediator", "custom"}
)


def _schema_enum(path: Path, *keys: str) -> list[str]:
    document = json.loads(path.read_text(encoding="utf-8"))
    node = document
    for key in keys:
        node = node[key]
    enum = node["enum"]
    assert isinstance(enum, list) and enum, f"{path}: empty persona enum at {keys}"
    return enum


def _webmcp_default_persona_ids() -> list[str]:
    source = (ROOT / "webmcp" / "src" / "tools.ts").read_text(encoding="utf-8")
    start = source.index("const DEFAULT_PERSONAS")
    end = source.index("const MAX_PERSONAS", start)
    ids = re.findall(r"id:\s*'([^']+)'", source[start:end])
    assert ids, "webmcp/src/tools.ts: no DEFAULT_PERSONAS ids found"
    return ids


class PersonaRegistryTests(unittest.TestCase):
    def assert_within_registry(self, label: str, values: list[str]) -> None:
        unknown = sorted(set(values) - CANONICAL_PERSONAS)
        self.assertEqual(
            unknown, [], f"{label} uses personas outside the CSM-1 registry"
        )
        self.assertEqual(
            len(values), len(set(values)), f"{label} has duplicate personas"
        )

    def test_manifest_v1_persona_enum(self) -> None:
        enum = _schema_enum(
            ROOT / "schemas" / "vcp-manifest-v1.schema.json",
            "properties",
            "metadata",
            "properties",
            "persona",
        )
        self.assertEqual(set(enum), CANONICAL_PERSONAS)

    def test_manifest_v2_persona_enum(self) -> None:
        enum = _schema_enum(
            ROOT / "schemas" / "vcp-manifest-v2.schema.json",
            "properties",
            "metadata",
            "properties",
            "persona",
        )
        self.assertEqual(set(enum), CANONICAL_PERSONAS)

    def test_csm1_semantics_persona_names(self) -> None:
        enum = _schema_enum(
            ROOT / "schemas" / "vcp-semantics-csm1.schema.json",
            "properties",
            "persona_name",
        )
        self.assertEqual(set(enum), CANONICAL_PERSONAS)

    def test_webmcp_default_personas(self) -> None:
        ids = _webmcp_default_persona_ids()
        self.assert_within_registry("webmcp DEFAULT_PERSONAS", ids)
        self.assertIn("ambassador", ids, "vcp_chat default persona must be configured")


if __name__ == "__main__":
    unittest.main()
