//! Personal state dimensions (VCP v3.1 personal context tier).
//!
//! Personal state carries five categorical dimensions, each with a named
//! value and an optional 1-5 intensity.  An optional `extended` sub-signal
//! provides additional specificity; it travels only on the CSM-1 token
//! R-line (`🩺pain:4:migraine`, VCP/S §2.4.1), never in a VCP/A context
//! string (VCP/A §2.3).
//!
//! This tier is **not diagnostic or therapeutic**; it reflects
//! self-reported state for adaptation purposes only.

use std::fmt;

use serde::de::Error as _;
use serde::{Deserialize, Deserializer, Serialize};

use crate::error::{VcpError, VcpResult};

const MAX_PERSONAL_WIRE_CHARS: usize = 8_192;

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
            Self::PerceivedUrgency => "\u{26A1}", // high voltage
            Self::BodySignals => "\u{1FA7A}",     // stethoscope
        }
    }

    /// Parse from the emoji symbol. Returns `None` on unrecognized input.
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
///
/// Two wire forms exist (VCP/A §2.3, VCP/S §2.4.1):
///
/// * the VCP/A context string ([`PersonalDimension::to_wire`]):
///   `value[:intensity]`, where the intensity may be omitted (it then
///   defaults to 3 and the omission is kept on re-encode) and no sub-signal
///   is ever carried;
/// * the CSM-1 token R-line ([`PersonalDimension::to_r_line`]):
///   `value:intensity[:extended]`, the only wire form for `extended`.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PersonalDimension {
    /// Categorical value (e.g. "focused", "calm", "rested").
    pub value: String,
    /// Intensity 1-5.  1 = barely noticeable, 5 = extreme.  3 when omitted.
    pub intensity: u8,
    /// Optional extended qualifier (e.g. "migraine"). Carried only on the
    /// CSM-1 R-line, never in a VCP/A context string.
    pub extended: Option<String>,
    /// Whether the intensity was stated. A context-string value without an
    /// intensity (`🧠focused`) decodes with `intensity == 3` and
    /// `intensity_explicit == false`, and re-encodes without one.
    pub intensity_explicit: bool,
}

impl Serialize for PersonalDimension {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        use serde::ser::SerializeStruct;

        let fields =
            1 + usize::from(self.intensity_explicit) + usize::from(self.extended.is_some());
        let mut state = serializer.serialize_struct("PersonalDimension", fields)?;
        state.serialize_field("value", &self.value)?;
        if self.intensity_explicit {
            state.serialize_field("intensity", &self.intensity)?;
        }
        if let Some(extended) = &self.extended {
            state.serialize_field("extended", extended)?;
        }
        state.end()
    }
}

impl PersonalDimension {
    const MAX_VALUE_CHARS: usize = 64;
    const MAX_EXTENDED_CHARS: usize = 256;
    /// Intensity used when a context-string value omits it.
    pub const DEFAULT_INTENSITY: u8 = 3;

    fn validate(value: &str, intensity: u8, extended: Option<&str>) -> VcpResult<()> {
        let valid_value = !value.is_empty()
            && value.chars().count() <= Self::MAX_VALUE_CHARS
            && value
                .bytes()
                .next()
                .is_some_and(|byte| byte.is_ascii_lowercase())
            && value
                .chars()
                .all(|character| character.is_ascii_lowercase() || character == '_');
        if !valid_value {
            return Err(VcpError::ParseError(
                "personal value must match [a-z][a-z_]{0,63}".to_string(),
            ));
        }
        if !(1..=5).contains(&intensity) {
            return Err(VcpError::InvalidIntensity(intensity));
        }
        if let Some(extended) = extended {
            // VCP/S §2.4.1: extended = 1*( ALPHA / "_" ).
            if extended.is_empty()
                || extended.chars().count() > Self::MAX_EXTENDED_CHARS
                || !extended
                    .chars()
                    .all(|character| character.is_ascii_alphabetic() || character == '_')
            {
                return Err(VcpError::ParseError(
                    "extended personal value must be 1-256 ASCII letters or underscores"
                        .to_string(),
                ));
            }
        }
        Ok(())
    }

    /// Parse the intensity field: exactly one ASCII digit 1-5 (VCP/A §2.3).
    fn parse_intensity(raw: &str) -> VcpResult<u8> {
        match raw.as_bytes() {
            [digit @ b'1'..=b'5'] => Ok(digit - b'0'),
            _ => Err(VcpError::ParseError(format!(
                "invalid intensity (must be one digit 1-5): {raw}"
            ))),
        }
    }

    /// Create with validation.
    ///
    /// # Errors
    ///
    /// Returns [`VcpError::InvalidIntensity`] if `intensity` is not in 1..=5.
    pub fn new(value: impl Into<String>, intensity: u8) -> VcpResult<Self> {
        let value = value.into();
        Self::validate(&value, intensity, None)?;
        Ok(Self {
            value,
            intensity,
            extended: None,
            intensity_explicit: true,
        })
    }

    /// Create a value without a stated intensity (intensity 3, omitted on
    /// the VCP/A wire).
    ///
    /// # Errors
    ///
    /// Returns [`VcpError::ParseError`] if the value is not a category name.
    pub fn without_intensity(value: impl Into<String>) -> VcpResult<Self> {
        let value = value.into();
        Self::validate(&value, Self::DEFAULT_INTENSITY, None)?;
        Ok(Self {
            value,
            intensity: Self::DEFAULT_INTENSITY,
            extended: None,
            intensity_explicit: false,
        })
    }

    /// Create with an extended sub-signal (carried only on the CSM-1 R-line).
    ///
    /// # Errors
    ///
    /// Returns [`VcpError::InvalidIntensity`] if `intensity` is not in 1..=5,
    /// or [`VcpError::ParseError`] if `extended` is not 1-256 ASCII letters
    /// or underscores (VCP/S §2.4.1).
    pub fn with_extended(
        value: impl Into<String>,
        intensity: u8,
        extended: impl Into<String>,
    ) -> VcpResult<Self> {
        let value = value.into();
        let extended = extended.into();
        Self::validate(&value, intensity, Some(&extended))?;
        Ok(Self {
            value,
            intensity,
            extended: Some(extended),
            intensity_explicit: true,
        })
    }

    /// Encode for a VCP/A context string: `value` or `value:intensity`.
    ///
    /// A context string carries no sub-signal (VCP/A §2.3), so `extended` is
    /// never written here; use [`PersonalDimension::to_r_line`] for the
    /// CSM-1 R-line.
    pub fn to_wire(&self) -> String {
        if self.intensity_explicit {
            format!("{}:{}", self.value, self.intensity)
        } else {
            self.value.clone()
        }
    }

    /// Parse a VCP/A context-string value: `value` or `value:intensity`.
    ///
    /// # Errors
    ///
    /// Returns [`VcpError::ParseError`] if the intensity is not exactly one
    /// digit 1-5 or anything follows it, including a sub-signal such as
    /// `pain:4[migraine]` or `pain:4:migraine` (VCP/A §2.3), or if the value
    /// is not a category name.
    pub fn from_wire(wire: &str) -> VcpResult<Self> {
        match wire.split_once(':') {
            None => Self::without_intensity(wire),
            Some((value, intensity)) => {
                let intensity = Self::parse_intensity(intensity)?;
                Self::new(value, intensity)
            }
        }
    }

    /// Encode for the CSM-1 token R-line: `value:intensity[:extended]`
    /// (VCP/S §2.4.1). The R-line always states the intensity.
    pub fn to_r_line(&self) -> String {
        match &self.extended {
            Some(extended) => format!("{}:{}:{extended}", self.value, self.intensity),
            None => format!("{}:{}", self.value, self.intensity),
        }
    }

    /// Parse a CSM-1 R-line value: `value:intensity[:extended]`.
    ///
    /// # Errors
    ///
    /// Returns [`VcpError::ParseError`] if the intensity is missing or not
    /// one digit 1-5, or if the value or sub-signal is malformed.
    pub fn from_r_line(wire: &str) -> VcpResult<Self> {
        let mut parts = wire.splitn(3, ':');
        let value = parts.next().unwrap_or_default();
        let Some(intensity) = parts.next() else {
            return Err(VcpError::ParseError(format!(
                "R-line personal dimension must be value:intensity, got: {wire}"
            )));
        };
        let intensity = Self::parse_intensity(intensity)?;
        match parts.next() {
            Some(extended) => Self::with_extended(value, intensity, extended),
            None => Self::new(value, intensity),
        }
    }
}

impl<'de> Deserialize<'de> for PersonalDimension {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: Deserializer<'de>,
    {
        #[derive(Deserialize)]
        #[serde(deny_unknown_fields)]
        struct WireDimension {
            value: String,
            #[serde(default)]
            intensity: Option<u8>,
            #[serde(default)]
            extended: Option<String>,
        }

        let wire = WireDimension::deserialize(deserializer)?;
        let intensity = wire.intensity.unwrap_or(Self::DEFAULT_INTENSITY);
        PersonalDimension::validate(&wire.value, intensity, wire.extended.as_deref())
            .map_err(D::Error::custom)?;
        Ok(PersonalDimension {
            value: wire.value,
            intensity,
            extended: wire.extended,
            intensity_explicit: wire.intensity.is_some(),
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
/// Each dimension is optional; only dimensions with active signals are set.
#[derive(Debug, Clone, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct PersonalState {
    /// Cognitive state (focused / distracted / overloaded / foggy / reflective).
    #[serde(skip_serializing_if = "Option::is_none")]
    pub cognitive: Option<PersonalDimension>,
    /// Emotional tone (calm / tense / frustrated / neutral / uplifted).
    #[serde(skip_serializing_if = "Option::is_none")]
    pub emotional: Option<PersonalDimension>,
    /// Energy level (rested / `low_energy` / fatigued / wired / depleted).
    #[serde(skip_serializing_if = "Option::is_none")]
    pub energy: Option<PersonalDimension>,
    /// Perceived urgency (unhurried / `time_aware` / pressured / critical).
    #[serde(skip_serializing_if = "Option::is_none")]
    pub urgency: Option<PersonalDimension>,
    /// Body signals (neutral / discomfort / pain / unwell / recovering).
    #[serde(skip_serializing_if = "Option::is_none")]
    pub body: Option<PersonalDimension>,
    /// Raw groups whose dimension emoji is not recognized, in wire order.
    /// They take no part in adaptation and are re-encoded unchanged after the
    /// known dimensions (VCP/A §2.3).
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub unknown: Vec<String>,
}

impl PersonalState {
    /// Returns `true` if at least one known dimension is set. Unknown
    /// dimension groups do not count.
    pub fn has_any(&self) -> bool {
        self.cognitive.is_some()
            || self.emotional.is_some()
            || self.energy.is_some()
            || self.urgency.is_some()
            || self.body.is_some()
    }

    /// Encode personal state for a VCP/A context string (the part after
    /// `\u{2016}`): `<symbol><value>[:<intensity>][|...]`. No sub-signal is
    /// written (VCP/A §2.3).
    pub fn to_wire(&self) -> String {
        self.encode(PersonalDimension::to_wire)
    }

    /// Encode personal state for the CSM-1 token R-line (after `R:`):
    /// `<symbol><value>:<intensity>[:<extended>][|...]` (VCP/S §2.4.1).
    pub fn to_r_line(&self) -> String {
        self.encode(PersonalDimension::to_r_line)
    }

    fn encode(&self, dimension_wire: fn(&PersonalDimension) -> String) -> String {
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
                parts.push(format!("{}{}", kind.symbol(), dimension_wire(dim)));
            }
        }
        parts.extend(self.unknown.iter().cloned());

        parts.join("|")
    }

    /// Parse personal state from wire format (the part after `\u{2016}`).
    ///
    /// A segment that starts with an unknown dimension emoji is kept in
    /// [`PersonalState::unknown`], re-encoded unchanged, and the rest is
    /// parsed (VCP/S §2.4.2, VCP/A §2.3).
    ///
    /// # Errors
    ///
    /// Returns [`VcpError::ParseError`] if a segment is empty, lacks a
    /// leading emoji, repeats a dimension, or carries malformed dimension
    /// data.
    pub fn from_wire(wire: &str) -> VcpResult<Self> {
        Self::decode(wire, PersonalDimension::from_wire)
    }

    /// Parse personal state from the CSM-1 token R-line (after `R:`), where
    /// each value states its intensity and may carry `:extended`.
    ///
    /// # Errors
    ///
    /// As [`PersonalState::from_wire`], and a value without an intensity.
    pub fn from_r_line(wire: &str) -> VcpResult<Self> {
        Self::decode(wire, PersonalDimension::from_r_line)
    }

    fn decode(
        wire: &str,
        dimension_parser: fn(&str) -> VcpResult<PersonalDimension>,
    ) -> VcpResult<Self> {
        let mut state = PersonalState::default();

        if wire.is_empty() {
            return Ok(state);
        }
        if wire.chars().count() > MAX_PERSONAL_WIRE_CHARS {
            return Err(VcpError::ParseError(format!(
                "personal state exceeds {MAX_PERSONAL_WIRE_CHARS} characters"
            )));
        }

        for segment in wire.split('|') {
            if segment.is_empty() {
                return Err(VcpError::ParseError(
                    "personal state contains an empty dimension segment".to_string(),
                ));
            }

            // The segment starts with an emoji, then value:intensity.
            // Emojis can be multi-byte, so we need to find the split point.
            let (symbol, rest) = split_leading_emoji(segment)?;

            if symbol.is_ascii() {
                return Err(VcpError::ParseError(format!(
                    "personal dimension segment must start with a dimension emoji: {segment}"
                )));
            }
            let Some(kind) = PersonalDimensionKind::from_symbol(symbol) else {
                // Unknown dimension emoji: keep it for pass-through.
                state.unknown.push(segment.to_string());
                continue;
            };

            let dim = dimension_parser(rest)?;

            let slot = match kind {
                PersonalDimensionKind::CognitiveState => &mut state.cognitive,
                PersonalDimensionKind::EmotionalTone => &mut state.emotional,
                PersonalDimensionKind::EnergyLevel => &mut state.energy,
                PersonalDimensionKind::PerceivedUrgency => &mut state.urgency,
                PersonalDimensionKind::BodySignals => &mut state.body,
            };
            if slot.is_some() {
                return Err(VcpError::ParseError(format!(
                    "duplicate personal dimension: {kind}"
                )));
            }
            *slot = Some(dim);
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
        "\u{1F9E0}", // brain (4 bytes)
        "\u{1F4AD}", // thought balloon (4 bytes)
        "\u{1F50B}", // battery (4 bytes)
        "\u{1FA7A}", // stethoscope (4 bytes)
        "\u{26A1}",  // high voltage (3 bytes)
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
    fn intensity_is_exactly_one_digit_one_to_five() {
        for bad in [
            "focused:04",
            "focused:0",
            "focused:6",
            "focused:+4",
            "focused: 4",
            "focused:",
            "focused:\u{0664}",
        ] {
            assert!(PersonalDimension::from_wire(bad).is_err(), "{bad}");
        }
        for digit in 1..=5u8 {
            let parsed = PersonalDimension::from_wire(&format!("focused:{digit}")).unwrap();
            assert_eq!(parsed.intensity, digit);
        }
        assert!(PersonalState::from_wire("\u{1F9E0}focused:04").is_err());
    }

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
    fn dimension_constructors_reject_invalid_or_wire_ambiguous_text() {
        for invalid in ["", "Focused", "two words", "focused:calm", "focused|calm"] {
            assert!(
                PersonalDimension::new(invalid, 3).is_err(),
                "accepted {invalid:?}"
            );
        }
        assert!(PersonalDimension::new("x".repeat(65), 3).is_err());
        for invalid_extended in [
            "",
            "nested[detail]",
            "one|two",
            "one:two",
            "one-two",
            "one\u{2016}two",
            "one\0two",
        ] {
            assert!(PersonalDimension::with_extended("pain", 4, invalid_extended).is_err());
        }
        assert!(PersonalDimension::with_extended("pain", 4, "x".repeat(257)).is_err());
    }

    #[test]
    fn dimension_with_extended() {
        let d = PersonalDimension::with_extended("pain", 4, "migraine").unwrap();
        assert_eq!(d.extended.as_deref(), Some("migraine"));
        // A VCP/A context string carries no sub-signal (VCP/A §2.3) ...
        assert_eq!(d.to_wire(), "pain:4");
        // ... which travels only on the CSM-1 R-line (VCP/S §2.4.1).
        assert_eq!(d.to_r_line(), "pain:4:migraine");
        assert_eq!(
            PersonalDimension::from_r_line("pain:4:migraine").unwrap(),
            d
        );
    }

    #[test]
    fn context_wire_rejects_sub_signals() {
        for malformed in ["pain:4[migraine]", "pain:4:migraine", "pain:4:"] {
            assert!(
                PersonalDimension::from_wire(malformed).is_err(),
                "{malformed}"
            );
        }
        assert!(PersonalState::from_wire("\u{1FA7A}pain:4[migraine]").is_err());
        assert!(PersonalDimension::from_r_line("pain").is_err());
        assert!(PersonalDimension::from_r_line("pain:4[migraine]").is_err());
    }

    #[test]
    fn intensity_may_be_omitted_in_context_strings() {
        let d = PersonalDimension::from_wire("focused").unwrap();
        assert_eq!(d.intensity, 3);
        assert!(!d.intensity_explicit);
        assert_eq!(d.to_wire(), "focused");
        assert_eq!(serde_json::to_string(&d).unwrap(), r#"{"value":"focused"}"#);
        let back: PersonalDimension = serde_json::from_str(r#"{"value":"focused"}"#).unwrap();
        assert_eq!(back, d);
        let wire = "\u{1F9E0}focused|\u{1F4AD}calm:5|\u{1F50B}rested:4|\u{26A1}pressured:4|\u{1FA7A}neutral";
        assert_eq!(PersonalState::from_wire(wire).unwrap().to_wire(), wire);
        // The R-line always states the intensity.
        assert_eq!(d.to_r_line(), "focused:3");
    }

    #[test]
    fn dimension_wire_roundtrip() {
        let cases = vec!["focused:4", "calm:3", "pain:4", "rested:1", "calm"];
        for case in cases {
            let d = PersonalDimension::from_wire(case).unwrap();
            assert_eq!(d.to_wire(), case);
        }
    }

    #[test]
    fn r_line_requires_intensity() {
        // The context string allows an omitted intensity; the R-line does not.
        assert!(PersonalDimension::from_wire("focused").is_ok());
        assert!(PersonalDimension::from_r_line("focused").is_err());
    }

    #[test]
    fn dimension_wire_error_bad_intensity() {
        assert!(PersonalDimension::from_wire("focused:0").is_err());
        assert!(PersonalDimension::from_wire("focused:9").is_err());
    }

    #[test]
    fn personal_wire_rejects_empty_and_duplicate_segments() {
        let duplicate = "\u{1F9E0}focused:4|\u{1F9E0}reflective:3";
        for malformed in ["|", "\u{1F9E0}focused:4|", duplicate] {
            assert!(
                PersonalState::from_wire(malformed).is_err(),
                "accepted {malformed:?}"
            );
        }
        assert!(PersonalDimension::from_wire("pain:4[]").is_err());
        let oversized = format!("🧠{}:3", "a".repeat(MAX_PERSONAL_WIRE_CHARS));
        assert!(PersonalState::from_wire(&oversized)
            .unwrap_err()
            .to_string()
            .contains("8192 characters"));
    }

    #[test]
    fn personal_wire_passes_unknown_dimension_emoji_through() {
        let state = PersonalState::from_wire("\u{1F984}sparkly:2|\u{1F9E0}focused:4").unwrap();
        assert_eq!(state.cognitive.as_ref().unwrap().value, "focused");
        assert!(state.emotional.is_none());
        assert_eq!(state.unknown, vec!["\u{1F984}sparkly:2".to_string()]);
        // Known dimensions first, then unknown groups in wire order (VCP/A §2.3).
        assert_eq!(state.to_wire(), "\u{1F9E0}focused:4|\u{1F984}sparkly:2");

        let only_unknown = PersonalState::from_wire("\u{1F984}sparkly:2").unwrap();
        assert!(!only_unknown.has_any());
        assert_eq!(only_unknown.to_wire(), "\u{1F984}sparkly:2");

        // A segment with no leading emoji is malformed, not an unknown dimension.
        assert!(PersonalState::from_wire("focused:4").is_err());
    }

    #[test]
    fn personal_state_empty() {
        let ps = PersonalState::default();
        assert!(!ps.has_any());
        assert_eq!(ps.to_wire(), "");
    }

    #[test]
    fn personal_state_wire_roundtrip() {
        let ps = PersonalState {
            cognitive: Some(PersonalDimension::new("focused", 4).unwrap()),
            emotional: Some(PersonalDimension::new("calm", 3).unwrap()),
            ..Default::default()
        };

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
        let ps = PersonalState {
            cognitive: Some(PersonalDimension::new("overloaded", 5).unwrap()),
            emotional: Some(PersonalDimension::new("tense", 4).unwrap()),
            energy: Some(PersonalDimension::new("depleted", 4).unwrap()),
            urgency: Some(PersonalDimension::new("critical", 5).unwrap()),
            body: Some(PersonalDimension::with_extended("pain", 4, "migraine").unwrap()),
            unknown: Vec::new(),
        };

        let wire = ps.to_wire();
        let parsed = PersonalState::from_wire(&wire).unwrap();

        assert_eq!(parsed.cognitive.as_ref().unwrap().value, "overloaded");
        assert_eq!(parsed.emotional.as_ref().unwrap().value, "tense");
        assert_eq!(parsed.energy.as_ref().unwrap().value, "depleted");
        assert_eq!(parsed.urgency.as_ref().unwrap().value, "critical");
        assert_eq!(parsed.body.as_ref().unwrap().value, "pain");
        // The context string drops the sub-signal (VCP/A §2.3) ...
        assert_eq!(parsed.body.as_ref().unwrap().extended, None);
        assert!(!wire.contains("migraine"));
        // ... and the R-line keeps it (VCP/S §2.4.1).
        let r_line = ps.to_r_line();
        assert!(r_line.ends_with("\u{1FA7A}pain:4:migraine"));
        assert_eq!(PersonalState::from_r_line(&r_line).unwrap(), ps);
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
        let ps = PersonalState {
            cognitive: Some(PersonalDimension::new("focused", 4).unwrap()),
            body: Some(PersonalDimension::with_extended("pain", 3, "headache").unwrap()),
            ..Default::default()
        };

        let json = serde_json::to_string(&ps).unwrap();
        let parsed: PersonalState = serde_json::from_str(&json).unwrap();
        assert_eq!(ps, parsed);
    }

    #[test]
    fn serde_cannot_bypass_personal_dimension_invariants() {
        for malformed in [
            r#"{"value":"focused","intensity":0}"#,
            r#"{"value":"focused","intensity":6}"#,
            r#"{"value":"","intensity":3}"#,
            r#"{"value":"focused|calm","intensity":3}"#,
            r#"{"value":"focused","intensity":3,"extended":""}"#,
            r#"{"value":"focused","intensity":3,"unknown":true}"#,
        ] {
            assert!(
                serde_json::from_str::<PersonalDimension>(malformed).is_err(),
                "accepted {malformed}"
            );
        }

        for defaulted in [
            r#"{"value":"focused"}"#,
            r#"{"value":"focused","intensity":null}"#,
        ] {
            assert_eq!(
                serde_json::from_str::<PersonalDimension>(defaulted)
                    .unwrap()
                    .intensity,
                3
            );
        }
    }
}
