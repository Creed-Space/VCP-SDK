//! # vcp-wasm
//!
//! WebAssembly bindings for the VCP SDK, exposing core parsing
//! and encoding functions to JavaScript/TypeScript via `wasm-bindgen`.
//!
//! ## Usage from JS
//!
//! ```js
//! import init, { parse_csm1, encode_csm1, parse_context_wire, validate_token } from 'vcp-wasm';
//!
//! await init();
//!
//! const code = parse_csm1("N5+F+E");
//! console.log(code.persona); // "Nanny"
//!
//! const wire = parse_context_wire("⏰🌅|📍🏡‖🧠focused:4|💭calm:3");
//! console.log(wire.personal.cognitive.value); // "focused"
//! ```

use wasm_bindgen::prelude::*;

use vcp_core::context::FullContext;
use vcp_core::csm1::{Csm1Code, Csm1Token};
use vcp_core::identity::VcpToken;
use vcp_core::transport;

/// Parse a CSM-1 compact code (e.g. `"N5+F+E"`) and return it as a JS object.
#[wasm_bindgen]
pub fn parse_csm1(code: &str) -> Result<JsValue, JsValue> {
    let parsed = Csm1Code::parse(code).map_err(|e| JsValue::from_str(&e.to_string()))?;
    serde_wasm_bindgen::to_value(&parsed).map_err(|e| JsValue::from_str(&e.to_string()))
}

/// Encode a CSM-1 compact code from a JS object back to a string.
///
/// Accepts the same shape returned by `parse_csm1`.
#[wasm_bindgen]
pub fn encode_csm1(obj: JsValue) -> Result<String, JsValue> {
    let code: Csm1Code =
        serde_wasm_bindgen::from_value(obj).map_err(|e| JsValue::from_str(&e.to_string()))?;
    Ok(code.encode())
}

/// Parse a CSM-1 8-line token string and return it as a JS object.
#[wasm_bindgen]
pub fn parse_csm1_token(token: &str) -> Result<JsValue, JsValue> {
    let parsed = Csm1Token::parse(token).map_err(|e| JsValue::from_str(&e.to_string()))?;
    serde_wasm_bindgen::to_value(&parsed).map_err(|e| JsValue::from_str(&e.to_string()))
}

/// Encode a CSM-1 8-line token from a JS object back to a string.
#[wasm_bindgen]
pub fn encode_csm1_token(obj: JsValue) -> Result<String, JsValue> {
    let token: Csm1Token =
        serde_wasm_bindgen::from_value(obj).map_err(|e| JsValue::from_str(&e.to_string()))?;
    Ok(token.encode())
}

/// Parse the full context wire format (situational + personal, separated by `‖`).
///
/// Returns a JS object with `situational` and `personal` fields.
#[wasm_bindgen]
pub fn parse_context_wire(wire: &str) -> Result<JsValue, JsValue> {
    let parsed = FullContext::from_wire(wire).map_err(|e| JsValue::from_str(&e.to_string()))?;
    serde_wasm_bindgen::to_value(&parsed).map_err(|e| JsValue::from_str(&e.to_string()))
}

/// Encode a full context object to wire format.
#[wasm_bindgen]
pub fn encode_context_wire(obj: JsValue) -> Result<String, JsValue> {
    let ctx: FullContext =
        serde_wasm_bindgen::from_value(obj).map_err(|e| JsValue::from_str(&e.to_string()))?;
    Ok(ctx.to_wire())
}

/// Validate a VCP/I identity token (e.g. `"family.safe.guide@1.2.0"`).
///
/// Returns the parsed token as a JS object on success.
#[wasm_bindgen]
pub fn validate_token(token: &str) -> Result<JsValue, JsValue> {
    let parsed = VcpToken::parse(token).map_err(|e| JsValue::from_str(&e.to_string()))?;
    serde_wasm_bindgen::to_value(&parsed).map_err(|e| JsValue::from_str(&e.to_string()))
}

/// Compute the SHA-256 content hash of constitution text.
///
/// Returns a string in the format `"sha256:<hex>"`.
#[wasm_bindgen]
pub fn hash_content(content: &str) -> Result<String, JsValue> {
    transport::compute_content_hash(content).map_err(|e| JsValue::from_str(&e.to_string()))
}

/// Verify that content matches an expected hash.
///
/// Returns `true` if the hash matches.
#[wasm_bindgen]
pub fn verify_hash(content: &str, expected_hash: &str) -> Result<bool, JsValue> {
    transport::verify_content_hash(content, expected_hash)
        .map_err(|e| JsValue::from_str(&e.to_string()))
}

/// Verify a bundle (manifest JSON + content).
///
/// Returns a JS object with `code` and `message` fields.
#[wasm_bindgen]
pub fn verify_bundle(manifest_json: &str, content: &str) -> Result<JsValue, JsValue> {
    let result = transport::verify_bundle(manifest_json, content)
        .map_err(|e| JsValue::from_str(&e.to_string()))?;
    serde_wasm_bindgen::to_value(&result).map_err(|e| JsValue::from_str(&e.to_string()))
}
