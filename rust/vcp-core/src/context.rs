//! Context wire format: combined situational + personal encoding (VCP v3.2).
//!
//! The full wire format joins the situational and personal halves with
//! a double-pipe separator (`\u{2016}`):
//!
//! ```text
//! <situational-wire>\u{2016}<personal-wire>
//! ```
//!
//! For example:
//! ```text
//! \u{23F0}\u{1F305}|\u{1F4CD}\u{1F3E1}\u{2016}\u{1F9E0}focused:4|\u{1F4AD}calm:3
//! ```
//!
//! ## Conformance levels (VCP v3.2)
//!
//! | level          | shape                                                 |
//! |----------------|-------------------------------------------------------|
//! | VCP-Minimal    | situational only, core 9 dims (positions 1-9)         |
//! | VCP-Standard   | Minimal + any personal-state dim                      |
//! | VCP-Extended   | Standard (or Minimal) + any VEP-0004 dim (pos 10-13)  |

use serde::{Deserialize, Serialize};

use crate::error::VcpResult;
use crate::personal::PersonalState;
use crate::situational::SituationalContext;

/// VCP v3.2 conformance classification for a [`FullContext`].
///
/// Serializes as the canonical labels `VCP-Minimal`, `VCP-Standard`,
/// or `VCP-Extended` — matching the schema at
/// `schemas/vcp-adaptation-context.schema.json`.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum ConformanceLevel {
    /// Situational only, core 9 dims (positions 1-9). No personal,
    /// no VEP-0004.
    #[serde(rename = "VCP-Minimal")]
    Minimal,
    /// Core 9 situational + at least one personal-state dim.
    #[serde(rename = "VCP-Standard")]
    Standard,
    /// Any VEP-0004 dimension present (positions 10-13). Takes
    /// precedence over Standard.
    #[serde(rename = "VCP-Extended")]
    Extended,
}

impl ConformanceLevel {
    /// Canonical kebab-case label: `VCP-Minimal` / `VCP-Standard` / `VCP-Extended`.
    pub fn label(self) -> &'static str {
        match self {
            Self::Minimal => "VCP-Minimal",
            Self::Standard => "VCP-Standard",
            Self::Extended => "VCP-Extended",
        }
    }
}

/// The separator between the situational and personal halves of the
/// full context wire format.
pub const WIRE_SEPARATOR: char = '\u{2016}'; // double vertical line

/// Full VCP context combining situational and personal state (VCP v3.2).
///
/// Situational carries 13 dimensions (9 core + 4 VEP-0004).
/// Personal carries 5 dimensions.
#[derive(Debug, Clone, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct FullContext {
    /// Situational context (13 dimensions, VCP v3.2).
    pub situational: SituationalContext,
    /// Personal state (5 dimensions).
    pub personal: PersonalState,
}

impl FullContext {
    /// Create from its parts.
    pub fn new(situational: SituationalContext, personal: PersonalState) -> Self {
        Self {
            situational,
            personal,
        }
    }

    /// Returns `true` if either half has data.
    pub fn has_any(&self) -> bool {
        self.situational.has_any() || self.personal.has_any()
    }

    /// Classify this context against the VCP v3.2 conformance levels.
    ///
    /// Extended (any VEP-0004 dim) wins over Standard. A context with no
    /// personal data and no VEP-0004 dims is classified as Minimal — even
    /// if it is empty.
    pub fn conformance_level(&self) -> ConformanceLevel {
        if self.situational.has_vep_0004() {
            ConformanceLevel::Extended
        } else if self.personal.has_any() {
            ConformanceLevel::Standard
        } else {
            ConformanceLevel::Minimal
        }
    }

    /// Encode to the full wire format.
    ///
    /// If only one half has data, the separator is still included
    /// to make the format unambiguous. If neither has data,
    /// returns an empty string.
    pub fn to_wire(&self) -> String {
        let sit = self.situational.to_wire();
        let per = self.personal.to_wire();

        if sit.is_empty() && per.is_empty() {
            return String::new();
        }

        if per.is_empty() {
            return sit;
        }

        if sit.is_empty() {
            return format!("{WIRE_SEPARATOR}{per}");
        }

        format!("{sit}{WIRE_SEPARATOR}{per}")
    }

    /// Parse from the full wire format.
    ///
    /// # Errors
    ///
    /// Returns [`VcpError::ParseError`] if the situational or personal
    /// portion of the wire format is malformed.
    pub fn from_wire(wire: &str) -> VcpResult<Self> {
        if wire.is_empty() {
            return Ok(Self::default());
        }

        if let Some(sep_idx) = wire.find(WIRE_SEPARATOR) {
            let sit_part = &wire[..sep_idx];
            let per_part = &wire[sep_idx + WIRE_SEPARATOR.len_utf8()..];

            let situational = SituationalContext::from_wire(sit_part)?;
            let personal = PersonalState::from_wire(per_part)?;

            Ok(Self {
                situational,
                personal,
            })
        } else {
            // No separator -- treat the entire string as situational only.
            let situational = SituationalContext::from_wire(wire)?;
            Ok(Self {
                situational,
                personal: PersonalState::default(),
            })
        }
    }
}

impl std::fmt::Display for FullContext {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.write_str(&self.to_wire())
    }
}

// ── Tests ───────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;
    use crate::personal::PersonalDimension;

    #[test]
    fn empty_context() {
        let ctx = FullContext::default();
        assert!(!ctx.has_any());
        assert_eq!(ctx.to_wire(), "");
    }

    #[test]
    fn situational_only() {
        let mut ctx = FullContext::default();
        ctx.situational.time = Some(vec!["\u{1F305}".to_string()]);

        let wire = ctx.to_wire();
        assert!(!wire.contains(WIRE_SEPARATOR));
        assert!(wire.contains("\u{23F0}"));

        let parsed = FullContext::from_wire(&wire).unwrap();
        assert!(parsed.situational.time.is_some());
        assert!(!parsed.personal.has_any());
    }

    #[test]
    fn personal_only() {
        let mut ctx = FullContext::default();
        ctx.personal.cognitive = Some(PersonalDimension::new("focused", 4).unwrap());

        let wire = ctx.to_wire();
        assert!(wire.starts_with(WIRE_SEPARATOR));

        let parsed = FullContext::from_wire(&wire).unwrap();
        assert!(!parsed.situational.has_any());
        assert_eq!(parsed.personal.cognitive.as_ref().unwrap().value, "focused");
    }

    #[test]
    fn full_roundtrip() {
        let mut ctx = FullContext::default();
        ctx.situational.time = Some(vec!["\u{1F305}".to_string()]);
        ctx.situational.space = Some(vec!["\u{1F3E1}".to_string()]);
        ctx.personal.cognitive = Some(PersonalDimension::new("focused", 4).unwrap());
        ctx.personal.emotional = Some(PersonalDimension::new("calm", 3).unwrap());

        let wire = ctx.to_wire();
        assert!(wire.contains(WIRE_SEPARATOR));

        let parsed = FullContext::from_wire(&wire).unwrap();
        assert!(parsed.situational.time.is_some());
        assert!(parsed.situational.space.is_some());
        assert_eq!(parsed.personal.cognitive.as_ref().unwrap().value, "focused");
        assert_eq!(parsed.personal.emotional.as_ref().unwrap().value, "calm");
    }

    #[test]
    fn from_wire_empty() {
        let ctx = FullContext::from_wire("").unwrap();
        assert!(!ctx.has_any());
    }

    #[test]
    fn serde_roundtrip() {
        let mut ctx = FullContext::default();
        ctx.situational.company = Some(vec!["team".to_string()]);
        ctx.personal.urgency = Some(PersonalDimension::new("pressured", 4).unwrap());

        let json = serde_json::to_string(&ctx).unwrap();
        let parsed: FullContext = serde_json::from_str(&json).unwrap();
        assert_eq!(ctx, parsed);
    }

    // ── VEP-0004 / v3.2 ─────────────────────────────────────

    #[test]
    fn full_eighteen_dim_roundtrip() {
        let mut ctx = FullContext::default();
        // Situational core
        ctx.situational.time = Some(vec!["\u{1F305}".to_string()]);
        ctx.situational.space = Some(vec!["\u{1F3E2}".to_string()]);
        ctx.situational.company = Some(vec!["\u{1F454}".to_string()]);
        ctx.situational.occasion = Some(vec!["\u{1F4BC}".to_string()]);
        // VEP-0004
        ctx.situational.embodiment = Some(vec!["\u{270B}".to_string()]);
        ctx.situational.proximity = Some(vec!["\u{1F90F}".to_string()]);
        ctx.situational.relationship = Some(vec!["colleague:professional".to_string()]);
        ctx.situational.formality = Some(vec!["\u{1F4BC}".to_string()]);
        // Personal
        ctx.personal.cognitive = Some(PersonalDimension::new("focused", 4).unwrap());
        ctx.personal.emotional = Some(PersonalDimension::new("calm", 5).unwrap());

        let wire = ctx.to_wire();
        assert!(wire.contains(WIRE_SEPARATOR));
        assert!(wire.contains("\u{1FAA2}colleague:professional"));

        let parsed = FullContext::from_wire(&wire).unwrap();
        assert_eq!(
            parsed.situational.relationship.as_deref(),
            Some(&["colleague:professional".to_string()][..])
        );
        assert_eq!(parsed.personal.cognitive.as_ref().unwrap().value, "focused");
        assert_eq!(parsed.personal.emotional.as_ref().unwrap().intensity, 5);
    }

    #[test]
    fn conformance_minimal_empty() {
        let ctx = FullContext::default();
        assert_eq!(ctx.conformance_level(), ConformanceLevel::Minimal);
        assert_eq!(ctx.conformance_level().label(), "VCP-Minimal");
    }

    #[test]
    fn conformance_minimal_core_only() {
        let mut ctx = FullContext::default();
        ctx.situational.time = Some(vec!["\u{1F305}".to_string()]);
        assert_eq!(ctx.conformance_level(), ConformanceLevel::Minimal);
    }

    #[test]
    fn conformance_standard_with_personal() {
        let mut ctx = FullContext::default();
        ctx.situational.time = Some(vec!["\u{1F305}".to_string()]);
        ctx.personal.cognitive = Some(PersonalDimension::new("focused", 4).unwrap());
        assert_eq!(ctx.conformance_level(), ConformanceLevel::Standard);
    }

    #[test]
    fn conformance_extended_with_vep_0004() {
        let mut ctx = FullContext::default();
        ctx.situational.embodiment = Some(vec!["\u{270B}".to_string()]);
        assert_eq!(ctx.conformance_level(), ConformanceLevel::Extended);
    }

    #[test]
    fn conformance_extended_wins_over_standard() {
        let mut ctx = FullContext::default();
        ctx.situational.formality = Some(vec!["\u{1F4BC}".to_string()]);
        ctx.personal.cognitive = Some(PersonalDimension::new("focused", 4).unwrap());
        assert_eq!(ctx.conformance_level(), ConformanceLevel::Extended);
    }
}
