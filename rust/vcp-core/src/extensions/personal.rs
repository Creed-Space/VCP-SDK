//! Personal state signals for VCP v3.1.
//!
//! Provides categorical personal dimensions (cognitive state, emotional tone,
//! energy level, perceived urgency, body signals) with 1-5 intensity and
//! exponential/linear/step decay over time.

use std::fmt;
use std::time::SystemTime;

// ── Enums ──────────────────────────────────────────────────────────────────

/// The 5 personal state dimensions.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, serde::Serialize, serde::Deserialize)]
pub enum PersonalDimension {
    CognitiveState,
    EmotionalTone,
    EnergyLevel,
    PerceivedUrgency,
    BodySignals,
}

impl fmt::Display for PersonalDimension {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::CognitiveState => write!(f, "cognitive_state"),
            Self::EmotionalTone => write!(f, "emotional_tone"),
            Self::EnergyLevel => write!(f, "energy_level"),
            Self::PerceivedUrgency => write!(f, "perceived_urgency"),
            Self::BodySignals => write!(f, "body_signals"),
        }
    }
}

/// Source of a personal signal.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, serde::Serialize, serde::Deserialize)]
pub enum SignalSource {
    Declared,
    Inferred,
    InferredLocal,
    Preset,
    Decayed,
}

/// Lifecycle state for a personal dimension signal.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, serde::Serialize, serde::Deserialize)]
pub enum LifecycleState {
    /// Just declared (t=0).
    Set,
    /// Within fresh window, minimal decay.
    Active,
    /// Intensity actively declining.
    Decaying,
    /// Below usefulness threshold but above baseline.
    Stale,
    /// At baseline, effectively cleared.
    Expired,
}

/// Decay curve shapes.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, serde::Serialize, serde::Deserialize)]
pub enum DecayCurve {
    Exponential,
    Linear,
    Step,
}

// ── Structs ────────────────────────────────────────────────────────────────

/// A single personal state signal with category + intensity.
#[derive(Debug, Clone, PartialEq, serde::Serialize, serde::Deserialize)]
pub struct PersonalSignal {
    /// Categorical value (e.g., "focused", "calm").
    pub category: String,
    /// Signal intensity 1-5 (1=minimal, 5=strong).
    pub intensity: u8,
    /// How this signal was obtained.
    pub source: SignalSource,
    /// Confidence in this signal (0.0-1.0).
    pub confidence: f64,
    /// When signal was declared (for decay). Uses SystemTime.
    pub declared_at: Option<SystemTime>,
}

impl PersonalSignal {
    /// Create a new personal signal. Intensity is clamped to [1, 5].
    pub fn new(category: impl Into<String>, intensity: u8) -> Self {
        Self {
            category: category.into(),
            intensity: intensity.clamp(1, 5),
            source: SignalSource::Declared,
            confidence: 1.0,
            declared_at: None,
        }
    }

    /// Set the source of this signal.
    pub fn with_source(mut self, source: SignalSource) -> Self {
        self.source = source;
        self
    }

    /// Set the confidence of this signal.
    pub fn with_confidence(mut self, confidence: f64) -> Self {
        self.confidence = confidence.clamp(0.0, 1.0);
        self
    }

    /// Set the declaration time for decay.
    pub fn with_declared_at(mut self, at: SystemTime) -> Self {
        self.declared_at = Some(at);
        self
    }
}

/// Personal state context (5 dimensions).
#[derive(Debug, Clone, PartialEq, Default, serde::Serialize, serde::Deserialize)]
pub struct PersonalContext {
    pub cognitive_state: Option<PersonalSignal>,
    pub emotional_tone: Option<PersonalSignal>,
    pub energy_level: Option<PersonalSignal>,
    pub perceived_urgency: Option<PersonalSignal>,
    pub body_signals: Option<PersonalSignal>,
}

impl PersonalContext {
    /// Check if any personal signal is set.
    pub fn has_any_signal(&self) -> bool {
        self.cognitive_state.is_some()
            || self.emotional_tone.is_some()
            || self.energy_level.is_some()
            || self.perceived_urgency.is_some()
            || self.body_signals.is_some()
    }
}

/// A discrete intensity step for step-curve decay.
#[derive(Debug, Clone, PartialEq, serde::Serialize, serde::Deserialize)]
pub struct StepThreshold {
    /// Time after declaration when this step activates.
    pub after_seconds: f64,
    /// The intensity value for this step.
    pub intensity: u8,
}

/// Configuration for signal decay behavior.
#[derive(Debug, Clone, PartialEq, serde::Serialize, serde::Deserialize)]
pub struct DecayConfig {
    /// Half-life in seconds (for exponential decay).
    pub half_life_seconds: f64,
    /// Integer baseline (1 = signal clears).
    pub baseline: u8,
    /// Whether engagement resets the decay timer.
    pub reset_on_engagement: bool,
    /// Decay curve shape.
    pub curve: DecayCurve,
    /// Fraction of declared intensity marking staleness.
    pub stale_threshold: f64,
    /// Seconds in ACTIVE before DECAYING.
    pub fresh_window_seconds: f64,
    /// Whether this signal is pinned (never decays).
    pub pinned: bool,
    /// For linear curve: total seconds until fully decayed.
    pub full_decay_seconds: Option<f64>,
    /// For step curve: discrete intensity thresholds.
    pub step_thresholds: Vec<StepThreshold>,
}

impl DecayConfig {
    /// Create a new exponential decay config with the given half-life.
    pub fn exponential(half_life_seconds: f64) -> Self {
        Self {
            half_life_seconds,
            baseline: 1,
            reset_on_engagement: false,
            curve: DecayCurve::Exponential,
            stale_threshold: 0.3,
            fresh_window_seconds: 60.0,
            pinned: false,
            full_decay_seconds: None,
            step_thresholds: Vec::new(),
        }
    }

    /// Create a linear decay config.
    pub fn linear(full_decay_seconds: f64) -> Self {
        Self {
            half_life_seconds: 0.0,
            baseline: 1,
            reset_on_engagement: false,
            curve: DecayCurve::Linear,
            stale_threshold: 0.3,
            fresh_window_seconds: 60.0,
            pinned: false,
            full_decay_seconds: Some(full_decay_seconds),
            step_thresholds: Vec::new(),
        }
    }

    /// Set the baseline intensity.
    pub fn with_baseline(mut self, baseline: u8) -> Self {
        self.baseline = baseline;
        self
    }

    /// Set the reset-on-engagement flag.
    pub fn with_reset_on_engagement(mut self, reset: bool) -> Self {
        self.reset_on_engagement = reset;
        self
    }

    /// Set the pinned flag.
    pub fn with_pinned(mut self, pinned: bool) -> Self {
        self.pinned = pinned;
        self
    }
}

// ── Default decay configs per dimension ────────────────────────────────────

/// Returns the default decay configuration for a given personal dimension.
pub fn default_decay_config(dim: PersonalDimension) -> DecayConfig {
    match dim {
        PersonalDimension::PerceivedUrgency => DecayConfig::exponential(900.0), // 15 min
        PersonalDimension::BodySignals => DecayConfig::exponential(14400.0),    // 4 hours
        PersonalDimension::CognitiveState => {
            DecayConfig::exponential(720.0).with_reset_on_engagement(true) // 12 min
        }
        PersonalDimension::EmotionalTone => DecayConfig::exponential(1800.0), // 30 min
        PersonalDimension::EnergyLevel => DecayConfig::exponential(7200.0),   // 2 hours
    }
}

// ── Decay computation ──────────────────────────────────────────────────────

/// Compute decayed intensity using exponential decay.
///
/// result = max(baseline, floor(baseline + (declared - baseline) * exp(-lambda * t)))
///
/// When intensity decays to baseline (1), the signal effectively clears.
pub fn compute_decayed_intensity(
    declared_intensity: u8,
    declared_at: SystemTime,
    config: &DecayConfig,
    now: SystemTime,
) -> u8 {
    if config.pinned {
        return declared_intensity;
    }

    let elapsed = match now.duration_since(declared_at) {
        Ok(d) => d.as_secs_f64(),
        Err(_) => return declared_intensity, // now is before declared_at
    };

    if elapsed <= 0.0 {
        return declared_intensity;
    }

    match config.curve {
        DecayCurve::Exponential => {
            if declared_intensity <= config.baseline {
                return config.baseline;
            }
            let lambda = (2.0_f64).ln() / config.half_life_seconds;
            let decayed = f64::from(config.baseline)
                + f64::from(declared_intensity.saturating_sub(config.baseline))
                    * (-lambda * elapsed).exp();
            let floored = decayed.floor() as u8;
            floored.max(config.baseline)
        }
        DecayCurve::Linear => {
            let full_decay = match config.full_decay_seconds {
                Some(fd) if fd > 0.0 => fd,
                _ => return declared_intensity,
            };
            if declared_intensity <= config.baseline {
                return config.baseline;
            }
            let fraction = (elapsed / full_decay).min(1.0);
            let decayed = f64::from(declared_intensity)
                - f64::from(declared_intensity.saturating_sub(config.baseline)) * fraction;
            let floored = decayed.floor() as u8;
            floored.max(config.baseline)
        }
        DecayCurve::Step => {
            if config.step_thresholds.is_empty() {
                return declared_intensity;
            }
            // Sort thresholds descending by after_seconds, pick the first that applies.
            let mut sorted: Vec<&StepThreshold> = config.step_thresholds.iter().collect();
            sorted.sort_by(|a, b| b.after_seconds.partial_cmp(&a.after_seconds).unwrap());
            for threshold in &sorted {
                if elapsed >= threshold.after_seconds {
                    return threshold.intensity.max(config.baseline);
                }
            }
            declared_intensity
        }
    }
}

/// Compute the lifecycle state for a personal dimension signal.
pub fn compute_lifecycle_state(
    declared_intensity: u8,
    declared_at: SystemTime,
    config: &DecayConfig,
    now: SystemTime,
) -> LifecycleState {
    if config.pinned {
        return LifecycleState::Active;
    }

    let elapsed = match now.duration_since(declared_at) {
        Ok(d) => d.as_secs_f64(),
        Err(_) => return LifecycleState::Set,
    };

    if elapsed <= 0.0 {
        return LifecycleState::Set;
    }

    if elapsed < config.fresh_window_seconds {
        return LifecycleState::Active;
    }

    let effective = compute_decayed_intensity(declared_intensity, declared_at, config, now);

    if effective <= config.baseline {
        return LifecycleState::Expired;
    }

    let stale_level = f64::from(config.baseline)
        + f64::from(declared_intensity - config.baseline) * config.stale_threshold;

    if f64::from(effective) <= stale_level {
        LifecycleState::Stale
    } else {
        LifecycleState::Decaying
    }
}

// ── Tests ──────────────────────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;
    use std::time::Duration;

    fn time_plus_secs(base: SystemTime, secs: f64) -> SystemTime {
        base + Duration::from_secs_f64(secs)
    }

    #[test]
    fn test_personal_signal_clamps_intensity() {
        let sig = PersonalSignal::new("focused", 0);
        assert_eq!(sig.intensity, 1);
        let sig = PersonalSignal::new("focused", 10);
        assert_eq!(sig.intensity, 5);
        let sig = PersonalSignal::new("focused", 3);
        assert_eq!(sig.intensity, 3);
    }

    #[test]
    fn test_personal_context_has_any_signal() {
        let ctx = PersonalContext::default();
        assert!(!ctx.has_any_signal());

        let ctx = PersonalContext {
            cognitive_state: Some(PersonalSignal::new("focused", 3)),
            ..Default::default()
        };
        assert!(ctx.has_any_signal());
    }

    #[test]
    fn test_exponential_decay_no_elapsed() {
        let config = DecayConfig::exponential(900.0);
        let now = SystemTime::now();
        let result = compute_decayed_intensity(5, now, &config, now);
        assert_eq!(result, 5);
    }

    #[test]
    fn test_exponential_decay_one_half_life() {
        let config = DecayConfig::exponential(900.0);
        let base = SystemTime::now();
        let now = time_plus_secs(base, 900.0);
        // declared=5, baseline=1, after 1 half-life:
        // 1 + (5-1) * 0.5 = 1 + 2.0 = 3.0 -> floor = 3
        let result = compute_decayed_intensity(5, base, &config, now);
        assert_eq!(result, 3);
    }

    #[test]
    fn test_exponential_decay_many_half_lives() {
        let config = DecayConfig::exponential(900.0);
        let base = SystemTime::now();
        let now = time_plus_secs(base, 9000.0); // 10 half-lives
        let result = compute_decayed_intensity(5, base, &config, now);
        assert_eq!(result, 1); // should be at baseline
    }

    #[test]
    fn test_pinned_never_decays() {
        let config = DecayConfig::exponential(900.0).with_pinned(true);
        let base = SystemTime::now();
        let now = time_plus_secs(base, 99999.0);
        let result = compute_decayed_intensity(5, base, &config, now);
        assert_eq!(result, 5);
    }

    #[test]
    fn test_linear_decay() {
        let config = DecayConfig::linear(100.0);
        let base = SystemTime::now();
        // At 50% through: 5 - (5-1)*0.5 = 5 - 2 = 3
        let now = time_plus_secs(base, 50.0);
        let result = compute_decayed_intensity(5, base, &config, now);
        assert_eq!(result, 3);
    }

    #[test]
    fn test_linear_decay_fully_elapsed() {
        let config = DecayConfig::linear(100.0);
        let base = SystemTime::now();
        let now = time_plus_secs(base, 200.0);
        let result = compute_decayed_intensity(5, base, &config, now);
        assert_eq!(result, 1);
    }

    #[test]
    fn test_step_decay() {
        let config = DecayConfig {
            half_life_seconds: 0.0,
            baseline: 1,
            reset_on_engagement: false,
            curve: DecayCurve::Step,
            stale_threshold: 0.3,
            fresh_window_seconds: 60.0,
            pinned: false,
            full_decay_seconds: None,
            step_thresholds: vec![
                StepThreshold {
                    after_seconds: 60.0,
                    intensity: 4,
                },
                StepThreshold {
                    after_seconds: 120.0,
                    intensity: 3,
                },
                StepThreshold {
                    after_seconds: 300.0,
                    intensity: 1,
                },
            ],
        };
        let base = SystemTime::now();

        // Before first threshold
        assert_eq!(
            compute_decayed_intensity(5, base, &config, time_plus_secs(base, 30.0)),
            5
        );
        // After first threshold
        assert_eq!(
            compute_decayed_intensity(5, base, &config, time_plus_secs(base, 90.0)),
            4
        );
        // After second threshold
        assert_eq!(
            compute_decayed_intensity(5, base, &config, time_plus_secs(base, 200.0)),
            3
        );
        // After third threshold
        assert_eq!(
            compute_decayed_intensity(5, base, &config, time_plus_secs(base, 500.0)),
            1
        );
    }

    #[test]
    fn test_lifecycle_state_set() {
        let config = DecayConfig::exponential(900.0);
        let now = SystemTime::now();
        let state = compute_lifecycle_state(5, now, &config, now);
        assert_eq!(state, LifecycleState::Set);
    }

    #[test]
    fn test_lifecycle_state_active() {
        let config = DecayConfig::exponential(900.0);
        let base = SystemTime::now();
        let now = time_plus_secs(base, 30.0); // within 60s fresh window
        let state = compute_lifecycle_state(5, base, &config, now);
        assert_eq!(state, LifecycleState::Active);
    }

    #[test]
    fn test_lifecycle_state_expired() {
        let config = DecayConfig::exponential(900.0);
        let base = SystemTime::now();
        let now = time_plus_secs(base, 99999.0);
        let state = compute_lifecycle_state(5, base, &config, now);
        assert_eq!(state, LifecycleState::Expired);
    }

    #[test]
    fn test_lifecycle_state_pinned() {
        let config = DecayConfig::exponential(900.0).with_pinned(true);
        let base = SystemTime::now();
        let now = time_plus_secs(base, 99999.0);
        let state = compute_lifecycle_state(5, base, &config, now);
        assert_eq!(state, LifecycleState::Active);
    }

    #[test]
    fn test_default_decay_configs() {
        let urg = default_decay_config(PersonalDimension::PerceivedUrgency);
        assert!((urg.half_life_seconds - 900.0).abs() < f64::EPSILON);
        assert!(!urg.reset_on_engagement);

        let cog = default_decay_config(PersonalDimension::CognitiveState);
        assert!((cog.half_life_seconds - 720.0).abs() < f64::EPSILON);
        assert!(cog.reset_on_engagement);

        let body = default_decay_config(PersonalDimension::BodySignals);
        assert!((body.half_life_seconds - 14400.0).abs() < f64::EPSILON);
    }

    #[test]
    fn test_personal_dimension_display() {
        assert_eq!(
            PersonalDimension::CognitiveState.to_string(),
            "cognitive_state"
        );
        assert_eq!(PersonalDimension::BodySignals.to_string(), "body_signals");
    }
}
