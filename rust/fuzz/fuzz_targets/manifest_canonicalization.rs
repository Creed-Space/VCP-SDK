#![no_main]

use libfuzzer_sys::fuzz_target;
use vcp_core::transport::canonicalize_manifest;

fuzz_target!(|data: &[u8]| {
    let Ok(value) = serde_json::from_slice(data) else {
        return;
    };
    if let Ok(first) = canonicalize_manifest(&value) {
        let reparsed: serde_json::Value =
            serde_json::from_slice(&first).expect("canonical output must be JSON");
        let second = canonicalize_manifest(&reparsed).expect("canonical output must remain valid");
        assert_eq!(first, second);
    }
});
