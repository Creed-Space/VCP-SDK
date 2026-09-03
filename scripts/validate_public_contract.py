#!/usr/bin/env python3
"""Validate the public package and protocol contract across VCP repositories."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import tomllib

EXPECTED_SDK_VERSION = "4.2.0"
EXPECTED_DEMO_VERSION = "0.1.0"
EXPECTED_PYTHON_PACKAGE = "value-context-protocol"
EXPECTED_RUST_PACKAGE = "vcp-core"
# States that may hold before any registry receipt exists. `candidate` means
# names are ratified and publication is authorised; nothing is claimed as live.
PREPUBLICATION_STATES = {"source-only", "candidate"}
# `published` means every artifact carries a registry receipt and a pinned
# source commit; registry install commands are then allowed in public copy.
ALLOWED_STATES = PREPUBLICATION_STATES | {"published"}
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")
EXPECTED_WEB_PACKAGE = "@creedspace/vcp-sdk"

RETIRED_PUBLIC_TERMS = (
    "creed-sdk",
    "creed_sdk",
    "@creed-space/sdk",
    "@creed-space/vcp-sdk",
    "@creedspace/sdk",
    "@vcp/webmcp",
    "vcp-python-sdk",
    "CreedClient",
    "CreedError",
    "create_client",
    "createClient",
    "18 verification states",
    "METTLE_VERIFICATION",
    "METTLE_GEOMETRIC",
    "BILATERAL_VERIFIED",
)

REGISTRY_INSTALL_PATTERNS = (
    re.compile(
        r"(?:python(?:3)?\s+-m\s+)?pip\s+install\s+['\"]?value-context-protocol",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?:python(?:3)?\s+-m\s+)?pip\s+install\s+['\"]?vcp(?:\b|\[)",
        re.IGNORECASE,
    ),
    re.compile(r"npm\s+(?:install|i)\s+@creedspace/vcp-sdk", re.IGNORECASE),
    re.compile(r"npm\s+(?:install|i)\s+@valuecontextprotocol/sdk", re.IGNORECASE),
    re.compile(r"cargo\s+add\s+(?:vcp-core|rvcp)", re.IGNORECASE),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", required=True, type=Path)
    parser.add_argument("--spec", required=True, type=Path)
    parser.add_argument("--sdk", type=Path, default=Path(__file__).parents[1])
    parser.add_argument(
        "--standalone-python-sdk",
        type=Path,
        help=(
            "Optional legacy vcp-sdk-python checkout. It is validated as a separate "
            "source candidate, never as part of the main SDK package set."
        ),
    )
    return parser.parse_args()


def root(path: Path, label: str) -> Path:
    resolved = path.expanduser().resolve()
    if not resolved.is_dir():
        raise ValueError(f"{label} repository is not a directory: {resolved}")
    return resolved


def load_toml(path: Path) -> dict[str, object]:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def load_json(path: Path) -> dict[str, object]:
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise TypeError(f"{path} must contain an object")
    return loaded


def require_equal(
    problems: list[str], label: str, actual: object, expected: object
) -> None:
    if actual != expected:
        problems.append(f"{label} is {actual!r}; expected {expected!r}")


def require_fragments(
    problems: list[str], label: str, text: str, fragments: tuple[str, ...]
) -> None:
    normalized_text = " ".join(text.split())
    for fragment in fragments:
        if " ".join(fragment.split()) not in normalized_text:
            problems.append(f"{label} is missing required public contract: {fragment}")


def cargo_version(package: dict[str, object], workspace_version: object) -> object:
    value = package.get("version")
    if value == {"workspace": True}:
        return workspace_version
    return value


def validate_metadata(
    problems: list[str], demo: Path, sdk: Path
) -> tuple[str, str, str, str]:
    python_project = load_toml(sdk / "python" / "pyproject.toml")["project"]
    if not isinstance(python_project, dict):
        raise TypeError("python/pyproject.toml project metadata must be a table")
    web_package = load_json(sdk / "webmcp" / "package.json")
    rust_workspace = load_toml(sdk / "rust" / "Cargo.toml")["workspace"]
    rust_core = load_toml(sdk / "rust" / "vcp-core" / "Cargo.toml")["package"]
    demo_package = load_json(demo / "package.json")
    if not isinstance(rust_workspace, dict) or not isinstance(rust_core, dict):
        raise TypeError("Rust workspace and core package metadata must be tables")
    workspace_package = rust_workspace.get("package")
    if not isinstance(workspace_package, dict):
        raise TypeError("Rust workspace.package metadata must be a table")

    python_version = str(python_project.get("version"))
    web_version = str(web_package.get("version"))
    rust_version = str(cargo_version(rust_core, workspace_package.get("version")))
    demo_version = str(demo_package.get("version"))

    require_equal(
        problems,
        "Python distribution name",
        python_project.get("name"),
        EXPECTED_PYTHON_PACKAGE,
    )
    require_equal(
        problems,
        "WebMCP package name",
        web_package.get("name"),
        EXPECTED_WEB_PACKAGE,
    )
    require_equal(
        problems,
        "Rust core package name",
        rust_core.get("name"),
        EXPECTED_RUST_PACKAGE,
    )
    require_equal(problems, "Python SDK version", python_version, EXPECTED_SDK_VERSION)
    require_equal(problems, "WebMCP SDK version", web_version, EXPECTED_SDK_VERSION)
    require_equal(problems, "Rust SDK version", rust_version, EXPECTED_SDK_VERSION)
    require_equal(problems, "Demo version", demo_version, EXPECTED_DEMO_VERSION)
    if len({python_version, web_version, rust_version}) != 1:
        problems.append(
            "SDK package versions disagree: "
            f"Python={python_version}, WebMCP={web_version}, Rust={rust_version}"
        )
    return python_version, web_version, rust_version, demo_version


def validate_exports(problems: list[str], sdk: Path) -> None:
    python_exports = (sdk / "python" / "src" / "vcp" / "__init__.py").read_text(
        encoding="utf-8"
    )
    rust_exports = (sdk / "rust" / "vcp-core" / "src" / "lib.rs").read_text(
        encoding="utf-8"
    )
    web_exports = (sdk / "webmcp" / "src" / "index.ts").read_text(encoding="utf-8")
    require_fragments(
        problems,
        "Python public exports",
        python_exports,
        ('"CSM1Code"', '"Token"'),
    )
    require_fragments(
        problems,
        "Rust public exports",
        rust_exports,
        ("pub use csm1::{Csm1Code", "pub use identity::VcpToken;"),
    )
    require_fragments(
        problems,
        "WebMCP public exports",
        web_exports,
        ("export { registerVCPTools } from './registration.js';",),
    )


def validate_standalone_python_sdk(
    problems: list[str], standalone: Path
) -> tuple[str, str]:
    """Validate the explicit boundary around the legacy sibling implementation."""
    project_data = load_toml(standalone / "pyproject.toml").get("project")
    if not isinstance(project_data, dict):
        raise TypeError("standalone Python SDK project metadata must be a table")
    name = project_data.get("name")
    version = project_data.get("version")
    if not isinstance(name, str) or not name:
        problems.append("standalone Python SDK needs a non-empty distribution name")
        name = "unknown"
    if not isinstance(version, str) or not version:
        problems.append("standalone Python SDK needs a non-empty version")
        version = "unknown"
    if name == EXPECTED_PYTHON_PACKAGE:
        problems.append(
            "standalone Python SDK must not claim the maintained SDK distribution name"
        )
    if not (standalone / "src" / "vcp").is_dir():
        problems.append(
            "standalone Python SDK does not expose the expected vcp namespace"
        )

    readme_path = standalone / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    require_fragments(
        problems,
        "Standalone Python SDK boundary",
        readme,
        (
            "legacy standalone implementation candidate",
            "not the project-maintained VCP-SDK",
            "no PyPI release or registry package name is claimed",
            "both use the `vcp` Python import namespace",
            "separate virtual environments",
        ),
    )
    for pattern in REGISTRY_INSTALL_PATTERNS:
        if pattern.search(readme):
            problems.append(
                "standalone Python SDK source-only copy contains a registry install "
                f"command: {pattern.pattern}"
            )
    return name, version


def validate_publication_state(
    problems: list[str], demo: Path, spec: Path, sdk: Path
) -> dict[str, object]:
    canonical_path = sdk / "release" / "publication-state.json"
    canonical_bytes = canonical_path.read_bytes()
    state = load_json(canonical_path)
    mirrors = (
        demo / "static" / "status" / "publication-state.json",
        spec / "status" / "publication-state.json",
    )
    for mirror in mirrors:
        if mirror.read_bytes() != canonical_bytes:
            problems.append(f"publication-state mirror drifted: {mirror}")

    require_equal(
        problems,
        "publication-state schema",
        state.get("schema"),
        "vcp-publication-state/1",
    )
    overall_state = state.get("overall_state")
    if overall_state not in ALLOWED_STATES:
        problems.append(
            "ecosystem publication state must be one of "
            f"{sorted(ALLOWED_STATES)}, found {overall_state!r}"
        )
    published = overall_state == "published"
    require_equal(
        problems,
        "candidate-name ratification",
        state.get("candidate_names_ratified"),
        overall_state in {"candidate", "published"},
    )
    conformance = state.get("conformance")
    if not isinstance(conformance, dict):
        problems.append("publication-state conformance must be an object")
    else:
        coverage = load_json(sdk / "conformance" / "coverage-manifest.json")
        coverage_summary = coverage.get("summary")
        coverage_suites = coverage.get("suites")
        if not isinstance(coverage_summary, dict) or not isinstance(
            coverage_suites, list
        ):
            problems.append(
                "conformance coverage manifest summary or suites are malformed"
            )
        else:
            extension_suites = sum(
                1
                for suite in coverage_suites
                if isinstance(suite, dict)
                and str(suite.get("suite", "")).startswith("extensions/")
            )
            require_equal(
                problems,
                "publication-state fixture count",
                conformance.get("fixture_count"),
                coverage_summary.get("fixture_count"),
            )
            require_equal(
                problems,
                "publication-state case count",
                conformance.get("case_count"),
                coverage_summary.get("vector_count"),
            )
            require_equal(
                problems,
                "publication-state extension suite count",
                conformance.get("extension_suite_count"),
                extension_suites,
            )
        for label, expected in (
            ("protocol_layer_count", 6),
            ("full_project_controlled_implementations", 2),
            ("browser_integrations", 1),
            ("independent_implementations", 0),
        ):
            require_equal(
                problems,
                f"publication-state {label.replace('_', ' ')}",
                conformance.get(label),
                expected,
            )
    policy = state.get("public_copy_policy")
    if not isinstance(policy, dict):
        problems.append("publication-state public_copy_policy must be an object")
    else:
        require_equal(
            problems,
            "registry command policy",
            policy.get("registry_install_commands_allowed"),
            published,
        )

    artifacts = state.get("artifacts")
    if not isinstance(artifacts, list):
        problems.append("publication-state artifacts must be an array")
        artifacts = []
    by_id = {
        artifact.get("id"): artifact
        for artifact in artifacts
        if isinstance(artifact, dict) and isinstance(artifact.get("id"), str)
    }
    expected = {
        "python": (EXPECTED_PYTHON_PACKAGE, "python -m pip install ./python"),
        "webmcp": (EXPECTED_WEB_PACKAGE, "npm install ./webmcp"),
        "rust-core": (
            EXPECTED_RUST_PACKAGE,
            "cargo build --manifest-path ./rust/Cargo.toml -p vcp-core",
        ),
    }
    for artifact_id, (name, command) in expected.items():
        artifact = by_id.get(artifact_id)
        if not isinstance(artifact, dict):
            problems.append(f"publication-state artifact is missing: {artifact_id}")
            continue
        require_equal(
            problems,
            f"{artifact_id} candidate name",
            artifact.get("candidate_name"),
            name,
        )
        require_equal(
            problems,
            f"{artifact_id} source command",
            artifact.get("source_command"),
            command,
        )
        require_equal(
            problems, f"{artifact_id} state", artifact.get("state"), overall_state
        )
        source_commit = artifact.get("source_commit")
        registry_receipt = artifact.get("registry_receipt")
        if published:
            if not isinstance(source_commit, str) or not COMMIT_PATTERN.match(
                source_commit
            ):
                problems.append(
                    f"{artifact_id} source commit must be a full commit SHA once published"
                )
            if not isinstance(registry_receipt, str) or not registry_receipt.startswith(
                "https://"
            ):
                problems.append(
                    f"{artifact_id} registry receipt must be an https URL once published"
                )
        else:
            require_equal(problems, f"{artifact_id} source commit", source_commit, None)
            require_equal(
                problems, f"{artifact_id} registry receipt", registry_receipt, None
            )

    public_files = [
        *sorted((demo / "src" / "routes").rglob("*.svelte")),
        demo / "src/lib/components/shared/BuiltForDevelopers.svelte",
        spec / "README.md",
        *sorted((spec / "docs").rglob("*.md")),
        sdk / "README.md",
        sdk / "COMPATIBILITY.md",
        sdk / "python/README.md",
        sdk / "webmcp/README.md",
        sdk / "examples/README.md",
    ]
    for path in public_files if not published else []:
        text = path.read_text(encoding="utf-8")
        for pattern in REGISTRY_INSTALL_PATTERNS:
            if pattern.search(text):
                problems.append(
                    f"source-only public copy contains registry install command in {path}: {pattern.pattern}"
                )
    return state


def validate_compatibility_docs(
    problems: list[str], demo: Path, spec: Path, sdk: Path, publication_state: dict
) -> None:
    spec_compatibility = (spec / "COMPATIBILITY.md").read_text(encoding="utf-8")
    sdk_compatibility = (sdk / "COMPATIBILITY.md").read_text(encoding="utf-8")
    common = (
        "v3.1 source baseline",
        EXPECTED_PYTHON_PACKAGE,
        EXPECTED_RUST_PACKAGE,
        EXPECTED_WEB_PACKAGE,
        EXPECTED_SDK_VERSION,
        "Demonstration release, not conformance evidence",
    )
    require_fragments(problems, "Spec compatibility policy", spec_compatibility, common)
    require_fragments(problems, "SDK compatibility policy", sdk_compatibility, common)

    getting_started = (
        demo / "src" / "routes" / "docs" / "getting-started" / "+page.svelte"
    ).read_text(encoding="utf-8")
    developer_panel = (
        demo / "src" / "lib" / "components" / "shared" / "BuiltForDevelopers.svelte"
    ).read_text(encoding="utf-8")
    published = publication_state.get("overall_state") == "published"
    status_fragments = (
        (
            "Published 4.2.0.",
            "pip install value-context-protocol==4.2.0",
            "npm install @creedspace/vcp-sdk@4.2.0",
            "cargo add vcp-core@4.2.0",
        )
        if published
        else ("Source-only candidate.",)
    )
    require_fragments(
        problems,
        "Demo getting-started guide",
        getting_started,
        (
            *status_fragments,
            "python -m pip install ./python",
            "npm install ./webmcp",
            "cargo build --manifest-path ./rust/Cargo.toml -p vcp-core",
            "document.modelContext",
            "VCP v3.1",
            "Candidate or experimental",
        ),
    )
    require_fragments(
        problems,
        "Demo developer panel",
        developer_panel,
        (
            "from vcp import CSM1Code, Token",
            'from "@creedspace/vcp-sdk"',
            "use vcp_core::{Csm1Code, VcpToken};",
        ),
    )


def validate_demo_copy(problems: list[str], demo: Path) -> None:
    public_files = sorted((demo / "src" / "routes").rglob("*.svelte"))
    public_files.append(
        demo / "src" / "lib" / "components" / "shared" / "BuiltForDevelopers.svelte"
    )
    for path in public_files:
        text = path.read_text(encoding="utf-8")
        normalized_text = " ".join(text.split())
        for term in RETIRED_PUBLIC_TERMS:
            if " ".join(term.split()) in normalized_text:
                problems.append(
                    f"Demo public copy advertises retired term {term!r} in "
                    f"{path.relative_to(demo)}"
                )

    welfare = (
        demo / "src" / "routes" / "docs" / "welfare-signal" / "+page.svelte"
    ).read_text(encoding="utf-8")
    require_fragments(
        problems,
        "Demo welfare instrumentation guide",
        welfare,
        (
            "Status: Experimental.",
            "VCP-SDK 4.2.0 does not expose",
            "Do not claim SDK support or conformance",
        ),
    )


def main() -> int:
    args = parse_args()
    problems: list[str] = []
    try:
        demo = root(args.demo, "Demo")
        spec = root(args.spec, "Spec")
        sdk = root(args.sdk, "SDK")
        versions = validate_metadata(problems, demo, sdk)
        validate_exports(problems, sdk)
        publication_state = validate_publication_state(problems, demo, spec, sdk)
        validate_compatibility_docs(problems, demo, spec, sdk, publication_state)
        validate_demo_copy(problems, demo)
        standalone_identity = None
        if args.standalone_python_sdk is not None:
            standalone = root(args.standalone_python_sdk, "Standalone Python SDK")
            if standalone == sdk or standalone == sdk / "python":
                raise ValueError(
                    "standalone Python SDK must be a separate repository checkout"
                )
            standalone_identity = validate_standalone_python_sdk(problems, standalone)
    except (
        KeyError,
        OSError,
        TypeError,
        UnicodeError,
        ValueError,
        tomllib.TOMLDecodeError,
    ) as exc:
        print(f"ERROR: unable to evaluate public contract: {exc}", file=sys.stderr)
        return 2

    if problems:
        for problem in sorted(set(problems)):
            print(f"ERROR: {problem}", file=sys.stderr)
        print(
            f"VCP public contract failed with {len(set(problems))} problem(s).",
            file=sys.stderr,
        )
        return 1

    sibling = (
        f", standalone Python sibling {standalone_identity[0]} "
        f"{standalone_identity[1]} isolated"
        if standalone_identity is not None
        else ""
    )
    print(
        "VCP public contract passed: "
        f"Python {versions[0]}, WebMCP {versions[1]}, Rust {versions[2]}, "
        f"Demo {versions[3]}, protocol v3.1 source baseline, "
        f"artifacts {publication_state['overall_state']}{sibling}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
