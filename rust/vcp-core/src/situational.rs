//! Situational context dimensions (VCP v3.1 Layer 2).
//!
//! Nine categorical dimensions describe the user's current situation
//! using emoji-keyed tag arrays in a compact wire format.
//!
//! Wire format example: `\u{23F0}\u{1F305}|\u{1F4CD}\u{1F3E1}|\u{1F465}\u{1F454}`

use std::fmt;

use serde::{Deserialize, Serialize};

use crate::error::{VcpError, VcpResult};

/// The nine situational context dimensions.
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
}

impl SituationalDimension {
    /// Emoji symbol used as the wire-format prefix.
    pub fn symbol(self) -> &'static str {
        match self {
            Self::Time => "\u{23F0}",                 // alarm clock
            Self::Space => "\u{1F4CD}",               // round pushpin
            Self::Company => "\u{1F465}",             // busts in silhouette
            Self::Culture => "\u{1F30D}",             // globe showing Europe-Africa
            Self::Occasion => "\u{1F3AD}",            // performing arts
            Self::Environment => "\u{1F321}\u{FE0F}", // thermometer
            Self::Agency => "\u{1F537}",              // large blue diamond
            Self::Constraints => "\u{1F536}",         // large orange diamond
            Self::SystemContext => "\u{1F4E1}",       // satellite antenna
        }
    }

    /// Parse from the emoji symbol prefix.
    pub fn from_symbol(s: &str) -> Option<Self> {
        // Check two-codepoint variant first (thermometer + VS16).
        if s.starts_with("\u{1F321}\u{FE0F}") || s == "\u{1F321}\u{FE0F}" {
            return Some(Self::Environment);
        }
        // Also accept bare thermometer without variation selector.
        if s.starts_with("\u{1F321}") || s == "\u{1F321}" {
            return Some(Self::Environment);
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
            _ => None,
        }
    }

    /// All nine dimensions in canonical order.
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
        };
        f.write_str(label)
    }
}

/// The complete set of situational context tags.
///
/// Each dimension maps to an optional list of tags (emoji values in wire format).
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
    }

    /// Encode to wire format.
    ///
    /// Each dimension is encoded as `<symbol><tag1><tag2>...` and
    /// dimensions are separated by `|`.
    pub fn to_wire(&self) -> String {
        let mut parts = Vec::new();

        let dims: [(SituationalDimension, &Option<Vec<String>>); 9] = [
            (SituationalDimension::Time, &self.time),
            (SituationalDimension::Space, &self.space),
            (SituationalDimension::Company, &self.company),
            (SituationalDimension::Culture, &self.culture),
            (SituationalDimension::Occasion, &self.occasion),
            (SituationalDimension::Environment, &self.environment),
            (SituationalDimension::Agency, &self.agency),
            (SituationalDimension::Constraints, &self.constraints),
            (SituationalDimension::SystemContext, &self.system_context),
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
                // Tags are the remaining content. They are typically emoji
                // characters but we treat them as opaque strings. Each
                // "word" is a separate tag when space-separated, or
                // the whole remainder is one tag.
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
/// Environment uses a two-codepoint emoji (\u{1F321}\u{FE0F}), so we
/// must check for it before single-codepoint symbols.
fn split_situational_symbol(s: &str) -> VcpResult<(SituationalDimension, &str)> {
    // Known single-codepoint symbols in descending byte-length order.
    static SYMBOLS: &[(SituationalDimension, &str)] = &[
        (SituationalDimension::Space, "\u{1F4CD}"),
        (SituationalDimension::Company, "\u{1F465}"),
        (SituationalDimension::Culture, "\u{1F30D}"),
        (SituationalDimension::Occasion, "\u{1F3AD}"),
        (SituationalDimension::Agency, "\u{1F537}"),
        (SituationalDimension::Constraints, "\u{1F536}"),
        (SituationalDimension::SystemContext, "\u{1F4E1}"),
        (SituationalDimension::Time, "\u{23F0}"),
    ];

    // Check two-codepoint Environment symbol first.
    let env_sym = "\u{1F321}\u{FE0F}";
    if let Some(rest) = s.strip_prefix(env_sym) {
        return Ok((SituationalDimension::Environment, rest));
    }
    // Also accept bare thermometer without variation selector.
    let env_bare = "\u{1F321}";
    if let Some(rest) = s.strip_prefix(env_bare) {
        return Ok((SituationalDimension::Environment, rest));
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
    fn empty_context() {
        let ctx = SituationalContext::default();
        assert!(!ctx.has_any());
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
}
