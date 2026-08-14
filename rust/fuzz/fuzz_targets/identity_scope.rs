#![no_main]

use libfuzzer_sys::fuzz_target;
use vcp_core::VcpToken;

fuzz_target!(|data: &[u8]| {
    let Some(separator) = data.iter().position(|byte| *byte == 0) else {
        return;
    };
    let Ok(token_text) = std::str::from_utf8(&data[..separator]) else {
        return;
    };
    let Ok(pattern) = std::str::from_utf8(&data[separator + 1..]) else {
        return;
    };
    if let Ok(token) = VcpToken::parse(token_text) {
        let _ = token.matches_pattern(pattern);
        assert!(token.matches_pattern(&token.segments.join(".")));
    }
});
