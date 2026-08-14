#!/usr/bin/env python3
"""Generate deterministic CycloneDX SBOMs for the three SDK ecosystems."""

from __future__ import annotations

import argparse
import base64
import json
import re
import subprocess
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - exercised on Python 3.10 CI
    import tomli as tomllib

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_URL = "https://github.com/Creed-Space/VCP-SDK"
LOCK_REQUIREMENT = re.compile(r"^([A-Za-z0-9_.-]+)==([^\s\\]+)", re.MULTILINE)


def command(*arguments: str, cwd: Path = ROOT) -> str:
    return subprocess.run(
        arguments,
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def normalized_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def component_ref(ecosystem: str, name: str, version: str) -> str:
    return f"pkg:{ecosystem}/{name}@{version}"


def component(
    ecosystem: str,
    name: str,
    version: str,
    *,
    properties: list[dict[str, str]] | None = None,
    hashes: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    ref = component_ref(ecosystem, name, version)
    result: dict[str, Any] = {
        "type": "library",
        "bom-ref": ref,
        "name": name,
        "version": version,
        "purl": ref,
    }
    if properties:
        result["properties"] = properties
    if hashes:
        result["hashes"] = hashes
    return result


def document(
    name: str,
    version: str,
    ecosystem: str,
    components: list[dict[str, Any]],
    dependencies: list[dict[str, Any]],
    git_head: str,
    timestamp: str,
) -> dict[str, Any]:
    root_ref = component_ref(ecosystem, name, version)
    serial = uuid.uuid5(uuid.NAMESPACE_URL, f"{REPOSITORY_URL}@{git_head}/{ecosystem}")
    return {
        "$schema": "https://cyclonedx.org/schema/bom-1.6.schema.json",
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "serialNumber": f"urn:uuid:{serial}",
        "version": 1,
        "metadata": {
            "timestamp": timestamp,
            "tools": {
                "components": [
                    {
                        "type": "application",
                        "name": "vcp-release-sbom-generator",
                        "version": "1",
                    }
                ]
            },
            "component": {
                "type": "library",
                "bom-ref": root_ref,
                "name": name,
                "version": version,
                "purl": root_ref,
                "externalReferences": [
                    {"type": "vcs", "url": f"{REPOSITORY_URL}#{git_head}"}
                ],
                "properties": [{"name": "vcp:git_sha", "value": git_head}],
            },
        },
        "components": sorted(components, key=lambda item: item["bom-ref"]),
        "dependencies": sorted(dependencies, key=lambda item: item["ref"]),
    }


def python_sbom(git_head: str, timestamp: str) -> dict[str, Any]:
    pyproject = tomllib.loads((ROOT / "python" / "pyproject.toml").read_text())
    project = pyproject["project"]
    resolved = {
        normalized_name(name): version
        for name, version in LOCK_REQUIREMENT.findall(
            (ROOT / "python" / "requirements-dev.lock").read_text()
        )
    }
    components = [
        component(
            "pypi",
            name,
            version,
            properties=[
                {
                    "name": "vcp:inventory_scope",
                    "value": "locked build, test, runtime, and optional dependency set",
                }
            ],
        )
        for name, version in resolved.items()
        if name != normalized_name(project["name"])
    ]
    root_ref = component_ref("pypi", project["name"], project["version"])
    dependencies = [
        {"ref": root_ref, "dependsOn": sorted(item["bom-ref"] for item in components)}
    ]
    dependencies.extend(
        {"ref": item["bom-ref"], "dependsOn": []} for item in components
    )
    return document(
        project["name"],
        project["version"],
        "pypi",
        components,
        dependencies,
        git_head,
        timestamp,
    )


def rust_sbom(git_head: str, timestamp: str) -> dict[str, Any]:
    metadata = json.loads(
        command(
            "cargo",
            "metadata",
            "--locked",
            "--format-version",
            "1",
            cwd=ROOT / "rust",
        )
    )
    packages = {package["id"]: package for package in metadata["packages"]}
    workspace_ids = set(metadata["workspace_members"])
    components: list[dict[str, Any]] = []
    refs: dict[str, str] = {}
    for package_id, package in packages.items():
        ref = component_ref("cargo", package["name"], package["version"])
        refs[package_id] = ref
        if package_id not in workspace_ids:
            components.append(component("cargo", package["name"], package["version"]))
    dependencies: list[dict[str, Any]] = []
    for node in metadata["resolve"]["nodes"]:
        if node["id"] in workspace_ids:
            continue
        dependencies.append(
            {
                "ref": refs[node["id"]],
                "dependsOn": sorted(
                    refs[item]
                    for item in node["dependencies"]
                    if item not in workspace_ids
                ),
            }
        )
    workspace = tomllib.loads((ROOT / "rust" / "Cargo.toml").read_text())
    version = workspace["workspace"]["package"]["version"]
    root_ref = component_ref("cargo", "vcp-sdk-rust-workspace", version)
    direct = sorted(
        {
            refs[dependency]
            for node in metadata["resolve"]["nodes"]
            if node["id"] in workspace_ids
            for dependency in node["dependencies"]
            if dependency not in workspace_ids
        }
    )
    dependencies.append({"ref": root_ref, "dependsOn": direct})
    return document(
        "vcp-sdk-rust-workspace",
        version,
        "cargo",
        components,
        dependencies,
        git_head,
        timestamp,
    )


def sri_hash(integrity: str) -> list[dict[str, str]]:
    if "-" not in integrity:
        return []
    algorithm, encoded = integrity.split("-", 1)
    names = {"sha256": "SHA-256", "sha384": "SHA-384", "sha512": "SHA-512"}
    if algorithm not in names:
        return []
    try:
        content = base64.b64decode(encoded, validate=True).hex()
    except ValueError:
        return []
    return [{"alg": names[algorithm], "content": content}]


def npm_sbom(git_head: str, timestamp: str) -> dict[str, Any]:
    package = json.loads((ROOT / "webmcp" / "package.json").read_text())
    lock = json.loads((ROOT / "webmcp" / "package-lock.json").read_text())
    components_by_ref: dict[str, dict[str, Any]] = {}
    for path, item in lock.get("packages", {}).items():
        if not path or "version" not in item:
            continue
        name = item.get("name")
        if not name:
            marker = "node_modules/"
            name = path.rsplit(marker, 1)[-1]
        properties = [
            {
                "name": "vcp:development_dependency",
                "value": str(bool(item.get("dev"))).lower(),
            }
        ]
        value = component(
            "npm",
            name,
            item["version"],
            properties=properties,
            hashes=sri_hash(item.get("integrity", "")),
        )
        components_by_ref[value["bom-ref"]] = value
    components = list(components_by_ref.values())
    root_ref = component_ref("npm", package["name"], package["version"])
    dependencies = [
        {"ref": root_ref, "dependsOn": sorted(item["bom-ref"] for item in components)}
    ]
    dependencies.extend(
        {"ref": item["bom-ref"], "dependsOn": []} for item in components
    )
    return document(
        package["name"],
        package["version"],
        "npm",
        components,
        dependencies,
        git_head,
        timestamp,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        git_head = command("git", "rev-parse", "HEAD")
        timestamp = (
            datetime.fromisoformat(command("git", "show", "-s", "--format=%cI", "HEAD"))
            .isoformat()
            .replace("+00:00", "Z")
        )
        output = args.output_dir.resolve()
        output.mkdir(parents=True, exist_ok=True)
        documents = {
            "python.cdx.json": python_sbom(git_head, timestamp),
            "rust.cdx.json": rust_sbom(git_head, timestamp),
            "webmcp.cdx.json": npm_sbom(git_head, timestamp),
        }
        for filename, value in documents.items():
            refs = [item["bom-ref"] for item in value["components"]]
            if len(refs) != len(set(refs)):
                raise ValueError(f"duplicate component references in {filename}")
            (output / filename).write_text(
                json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
    except (
        OSError,
        ValueError,
        KeyError,
        json.JSONDecodeError,
        subprocess.CalledProcessError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Generated {len(documents)} deterministic CycloneDX SBOMs in {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
