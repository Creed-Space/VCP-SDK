//! Personal state dimensions (VCP v3.1 Layer 3).
//!
//! Personal state carries five categorical dimensions, each with a named
//! value and a 1-5 intensity.  An optional `extended` sub-signal provides
//! additional specificity (e.g. `body_signals = pain:4 [migraine]`).
//!
//! This layer is **not diagnostic or therapeutic**; it reflects
//! self-reported state for adaptation purposes only.

use std::fmt;

use serde::{Deserialize, Serialize};

use crate::error::{VcpError, VcpResult};

// ── Dimension enums ─────────────────────────────────────────

/// The five personal-state dimensions.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum PersonalDimensionKind {
    CognitiveState,
    EmotionalTone,
    EnergyLevel,
    PerceivedUrgency,
    BodySignals,
}

impl PersonalDimensionKind {
    /// Emoji symbol used in wire format.
    pub fn symbol(self) -> &'static str {
        match self {
            Self::CognitiveState => "\u{1F9E0}",  // brain
            Self::EmotionalTone => "\u{1F4AD}",   // thought balloon
            Self::EnergyLevel => "\u{1F50B}",     // battery
            Self::PerceivedUrgency => "\u{26A1}",  // high voltage
            Self::BodySignals => "\u{1FA7A}",      // stethoscope
        }
    }

    /// Parse from the emoji symbol. Returns `None` on unrecognised input.
    pub fn from_symbol(s: &str) -> Option<Self> {
        match s {
            "\u{1F9E0}" => Some(Self::CognitiveState),
            "\u{1F4AD}" => Some(Self::EmotionalTone),
            "\u{1F50B}" => Some(Self::EnergyLevel),
            "\u{26A1}" => Some(Self::PerceivedUrgency),
            "\u{1FA7A}" => Some(Self::BodySignals),
            _ => None,
        }
    }

    /// The set of valid category names for this dimension.
    pub fn valid_values(self) -> &'static [&'static str] {
        match self {
            Self::CognitiveState => &["focused", "distracted", "overloaded", "foggy", "reflective"],
            Self::EmotionalTone => &["calm", "tense", "frustrated", "neutral", "uplifted"],
            Self::EnergyLevel => &["rested", "low_energy", "fatigued", "wired", "depleted"],
            Self::PerceivedUrgency => &["unhurried", "time_aware", "pressured", "critical"],
            Self::BodySignals => &["neutral", "discomfort", "pain", "unwell", "recovering"],
        }
    }
}

impl fmt::Display for PersonalDimensionKind {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let label = match self {
            Self::CognitiveState => "cognitive_state",
            Self::EmotionalTone => "emotional_tone",
            Self::EnergyLevel => "energy_level",
            Self::PerceivedUrgency => "perceived_urgency",
            Self::BodySignals => "body_signals",
        };
        f.write_str(label)
    }
}

// ── Single dimension value ──────────────────────────────────

/// A single personal-state dimension with a categorical value,
/// intensity (1-5, default 3), and optional extended sub-signal.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct PersonalDimension {
    /// Categorical value (e.g. "focused", "calm", "rested").
    pub value: String,
    /// Intensity 1-5.  1 = barely noticeable, 5 = extreme.
    pub intensity: u8,
    /// Optional extended qualifier (e.g. "migraine", "bathroom").
    #[serde(skip_serializing_if = "Option::is_none")]
    pub extended: Option<String>,
}

impl PersonalDimension {
    /// Create with validation.
    pub fn new(value: impl Into<String>, intensity: u8) -> VcpResult<Self> {
        if !(1..=5).contains(&intensity) {
            return Err(VcpError::InvalidIntensity(intensity));
        }
        Ok(Self {
            value: value.into(),
            intensity,
            extended: None,
        })
    }

    /// Create with an extended sub-signal.
    pub fn with_extended(
        value: impl Into<String>,
        intensity: u8,
        extended: impl Into<String>,
    ) -> VcpResult<Self> {
        if !(1..=5).contains(&intensity) {
            return Err(VcpError::InvalidIntensity(intensity));
        }
        Ok(Self {
            value: value.into(),
            intensity,
            extended: Some(extended.into()),
        })
    }

    /// Encode to wire-format segment: `value:intensity` or `value:intensity[ext]`.
    pub fn to_wire(&self) -> String {
        let mut s = format!("{}:{}", self.value, self.intensity);
        if let Some(ref ext) = self.extended {
            s.push('[');
            s.push_str(ext);
            s.push(']');
        }
        s
    }

    /// Parse from wire-format segment: `value:intensity` or `value:intensity[ext]`.
    pub fn from_wire(wire: &str) -> VcpResult<Self> {
        // Check for extended: value:intensity[ext]
        let (main, extended) = if let Some(bracket_start) = wire.find('[') {
            if !wire.ends_with(']') {
                return Err(VcpError::ParseError(format!(
                    "unterminated bracket in personal dimension: {wire}"
                )));
            }
            let ext = &wire[bracket_start + 1..wire.len() - 1];
            (&wire[..bracket_start], Some(ext.to_string()))
        } else {
            (wire, None)
        };

        let parts: Vec<&str> = main.split(':').collect();
        if parts.len() != 2 {
            return Err(VcpError::ParseError(format!(
                "personal dimension must be value:intensity, got: {wire}"
            )));
        }

        let value = parts[0].to_string();
        let intensity: u8 = parts[1]
            .parse()
            .map_err(|_| VcpError::ParseError(format!("invalid intensity: {}", parts[1])))?;

        if !(1..=5).contains(&intensity) {
            return Err(VcpError::InvalidIntensity(intensity));
        }

        Ok(Self {
            value,
            intensity,
            extended,
        })
    }
}

impl fmt::Display for PersonalDimension {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(&self.to_wire())
    }
}

// ── Full personal state ─────────────────────────────────────

/// Complete personal state across all five dimensions.
///
/// Each dimension is optional -- only dimensions with active signals are set.
#[derive(Debug, Clone, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct PersonalState {
    /// Cognitive state (focused / distracted / overloaded / foggy / reflective).
    #[serde(skip_serializing_if = "Option::is_none")]
    pub cognitive: Option<PersonalDimension>,
    /// Emotional tone (calm / tense / frustrated / neutral / uplifted).
    #[serde(skip_serializing_if = "Option::is_none")]
    pub emotional: Option<PersonalDimension>,
    /// Energy level (rested / low_energy / fatigued / wired / depleted).
    #[serde(skip_serializing_if = "Option::is_none")]
    pub energy: Option<PersonalDimension>,
    /// Perceived urgency (unhurried / time_aware / pressured / critical).
    #[serde(skip_serializing_if = "Option::is_none")]
    pub urgency: Option<PersonalDimension>,
    /// Body signals (neutral / discomfort / pain / unwell / recovering).
    #[serde(skip_serializing_if = "Option::is_none")]
    pub body: Option<PersonalDimension>,
}

impl PersonalState {
    /// Returns `true` if at least one dimension is set.
    pub fn has_any(&self) -> bool {
        self.cognitive.is_some()
            || self.emotional.is_some()
            || self.energy.is_some()
            || self.urgency.is_some()
            || self.body.is_some()
    }

    /// Encode personal state to wire format (the part after `\u{2016}`).
    ///
    /// Format: `<symbol><value>:<intensity>[|...]`
    pub fn to_wire(&self) -> String {
        let mut parts = Vec::new();

        let dims: [(PersonalDimensionKind, &Option<PersonalDimension>); 5] = [
            (PersonalDimensionKind::CognitiveState, &self.cognitive),
            (PersonalDimensionKind::EmotionalTone, &self.emotional),
            (PersonalDimensionKind::EnergyLevel, &self.energy),
            (PersonalDimensionKind::PerceivedUrgency, &self.urgency),
            (PersonalDimensionKind::BodySignals, &self.body),
        ];

        for (kind, dim_opt) in &dims {
            if let Some(dim) = dim_opt {
                parts.push(format!("{}{}", kind.symbol(), dim.to_wire()));
            }
        }

        parts.join("|")
    }

    /// Parse personal state from wire format (the part after `\u{2016}`).
    pub fn from_wire(wire: &str) -> VcpResult<Self> {
        let mut state = PersonalState::default();

        if wire.is_empty() {
            return Ok(state);
        }

        for segment in wire.split('|') {
            let segment = segment.trim();
            if segment.is_empty() {
                continue;
            }

            // The segment starts with an emoji, then value:intensity.
            // Emojis can be multi-byte, so we need to find the split point.
            let (symbol, rest) = split_leading_emoji(segment)?;

            let kind = PersonalDimensionKind::from_symbol(symbol).ok_or_else(|| {
                VcpError::ParseError(format!("unknown personal dimension symbol: {symbol}"))
            })?;

            let dim = PersonalDimension::from_wire(rest)?;

            match kind {
                PersonalDimensionKind::CognitiveState => state.cognitive = Some(dim),
                PersonalDimensionKind::EmotionalTone => state.emotional = Some(dim),
                PersonalDimensionKind::EnergyLevel => state.energy = Some(dim),
                PersonalDimensionKind::PerceivedUrgency => state.urgency = Some(dim),
                PersonalDimensionKind::BodySignals => state.body = Some(dim),
            }
        }

        Ok(state)
    }
}

impl fmt::Display for PersonalState {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(&self.to_wire())
    }
}

/// Split the leading emoji character(s) from the rest of a wire segment.
///
/// VCP personal dimension emojis are either single code points or short
/// multi-code-point sequences. We try known symbols first, then fall back
/// to taking the first Unicode scalar.
fn split_leading_emoji(s: &str) -> VcpResult<(&str, &str)> {
    // Known symbols in descending byte-length order for greedy matching.
    static SYMBOLS: &[&str] = &[
        "\u{1F9E0}",  // brain (4 bytes)
        "\u{1F4AD}",  // thought balloon (4 bytes)
        "\u{1F50B}",  // battery (4 bytes)
        "\u{1FA7A}",  // stethoscope (4 bytes)
        "\u{26A1}",   // high voltage (3 bytes)
    ];

    for sym in SYMBOLS {
        if let Some(rest) = s.strip_prefix(sym) {
            return Ok((sym, rest));
        }
    }

    // Fallback: take the first char.
    let first_char_len = s
        .chars()
        .next()
        .ok_or_else(|| VcpError::ParseError("empty segment".into()))?
        .len_utf8();
    Ok((&s[..first_char_len], &s[first_char_len..]))
}

// ── Tests ───────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;
    use pretty_assertions::assert_eq;

    #[test]
    fn dimension_new_valid() {
        let d = PersonalDimension::new("focused", 4).unwrap();
        assert_eq!(d.value, "focused");
        assert_eq!(d.intensity, 4);
        assert_eq!(d.extended, None);
    }

    #[test]
    fn dimension_new_invalid_intensity() {
        assert!(PersonalDimension::new("focused", 0).is_err());
        assert!(PersonalDimension::new("focused", 6).is_err());
    }

    #[test]
    fn dimension_with_extended() {
        let d = PersonalDimension::with_extended("pain", 4, "migraine").unwrap();
        assert_eq!(d.extended.as_deref(), Some("migraine"));
        assert_eq!(d.to_wire(), "pain:4[migraine]");
    }

    #[test]
    fn dimension_wire_roundtrip() {
        let cases = vec!["focused:4", "calm:3", "pain:4[migraine]", "rested:1"];
        for case in cases {
            let d = PersonalDimension::from_wire(case).unwrap();
            assert_eq!(d.to_wire(), case);
        }
    }

    #[test]
    fn dimension_wire_error_missing_colon() {
        assert!(PersonalDimension::from_wire("focused").is_err());
    }

    #[test]
    fn dimension_wire_error_bad_intensity() {
        assert!(PersonalDimension::from_wire("focused:0").is_err());
        assert!(PersonalDimension::from_wire("focused:9").is_err());
    }

    #[test]
    fn personal_state_empty() {
        let ps = PersonalState::default();
        assert!(!ps.has_any());
        assert_eq!(ps.to_wire(), "");
    }

    #[test]
    fn personal_state_wire_roundtrip() {
        let mut ps = PersonalState::default();
        ps.cognitive = Some(PersonalDimension::new("focused", 4).unwrap());
        ps.emotional = Some(PersonalDimension::new("calm", 3).unwrap());

        let wire = ps.to_wire();
        assert!(wire.contains("focused:4"));
        assert!(wire.contains("calm:3"));

        let parsed = PersonalState::from_wire(&wire).unwrap();
        assert_eq!(parsed.cognitive.as_ref().unwrap().value, "focused");
        assert_eq!(parsed.cognitive.as_ref().unwrap().intensity, 4);
        assert_eq!(parsed.emotional.as_ref().unwrap().value, "calm");
        assert_eq!(parsed.emotional.as_ref().unwrap().intensity, 3);
    }

    #[test]
    fn personal_state_all_dimensions() {
        let mut ps = PersonalState::default();
        ps.cognitive = Some(PersonalDimension::new("overloaded", 5).unwrap());
        ps.emotional = Some(PersonalDimension::new("tense", 4).unwrap());
        ps.energy = Some(PersonalDimension::new("depleted", 4).unwrap());
        ps.urgency = Some(PersonalDimension::new("critical", 5).unwrap());
        ps.body = Some(PersonalDimension::with_extended("pain", 4, "migraine").unwrap());

        let wire = ps.to_wire();
        let parsed = PersonalState::from_wire(&wire).unwrap();

        assert_eq!(parsed.cognitive.as_ref().unwrap().value, "overloaded");
        assert_eq!(parsed.emotional.as_ref().unwrap().value, "tense");
        assert_eq!(parsed.energy.as_ref().unwrap().value, "depleted");
        assert_eq!(parsed.urgency.as_ref().unwrap().value, "critical");
        assert_eq!(parsed.body.as_ref().unwrap().value, "pain");
        assert_eq!(
            parsed.body.as_ref().unwrap().extended.as_deref(),
            Some("migraine")
        );
    }

    #[test]
    fn dimension_kind_symbols() {
        for kind in [
            PersonalDimensionKind::CognitiveState,
            PersonalDimensionKind::EmotionalTone,
            PersonalDimensionKind::EnergyLevel,
            PersonalDimensionKind::PerceivedUrgency,
            PersonalDimensionKind::BodySignals,
        ] {
            let sym = kind.symbol();
            assert_eq!(PersonalDimensionKind::from_symbol(sym), Some(kind));
        }
    }

    #[test]
    fn dimension_kind_valid_values() {
        assert!(PersonalDimensionKind::CognitiveState
            .valid_values()
            .contains(&"focused"));
        assert!(PersonalDimensionKind::PerceivedUrgency
            .valid_values()
            .contains(&"critical"));
    }

    #[test]
    fn serde_roundtrip() {
        let mut ps = PersonalState::default();
        ps.cognitive = Some(PersonalDimension::new("focused", 4).unwrap());
        ps.body = Some(PersonalDimension::with_extended("pain", 3, "headache").unwrap());

        let json = serde_json::to_string(&ps).unwrap();
        let parsed: PersonalState = serde_json::from_str(&json).unwrap();
        assert_eq!(ps, parsed);
    }
}
