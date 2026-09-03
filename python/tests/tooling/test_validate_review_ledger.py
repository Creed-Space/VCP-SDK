from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "validate_review_ledger.py"
SPEC = importlib.util.spec_from_file_location("validate_review_ledger", SCRIPT)
assert SPEC and SPEC.loader
ledger_validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ledger_validator)


def prepublication_ledger() -> dict[str, object]:
    ledger = json.loads((ROOT / "release/review-ledger.template.json").read_text())
    candidate = ledger["candidate"]
    for index, repository in enumerate(candidate["repositories"], start=1):
        repository["commit"] = f"{index}" * 40
        repository["working_tree_sha256"] = f"{index}" * 64
    candidate["combined_candidate_sha256"] = "a" * 64
    candidate["source_manifest_sha256"] = "b" * 64
    candidate["protocol"]["amendment_maturity"] = "candidate"
    candidate["deployment"]["environment"] = "production"
    candidate["deployment"]["url"] = "https://valuecontextprotocol.org/"

    for review in ledger["reviews"]:
        gate_id = review["id"]
        if gate_id in ledger_validator.POST_PUBLICATION_GATES:
            continue
        review["status"] = "approved"
        review["reviewer"] = {
            "name": f"Reviewer {gate_id}",
            "role": "authorized reviewer",
            "organization": "Example review body",
            "independence_statement": (
                "No implementation authorship or conflicting financial interest."
            ),
        }
        review["reviewed_at"] = "2026-08-15T00:00:00Z"
        review["decision_summary"] = (
            f"Gate {gate_id} approved for the exact candidate and evidence set."
        )
        review["evidence"] = [
            {
                "kind": kind,
                "uri": f"evidence/{gate_id}/{kind}.json",
                "sha256": "c" * 64,
            }
            for kind in sorted(ledger_validator.REQUIRED_EVIDENCE[gate_id])
        ]
        review["attestation"] = {
            "method": "signed-review-record",
            "identity": f"reviewer:{gate_id}",
            "signed_at": "2026-08-15T00:00:00Z",
            "value": f"approval-{gate_id}",
        }
    return ledger


def semantic_problems(
    ledger: dict[str, object], *, prepublication: bool, complete: bool
) -> list[str]:
    problems = ledger_validator.Problems()
    ledger_validator.validate_review_shape(ledger, problems)
    ledger_validator.validate_candidate_semantics(
        ledger,
        problems,
        prepublication,
        complete,
    )
    return problems.items


def test_prepublication_allows_only_postpublication_gates_to_remain_pending() -> None:
    assert not semantic_problems(prepublication_ledger(), prepublication=True, complete=False)


def test_complete_requires_postpublication_gates_and_deployment_receipt() -> None:
    problems = semantic_problems(prepublication_ledger(), prepublication=False, complete=True)
    assert any("X018=pending" in problem for problem in problems)
    assert any("K044=pending" in problem for problem in problems)
    assert "require-complete needs deployment.release_id" in problems
    assert "require-complete needs deployment.deployed_at" in problems


def test_prepublication_rejects_nonfinal_required_decision() -> None:
    ledger = copy.deepcopy(prepublication_ledger())
    review = next(item for item in ledger["reviews"] if item["id"] == "X015")
    review["status"] = "rejected"
    problems = semantic_problems(ledger, prepublication=True, complete=False)
    assert any("X015=rejected" in problem for problem in problems)


def test_prepublication_rejects_unresolved_conditional_approval() -> None:
    ledger = copy.deepcopy(prepublication_ledger())
    review = next(item for item in ledger["reviews"] if item["id"] == "X015")
    review["status"] = "approved_with_conditions"
    review["conditions"] = ["Publish only after the named condition closes."]
    problems = semantic_problems(ledger, prepublication=True, complete=False)
    assert any("X015=approved_with_conditions" in problem for problem in problems)


def waived_review(gate_id: str) -> dict[str, object]:
    return {
        "status": "waived",
        "reviewer": {
            "name": "Release authority",
            "role": "interim administrator",
            "organization": "Example project",
            "independence_statement": (
                "Author and interim administrator of the candidate; not independent."
            ),
        },
        "reviewed_at": "2026-08-15T00:00:00Z",
        "decision_summary": (
            f"Gate {gate_id} is waived for first publication because no independent "
            "reviewer has been engaged. Residual risk is recorded in the status "
            "registry and the gate reopens for the next candidate."
        ),
        "conditions": [],
        "findings": [],
        "evidence": [
            {
                "kind": "waiver-record",
                "uri": f"evidence/{gate_id}/waiver.md",
                "sha256": "d" * 64,
            }
        ],
        "attestation": {
            "method": "chat-approval",
            "identity": "release-authority",
            "signed_at": "2026-08-15T00:00:00Z",
            "value": f"waiver-{gate_id}",
        },
    }


def _with_waiver(gate_id: str) -> dict[str, object]:
    ledger = copy.deepcopy(prepublication_ledger())
    review = next(item for item in ledger["reviews"] if item["id"] == gate_id)
    review.update(waived_review(gate_id))
    return ledger


def test_waived_independent_gate_is_final_with_waiver_record() -> None:
    for gate_id in sorted(ledger_validator.WAIVABLE_GATES):
        assert not semantic_problems(_with_waiver(gate_id), prepublication=True, complete=False), (
            gate_id
        )


def test_waiver_is_rejected_outside_independent_gates() -> None:
    problems = semantic_problems(_with_waiver("X015"), prepublication=True, complete=False)
    assert "X015 cannot be waived; only independent gates may be" in problems


def test_waiver_requires_waiver_record_and_rationale() -> None:
    ledger = _with_waiver("K045")
    review = next(item for item in ledger["reviews"] if item["id"] == "K045")
    review["evidence"] = [{"kind": "independent-security-report", "uri": "x", "sha256": "e" * 64}]
    review["decision_summary"] = "Waived because we said so."
    problems = semantic_problems(ledger, prepublication=True, complete=False)
    assert "K045 is missing evidence kinds ['waiver-record']" in problems
    assert any("written rationale" in problem for problem in problems)


def test_waiver_requires_relationship_disclosure() -> None:
    ledger = _with_waiver("S033")
    review = next(item for item in ledger["reviews"] if item["id"] == "S033")
    review["reviewer"]["independence_statement"] = "n/a"
    problems = semantic_problems(ledger, prepublication=True, complete=False)
    assert any("disclosure of its relationship" in problem for problem in problems)
