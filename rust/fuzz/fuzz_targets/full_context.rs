#![no_main]

use libfuzzer_sys::fuzz_target;
use vcp_core::FullContext;

fuzz_target!(|data: &[u8]| {
    let Ok(raw) = std::str::from_utf8(data) else {
        return;
    };
    if let Ok(parsed) = FullContext::from_wire(raw) {
        let canonical = parsed.to_wire();
        let reparsed = FullContext::from_wire(&canonical).expect("encoder output must parse");
        assert_eq!(reparsed.to_wire(), canonical);
    }
});
