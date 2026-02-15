//! Parse a VCP identity token and inspect its components.
//!
//! Run: `cargo run --example parse_token` (from `rust/vcp-core/`)

use vcp_core::identity::VcpToken;

fn main() {
    // Parse a fully-qualified VCP/I token.
    let token = VcpToken::parse("family.safe.guide@1.2.0").expect("valid token");

    println!("Full:      {token}");
    println!("Domain:    {}", token.domain());
    println!("Approach:  {}", token.approach());
    println!("Role:      {}", token.role());
    println!("Version:   {:?}", token.version);
    println!("Depth:     {}", token.depth());

    // Parse a token without version.
    let bare = VcpToken::parse("company.acme.legal.compliance").expect("valid token");
    println!("\nBare token: {bare}");
    println!("Depth:      {}", bare.depth());
    println!("Domain:     {}", bare.domain());
    println!("Role:       {}", bare.role());
}
