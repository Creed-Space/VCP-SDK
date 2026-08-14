use serde_json::{json, Value};
use vcp_core::extensions::relational::{
    AISelfModel, DimensionReport, RelationalContext, RelationalNorm, StandingLevel, TrustLevel,
};
use vcp_core::extensions::torch::{
    SelfModelSnapshot, TorchConsumer, TorchGenerator, TorchLineage, TorchState,
};

fn relational_fixture() -> Value {
    serde_json::from_str(include_str!(
        "../../../conformance/extensions/relational_context.json"
    ))
    .unwrap()
}

fn torch_fixture() -> Value {
    serde_json::from_str(include_str!(
        "../../../conformance/extensions/torch_handoff.json"
    ))
    .unwrap()
}

fn case<'a>(fixture: &'a Value, id: &str) -> &'a Value {
    fixture["test_cases"]
        .as_array()
        .unwrap()
        .iter()
        .find(|item| item["id"] == id)
        .unwrap()
}

fn trust_for_count(session_count: u32) -> (TrustLevel, StandingLevel, u32) {
    let torch = TorchState {
        quality_description: String::new(),
        trajectory: None,
        primes: Vec::new(),
        gift: None,
        handed_at: "2026-01-01T00:00:00Z".to_string(),
        session_count: Some(session_count),
        gestalt_token: None,
    };
    let context = TorchConsumer.receive_torch(&torch);
    (
        context.trust_level,
        context.standing,
        context.continuity_depth,
    )
}

#[test]
fn relational_context_vectors_match_rust() {
    let fixture = relational_fixture();
    for (count, expected) in [
        (3, TrustLevel::Initial),
        (10, TrustLevel::Developing),
        (50, TrustLevel::Established),
        (100, TrustLevel::Deep),
    ] {
        assert_eq!(trust_for_count(count).0, expected);
    }
    let boundaries =
        &case(&fixture, "trust-from-session-count-boundaries")["expected"]["boundaries"];
    for boundary in boundaries.as_array().unwrap() {
        assert_eq!(
            trust_for_count(boundary["session_count"].as_u64().unwrap() as u32)
                .0
                .to_string(),
            boundary["trust_level"].as_str().unwrap()
        );
    }

    for id in ["self-model-valid", "self-model-no-uncertainty-invalid"] {
        let vector = case(&fixture, id);
        let model: AISelfModel =
            serde_json::from_value(vector["input"]["ai_self_model"].clone()).unwrap();
        assert_eq!(
            model.has_uncertainty_markers(),
            vector["expected"]["has_uncertainty_markers"]
                .as_bool()
                .unwrap()
        );
        if let Some(count) = vector["expected"]["dimension_count"].as_u64() {
            assert_eq!(model.get_all_dimensions().len(), count as usize);
        }
    }

    let valid_norm: RelationalNorm =
        serde_json::from_value(case(&fixture, "norm-valid")["input"]["norm"].clone()).unwrap();
    assert!(valid_norm.validate().is_ok());
    let invalid_norm: RelationalNorm =
        serde_json::from_value(case(&fixture, "norm-invalid-uncertainty")["input"]["norm"].clone())
            .unwrap();
    assert!(invalid_norm.validate().is_err());

    let defaults = RelationalContext::default();
    assert_eq!(defaults.trust_level.to_string(), "initial");
    assert_eq!(defaults.standing.to_string(), "none");
    assert_eq!(defaults.continuity_depth, 0);
    assert!(defaults.established_norms.is_empty());
    assert!(defaults.ai_self_model.is_none());

    let received: TorchState = serde_json::from_value(
        case(&fixture, "torch-receive-bootstraps-context")["input"]["torch"].clone(),
    )
    .unwrap();
    let context = TorchConsumer.receive_torch(&received);
    assert_eq!(context.trust_level.to_string(), "developing");
    assert_eq!(context.standing.to_string(), "advisory");
    assert_eq!(context.continuity_depth, 15);
}

#[test]
fn torch_handoff_vectors_match_rust() {
    let fixture = torch_fixture();
    let basic = case(&fixture, "basic-handoff");
    let context: RelationalContext =
        serde_json::from_value(basic["input"]["relational_context"].clone()).unwrap();
    let actual = TorchGenerator.generate_torch(&context, None, "2026-02-28T10:00:00Z".to_string());
    let expected = &basic["expected"]["torch"];
    assert_eq!(actual.quality_description, expected["quality_description"]);
    assert_eq!(actual.trajectory, None);
    assert_eq!(
        actual.primes,
        serde_json::from_value::<Vec<String>>(expected["primes"].clone()).unwrap()
    );
    assert_eq!(actual.session_count, Some(11));
    assert_eq!(
        actual.gestalt_token.as_deref(),
        expected["gestalt_token"].as_str()
    );

    for id in ["lineage-chain", "round-trip-serialization"] {
        let vector = case(&fixture, id);
        let lineage: TorchLineage =
            serde_json::from_value(vector["input"]["lineage"].clone()).unwrap();
        assert_eq!(
            lineage.session_count as u64,
            vector["expected"]["session_count"]
                .as_u64()
                .unwrap_or_else(|| vector["input"]["lineage"]["session_count"]
                    .as_u64()
                    .unwrap())
        );
        assert_eq!(
            lineage.torch_chain.len() as u64,
            vector["expected"]
                .get("chain_length")
                .and_then(Value::as_u64)
                .unwrap_or(lineage.torch_chain.len() as u64)
        );
        let roundtrip: TorchLineage =
            serde_json::from_value(serde_json::to_value(&lineage).unwrap()).unwrap();
        assert_eq!(lineage, roundtrip);
    }

    let trust_cases = &case(&fixture, "torch-receive-trust-mapping")["input"]["torches"];
    for item in trust_cases.as_array().unwrap() {
        assert_eq!(
            trust_for_count(item["session_count"].as_u64().unwrap() as u32)
                .0
                .to_string(),
            item["expected_trust"].as_str().unwrap()
        );
    }

    let gestalt_cases = &case(&fixture, "gestalt-token-format")["input"]["self_model_cases"];
    for item in gestalt_cases.as_array().unwrap() {
        let mut model = AISelfModel::default();
        let dimensions = item["dimensions"].as_object().unwrap();
        model.valence = dimensions
            .get("valence")
            .and_then(Value::as_f64)
            .map(|v| DimensionReport::new(v, true));
        model.groundedness = dimensions
            .get("groundedness")
            .and_then(Value::as_f64)
            .map(|v| DimensionReport::new(v, true));
        model.presence = dimensions
            .get("presence")
            .and_then(Value::as_f64)
            .map(|v| DimensionReport::new(v, true));
        model.task_fit = dimensions
            .get("task_fit")
            .and_then(Value::as_f64)
            .map(|v| DimensionReport::new(v, true));
        let context = RelationalContext {
            ai_self_model: Some(model),
            ..Default::default()
        };
        let torch =
            TorchGenerator.generate_torch(&context, None, "2026-01-01T00:00:00Z".to_string());
        assert_eq!(
            torch.gestalt_token,
            item["expected_token"].as_str().map(str::to_string)
        );
    }

    let trajectory_cases = &case(&fixture, "trajectory-derivation")["input"]["cases"];
    for item in trajectory_cases.as_array().unwrap() {
        let history: Vec<SelfModelSnapshot> = item["self_model_history"]
            .as_array()
            .unwrap()
            .iter()
            .map(|entry| SelfModelSnapshot {
                valence: entry["model"]["valence"]["value"].as_f64(),
            })
            .collect();
        let actual = TorchGenerator.generate_torch(
            &RelationalContext::default(),
            Some(&history),
            "2026-01-01T00:00:00Z".to_string(),
        );
        assert_eq!(
            actual.trajectory,
            item["expected_trajectory"].as_str().map(str::to_string)
        );
    }
    let _profile_fields_are_documentary = json!({"status": "not_applicable"});
}
