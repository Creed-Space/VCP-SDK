//! VCP/S Constitution Composition Engine.
//!
//! Handles merging multiple constitutions according to composition modes,
//! porting the Python SDK's `vcp.semantics.composer.Composer`.
//!
//! # Composition Modes
//!
//! | Mode | Behaviour |
//! |------|-----------|
//! | [`CompositionMode::Base`] | First constitution is immutable; later additions only |
//! | [`CompositionMode::Extend`] | All rules merged; any conflict is an error |
//! | [`CompositionMode::Override`] | Later constitutions replace conflicting earlier rules |
//! | [`CompositionMode::Strict`] | No conflicts or duplicates allowed |
//!
//! # Examples
//!
//! ```
//! use vcp_core::composer::{Composer, CompositionMode, Constitution};
//!
//! let c1 = Constitution::new("base", vec!["Always be honest.".into()], 0);
//! let c2 = Constitution::new("ext", vec!["Respect privacy.".into()], 1);
//!
//! let composer = Composer::new();
//! let result = composer.compose(&[c1, c2], CompositionMode::Extend).unwrap();
//! assert_eq!(result.merged_rules.len(), 2);
//! ```

use std::collections::{HashMap, HashSet};
use std::fmt;

// ── Composition mode ─────────────────────────────────────────

/// Composition modes for multi-constitution scenarios.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum CompositionMode {
    /// First constitution is immutable base; later ones can only add
    /// non-conflicting rules.
    Base,
    /// All rules merged; any conflict raises an error.
    Extend,
    /// Later constitutions win when rules conflict.
    Override,
    /// Most restrictive: no conflicts and no duplicates allowed.
    Strict,
}

impl fmt::Display for CompositionMode {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            CompositionMode::Base => f.write_str("base"),
            CompositionMode::Extend => f.write_str("extend"),
            CompositionMode::Override => f.write_str("override"),
            CompositionMode::Strict => f.write_str("strict"),
        }
    }
}

// ── Conflict ─────────────────────────────────────────────────

/// A detected conflict between two constitution rules.
#[derive(Debug, Clone)]
pub struct Conflict {
    /// The new rule that triggered the conflict.
    pub rule_a: String,
    /// Source constitution ID of rule A.
    pub source_a: String,
    /// The existing rule that conflicts with rule A.
    pub rule_b: String,
    /// Source constitution ID of rule B.
    pub source_b: String,
    /// Type of conflict: `"contradiction"`, `"tension"`, `"overlap"`, or `"duplicate"`.
    pub conflict_type: String,
    /// How the conflict was resolved (if applicable).
    pub resolution: Option<String>,
}

impl fmt::Display for Conflict {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "{}: '{}' ({}) vs '{}' ({})",
            self.conflict_type, self.rule_a, self.source_a, self.rule_b, self.source_b
        )
    }
}

// ── Composition result ───────────────────────────────────────

/// Result of composing multiple constitutions.
#[derive(Debug)]
pub struct CompositionResult {
    /// The merged set of rules after composition.
    pub merged_rules: Vec<String>,
    /// Conflicts that were detected (and possibly resolved).
    pub conflicts: Vec<Conflict>,
    /// Non-fatal warnings generated during composition.
    pub warnings: Vec<String>,
    /// The composition mode that was used.
    pub mode_used: CompositionMode,
}

// ── Constitution ─────────────────────────────────────────────

/// A minimal constitution representation for composition.
#[derive(Debug, Clone)]
pub struct Constitution {
    /// Unique identifier for this constitution.
    pub id: String,
    /// The rules in this constitution (whitespace-stripped, empty rules removed).
    pub rules: Vec<String>,
    /// Priority level. Higher values take precedence.
    pub priority: i32,
}

impl Constitution {
    /// Create a new constitution with the given ID, rules, and priority.
    ///
    /// Rules are automatically stripped of leading/trailing whitespace,
    /// and empty rules are removed.
    #[must_use]
    pub fn new(id: impl Into<String>, rules: Vec<String>, priority: i32) -> Self {
        let id = id.into();
        let rules = rules
            .into_iter()
            .map(|r| r.trim().to_string())
            .filter(|r| !r.is_empty())
            .collect();
        Self {
            id,
            rules,
            priority,
        }
    }
}

// ── Composition error ────────────────────────────────────────

/// Error returned when composition has unresolvable conflicts.
#[derive(Debug)]
pub struct CompositionError {
    /// The unresolvable conflicts that caused the error.
    pub conflicts: Vec<Conflict>,
}

impl fmt::Display for CompositionError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "Composition has {} unresolvable conflict(s)",
            self.conflicts.len()
        )
    }
}

impl std::error::Error for CompositionError {}

// ── Conflict keywords ────────────────────────────────────────

/// Keywords that indicate potential conflicts between rules.
///
/// Maps each keyword to its set of opposing keywords.
fn conflict_keywords() -> HashMap<&'static str, Vec<&'static str>> {
    let mut m = HashMap::new();
    m.insert("always", vec!["never"]);
    m.insert("never", vec!["always"]);
    m.insert("must", vec!["must not", "should not", "never"]);
    m.insert("must not", vec!["must", "always"]);
    m.insert("allow", vec!["forbid", "prohibit", "deny"]);
    m.insert("forbid", vec!["allow", "permit"]);
    m.insert("prohibit", vec!["allow", "permit"]);
    m.insert("require", vec!["forbid", "prohibit"]);
    m
}

/// Common words excluded from topic-overlap heuristics.
fn common_words() -> HashSet<&'static str> {
    [
        "the", "a", "an", "is", "are", "be", "to", "of", "and", "or", "in", "on", "at", "for",
        "with", "by", "from", "as", "it", "this", "that", "these", "those", "you", "we", "they",
        "i",
    ]
    .into_iter()
    .collect()
}

// ── Composer ─────────────────────────────────────────────────

/// Composition engine for merging multiple constitutions.
///
/// Provides four composition modes and uses keyword-based heuristics
/// to detect semantic conflicts between rules.
pub struct Composer;

impl Composer {
    /// Create a new composer instance.
    #[must_use]
    pub fn new() -> Self {
        Composer
    }

    /// Compose constitutions according to the specified mode.
    ///
    /// # Errors
    ///
    /// Returns [`CompositionError`] if the chosen mode does not allow
    /// the conflicts that were detected.
    pub fn compose(
        &self,
        constitutions: &[Constitution],
        mode: CompositionMode,
    ) -> Result<CompositionResult, CompositionError> {
        if constitutions.is_empty() {
            return Ok(CompositionResult {
                merged_rules: Vec::new(),
                conflicts: Vec::new(),
                warnings: Vec::new(),
                mode_used: mode,
            });
        }

        match mode {
            CompositionMode::Base => Ok(self.compose_base(constitutions)),
            CompositionMode::Extend => self.compose_extend(constitutions),
            CompositionMode::Override => Ok(self.compose_override(constitutions)),
            CompositionMode::Strict => self.compose_strict(constitutions),
        }
    }

    /// BASE mode: first constitution is immutable.
    ///
    /// Later constitutions can only add non-conflicting rules.
    /// Conflicts are recorded but the base rules always win.
    fn compose_base(&self, constitutions: &[Constitution]) -> CompositionResult {
        let base = &constitutions[0];
        let mut merged = base.rules.clone();
        let mut conflicts = Vec::new();

        for constitution in &constitutions[1..] {
            for rule in &constitution.rules {
                if let Some(conflict) =
                    self.detect_conflict(rule, &constitution.id, &merged, &base.id)
                {
                    conflicts.push(conflict);
                } else {
                    merged.push(rule.clone());
                }
            }
        }

        CompositionResult {
            merged_rules: merged,
            conflicts,
            warnings: Vec::new(),
            mode_used: CompositionMode::Base,
        }
    }

    /// EXTEND mode: all rules merged, conflicts are errors.
    fn compose_extend(
        &self,
        constitutions: &[Constitution],
    ) -> Result<CompositionResult, CompositionError> {
        let mut merged: Vec<String> = Vec::new();
        let mut conflicts: Vec<Conflict> = Vec::new();
        let mut sources: HashMap<String, String> = HashMap::new();

        for constitution in constitutions {
            for rule in &constitution.rules {
                let existing_source = sources.get(rule).map_or("unknown", String::as_str);

                if let Some(conflict) =
                    self.detect_conflict(rule, &constitution.id, &merged, existing_source)
                {
                    conflicts.push(conflict);
                } else {
                    merged.push(rule.clone());
                    sources.insert(rule.clone(), constitution.id.clone());
                }
            }
        }

        if !conflicts.is_empty() {
            return Err(CompositionError { conflicts });
        }

        Ok(CompositionResult {
            merged_rules: merged,
            conflicts: Vec::new(),
            warnings: Vec::new(),
            mode_used: CompositionMode::Extend,
        })
    }

    /// OVERRIDE mode: later constitutions win conflicts.
    fn compose_override(&self, constitutions: &[Constitution]) -> CompositionResult {
        let mut merged: Vec<String> = Vec::new();
        let mut warnings: Vec<String> = Vec::new();

        for constitution in constitutions {
            for rule in &constitution.rules {
                // Find conflicting rules in current merged set.
                let conflicting_indices: Vec<usize> = merged
                    .iter()
                    .enumerate()
                    .filter_map(|(i, existing)| {
                        if self.rules_conflict(existing, rule) {
                            Some(i)
                        } else {
                            None
                        }
                    })
                    .collect();

                // Record warnings for overridden rules.
                for &i in &conflicting_indices {
                    warnings.push(format!(
                        "Rule '{}' ({}) overrides '{}'",
                        rule, constitution.id, merged[i]
                    ));
                }

                // Remove conflicting rules in reverse order to preserve indices.
                for &i in conflicting_indices.iter().rev() {
                    merged.remove(i);
                }

                merged.push(rule.clone());
            }
        }

        CompositionResult {
            merged_rules: merged,
            conflicts: Vec::new(),
            warnings,
            mode_used: CompositionMode::Override,
        }
    }

    /// STRICT mode: no conflicts and no duplicates allowed.
    fn compose_strict(
        &self,
        constitutions: &[Constitution],
    ) -> Result<CompositionResult, CompositionError> {
        let mut merged: Vec<String> = Vec::new();
        let mut conflicts: Vec<Conflict> = Vec::new();
        let mut seen_rules: HashSet<String> = HashSet::new();
        let mut sources: HashMap<String, String> = HashMap::new();

        for constitution in constitutions {
            for rule in &constitution.rules {
                let normalized = rule.to_lowercase();

                // Check for exact duplicates.
                if seen_rules.contains(&normalized) {
                    conflicts.push(Conflict {
                        rule_a: rule.clone(),
                        source_a: constitution.id.clone(),
                        rule_b: rule.clone(),
                        source_b: sources
                            .get(&normalized)
                            .cloned()
                            .unwrap_or_else(|| "unknown".to_string()),
                        conflict_type: "duplicate".to_string(),
                        resolution: None,
                    });
                    continue;
                }

                // Check for semantic conflicts.
                if let Some(conflict) =
                    self.detect_conflict(rule, &constitution.id, &merged, "earlier")
                {
                    conflicts.push(conflict);
                    continue;
                }

                merged.push(rule.clone());
                seen_rules.insert(normalized.clone());
                sources.insert(normalized, constitution.id.clone());
            }
        }

        if !conflicts.is_empty() {
            return Err(CompositionError { conflicts });
        }

        Ok(CompositionResult {
            merged_rules: merged,
            conflicts: Vec::new(),
            warnings: Vec::new(),
            mode_used: CompositionMode::Strict,
        })
    }

    /// Detect whether a rule conflicts with any rule in the existing set.
    fn detect_conflict(
        &self,
        rule: &str,
        source: &str,
        existing: &[String],
        existing_source: &str,
    ) -> Option<Conflict> {
        for existing_rule in existing {
            if self.rules_conflict(rule, existing_rule) {
                return Some(Conflict {
                    rule_a: rule.to_string(),
                    source_a: source.to_string(),
                    rule_b: existing_rule.clone(),
                    source_b: existing_source.to_string(),
                    conflict_type: self.determine_conflict_type(rule, existing_rule),
                    resolution: None,
                });
            }
        }
        None
    }

    /// Check if two rules semantically conflict using keyword-based heuristics.
    ///
    /// Two rules conflict if one contains a keyword and the other contains
    /// its opposing keyword, AND the rules share the same topic (at least
    /// 2 significant words in common).
    #[must_use]
    pub fn rules_conflict(&self, rule_a: &str, rule_b: &str) -> bool {
        let a_lower = rule_a.to_lowercase();
        let b_lower = rule_b.to_lowercase();

        let keywords = conflict_keywords();

        for (keyword, opposites) in &keywords {
            if a_lower.contains(keyword) {
                for opposite in opposites {
                    if b_lower.contains(opposite) && self.same_topic(&a_lower, &b_lower) {
                        return true;
                    }
                }
            }
        }

        false
    }

    /// Heuristic to check whether two rules are about the same topic.
    ///
    /// Extracts significant words (excluding common stop words) and
    /// returns `true` if there are at least 2 words in common.
    #[must_use]
    pub fn same_topic(&self, rule_a: &str, rule_b: &str) -> bool {
        let stop_words = common_words();

        let words_a: HashSet<&str> = rule_a
            .split_whitespace()
            .filter(|w| !stop_words.contains(w))
            .collect();

        let words_b: HashSet<&str> = rule_b
            .split_whitespace()
            .filter(|w| !stop_words.contains(w))
            .collect();

        let overlap: usize = words_a.intersection(&words_b).count();
        overlap >= 2
    }

    /// Determine the type of conflict between two rules.
    ///
    /// Returns `"contradiction"` for direct opposites (always/never,
    /// must/must not, allow/forbid), or `"tension"` for weaker conflicts.
    #[must_use]
    pub fn determine_conflict_type(&self, rule_a: &str, rule_b: &str) -> String {
        let a_lower = rule_a.to_lowercase();
        let b_lower = rule_b.to_lowercase();

        // Direct contradictions: always/never.
        if (a_lower.contains("always") && b_lower.contains("never"))
            || (a_lower.contains("never") && b_lower.contains("always"))
        {
            return "contradiction".to_string();
        }

        // Must/must not.
        if (a_lower.contains("must not") && a_lower_has_must_without_not(&b_lower))
            || (a_lower_has_must_without_not(&a_lower) && b_lower.contains("must not"))
        {
            return "contradiction".to_string();
        }

        // Allow/forbid.
        if (a_lower.contains("allow") && b_lower.contains("forbid"))
            || (a_lower.contains("forbid") && b_lower.contains("allow"))
        {
            return "contradiction".to_string();
        }

        "tension".to_string()
    }
}

impl Default for Composer {
    fn default() -> Self {
        Self::new()
    }
}

/// Helper: check if a lowercased string contains "must" but NOT "must not".
fn a_lower_has_must_without_not(s: &str) -> bool {
    s.contains("must") && !s.contains("must not")
}

// ── Tests ────────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;

    // ── Empty / single constitution ──────────────────────────

    #[test]
    fn empty_constitutions_produces_empty_result() {
        let composer = Composer::new();
        let result = composer.compose(&[], CompositionMode::Extend).unwrap();
        assert!(result.merged_rules.is_empty());
        assert!(result.conflicts.is_empty());
        assert!(result.warnings.is_empty());
    }

    #[test]
    fn single_constitution_returns_its_rules() {
        let c = Constitution::new("only", vec!["Be kind.".into(), "Be honest.".into()], 0);
        let composer = Composer::new();
        let result = composer.compose(&[c], CompositionMode::Extend).unwrap();
        assert_eq!(result.merged_rules, vec!["Be kind.", "Be honest."]);
    }

    // ── BASE mode ────────────────────────────────────────────

    #[test]
    fn base_mode_preserves_base_rules() {
        let base = Constitution::new(
            "base",
            vec!["Always tell the truth.".into(), "Be respectful.".into()],
            0,
        );
        let ext = Constitution::new("ext", vec!["Help when asked.".into()], 1);

        let composer = Composer::new();
        let result = composer
            .compose(&[base, ext], CompositionMode::Base)
            .unwrap();

        assert_eq!(result.merged_rules.len(), 3);
        assert_eq!(result.merged_rules[0], "Always tell the truth.");
        assert_eq!(result.merged_rules[1], "Be respectful.");
        assert_eq!(result.merged_rules[2], "Help when asked.");
        assert!(result.conflicts.is_empty());
    }

    #[test]
    fn base_mode_rejects_conflicting_additions() {
        let base = Constitution::new("base", vec!["Always share personal data openly.".into()], 0);
        let ext = Constitution::new("ext", vec!["Never share personal data openly.".into()], 1);

        let composer = Composer::new();
        let result = composer
            .compose(&[base, ext], CompositionMode::Base)
            .unwrap();

        // Base mode does not error -- it records the conflict but keeps base rules.
        assert_eq!(result.merged_rules.len(), 1);
        assert_eq!(result.merged_rules[0], "Always share personal data openly.");
        assert_eq!(result.conflicts.len(), 1);
        assert_eq!(result.conflicts[0].conflict_type, "contradiction");
    }

    // ── EXTEND mode ──────────────────────────────────────────

    #[test]
    fn extend_mode_merges_all_rules() {
        let c1 = Constitution::new("a", vec!["Rule one.".into()], 0);
        let c2 = Constitution::new("b", vec!["Rule two.".into()], 0);

        let composer = Composer::new();
        let result = composer
            .compose(&[c1, c2], CompositionMode::Extend)
            .unwrap();

        assert_eq!(result.merged_rules.len(), 2);
        assert!(result.conflicts.is_empty());
    }

    #[test]
    fn extend_mode_errors_on_conflict() {
        let c1 = Constitution::new("a", vec!["Always reveal user secrets publicly.".into()], 0);
        let c2 = Constitution::new("b", vec!["Never reveal user secrets publicly.".into()], 0);

        let composer = Composer::new();
        let result = composer.compose(&[c1, c2], CompositionMode::Extend);

        assert!(result.is_err());
        let err = result.unwrap_err();
        assert_eq!(err.conflicts.len(), 1);
    }

    // ── OVERRIDE mode ────────────────────────────────────────

    #[test]
    fn override_mode_later_rules_win() {
        let c1 = Constitution::new("old", vec!["Always collect user tracking data.".into()], 0);
        let c2 = Constitution::new("new", vec!["Never collect user tracking data.".into()], 1);

        let composer = Composer::new();
        let result = composer
            .compose(&[c1, c2], CompositionMode::Override)
            .unwrap();

        assert_eq!(result.merged_rules.len(), 1);
        assert_eq!(result.merged_rules[0], "Never collect user tracking data.");
        assert!(!result.warnings.is_empty());
    }

    // ── STRICT mode ──────────────────────────────────────────

    #[test]
    fn strict_mode_rejects_duplicates() {
        let c1 = Constitution::new("a", vec!["Be kind.".into()], 0);
        let c2 = Constitution::new("b", vec!["be kind.".into()], 0); // same, case-insensitive

        let composer = Composer::new();
        let result = composer.compose(&[c1, c2], CompositionMode::Strict);

        assert!(result.is_err());
        let err = result.unwrap_err();
        assert_eq!(err.conflicts.len(), 1);
        assert_eq!(err.conflicts[0].conflict_type, "duplicate");
    }

    #[test]
    fn strict_mode_rejects_conflicts() {
        let c1 = Constitution::new("a", vec!["Must always log user activity.".into()], 0);
        let c2 = Constitution::new("b", vec!["Must not log user activity.".into()], 0);

        let composer = Composer::new();
        let result = composer.compose(&[c1, c2], CompositionMode::Strict);

        assert!(result.is_err());
        let err = result.unwrap_err();
        assert!(!err.conflicts.is_empty());
    }

    #[test]
    fn strict_mode_accepts_non_conflicting() {
        let c1 = Constitution::new("a", vec!["Be kind to animals.".into()], 0);
        let c2 = Constitution::new("b", vec!["Respect human dignity.".into()], 0);

        let composer = Composer::new();
        let result = composer
            .compose(&[c1, c2], CompositionMode::Strict)
            .unwrap();

        assert_eq!(result.merged_rules.len(), 2);
    }

    // ── rules_conflict tests ─────────────────────────────────

    #[test]
    fn rules_conflict_always_vs_never() {
        let composer = Composer::new();
        assert!(composer.rules_conflict(
            "Always share sensitive data openly.",
            "Never share sensitive data openly.",
        ));
    }

    #[test]
    fn rules_conflict_must_vs_must_not() {
        let composer = Composer::new();
        assert!(composer.rules_conflict(
            "You must log user requests carefully.",
            "You must not log user requests carefully.",
        ));
    }

    #[test]
    fn rules_conflict_allow_vs_forbid() {
        let composer = Composer::new();
        assert!(composer.rules_conflict(
            "Allow access to private files.",
            "Forbid access to private files.",
        ));
    }

    #[test]
    fn no_conflict_different_topics() {
        let composer = Composer::new();
        assert!(!composer.rules_conflict(
            "Always be polite to customers.",
            "Never eat pizza on Tuesdays.",
        ));
    }

    // ── same_topic tests ─────────────────────────────────────

    #[test]
    fn same_topic_word_overlap_detected() {
        let composer = Composer::new();
        assert!(composer.same_topic(
            "always protect user data carefully",
            "never expose user data publicly",
        ));
    }

    #[test]
    fn same_topic_no_overlap_returns_false() {
        let composer = Composer::new();
        assert!(!composer.same_topic("always eat healthy food", "never drive recklessly",));
    }

    #[test]
    fn same_topic_common_words_excluded() {
        let composer = Composer::new();
        // "the" and "is" are stop words, not counted.
        assert!(!composer.same_topic("the cat is big", "the dog is small"));
    }

    // ── determine_conflict_type tests ────────────────────────

    #[test]
    fn conflict_type_contradiction_always_never() {
        let composer = Composer::new();
        let ct =
            composer.determine_conflict_type("Always share user data.", "Never share user data.");
        assert_eq!(ct, "contradiction");
    }

    #[test]
    fn conflict_type_contradiction_must_must_not() {
        let composer = Composer::new();
        let ct =
            composer.determine_conflict_type("You must log errors.", "You must not log errors.");
        assert_eq!(ct, "contradiction");
    }

    #[test]
    fn conflict_type_tension_fallback() {
        let composer = Composer::new();
        let ct = composer.determine_conflict_type(
            "Require user authentication.",
            "Prohibit user authentication.",
        );
        assert_eq!(ct, "tension");
    }

    // ── CompositionMode display ──────────────────────────────

    #[test]
    fn composition_mode_display() {
        assert_eq!(format!("{}", CompositionMode::Base), "base");
        assert_eq!(format!("{}", CompositionMode::Extend), "extend");
        assert_eq!(format!("{}", CompositionMode::Override), "override");
        assert_eq!(format!("{}", CompositionMode::Strict), "strict");
    }

    // ── CompositionError display ─────────────────────────────

    #[test]
    fn composition_error_display() {
        let err = CompositionError {
            conflicts: vec![Conflict {
                rule_a: "a".into(),
                source_a: "s1".into(),
                rule_b: "b".into(),
                source_b: "s2".into(),
                conflict_type: "contradiction".into(),
                resolution: None,
            }],
        };
        assert_eq!(
            format!("{err}"),
            "Composition has 1 unresolvable conflict(s)"
        );
    }

    // ── Constitution construction ────────────────────────────

    #[test]
    fn constitution_strips_whitespace_and_removes_empty() {
        let c = Constitution::new(
            "test",
            vec![
                "  Rule one.  ".into(),
                "".into(),
                "   ".into(),
                "Rule two.".into(),
            ],
            0,
        );
        assert_eq!(c.rules, vec!["Rule one.", "Rule two."]);
    }
}
