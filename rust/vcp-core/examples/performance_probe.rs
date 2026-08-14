use std::hint::black_box;
use std::time::Instant;

use ed25519_dalek::SigningKey;
use serde_json::{json, Map, Value};
use vcp_core::csm1::Csm1Code;
use vcp_core::transport::{
    canonicalize_manifest, compute_content_hash, sign_manifest, verify_manifest_signature,
};
use vcp_core::VcpToken;

fn summarize(name: &str, samples_ns: &mut [u128]) -> Value {
    samples_ns.sort_unstable();
    let count = samples_ns.len();
    let total_ns: u128 = samples_ns.iter().sum();
    let p50 = samples_ns[count / 2] as f64 / 1_000.0;
    let p95_index = ((count as f64 * 0.95).ceil() as usize).saturating_sub(1);
    let p95 = samples_ns[p95_index] as f64 / 1_000.0;
    json!({
        "name": name,
        "iterations": count,
        "ops_per_second": count as f64 / (total_ns as f64 / 1_000_000_000.0),
        "p50_us": p50,
        "p95_us": p95
    })
}

fn main() {
    let arguments: Vec<_> = std::env::args().collect();
    let argument_value = |name: &str, fallback: usize| {
        arguments
            .iter()
            .position(|argument| argument == name)
            .and_then(|index| arguments.get(index + 1))
            .and_then(|value| value.parse::<usize>().ok())
            .unwrap_or(fallback)
    };
    let iterations = argument_value("--iterations", 20_000).max(100);
    let hash_iterations = argument_value("--hash-iterations", 25).max(10);

    for _ in 0..1_000 {
        black_box(Csm1Code::parse("Z5+P+T:SEC@4.2.0").unwrap().encode());
    }

    let mut csm_samples = Vec::with_capacity(iterations);
    for _ in 0..iterations {
        let start = Instant::now();
        black_box(Csm1Code::parse("Z5+P+T:SEC@4.2.0").unwrap().encode());
        csm_samples.push(start.elapsed().as_nanos());
    }

    let content = "vcp-performance-payload\n".repeat(2_800);
    let mut hash_samples = Vec::with_capacity(hash_iterations);
    for _ in 0..hash_iterations {
        let start = Instant::now();
        black_box(compute_content_hash(&content).unwrap());
        hash_samples.push(start.elapsed().as_nanos());
    }

    let token = VcpToken::parse("company.product.safety.review.workflow.agent").unwrap();
    let mut scope_samples = Vec::with_capacity(iterations);
    for _ in 0..iterations {
        let start = Instant::now();
        black_box(token.matches_pattern("company.*.safety.**"));
        scope_samples.push(start.elapsed().as_nanos());
    }

    let fields: Map<String, Value> = (0..512)
        .map(|index| (format!("field_{index:04}"), Value::String("v".repeat(80))))
        .collect();
    let large_manifest = json!({"bundle": fields, "signature": {"value": "excluded"}});
    let mut manifest_samples = Vec::with_capacity(hash_iterations);
    for _ in 0..hash_iterations {
        let start = Instant::now();
        black_box(canonicalize_manifest(&large_manifest).unwrap());
        manifest_samples.push(start.elapsed().as_nanos());
    }

    let signature_manifest = json!({"bundle": {"id": "verification-probe"}});
    let signing_key = SigningKey::from_bytes(&[7; 32]);
    let public_key = signing_key.verifying_key().to_bytes();
    let signature = sign_manifest(&signature_manifest, &signing_key.to_bytes()).unwrap();
    let verification_iterations = (iterations / 20).max(100);
    let mut verification_samples = Vec::with_capacity(verification_iterations);
    for _ in 0..verification_iterations {
        let start = Instant::now();
        black_box(verify_manifest_signature(&signature_manifest, &public_key, &signature).unwrap());
        verification_samples.push(start.elapsed().as_nanos());
    }

    println!(
        "{}",
        json!({
            "runtime": "rust",
            "metrics": [
                summarize("rust_csm1_roundtrip", &mut csm_samples),
                summarize("rust_content_hash_64k", &mut hash_samples),
                summarize("rust_scope_glob_6", &mut scope_samples),
                summarize("rust_manifest_canonicalization_48k", &mut manifest_samples),
                summarize("rust_ed25519_verification", &mut verification_samples)
            ]
        })
    );
}
