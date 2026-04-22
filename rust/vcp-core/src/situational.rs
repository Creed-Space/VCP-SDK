//! Situational context dimensions (VCP v3.2 Layer 2).
//!
//! Thirteen categorical dimensions describe the user's current situation
//! using emoji-keyed tag arrays in a compact wire format.
//!
//! **VCP v3.2 (incl. VEP-0004) dimension map**
//!
//! | # | dim            | symbol     | notes                              |
//! |---|----------------|------------|------------------------------------|
//! | 1 | time           | ⏰          |                                    |
//! | 2 | space          | 📍          |                                    |
//! | 3 | company        | 👥          |                                    |
//! | 4 | culture        | 🌍          | communication styles, NOT nations |
//! | 5 | occasion       | 🎭          |                                    |
//! | 6 | environment    | 🌡️ (VS16)  |                                    |
//! | 7 | agency         | 🔷          |                                    |
//! | 8 | constraints    | 🔶          |                                    |
//! | 9 | `system_context` | 📡          | replaces deprecated STATE (v3.0)   |
//! |10 | embodiment     | 🧍          | VEP-0004                           |
//! |11 | proximity      | ↔️ (VS16)  | VEP-0004                           |
//! |12 | relationship   | 🪢          | VEP-0004, free-form `{tie}:{fn}`  |
//! |13 | formality      | 🎩          | VEP-0004                           |
//!
//! Wire format example (core-only):
//! `⏰🌅|📍🏡|👥👶`
//!
//! Wire format example (full 13-dim + VEP-0004):
//! `⏰🌅|📍🏢|👥👔|🎭💼|🧍✋|↔️🤏|🪢colleague:professional|🎩💼`

use std::fmt;

use serde::{Deserialize, Serialize};

use crate::error::{VcpError, VcpResult};

/// The thirteen situational context dimensions (VCP v3.2, incl. VEP-0004).
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum SituationalDimension {
    Time,
    Space,
    Company,
    Culture,
    Occasion,
    Environment,
    Agency,
    Constraints,
    SystemContext,
    // VEP-0004 dimensions (positions 10-13)
    Embodiment,
    Proximity,
    Relationship,
    Formality,
}

impl SituationalDimension {
    /// Emoji symbol used as the wire-format prefix.
    pub fn symbol(self) -> &'static str {
        match self {
            Self::Time => "\u{23F0}",                 // ⏰ alarm clock
            Self::Space => "\u{1F4CD}",               // 📍 round pushpin
            Self::Company => "\u{1F465}",             // 👥 busts in silhouette
            Self::Culture => "\u{1F30D}",             // 🌍 globe Europe-Africa
            Self::Occasion => "\u{1F3AD}",            // 🎭 performing arts
            Self::Environment => "\u{1F321}\u{FE0F}", // 🌡️ thermometer (+ VS16)
            Self::Agency => "\u{1F537}",              // 🔷 large blue diamond
            Self::Constraints => "\u{1F536}",         // 🔶 large orange diamond
            Self::SystemContext => "\u{1F4E1}",       // 📡 satellite antenna
            // VEP-0004
            Self::Embodiment => "\u{1F9CD}", // 🧍 standing person
            Self::Proximity => "\u{2194}\u{FE0F}", // ↔️ left-right arrow (+ VS16)
            Self::Relationship => "\u{1FAA2}", // 🪢 knot
            Self::Formality => "\u{1F3A9}",  // 🎩 top hat
        }
    }

    /// Canonical position (1-13) of this dimension in the wire format.
    pub fn position(self) -> u8 {
        match self {
            Self::Time => 1,
            Self::Space => 2,
            Self::Company => 3,
            Self::Culture => 4,
            Self::Occasion => 5,
            Self::Environment => 6,
            Self::Agency => 7,
            Self::Constraints => 8,
            Self::SystemContext => 9,
            Self::Embodiment => 10,
            Self::Proximity => 11,
            Self::Relationship => 12,
            Self::Formality => 13,
        }
    }

    /// `true` if this dimension was introduced by VEP-0004 (positions 10-13).
    pub fn is_vep_0004(self) -> bool {
        matches!(
            self,
            Self::Embodiment | Self::Proximity | Self::Relationship | Self::Formality
        )
    }

    /// `true` if this dimension carries free-form string values
    /// rather than an emoji tag vocabulary.
    ///
    /// Currently only [`Self::Relationship`] is free-form: its value
    /// is a compound string of form `{tie}:{function}`
    /// (e.g. `colleague:professional`).
    pub fn is_free_form(self) -> bool {
        matches!(self, Self::Relationship)
    }

    /// Parse from the emoji symbol prefix.
    pub fn from_symbol(s: &str) -> Option<Self> {
        // Multi-codepoint symbols first.
        if s == "\u{1F321}\u{FE0F}" || s.starts_with("\u{1F321}\u{FE0F}") {
            return Some(Self::Environment);
        }
        if s == "\u{1F321}" || s.starts_with("\u{1F321}") {
            // bare thermometer without VS16
            return Some(Self::Environment);
        }
        if s == "\u{2194}\u{FE0F}" || s.starts_with("\u{2194}\u{FE0F}") {
            return Some(Self::Proximity);
        }
        if s == "\u{2194}" || s.starts_with("\u{2194}") {
            // bare arrow without VS16
            return Some(Self::Proximity);
        }
        match s {
            "\u{23F0}" => Some(Self::Time),
            "\u{1F4CD}" => Some(Self::Space),
            "\u{1F465}" => Some(Self::Company),
            "\u{1F30D}" => Some(Self::Culture),
            "\u{1F3AD}" => Some(Self::Occasion),
            "\u{1F537}" => Some(Self::Agency),
            "\u{1F536}" => Some(Self::Constraints),
            "\u{1F4E1}" => Some(Self::SystemContext),
            "\u{1F9CD}" => Some(Self::Embodiment),
            "\u{1FAA2}" => Some(Self::Relationship),
            "\u{1F3A9}" => Some(Self::Formality),
            _ => None,
        }
    }

    /// All thirteen dimensions in canonical position order (1..=13).
    pub fn all() -> &'static [SituationalDimension] {
        &[
            Self::Time,
            Self::Space,
            Self::Company,
            Self::Culture,
            Self::Occasion,
            Self::Environment,
            Self::Agency,
            Self::Constraints,
            Self::SystemContext,
            Self::Embodiment,
            Self::Proximity,
            Self::Relationship,
            Self::Formality,
        ]
    }
}

impl fmt::Display for SituationalDimension {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let label = match self {
            Self::Time => "time",
            Self::Space => "space",
            Self::Company => "company",
            Self::Culture => "culture",
            Self::Occasion => "occasion",
            Self::Environment => "environment",
            Self::Agency => "agency",
            Self::Constraints => "constraints",
            Self::SystemContext => "system_context",
            Self::Embodiment => "embodiment",
            Self::Proximity => "proximity",
            Self::Relationship => "relationship",
            Self::Formality => "formality",
        };
        f.write_str(label)
    }
}

/// The complete set of situational context tags (VCP v3.2, 13 dims).
///
/// Each dimension maps to an optional list of tag strings.
/// For the standard dimensions, tags are emoji values from the
/// dimension's vocabulary. For [`SituationalDimension::Relationship`],
/// tags are free-form compound strings of form `{tie}:{function}`.
#[derive(Debug, Clone, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct SituationalContext {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub time: Option<Vec<String>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub space: Option<Vec<String>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub company: Option<Vec<String>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub culture: Option<Vec<String>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub occasion: Option<Vec<String>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub environment: Option<Vec<String>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub agency: Option<Vec<String>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub constraints: Option<Vec<String>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub system_context: Option<Vec<String>>,
    // VEP-0004 dims
    #[serde(skip_serializing_if = "Option::is_none")]
    pub embodiment: Option<Vec<String>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub proximity: Option<Vec<String>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub relationship: Option<Vec<String>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub formality: Option<Vec<String>>,
}

impl SituationalContext {
    /// Returns `true` if at least one dimension has tags.
    pub fn has_any(&self) -> bool {
        self.time.is_some()
            || self.space.is_some()
            || self.company.is_some()
            || self.culture.is_some()
            || self.occasion.is_some()
            || self.environment.is_some()
            || self.agency.is_some()
            || self.constraints.is_some()
            || self.system_context.is_some()
            || self.embodiment.is_some()
            || self.proximity.is_some()
            || self.relationship.is_some()
            || self.formality.is_some()
    }

    /// Returns `true` if any VEP-0004 dimension (positions 10-13) has tags.
    pub fn has_vep_0004(&self) -> bool {
        self.embodiment.is_some()
            || self.proximity.is_some()
            || self.relationship.is_some()
            || self.formality.is_some()
    }

    /// Encode to wire format.
    ///
    /// Each dimension is encoded as `<symbol><tag1><tag2>...` and
    /// dimensions are separated by `|`. Dimensions are emitted in
    /// canonical position order (1..=13).
    pub fn to_wire(&self) -> String {
        let mut parts = Vec::new();

        let dims: [(SituationalDimension, &Option<Vec<String>>); 13] = [
            (SituationalDimension::Time, &self.time),
            (SituationalDimension::Space, &self.space),
            (SituationalDimension::Company, &self.company),
            (SituationalDimension::Culture, &self.culture),
            (SituationalDimension::Occasion, &self.occasion),
            (SituationalDimension::Environment, &self.environment),
            (SituationalDimension::Agency, &self.agency),
            (SituationalDimension::Constraints, &self.constraints),
            (SituationalDimension::SystemContext, &self.system_context),
            (SituationalDimension::Embodiment, &self.embodiment),
            (SituationalDimension::Proximity, &self.proximity),
            (SituationalDimension::Relationship, &self.relationship),
            (SituationalDimension::Formality, &self.formality),
        ];

        for (dim, tags_opt) in &dims {
            if let Some(tags) = tags_opt {
                if !tags.is_empty() {
                    let mut s = String::from(dim.symbol());
                    for tag in tags {
                        s.push_str(tag);
                    }
                    parts.push(s);
                }
            }
        }

        parts.join("|")
    }

    /// Parse from wire format.
    ///
    /// The wire format is `<symbol><tags>|<symbol><tags>|...`.
    ///
    /// # Errors
    ///
    /// Returns [`VcpError::ParseError`] if a segment contains an
    /// unrecognised dimension symbol.
    pub fn from_wire(wire: &str) -> VcpResult<Self> {
        let mut ctx = SituationalContext::default();

        if wire.is_empty() {
            return Ok(ctx);
        }

        for segment in wire.split('|') {
            let segment = segment.trim();
            if segment.is_empty() {
                continue;
            }

            let (dim, rest) = split_situational_symbol(segment)?;
            let tags = if rest.is_empty() {
                Vec::new()
            } else {
                // Tags are the remaining content. Relationship values
                // are free-form `{tie}:{function}` strings and must
                // be kept intact. Other dimensions' remainders are
                // treated as a single opaque tag.
                vec![rest.to_string()]
            };

            match dim {
                SituationalDimension::Time => ctx.time = Some(tags),
                SituationalDimension::Space => ctx.space = Some(tags),
                SituationalDimension::Company => ctx.company = Some(tags),
                SituationalDimension::Culture => ctx.culture = Some(tags),
                SituationalDimension::Occasion => ctx.occasion = Some(tags),
                SituationalDimension::Environment => ctx.environment = Some(tags),
                SituationalDimension::Agency => ctx.agency = Some(tags),
                SituationalDimension::Constraints => ctx.constraints = Some(tags),
                SituationalDimension::SystemContext => ctx.system_context = Some(tags),
                SituationalDimension::Embodiment => ctx.embodiment = Some(tags),
                SituationalDimension::Proximity => ctx.proximity = Some(tags),
                SituationalDimension::Relationship => ctx.relationship = Some(tags),
                SituationalDimension::Formality => ctx.formality = Some(tags),
            }
        }

        Ok(ctx)
    }

    /// Get tags for a specific dimension.
    pub fn get(&self, dim: SituationalDimension) -> Option<&Vec<String>> {
        match dim {
            SituationalDimension::Time => self.time.as_ref(),
            SituationalDimension::Space => self.space.as_ref(),
            SituationalDimension::Company => self.company.as_ref(),
            SituationalDimension::Culture => self.culture.as_ref(),
            SituationalDimension::Occasion => self.occasion.as_ref(),
            SituationalDimension::Environment => self.environment.as_ref(),
            SituationalDimension::Agency => self.agency.as_ref(),
            SituationalDimension::Constraints => self.constraints.as_ref(),
            SituationalDimension::SystemContext => self.system_context.as_ref(),
            SituationalDimension::Embodiment => self.embodiment.as_ref(),
            SituationalDimension::Proximity => self.proximity.as_ref(),
            SituationalDimension::Relationship => self.relationship.as_ref(),
            SituationalDimension::Formality => self.formality.as_ref(),
        }
    }

    /// Set tags for a specific dimension.
    pub fn set(&mut self, dim: SituationalDimension, tags: Vec<String>) {
        match dim {
            SituationalDimension::Time => self.time = Some(tags),
            SituationalDimension::Space => self.space = Some(tags),
            SituationalDimension::Company => self.company = Some(tags),
            SituationalDimension::Culture => self.culture = Some(tags),
            SituationalDimension::Occasion => self.occasion = Some(tags),
            SituationalDimension::Environment => self.environment = Some(tags),
            SituationalDimension::Agency => self.agency = Some(tags),
            SituationalDimension::Constraints => self.constraints = Some(tags),
            SituationalDimension::SystemContext => self.system_context = Some(tags),
            SituationalDimension::Embodiment => self.embodiment = Some(tags),
            SituationalDimension::Proximity => self.proximity = Some(tags),
            SituationalDimension::Relationship => self.relationship = Some(tags),
            SituationalDimension::Formality => self.formality = Some(tags),
        }
    }
}

impl fmt::Display for SituationalContext {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(&self.to_wire())
    }
}

/// Split the leading dimension symbol from a wire-format segment.
///
/// Environment uses a two-codepoint emoji (`🌡️` = U+1F321 U+FE0F), and
/// Proximity uses a two-codepoint emoji (`↔️` = U+2194 U+FE0F), so
/// these must be checked before their single-codepoint base forms.
fn split_situational_symbol(s: &str) -> VcpResult<(SituationalDimension, &str)> {
    static SYMBOLS: &[(SituationalDimension, &str)] = &[
        (SituationalDimension::Space, "\u{1F4CD}"),
        (SituationalDimension::Company, "\u{1F465}"),
        (SituationalDimension::Culture, "\u{1F30D}"),
        (SituationalDimension::Occasion, "\u{1F3AD}"),
        (SituationalDimension::Agency, "\u{1F537}"),
        (SituationalDimension::Constraints, "\u{1F536}"),
        (SituationalDimension::SystemContext, "\u{1F4E1}"),
        (SituationalDimension::Embodiment, "\u{1F9CD}"),
        (SituationalDimension::Relationship, "\u{1FAA2}"),
        (SituationalDimension::Formality, "\u{1F3A9}"),
        (SituationalDimension::Time, "\u{23F0}"),
    ];

    // Two-codepoint (VS16) symbols — check first.
    let env_sym = "\u{1F321}\u{FE0F}";
    if let Some(rest) = s.strip_prefix(env_sym) {
        return Ok((SituationalDimension::Environment, rest));
    }
    let prox_sym = "\u{2194}\u{FE0F}";
    if let Some(rest) = s.strip_prefix(prox_sym) {
        return Ok((SituationalDimension::Proximity, rest));
    }
    // Also accept bare (no-VS16) variants.
    let env_bare = "\u{1F321}";
    if let Some(rest) = s.strip_prefix(env_bare) {
        return Ok((SituationalDimension::Environment, rest));
    }
    let prox_bare = "\u{2194}";
    if let Some(rest) = s.strip_prefix(prox_bare) {
        return Ok((SituationalDimension::Proximity, rest));
    }

    for (dim, sym) in SYMBOLS {
        if let Some(rest) = s.strip_prefix(sym) {
            return Ok((*dim, rest));
        }
    }

    Err(VcpError::ParseError(format!(
        "unrecognised situational dimension symbol in: {s}"
    )))
}

// ── Tests ───────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;
    use pretty_assertions::assert_eq;

    #[test]
    fn dimension_symbols_roundtrip() {
        for dim in SituationalDimension::all() {
            let sym = dim.symbol();
            assert_eq!(
                SituationalDimension::from_symbol(sym),
                Some(*dim),
                "symbol roundtrip failed for {dim}"
            );
        }
    }

    #[test]
    fn thirteen_dimensions_unique_positions() {
        let mut positions: Vec<u8> = SituationalDimension::all()
            .iter()
            .map(|d| d.position())
            .collect();
        positions.sort_unstable();
        assert_eq!(positions, (1u8..=13).collect::<Vec<_>>());
    }

    #[test]
    fn vep_0004_flags() {
        for dim in SituationalDimension::all() {
            let expected = matches!(
                dim,
                SituationalDimension::Embodiment
                    | SituationalDimension::Proximity
                    | SituationalDimension::Relationship
                    | SituationalDimension::Formality
            );
            assert_eq!(dim.is_vep_0004(), expected, "is_vep_0004 wrong for {dim}");
        }
    }

    #[test]
    fn relationship_is_free_form_others_are_not() {
        assert!(SituationalDimension::Relationship.is_free_form());
        for dim in SituationalDimension::all() {
            if *dim != SituationalDimension::Relationship {
                assert!(!dim.is_free_form(), "unexpected free-form for {dim}");
            }
        }
    }

    #[test]
    fn empty_context() {
        let ctx = SituationalContext::default();
        assert!(!ctx.has_any());
        assert!(!ctx.has_vep_0004());
        assert_eq!(ctx.to_wire(), "");
    }

    #[test]
    fn wire_roundtrip_single() {
        let mut ctx = SituationalContext::default();
        ctx.time = Some(vec!["\u{1F305}".to_string()]); // sunrise
        ctx.space = Some(vec!["\u{1F3E1}".to_string()]); // house

        let wire = ctx.to_wire();
        assert!(wire.contains("\u{23F0}\u{1F305}"));
        assert!(wire.contains("\u{1F4CD}\u{1F3E1}"));
    }

    #[test]
    fn from_wire_basic() {
        let wire = "\u{23F0}\u{1F305}|\u{1F4CD}\u{1F3E1}";
        let ctx = SituationalContext::from_wire(wire).unwrap();

        assert!(ctx.time.is_some());
        assert!(ctx.space.is_some());
        assert!(ctx.company.is_none());
    }

    #[test]
    fn from_wire_empty() {
        let ctx = SituationalContext::from_wire("").unwrap();
        assert!(!ctx.has_any());
    }

    #[test]
    fn get_and_set() {
        let mut ctx = SituationalContext::default();
        assert!(ctx.get(SituationalDimension::Culture).is_none());

        ctx.set(
            SituationalDimension::Culture,
            vec!["\u{1F1EC}\u{1F1E7}".to_string()],
        );
        assert!(ctx.get(SituationalDimension::Culture).is_some());
    }

    #[test]
    fn serde_roundtrip() {
        let mut ctx = SituationalContext::default();
        ctx.time = Some(vec!["morning".to_string()]);
        ctx.company = Some(vec!["alone".to_string()]);

        let json = serde_json::to_string(&ctx).unwrap();
        let parsed: SituationalContext = serde_json::from_str(&json).unwrap();
        assert_eq!(ctx, parsed);
    }

    // ── VEP-0004 ────────────────────────────────────────────

    #[test]
    fn vep_0004_symbols_encode_and_parse() {
        let mut ctx = SituationalContext::default();
        ctx.embodiment = Some(vec!["\u{270B}".to_string()]); // ✋
        ctx.proximity = Some(vec!["\u{1F90F}".to_string()]); // 🤏
        ctx.relationship = Some(vec!["colleague:professional".to_string()]);
        ctx.formality = Some(vec!["\u{1F4BC}".to_string()]); // 💼

        let wire = ctx.to_wire();
        assert!(wire.contains("\u{1F9CD}\u{270B}"));
        assert!(wire.contains("\u{2194}\u{FE0F}\u{1F90F}"));
        assert!(wire.contains("\u{1FAA2}colleague:professional"));
        assert!(wire.contains("\u{1F3A9}\u{1F4BC}"));

        let parsed = SituationalContext::from_wire(&wire).unwrap();
        assert_eq!(
            parsed.embodiment.as_deref(),
            Some(&["\u{270B}".to_string()][..])
        );
        assert_eq!(
            parsed.proximity.as_deref(),
            Some(&["\u{1F90F}".to_string()][..])
        );
        assert_eq!(
            parsed.relationship.as_deref(),
            Some(&["colleague:professional".to_string()][..])
        );
        assert_eq!(
            parsed.formality.as_deref(),
            Some(&["\u{1F4BC}".to_string()][..])
        );
    }

    #[test]
    fn has_vep_0004_is_true_when_vep_dim_set() {
        let mut ctx = SituationalContext::default();
        ctx.time = Some(vec!["\u{1F305}".to_string()]);
        assert!(!ctx.has_vep_0004());

        ctx.formality = Some(vec!["\u{1F4BC}".to_string()]);
        assert!(ctx.has_vep_0004());
    }

    #[test]
    fn canonical_thirteen_dim_example_encodes() {
        let mut ctx = SituationalContext::default();
        ctx.time = Some(vec!["\u{1F305}".to_string()]); // 🌅
        ctx.space = Some(vec!["\u{1F3E2}".to_string()]); // 🏢
        ctx.company = Some(vec!["\u{1F454}".to_string()]); // 👔
        ctx.occasion = Some(vec!["\u{1F4BC}".to_string()]); // 💼
        ctx.embodiment = Some(vec!["\u{270B}".to_string()]); // ✋
        ctx.proximity = Some(vec!["\u{1F90F}".to_string()]); // 🤏
        ctx.relationship = Some(vec!["colleague:professional".to_string()]);
        ctx.formality = Some(vec!["\u{1F4BC}".to_string()]); // 💼

        let expected = "\u{23F0}\u{1F305}\
                        |\u{1F4CD}\u{1F3E2}\
                        |\u{1F465}\u{1F454}\
                        |\u{1F3AD}\u{1F4BC}\
                        |\u{1F9CD}\u{270B}\
                        |\u{2194}\u{FE0F}\u{1F90F}\
                        |\u{1FAA2}colleague:professional\
                        |\u{1F3A9}\u{1F4BC}";
        assert_eq!(ctx.to_wire(), expected);
    }
}
