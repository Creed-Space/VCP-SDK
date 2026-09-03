use serde_json::Value;
use vcp_core::agent::{
    parse_agent_artifact, parse_agent_runtime_document, AgentResultStatus, AgentRuntimeDocument,
    LocalAgentRuntime,
};

/// Crate-local mirrors of `conformance/agent-runtime/*.json`, kept
/// byte-identical by `scripts/validate_repo.py`, so the packaged crate's
/// tests run without the repository checkout.
fn fixture(name: &str) -> Value {
    let text = match name {
        "observe_contracts.json" => include_str!("../testdata/observe_contracts.json"),
        "controlled_contracts.json" => include_str!("../testdata/controlled_contracts.json"),
        "accretive_contracts.json" => include_str!("../testdata/accretive_contracts.json"),
        other => panic!("unknown shared fixture {other}"),
    };
    serde_json::from_str(text).expect("fixture JSON")
}

#[test]
fn local_bootstrap_is_bounded_and_deterministic() {
    let runtime = LocalAgentRuntime;
    let first = runtime.bootstrap("Orient safely").unwrap();
    let second = runtime.bootstrap("Orient safely").unwrap();
    assert_eq!(first.status, AgentResultStatus::Ready);
    assert_eq!(
        first.value.as_ref().unwrap().view().digest,
        second.value.as_ref().unwrap().view().digest
    );
    let view = first.value.unwrap().into_view();
    assert!(view.unknowns.contains(&"deployment state".to_owned()));
    assert_eq!(
        view.authority_refs,
        vec!["vcp:artifact:authority:local-read"]
    );
}

#[test]
fn shared_profile_fixtures_parse_and_reject_authority_injection() {
    let mut checked = 0;
    for name in [
        "observe_contracts.json",
        "controlled_contracts.json",
        "accretive_contracts.json",
    ] {
        let fixture = fixture(name);
        let cases = fixture["test_cases"].as_array().unwrap();
        for case in cases {
            checked += 1;
            let encoded = serde_json::to_string(&case["document"]).unwrap();
            let parsed = parse_agent_runtime_document(&encoded);
            if case["expected_valid"] == true {
                let document = parsed.expect("valid shared fixture");
                assert!(matches!(
                    document,
                    AgentRuntimeDocument::ProfileOffer(_)
                        | AgentRuntimeDocument::ProfileAcknowledgement(_)
                        | AgentRuntimeDocument::SituationView(_)
                        | AgentRuntimeDocument::ActionIntent(_)
                        | AgentRuntimeDocument::AccretionCandidate(_)
                ));
            } else {
                assert!(parsed.is_err(), "injected field must fail");
            }
        }
    }
    assert_eq!(checked, 10);
}

#[test]
fn duplicate_keys_are_rejected_before_typed_deserialization() {
    let encoded = r#"{
        "kind":"execution_receipt",
        "kind":"execution_receipt",
        "version":"0.1.0",
        "receipt_id":"r",
        "attempt_ref":"vcp:artifact:attempt:a",
        "effect_status":"none",
        "provider_ref":null,
        "evidence_refs":[],
        "observed_at":"2026-09-01T00:00:00Z",
        "reconcile_ref":null,
        "digest":"sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    }"#;
    assert!(parse_agent_artifact(encoded).is_err());
}
