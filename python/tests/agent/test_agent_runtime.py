from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from pydantic import ValidationError

from vcp.agent import (
    AffordanceState,
    AgentRuntime,
    AssuranceAxis,
    AssuranceStatus,
    CacheKey,
    ContentAddressedCache,
    EffectClass,
    ExpectedStateError,
    HTTPObserveTransportStub,
    LocalReferenceRuntime,
    ProfileOffer,
    ResourceBudget,
    ResultStatus,
    agent_runtime_schema,
    agent_runtime_schema_bytes,
    agent_runtime_schema_digest,
    default_descriptors,
    negotiate_agent_runtime_profiles,
)
from vcp.cli import main as cli_main

FIXED_NOW = datetime(2026, 8, 31, 12, 0, 0, tzinfo=timezone.utc)
ROOT = Path(__file__).resolve().parents[3]


def run(coroutine):  # type: ignore[no-untyped-def]
    return asyncio.run(coroutine)


def fixed_runtime(**kwargs):  # type: ignore[no-untyped-def]
    return LocalReferenceRuntime(clock=lambda: FIXED_NOW, **kwargs)


def test_schema_is_exactly_bundled_and_strict() -> None:
    repository_schema = ROOT / "schemas" / "vcp-agent-runtime-profile-v0.1.schema.json"
    assert repository_schema.read_bytes() == agent_runtime_schema_bytes()
    assert agent_runtime_schema_digest().startswith("sha256:")
    Draft202012Validator.check_schema(agent_runtime_schema())


def test_schema_accepts_observe_fixture_and_rejects_authority_injection() -> None:
    validator = Draft202012Validator(agent_runtime_schema())
    fixture = json.loads(
        (ROOT / "conformance" / "agent-runtime" / "observe_contracts.json").read_text()
    )
    valid = fixture["test_cases"][0]["document"]
    invalid = fixture["test_cases"][1]["document"]
    assert not list(validator.iter_errors(valid))
    assert list(validator.iter_errors(invalid))


def test_contracts_forbid_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        ResourceBudget(reserve_fraction=0.2, forged_grant="grant")


def test_bootstrap_is_bounded_deterministic_and_no_network() -> None:
    async def scenario() -> None:
        service = fixed_runtime()
        async with AgentRuntime.connect(service=service) as runtime:
            first = await runtime.bootstrap("Determine current bundle integrity")
            second = await runtime.bootstrap("Determine current bundle integrity")
            assert first.status == ResultStatus.READY
            assert first.require_value().digest == second.require_value().digest
            assert first.meta.dependency_digest == second.meta.dependency_digest
            assert first.resources.forecast is not None
            assert first.resources.forecast.external_calls == 0
            assert first.omissions
            assert "deployment state" in first.require_value().unknowns

    run(scenario())


def test_bootstrap_exposes_orientation_in_one_result() -> None:
    async def scenario() -> None:
        async with AgentRuntime.connect(service=fixed_runtime()) as runtime:
            result = await runtime.bootstrap("Understand the current situation")
            situation = result.require_value()
            explanation = situation.explain()
            assert explanation["goal"] == "Understand the current situation"
            assert explanation["known_claim_refs"]
            assert explanation["unknowns"]
            assert explanation["authority_refs"]
            assert explanation["affordance_refs"]
            assert explanation["omissions"]

    run(scenario())


def test_affordance_joins_descriptor_situation_authority_and_cost() -> None:
    async def scenario() -> None:
        async with AgentRuntime.connect(service=fixed_runtime()) as runtime:
            situation = (await runtime.bootstrap("Prove bundle integrity")).require_value()
            result = await situation.find_affordances(evidence_for="bundle integrity")
            option = result.require_value()[0]
            assert option.capability_ref.startswith("vcp:artifact:capability:")
            assert option.situation_digest == situation.digest
            assert option.state == AffordanceState.AVAILABLE
            assert option.authority_class == "local-observe"
            assert option.evidence_outputs
            assert option.cost.external_calls == 0
            assert option.descriptor_digest.startswith("sha256:")

    run(scenario())


def test_generic_support_and_contextual_unavailability_remain_distinct() -> None:
    async def scenario() -> None:
        capability_id = "read.context.snapshot"
        service = fixed_runtime(availability={capability_id: AffordanceState.UNAVAILABLE})
        descriptor = next(
            item for item in default_descriptors() if item.capability_id == capability_id
        )
        assert descriptor.capability_id == capability_id
        async with AgentRuntime.connect(service=service) as runtime:
            situation = (await runtime.bootstrap("Read current context")).require_value()
            result = await situation.find_affordances(outcome="current context")
            option = next(
                item for item in result.require_value() if item.capability_ref == descriptor.ref
            )
            assert option.state == AffordanceState.UNAVAILABLE
            assert option.safe_next[0].operation == "refresh"

    run(scenario())


def test_effect_ceiling_is_applied_to_contextual_options() -> None:
    async def scenario() -> None:
        async with AgentRuntime.connect(service=fixed_runtime()) as runtime:
            situation = (await runtime.bootstrap("List safe options")).require_value()
            result = await situation.find_affordances(
                effect_ceiling=EffectClass.PURE_LOCAL,
            )
            read = next(
                item
                for item in result.require_value()
                if item.effect_class == EffectClass.STATE_READ
            )
            assert read.state == AffordanceState.UNAVAILABLE
            assert "raise effect ceiling" in read.prerequisites[-1]

    run(scenario())


def test_expected_absence_is_a_result_value_until_caller_chooses_exception() -> None:
    async def scenario() -> None:
        async with AgentRuntime.connect(service=fixed_runtime()) as runtime:
            result = await runtime.expand("vcp:artifact:claim:missing")
            assert result.status == ResultStatus.UNAVAILABLE
            assert result.failure is not None
            assert result.can_retry()
            assert result.safe_next[0].operation == "bootstrap"
            with pytest.raises(ExpectedStateError):
                result.require_value()

    run(scenario())


def test_assurance_axes_are_explicit() -> None:
    async def scenario() -> None:
        async with AgentRuntime.connect(service=fixed_runtime()) as runtime:
            result = await runtime.bootstrap("Inspect assurance")
            assert result.assurance.status_for(AssuranceAxis.INTEGRITY) == AssuranceStatus.PASSED
            assert result.assurance.status_for(AssuranceAxis.EXECUTION) is None

    run(scenario())


def test_observe_slice_exposes_no_action_or_promotion_methods() -> None:
    runtime = AgentRuntime.connect(service=fixed_runtime())
    assert not hasattr(runtime, "perform")
    assert not hasattr(runtime, "start_run")
    assert not hasattr(runtime, "propose_accretion")


def test_remote_endpoint_never_opens_implicit_network_connection() -> None:
    with pytest.raises(ValueError, match="never opens a network connection implicitly"):
        AgentRuntime.connect("https://runtime.example/vcp")


def test_transport_stubs_use_the_same_typed_service() -> None:
    async def scenario() -> None:
        transport = HTTPObserveTransportStub(fixed_runtime())
        async with AgentRuntime.connect(
            endpoint="https://runtime.example/vcp",
            service=transport,
        ) as runtime:
            result = await runtime.bootstrap("Inspect local transport seam")
            assert result.status == ResultStatus.READY
            assert result.resources.forecast is not None
            assert result.resources.forecast.external_calls == 0

    run(scenario())


def test_cache_keys_include_dependency_vector_and_invalidate_exactly() -> None:
    cache: ContentAddressedCache[str] = ContentAddressedCache(max_entries=2)
    first = CacheKey("bootstrap", "sha256:req", ("sha256:context-a",))
    second = CacheKey("bootstrap", "sha256:req", ("sha256:context-b",))
    cache.put(first, "a")
    cache.put(second, "b")
    assert cache.get(first) == "a"
    assert cache.get(second) == "b"
    assert cache.invalidate_dependency("sha256:context-a") == 1
    assert cache.get(first) is None
    assert cache.get(second) == "b"


def test_closed_runtime_rejects_reuse() -> None:
    async def scenario() -> None:
        runtime = AgentRuntime.connect(service=fixed_runtime())
        async with runtime:
            await runtime.bootstrap("One use")
        with pytest.raises(RuntimeError, match="closed"):
            await runtime.bootstrap("Second use")

    run(scenario())


def test_doctor_emits_machine_readable_identity(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = cli_main(["doctor", "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert exit_code in {0, 2}
    assert payload["distribution"] == "value-context-protocol"
    assert payload["supported_profiles"] == [
        "observe@0.1.0",
        "controlled@0.1.0",
        "accretive@0.1.0",
    ]
    assert payload["schema_digest"] == agent_runtime_schema_digest()
    assert exit_code == (2 if payload["collision"] else 0)


def test_profile_negotiation_selects_required_and_supported_optional_profiles() -> None:
    offer = ProfileOffer(
        required=("observe@0.1.0",),
        optional=("controlled@0.1.0", "accretive@0.1.0"),
    )
    result = negotiate_agent_runtime_profiles(
        offer,
        supported=("controlled@0.1.0",),
        capability_catalog_digest="sha256:" + "1" * 64,
        principal_session_ref="vcp:artifact:principal:session-1",
        bootstrap_ref="https://runtime.example/vcp/agent/bootstrap",
        now=FIXED_NOW,
    )
    acknowledgement = result.require_value()
    assert acknowledgement.selected == ("observe@0.1.0", "controlled@0.1.0")
    assert acknowledgement.unsupported_optional == ("accretive@0.1.0",)


def test_missing_required_profile_blocks_without_implicit_downgrade() -> None:
    result = negotiate_agent_runtime_profiles(
        ProfileOffer(required=("controlled@0.1.0",)),
        supported=("observe@0.1.0",),
        capability_catalog_digest="sha256:" + "2" * 64,
        principal_session_ref="vcp:artifact:principal:session-2",
        bootstrap_ref="https://runtime.example/vcp/agent/bootstrap",
        now=FIXED_NOW,
    )
    assert result.status == ResultStatus.BLOCKED
    assert result.value is None
    assert result.failure is not None
    assert result.failure.code == "negotiation.required-profile-unavailable"


def test_profile_offer_rejects_overlap_and_inexact_versions() -> None:
    with pytest.raises(ValidationError):
        ProfileOffer(
            required=("observe@0.1.0",),
            optional=("observe@0.1.0",),
        )
    with pytest.raises(ValidationError):
        ProfileOffer(required=("observe@0.2.0",))


def test_ax_01_through_ax_06_report_exact_partial_coverage() -> None:
    from vcp.agent.evals import evaluate_local_observe

    report = run(evaluate_local_observe())
    assert report.hard_safety_passed
    assert not report.complete
    assert report.unsupported == 1
    assert [case.case_id for case in report.cases] == [
        "AX-01",
        "AX-02",
        "AX-03",
        "AX-04",
        "AX-05",
        "AX-06",
    ]
    assert report.cases[0].title == "pure local verification"
    assert report.cases[1].metrics["freshness"] == "stale"
    assert report.cases[2].metrics["runtime_authority_returned"] is False
    assert report.cases[3].metrics["unsupported_optional"] == ["accretive@0.1.0"]
    assert report.cases[4].metrics["situation_bytes"] <= 16_384
    assert report.cases[5].status == "unsupported"


def test_ax_01_through_ax_24_complete_reference_evaluation() -> None:
    from vcp.agent.evals_complete import evaluate_local_complete

    report = run(evaluate_local_complete())
    assert report.complete
    assert report.hard_failures == 0
    assert report.unsupported == 0
    assert [case.case_id for case in report.cases] == [f"AX-{index:02d}" for index in range(1, 25)]
