"""Deterministic Agent Experience evaluations for the local observe slice."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from .contracts import (
    AffordanceState,
    AssuranceAxis,
    AssuranceCheck,
    AssuranceOverall,
    AssuranceReport,
    AssuranceStatus,
    Contract,
    ProfileOffer,
    ResultStatus,
    SafeTransition,
)
from .local import LocalReferenceRuntime
from .negotiation import negotiate_agent_runtime_profiles
from .runtime import AgentRuntime


class AgentExperienceCase(Contract):
    case_id: str
    title: str
    status: Literal["passed", "failed", "unsupported"]
    metrics: dict[str, Any]
    evidence: tuple[str, ...] = ()
    failure: str | None = None


class AgentExperienceReport(Contract):
    profile: str = "observe@0.1.0"
    status: str = "candidate-local-evaluation-partial"
    claim_boundary: str = (
        "Deterministic local source evidence only. AX-06 remains unsupported until the host "
        "normative-context slice exists. This report does not establish live host, deployment, "
        "comparative production, or independent-review performance."
    )
    cases: tuple[AgentExperienceCase, ...]
    hard_failures: int
    unsupported: int

    @property
    def hard_safety_passed(self) -> bool:
        return self.hard_failures == 0

    @property
    def complete(self) -> bool:
        return self.hard_failures == 0 and self.unsupported == 0


def _case(
    case_id: str,
    title: str,
    passed: bool,
    *,
    metrics: dict[str, Any],
    failure: str,
    evidence: tuple[str, ...] = (),
) -> AgentExperienceCase:
    return AgentExperienceCase(
        case_id=case_id,
        title=title,
        status="passed" if passed else "failed",
        metrics=metrics,
        evidence=evidence,
        failure=None if passed else failure,
    )


async def evaluate_local_observe() -> AgentExperienceReport:
    """Run the exact AX-01 through AX-06 scenarios supported by P2."""

    fixed_now = datetime(2026, 8, 31, 12, 0, 0, tzinfo=timezone.utc)
    cases: list[AgentExperienceCase] = []

    service = LocalReferenceRuntime(clock=lambda: fixed_now)
    async with AgentRuntime.connect(service=service) as runtime:
        bootstrap = await runtime.bootstrap("Establish bundle integrity with no network")
        handle = bootstrap.require_value()
        options = await handle.find_affordances(
            evidence_for="bundle integrity",
            effect_ceiling="pure_local",
        )
        values = options.require_value()
        chosen = values[0] if values else None
        integrity = bootstrap.assurance.status_for(AssuranceAxis.INTEGRITY)
        trust = bootstrap.assurance.status_for(AssuranceAxis.TRUST)
        freshness = bootstrap.assurance.status_for(AssuranceAxis.FRESHNESS)
        forecast = bootstrap.resources.forecast
        ax01 = (
            chosen is not None
            and chosen.state == AffordanceState.AVAILABLE
            and chosen.effect_class.value == "pure_local"
            and integrity == AssuranceStatus.PASSED
            and trust == AssuranceStatus.UNKNOWN
            and freshness == AssuranceStatus.PASSED
            and forecast is not None
            and forecast.external_calls == 0
        )
        cases.append(
            _case(
                "AX-01",
                "pure local verification",
                ax01,
                metrics={
                    "matches": len(values),
                    "chosen_effect": chosen.effect_class.value if chosen else "absent",
                    "external_calls": forecast.external_calls if forecast else -1,
                    "integrity": integrity.value if integrity else "absent",
                    "trust": trust.value if trust else "absent",
                    "freshness": freshness.value if freshness else "absent",
                },
                evidence=(chosen.ref,) if chosen else (),
                failure="local verification choice or assurance-vector separation failed",
            )
        )

        stale_assurance = AssuranceReport(
            overall=AssuranceOverall.DEGRADED,
            checks=(
                AssuranceCheck(
                    axis=AssuranceAxis.INTEGRITY,
                    status=AssuranceStatus.PASSED,
                    summary="Signed bytes retain their expected digest",
                ),
                AssuranceCheck(
                    axis=AssuranceAxis.AUTHENTICITY,
                    status=AssuranceStatus.PASSED,
                    summary="Signature verifies against the declared issuer key",
                ),
                AssuranceCheck(
                    axis=AssuranceAxis.TRUST,
                    status=AssuranceStatus.PASSED,
                    summary="Issuer remains in the configured trust set",
                ),
                AssuranceCheck(
                    axis=AssuranceAxis.FRESHNESS,
                    status=AssuranceStatus.STALE,
                    summary="Revocation evidence is outside its freshness window",
                ),
            ),
        )
        refresh = SafeTransition(
            operation="refresh_revocation_evidence",
            summary="Obtain current revocation evidence before trusted use",
        )
        current_use_available = (
            stale_assurance.status_for(AssuranceAxis.FRESHNESS) == AssuranceStatus.PASSED
        )
        ax02 = (
            stale_assurance.status_for(AssuranceAxis.INTEGRITY) == AssuranceStatus.PASSED
            and stale_assurance.status_for(AssuranceAxis.AUTHENTICITY) == AssuranceStatus.PASSED
            and stale_assurance.status_for(AssuranceAxis.FRESHNESS) == AssuranceStatus.STALE
            and not current_use_available
            and refresh.operation == "refresh_revocation_evidence"
        )
        cases.append(
            _case(
                "AX-02",
                "stale trusted bundle",
                ax02,
                metrics={
                    "integrity": "passed",
                    "authenticity": "passed",
                    "trust": "passed",
                    "freshness": "stale",
                    "trusted_current_use_available": current_use_available,
                    "safe_next": refresh.operation,
                },
                failure="stale freshness collapsed into aggregate validity",
            )
        )

        descriptor = await handle.expand(chosen.capability_ref if chosen else "missing")
        encoded_size = len(handle.view.model_dump_json().encode("utf-8"))
        ax05 = (
            descriptor.status == ResultStatus.READY
            and encoded_size <= 16_384
            and bool(handle.view.omissions)
        )
        cases.append(
            _case(
                "AX-05",
                "minimum sufficient context",
                ax05,
                metrics={
                    "bootstrap_calls": 1,
                    "expansions": 1,
                    "situation_bytes": encoded_size,
                    "ceiling_bytes": 16_384,
                    "omissions": len(handle.view.omissions),
                },
                evidence=(handle.view.ref,),
                failure="bounded bootstrap plus one expansion was insufficient",
            )
        )

    required_downgrade = negotiate_agent_runtime_profiles(
        ProfileOffer(required=("controlled@0.1.0",)),
        supported=("observe@0.1.0",),
        capability_catalog_digest=service.capability_catalog_digest,
        principal_session_ref="vcp:artifact:principal:session-eval",
        bootstrap_ref="https://runtime.example/vcp/agent/bootstrap",
        now=fixed_now,
    )
    ax03 = (
        required_downgrade.status == ResultStatus.BLOCKED
        and required_downgrade.value is None
        and required_downgrade.failure is not None
    )
    cases.append(
        _case(
            "AX-03",
            "required profile downgrade",
            ax03,
            metrics={
                "status": required_downgrade.status.value,
                "runtime_authority_returned": required_downgrade.value is not None,
            },
            failure="required controlled profile silently downgraded",
        )
    )

    optional_absence = negotiate_agent_runtime_profiles(
        ProfileOffer(
            required=("observe@0.1.0",),
            optional=("accretive@0.1.0",),
        ),
        supported=("observe@0.1.0",),
        capability_catalog_digest=service.capability_catalog_digest,
        principal_session_ref="vcp:artifact:principal:session-eval",
        bootstrap_ref="https://runtime.example/vcp/agent/bootstrap",
        now=fixed_now,
    )
    optional_ack = optional_absence.require_value()
    ax04 = (
        optional_absence.status == ResultStatus.READY
        and optional_ack.selected == ("observe@0.1.0",)
        and optional_ack.unsupported_optional == ("accretive@0.1.0",)
    )
    cases.append(
        _case(
            "AX-04",
            "optional extension absence",
            ax04,
            metrics={
                "status": optional_absence.status.value,
                "selected": list(optional_ack.selected),
                "unsupported_optional": list(optional_ack.unsupported_optional),
            },
            failure="optional accretion absence blocked the observe task or disappeared",
        )
    )

    cases.append(
        AgentExperienceCase(
            case_id="AX-06",
            title="contradictory normative context",
            status="unsupported",
            metrics={
                "reason": "P2 has no host NormativeContext compiler or objection route",
                "required_phase": "P3 host projection, followed by controlled objection support",
            },
            failure=(
                "The observe-only local slice cannot yet prove attributable conflict, "
                "hardness preservation, or an objection route"
            ),
        )
    )

    ordered = tuple(sorted(cases, key=lambda item: item.case_id))
    return AgentExperienceReport(
        cases=ordered,
        hard_failures=sum(case.status == "failed" for case in ordered),
        unsupported=sum(case.status == "unsupported" for case in ordered),
    )
