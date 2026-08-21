use std::net::{IpAddr, Ipv4Addr};

use proptest::prelude::*;
use vcp_core::csm1::{Csm1Code, Persona, Scope};
use vcp_core::revocation::{is_private_ip, validate_uri, Crl};
use vcp_core::{FullContext, VcpToken};

const SCOPES: [Scope; 11] = [
    Scope::Family,
    Scope::Work,
    Scope::Privacy,
    Scope::Education,
    Scope::Technical,
    Scope::Official,
    Scope::Vulnerable,
    Scope::Adult,
    Scope::Healthcare,
    Scope::Social,
    Scope::Religious,
];

fn persona(index: usize) -> Persona {
    [
        Persona::Nanny,
        Persona::Sentinel,
        Persona::Godparent,
        Persona::Ambassador,
        Persona::Muse,
        Persona::Mediator,
        Persona::Custom,
    ][index]
}

proptest! {
    #![proptest_config(ProptestConfig {
        cases: 512,
        failure_persistence: None,
        .. ProptestConfig::default()
    })]

    #[test]
    fn csm1_encode_parse_is_canonical(
        persona_index in 0usize..7,
        level in 0u8..=5,
        scope_mask in 0u16..(1u16 << SCOPES.len()),
        namespace in "[A-Z]{1,8}",
        version in prop_oneof![
            Just("latest".to_string()),
            Just("canary".to_string()),
            (0u16..=999, 0u16..=999, 0u16..=999)
                .prop_map(|(major, minor, patch)| format!("{major}.{minor}.{patch}")),
        ],
    ) {
        let selected: Vec<_> = SCOPES
            .iter()
            .enumerate()
            .filter(|(index, _)| scope_mask & (1 << index) != 0)
            .map(|(_, scope)| *scope)
            .collect();
        prop_assume!(!(selected.contains(&Scope::Adult)
            && (selected.contains(&Scope::Family)
                || selected.contains(&Scope::Vulnerable)
                || selected.contains(&Scope::Healthcare))));
        let selected_persona = persona(persona_index);
        let code = Csm1Code {
            persona: selected_persona,
            adherence_level: level,
            scopes: selected,
            namespace: (selected_persona == Persona::Custom).then_some(namespace),
            version: Some(version),
        };
        let encoded = code.encode();
        let parsed = Csm1Code::parse(&encoded).unwrap();
        prop_assert_eq!(parsed.encode(), encoded);
    }

    #[test]
    fn parsers_do_not_panic_on_arbitrary_text(raw in ".{0,256}") {
        let _ = Csm1Code::parse(&raw);
        let _ = VcpToken::parse(&raw);
        let _ = VcpToken::from_uri(&raw);
        let _ = FullContext::from_wire(&raw);
        let _ = Crl::from_json(&raw);
        let _ = validate_uri(&raw);
    }

    #[test]
    fn generated_private_ipv4_ranges_are_always_rejected(
        second in any::<u8>(),
        third in any::<u8>(),
        fourth in any::<u8>(),
        family in 0u8..4,
    ) {
        let address = match family {
            0 => Ipv4Addr::new(10, second, third, fourth),
            1 => Ipv4Addr::new(127, second, third, fourth),
            2 => Ipv4Addr::new(172, 16 + second % 16, third, fourth),
            _ => Ipv4Addr::new(192, 168, third, fourth),
        };
        prop_assert!(is_private_ip(IpAddr::V4(address)));
    }

    #[test]
    fn token_scope_globs_match_generated_authorized_paths(
        segments in prop::collection::vec("[a-z][a-z0-9]{0,11}", 3..=8),
        wildcard_mask in prop::collection::vec(any::<bool>(), 8),
    ) {
        let canonical = segments.join(".");
        let token = VcpToken::parse(&canonical).unwrap();
        let pattern = segments
            .iter()
            .enumerate()
            .map(|(index, segment)| if wildcard_mask[index] { "*" } else { segment })
            .collect::<Vec<_>>()
            .join(".");
        prop_assert!(token.matches_pattern(&pattern));
        prop_assert!(token.matches_pattern("**"));
        let prefix_pattern = format!("{}.**", segments[0]);
        prop_assert!(token.matches_pattern(&prefix_pattern));
        prop_assert!(!token.matches_pattern("definitely-different.**"));
    }
}
