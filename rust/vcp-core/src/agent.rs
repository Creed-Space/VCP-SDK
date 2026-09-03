//! Agent-intuitive contracts and a no-network observe reference facade.
//!
//! Controlled and accretive artifacts are portable here for cross-language
//! inspection. Execution authority remains a host responsibility.

use serde::{Deserialize, Serialize};
use serde_json::Value;
use sha2::{Digest, Sha256};

use crate::error::{VcpError, VcpResult};
use crate::transport::parse_json_strict;

/// Exact candidate runtime profile.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum AgentProfile {
    /// Bounded orientation and capability discovery.
    #[serde(rename = "observe@0.1.0")]
    Observe,
    /// Governed execution and proof artifacts.
    #[serde(rename = "controlled@0.1.0")]
    Controlled,
    /// Candidate-first learning with traceable influence.
    #[serde(rename = "accretive@0.1.0")]
    Accretive,
}

impl AgentProfile {
    /// Return the exact versioned profile identifier.
    pub const fn identifier(self) -> &'static str {
        match self {
            Self::Observe => "observe@0.1.0",
            Self::Controlled => "controlled@0.1.0",
            Self::Accretive => "accretive@0.1.0",
        }
    }
}

/// Required and optional exact Agent Runtime Profile candidates.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct AgentRuntimeProfileOffer {
    pub version: String,
    pub required: Vec<AgentProfile>,
    pub optional: Vec<AgentProfile>,
}

/// Host acknowledgement bound to bootstrap, catalog, principal, event mode, and expiry.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct AgentRuntimeProfileAcknowledgement {
    pub version: String,
    pub selected: Vec<AgentProfile>,
    pub unsupported_optional: Vec<AgentProfile>,
    pub bootstrap_ref: String,
    pub capability_catalog_digest: String,
    pub principal_session_ref: String,
    pub event_binding: EventBinding,
    pub expires_at: String,
}

/// Negotiated event projection mode.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum EventBinding {
    Cursor,
    Stream,
    Poll,
}

/// Explicit effect class ordered from local computation to physical effect.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum EffectClass {
    /// Pure local computation.
    PureLocal,
    /// Read host state.
    StateRead,
    /// Disclose sensitive information.
    SensitiveEgress,
    /// Reversible mutation.
    ReversibleWrite,
    /// Communicate externally.
    Communication,
    /// Create a financial effect.
    Financial,
    /// Create a legal effect.
    Legal,
    /// Create a physical effect.
    Physical,
}

/// Every resource dimension available to profile planning.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ResourceBudget {
    pub wall_time_ms: Option<u64>,
    pub tokens: Option<u64>,
    pub external_calls: Option<u64>,
    pub money_minor: Option<u64>,
    pub human_interruptions: Option<u64>,
    pub reserve_fraction: f64,
    pub model_calls: Option<u64>,
    pub local_compute_ms: Option<u64>,
    pub bytes: Option<u64>,
    pub sensitive_egress_bytes: Option<u64>,
    pub privacy_units: Option<u64>,
    pub risk_units: Option<u64>,
    pub welfare_load_units: Option<u64>,
}

impl ResourceBudget {
    /// Conservative no-network observe budget.
    pub const fn observe_default() -> Self {
        Self {
            wall_time_ms: Some(2_000),
            tokens: Some(4_000),
            external_calls: Some(0),
            money_minor: Some(0),
            human_interruptions: Some(0),
            reserve_fraction: 0.2,
            model_calls: Some(0),
            local_compute_ms: Some(500),
            bytes: Some(65_536),
            sensitive_egress_bytes: Some(0),
            privacy_units: Some(0),
            risk_units: Some(0),
            welfare_load_units: Some(0),
        }
    }
}

/// One explicitly accounted omission.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Omission {
    pub field: String,
    pub reason: String,
    #[serde(default)]
    pub expand_ref: Option<String>,
}

/// Bounded orientation root.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct SituationView {
    pub version: String,
    pub situation_id: String,
    pub goal: String,
    pub principal_ref: String,
    pub known_claim_refs: Vec<String>,
    pub unknowns: Vec<String>,
    pub conflict_refs: Vec<String>,
    pub normative_context_ref: String,
    pub authority_refs: Vec<String>,
    pub budget: ResourceBudget,
    pub active_work_refs: Vec<String>,
    pub control_operations: Vec<String>,
    pub affordance_refs: Vec<String>,
    pub omissions: Vec<Omission>,
    pub as_of: String,
    pub cursor: String,
    pub dependency_digest: String,
    pub digest: String,
}

/// Exact preflighted controlled-action intent.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ActionIntent {
    pub version: String,
    pub intent_id: String,
    pub run_ref: String,
    pub step_ref: String,
    pub affordance_ref: String,
    pub arguments_digest: String,
    pub destination: String,
    pub context_digest: String,
    pub policy_digest: String,
    pub descriptor_digest: String,
    pub requested_at: String,
    pub digest: String,
    pub schema_digest: String,
    pub effect_class: EffectClass,
    pub situation_digest: String,
    pub expected_postconditions: Vec<String>,
    pub resource_ceiling: ResourceBudget,
    pub idempotency_scope: String,
    pub requested_authority: String,
}

/// Observed status of an attempted effect.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum EffectStatus {
    None,
    Accepted,
    Observed,
    Failed,
    Possible,
    Indeterminate,
    Compensated,
}

/// Runtime observation kept separate from policy and proof.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ExecutionReceipt {
    pub version: String,
    pub receipt_id: String,
    pub attempt_ref: String,
    pub effect_status: EffectStatus,
    pub provider_ref: Option<String>,
    pub evidence_refs: Vec<String>,
    pub observed_at: String,
    pub reconcile_ref: Option<String>,
    pub digest: String,
}

/// Candidate-first learned artifact.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct AccretionCandidate {
    pub version: String,
    pub candidate_id: String,
    pub candidate_kind: String,
    pub content: Value,
    pub scope: Vec<String>,
    pub provenance_refs: Vec<String>,
    pub validation_status: String,
    pub review_required: bool,
    #[serde(default)]
    pub expires_at: Option<String>,
    pub digest: String,
    pub source_run_ref: String,
    pub supporting_evidence_refs: Vec<String>,
    pub contradicting_evidence_refs: Vec<String>,
    pub sensitivity: String,
    pub confidence: f64,
    pub invalidation_triggers: Vec<String>,
    pub revalidation: String,
    pub promotion_policy: String,
    pub expected_utility: f64,
    pub rollback: String,
    pub quarantine_status: String,
    pub dependency_digest: String,
}

/// Auditable promotion under a distinct memory authority.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PromotionRecord {
    pub version: String,
    pub promotion_id: String,
    pub candidate_ref: String,
    pub promoted_asset_ref: String,
    pub authority_ref: String,
    pub decision_ref: String,
    pub promoted_at: String,
    #[serde(default)]
    pub expires_at: Option<String>,
    pub revocation_ref: String,
    pub digest: String,
    pub evidence_refs: Vec<String>,
    pub validation_results: Vec<String>,
    pub scope: Vec<String>,
    pub promoted_content_digest: String,
    pub dependency_digest: String,
}

/// Portable discriminated union for supported cross-language artifacts.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(tag = "kind")]
pub enum AgentArtifact {
    #[serde(rename = "situation_view")]
    SituationView(SituationView),
    #[serde(rename = "action_intent")]
    ActionIntent(ActionIntent),
    #[serde(rename = "execution_receipt")]
    ExecutionReceipt(ExecutionReceipt),
    #[serde(rename = "accretion_candidate")]
    AccretionCandidate(AccretionCandidate),
    #[serde(rename = "promotion_record")]
    PromotionRecord(PromotionRecord),
}

/// Portable runtime document, including authority-free profile negotiation.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(tag = "kind")]
pub enum AgentRuntimeDocument {
    #[serde(rename = "agent_runtime_profile_offer")]
    ProfileOffer(AgentRuntimeProfileOffer),
    #[serde(rename = "agent_runtime_profile_ack")]
    ProfileAcknowledgement(AgentRuntimeProfileAcknowledgement),
    #[serde(rename = "situation_view")]
    SituationView(SituationView),
    #[serde(rename = "action_intent")]
    ActionIntent(ActionIntent),
    #[serde(rename = "execution_receipt")]
    ExecutionReceipt(ExecutionReceipt),
    #[serde(rename = "accretion_candidate")]
    AccretionCandidate(AccretionCandidate),
    #[serde(rename = "promotion_record")]
    PromotionRecord(PromotionRecord),
}

/// Parse a strict portable runtime document, including exact profile negotiation.
///
/// # Errors
///
/// Returns `VcpError::JsonError` for malformed, duplicate, unsupported, or
/// authority-injected fields.
pub fn parse_agent_runtime_document(input: &str) -> VcpResult<AgentRuntimeDocument> {
    let value = parse_json_strict(input)?;
    if value.get("version").and_then(Value::as_str) != Some("0.1.0") {
        return Err(VcpError::JsonError(
            "unsupported agent runtime document version".into(),
        ));
    }
    let document: AgentRuntimeDocument = serde_json::from_value(value)?;
    match &document {
        AgentRuntimeDocument::ProfileOffer(offer) => {
            if offer.required.len() > 3 || offer.optional.len() > 3 {
                return Err(VcpError::JsonError(
                    "profile offer lists may contain at most three entries".into(),
                ));
            }
            let mut identifiers: Vec<_> = offer
                .required
                .iter()
                .chain(&offer.optional)
                .map(|profile| profile.identifier())
                .collect();
            let offered_count = identifiers.len();
            identifiers.sort_unstable();
            identifiers.dedup();
            if identifiers.len() != offered_count {
                return Err(VcpError::JsonError(
                    "profile offer entries must be unique".into(),
                ));
            }
        }
        AgentRuntimeDocument::ProfileAcknowledgement(acknowledgement)
            if acknowledgement.selected.is_empty() || acknowledgement.selected.len() > 3 =>
        {
            return Err(VcpError::JsonError(
                "selected profiles must contain one to three entries".into(),
            ));
        }
        _ => {}
    }
    Ok(document)
}

/// Parse strict JSON and reject duplicate or undeclared fields.
///
/// # Errors
///
/// Returns `VcpError::JsonError` for malformed, duplicate, unsupported, or
/// authority-injected fields.
pub fn parse_agent_artifact(input: &str) -> VcpResult<AgentArtifact> {
    match parse_agent_runtime_document(input)? {
        AgentRuntimeDocument::SituationView(value) => Ok(AgentArtifact::SituationView(value)),
        AgentRuntimeDocument::ActionIntent(value) => Ok(AgentArtifact::ActionIntent(value)),
        AgentRuntimeDocument::ExecutionReceipt(value) => Ok(AgentArtifact::ExecutionReceipt(value)),
        AgentRuntimeDocument::AccretionCandidate(value) => {
            Ok(AgentArtifact::AccretionCandidate(value))
        }
        AgentRuntimeDocument::PromotionRecord(value) => Ok(AgentArtifact::PromotionRecord(value)),
        AgentRuntimeDocument::ProfileOffer(_) | AgentRuntimeDocument::ProfileAcknowledgement(_) => {
            Err(VcpError::JsonError(
                "expected an agent artifact, received negotiation metadata".into(),
            ))
        }
    }
}

/// Operational result state retained without exception text.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum AgentResultStatus {
    Ready,
    Degraded,
    AwaitingReview,
    Blocked,
    Unavailable,
    Stale,
    Conflicting,
    BudgetExhausted,
    Indeterminate,
    Failed,
}

/// Typed operational result.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct AgentResult<T> {
    pub status: AgentResultStatus,
    pub value: Option<T>,
    pub evidence_refs: Vec<String>,
    pub warnings: Vec<String>,
}

/// Newtyped situation handle for exact portable state.
#[derive(Debug, Clone, PartialEq)]
pub struct SituationHandle(SituationView);

impl SituationHandle {
    /// Borrow the immutable portable view.
    pub const fn view(&self) -> &SituationView {
        &self.0
    }

    /// Consume the handle and return the portable view.
    pub fn into_view(self) -> SituationView {
        self.0
    }
}

/// No-network local observe facade.
#[derive(Debug, Default)]
pub struct LocalAgentRuntime;

impl LocalAgentRuntime {
    /// Compile a deterministic bounded view without opening a network connection.
    ///
    /// # Errors
    ///
    /// Returns `VcpError::ParseError` when the goal is empty or canonical JSON
    /// serialization fails.
    pub fn bootstrap(&self, goal: &str) -> VcpResult<AgentResult<SituationHandle>> {
        if goal.is_empty() {
            return Err(VcpError::ParseError("goal must not be empty".into()));
        }
        let budget = ResourceBudget::observe_default();
        let dependency_value = serde_json::json!({
            "goal": goal,
            "budget": budget,
            "profile": AgentProfile::Observe.identifier(),
        });
        let dependency = digest_value(&dependency_value)?;
        let suffix = &dependency[7..23];
        let mut view_value = serde_json::json!({
            "version": "0.1.0",
            "situation_id": format!("situation.rust.{suffix}"),
            "goal": goal,
            "principal_ref": "vcp:artifact:principal:rust-observer",
            "known_claim_refs": [],
            "unknowns": ["host policy state", "deployment state"],
            "conflict_refs": [],
            "normative_context_ref": "vcp:artifact:normative:rust-observe",
            "authority_refs": ["vcp:artifact:authority:local-read"],
            "budget": budget,
            "active_work_refs": [],
            "control_operations": [],
            "affordance_refs": [format!("vcp:artifact:affordance:inspect.assurance.{suffix}")],
            "omissions": [{"field": "host authority", "reason": "unavailable", "expand_ref": null}],
            "as_of": "1970-01-01T00:00:00Z",
            "cursor": "cursor.rust.0",
            "dependency_digest": dependency,
        });
        let digest = digest_value(&view_value)?;
        view_value
            .as_object_mut()
            .ok_or_else(|| VcpError::JsonError("situation must be an object".into()))?
            .insert("digest".into(), Value::String(digest));
        let view: SituationView = serde_json::from_value(view_value)?;
        Ok(AgentResult {
            status: AgentResultStatus::Ready,
            value: Some(SituationHandle(view)),
            evidence_refs: Vec::new(),
            warnings: Vec::new(),
        })
    }
}

fn digest_value(value: &Value) -> VcpResult<String> {
    let canonical = serde_json_canonicalizer::to_vec(value)
        .map_err(|error| VcpError::JsonError(error.to_string()))?;
    let mut hasher = Sha256::new();
    hasher.update(canonical);
    Ok(format!("sha256:{:x}", hasher.finalize()))
}
