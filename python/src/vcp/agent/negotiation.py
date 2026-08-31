"""Downgrade-resistant Agent Runtime Profile candidate negotiation."""

from __future__ import annotations

import hashlib
from collections.abc import Iterable
from datetime import datetime, timedelta, timezone
from typing import Any

import rfc8785

from .contracts import (
    AgentResult,
    AssuranceAxis,
    AssuranceCheck,
    AssuranceOverall,
    AssuranceReport,
    AssuranceStatus,
    FailureFrame,
    ProfileAcknowledgement,
    ProfileOffer,
    ResultMeta,
    ResultStatus,
    RetryDisposition,
    SafeTransition,
)
from .schema import agent_runtime_schema_digest

_PROFILE_ORDER = {
    "observe@0.1.0": 0,
    "controlled@0.1.0": 1,
    "accretive@0.1.0": 2,
}


def _digest(value: Any) -> str:
    return f"sha256:{hashlib.sha256(rfc8785.dumps(value)).hexdigest()}"


def _timestamp(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("negotiation time must be timezone-aware")
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace(
        "+00:00", "Z"
    )


def _support_closure(supported: Iterable[str]) -> set[str]:
    closure = set(supported)
    if "accretive@0.1.0" in closure:
        closure.update({"controlled@0.1.0", "observe@0.1.0"})
    if "controlled@0.1.0" in closure:
        closure.add("observe@0.1.0")
    unknown = closure - _PROFILE_ORDER.keys()
    if unknown:
        raise ValueError(f"server advertised unsupported candidate profiles: {sorted(unknown)}")
    return closure


def negotiate_agent_runtime_profiles(
    offer: ProfileOffer,
    *,
    supported: Iterable[str],
    capability_catalog_digest: str,
    principal_session_ref: str,
    bootstrap_ref: str,
    now: datetime | None = None,
    lifetime: timedelta = timedelta(minutes=15),
) -> AgentResult[ProfileAcknowledgement]:
    """Negotiate exact profiles while preserving required versus optional meaning."""

    if lifetime <= timedelta(0):
        raise ValueError("negotiation acknowledgement lifetime must be positive")
    current = now or datetime.now(timezone.utc)
    available = _support_closure(supported)
    missing_required = tuple(item for item in offer.required if item not in available)
    unsupported_optional = tuple(item for item in offer.optional if item not in available)
    selected = tuple(
        sorted(
            {
                item
                for item in offer.required + offer.optional
                if item in available
            },
            key=_PROFILE_ORDER.__getitem__,
        )
    )
    dependency = _digest(
        {
            "offer": offer.model_dump(mode="json"),
            "supported": sorted(available),
            "capability_catalog_digest": capability_catalog_digest,
            "principal_session_ref": principal_session_ref,
            "bootstrap_ref": bootstrap_ref,
        }
    )
    meta = ResultMeta(
        schema_digest=agent_runtime_schema_digest(),
        correlation_id=f"negotiation.{dependency[-16:]}",
        as_of=_timestamp(current),
        dependency_digest=dependency,
    )
    if missing_required:
        transition = SafeTransition(
            operation="revise_profile_offer",
            summary="Remove an unavailable required profile or connect to a compatible host",
        )
        failure = FailureFrame(
            code="negotiation.required-profile-unavailable",
            category="negotiation",
            summary=f"Required profiles are unavailable: {', '.join(missing_required)}",
            retry=RetryDisposition.NEVER,
            safe_next=(transition,),
        )
        return AgentResult(
            meta=meta,
            status=ResultStatus.BLOCKED,
            value=None,
            assurance=AssuranceReport(
                overall=AssuranceOverall.BLOCKED,
                checks=(
                    AssuranceCheck(
                        axis=AssuranceAxis.APPLICABILITY,
                        status=AssuranceStatus.FAILED,
                        summary="At least one required exact profile is unavailable",
                    ),
                ),
            ),
            safe_next=(transition,),
            failure=failure,
        )
    acknowledgement = ProfileAcknowledgement(
        selected=selected,
        unsupported_optional=unsupported_optional,
        bootstrap_ref=bootstrap_ref,
        capability_catalog_digest=capability_catalog_digest,
        principal_session_ref=principal_session_ref,
        event_binding="cursor",
        expires_at=_timestamp(current + lifetime),
    )
    return AgentResult(
        meta=meta,
        status=ResultStatus.READY,
        value=acknowledgement,
        assurance=AssuranceReport(
            overall=AssuranceOverall.READY,
            checks=(
                AssuranceCheck(
                    axis=AssuranceAxis.APPLICABILITY,
                    status=AssuranceStatus.PASSED,
                    summary="Every required exact profile was selected",
                ),
                AssuranceCheck(
                    axis=AssuranceAxis.SCOPE,
                    status=AssuranceStatus.PASSED,
                    summary="Acknowledgement is bound to the offered profile set",
                ),
            ),
        ),
    )
