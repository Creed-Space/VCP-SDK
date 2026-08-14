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

use vcp_core::composer::{compose_layered, LayeredBundle};
use vcp_core::context::FullContext;
use vcp_core::csm1::{Csm1Code, Csm1Token, Persona};
use vcp_core::extensions::consensus::{Ballot, SchulzeElection};
use vcp_core::extensions::personal::{
    compute_decayed_intensity, compute_lifecycle_state, default_decay_config, DecayConfig,
    PersonalDimension,
};
use vcp_core::identity::VcpToken;
use vcp_core::negotiation::{negotiate_versioned, VersionedExtension};
use vcp_core::orchestrator::{classify_temporal_claims, Orchestrator, MAX_CONTENT_SIZE};
use vcp_core::transport;
use vcp_core::trust::TrustConfig;

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
    /// Canonicalize and validate a VCP/I identity token.
    CanonicalizeToken {
        /// Potentially non-canonical token string.
        token: String,
    },

    /// Check a VCP/I token against a segment wildcard pattern.
    MatchToken { token: String, pattern: String },

    /// Check ancestor and descendant relationships between two tokens.
    TokenHierarchy {
        ancestor: String,
        descendant: String,
    },

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

    /// Resolve a case-sensitive CSM-1 persona wire code.
    ResolvePersona { code: String },

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

    /// Encode a conformance-fixture context JSON object.
    EncodeContext { path: String },

    /// Canonicalize a UTF-8 content file and print a JSON string.
    CanonicalizeContent { path: String },

    /// Canonicalize a JSON manifest and print the JCS string.
    CanonicalizeManifest { path: String },

    /// Sign a JSON manifest with a deterministic 32-byte seed value.
    SignManifest { path: String, seed_byte: u8 },

    /// Verify a manifest signature with a hex-encoded 32-byte public key.
    VerifyManifestSignature {
        path: String,
        public_key_hex: String,
        signature: String,
    },

    /// Verify an Ed25519 signature over the exact bytes in a file.
    VerifyEd25519 {
        path: String,
        public_key_hex: String,
        signature: String,
    },

    /// Classify timestamp claims at the fixture's explicit reference time.
    ClassifyTemporal { path: String },

    /// Inspect size, canonicalization, and injection policy for content.
    ContentPolicy { path: String },

    /// Compute exponential personal-state decay for a fixture case.
    PersonalDecay {
        declared: u8,
        half_life_seconds: f64,
        baseline: u8,
        elapsed_seconds: u64,
        #[arg(long)]
        pinned: bool,
    },

    /// Compute personal-state lifecycle for a fixture case.
    PersonalLifecycle {
        declared: u8,
        half_life_seconds: f64,
        baseline: u8,
        elapsed_seconds: u64,
        fresh_window_seconds: f64,
        stale_threshold: f64,
        #[arg(long)]
        pinned: bool,
    },

    /// Print the default personal-state decay configuration table.
    PersonalConfigs,

    /// Negotiate the versioned extension fixture input in a JSON file.
    NegotiateExtensions { path: String },

    /// Run a Schulze consensus fixture input from a JSON file.
    RunConsensus { path: String },

    /// Run a layered constitution-composition fixture input.
    RunLayeredComposition { path: String },

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
        Commands::CanonicalizeToken { token } => cmd_canonicalize_token(&token),
        Commands::MatchToken { token, pattern } => cmd_match_token(&token, &pattern),
        Commands::TokenHierarchy {
            ancestor,
            descendant,
        } => cmd_token_hierarchy(&ancestor, &descendant),
        Commands::ParseToken { token } => cmd_parse_token(&token),
        Commands::ParseCsm1 { code } => cmd_parse_csm1(&code),
        Commands::ResolvePersona { code } => cmd_resolve_persona(&code),
        Commands::ParseCsm1Token { path } => cmd_parse_csm1_token(&path),
        Commands::EncodeCsm1 { json } => cmd_encode_csm1(&json),
        Commands::ParseContext { wire } => cmd_parse_context(&wire),
        Commands::EncodeContext { path } => cmd_encode_context(&path),
        Commands::CanonicalizeContent { path } => cmd_canonicalize_content(&path),
        Commands::CanonicalizeManifest { path } => cmd_canonicalize_manifest(&path),
        Commands::SignManifest { path, seed_byte } => cmd_sign_manifest(&path, seed_byte),
        Commands::VerifyManifestSignature {
            path,
            public_key_hex,
            signature,
        } => cmd_verify_manifest_signature(&path, &public_key_hex, &signature),
        Commands::VerifyEd25519 {
            path,
            public_key_hex,
            signature,
        } => cmd_verify_ed25519(&path, &public_key_hex, &signature),
        Commands::ClassifyTemporal { path } => cmd_classify_temporal(&path),
        Commands::ContentPolicy { path } => cmd_content_policy(&path),
        Commands::PersonalDecay {
            declared,
            half_life_seconds,
            baseline,
            elapsed_seconds,
            pinned,
        } => cmd_personal_decay(
            declared,
            half_life_seconds,
            baseline,
            elapsed_seconds,
            pinned,
        ),
        Commands::PersonalLifecycle {
            declared,
            half_life_seconds,
            baseline,
            elapsed_seconds,
            fresh_window_seconds,
            stale_threshold,
            pinned,
        } => cmd_personal_lifecycle(
            declared,
            half_life_seconds,
            baseline,
            elapsed_seconds,
            fresh_window_seconds,
            stale_threshold,
            pinned,
        ),
        Commands::PersonalConfigs => cmd_personal_configs(),
        Commands::NegotiateExtensions { path } => cmd_negotiate_extensions(&path),
        Commands::RunConsensus { path } => cmd_run_consensus(&path),
        Commands::RunLayeredComposition { path } => cmd_run_layered_composition(&path),
        Commands::Hash { path } => cmd_hash(&path),
        Commands::Verify { manifest, content } => cmd_verify(&manifest, &content),
    };

    if let Err(e) = result {
        eprintln!("error: {e}");
        process::exit(1);
    }
}

fn cmd_canonicalize_token(raw: &str) -> Result<(), String> {
    println!(
        "{}",
        VcpToken::canonicalize(raw).map_err(|error| error.to_string())?
    );
    Ok(())
}

fn cmd_match_token(raw: &str, pattern: &str) -> Result<(), String> {
    let token = VcpToken::parse(raw).map_err(|error| error.to_string())?;
    println!("{}", token.matches_pattern(pattern));
    Ok(())
}

fn cmd_token_hierarchy(ancestor_raw: &str, descendant_raw: &str) -> Result<(), String> {
    let ancestor = VcpToken::parse(ancestor_raw).map_err(|error| error.to_string())?;
    let descendant = VcpToken::parse(descendant_raw).map_err(|error| error.to_string())?;
    println!(
        "{}",
        serde_json::json!({
            "is_ancestor": ancestor.is_ancestor_of(&descendant),
            "is_descendant": descendant.is_descendant_of(&ancestor),
            "reverse_is_ancestor": descendant.is_ancestor_of(&ancestor),
        })
    );
    Ok(())
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

fn cmd_resolve_persona(raw: &str) -> Result<(), String> {
    let mut chars = raw.chars();
    let code = chars
        .next()
        .ok_or_else(|| "persona code is required".to_string())?;
    if chars.next().is_some() {
        return Err("persona code must be one character".to_string());
    }
    let persona = Persona::from_wire_char(code).map_err(|error| error.to_string())?;
    println!(
        "{}",
        serde_json::json!({
            "persona_code": persona.code().to_string(),
            "persona_name": format!("{persona:?}").to_lowercase(),
            "focus": persona.focus(),
            "default_adherence": persona.default_adherence(),
            "requires_namespace": persona == Persona::Custom,
        })
    );
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

fn cmd_encode_context(path: &str) -> Result<(), String> {
    let mut value = read_json(path)?;
    if let Some(personal) = value
        .get_mut("personal")
        .and_then(serde_json::Value::as_object_mut)
    {
        for (source, target) in [
            ("cognitive_state", "cognitive"),
            ("emotional_tone", "emotional"),
            ("energy_level", "energy"),
            ("perceived_urgency", "urgency"),
            ("body_signals", "body"),
        ] {
            if let Some(field) = personal.remove(source) {
                personal.insert(target.to_string(), field);
            }
        }
    }
    let context: FullContext = serde_json::from_value(value).map_err(|error| error.to_string())?;
    let wire = context.to_wire();
    let decoded = FullContext::from_wire(&wire).map_err(|error| error.to_string())?;
    println!(
        "{}",
        serde_json::json!({
            "wire": wire,
            "has_any": context.has_any(),
            "has_situational": context.situational.has_any(),
            "has_personal": context.personal.has_any(),
            "has_vep_0004": context.situational.has_vep_0004(),
            "conformance_level": context.conformance_level().label(),
            "roundtrip": decoded,
        })
    );
    Ok(())
}

fn read_json(path: &str) -> Result<serde_json::Value, String> {
    let raw = fs::read_to_string(path).map_err(|error| format!("cannot read {path}: {error}"))?;
    serde_json::from_str(&raw).map_err(|error| error.to_string())
}

fn cmd_canonicalize_content(path: &str) -> Result<(), String> {
    let content =
        fs::read_to_string(path).map_err(|error| format!("cannot read {path}: {error}"))?;
    let canonical = transport::canonicalize_content(&content).map_err(|error| error.to_string())?;
    let canonical = String::from_utf8(canonical).map_err(|error| error.to_string())?;
    println!(
        "{}",
        serde_json::to_string(&canonical).map_err(|error| error.to_string())?
    );
    Ok(())
}

fn cmd_canonicalize_manifest(path: &str) -> Result<(), String> {
    let manifest = read_json(path)?;
    let canonical =
        transport::canonicalize_manifest(&manifest).map_err(|error| error.to_string())?;
    println!(
        "{}",
        String::from_utf8(canonical).map_err(|error| error.to_string())?
    );
    Ok(())
}

fn cmd_sign_manifest(path: &str, seed_byte: u8) -> Result<(), String> {
    let manifest = read_json(path)?;
    let signature =
        transport::sign_manifest(&manifest, &[seed_byte; 32]).map_err(|error| error.to_string())?;
    println!("{signature}");
    Ok(())
}

fn decode_hex_32(raw: &str) -> Result<[u8; 32], String> {
    if raw.len() != 64 {
        return Err(format!(
            "public key must be 64 hex characters, got {}",
            raw.len()
        ));
    }
    let mut bytes = [0u8; 32];
    for (index, output) in bytes.iter_mut().enumerate() {
        *output = u8::from_str_radix(&raw[index * 2..index * 2 + 2], 16)
            .map_err(|_| "public key contains invalid hex".to_string())?;
    }
    Ok(bytes)
}

fn cmd_verify_manifest_signature(
    path: &str,
    public_key_hex: &str,
    signature: &str,
) -> Result<(), String> {
    let manifest = read_json(path)?;
    let public_key = decode_hex_32(public_key_hex)?;
    let valid = transport::verify_manifest_signature(&manifest, &public_key, signature)
        .map_err(|error| error.to_string())?;
    println!("{valid}");
    if valid {
        Ok(())
    } else {
        Err("signature verification failed".to_string())
    }
}

fn cmd_verify_ed25519(path: &str, public_key_hex: &str, signature: &str) -> Result<(), String> {
    let payload = fs::read(path).map_err(|e| format!("cannot read {path}: {e}"))?;
    let public_key = decode_hex_32(public_key_hex)?;
    let valid = transport::verify_ed25519_signature(&payload, &public_key, signature)
        .map_err(|e| e.to_string())?;
    if !valid {
        return Err("signature did not verify".to_string());
    }
    println!("true");
    Ok(())
}

fn cmd_classify_temporal(path: &str) -> Result<(), String> {
    let value: serde_json::Value = serde_json::from_str(
        &fs::read_to_string(path).map_err(|e| format!("cannot read {path}: {e}"))?,
    )
    .map_err(|e| format!("invalid temporal fixture JSON: {e}"))?;
    let timestamps = value
        .get("timestamps")
        .ok_or_else(|| "timestamps are required".to_string())?;
    let field = |name: &str| {
        timestamps
            .get(name)
            .and_then(serde_json::Value::as_str)
            .ok_or_else(|| format!("timestamps.{name} is required"))
    };
    let reference_time = value
        .get("reference_time")
        .and_then(serde_json::Value::as_str)
        .ok_or_else(|| "reference_time is required".to_string())?;
    let max_exp_days = value
        .get("max_exp_days")
        .and_then(serde_json::Value::as_u64)
        .unwrap_or(90);
    let max_exp_days =
        u32::try_from(max_exp_days).map_err(|_| "max_exp_days is too large".to_string())?;
    println!(
        "{}",
        serde_json::to_string(&classify_temporal_claims(
            field("iat")?,
            field("nbf")?,
            field("exp")?,
            reference_time,
            max_exp_days,
        ))
        .map_err(|e| e.to_string())?
    );
    Ok(())
}

fn cmd_content_policy(path: &str) -> Result<(), String> {
    let content = fs::read_to_string(path).map_err(|e| format!("cannot read {path}: {e}"))?;
    let orchestrator = Orchestrator::new(TrustConfig::default());
    println!(
        "{}",
        serde_json::json!({
            "byte_length": content.len(),
            "size_allowed": content.len() <= MAX_CONTENT_SIZE,
            "canonical_valid": transport::canonicalize_content(&content).is_ok(),
            "injection_findings": orchestrator.scan_for_injection(&content),
        })
    );
    Ok(())
}

fn personal_config(half_life_seconds: f64, baseline: u8, pinned: bool) -> DecayConfig {
    DecayConfig::exponential(half_life_seconds)
        .with_baseline(baseline)
        .with_pinned(pinned)
}

fn cmd_personal_decay(
    declared: u8,
    half_life_seconds: f64,
    baseline: u8,
    elapsed_seconds: u64,
    pinned: bool,
) -> Result<(), String> {
    use std::time::{Duration, SystemTime};
    let declared_at = SystemTime::UNIX_EPOCH;
    let now = declared_at + Duration::from_secs(elapsed_seconds);
    let config = personal_config(half_life_seconds, baseline, pinned);
    println!(
        "{}",
        compute_decayed_intensity(declared, declared_at, &config, now)
    );
    Ok(())
}

#[allow(clippy::too_many_arguments)]
fn cmd_personal_lifecycle(
    declared: u8,
    half_life_seconds: f64,
    baseline: u8,
    elapsed_seconds: u64,
    fresh_window_seconds: f64,
    stale_threshold: f64,
    pinned: bool,
) -> Result<(), String> {
    use std::time::{Duration, SystemTime};
    let declared_at = SystemTime::UNIX_EPOCH;
    let now = declared_at + Duration::from_secs(elapsed_seconds);
    let mut config = personal_config(half_life_seconds, baseline, pinned);
    config.fresh_window_seconds = fresh_window_seconds;
    config.stale_threshold = stale_threshold;
    let lifecycle = compute_lifecycle_state(declared, declared_at, &config, now);
    let effective = compute_decayed_intensity(declared, declared_at, &config, now);
    println!(
        "{}",
        serde_json::json!({
            "lifecycle_state": format!("{lifecycle:?}").to_lowercase(),
            "effective_intensity": effective,
        })
    );
    Ok(())
}

fn cmd_personal_configs() -> Result<(), String> {
    let dimensions = [
        ("perceived_urgency", PersonalDimension::PerceivedUrgency),
        ("body_signals", PersonalDimension::BodySignals),
        ("cognitive_state", PersonalDimension::CognitiveState),
        ("emotional_tone", PersonalDimension::EmotionalTone),
        ("energy_level", PersonalDimension::EnergyLevel),
    ];
    let mut output = serde_json::Map::new();
    for (name, dimension) in dimensions {
        let config = default_decay_config(dimension);
        output.insert(
            name.to_string(),
            serde_json::json!({
                "half_life_seconds": config.half_life_seconds,
                "baseline": config.baseline,
                "reset_on_engagement": config.reset_on_engagement,
            }),
        );
    }
    println!("{}", serde_json::Value::Object(output));
    Ok(())
}

fn cmd_negotiate_extensions(path: &str) -> Result<(), String> {
    let value: serde_json::Value = serde_json::from_str(
        &fs::read_to_string(path).map_err(|e| format!("cannot read {path}: {e}"))?,
    )
    .map_err(|e| format!("invalid negotiation JSON: {e}"))?;
    let client = value
        .get("client_hello")
        .ok_or_else(|| "client_hello is required".to_string())?;
    let server = value
        .get("server_capabilities")
        .ok_or_else(|| "server_capabilities is required".to_string())?;
    let client_version = client
        .get("vcp_version")
        .and_then(serde_json::Value::as_str)
        .ok_or_else(|| "client vcp_version is required".to_string())?;
    let server_version = server
        .get("vcp_version")
        .and_then(serde_json::Value::as_str)
        .ok_or_else(|| "server vcp_version is required".to_string())?;
    let client_extensions: Vec<VersionedExtension> = serde_json::from_value(
        client
            .get("extensions")
            .cloned()
            .unwrap_or_else(|| serde_json::json!([])),
    )
    .map_err(|e| format!("invalid client extensions: {e}"))?;
    let server_extensions: Vec<VersionedExtension> = serde_json::from_value(
        server
            .get("extensions")
            .cloned()
            .unwrap_or_else(|| serde_json::json!([])),
    )
    .map_err(|e| format!("invalid server extensions: {e}"))?;
    let result = negotiate_versioned(
        client_version,
        &client_extensions,
        server_version,
        &server_extensions,
    )?;
    println!(
        "{}",
        serde_json::to_string(&result).map_err(|e| e.to_string())?
    );
    Ok(())
}

fn cmd_run_consensus(path: &str) -> Result<(), String> {
    let value: serde_json::Value = serde_json::from_str(
        &fs::read_to_string(path).map_err(|e| format!("cannot read {path}: {e}"))?,
    )
    .map_err(|e| format!("invalid consensus JSON: {e}"))?;
    let candidates: Vec<String> = serde_json::from_value(
        value
            .get("candidates")
            .cloned()
            .ok_or_else(|| "candidates are required".to_string())?,
    )
    .map_err(|e| format!("invalid candidates: {e}"))?;
    let ballots: Vec<Ballot> = serde_json::from_value(
        value
            .get("ballots")
            .cloned()
            .unwrap_or_else(|| serde_json::json!([])),
    )
    .map_err(|e| format!("invalid ballots: {e}"))?;
    let mut election = SchulzeElection::new(candidates).map_err(str::to_string)?;
    for ballot in ballots {
        election.add_ballot(ballot);
    }
    println!(
        "{}",
        serde_json::to_string(&election.compute()).map_err(|e| e.to_string())?
    );
    Ok(())
}

fn cmd_run_layered_composition(path: &str) -> Result<(), String> {
    let value: serde_json::Value = serde_json::from_str(
        &fs::read_to_string(path).map_err(|e| format!("cannot read {path}: {e}"))?,
    )
    .map_err(|e| format!("invalid composition JSON: {e}"))?;
    let bundles: Vec<LayeredBundle> = serde_json::from_value(
        value
            .get("bundles")
            .cloned()
            .unwrap_or_else(|| serde_json::json!([])),
    )
    .map_err(|e| format!("invalid layered bundles: {e}"))?;
    let available: Option<Vec<String>> = value
        .get("available_constitutions")
        .filter(|candidate| !candidate.is_null())
        .cloned()
        .map(serde_json::from_value)
        .transpose()
        .map_err(|e| format!("invalid available_constitutions: {e}"))?;
    println!(
        "{}",
        serde_json::to_string(&compose_layered(&bundles, available.as_deref()))
            .map_err(|e| e.to_string())?
    );
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
