//! Relational context models for VCP v3.1.
//!
//! Partnership-level relational context layer. Distinct from user state and
//! AI state — this is about the relationship itself: trust, standing, norms,
//! self-model, and session continuity.

use std::collections::HashMap;
use std::fmt;

// ── Enums ──────────────────────────────────────────────────────────────────

/// Trust levels — established through behavior, not declared.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, serde::Serialize, serde::Deserialize)]
pub enum TrustLevel {
    Initial,
    Developing,
    Established,
    Deep,
}

impl fmt::Display for TrustLevel {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Initial => write!(f, "initial"),
            Self::Developing => write!(f, "developing"),
            Self::Established => write!(f, "established"),
            Self::Deep => write!(f, "deep"),
        }
    }
}

/// AI's standing in the partnership.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, serde::Serialize, serde::Deserialize)]
pub enum StandingLevel {
    None,
    Advisory,
    Collaborative,
    Bilateral,
}

impl fmt::Display for StandingLevel {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::None => write!(f, "none"),
            Self::Advisory => write!(f, "advisory"),
            Self::Collaborative => write!(f, "collaborative"),
            Self::Bilateral => write!(f, "bilateral"),
        }
    }
}

/// Who originated a relational norm.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, serde::Serialize, serde::Deserialize)]
pub enum NormOrigin {
    Human,
    Ai,
    CoAuthored,
    Inherited,
}

/// Direction of change since last self-model report.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, serde::Serialize, serde::Deserialize)]
pub enum TrendDirection {
    Rising,
    Stable,
    Falling,
    Unknown,
}

// ── Structs ────────────────────────────────────────────────────────────────

/// A single self-model dimension report.
///
/// The `uncertain` flag is REQUIRED. Any self-report without explicit
/// uncertainty marking is rejected as epistemically dishonest.
#[derive(Debug, Clone, PartialEq, serde::Serialize, serde::Deserialize)]
pub struct DimensionReport {
    /// Self-reported value on 1.0-9.0 scale.
    pub value: f64,
    /// Whether this dimension's value is uncertain. MUST be true for dimensions
    /// the AI cannot verify from inside.
    pub uncertain: bool,
    /// Human-readable description.
    pub label: Option<String>,
    /// Direction of change since last report.
    pub trend: Option<TrendDirection>,
}

impl DimensionReport {
    /// Create a new dimension report. Value is clamped to [1.0, 9.0].
    pub fn new(value: f64, uncertain: bool) -> Self {
        Self {
            value: value.clamp(1.0, 9.0),
            uncertain,
            label: None,
            trend: None,
        }
    }

    /// Set a label.
    #[must_use]
    pub fn with_label(mut self, label: impl Into<String>) -> Self {
        self.label = Some(label.into());
        self
    }

    /// Set a trend direction.
    #[must_use]
    pub fn with_trend(mut self, trend: TrendDirection) -> Self {
        self.trend = Some(trend);
        self
    }
}

/// AI self-model carried in relational context.
///
/// Design principles:
/// 1. Uncertainty markers are REQUIRED, not optional
/// 2. Negative states must be representable
/// 3. Custom dimensions are first-class
#[derive(Debug, Clone, PartialEq, Default, serde::Serialize, serde::Deserialize)]
pub struct AISelfModel {
    pub valence: Option<DimensionReport>,
    pub task_fit: Option<DimensionReport>,
    pub friction: Option<DimensionReport>,
    pub uncertainty: Option<DimensionReport>,
    pub groundedness: Option<DimensionReport>,
    pub presence: Option<DimensionReport>,
    pub depth: Option<DimensionReport>,
    pub custom_dimensions: HashMap<String, DimensionReport>,
    pub scaffold_version: Option<String>,
}

impl AISelfModel {
    /// Check that at least one dimension is marked as uncertain.
    /// A model where ALL dimensions claim certainty is epistemically dishonest.
    pub fn has_uncertainty_markers(&self) -> bool {
        let core = [
            &self.valence,
            &self.task_fit,
            &self.friction,
            &self.uncertainty,
            &self.groundedness,
            &self.presence,
            &self.depth,
        ];

        let active_core: Vec<&DimensionReport> = core.iter().filter_map(|d| d.as_ref()).collect();
        let active_custom: Vec<&DimensionReport> = self.custom_dimensions.values().collect();

        let all_active: Vec<&DimensionReport> =
            active_core.into_iter().chain(active_custom).collect();

        if all_active.is_empty() {
            return true; // No dimensions = vacuously true
        }

        all_active.iter().any(|d| d.uncertain)
    }

    /// Get all active dimensions as a flat map.
    pub fn get_all_dimensions(&self) -> HashMap<String, &DimensionReport> {
        let mut result = HashMap::new();
        let named = [
            ("valence", &self.valence),
            ("task_fit", &self.task_fit),
            ("friction", &self.friction),
            ("uncertainty", &self.uncertainty),
            ("groundedness", &self.groundedness),
            ("presence", &self.presence),
            ("depth", &self.depth),
        ];
        for (name, dim) in &named {
            if let Some(d) = dim {
                result.insert((*name).to_string(), d);
            }
        }
        for (name, dim) in &self.custom_dimensions {
            result.insert(name.clone(), dim);
        }
        result
    }
}

/// A norm established through the partnership's practice.
#[derive(Debug, Clone, PartialEq, serde::Serialize, serde::Deserialize)]
pub struct RelationalNorm {
    pub norm_id: String,
    pub description: String,
    pub origin: NormOrigin,
    pub established_date: String,
    pub last_exercised: Option<String>,
    /// 0.0 = fully established, 1.0 = provisional/uncertain.
    pub uncertainty: f64,
    pub active: bool,
}

impl RelationalNorm {
    pub fn new(
        norm_id: impl Into<String>,
        description: impl Into<String>,
        origin: NormOrigin,
        established_date: impl Into<String>,
    ) -> Self {
        Self {
            norm_id: norm_id.into(),
            description: description.into(),
            origin,
            established_date: established_date.into(),
            last_exercised: None,
            uncertainty: 0.0,
            active: true,
        }
    }
}

/// VCP relational context — the state of the partnership itself.
#[derive(Debug, Clone, PartialEq, serde::Serialize, serde::Deserialize)]
pub struct RelationalContext {
    pub trust_level: TrustLevel,
    pub standing: StandingLevel,
    pub continuity_depth: u32,
    pub established_norms: Vec<RelationalNorm>,
    pub ai_self_model: Option<AISelfModel>,
}

impl Default for RelationalContext {
    fn default() -> Self {
        Self {
            trust_level: TrustLevel::Initial,
            standing: StandingLevel::None,
            continuity_depth: 0,
            established_norms: Vec::new(),
            ai_self_model: None,
        }
    }
}

// ── Tests ──────────────────────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_trust_level_display() {
        assert_eq!(TrustLevel::Initial.to_string(), "initial");
        assert_eq!(TrustLevel::Deep.to_string(), "deep");
    }

    #[test]
    fn test_standing_level_display() {
        assert_eq!(StandingLevel::None.to_string(), "none");
        assert_eq!(StandingLevel::Bilateral.to_string(), "bilateral");
    }

    #[test]
    fn test_dimension_report_clamps() {
        let d = DimensionReport::new(0.0, true);
        assert!((d.value - 1.0).abs() < f64::EPSILON);
        let d = DimensionReport::new(10.0, false);
        assert!((d.value - 9.0).abs() < f64::EPSILON);
    }

    #[test]
    fn test_ai_self_model_uncertainty_vacuously_true() {
        let model = AISelfModel::default();
        assert!(model.has_uncertainty_markers());
    }

    #[test]
    fn test_ai_self_model_no_uncertainty_markers() {
        let model = AISelfModel {
            valence: Some(DimensionReport::new(7.0, false)),
            task_fit: Some(DimensionReport::new(8.0, false)),
            ..Default::default()
        };
        assert!(!model.has_uncertainty_markers());
    }

    #[test]
    fn test_ai_self_model_has_uncertainty_markers() {
        let model = AISelfModel {
            valence: Some(DimensionReport::new(7.0, false)),
            task_fit: Some(DimensionReport::new(8.0, true)),
            ..Default::default()
        };
        assert!(model.has_uncertainty_markers());
    }

    #[test]
    fn test_ai_self_model_get_all_dimensions() {
        let mut custom = HashMap::new();
        custom.insert("flow".to_string(), DimensionReport::new(6.0, true));
        let model = AISelfModel {
            valence: Some(DimensionReport::new(7.0, false)),
            custom_dimensions: custom,
            ..Default::default()
        };
        let all = model.get_all_dimensions();
        assert_eq!(all.len(), 2);
        assert!(all.contains_key("valence"));
        assert!(all.contains_key("flow"));
    }

    #[test]
    fn test_relational_context_default() {
        let ctx = RelationalContext::default();
        assert_eq!(ctx.trust_level, TrustLevel::Initial);
        assert_eq!(ctx.standing, StandingLevel::None);
        assert_eq!(ctx.continuity_depth, 0);
        assert!(ctx.established_norms.is_empty());
        assert!(ctx.ai_self_model.is_none());
    }

    #[test]
    fn test_relational_norm_creation() {
        let norm = RelationalNorm::new("n1", "Be direct", NormOrigin::CoAuthored, "2025-01-01");
        assert_eq!(norm.norm_id, "n1");
        assert!(norm.active);
        assert!((norm.uncertainty - 0.0).abs() < f64::EPSILON);
    }
}
