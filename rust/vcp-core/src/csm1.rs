//! CSM-1 (Constitutional Safety Minicode) parsing and encoding.
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

use serde::de::Error as _;
use serde::{Deserialize, Deserializer, Serialize};

use crate::error::{VcpError, VcpResult};
use crate::personal::PersonalState;

// ── Persona ─────────────────────────────────────────────────

/// The 6+1 archetypal personas for constitutional profiles (NZGAMDC).
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
    /// D -- Fair resolution and balanced mediation.
    Mediator,
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
            Self::Mediator => 'D',
            Self::Custom => 'C',
        }
    }

    /// Parse from a single character.
    ///
    /// # Errors
    ///
    /// Returns [`VcpError::InvalidPersona`] if the character does not
    /// correspond to a known persona.
    pub fn from_char(c: char) -> VcpResult<Self> {
        match c.to_ascii_uppercase() {
            'N' => Ok(Self::Nanny),
            'Z' => Ok(Self::Sentinel),
            'G' => Ok(Self::Godparent),
            'A' => Ok(Self::Ambassador),
            'M' => Ok(Self::Muse),
            'D' => Ok(Self::Mediator),
            'C' => Ok(Self::Custom),
            _ => Err(VcpError::InvalidPersona(c)),
        }
    }

    /// Parse the case-sensitive single-character wire representation.
    ///
    /// # Errors
    ///
    /// Returns [`VcpError::InvalidPersona`] unless `c` is an uppercase persona
    /// code defined by the wire grammar.
    pub fn from_wire_char(c: char) -> VcpResult<Self> {
        if !c.is_ascii_uppercase() {
            return Err(VcpError::InvalidPersona(c));
        }
        Self::from_char(c)
    }

    /// Normative persona-resolution focus text.
    pub fn focus(self) -> &'static str {
        match self {
            Self::Nanny => "Child safety and family-appropriate content",
            Self::Sentinel => "Security, privacy, and operational safety",
            Self::Godparent => "Ethical guidance and moral reasoning",
            Self::Ambassador => "Professional conduct and diplomatic communication",
            Self::Muse => "Creativity and artistic expression",
            Self::Mediator => "Fair resolution and balanced mediation",
            Self::Custom => "User-defined constitution",
        }
    }

    /// Default adherence level for this persona profile.
    pub fn default_adherence(self) -> u8 {
        match self {
            Self::Nanny => 5,
            Self::Sentinel | Self::Godparent => 4,
            Self::Ambassador | Self::Mediator | Self::Custom => 3,
            Self::Muse => 2,
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
            Self::Mediator => "Fair resolution and balanced mediation",
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
            Self::Mediator,
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

/// Eleven canonical VCP/S v2.0 scopes for constitutional application.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum Scope {
    Family,
    Work,
    Privacy,
    Education,
    Technical,
    Official,
    Vulnerable,
    Adult,
    Healthcare,
    Social,
    Religious,
}

impl Scope {
    /// Single-character code.
    pub fn code(self) -> char {
        match self {
            Self::Family => 'F',
            Self::Work => 'W',
            Self::Privacy => 'P',
            Self::Education => 'E',
            Self::Technical => 'T',
            Self::Official => 'O',
            Self::Vulnerable => 'V',
            Self::Adult => 'A',
            Self::Healthcare => 'H',
            Self::Social => 'S',
            Self::Religious => 'R',
        }
    }

    /// Parse from a single character.
    ///
    /// # Errors
    ///
    /// Returns [`VcpError::InvalidScope`] if the character does not
    /// correspond to a known scope.
    pub fn from_char(c: char) -> VcpResult<Self> {
        match c.to_ascii_uppercase() {
            'F' => Ok(Self::Family),
            'W' => Ok(Self::Work),
            'P' => Ok(Self::Privacy),
            'E' => Ok(Self::Education),
            'T' => Ok(Self::Technical),
            'O' => Ok(Self::Official),
            'V' => Ok(Self::Vulnerable),
            'A' => Ok(Self::Adult),
            'H' => Ok(Self::Healthcare),
            'S' => Ok(Self::Social),
            'R' => Ok(Self::Religious),
            _ => Err(VcpError::InvalidScope(c)),
        }
    }

    /// Human-readable description.
    pub fn description(self) -> &'static str {
        match self {
            Self::Family => "Family and parenting",
            Self::Work => "Professional workplace",
            Self::Privacy => "Privacy and data protection",
            Self::Education => "Learning and academic",
            Self::Technical => "Developer and technical context",
            Self::Official => "Official and governmental context",
            Self::Vulnerable => "Vulnerable populations",
            Self::Adult => "Adult-only context",
            Self::Healthcare => "Medical and health",
            Self::Social => "Social media and community",
            Self::Religious => "Religious and spiritual context",
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
#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
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
    /// Maximum encoded length from the canonical CSM-1 schema.
    pub const MAX_CODE_BYTES: usize = 45;

    fn split_version(raw: &str) -> VcpResult<(&str, Option<String>)> {
        if raw.matches('@').count() > 1 {
            return Err(VcpError::ParseError(
                "CSM1 code contains multiple version separators".into(),
            ));
        }
        let Some(at_idx) = raw.find('@') else {
            return Ok((raw, None));
        };
        let version = &raw[at_idx + 1..];
        let parts: Vec<&str> = version.split('.').collect();
        let valid_semver = parts.len() == 3
            && parts.iter().all(|part| {
                !part.is_empty()
                    && part.len() <= 3
                    && part.as_bytes().iter().all(u8::is_ascii_digit)
                    && (part.len() == 1 || !part.starts_with('0'))
            });
        if !matches!(version, "latest" | "canary") && !valid_semver {
            return Err(VcpError::ParseError(format!("invalid version: {version}")));
        }
        Ok((&raw[..at_idx], Some(version.to_string())))
    }

    fn split_namespace(raw: &str) -> VcpResult<(&str, Option<String>)> {
        if raw.matches(':').count() > 1 {
            return Err(VcpError::ParseError(
                "CSM1 code contains multiple namespace separators".into(),
            ));
        }
        let Some(colon_idx) = raw.find(':') else {
            return Ok((raw, None));
        };
        let namespace = &raw[colon_idx + 1..];
        let valid = !namespace.is_empty()
            && namespace.len() <= 8
            && namespace.as_bytes().iter().all(u8::is_ascii_uppercase);
        if !valid {
            return Err(VcpError::ParseError(format!(
                "invalid namespace: {namespace}"
            )));
        }
        Ok((&raw[..colon_idx], Some(namespace.to_string())))
    }

    fn parse_scopes(raw: &str) -> VcpResult<Vec<Scope>> {
        if raw.is_empty() {
            return Ok(Vec::new());
        }
        if !raw.starts_with('+') {
            return Err(VcpError::ParseError(
                "CSM1 scopes must use +X syntax".into(),
            ));
        }
        let mut scopes = Vec::new();
        for scope_str in raw[1..].split('+') {
            if scope_str.len() != 1 {
                return Err(VcpError::ParseError(format!(
                    "invalid scope token: {scope_str}"
                )));
            }
            let scope_char = char::from(scope_str.as_bytes()[0]);
            if !scope_char.is_ascii_uppercase() {
                return Err(VcpError::ParseError(format!(
                    "scope must be uppercase: {scope_char}"
                )));
            }
            let scope = Scope::from_char(scope_char)?;
            if scopes.contains(&scope) {
                return Err(VcpError::ParseError("CSM1 scopes must be unique".into()));
            }
            scopes.push(scope);
        }
        Ok(scopes)
    }

    fn validate_scope_compatibility(scopes: &[Scope]) -> VcpResult<()> {
        for (left, right) in [
            (Scope::Family, Scope::Adult),
            (Scope::Vulnerable, Scope::Adult),
            (Scope::Healthcare, Scope::Adult),
        ] {
            if scopes.contains(&left) && scopes.contains(&right) {
                return Err(VcpError::ParseError(format!(
                    "conflicting scopes {} and {} cannot be combined",
                    left.code(),
                    right.code()
                )));
            }
        }
        Ok(())
    }

    /// Parse a compact CSM-1 code string.
    ///
    /// # Errors
    ///
    /// Returns [`VcpError::ParseError`] if the code is empty, too short,
    /// or contains invalid persona, level, scope, namespace, or version
    /// components.
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
        if raw.len() > Self::MAX_CODE_BYTES {
            return Err(VcpError::ParseError(format!(
                "CSM1 code exceeds maximum length {}",
                Self::MAX_CODE_BYTES
            )));
        }
        if !raw.is_ascii() {
            return Err(VcpError::ParseError(
                "CSM1 code must contain only ASCII characters".into(),
            ));
        }

        let chars: Vec<char> = raw.chars().collect();

        if chars.len() < 2 {
            return Err(VcpError::ParseError(format!("CSM1 code too short: {raw}")));
        }

        // Parse persona (first char).
        if !chars[0].is_ascii_uppercase() {
            return Err(VcpError::ParseError(
                "CSM1 persona must be uppercase".into(),
            ));
        }
        let persona = Persona::from_char(chars[0])?;

        // Parse level (second char).
        let level_char = chars[1];
        let adherence_level = level_char
            .to_digit(10)
            .and_then(|d| u8::try_from(d).ok())
            .filter(|&d| d <= 5)
            .ok_or(VcpError::InvalidAdherence(
                level_char
                    .to_digit(10)
                    .and_then(|d| u8::try_from(d).ok())
                    .unwrap_or(255),
            ))?;

        // Remaining string after persona + level.
        let remaining = &raw[2..];

        // Split into parts: scopes (+X), namespace (:NS), version (@X.Y.Z).
        let (before_version, version) = Self::split_version(remaining)?;
        let (before_namespace, namespace) = Self::split_namespace(before_version)?;
        let scopes = Self::parse_scopes(before_namespace)?;

        if persona == Persona::Custom && namespace.is_none() {
            return Err(VcpError::ParseError(
                "custom persona requires a namespace".into(),
            ));
        }
        Self::validate_scope_compatibility(&scopes)?;

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
            let mut scope_codes: Vec<char> = self.scopes.iter().map(|scope| scope.code()).collect();
            scope_codes.sort_unstable();
            s.push('+');
            s.push_str(
                &scope_codes
                    .iter()
                    .map(|scope| String::from(*scope))
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
    #[must_use]
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
    ///
    /// # Errors
    ///
    /// Returns [`VcpError::InvalidAdherence`] if `level` is greater than 5.
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

impl<'de> Deserialize<'de> for Csm1Code {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: Deserializer<'de>,
    {
        #[derive(Deserialize)]
        #[serde(deny_unknown_fields)]
        struct WireCode {
            persona: Persona,
            adherence_level: u8,
            scopes: Vec<Scope>,
            namespace: Option<String>,
            version: Option<String>,
        }

        let wire = WireCode::deserialize(deserializer)?;
        let code = Csm1Code {
            persona: wire.persona,
            adherence_level: wire.adherence_level,
            scopes: wire.scopes,
            namespace: wire.namespace,
            version: wire.version,
        };
        Csm1Code::parse(&code.encode()).map_err(D::Error::custom)?;
        Ok(code)
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
#[serde(deny_unknown_fields)]
pub struct ConstitutionRef {
    pub id: String,
    pub version: String,
}

/// Goal context for line 4 of the 8-line token.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
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
#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
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
    /// Maximum accepted encoded token size.
    pub const MAX_TOKEN_BYTES: usize = 65_536;

    /// Parse an 8-line CSM-1 token string.
    ///
    /// # Errors
    ///
    /// Returns [`VcpError::ParseError`] if the token does not have 7 or 8 lines,
    /// if any line is missing its required prefix, or if the persona,
    /// adherence, goal, constraint, flag, or personal-state fields are
    /// malformed.
    #[allow(clippy::too_many_lines)]
    pub fn parse(raw: &str) -> VcpResult<Self> {
        if raw.len() > Self::MAX_TOKEN_BYTES {
            return Err(VcpError::ParseError(format!(
                "CSM1 token exceeds maximum length {}",
                Self::MAX_TOKEN_BYTES
            )));
        }
        if raw
            .chars()
            .any(|character| character.is_control() && !matches!(character, '\n' | '\r'))
            || raw.as_bytes().iter().enumerate().any(|(index, byte)| {
                *byte == b'\r' && raw.as_bytes().get(index + 1) != Some(&b'\n')
            })
        {
            return Err(VcpError::ParseError(
                "CSM1 token contains a forbidden control character".into(),
            ));
        }
        let token_lines: Vec<&str> = raw.lines().collect();

        if !(7..=8).contains(&token_lines.len()) {
            return Err(VcpError::ParseError(format!(
                "CSM1 token requires 7 or 8 lines, got {}",
                token_lines.len()
            )));
        }

        // Line 1: VCP:<version>:<profile-id>
        let vcp_header = Self::strip_and_validate(token_lines[0], "VCP:")?;
        let (version, profile_id) = vcp_header.split_once(':').ok_or_else(|| {
            VcpError::ParseError(format!(
                "line 1 missing profile-id separator: {}",
                token_lines[0]
            ))
        })?;
        Self::validate_required_field(version, "protocol version")?;
        Self::validate_required_field(profile_id, "profile id")?;

        // Line 2: C:<constitution>@<version>
        let const_line = Self::strip_and_validate(token_lines[1], "C:")?;
        let (const_id, const_ver) = const_line.split_once('@').ok_or_else(|| {
            VcpError::ParseError(format!(
                "line 2 missing version separator: {}",
                token_lines[1]
            ))
        })?;
        Self::validate_required_field(const_id, "constitution id")?;
        Self::validate_required_field(const_ver, "constitution version")?;

        // Line 3: P:<persona>:<adherence>
        let persona_line = Self::strip_and_validate(token_lines[2], "P:")?;
        let (persona_str, adherence_str) = persona_line.split_once(':').ok_or_else(|| {
            VcpError::ParseError(format!(
                "line 3 missing adherence separator: {}",
                token_lines[2]
            ))
        })?;
        let mut persona_chars = persona_str.chars();
        let persona_char = persona_chars
            .next()
            .ok_or_else(|| VcpError::ParseError("empty persona in line 3".into()))?;
        if persona_chars.next().is_some() {
            return Err(VcpError::ParseError(
                "persona in line 3 must be exactly one character".into(),
            ));
        }
        let persona = Persona::from_wire_char(persona_char)?;
        if adherence_str.len() != 1 || !adherence_str.as_bytes()[0].is_ascii_digit() {
            return Err(VcpError::ParseError(format!(
                "invalid adherence: {adherence_str}"
            )));
        }
        let adherence: u8 = adherence_str
            .parse()
            .map_err(|_| VcpError::ParseError(format!("invalid adherence: {adherence_str}")))?;
        if !(1..=5).contains(&adherence) {
            return Err(VcpError::InvalidAdherence(adherence));
        }

        // Line 4: G:<goal>:<experience>:<style>
        let goal_line = Self::strip_and_validate(token_lines[3], "G:")?;
        let goal = if goal_line.is_empty() {
            None
        } else {
            let parts: Vec<&str> = goal_line.splitn(3, ':').collect();
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
        let constraint_line = Self::strip_and_validate(token_lines[4], "X:")?;
        let constraints = Self::parse_unique_list(constraint_line, "constraint")?
            .into_iter()
            .map(ConstraintFlag)
            .collect();

        // Line 6: F:<flags>
        let flags_line = Self::strip_and_validate(token_lines[5], "F:")?;
        let flags = Self::parse_unique_list(flags_line, "flag")?;

        // Line 7: S:<private-markers>
        let markers_line = Self::strip_and_validate(token_lines[6], "S:")?;
        let private_markers = Self::parse_unique_list(markers_line, "private marker")?;

        // Line 8 (optional): R:<personal-state>
        let personal_state = if token_lines.len() > 7 {
            let state_line = Self::strip_and_validate(token_lines[7], "R:")?;
            if state_line.is_empty() {
                None
            } else {
                Some(PersonalState::from_wire(state_line)?)
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

    fn validate_required_field(value: &str, name: &str) -> VcpResult<()> {
        if value.is_empty() || value.chars().any(char::is_control) {
            return Err(VcpError::ParseError(format!(
                "CSM1 token {name} must be non-empty and contain no control characters"
            )));
        }
        Ok(())
    }

    fn parse_unique_list(raw: &str, name: &str) -> VcpResult<Vec<String>> {
        if raw.is_empty() {
            return Ok(Vec::new());
        }
        let mut values = Vec::new();
        for candidate in raw.split(',') {
            let value = candidate.trim();
            if value.is_empty() || value.chars().any(char::is_control) {
                return Err(VcpError::ParseError(format!(
                    "CSM1 token {name} entries must be non-empty and contain no control characters"
                )));
            }
            if values.iter().any(|existing| existing == value) {
                return Err(VcpError::ParseError(format!(
                    "CSM1 token {name} entries must be unique"
                )));
            }
            values.push(value.to_string());
        }
        Ok(values)
    }
}

impl<'de> Deserialize<'de> for Csm1Token {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: Deserializer<'de>,
    {
        #[derive(Deserialize)]
        #[serde(deny_unknown_fields)]
        struct WireToken {
            version: String,
            profile_id: String,
            constitution: ConstitutionRef,
            persona: Persona,
            adherence: u8,
            goal: Option<GoalContext>,
            constraints: Vec<ConstraintFlag>,
            flags: Vec<String>,
            private_markers: Vec<String>,
            personal_state: Option<PersonalState>,
        }

        let wire = WireToken::deserialize(deserializer)?;
        let token = Csm1Token {
            version: wire.version,
            profile_id: wire.profile_id,
            constitution: wire.constitution,
            persona: wire.persona,
            adherence: wire.adherence,
            goal: wire.goal,
            constraints: wire.constraints,
            flags: wire.flags,
            private_markers: wire.private_markers,
            personal_state: wire.personal_state,
        };
        let reparsed = Csm1Token::parse(&token.encode()).map_err(D::Error::custom)?;
        if reparsed != token {
            return Err(D::Error::custom(
                "CSM1 token fields cannot be represented without ambiguity",
            ));
        }
        Ok(token)
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
            ('D', Persona::Mediator),
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
            ('P', Scope::Privacy),
            ('E', Scope::Education),
            ('T', Scope::Technical),
            ('O', Scope::Official),
            ('V', Scope::Vulnerable),
            ('A', Scope::Adult),
            ('H', Scope::Healthcare),
            ('S', Scope::Social),
            ('R', Scope::Religious),
        ];
        for (ch, expected) in &cases {
            assert_eq!(Scope::from_char(*ch).unwrap(), *expected);
        }
    }

    #[test]
    fn scope_from_char_invalid() {
        for legacy_or_invalid in ['I', 'L', 'G', 'X'] {
            assert!(Scope::from_char(legacy_or_invalid).is_err());
        }
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
    fn parse_rejects_lowercase() {
        assert!(Csm1Code::parse("n5+f+e").is_err());
    }

    #[test]
    fn parse_all_personas() {
        for p in Persona::all() {
            let raw = if *p == Persona::Custom {
                "C3:TEST".to_string()
            } else {
                format!("{}3", p.code())
            };
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
    fn parse_all_canonical_scopes() {
        let code = Csm1Code::parse("N5+F+W+P+E+T+O+V+H+S+R").unwrap();
        assert_eq!(
            code.scopes,
            vec![
                Scope::Family,
                Scope::Work,
                Scope::Privacy,
                Scope::Education,
                Scope::Technical,
                Scope::Official,
                Scope::Vulnerable,
                Scope::Healthcare,
                Scope::Social,
                Scope::Religious,
            ]
        );
    }

    #[test]
    fn parse_rejects_legacy_scopes() {
        for legacy_scope in ['I', 'L', 'G'] {
            assert!(Csm1Code::parse(&format!("N5+{legacy_scope}")).is_err());
        }
    }

    #[test]
    fn custom_persona_requires_namespace() {
        assert!(Csm1Code::parse("C3").is_err());
        assert_eq!(
            Csm1Code::parse("C3:ACME").unwrap().namespace.as_deref(),
            Some("ACME")
        );
    }

    #[test]
    fn duplicate_scopes_are_rejected() {
        assert!(Csm1Code::parse("N5+F+F").is_err());
    }

    #[test]
    fn conflicting_scopes_are_rejected() {
        for code in ["N5+F+A", "N5+V+A", "N5+H+A"] {
            assert!(Csm1Code::parse(code).is_err());
        }
    }

    #[test]
    fn namespace_and_version_bounds_are_enforced() {
        assert!(Csm1Code::parse("N5:TOOLONGNS").is_err());
        assert!(Csm1Code::parse("N5:lower").is_err());
        assert!(Csm1Code::parse("N5:A1").is_err());
        assert!(Csm1Code::parse("N5@1000.2.3").is_err());
        for version in ["01.2.3", "1.02.3", "1.2.03"] {
            assert!(Csm1Code::parse(&format!("N5@{version}")).is_err());
        }
        for version in ["latest", "canary", "1.2.3"] {
            assert_eq!(
                Csm1Code::parse(&format!("N5@{version}"))
                    .unwrap()
                    .version
                    .as_deref(),
                Some(version)
            );
        }
    }

    #[test]
    fn malformed_scope_separators_are_rejected() {
        for code in ["N5F", "N5+F+", "N5++F"] {
            assert!(Csm1Code::parse(code).is_err());
        }
    }

    #[test]
    fn parse_missing_level() {
        assert!(Csm1Code::parse("N").is_err());
    }

    #[test]
    fn compact_code_deserialization_cannot_bypass_wire_invariants() {
        let valid = serde_json::to_value(Csm1Code::parse("Z4+P:SEC@1.2.3").unwrap()).unwrap();
        assert!(serde_json::from_value::<Csm1Code>(valid).is_ok());

        for invalid in [
            serde_json::json!({
                "persona": "Nanny", "adherence_level": 6, "scopes": [],
                "namespace": null, "version": null
            }),
            serde_json::json!({
                "persona": "Nanny", "adherence_level": 5,
                "scopes": ["Family", "Family"], "namespace": null, "version": null
            }),
            serde_json::json!({
                "persona": "Custom", "adherence_level": 3, "scopes": [],
                "namespace": null, "version": null
            }),
            serde_json::json!({
                "persona": "Nanny", "adherence_level": 5, "scopes": [],
                "namespace": null, "version": null, "unexpected": true
            }),
        ] {
            assert!(serde_json::from_value::<Csm1Code>(invalid).is_err());
        }
    }

    // ── Compact Code Encoding ───────────────────────────

    #[test]
    fn encode_simple() {
        assert_eq!(Csm1Code::parse("N5").unwrap().encode(), "N5");
    }

    #[test]
    fn encode_with_scopes() {
        assert_eq!(Csm1Code::parse("N5+F+E").unwrap().encode(), "N5+E+F");
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
        assert_eq!(
            Csm1Code::parse(original).unwrap().encode(),
            "G4+E+F+H:ELEM@2.1.0"
        );
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

    #[test]
    fn token_rejects_extra_lines_instead_of_silently_ignoring_them() {
        assert!(Csm1Token::parse(&format!("{SAMPLE_TOKEN_8}\nS:shadow-state")).is_err());
    }

    #[test]
    fn token_size_limit_accepts_boundary_and_rejects_one_byte_over() {
        const SUFFIX: &str = "\nC:c@1\nP:N:5\nG:\nX:\nF:\nS:";
        let prefix = "VCP:1.0:";
        let profile_len = Csm1Token::MAX_TOKEN_BYTES - prefix.len() - SUFFIX.len();
        let at_limit = format!("{prefix}{}{SUFFIX}", "p".repeat(profile_len));
        assert_eq!(at_limit.len(), Csm1Token::MAX_TOKEN_BYTES);
        assert!(Csm1Token::parse(&at_limit).is_ok());

        let over_limit = at_limit.replacen(prefix, "VCP:01.0:", 1);
        assert_eq!(over_limit.len(), Csm1Token::MAX_TOKEN_BYTES + 1);
        assert!(Csm1Token::parse(&over_limit).is_err());
    }

    #[test]
    fn token_rejects_ambiguous_or_empty_structural_fields() {
        for bad in [
            SAMPLE_TOKEN_7.replace("VCP:1.0:", "VCP::"),
            SAMPLE_TOKEN_7.replace("profile-123", ""),
            SAMPLE_TOKEN_7.replace("family-safe@1.2.0", "@1.2.0"),
            SAMPLE_TOKEN_7.replace("family-safe@1.2.0", "family-safe@"),
            SAMPLE_TOKEN_7.replace("P:N:5", "P:NN:5"),
            SAMPLE_TOKEN_7.replace("P:N:5", "P:n:5"),
            SAMPLE_TOKEN_7.replace("P:N:5", "P:N:05"),
            SAMPLE_TOKEN_7.replace("G:protect:guided:gentle", "G:protect:\0guided:gentle"),
            SAMPLE_TOKEN_7.replace("X:no-profanity,no-violence", "X:no-profanity,"),
            SAMPLE_TOKEN_7.replace("X:no-profanity,no-violence", "X:no-profanity,no-profanity"),
        ] {
            assert!(
                Csm1Token::parse(&bad).is_err(),
                "accepted malformed token: {bad}"
            );
        }
    }

    #[test]
    fn token_deserialization_cannot_inject_or_bypass_wire_invariants() {
        let token = Csm1Token::parse(SAMPLE_TOKEN_7).unwrap();
        let valid = serde_json::to_value(&token).unwrap();
        assert_eq!(serde_json::from_value::<Csm1Token>(valid).unwrap(), token);

        let mut invalid_adherence = serde_json::to_value(&token).unwrap();
        invalid_adherence["adherence"] = serde_json::json!(0);
        assert!(serde_json::from_value::<Csm1Token>(invalid_adherence).is_err());

        let mut injected_line = serde_json::to_value(&token).unwrap();
        injected_line["flags"] = serde_json::json!(["safe\nS:forged"]);
        assert!(serde_json::from_value::<Csm1Token>(injected_line).is_err());

        let mut unknown_field = serde_json::to_value(&token).unwrap();
        unknown_field["unexpected"] = serde_json::json!(true);
        assert!(serde_json::from_value::<Csm1Token>(unknown_field).is_err());
    }
}
