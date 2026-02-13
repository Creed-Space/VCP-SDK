//! Context wire format: combined situational + personal encoding.
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

use serde::{Deserialize, Serialize};

use crate::error::VcpResult;
use crate::personal::PersonalState;
use crate::situational::SituationalContext;

/// The separator between the situational and personal halves of the
/// full context wire format.
pub const WIRE_SEPARATOR: char = '\u{2016}'; // double vertical line

/// Full VCP context combining situational and personal state.
#[derive(Debug, Clone, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct FullContext {
    /// Situational context (9 dimensions).
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
}
