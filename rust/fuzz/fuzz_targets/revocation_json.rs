#![no_main]

use libfuzzer_sys::fuzz_target;
use vcp_core::revocation::Crl;

fuzz_target!(|data: &[u8]| {
    let Ok(raw) = std::str::from_utf8(data) else {
        return;
    };
    let _ = Crl::from_json(raw);
});
