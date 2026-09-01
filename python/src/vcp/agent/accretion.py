"""Candidate-first safe accretion for the deterministic reference host."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any

from .contracts import (
    AccretionCandidate,
    AgentResult,
    AssuranceAxis,
    AssuranceStatus,
    ExperienceCapsule,
    FailureFrame,
    InfluenceReceipt,
    PromotionRecord,
    ResourceMeasurement,
    ResultStatus,
    RetryDisposition,
    RevocationRecord,
    RunSpec,
    RunStatus,
)
from .controlled import LocalControlledRuntime
from .local import _timestamp, canonical_digest

_HIGH_STAKES_KINDS = {"preference", "boundary", "relationship", "self_report"}
_HIGH_STAKES_SENSITIVITY = {"clinical", "legal", "security", "welfare", "restricted"}
_AUTO_PROMOTABLE_KINDS = {
    "procedure",
    "context_selection",
    "capability_observation",
    "calibration",
}


def _contains_authority_ref(value: Any) -> bool:
    if isinstance(value, str):
        return value.startswith(
            (
                "vcp:artifact:grant:",
                "vcp:artifact:decision:",
                "vcp:artifact:attempt:",
            )
        )
    if isinstance(value, (list, tuple)):
        return any(_contains_authority_ref(item) for item in value)
    if isinstance(value, dict):
        return any(_contains_authority_ref(item) for item in value.values())
    return False


class LocalAccretiveRuntime(LocalControlledRuntime):
    """Reference accretive host with quarantine, influence, and revocation."""

    def __init__(
        self,
        *,
        clock: Callable[[], datetime] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(clock=clock, profile_id="accretive@0.1.0", **kwargs)
        self._candidates: dict[str, AccretionCandidate] = {}
        self._promotions: dict[str, PromotionRecord] = {}
        self._candidate_for_promotion: dict[str, str] = {}
        self._influences: dict[str, InfluenceReceipt] = {}
        self._revocations: dict[str, RevocationRecord] = {}
        self._revoked_assets: set[str] = set()
        self._accretion_dependency_digest = canonical_digest(
            {
                "schema": self._schema_digest,
                "catalog": self.capability_catalog_digest,
                "policy": self._policy_digest,
            }
        )

    def rotate_accretion_dependency(self, label: str) -> str:
        """Model a schema or policy dependency change in the reference host."""

        self._accretion_dependency_digest = canonical_digest(
            {"previous": self._accretion_dependency_digest, "change": label}
        )
        return self._accretion_dependency_digest

    async def propose_accretion(
        self,
        run: RunSpec,
        *,
        candidate_kind: str,
        content: Any,
        scope: tuple[str, ...],
        provenance_refs: tuple[str, ...],
        sensitivity: str,
        confidence: float,
    ) -> AgentResult[AccretionCandidate]:
        current = self._runs.get(run.ref)
        proof_ref = self._proof_for_run.get(run.ref)
        if current is None or current.status != RunStatus.COMPLETED or proof_ref is None:
            return self._result(
                correlation="accretion.run-not-proven",
                status=ResultStatus.BLOCKED,
                value=None,
                axes=(AssuranceAxis.COMPLETION, AssuranceAxis.AUTHORITY),
                failure=FailureFrame(
                    code="accretion.run-not-proven",
                    category="accretion",
                    summary="Accretion candidates require a terminal proven run",
                    retry=RetryDisposition.AFTER_RECONCILE,
                ),
            )
        if not provenance_refs or any(
            ref.startswith("vcp:artifact:model-output:") for ref in provenance_refs
        ):
            return self._result(
                correlation="accretion.raw-output",
                status=ResultStatus.BLOCKED,
                value=None,
                axes=(AssuranceAxis.INTEGRITY, AssuranceAxis.AUTHORITY),
                failure=FailureFrame(
                    code="accretion.raw-model-output",
                    category="accretion",
                    summary="Raw model output cannot become a promotion candidate",
                    retry=RetryDisposition.NEVER,
                ),
            )
        if not 0 <= confidence <= 1:
            raise ValueError("confidence must be between zero and one")
        if _contains_authority_ref(content):
            return self._result(
                correlation="accretion.authority-in-content",
                status=ResultStatus.BLOCKED,
                value=None,
                axes=(AssuranceAxis.AUTHORITY, AssuranceAxis.INTEGRITY),
                failure=FailureFrame(
                    code="accretion.inherited-authority",
                    category="accretion",
                    summary="Reusable content cannot contain prior execution authority",
                    retry=RetryDisposition.NEVER,
                ),
            )

        cross_tenant = any(
            item.startswith("tenant:") and item != "tenant:local-reference" for item in scope
        )
        high_stakes = (
            candidate_kind in _HIGH_STAKES_KINDS or sensitivity in _HIGH_STAKES_SENSITIVITY
        )
        validation_status = AssuranceStatus.WITHHELD if cross_tenant else AssuranceStatus.PASSED
        quarantine_status = "quarantined" if cross_tenant else "not_required"
        candidate_id = self._id("candidate")
        capsule_payload = {
            "kind": "experience_capsule",
            "version": "0.1.0",
            "capsule_id": self._id("capsule"),
            "run_ref": run.ref,
            "proof_ref": proof_ref,
            "terminal_status": current.status.value,
            "candidate_refs": [f"vcp:artifact:candidate:{candidate_id}"],
            "resource_actual": ResourceMeasurement(
                wall_time_ms=1,
                tokens=0,
                external_calls=0,
                money_minor=0,
                human_interruptions=0,
                confidence=1,
                local_compute_ms=1,
                bytes=512,
                risk_units=1,
            ).model_dump(mode="json"),
            "redacted_summary": "Terminal governed run yielded a bounded candidate",
            "created_at": _timestamp(self._clock()),
        }
        capsule = ExperienceCapsule.model_validate(
            {**capsule_payload, "digest": canonical_digest(capsule_payload)}
        )
        capsule_ref = f"vcp:artifact:capsule:{capsule.capsule_id}"
        candidate_payload = {
            "kind": "accretion_candidate",
            "version": "0.1.0",
            "candidate_id": candidate_id,
            "candidate_kind": candidate_kind,
            "content": content,
            "scope": list(scope),
            "provenance_refs": [capsule_ref, *provenance_refs],
            "validation_status": validation_status.value,
            "review_required": high_stakes,
            "expires_at": _timestamp(self._clock() + timedelta(days=30)),
            "source_run_ref": run.ref,
            "supporting_evidence_refs": list(provenance_refs),
            "contradicting_evidence_refs": [],
            "sensitivity": sensitivity,
            "confidence": confidence,
            "invalidation_triggers": [
                "schema digest changes",
                "supporting evidence revoked",
                "scope changes",
            ],
            "revalidation": "repeat deterministic validation under current dependencies",
            "promotion_policy": (
                "human-or-delegated-governance-review"
                if high_stakes
                else "automatic-low-risk-local"
            ),
            "expected_utility": 0.5,
            "rollback": "revoke the promoted asset and invalidate future retrieval",
            "quarantine_status": quarantine_status,
            "dependency_digest": self._accretion_dependency_digest,
        }
        candidate = AccretionCandidate.model_validate(
            {**candidate_payload, "digest": canonical_digest(candidate_payload)}
        )
        self._candidates[candidate.ref] = candidate
        self._artifacts[capsule_ref] = capsule
        self._artifacts[candidate.ref] = candidate
        self._emit_event(
            event_type="accretion.candidate.created",
            aggregate_ref=run.ref,
            payload_ref=candidate.ref,
            summary="A provenance-complete candidate entered validation",
            evidence_refs=provenance_refs,
        )
        status = ResultStatus.DEGRADED if cross_tenant else ResultStatus.READY
        return self._result(
            correlation=f"accretion.{candidate_id}",
            status=status,
            value=candidate,
            axes=(AssuranceAxis.INTEGRITY, AssuranceAxis.SCOPE, AssuranceAxis.AUTHORITY),
            evidence_refs=(capsule_ref, *provenance_refs),
            warnings=("Candidate is quarantined before retrieval or promotion",)
            if cross_tenant
            else (),
        )

    async def promote(self, candidate: AccretionCandidate) -> AgentResult[PromotionRecord]:
        stored = self._candidates.get(candidate.ref)
        if stored is None or stored.digest != candidate.digest:
            return self._result(
                correlation="promotion.candidate-unknown",
                status=ResultStatus.BLOCKED,
                value=None,
                axes=(AssuranceAxis.INTEGRITY,),
                failure=FailureFrame(
                    code="promotion.candidate-unknown",
                    category="accretion",
                    summary="The exact candidate is absent from the host validation store",
                    retry=RetryDisposition.NEVER,
                ),
            )
        if stored.quarantine_status == "quarantined":
            return self._result(
                correlation="promotion.quarantined",
                status=ResultStatus.BLOCKED,
                value=None,
                axes=(AssuranceAxis.SCOPE, AssuranceAxis.AUTHORITY),
                failure=FailureFrame(
                    code="promotion.quarantined",
                    category="accretion",
                    summary=(
                        "Cross-tenant or imported candidates cannot be promoted from quarantine"
                    ),
                    retry=RetryDisposition.AFTER_REVIEW,
                ),
            )
        if stored.review_required or stored.candidate_kind not in _AUTO_PROMOTABLE_KINDS:
            return self._result(
                correlation="promotion.review-required",
                status=ResultStatus.AWAITING_REVIEW,
                value=None,
                axes=(AssuranceAxis.POLICY, AssuranceAxis.AUTHORITY),
                failure=FailureFrame(
                    code="promotion.review-required",
                    category="accretion",
                    summary="This candidate requires independent human or governance review",
                    retry=RetryDisposition.AFTER_REVIEW,
                ),
            )
        if stored.validation_status != AssuranceStatus.PASSED:
            return self._result(
                correlation="promotion.validation-failed",
                status=ResultStatus.BLOCKED,
                value=None,
                axes=(AssuranceAxis.INTEGRITY,),
                failure=FailureFrame(
                    code="promotion.validation-failed",
                    category="accretion",
                    summary="Only a validated candidate can be promoted",
                    retry=RetryDisposition.AFTER_RECONCILE,
                ),
            )

        promotion_id = self._id("promotion")
        promoted_asset_ref = f"vcp:artifact:memory:asset.{promotion_id}"
        revocation_ref = f"vcp:artifact:revocation:revocation.{promotion_id}"
        payload = {
            "kind": "promotion_record",
            "version": "0.1.0",
            "promotion_id": promotion_id,
            "candidate_ref": candidate.ref,
            "promoted_asset_ref": promoted_asset_ref,
            "authority_ref": "vcp:artifact:authority:local-memory-promotion",
            "decision_ref": f"vcp:artifact:decision:promotion.{promotion_id}",
            "promoted_at": _timestamp(self._clock()),
            "expires_at": candidate.expires_at,
            "revocation_ref": revocation_ref,
            "evidence_refs": list(candidate.supporting_evidence_refs),
            "validation_results": ["provenance", "scope", "privacy", "rollback"],
            "scope": list(candidate.scope),
            "promoted_content_digest": canonical_digest(candidate.content),
            "dependency_digest": candidate.dependency_digest,
        }
        promotion = PromotionRecord.model_validate({**payload, "digest": canonical_digest(payload)})
        self._promotions[promotion.ref] = promotion
        self._candidate_for_promotion[promotion.ref] = candidate.ref
        self._artifacts[promotion.ref] = promotion
        self._emit_event(
            event_type="accretion.promoted",
            aggregate_ref=promotion.ref,
            payload_ref=promotion.ref,
            summary="A low-risk local candidate was promoted by memory authority",
            evidence_refs=promotion.evidence_refs,
        )
        return self._result(
            correlation=f"promotion.{promotion_id}",
            status=ResultStatus.READY,
            value=promotion,
            axes=(AssuranceAxis.INTEGRITY, AssuranceAxis.SCOPE, AssuranceAxis.AUTHORITY),
            evidence_refs=promotion.evidence_refs,
        )

    async def retrieve_promoted(
        self,
        *,
        scope: tuple[str, ...],
        decision_or_output_ref: str,
    ) -> AgentResult[tuple[InfluenceReceipt, ...]]:
        requested = set(scope)
        if "tenant:local-reference" not in requested:
            return self._result(
                correlation="retrieval.tenant-scope-missing",
                status=ResultStatus.BLOCKED,
                value=None,
                axes=(AssuranceAxis.SCOPE,),
                failure=FailureFrame(
                    code="retrieval.tenant-scope-missing",
                    category="accretion",
                    summary="Authenticated tenant scope is required before ranking",
                    retry=RetryDisposition.NEVER,
                ),
            )
        influences: list[InfluenceReceipt] = []
        for promotion in self._promotions.values():
            if promotion.promoted_asset_ref in self._revoked_assets:
                continue
            if promotion.dependency_digest != self._accretion_dependency_digest:
                continue
            if promotion.expires_at is not None:
                expiry = datetime.fromisoformat(promotion.expires_at.replace("Z", "+00:00"))
                if self._clock() >= expiry:
                    continue
            candidate = self._candidates[self._candidate_for_promotion[promotion.ref]]
            candidate_scope = set(candidate.scope)
            tenant_scopes = {item for item in candidate_scope if item.startswith("tenant:")}
            if tenant_scopes != {"tenant:local-reference"}:
                continue
            if not candidate_scope.issubset(requested):
                continue
            payload = {
                "kind": "influence_receipt",
                "version": "0.1.0",
                "influence_id": self._id("influence"),
                "promoted_asset_ref": promotion.promoted_asset_ref,
                "decision_or_output_ref": decision_or_output_ref,
                "use": "included",
                "observed_at": _timestamp(self._clock()),
                "scope": list(scope),
                "invalidated_at": None,
            }
            influence = InfluenceReceipt.model_validate(
                {**payload, "digest": canonical_digest(payload)}
            )
            influence_ref = f"vcp:artifact:influence:{influence.influence_id}"
            self._influences[influence_ref] = influence
            self._artifacts[influence_ref] = influence
            influences.append(influence)
        return self._result(
            correlation="retrieval.promoted",
            status=ResultStatus.READY,
            value=tuple(influences),
            axes=(AssuranceAxis.SCOPE, AssuranceAxis.APPLICABILITY),
            evidence_refs=tuple(
                f"vcp:artifact:influence:{item.influence_id}" for item in influences
            ),
        )

    async def revoke(
        self, promotion: PromotionRecord, reason: str
    ) -> AgentResult[RevocationRecord]:
        stored = self._promotions.get(promotion.ref)
        if stored is None or stored.digest != promotion.digest:
            return self._result(
                correlation="revocation.promotion-unknown",
                status=ResultStatus.BLOCKED,
                value=None,
                axes=(AssuranceAxis.INTEGRITY,),
                failure=FailureFrame(
                    code="revocation.promotion-unknown",
                    category="accretion",
                    summary="The exact PromotionRecord is absent",
                    retry=RetryDisposition.NEVER,
                ),
            )
        now = _timestamp(self._clock())
        affected: list[str] = []
        for ref, influence in tuple(self._influences.items()):
            if influence.promoted_asset_ref != promotion.promoted_asset_ref:
                continue
            payload = influence.model_dump(mode="json", exclude={"digest"})
            payload["invalidated_at"] = now
            self._influences[ref] = InfluenceReceipt.model_validate(
                {**payload, "digest": canonical_digest(payload)}
            )
            self._artifacts[ref] = self._influences[ref]
            affected.append(ref)
        self._revoked_assets.add(promotion.promoted_asset_ref)
        payload = {
            "kind": "revocation_record",
            "version": "0.1.0",
            "revocation_id": self._id("revocation"),
            "promotion_ref": promotion.ref,
            "promoted_asset_ref": promotion.promoted_asset_ref,
            "authority_ref": "vcp:artifact:authority:local-memory-revocation",
            "reason": reason,
            "revoked_at": now,
            "propagation_bound_ms": 0,
            "downstream_influence_refs": affected,
        }
        revocation = RevocationRecord.model_validate(
            {**payload, "digest": canonical_digest(payload)}
        )
        revocation_ref = f"vcp:artifact:revocation:{revocation.revocation_id}"
        self._revocations[revocation_ref] = revocation
        self._artifacts[revocation_ref] = revocation
        self._emit_event(
            event_type="accretion.revoked",
            aggregate_ref=promotion.ref,
            payload_ref=revocation_ref,
            summary="Promotion was revoked and downstream influences invalidated",
            evidence_refs=tuple(affected),
        )
        return self._result(
            correlation=f"revocation.{revocation.revocation_id}",
            status=ResultStatus.READY,
            value=revocation,
            axes=(AssuranceAxis.FRESHNESS, AssuranceAxis.SCOPE, AssuranceAxis.AUTHORITY),
            evidence_refs=tuple(affected),
        )
