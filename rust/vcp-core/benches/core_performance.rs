use std::hint::black_box;

use criterion::{criterion_group, criterion_main, Criterion};
use ed25519_dalek::SigningKey;
use serde_json::{json, Map, Value};
use vcp_core::csm1::Csm1Code;
use vcp_core::revocation::Crl;
use vcp_core::transport::{
    canonicalize_manifest, compute_content_hash, sign_manifest, verify_manifest_signature,
};
use vcp_core::VcpToken;

fn core_performance(criterion: &mut Criterion) {
    criterion.bench_function("csm1_parse_encode", |bencher| {
        bencher.iter(|| {
            let code = Csm1Code::parse(black_box("Z5+P+T:SEC@4.2.0")).unwrap();
            black_box(code.encode());
        });
    });

    let content = "vcp-performance-payload\n".repeat(2_800);
    criterion.bench_function("content_hash_64k", |bencher| {
        bencher.iter(|| black_box(compute_content_hash(black_box(&content)).unwrap()));
    });

    let token = VcpToken::parse("company.product.safety.review.workflow.agent").unwrap();
    criterion.bench_function("scope_glob_6", |bencher| {
        bencher.iter(|| black_box(token.matches_pattern(black_box("company.*.safety.**"))));
    });

    let fields: Map<String, Value> = (0..512)
        .map(|index| (format!("field_{index:04}"), Value::String("v".repeat(80))))
        .collect();
    let large_manifest = json!({"bundle": fields, "signature": {"value": "excluded"}});
    criterion.bench_function("manifest_canonicalization_48k", |bencher| {
        bencher.iter(|| black_box(canonicalize_manifest(black_box(&large_manifest)).unwrap()));
    });

    let signature_manifest = json!({"bundle": {"id": "verification-probe"}});
    let signing_key = SigningKey::from_bytes(&[7; 32]);
    let public_key = signing_key.verifying_key().to_bytes();
    let signature = sign_manifest(&signature_manifest, &signing_key.to_bytes()).unwrap();
    criterion.bench_function("ed25519_manifest_verification", |bencher| {
        bencher.iter(|| {
            black_box(
                verify_manifest_signature(
                    black_box(&signature_manifest),
                    black_box(&public_key),
                    black_box(&signature),
                )
                .unwrap(),
            )
        });
    });

    let crl = r#"{
        "issuer":"issuer.example",
        "updated_at":"2026-01-01T00:00:00Z",
        "next_update":"2099-01-01T00:00:00Z",
        "revoked":[
            {"jti":"bundle-1","revoked_at":"2026-02-01T00:00:00Z","reason":"test"}
        ]
    }"#;
    criterion.bench_function("crl_parse", |bencher| {
        bencher.iter(|| black_box(Crl::from_json(black_box(crl)).unwrap()));
    });
}

criterion_group!(benches, core_performance);
criterion_main!(benches);
