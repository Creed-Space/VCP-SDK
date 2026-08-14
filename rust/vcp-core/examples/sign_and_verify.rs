//! Sign a manifest and verify the Ed25519 signature.
//!
//! Run: `cargo run --example sign_and_verify` (from `rust/vcp-core/`)

use vcp_core::transport::{sign_manifest, verify_manifest_signature};

fn main() {
    // Deterministic example-only key. Production callers must load a protected,
    // independently generated key instead of embedding secret key material.
    use ed25519_dalek::SigningKey;

    let signing_key = SigningKey::from_bytes(&[42_u8; 32]);
    let secret_bytes = signing_key.to_bytes();
    let public_bytes = signing_key.verifying_key().to_bytes();

    // A minimal manifest as a JSON value.
    let manifest: serde_json::Value = serde_json::json!({
        "vcp_version": "2.0",
        "bundle": {
            "id": "family.safe.guide",
            "version": "1.2.0",
            "content_hash": "sha256:abc123"
        }
    });

    // Sign the manifest.
    let signature = sign_manifest(&manifest, &secret_bytes).expect("signing ok");
    println!("Signature: {}", &signature[..40]);

    // Verify the signature.
    let valid =
        verify_manifest_signature(&manifest, &public_bytes, &signature).expect("verification ok");
    println!("Valid? {valid}");
}
