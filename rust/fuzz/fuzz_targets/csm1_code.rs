#![no_main]

use libfuzzer_sys::fuzz_target;
use vcp_core::Csm1Code;

fuzz_target!(|data: &[u8]| {
    let Ok(raw) = std::str::from_utf8(data) else {
        return;
    };
    if let Ok(parsed) = Csm1Code::parse(raw) {
        let canonical = parsed.encode();
        let reparsed = Csm1Code::parse(&canonical).expect("encoder output must parse");
        assert_eq!(reparsed.encode(), canonical);
    }
});
