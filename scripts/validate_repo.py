#!/usr/bin/env python3
"""Deterministic structural validation for the VCP-SDK repository."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

import tomllib
import yaml

ROOT = Path(__file__).resolve().parents[1]
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
FENCE_RE = re.compile(r"^\s*(?:\x60{3}|~~~)")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
REQUIRED_FILES = (
    "README.md",
    "CONTRIBUTING.md",
    "GOVERNANCE.md",
    "SECURITY.md",
    "COMPATIBILITY.md",
    "DEPENDENCY_POLICY.md",
    "SCHEMA_OWNERSHIP.md",
    "ARTIFACTS.md",
    "RELEASE_CHECKLIST.md",
    "REPOSITORY_CONTROLS.md",
    ".github/repository-policy.json",
    ".github/workflows/codeql.yml",
    ".github/workflows/dependency-review.yml",
    ".github/workflows/release.yml",
    ".github/workflows/webmcp-upstream.yml",
    "release/COORDINATED_RELEASE_RUNBOOK.md",
    "release/review-ledger.schema.json",
    "release/review-ledger.template.json",
    "reviews/SDK_SECURITY_SEMVER_PUBLICATION_REVIEW.md",
    "reviews/DEPENDABOT_DISPOSITION_2026-08-14.md",
    "reviews/DEPENDENCY_CONSOLIDATION_2026-08-15.md",
    "scripts/build_candidate_manifest.py",
    "scripts/validate_review_ledger.py",
    "scripts/validate_ecosystem.py",
    "scripts/validate_public_contract.py",
    "scripts/generate_conformance_coverage.py",
    "scripts/generate_feature_matrix.py",
    "scripts/generate_api_snapshot.py",
    "scripts/check_status_registry.py",
    "scripts/validate_conformance_claim.py",
    "scripts/sync_publication_state.py",
    "scripts/verify_artifacts.py",
    "scripts/normalize_python_sdist.py",
    "scripts/check_release_authority.py",
    "scripts/generate_sboms.py",
    "scripts/finalize_release_manifest.py",
    "scripts/compare_release_artifacts.py",
    "conformance/coverage-manifest.json",
    "conformance/runners/run_all.py",
    "conformance/reports/README.md",
    "rust/vcp-core/testdata/revocation-responses.json",
    "rust/vcp-core/testdata/revocation-crl-responses.json",
    "rust/vcp-core/testdata/relational_context.json",
    "rust/vcp-core/testdata/torch_handoff.json",
    "webmcp/upstream-contract.json",
    "schemas/vcp-conformance-aggregate-report.schema.json",
    "release/ECOSYSTEM_STATUS.md",
    "docs/FEATURE_MATRIX.json",
    "docs/FEATURE_MATRIX.md",
    "docs/RUNTIME_CONTRACTS.md",
    "api-snapshots/public-api.json",
    "python/requirements-dev.lock",
    "webmcp/package-lock.json",
    "package-lock.json",
)
COMMON_SCHEMAS = (
    "vcp-adaptation-context.schema.json",
    "vcp-identity-token.schema.json",
    "vcp-manifest-v1.schema.json",
    "vcp-semantics-csm1.schema.json",
)
PERSONAL_FIELDS = {
    "cognitive_state",
    "emotional_tone",
    "energy_level",
    "perceived_urgency",
    "body_signals",
}
FORBIDDEN_PERSONAL_FIELDS = {"cognitive", "emotional", "energy", "urgency", "body"}


class Problems:
    def __init__(self) -> None:
        self.items: list[str] = []

    def add(self, message: str) -> None:
        self.items.append(message)

    def finish(self) -> int:
        if self.items:
            for item in sorted(set(self.items)):
                print(f"ERROR: {item}", file=sys.stderr)
            print(
                f"VCP-SDK validation failed with {len(set(self.items))} problem(s).",
                file=sys.stderr,
            )
            return 1
        print("VCP-SDK repository validation passed.")
        return 0


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def excluded(path: Path) -> bool:
    try:
        parts = path.relative_to(ROOT).parts
    except ValueError:
        return True
    return any(
        part
        in {
            ".git",
            ".venv",
            "node_modules",
            "target",
            "dist",
            "build",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
            "reports",
        }
        or part.endswith(".egg-info")
        for part in parts
    )


def load_json(path: Path, problems: Problems) -> object | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        problems.add(f"{relative(path)} is not valid UTF-8 JSON: {exc}")
        return None


def validate_required_files(problems: Problems) -> None:
    for name in REQUIRED_FILES:
        if not (ROOT / name).is_file():
            problems.add(f"required file is missing: {name}")
    for name in COMMON_SCHEMAS:
        if not (ROOT / "schemas" / name).is_file():
            problems.add(f"common schema is missing: schemas/{name}")


def validate_json(problems: Problems) -> None:
    for path in sorted(ROOT.rglob("*.json")):
        if not excluded(path):
            load_json(path, problems)


def validate_conformance(problems: Problems) -> None:
    files = sorted(
        path
        for path in (ROOT / "conformance").rglob("*.json")
        if path.name != "coverage-manifest.json" and "reports" not in path.parts
    )
    if len(files) != 27:
        problems.add(f"expected 27 conformance fixture files, found {len(files)}")

    total_vectors = 0
    total_extension_cases = 0
    global_ids: dict[str, Path] = {}
    for path in files:
        loaded = load_json(path, problems)
        if not isinstance(loaded, dict):
            if loaded is not None:
                problems.add(f"{relative(path)} must contain an object")
            continue
        if not isinstance(loaded.get("suite"), str) or not loaded["suite"]:
            problems.add(f"{relative(path)} needs a non-empty suite")
        version = loaded.get("version")
        if not isinstance(version, str) or not SEMVER_RE.fullmatch(version):
            problems.add(f"{relative(path)} needs a semantic version")
        key = "test_cases" if "test_cases" in loaded else "vectors"
        cases = loaded.get(key)
        if not isinstance(cases, list) or not cases:
            problems.add(
                f"{relative(path)} needs a non-empty vectors or test_cases array"
            )
            continue
        if key == "test_cases":
            total_extension_cases += len(cases)
        else:
            total_vectors += len(cases)
        local_ids: set[str] = set()
        for index, case in enumerate(cases):
            if not isinstance(case, dict):
                problems.add(f"{relative(path)} case {index + 1} must be an object")
                continue
            case_id = case.get("id")
            if not isinstance(case_id, str) or not case_id:
                problems.add(f"{relative(path)} case {index + 1} needs an id")
                continue
            if case_id in local_ids:
                problems.add(f"{relative(path)} has duplicate id {case_id!r}")
            local_ids.add(case_id)
            if case_id in global_ids:
                problems.add(
                    f"duplicate conformance id {case_id!r}: "
                    f"{relative(global_ids[case_id])} and {relative(path)}"
                )
            global_ids[case_id] = path
            if not isinstance(case.get("description"), str):
                problems.add(f"{relative(path)} {case_id} needs a description")
            if "expected" not in case and "verification_checklist" not in case:
                problems.add(
                    f"{relative(path)} {case_id} needs expected results or a verification checklist"
                )

    if total_vectors != 216:
        problems.add(f"expected 216 top-level vectors, found {total_vectors}")
    if total_extension_cases != 78:
        problems.add(f"expected 78 extension test cases, found {total_extension_cases}")
    print(
        f"conformance inventory: {len(files)} files, "
        f"{total_vectors} vectors, {total_extension_cases} extension cases"
    )


def walk_personal(value: object, path: str, problems: Problems) -> None:
    if isinstance(value, dict):
        personal = value.get("personal")
        if isinstance(personal, dict):
            old = FORBIDDEN_PERSONAL_FIELDS.intersection(personal)
            unknown = set(personal).difference(PERSONAL_FIELDS)
            if old:
                problems.add(f"{path} uses retired personal fields: {sorted(old)}")
            if unknown:
                problems.add(f"{path} uses unknown personal fields: {sorted(unknown)}")
            for name, state in personal.items():
                if isinstance(state, dict) and "level" in state:
                    problems.add(
                        f"{path} personal.{name} uses retired level instead of intensity"
                    )
        for child in value.values():
            walk_personal(child, path, problems)
    elif isinstance(value, list):
        for child in value:
            walk_personal(child, path, problems)


def validate_context_fixtures(problems: Problems) -> None:
    for name in ("context_encoding.json", "context_encoding_extended.json"):
        path = ROOT / "conformance" / "adaptation" / name
        loaded = load_json(path, problems)
        if loaded is not None:
            walk_personal(loaded, relative(path), problems)
    base = (ROOT / "conformance/adaptation/context_encoding.json").read_text(
        encoding="utf-8"
    )
    if "U+2016" not in base or "\\u2016" not in base:
        problems.add("base context fixture must document and exercise U+2016")


def strip_fenced_code(text: str) -> str:
    output: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            output.append(line)
    return "\n".join(output)


def link_target(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("<") and ">" in raw:
        return raw[1 : raw.index(">")]
    return raw.split(maxsplit=1)[0]


def validate_markdown(problems: Problems) -> None:
    for path in sorted(ROOT.rglob("*.md")):
        if excluded(path):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            problems.add(f"{relative(path)} is not readable UTF-8: {exc}")
            continue
        lines = text.splitlines()
        if not any(line.startswith("# ") for line in lines[:20]):
            problems.add(f"{relative(path)} needs one H1 in its first 20 lines")
        if any(line.endswith((" ", "\t")) for line in lines):
            problems.add(f"{relative(path)} contains trailing whitespace")
        if "archives" in path.relative_to(ROOT).parts:
            continue
        for raw in LINK_RE.findall(strip_fenced_code(text)):
            target = unquote(link_target(raw))
            parts = urlsplit(target)
            if parts.scheme or target.startswith(("#", "//")):
                continue
            clean = parts.path
            if not clean:
                continue
            destination = (
                ROOT / clean.lstrip("/")
                if clean.startswith("/")
                else path.parent / clean
            ).resolve(strict=False)
            try:
                destination.relative_to(ROOT)
            except ValueError:
                problems.add(f"{relative(path)} link escapes repository: {target}")
                continue
            if not destination.exists():
                problems.add(f"{relative(path)} has broken local link: {target}")


def validate_yaml(problems: Problems) -> None:
    for path in sorted(ROOT.rglob("*.yml")) + sorted(ROOT.rglob("*.yaml")):
        if excluded(path):
            continue
        try:
            yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, yaml.YAMLError) as exc:
            problems.add(f"{relative(path)} is not valid YAML: {exc}")


def candidate_files(problems: Problems) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if result.returncode:
        problems.add("git ls-files failed while checking candidate files")
        return []
    return [ROOT / item.decode() for item in result.stdout.split(b"\0") if item]


def validate_repository_invariants(problems: Problems) -> None:
    dangerous = list(ROOT.glob("commit-*-sweep.sh")) + list(ROOT.rglob("*.bak"))
    for path in dangerous:
        if not excluded(path):
            problems.add(f"unsafe or ambiguous artifact remains: {relative(path)}")

    old_examples = ROOT / "examples" / "rust"
    if old_examples.exists() and any(old_examples.iterdir()):
        problems.add("Rust examples must live under rust/vcp-core/examples")
    rust_examples = ROOT / "rust" / "vcp-core" / "examples"
    expected_examples = {
        "parse_token.rs",
        "performance_probe.rs",
        "sign_and_verify.rs",
        "verify_bundle.rs",
    }
    actual_examples = {path.name for path in rust_examples.glob("*.rs")}
    if actual_examples != expected_examples:
        problems.add(
            "Cargo-discoverable Rust examples differ from the allowlist: "
            f"expected {sorted(expected_examples)}, found {sorted(actual_examples)}"
        )

    for retired in (ROOT / "python/src/api", ROOT / "python/src/mcp"):
        if retired.exists() and any(path.is_file() for path in retired.rglob("*")):
            problems.add(
                f"non-package adapter remains under package source: {relative(retired)}"
            )
    if (ROOT / ".github/ISSUE_TEMPLATE/spec_amendment.yml").exists():
        problems.add("SDK must not expose a second canonical VEP intake template")
    issue_config = ROOT / ".github/ISSUE_TEMPLATE/config.yml"
    if (
        issue_config.is_file()
        and "VCP-Spec/issues/new?template=spec_amendment.yml"
        not in issue_config.read_text(encoding="utf-8")
    ):
        problems.add("SDK issue chooser must route protocol changes to VCP-Spec")
    policy = load_json(ROOT / ".github/repository-policy.json", problems)
    if isinstance(policy, dict):
        if policy.get("schema") != "vcp-repository-policy/1":
            problems.add("repository policy has an unknown schema")
        if policy.get("repository") != "Creed-Space/VCP-SDK":
            problems.add("repository policy names the wrong repository")
        if policy.get("external_state_applied") is not False:
            problems.add("repository policy must not claim unverified external state")
        required = policy.get("desired", {}).get("required_checks", [])
        if not isinstance(required, list) or len(required) != len(set(required)):
            problems.add("repository policy required checks must be a unique list")
    if not (ROOT / "archives/host_integrations/creed_space_api_router.py").is_file():
        problems.add("archived host API adapter is missing")
    for test_path in (
        "python/tests/unit/plugins/test_vcp_adaptation_plugin.py",
        "python/tests/unit/test_vcp_bridge.py",
    ):
        if (ROOT / test_path).exists():
            problems.add(
                f"host-owned skipped test remains in the SDK suite: {test_path}"
            )

    website_entries = sorted(
        path.relative_to(ROOT / "website").as_posix()
        for path in (ROOT / "website").rglob("*")
        if path.is_file() and not excluded(path)
    )
    if website_entries != ["README.md"]:
        problems.add(f"website archive contains unexpected files: {website_entries}")

    candidate = candidate_files(problems)
    for path in candidate:
        if not path.exists():
            continue
        if path.is_symlink():
            problems.add(f"candidate source symlink is forbidden: {relative(path)}")
        if path.exists() and path.is_file() and path.stat().st_size > 50 * 1024 * 1024:
            problems.add(f"candidate file exceeds 50 MiB: {relative(path)}")
        parts = path.relative_to(ROOT).parts
        if any(part in {"node_modules", "target", "dist", "build"} for part in parts):
            problems.add(
                f"generated path is present in the candidate: {relative(path)}"
            )

    root_license = (ROOT / "LICENSE").read_bytes()
    for name in (
        "python/LICENSE",
        "rust/vcp-core/LICENSE",
        "rust/vcp-cli/LICENSE",
        "rust/vcp-wasm/LICENSE",
        "webmcp/LICENSE",
    ):
        path = ROOT / name
        if not path.is_file() or path.read_bytes() != root_license:
            problems.add(f"licence copy is missing or differs: {name}")


def validate_versions(problems: Problems) -> None:
    pyproject = tomllib.loads(
        (ROOT / "python/pyproject.toml").read_text(encoding="utf-8")
    )
    cargo = tomllib.loads((ROOT / "rust/Cargo.toml").read_text(encoding="utf-8"))
    web = json.loads((ROOT / "webmcp/package.json").read_text(encoding="utf-8"))
    versions = {
        "Python": pyproject["project"]["version"],
        "Rust": cargo["workspace"]["package"]["version"],
        "WebMCP": web["version"],
    }
    if len(set(versions.values())) != 1:
        problems.add(f"SDK distribution versions differ: {versions}")
    for label, version in versions.items():
        if not SEMVER_RE.fullmatch(version):
            problems.add(f"{label} version is not semantic: {version}")


def validate_rust_security_dependencies(problems: Problems) -> None:
    """Keep security-sensitive dependency features explicit and reviewable."""
    core = tomllib.loads(
        (ROOT / "rust/vcp-core/Cargo.toml").read_text(encoding="utf-8")
    )
    base64 = core.get("dependencies", {}).get("base64")
    if not isinstance(base64, dict):
        problems.add("vcp-core base64 dependency must use an explicit feature table")
        return
    if base64.get("default-features") is not False:
        problems.add("vcp-core base64 dependency must disable simd-unsafe defaults")
    if base64.get("features") != ["std"]:
        problems.add("vcp-core base64 dependency must enable only the std feature")


def validate_packaged_fixture_mirrors(problems: Problems) -> None:
    """Keep crate-local test data byte-identical to canonical conformance inputs."""
    fixture_mirrors = (
        ("security", "revocation-responses.json"),
        ("security", "revocation-crl-responses.json"),
        ("extensions", "relational_context.json"),
        ("extensions", "torch_handoff.json"),
    )
    for family, name in fixture_mirrors:
        canonical = ROOT / "conformance" / family / name
        packaged = ROOT / "rust" / "vcp-core" / "testdata" / name
        if not canonical.is_file() or not packaged.is_file():
            continue
        if canonical.read_bytes() != packaged.read_bytes():
            problems.add(
                f"packaged vcp-core test fixture differs from canonical input: {name}"
            )


def validate_workflows(problems: Problems) -> None:
    workflow_dir = ROOT / ".github" / "workflows"
    workflows = sorted(workflow_dir.glob("*.yml")) + sorted(workflow_dir.glob("*.yaml"))
    expected_workflows = [
        "ci.yml",
        "codeql.yml",
        "dependency-review.yml",
        "fuzz.yml",
        "mutation.yml",
        "performance.yml",
        "release.yml",
        "webmcp-upstream.yml",
    ]
    if [path.name for path in workflows] != expected_workflows:
        problems.add(
            "workflow files differ from the allowlist: "
            f"expected {expected_workflows}, found {[p.name for p in workflows]}"
        )
    uses_re = re.compile(r"^\s*uses:\s*([^#\s]+)", re.MULTILINE)
    sha_re = re.compile(r"^[^@]+@[0-9a-f]{40}$")
    for path in workflows:
        text = path.read_text(encoding="utf-8")
        for use in uses_re.findall(text):
            if not sha_re.fullmatch(use):
                problems.add(f"{relative(path)} has unpinned action: {use}")
        if "npm install -g" in text:
            problems.add(f"{relative(path)} installs mutable global npm tooling")
        if "requirements.txt" in text and "requirements-dev.lock" not in text:
            problems.add(
                f"{relative(path)} references the retired Python requirements file"
            )
        if path.name == "fuzz.yml" and '"rust/vcp-core/**"' not in text:
            problems.add(
                "fuzz.yml must run for all vcp-core changes so its independent lockfile cannot drift"
            )


def main() -> int:
    problems = Problems()
    validate_required_files(problems)
    validate_json(problems)
    validate_conformance(problems)
    validate_context_fixtures(problems)
    validate_markdown(problems)
    validate_yaml(problems)
    validate_repository_invariants(problems)
    validate_versions(problems)
    validate_rust_security_dependencies(problems)
    validate_packaged_fixture_mirrors(problems)
    validate_workflows(problems)
    return problems.finish()


if __name__ == "__main__":
    raise SystemExit(main())
