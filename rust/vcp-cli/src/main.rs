//! # vcp-cli
//!
//! Command-line interface for VCP SDK operations.
//!
//! ## Usage
//!
//! ```text
//! vcp-cli parse-token family.safe.guide@1.2.0
//! vcp-cli parse-csm1 N5+F+E
//! vcp-cli encode-csm1 '{"persona":"Nanny","adherence_level":5,...}'
//! vcp-cli hash <content-file>
//! vcp-cli verify <manifest.json> <content-file>
//! ```

use std::fs;
use std::process;

use clap::{Parser, Subcommand};

use vcp_core::context::FullContext;
use vcp_core::csm1::{Csm1Code, Csm1Token};
use vcp_core::identity::VcpToken;
use vcp_core::transport;

#[derive(Parser)]
#[command(name = "vcp-cli")]
#[command(about = "Value Context Protocol SDK command-line tools")]
#[command(version)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Parse a VCP/I identity token and display its components.
    ParseToken {
        /// Token string (e.g. "family.safe.guide@1.2.0").
        token: String,
    },

    /// Parse a CSM-1 compact code and display its components.
    ParseCsm1 {
        /// CSM-1 code string (e.g. "N5+F+E").
        code: String,
    },

    /// Parse a CSM-1 8-line token from a file or stdin.
    ParseCsm1Token {
        /// Path to a file containing the 8-line token, or "-" for stdin.
        #[arg(default_value = "-")]
        path: String,
    },

    /// Encode a CSM-1 code from JSON input.
    EncodeCsm1 {
        /// JSON object (e.g. '{"persona":"Nanny","adherence_level":5,"scopes":[]}').
        json: String,
    },

    /// Parse a context wire-format string.
    ParseContext {
        /// Wire-format string.
        wire: String,
    },

    /// Compute SHA-256 content hash of a file.
    Hash {
        /// Path to the content file.
        path: String,
    },

    /// Verify a bundle (manifest + content).
    Verify {
        /// Path to the manifest JSON file.
        manifest: String,
        /// Path to the content file.
        content: String,
    },
}

fn main() {
    let cli = Cli::parse();

    let result = match cli.command {
        Commands::ParseToken { token } => cmd_parse_token(&token),
        Commands::ParseCsm1 { code } => cmd_parse_csm1(&code),
        Commands::ParseCsm1Token { path } => cmd_parse_csm1_token(&path),
        Commands::EncodeCsm1 { json } => cmd_encode_csm1(&json),
        Commands::ParseContext { wire } => cmd_parse_context(&wire),
        Commands::Hash { path } => cmd_hash(&path),
        Commands::Verify { manifest, content } => cmd_verify(&manifest, &content),
    };

    if let Err(e) = result {
        eprintln!("error: {e}");
        process::exit(1);
    }
}

fn cmd_parse_token(raw: &str) -> Result<(), String> {
    let token = VcpToken::parse(raw).map_err(|e| e.to_string())?;
    let json = serde_json::to_string_pretty(&token).map_err(|e| e.to_string())?;
    println!("{json}");
    println!();
    println!("domain:    {}", token.domain());
    println!("approach:  {}", token.approach());
    println!("role:      {}", token.role());
    println!("depth:     {}", token.depth());
    if let Some(ref v) = token.version {
        println!("version:   {v}");
    }
    if let Some(ref ns) = token.namespace {
        println!("namespace: {ns}");
    }
    println!("canonical: {}", token.canonical());
    println!("full:      {}", token.full());
    Ok(())
}

fn cmd_parse_csm1(raw: &str) -> Result<(), String> {
    let code = Csm1Code::parse(raw).map_err(|e| e.to_string())?;
    let json = serde_json::to_string_pretty(&code).map_err(|e| e.to_string())?;
    println!("{json}");
    println!();
    println!(
        "persona:   {} ({})",
        code.persona,
        code.persona.description()
    );
    println!("level:     {}", code.adherence_level);
    if !code.scopes.is_empty() {
        let scope_strs: Vec<String> = code
            .scopes
            .iter()
            .map(|s| format!("{} ({})", s.code(), s.description()))
            .collect();
        println!("scopes:    {}", scope_strs.join(", "));
    }
    if let Some(ref ns) = code.namespace {
        println!("namespace: {ns}");
    }
    if let Some(ref v) = code.version {
        println!("version:   {v}");
    }
    println!("active:    {}", code.is_active());
    println!("maximum:   {}", code.is_maximum());
    println!("encoded:   {}", code.encode());
    Ok(())
}

fn cmd_parse_csm1_token(path: &str) -> Result<(), String> {
    let input = if path == "-" {
        use std::io::Read;
        let mut buf = String::new();
        std::io::stdin()
            .read_to_string(&mut buf)
            .map_err(|e| e.to_string())?;
        buf
    } else {
        fs::read_to_string(path).map_err(|e| format!("cannot read {path}: {e}"))?
    };

    let token = Csm1Token::parse(&input).map_err(|e| e.to_string())?;
    let json = serde_json::to_string_pretty(&token).map_err(|e| e.to_string())?;
    println!("{json}");
    Ok(())
}

fn cmd_encode_csm1(json: &str) -> Result<(), String> {
    let code: Csm1Code = serde_json::from_str(json).map_err(|e| e.to_string())?;
    println!("{}", code.encode());
    Ok(())
}

fn cmd_parse_context(wire: &str) -> Result<(), String> {
    let ctx = FullContext::from_wire(wire).map_err(|e| e.to_string())?;
    let json = serde_json::to_string_pretty(&ctx).map_err(|e| e.to_string())?;
    println!("{json}");
    Ok(())
}

fn cmd_hash(path: &str) -> Result<(), String> {
    let content = fs::read_to_string(path).map_err(|e| format!("cannot read {path}: {e}"))?;
    let hash = transport::compute_content_hash(&content).map_err(|e| e.to_string())?;
    println!("{hash}");
    Ok(())
}

fn cmd_verify(manifest_path: &str, content_path: &str) -> Result<(), String> {
    let manifest_json = fs::read_to_string(manifest_path)
        .map_err(|e| format!("cannot read {manifest_path}: {e}"))?;
    let content =
        fs::read_to_string(content_path).map_err(|e| format!("cannot read {content_path}: {e}"))?;

    let result = transport::verify_bundle(&manifest_json, &content).map_err(|e| e.to_string())?;

    if result.is_valid() {
        println!("VALID: {}", result.message);
    } else {
        println!("FAILED [{}]: {}", result.code, result.message);
        process::exit(2);
    }

    Ok(())
}
