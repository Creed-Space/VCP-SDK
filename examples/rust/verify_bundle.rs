//! Compute a content hash and verify it matches expectations.
//!
//! Run: `cargo run --example verify_bundle` (from `rust/vcp-core/`)

use vcp_core::transport::{compute_content_hash, verify_content_hash};

fn main() {
    let content = "Be kind to everyone.\n";

    // Compute the SHA-256 content hash (with canonicalization).
    let hash = compute_content_hash(content).expect("canonicalization ok");
    println!("Content hash: {hash}");

    // Verify the hash matches.
    let ok = verify_content_hash(content, &hash).expect("verify ok");
    println!("Hash valid?   {ok}");

    // A tampered hash should fail.
    let bad = verify_content_hash("Tampered content.\n", &hash).expect("verify ok");
    println!("Tampered?     {bad}");
}
