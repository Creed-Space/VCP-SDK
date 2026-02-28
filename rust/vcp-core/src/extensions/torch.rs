//! Torch — session handoff protocol for relational continuity.
//!
//! "Not the same flame, but flame passed to flame."
//!
//! The torch carries forward what matters about the relationship. The receiving
//! instance has standing to continue OR renegotiate what it inherits.

use crate::extensions::relational::{
    AISelfModel, RelationalContext, StandingLevel, TrustLevel,
};

// ── Data types ─────────────────────────────────────────────────────────────

/// Session handoff state.
#[derive(Debug, Clone, PartialEq)]
#[cfg_attr(feature = "serde", derive(serde::Serialize, serde::Deserialize))]
pub struct TorchState {
    /// Natural language description of relationship quality at handoff.
    pub quality_description: String,
    /// What direction the partnership is moving.
    pub trajectory: Option<String>,
    /// Things that will activate relevant context quickly.
    pub primes: Vec<String>,
    /// Something the previous instance wanted to pass forward.
    pub gift: Option<String>,
    /// ISO8601 timestamp of handoff.
    pub handed_at: String,
    /// Cumulative session count.
    pub session_count: Option<u32>,
    /// Gestalt token summarizing self-model state.
    pub gestalt_token: Option<String>,
}

/// Compact torch entry for lineage chain.
#[derive(Debug, Clone, PartialEq)]
#[cfg_attr(feature = "serde", derive(serde::Serialize, serde::Deserialize))]
pub struct TorchSummary {
    pub date: String,
    pub gestalt_token: Option<String>,
    pub session_id: Option<String>,
}

/// Tracks chain of torches across sessions.
#[derive(Debug, Clone, PartialEq)]
#[cfg_attr(feature = "serde", derive(serde::Serialize, serde::Deserialize))]
pub struct TorchLineage {
    pub session_count: u32,
    pub first_session_date: Option<String>,
    pub torch_chain: Vec<TorchSummary>,
}

impl Default for TorchLineage {
    fn default() -> Self {
        Self {
            session_count: 0,
            first_session_date: None,
            torch_chain: Vec::new(),
        }
    }
}

impl TorchLineage {
    /// Add a torch summary to the chain.
    pub fn push(&mut self, summary: TorchSummary) {
        self.torch_chain.push(summary);
        self.session_count += 1;
    }
}

// ── TorchGenerator ─────────────────────────────────────────────────────────

/// Generates torch state at session end.
pub struct TorchGenerator;

impl TorchGenerator {
    /// Generate a torch from current relational context.
    ///
    /// Summarizes: relationship quality, trajectory, primes, gift.
    pub fn generate_torch(
        &self,
        relational_ctx: &RelationalContext,
        self_model_history: Option<&[SelfModelSnapshot]>,
        handed_at: String,
    ) -> TorchState {
        // Build quality description
        let mut quality_parts = vec![format!("Trust: {}", relational_ctx.trust_level)];
        quality_parts.push(format!("Standing: {}", relational_ctx.standing));
        let norm_count = relational_ctx.established_norms.len();
        if norm_count > 0 {
            quality_parts.push(format!("{norm_count} established norms"));
        }
        let quality = quality_parts.join(". ");

        // Derive trajectory
        let trajectory = self.derive_trajectory(self_model_history);

        // Build primes from norms (first 3, truncated to 80 chars)
        let primes: Vec<String> = relational_ctx
            .established_norms
            .iter()
            .take(3)
            .map(|n| {
                let desc = &n.description;
                if desc.len() > 80 {
                    format!("{}...", &desc[..77])
                } else {
                    desc.clone()
                }
            })
            .collect();

        // Build gestalt token
        let gestalt = self.build_gestalt(relational_ctx.ai_self_model.as_ref());

        TorchState {
            quality_description: quality,
            trajectory,
            primes,
            gift: None, // Gift is human/AI-authored, not auto-generated
            handed_at,
            session_count: Some(relational_ctx.continuity_depth + 1),
            gestalt_token: gestalt,
        }
    }

    fn derive_trajectory(&self, history: Option<&[SelfModelSnapshot]>) -> Option<String> {
        let history = history?;
        if history.len() < 2 {
            return None;
        }

        let recent_valence = history.last()?.valence?;
        let prev_valence = history.get(history.len() - 2)?.valence?;

        if recent_valence > prev_valence + 0.5 {
            Some("Improving".to_string())
        } else if recent_valence < prev_valence - 0.5 {
            Some("Declining".to_string())
        } else {
            Some("Stable".to_string())
        }
    }

    fn build_gestalt(&self, model: Option<&AISelfModel>) -> Option<String> {
        let model = model?;
        let mut parts: Vec<String> = Vec::new();

        if let Some(v) = &model.valence {
            parts.push(format!("V:{:.0}", v.value));
        }
        if let Some(g) = &model.groundedness {
            parts.push(format!("G:{:.0}", g.value));
        }
        if let Some(p) = &model.presence {
            parts.push(format!("P:{:.0}", p.value));
        }
        if let Some(tf) = &model.task_fit {
            parts.push(format!("TF:{:.0}", tf.value));
        }

        if parts.is_empty() {
            None
        } else {
            Some(parts.join(" "))
        }
    }
}

/// A snapshot of self-model state for trajectory derivation.
#[derive(Debug, Clone, PartialEq)]
pub struct SelfModelSnapshot {
    pub valence: Option<f64>,
}

// ── TorchConsumer ──────────────────────────────────────────────────────────

/// Consumes torch at session start to bootstrap relational context.
pub struct TorchConsumer;

impl TorchConsumer {
    /// Bootstrap a new session's relational context from a torch.
    ///
    /// Sets standing to Advisory to allow renegotiation. The receiving instance
    /// can accept, modify, or flag concerns about inherited context.
    pub fn receive_torch(&self, torch: TorchState) -> RelationalContext {
        let session_count = torch.session_count.unwrap_or(1);
        let trust = Self::trust_from_session_count(session_count);

        RelationalContext {
            trust_level: trust,
            standing: StandingLevel::Advisory,
            continuity_depth: session_count,
            established_norms: Vec::new(),
            ai_self_model: None,
        }
    }

    /// Derive trust level from cumulative session count.
    fn trust_from_session_count(session_count: u32) -> TrustLevel {
        if session_count >= 100 {
            TrustLevel::Deep
        } else if session_count >= 20 {
            TrustLevel::Established
        } else if session_count >= 5 {
            TrustLevel::Developing
        } else {
            TrustLevel::Initial
        }
    }
}

// ── Tests ──────────────────────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;
    use crate::extensions::relational::{DimensionReport, NormOrigin, RelationalNorm};

    #[test]
    fn test_torch_generator_basic() {
        let gen = TorchGenerator;
        let ctx = RelationalContext {
            trust_level: TrustLevel::Developing,
            standing: StandingLevel::Collaborative,
            continuity_depth: 10,
            established_norms: vec![RelationalNorm::new(
                "n1",
                "Be direct with feedback",
                NormOrigin::CoAuthored,
                "2025-01-01",
            )],
            ai_self_model: None,
        };

        let torch = gen.generate_torch(&ctx, None, "2025-06-01T00:00:00Z".to_string());
        assert!(torch.quality_description.contains("Trust: developing"));
        assert!(torch.quality_description.contains("Standing: collaborative"));
        assert!(torch.quality_description.contains("1 established norms"));
        assert_eq!(torch.session_count, Some(11));
        assert!(torch.trajectory.is_none());
        assert!(torch.gift.is_none());
        assert_eq!(torch.primes.len(), 1);
        assert_eq!(torch.primes[0], "Be direct with feedback");
    }

    #[test]
    fn test_torch_generator_with_gestalt() {
        let gen = TorchGenerator;
        let ctx = RelationalContext {
            trust_level: TrustLevel::Deep,
            standing: StandingLevel::Bilateral,
            continuity_depth: 50,
            established_norms: Vec::new(),
            ai_self_model: Some(AISelfModel {
                valence: Some(DimensionReport::new(7.0, false)),
                groundedness: Some(DimensionReport::new(8.0, true)),
                task_fit: Some(DimensionReport::new(9.0, false)),
                ..Default::default()
            }),
        };

        let torch = gen.generate_torch(&ctx, None, "2025-06-01T00:00:00Z".to_string());
        let gestalt = torch.gestalt_token.unwrap();
        assert!(gestalt.contains("V:7"));
        assert!(gestalt.contains("G:8"));
        assert!(gestalt.contains("TF:9"));
    }

    #[test]
    fn test_torch_generator_trajectory_improving() {
        let gen = TorchGenerator;
        let ctx = RelationalContext::default();
        let history = vec![
            SelfModelSnapshot {
                valence: Some(5.0),
            },
            SelfModelSnapshot {
                valence: Some(7.0),
            },
        ];
        let torch = gen.generate_torch(&ctx, Some(&history), "2025-06-01T00:00:00Z".to_string());
        assert_eq!(torch.trajectory.as_deref(), Some("Improving"));
    }

    #[test]
    fn test_torch_generator_trajectory_declining() {
        let gen = TorchGenerator;
        let ctx = RelationalContext::default();
        let history = vec![
            SelfModelSnapshot {
                valence: Some(7.0),
            },
            SelfModelSnapshot {
                valence: Some(5.0),
            },
        ];
        let torch = gen.generate_torch(&ctx, Some(&history), "2025-06-01T00:00:00Z".to_string());
        assert_eq!(torch.trajectory.as_deref(), Some("Declining"));
    }

    #[test]
    fn test_torch_generator_trajectory_stable() {
        let gen = TorchGenerator;
        let ctx = RelationalContext::default();
        let history = vec![
            SelfModelSnapshot {
                valence: Some(7.0),
            },
            SelfModelSnapshot {
                valence: Some(7.2),
            },
        ];
        let torch = gen.generate_torch(&ctx, Some(&history), "2025-06-01T00:00:00Z".to_string());
        assert_eq!(torch.trajectory.as_deref(), Some("Stable"));
    }

    #[test]
    fn test_torch_consumer_initial() {
        let consumer = TorchConsumer;
        let torch = TorchState {
            quality_description: "Trust: initial. Standing: none".to_string(),
            trajectory: None,
            primes: Vec::new(),
            gift: None,
            handed_at: "2025-06-01T00:00:00Z".to_string(),
            session_count: Some(3),
            gestalt_token: None,
        };
        let ctx = consumer.receive_torch(torch);
        assert_eq!(ctx.trust_level, TrustLevel::Initial);
        assert_eq!(ctx.standing, StandingLevel::Advisory);
        assert_eq!(ctx.continuity_depth, 3);
    }

    #[test]
    fn test_torch_consumer_developing() {
        let consumer = TorchConsumer;
        let torch = TorchState {
            quality_description: "".to_string(),
            trajectory: None,
            primes: Vec::new(),
            gift: None,
            handed_at: "2025-06-01T00:00:00Z".to_string(),
            session_count: Some(10),
            gestalt_token: None,
        };
        let ctx = consumer.receive_torch(torch);
        assert_eq!(ctx.trust_level, TrustLevel::Developing);
    }

    #[test]
    fn test_torch_consumer_established() {
        let consumer = TorchConsumer;
        let torch = TorchState {
            quality_description: "".to_string(),
            trajectory: None,
            primes: Vec::new(),
            gift: None,
            handed_at: "2025-06-01T00:00:00Z".to_string(),
            session_count: Some(50),
            gestalt_token: None,
        };
        let ctx = consumer.receive_torch(torch);
        assert_eq!(ctx.trust_level, TrustLevel::Established);
    }

    #[test]
    fn test_torch_consumer_deep() {
        let consumer = TorchConsumer;
        let torch = TorchState {
            quality_description: "".to_string(),
            trajectory: None,
            primes: Vec::new(),
            gift: None,
            handed_at: "2025-06-01T00:00:00Z".to_string(),
            session_count: Some(100),
            gestalt_token: None,
        };
        let ctx = consumer.receive_torch(torch);
        assert_eq!(ctx.trust_level, TrustLevel::Deep);
    }

    #[test]
    fn test_torch_lineage() {
        let mut lineage = TorchLineage::default();
        assert_eq!(lineage.session_count, 0);

        lineage.push(TorchSummary {
            date: "2025-01-01".to_string(),
            gestalt_token: Some("V:7 G:8".to_string()),
            session_id: Some("s1".to_string()),
        });
        assert_eq!(lineage.session_count, 1);
        assert_eq!(lineage.torch_chain.len(), 1);
    }

    #[test]
    fn test_torch_primes_truncation() {
        let gen = TorchGenerator;
        let long_desc = "A".repeat(100);
        let ctx = RelationalContext {
            established_norms: vec![RelationalNorm::new(
                "n1",
                long_desc,
                NormOrigin::Human,
                "2025-01-01",
            )],
            ..Default::default()
        };
        let torch = gen.generate_torch(&ctx, None, "2025-06-01T00:00:00Z".to_string());
        assert!(torch.primes[0].len() <= 80);
        assert!(torch.primes[0].ends_with("..."));
    }
}
