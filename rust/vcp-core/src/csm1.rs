//! CSM-1 (Constitutional Semantics Mark 1) parsing and encoding.
//!
//! CSM-1 has two forms:
//!
//! ## Compact code (inline)
//!
//! ```text
//! persona level *("+" scope) [":" namespace] ["@" version]
//! ```
//!
//! Examples: `N5+F+E`, `Z3+P:SEC`, `M2@1.0.0`
//!
//! ## 8-line token (full profile)
//!
//! ```text
//! Line 1: VCP:<version>:<profile-id>
//! Line 2: C:<constitution>@<version>
//! Line 3: P:<persona>:<adherence>
//! Line 4: G:<goal>:<experience>:<style>
//! Line 5: X:<constraints>
//! Line 6: F:<flags>
//! Line 7: S:<private-markers>
//! Line 8: R:<personal-state>     (optional, v1.1)
//! ```

use std::fmt;

use serde::{Deserialize, Serialize};

use crate::error::{VcpError, VcpResult};
use crate::personal::PersonalState;

// ── Persona ─────────────────────────────────────────────────

/// The eight archetypal personas for constitutional profiles.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum Persona {
    /// N -- Child safety specialist.
    Nanny,
    /// Z -- Security and privacy guardian.
    Sentinel,
    /// G -- Ethical guidance counselor.
    Godparent,
    /// A -- Professional conduct advisor.
    Ambassador,
    /// M -- Creativity enabler.
    Muse,
    /// R -- Factual accuracy enforcer.
    Anchor,
    /// H -- Minimal constraints (expert mode).
    HotRod,
    /// C -- User-defined persona.
    Custom,
}

impl Persona {
    /// Single-character code for this persona.
    pub fn code(self) -> char {
        match self {
            Self::Nanny => 'N',
            Self::Sentinel => 'Z',
            Self::Godparent => 'G',
            Self::Ambassador => 'A',
            Self::Muse => 'M',
            Self::Anchor => 'R',
            Self::HotRod => 'H',
            Self::Custom => 'C',
        }
    }

    /// Parse from a single character.
    pub fn from_char(c: char) -> VcpResult<Self> {
        match c.to_ascii_uppercase() {
            'N' => Ok(Self::Nanny),
            'Z' => Ok(Self::Sentinel),
            'G' => Ok(Self::Godparent),
            'A' => Ok(Self::Ambassador),
            'M' => Ok(Self::Muse),
            'R' => Ok(Self::Anchor),
            'H' => Ok(Self::HotRod),
            'C' => Ok(Self::Custom),
            _ => Err(VcpError::InvalidPersona(c)),
        }
    }

    /// Human-readable description.
    pub fn description(self) -> &'static str {
        match self {
            Self::Nanny => "Child safety specialist",
            Self::Sentinel => "Security and privacy guardian",
            Self::Godparent => "Ethical guidance counselor",
            Self::Ambassador => "Professional conduct advisor",
            Self::Muse => "Creativity enabler",
            Self::Anchor => "Factual accuracy enforcer",
            Self::HotRod => "Minimal constraints (expert mode)",
            Self::Custom => "User-defined persona",
        }
    }

    /// All persona variants.
    pub fn all() -> &'static [Persona] {
        &[
            Self::Nanny,
            Self::Sentinel,
            Self::Godparent,
            Self::Ambassador,
            Self::Muse,
            Self::Anchor,
            Self::HotRod,
            Self::Custom,
        ]
    }
}

impl fmt::Display for Persona {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.code())
    }
}

// ── Scope ───────────────────────────────────────────────────

/// Eleven context scopes for constitutional application.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum Scope {
    Family,
    Work,
    Education,
    Healthcare,
    Finance,
    Legal,
    Privacy,
    Safety,
    Accessibility,
    Environment,
    General,
}

impl Scope {
    /// Single-character code.
    pub fn code(self) -> char {
        match self {
            Self::Family => 'F',
            Self::Work => 'W',
            Self::Education => 'E',
            Self::Healthcare => 'H',
            Self::Finance => 'I',
            Self::Legal => 'L',
            Self::Privacy => 'P',
            Self::Safety => 'S',
            Self::Accessibility => 'A',
            Self::Environment => 'V',
            Self::General => 'G',
        }
    }

    /// Parse from a single character.
    pub fn from_char(c: char) -> VcpResult<Self> {
        match c.to_ascii_uppercase() {
            'F' => Ok(Self::Family),
            'W' => Ok(Self::Work),
            'E' => Ok(Self::Education),
            'H' => Ok(Self::Healthcare),
            'I' => Ok(Self::Finance),
            'L' => Ok(Self::Legal),
            'P' => Ok(Self::Privacy),
            'S' => Ok(Self::Safety),
            'A' => Ok(Self::Accessibility),
            'V' => Ok(Self::Environment),
            'G' => Ok(Self::General),
            _ => Err(VcpError::InvalidScope(c)),
        }
    }

    /// Human-readable description.
    pub fn description(self) -> &'static str {
        match self {
            Self::Family => "Family and parenting",
            Self::Work => "Professional workplace",
            Self::Education => "Learning and academic",
            Self::Healthcare => "Medical and health",
            Self::Finance => "Financial and investment",
            Self::Legal => "Legal and compliance",
            Self::Privacy => "Privacy and data protection",
            Self::Safety => "Physical safety",
            Self::Accessibility => "Accessibility and inclusion",
            Self::Environment => "Environmental",
            Self::General => "General purpose",
        }
    }
}

impl fmt::Display for Scope {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.code())
    }
}

// ── CSM-1 Compact Code ─────────────────────────────────────

/// Parsed CSM-1 compact code: `<persona><level>[+scopes][:namespace][@version]`.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct Csm1Code {
    pub persona: Persona,
    /// Adherence level 0-5 (0 = disabled, 5 = maximum).
    pub adherence_level: u8,
    pub scopes: Vec<Scope>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub namespace: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub version: Option<String>,
}

impl Csm1Code {
    /// Parse a compact CSM-1 code string.
    ///
    /// # Examples
    ///
    /// ```
    /// use vcp_core::csm1::{Csm1Code, Persona, Scope};
    ///
    /// let code = Csm1Code::parse("N5+F+E").unwrap();
    /// assert_eq!(code.persona, Persona::Nanny);
    /// assert_eq!(code.adherence_level, 5);
    /// assert_eq!(code.scopes, vec![Scope::Family, Scope::Education]);
    /// ```
    pub fn parse(raw: &str) -> VcpResult<Self> {
        if raw.is_empty() {
            return Err(VcpError::ParseError("CSM1 code cannot be empty".into()));
        }

        let upper = raw.to_uppercase();
        let chars: Vec<char> = upper.chars().collect();

        if chars.len() < 2 {
            return Err(VcpError::ParseError(format!("CSM1 code too short: {raw}")));
        }

        // Parse persona (first char).
        let persona = Persona::from_char(chars[0])?;

        // Parse level (second char).
        let level_char = chars[1];
        let adherence_level = level_char
            .to_digit(10)
            .and_then(|d| if d <= 5 { Some(d as u8) } else { None })
            .ok_or(VcpError::InvalidAdherence(
                level_char.to_digit(10).unwrap_or(255) as u8,
            ))?;

        // Remaining string after persona + level.
        let remaining = &upper[2..];

        // Split into parts: scopes (+X), namespace (:NS), version (@X.Y.Z).
        let mut scopes = Vec::new();

        // Extract version if present.
        let (before_version, version) = if let Some(at_idx) = remaining.find('@') {
            let v = &remaining[at_idx + 1..];
            // Validate version format.
            let parts: Vec<&str> = v.split('.').collect();
            if parts.len() != 3 || parts.iter().any(|p| p.parse::<u32>().is_err()) {
                return Err(VcpError::ParseError(format!("invalid version: {v}")));
            }
            (&remaining[..at_idx], Some(v.to_string()))
        } else {
            (remaining, None)
        };

        // Extract namespace if present.
        let (before_ns, namespace) = if let Some(colon_idx) = before_version.find(':') {
            let n = &before_version[colon_idx + 1..];
            if n.is_empty() || !n.chars().next().unwrap().is_ascii_uppercase() {
                return Err(VcpError::ParseError(format!(
                    "invalid namespace: {n}"
                )));
            }
            (&before_version[..colon_idx], Some(n.to_string()))
        } else {
            (before_version, None)
        };

        // Parse scopes from remaining (e.g. "+F+E+H").
        if !before_ns.is_empty() {
            for scope_str in before_ns.split('+') {
                if scope_str.is_empty() {
                    continue;
                }
                if scope_str.len() != 1 {
                    return Err(VcpError::ParseError(format!(
                        "invalid scope token: {scope_str}"
                    )));
                }
                let scope_char = scope_str.chars().next().unwrap();
                scopes.push(Scope::from_char(scope_char)?);
            }
        }

        Ok(Csm1Code {
            persona,
            adherence_level,
            scopes,
            namespace,
            version,
        })
    }

    /// Encode back to a compact CSM-1 string.
    pub fn encode(&self) -> String {
        let mut s = format!("{}{}", self.persona.code(), self.adherence_level);

        if !self.scopes.is_empty() {
            s.push('+');
            s.push_str(
                &self
                    .scopes
                    .iter()
                    .map(|sc| String::from(sc.code()))
                    .collect::<Vec<_>>()
                    .join("+"),
            );
        }

        if let Some(ref ns) = self.namespace {
            s.push(':');
            s.push_str(ns);
        }

        if let Some(ref ver) = self.version {
            s.push('@');
            s.push_str(ver);
        }

        s
    }

    /// Check if this code applies to a given scope.
    ///
    /// An empty scope list means the code applies to all contexts.
    pub fn applies_to(&self, scope: Scope) -> bool {
        self.scopes.is_empty() || self.scopes.contains(&scope)
    }

    /// Returns a new code with the given scopes.
    pub fn with_scopes(&self, scopes: Vec<Scope>) -> Self {
        Csm1Code {
            persona: self.persona,
            adherence_level: self.adherence_level,
            scopes,
            namespace: self.namespace.clone(),
            version: self.version.clone(),
        }
    }

    /// Returns a new code with the given adherence level.
    pub fn with_level(&self, level: u8) -> VcpResult<Self> {
        if level > 5 {
            return Err(VcpError::InvalidAdherence(level));
        }
        Ok(Csm1Code {
            persona: self.persona,
            adherence_level: level,
            scopes: self.scopes.clone(),
            namespace: self.namespace.clone(),
            version: self.version.clone(),
        })
    }

    /// Check if this code is active (level > 0).
    pub fn is_active(&self) -> bool {
        self.adherence_level > 0
    }

    /// Check if this code is at maximum adherence.
    pub fn is_maximum(&self) -> bool {
        self.adherence_level == 5
    }
}

impl fmt::Display for Csm1Code {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(&self.encode())
    }
}

// ── CSM-1 8-line Token ──────────────────────────────────────

/// Reference to a constitution with version.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct ConstitutionRef {
    pub id: String,
    pub version: String,
}

/// Goal context for line 4 of the 8-line token.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct GoalContext {
    pub goal: String,
    pub experience: String,
    pub style: String,
}

/// Constraint flag for line 5 of the 8-line token.
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct ConstraintFlag(pub String);

/// A full CSM-1 8-line token.
///
/// ```text
/// VCP:1.0:profile-123
/// C:family-safe@1.2.0
/// P:N:5
/// G:protect:guided:gentle
/// X:no-profanity,no-violence
/// F:coppa,gdpr
/// S:internal-marker
/// R:focused:4|calm:3
/// ```
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct Csm1Token {
    /// Protocol version (e.g. "1.0").
    pub version: String,
    /// Profile identifier.
    pub profile_id: String,
    /// Constitution reference.
    pub constitution: ConstitutionRef,
    /// Persona type.
    pub persona: Persona,
    /// Adherence level 1-5.
    pub adherence: u8,
    /// Goal context (line 4).
    #[serde(skip_serializing_if = "Option::is_none")]
    pub goal: Option<GoalContext>,
    /// Constraint flags (line 5).
    pub constraints: Vec<ConstraintFlag>,
    /// Feature flags (line 6).
    pub flags: Vec<String>,
    /// Private markers (line 7).
    pub private_markers: Vec<String>,
    /// Personal state (line 8, optional v1.1).
    #[serde(skip_serializing_if = "Option::is_none")]
    pub personal_state: Option<PersonalState>,
}

impl Csm1Token {
    /// Parse an 8-line CSM-1 token string.
    pub fn parse(raw: &str) -> VcpResult<Self> {
        let lines: Vec<&str> = raw.lines().collect();

        if lines.len() < 7 {
            return Err(VcpError::ParseError(format!(
                "CSM1 token requires at least 7 lines, got {}",
                lines.len()
            )));
        }

        // Line 1: VCP:<version>:<profile-id>
        let line1 = Self::strip_and_validate(lines[0], "VCP:")?;
        let (version, profile_id) = line1.split_once(':').ok_or_else(|| {
            VcpError::ParseError(format!("line 1 missing profile-id separator: {}", lines[0]))
        })?;

        // Line 2: C:<constitution>@<version>
        let line2 = Self::strip_and_validate(lines[1], "C:")?;
        let (const_id, const_ver) = line2.split_once('@').ok_or_else(|| {
            VcpError::ParseError(format!("line 2 missing version separator: {}", lines[1]))
        })?;

        // Line 3: P:<persona>:<adherence>
        let line3 = Self::strip_and_validate(lines[2], "P:")?;
        let (persona_str, adherence_str) = line3.split_once(':').ok_or_else(|| {
            VcpError::ParseError(format!(
                "line 3 missing adherence separator: {}",
                lines[2]
            ))
        })?;
        let persona_char = persona_str
            .chars()
            .next()
            .ok_or_else(|| VcpError::ParseError("empty persona in line 3".into()))?;
        let persona = Persona::from_char(persona_char)?;
        let adherence: u8 = adherence_str
            .parse()
            .map_err(|_| VcpError::ParseError(format!("invalid adherence: {adherence_str}")))?;
        if !(1..=5).contains(&adherence) {
            return Err(VcpError::InvalidAdherence(adherence));
        }

        // Line 4: G:<goal>:<experience>:<style>
        let line4 = Self::strip_and_validate(lines[3], "G:")?;
        let goal = if line4.is_empty() {
            None
        } else {
            let parts: Vec<&str> = line4.splitn(3, ':').collect();
            if parts.len() == 3 {
                Some(GoalContext {
                    goal: parts[0].to_string(),
                    experience: parts[1].to_string(),
                    style: parts[2].to_string(),
                })
            } else {
                // Partial goal -- still valid.
                Some(GoalContext {
                    goal: parts.first().unwrap_or(&"").to_string(),
                    experience: parts.get(1).unwrap_or(&"").to_string(),
                    style: parts.get(2).unwrap_or(&"").to_string(),
                })
            }
        };

        // Line 5: X:<constraints>
        let line5 = Self::strip_and_validate(lines[4], "X:")?;
        let constraints = if line5.is_empty() {
            Vec::new()
        } else {
            line5
                .split(',')
                .map(|s| ConstraintFlag(s.trim().to_string()))
                .collect()
        };

        // Line 6: F:<flags>
        let line6 = Self::strip_and_validate(lines[5], "F:")?;
        let flags = if line6.is_empty() {
            Vec::new()
        } else {
            line6
                .split(',')
                .map(|s| s.trim().to_string())
                .collect()
        };

        // Line 7: S:<private-markers>
        let line7 = Self::strip_and_validate(lines[6], "S:")?;
        let private_markers = if line7.is_empty() {
            Vec::new()
        } else {
            line7
                .split(',')
                .map(|s| s.trim().to_string())
                .collect()
        };

        // Line 8 (optional): R:<personal-state>
        let personal_state = if lines.len() > 7 {
            let line8 = Self::strip_and_validate(lines[7], "R:")?;
            if line8.is_empty() {
                None
            } else {
                Some(PersonalState::from_wire(line8)?)
            }
        } else {
            None
        };

        Ok(Csm1Token {
            version: version.to_string(),
            profile_id: profile_id.to_string(),
            constitution: ConstitutionRef {
                id: const_id.to_string(),
                version: const_ver.to_string(),
            },
            persona,
            adherence,
            goal,
            constraints,
            flags,
            private_markers,
            personal_state,
        })
    }

    /// Encode to 8-line (or 7-line) string.
    pub fn encode(&self) -> String {
        let mut lines = Vec::with_capacity(8);

        // Line 1
        lines.push(format!("VCP:{}:{}", self.version, self.profile_id));

        // Line 2
        lines.push(format!(
            "C:{}@{}",
            self.constitution.id, self.constitution.version
        ));

        // Line 3
        lines.push(format!("P:{}:{}", self.persona.code(), self.adherence));

        // Line 4
        if let Some(ref g) = self.goal {
            lines.push(format!("G:{}:{}:{}", g.goal, g.experience, g.style));
        } else {
            lines.push("G:".to_string());
        }

        // Line 5
        let constraints_str: Vec<&str> = self.constraints.iter().map(|c| c.0.as_str()).collect();
        lines.push(format!("X:{}", constraints_str.join(",")));

        // Line 6
        lines.push(format!("F:{}", self.flags.join(",")));

        // Line 7
        lines.push(format!("S:{}", self.private_markers.join(",")));

        // Line 8 (only if personal state is present)
        if let Some(ref ps) = self.personal_state {
            lines.push(format!("R:{}", ps.to_wire()));
        }

        lines.join("\n")
    }

    /// Helper: strip a required prefix from a line.
    fn strip_and_validate<'a>(line: &'a str, prefix: &str) -> VcpResult<&'a str> {
        line.strip_prefix(prefix).ok_or_else(|| {
            VcpError::ParseError(format!(
                "expected line to start with '{prefix}', got: {line}"
            ))
        })
    }
}

impl fmt::Display for Csm1Token {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(&self.encode())
    }
}

// ── Tests ───────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;
    use pretty_assertions::assert_eq;

    // ── Persona ─────────────────────────────────────────

    #[test]
    fn persona_from_char_all() {
        let cases = [
            ('N', Persona::Nanny),
            ('Z', Persona::Sentinel),
            ('G', Persona::Godparent),
            ('A', Persona::Ambassador),
            ('M', Persona::Muse),
            ('R', Persona::Anchor),
            ('H', Persona::HotRod),
            ('C', Persona::Custom),
        ];
        for (ch, expected) in &cases {
            assert_eq!(Persona::from_char(*ch).unwrap(), *expected);
        }
    }

    #[test]
    fn persona_from_char_lowercase() {
        assert_eq!(Persona::from_char('n').unwrap(), Persona::Nanny);
    }

    #[test]
    fn persona_from_char_invalid() {
        assert!(Persona::from_char('X').is_err());
    }

    #[test]
    fn persona_descriptions() {
        for p in Persona::all() {
            assert!(!p.description().is_empty());
        }
    }

    // ── Scope ───────────────────────────────────────────

    #[test]
    fn scope_from_char_all() {
        let cases = [
            ('F', Scope::Family),
            ('W', Scope::Work),
            ('E', Scope::Education),
            ('H', Scope::Healthcare),
            ('I', Scope::Finance),
            ('L', Scope::Legal),
            ('P', Scope::Privacy),
            ('S', Scope::Safety),
            ('A', Scope::Accessibility),
            ('V', Scope::Environment),
            ('G', Scope::General),
        ];
        for (ch, expected) in &cases {
            assert_eq!(Scope::from_char(*ch).unwrap(), *expected);
        }
    }

    #[test]
    fn scope_from_char_invalid() {
        assert!(Scope::from_char('X').is_err());
    }

    // ── Compact Code Parsing ────────────────────────────

    #[test]
    fn parse_simple() {
        let code = Csm1Code::parse("N5").unwrap();
        assert_eq!(code.persona, Persona::Nanny);
        assert_eq!(code.adherence_level, 5);
        assert!(code.scopes.is_empty());
        assert_eq!(code.namespace, None);
        assert_eq!(code.version, None);
    }

    #[test]
    fn parse_with_scopes() {
        let code = Csm1Code::parse("N5+F+E").unwrap();
        assert_eq!(code.scopes, vec![Scope::Family, Scope::Education]);
    }

    #[test]
    fn parse_with_namespace() {
        let code = Csm1Code::parse("Z3+P:SEC").unwrap();
        assert_eq!(code.persona, Persona::Sentinel);
        assert_eq!(code.adherence_level, 3);
        assert_eq!(code.scopes, vec![Scope::Privacy]);
        assert_eq!(code.namespace.as_deref(), Some("SEC"));
    }

    #[test]
    fn parse_with_version() {
        let code = Csm1Code::parse("M2@1.0.0").unwrap();
        assert_eq!(code.persona, Persona::Muse);
        assert_eq!(code.adherence_level, 2);
        assert_eq!(code.version.as_deref(), Some("1.0.0"));
    }

    #[test]
    fn parse_full() {
        let code = Csm1Code::parse("G4+F+E+H:ELEM@2.1.0").unwrap();
        assert_eq!(code.persona, Persona::Godparent);
        assert_eq!(code.adherence_level, 4);
        assert_eq!(
            code.scopes,
            vec![Scope::Family, Scope::Education, Scope::Healthcare]
        );
        assert_eq!(code.namespace.as_deref(), Some("ELEM"));
        assert_eq!(code.version.as_deref(), Some("2.1.0"));
    }

    #[test]
    fn parse_lowercase() {
        let code = Csm1Code::parse("n5+f+e").unwrap();
        assert_eq!(code.persona, Persona::Nanny);
        assert_eq!(code.scopes, vec![Scope::Family, Scope::Education]);
    }

    #[test]
    fn parse_all_personas() {
        for p in Persona::all() {
            let raw = format!("{}3", p.code());
            let code = Csm1Code::parse(&raw).unwrap();
            assert_eq!(code.persona, *p);
        }
    }

    #[test]
    fn parse_all_levels() {
        for level in 0..=5 {
            let raw = format!("N{level}");
            let code = Csm1Code::parse(&raw).unwrap();
            assert_eq!(code.adherence_level, level);
        }
    }

    // ── Compact Code Validation ─────────────────────────

    #[test]
    fn parse_empty() {
        assert!(Csm1Code::parse("").is_err());
    }

    #[test]
    fn parse_invalid_persona() {
        assert!(Csm1Code::parse("X5").is_err());
    }

    #[test]
    fn parse_invalid_level() {
        // Level 9 out of range.
        assert!(Csm1Code::parse("N9").is_err());
    }

    #[test]
    fn parse_invalid_scope() {
        assert!(Csm1Code::parse("N5+X").is_err());
    }

    #[test]
    fn parse_missing_level() {
        assert!(Csm1Code::parse("N").is_err());
    }

    // ── Compact Code Encoding ───────────────────────────

    #[test]
    fn encode_simple() {
        assert_eq!(Csm1Code::parse("N5").unwrap().encode(), "N5");
    }

    #[test]
    fn encode_with_scopes() {
        assert_eq!(Csm1Code::parse("N5+F+E").unwrap().encode(), "N5+F+E");
    }

    #[test]
    fn encode_with_namespace() {
        assert_eq!(Csm1Code::parse("Z3+P:SEC").unwrap().encode(), "Z3+P:SEC");
    }

    #[test]
    fn encode_with_version() {
        assert_eq!(Csm1Code::parse("M2@1.0.0").unwrap().encode(), "M2@1.0.0");
    }

    #[test]
    fn roundtrip_full() {
        let original = "G4+F+E+H:ELEM@2.1.0";
        assert_eq!(Csm1Code::parse(original).unwrap().encode(), original);
    }

    // ── Compact Code Methods ────────────────────────────

    #[test]
    fn applies_to_empty_scopes() {
        let code = Csm1Code::parse("N5").unwrap();
        assert!(code.applies_to(Scope::Family));
        assert!(code.applies_to(Scope::Work));
    }

    #[test]
    fn applies_to_specific_scopes() {
        let code = Csm1Code::parse("N5+F+E").unwrap();
        assert!(code.applies_to(Scope::Family));
        assert!(code.applies_to(Scope::Education));
        assert!(!code.applies_to(Scope::Work));
    }

    #[test]
    fn with_scopes() {
        let code1 = Csm1Code::parse("N5").unwrap();
        let code2 = code1.with_scopes(vec![Scope::Family, Scope::Work]);
        assert!(code1.scopes.is_empty());
        assert_eq!(code2.scopes, vec![Scope::Family, Scope::Work]);
    }

    #[test]
    fn with_level() {
        let code1 = Csm1Code::parse("N5").unwrap();
        let code2 = code1.with_level(3).unwrap();
        assert_eq!(code1.adherence_level, 5);
        assert_eq!(code2.adherence_level, 3);
    }

    #[test]
    fn with_level_invalid() {
        let code = Csm1Code::parse("N5").unwrap();
        assert!(code.with_level(6).is_err());
    }

    #[test]
    fn is_active() {
        assert!(!Csm1Code::parse("N0").unwrap().is_active());
        assert!(Csm1Code::parse("N1").unwrap().is_active());
        assert!(Csm1Code::parse("N5").unwrap().is_active());
    }

    #[test]
    fn is_maximum() {
        assert!(!Csm1Code::parse("N4").unwrap().is_maximum());
        assert!(Csm1Code::parse("N5").unwrap().is_maximum());
    }

    // ── 8-line Token ────────────────────────────────────

    const SAMPLE_TOKEN_7: &str = "\
VCP:1.0:profile-123
C:family-safe@1.2.0
P:N:5
G:protect:guided:gentle
X:no-profanity,no-violence
F:coppa,gdpr
S:internal-marker";

    const SAMPLE_TOKEN_8: &str = "\
VCP:1.1:profile-456
C:workplace@2.0.0
P:A:4
G:advise:professional:formal
X:no-discrimination
F:hipaa
S:audit-trail
R:\u{1F9E0}focused:4|\u{1F4AD}calm:3";

    #[test]
    fn parse_7_line_token() {
        let token = Csm1Token::parse(SAMPLE_TOKEN_7).unwrap();
        assert_eq!(token.version, "1.0");
        assert_eq!(token.profile_id, "profile-123");
        assert_eq!(token.constitution.id, "family-safe");
        assert_eq!(token.constitution.version, "1.2.0");
        assert_eq!(token.persona, Persona::Nanny);
        assert_eq!(token.adherence, 5);
        assert!(token.goal.is_some());
        let g = token.goal.as_ref().unwrap();
        assert_eq!(g.goal, "protect");
        assert_eq!(g.experience, "guided");
        assert_eq!(g.style, "gentle");
        assert_eq!(token.constraints.len(), 2);
        assert_eq!(token.constraints[0].0, "no-profanity");
        assert_eq!(token.flags, vec!["coppa", "gdpr"]);
        assert_eq!(token.private_markers, vec!["internal-marker"]);
        assert!(token.personal_state.is_none());
    }

    #[test]
    fn parse_8_line_token() {
        let token = Csm1Token::parse(SAMPLE_TOKEN_8).unwrap();
        assert_eq!(token.version, "1.1");
        assert_eq!(token.persona, Persona::Ambassador);
        assert_eq!(token.adherence, 4);
        assert!(token.personal_state.is_some());
        let ps = token.personal_state.as_ref().unwrap();
        assert_eq!(ps.cognitive.as_ref().unwrap().value, "focused");
        assert_eq!(ps.cognitive.as_ref().unwrap().intensity, 4);
        assert_eq!(ps.emotional.as_ref().unwrap().value, "calm");
    }

    #[test]
    fn token_roundtrip_7_line() {
        let token = Csm1Token::parse(SAMPLE_TOKEN_7).unwrap();
        let encoded = token.encode();
        let reparsed = Csm1Token::parse(&encoded).unwrap();
        assert_eq!(token, reparsed);
    }

    #[test]
    fn token_roundtrip_8_line() {
        let token = Csm1Token::parse(SAMPLE_TOKEN_8).unwrap();
        let encoded = token.encode();
        let reparsed = Csm1Token::parse(&encoded).unwrap();
        assert_eq!(token, reparsed);
    }

    #[test]
    fn token_too_few_lines() {
        assert!(Csm1Token::parse("VCP:1.0:id\nC:x@1.0.0").is_err());
    }

    #[test]
    fn token_bad_prefix() {
        let bad = SAMPLE_TOKEN_7.replace("VCP:", "BAD:");
        assert!(Csm1Token::parse(&bad).is_err());
    }

    #[test]
    fn token_invalid_adherence() {
        let bad = SAMPLE_TOKEN_7.replace("P:N:5", "P:N:9");
        assert!(Csm1Token::parse(&bad).is_err());
    }
}
