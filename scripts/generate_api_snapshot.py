#!/usr/bin/env python3
"""Snapshot declared public package, CLI, and schema surfaces."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "api-snapshots" / "public-api.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def python_exports() -> list[str]:
    path = ROOT / "python" / "src" / "vcp" / "__init__.py"
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: set[str] = set()
    declared_all: list[str] | None = None
    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            names.update(alias.asname or alias.name for alias in node.names)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if not node.name.startswith("_"):
                names.add(node.name)
        elif isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "__all__"
            for target in node.targets
        ):
            try:
                value = ast.literal_eval(node.value)
            except (ValueError, TypeError):
                value = None
            if isinstance(value, (list, tuple)) and all(
                isinstance(item, str) for item in value
            ):
                declared_all = list(value)
    return sorted(declared_all if declared_all is not None else names)


def rust_surface() -> list[str]:
    path = ROOT / "rust" / "vcp-core" / "src" / "lib.rs"
    text = re.sub(r"//.*", "", path.read_text(encoding="utf-8"))
    statements = re.findall(r"\bpub\s+(?:mod|use)\s+.*?;", text, flags=re.DOTALL)
    return sorted(re.sub(r"\s+", " ", statement).strip() for statement in statements)


def typescript_exports() -> list[str]:
    source = ROOT / "webmcp" / "src"
    exports: set[str] = set()
    patterns = (
        re.compile(
            r"^export\s+(?:declare\s+)?(?:async\s+)?(?:function|class|const|let|var|interface|type|enum)\s+([A-Za-z_$][\w$]*)",
            re.MULTILINE,
        ),
        re.compile(r"^export\s*\{([^}]+)\}", re.MULTILINE),
    )
    for path in sorted(source.rglob("*.ts")):
        text = path.read_text(encoding="utf-8")
        for match in patterns[0].finditer(text):
            exports.add(match.group(1))
        for match in patterns[1].finditer(text):
            for raw in match.group(1).split(","):
                name = raw.strip().split(" as ")[-1].strip()
                if re.fullmatch(r"[A-Za-z_$][\w$]*", name):
                    exports.add(name)
    return sorted(exports)


def cli_commands() -> list[str]:
    path = ROOT / "rust" / "vcp-cli" / "src" / "main.rs"
    text = path.read_text(encoding="utf-8")
    match = re.search(r"enum Commands\s*\{(?P<body>.*?)\n\}", text, re.DOTALL)
    if match is None:
        raise RuntimeError("could not locate vcp-cli Commands enum")
    body = re.sub(r"///.*", "", match.group("body"))
    body = re.sub(r"\{[^{}]*\}", "", body, flags=re.DOTALL)
    return sorted(
        set(re.findall(r"^\s*([A-Z][A-Za-z0-9_]*)\s*(?:,|\{)", body, re.MULTILINE))
    )


def schema_ids() -> list[str]:
    values = []
    for path in sorted((ROOT / "schemas").glob("*.json")):
        value = json.loads(path.read_text(encoding="utf-8"))
        schema_id = value.get("$id")
        if isinstance(schema_id, str):
            values.append(schema_id)
    return sorted(values)


def build() -> dict[str, object]:
    watched = [
        ROOT / "python" / "src" / "vcp" / "__init__.py",
        ROOT / "rust" / "vcp-core" / "src" / "lib.rs",
        ROOT / "rust" / "vcp-cli" / "src" / "main.rs",
        *sorted((ROOT / "webmcp" / "src").rglob("*.ts")),
        *sorted((ROOT / "schemas").glob("*.json")),
    ]
    return {
        "schema": "vcp-public-api-snapshot/1",
        "generated_by": "scripts/generate_api_snapshot.py",
        "claim_boundary": (
            "This snapshot detects declared surface drift. It is not a complete "
            "semantic compatibility analysis and intentional changes still require review."
        ),
        "surfaces": {
            "python_top_level_exports": python_exports(),
            "rust_core_public_declarations": rust_surface(),
            "typescript_declared_exports": typescript_exports(),
            "cli_commands": cli_commands(),
            "schema_ids": schema_ids(),
        },
        "source_sha256": {
            path.relative_to(ROOT).as_posix(): sha256(path) for path in watched
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != expected:
            print("Public API snapshot is stale: api-snapshots/public-api.json")
            return 1
        print("Public API snapshot verified")
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(expected, encoding="utf-8")
    print("Public API snapshot generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
