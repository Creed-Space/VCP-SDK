#!/usr/bin/env python3
"""Generate the deterministic, vector-level conformance coverage manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFORMANCE = ROOT / "conformance"
OUTPUT = CONFORMANCE / "coverage-manifest.json"

RUNNERS = {
    "agent-runtime/observe_contracts": "conformance/runners/agent_runtime_profile.py",
    "identity/token_parsing": "conformance/runners/identity_parity.py",
    "identity/token_canonicalization": "conformance/runners/identity_parity.py",
    "transport/content_canonicalization": "conformance/runners/transport_parity.py",
    "transport/content_hashing": "conformance/runners/transport_parity.py",
    "transport/manifest_canonicalization": "conformance/runners/transport_parity.py",
    "transport/signature_verification": "conformance/runners/transport_parity.py",
    "transport/bundle_verification": "conformance/runners/transport_parity.py",
    "semantics/csm1_parsing": "conformance/runners/csm1_parity.py",
    "semantics/csm1_encoding": "conformance/runners/csm1_parity.py",
    "semantics/persona_resolution": "conformance/runners/persona_parity.py",
    "semantics/composition": "conformance/runners/composition_parity.py",
    "adaptation/context_encoding": "conformance/runners/context_parity.py",
    "adaptation/context_encoding_extended": "conformance/runners/context_parity.py",
    "adaptation/state_machine": "conformance/runners/state_machine_conformance.py",
    "adaptation/messaging": "conformance/runners/messaging_conformance.py",
    "interop/complete_bundle": "conformance/runners/interop_parity.py",
    "interop/cross_impl_roundtrip": "conformance/runners/interop_parity.py",
    "extensions/capability_negotiation": "conformance/runners/negotiation_parity.py",
    "extensions/consensus_voting": "conformance/runners/consensus_parity.py",
    "extensions/personal_state": "conformance/runners/personal_parity.py",
    "extensions/competence": "conformance/runners/competence_conformance.py",
    "extensions/relational_context": "conformance/runners/relational_torch_parity.py",
    "extensions/torch_handoff": "conformance/runners/relational_torch_parity.py",
    "security/revocation-responses": "conformance/runners/security_parity.py",
    "security/revocation-crl-responses": "conformance/runners/security_parity.py",
    "extensions/welfare": None,
    "extensions/stateless_mcp": None,
}

NORMATIVE_SOURCES = {
    "agent-runtime": "VCP-Spec/veps/VEP-0006-agent-runtime-profile.md",
    "identity": "VCP-Spec/specs/VCP_IDENTITY_v2.0.md",
    "transport": "VCP-Spec/specs/VCP_SPECIFICATION_v3.1.md",
    "security": "VCP-Spec/specs/VCP_SPECIFICATION_v3.1.md#revocation",
    "semantics/csm1": "VCP-Spec/docs/content/CSM1_GRAMMAR_SPECIFICATION.md",
    "semantics/persona": "VCP-Spec/docs/semantics/VCP_PERSONA_PROFILES.md",
    "semantics/composition": "VCP-Spec/docs/semantics/VCP_SEMANTICS_COMPOSITION.md",
    "adaptation/context": "VCP-Spec/docs/context/VCP_CONTEXT_SPECIFICATION.md",
    "adaptation/state": "VCP-Spec/docs/adaptation/VCP_STATE_MACHINE.md",
    "adaptation/messaging": "VCP-Spec/specs/VCP_SPECIFICATION_v3.1.md#messaging",
    "interop": "VCP-Spec/specs/VCP_SPECIFICATION_v3.1.md",
    "extensions/capability": "VCP-Spec/specs/VCP_SPECIFICATION_v3.1.md#capability-negotiation",
    "extensions/consensus": "VCP-Spec/specs/VCP_SPECIFICATION_v3.1.md#consensus",
    "extensions/personal": "VCP-Spec/specs/extensions/VCP-X-Personal/spec.md",
    "extensions/competence": "VCP-Spec/specs/VCP_SPECIFICATION_v3.1.md#competence",
    "extensions/relational": "VCP-Spec/specs/VCP_SPECIFICATION_v3.1.md#relational-context",
    "extensions/torch": "VCP-Spec/archives/docs/VCP_TORCH_ARCHITECTURE.md",
    "extensions/welfare": "VCP-Spec/veps/VEP-welfare-signals-draft.md",
    "extensions/stateless": "VCP-Spec/veps/VEP-0005-stateless-mcp.md",
}

WEBMCP_RELATIONAL_CASES = {
    "trust-level-ordering",
    "standing-level-ordering",
    "trust-from-session-count-initial",
    "trust-from-session-count-developing",
    "trust-from-session-count-established",
    "trust-from-session-count-deep",
    "trust-from-session-count-boundaries",
    "self-model-valid",
    "self-model-no-uncertainty-invalid",
    "relational-context-defaults",
    "torch-receive-bootstraps-context",
}


def normative_source(suite: str) -> str:
    """Return the most specific canonical source pointer for a suite."""
    matches = [
        (prefix, source)
        for prefix, source in NORMATIVE_SOURCES.items()
        if suite.startswith(prefix)
    ]
    if not matches:
        raise ValueError(f"No normative source mapping for {suite}")
    return max(matches, key=lambda item: len(item[0]))[1]


def implementation_status(
    suite: str, case: dict[str, Any], implementation: str
) -> tuple[str, str]:
    """Return an honest execution status and reason for one vector."""
    case_id = str(case["id"])
    if suite in {"extensions/welfare", "extensions/stateless_mcp"}:
        return "unsupported", "Draft profile has no claimed implementation"
    if suite == "agent-runtime/observe_contracts" and implementation != "python":
        return (
            "unsupported",
            "The first Agent Runtime candidate slice is Python observe-only",
        )
    if implementation == "webmcp" and suite in {
        "extensions/capability_negotiation",
        "extensions/personal_state",
        "adaptation/context_encoding",
        "adaptation/context_encoding_extended",
    }:
        return "checked", "Executed by the declared checked runner"
    if (
        implementation == "webmcp"
        and suite == "extensions/relational_context"
        and case_id in WEBMCP_RELATIONAL_CASES
    ):
        return "checked", "Executed by the declared checked runner"
    if implementation == "webmcp":
        return "not_applicable", "Fixture does not exercise the WebMCP package surface"
    if suite == "adaptation/messaging" and implementation == "rust":
        return "unsupported", "Rust does not claim VCP messaging v2.0"
    if (
        suite in {"adaptation/state_machine", "extensions/competence"}
        and implementation == "rust"
    ):
        return "unsupported", "Rust does not claim this profile"
    if suite == "extensions/consensus_voting" and "candidates" not in case.get(
        "input", {}
    ):
        return "not_applicable", "Vocabulary and model-shape documentation vector"
    if suite == "semantics/composition" and "bundles" not in case:
        return "not_applicable", "Vocabulary-only composition vector"
    if suite == "extensions/relational_context" and case_id in {
        "scaffold-types",
        "trend-directions",
        "privacy-levels",
    }:
        return "not_applicable", "Vocabulary-only relational vector"
    if suite == "extensions/torch_handoff" and case_id == "torch-state-fields":
        return "not_applicable", "Model-shape documentation vector"
    return "checked", "Executed by the declared checked runner"


def load_cases(document: dict[str, Any], path: Path) -> list[dict[str, Any]]:
    """Load the one supported case-array shape from a fixture."""
    for key in ("vectors", "test_cases", "cases"):
        value = document.get(key)
        if isinstance(value, list):
            return value
    raise ValueError(
        f"{path.relative_to(ROOT)} has no vectors, test_cases, or cases array"
    )


def build_manifest() -> dict[str, Any]:
    """Build the complete deterministic coverage record."""
    suites: list[dict[str, Any]] = []
    vector_total = 0
    status_totals = {
        implementation: {
            "checked": 0,
            "unsupported": 0,
            "not_applicable": 0,
        }
        for implementation in ("python", "rust", "webmcp")
    }
    fixture_paths = sorted(
        path
        for path in CONFORMANCE.rglob("*.json")
        if path != OUTPUT and "reports" not in path.parts
    )
    for path in fixture_paths:
        document = json.loads(path.read_text(encoding="utf-8"))
        suite = path.relative_to(CONFORMANCE).with_suffix("").as_posix()
        runner = RUNNERS.get(suite)
        if suite not in RUNNERS:
            raise ValueError(f"Fixture suite is not mapped: {suite}")
        cases = load_cases(document, path)
        vector_total += len(cases)
        records = []
        for case in cases:
            implementations: dict[str, dict[str, str]] = {}
            for implementation in ("python", "rust", "webmcp"):
                status, reason = implementation_status(suite, case, implementation)
                status_totals[implementation][status] += 1
                implementations[implementation] = {"status": status, "reason": reason}
            records.append(
                {
                    "id": case["id"],
                    "description": case.get("description", ""),
                    "applicability": (
                        "draft"
                        if suite in {"extensions/welfare", "extensions/stateless_mcp"}
                        else "protocol_behavior"
                    ),
                    "implementations": implementations,
                }
            )
        suites.append(
            {
                "suite": suite,
                "version": document.get("version"),
                "maturity": (
                    "draft"
                    if "draft" in str(document.get("version", ""))
                    else "conformance-candidate"
                ),
                "normative_source": normative_source(suite),
                "fixture": path.relative_to(ROOT).as_posix(),
                "fixture_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "runner": runner,
                "case_count": len(cases),
                "cases": records,
            }
        )
    return {
        "schema": "vcp-conformance-coverage/1",
        "generated_by": "scripts/generate_conformance_coverage.py",
        "claim_boundary": (
            "checked means executed by the named local runner; it does not establish "
            "independent implementation, certification, publication, or attestation"
        ),
        "summary": {
            "fixture_count": len(suites),
            "vector_count": vector_total,
            "implementation_status": status_totals,
            "webmcp_surface_checks": 2,
        },
        "webmcp_surface": {
            "runner": "webmcp/scripts/test-packed.mjs",
            "status": "checked",
            "scope": "packed npm ESM imports and document.modelContext tool lifecycle",
            "claim_boundary": "Chromium-only experimental WebMCP API",
        },
        "suites": suites,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = (
        json.dumps(build_manifest(), indent=2, ensure_ascii=False, sort_keys=True)
        + "\n"
    )
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != rendered:
            print(f"Coverage manifest is stale: {OUTPUT.relative_to(ROOT)}")
            return 1
        print("Conformance coverage manifest is current.")
        return 0
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
