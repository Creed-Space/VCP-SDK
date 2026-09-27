# Changelog

All notable changes to the VCP SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

These changes were made after signed tag `v4.2.0`. The published 4.2.0
packages do not contain them, and the next registry release will carry a new
version.

### Added
- The COMPACT tier of CSM-1 codes (VCP/S §2.8.3),
  `CS1|<persona name>|<adherence>|<identity token>|<scopes>`, in Python and
  Rust. Python `CSM1Code.parse` now accepts COMPACT input (it previously raised
  `ValueError`), and `CSM1Code.parse_compact`, `CSM1Code.encode_compact`, the
  optional `uvc_token` field and `Persona.from_name` / `Persona.wire_name` are
  new. The MCP server's `vcp_parse_csm1` tool accepts COMPACT input and
  reports its `uvc_token`. Rust adds the separate
  `vcp_core::csm1::Csm1CompactCode` type and `Persona::name` /
  `Persona::from_name`; `Csm1Code::parse`, `vcp-cli parse-csm1` and
  `vcp-wasm` `parse_csm1` still accept NANO and MICRO only. Python and Rust
  both require at least one scope and a canonical VCP/I token, and encode scopes
  in sorted order. They strip leading zeroes from the token's version only when
  building a code, not when parsing one.
- Rust `Csm1Token::extension_lines` keeps the optional lines that follow line 7
  and the R-line (`LC:`, `WC:`, `AS:`, `Q:` and the other prefixes in
  `Csm1Token::EXTENSION_PREFIXES`) verbatim and in order, so conformant tokens
  that carry them now parse and re-encode unchanged (VCP/S §2.4.7). The
  `vcp-wasm` `parse_csm1_token` output gains an `extension_lines` array only
  when such lines are present.
- The `measured` and `elicitation` signal sources, completing the seven-value
  VCP-X-Personal §2.3 source list in every binding: Python `SignalSource` enum
  and `SIGNAL_SOURCE_VALUES` (exported from `vcp.extensions`), Rust
  `SignalSource::Measured` and `SignalSource::Elicitation`, and WebMCP
  `SignalSource.MEASURED` and `SignalSource.ELICITATION`.
- Python `vcp.identity.namespace` exports `ORG_PREFIXES`,
  `COMMUNITY_PREFIXES`, `PERSONAL_PREFIX` and `is_known_namespace()`, the
  VCP/I §4.2 prefix lists for the tiers other than Core.
- Conformance vector `ctx-010` exercises the canonical CULTURE and
  SYSTEM_CONTEXT vocabularies in Python, Rust and WebMCP.
- VCP/I §3.4.1 semantic token validation, separate from syntactic parsing:
  Python `Token.validate()` and `Token.is_semantically_valid` (raising
  `vcp.identity.TokenValidationError`, a `ValueError` with a `code`), Rust
  `VcpToken::validate()`, `VcpToken::namespace_tier()`, `NamespaceTier`,
  `TokenValidationError` and the prefix and `RESERVED_WORDS` constants, a
  `vcp-cli validate-token` command, a `vcp-wasm` `parse_token` binding (syntax
  only), and WebMCP `validateIdentityToken`, `isIdentityTokenSyntax`,
  `namespaceTierOf`, `NAMESPACE_PREFIXES` and `RESERVED_WORDS`. A token fails
  validation with `unknown_namespace_prefix`, `core_segment_count` (a Core
  token without exactly three segments) or `reserved_word` (VCP/I §3.7.1).
  Conformance vectors `token-validate-*` check Python and Rust agreement;
  the syntactic `token-*` parse vectors are unchanged.
- VCP/A §2.3 forward compatibility. Python `VCPContext` gains
  `unknown_situational` and `unknown_personal`, Rust `SituationalContext` and
  `PersonalState` gain `unknown`, and WebMCP `VCPContext` gains an optional
  `unknown`: a group whose dimension emoji is not recognized is kept and
  re-encoded unchanged after the known dimensions, and plays no part in
  adaptation. Strict validators Python `validate_context_wire` (and
  `VCPContext.decode(..., strict=True)`) and WebMCP `validateContextWire`
  report unknown values, unknown dimension groups and non-canonical
  personal-state categories. Conformance vectors `ctx-011` (pass-through) and
  `ctx-012` (malformed input rejected by all three bindings).
- Python `AuditEntry.redacted()`, the view of an entry holding only the
  fields permitted at its level.
- Pseudonymous identities under the Personal tier: Python
  `pseudonymous_token(kind, pseudonym, *rest)` builds
  `user.anon-<24 hex>.<rest...>` or `user.pseudo-<24 hex>.<rest...>`, and
  `pseudonym_of`, `is_pseudonymous_token` and
  `migrate_legacy_pseudonymous_token` (all exported from `vcp.identity`) read
  and convert them. The registry module documents that pseudonymous owners
  prove possession of the pseudonym secret instead of the VCP/I §4.2.4 email
  verification.
- Conformance vectors `ctx-013` (a personal-only context that begins with
  `‖`) and `ctx-014` (a leading-zero intensity, rejected by Python, Rust and
  WebMCP).

### Changed
- Python `EMERGENCY_VALUES` (`vcp.adaptation.state`), used by `StateTracker`
  and `RedisStateTracker`, now also contains 🔥 and 🌪️ (ENVIRONMENT hazards),
  matching the VCP/A §7.1 `EMERGENCY_TOKENS`, plus the VS16-less spellings 🌪
  and ⚠. A context carrying any of them is an EMERGENCY transition. 🚨, 🛑
  (EMBODIMENT emergency_stop, VEP-0004), ⚠️ and 🆘 still count. Detection
  now matches an indicator inside a raw value too (new
  `contains_emergency`), so `🎭🦖🔥` is an emergency. Rust and WebMCP have no
  emergency set.
- **Breaking:** Rust personal-state wire forms follow the VCP-Spec
  sub-signal ruling. `PersonalDimension::to_wire` and
  `PersonalState::to_wire` write VCP/A context strings, which carry no
  sub-signal (VCP/A §2.3), so `🩺pain:4[migraine]` is no longer emitted and
  `from_wire` rejects both `pain:4[migraine]` and `pain:4:migraine`. The
  sub-signal travels on the CSM-1 R-line as a third field
  (`🩺pain:4:migraine`, VCP/S §2.4.1) through the new `to_r_line` and
  `from_r_line`, which `Csm1Token` now uses; the former bracket form is not
  read. `extended` must be 1-256 ASCII letters or underscores. A new
  cross-feed step in the context parity runner decodes every Rust encoding
  with Python and WebMCP (vector `ctx-015`).
- **Breaking:** Rust accepts a VCP/A personal value without an intensity
  (`🧠focused`): it decodes with `intensity` 3 and the new public field
  `intensity_explicit` set to `false`, and re-encodes without one
  (`PersonalDimension::without_intensity`). JSON omits `intensity` in that
  case. The CSM-1 R-line follows VCP/S §2.4.1 as revised at VCP-Spec
  57a561e (`value [":" intensity [":" extended]]`): `from_r_line` also accepts
  an omitted intensity (default 3), rejects a sub-signal without an explicit
  intensity (`unwell:migraine`), and `to_r_line` always writes the intensity.
  Vector `ctx-016` is the
  VCP/A §2.4 personal-only example.
- Python and WebMCP keep known values in a group that also holds unknown
  ones: `🎭🚨🦖` decodes to `🚨` and a raw `🦖` (it used to become one raw
  value, hiding the emergency). Unmatched runs are kept as written, and
  strict validators report only them (vector `ctx-017`). A known value is
  accepted only on a grapheme boundary, never inside an emoji sequence: it
  must not follow a ZERO WIDTH JOINER or be followed by a ZWJ, VS16,
  skin-tone modifier, combining keycap or tag character. `📡👁️‍🗨️`, `👥👶🏽`
  and `📍🏠️` therefore decode as single raw values rather than as `👁️`,
  `👶` or `🏠` plus a stray tail (vectors `ctx-023` to `ctx-025`).
- **Breaking:** Python and WebMCP reject a dimension repeated in one context
  string (`⏰🌅|⏰🌙`, `‖🧠focused|🧠foggy`), as Rust already did (VCP/A
  §2.3; vectors `ctx-018`, `ctx-019`).
- Python RELATIONSHIP values accept the single-part forms VCP/A allows,
  `{tie}` and `:{function}` (vectors `ctx-020`, `ctx-021`), and the MCP
  `vcp_encode_context` schema accepts them too.
- **Breaking:** `AuditLogger.get_entries(since=...)` raises `ValueError` on a
  `minimal` logger and leaves out entries recorded below `standard`, since
  filtering by time would reveal timestamps that level withholds.
- The MCP `vcp_encode_context` schema accepts the deprecated value names the
  encoder resolves (`midday`, `transit`, `noisy`, `casual`).
- Registry prefix nodes inherit the most restrictive privacy tier by an
  explicit rank (`PRIVACY_TIER_RANK`: public, community, organizational,
  personal, pseudonymous). The comparison used the alphabetical order of the
  enum values, under which `public` counted as the most restrictive, so a
  prefix shared with a personal or pseudonymous entry could be enumerated.
- `docs/identity/VCP_IDENTITY_NAMING.md` and
  `docs/uvc/UVC_NAMING_SPECIFICATION.md` are exact copies of the VCP-Spec
  companions (the VCP/I §3.4.1 and §3.7 rules and the 256-character limit),
  the namespace companions state the username rule, and the adaptation
  companions carry the VCP/A §2.3 repeated-dimension and sub-signal rules.
- **Breaking:** VCP/I defines no `anon` or `pseudo` prefix, so pseudonymous
  identities move to `user.anon-<hex>.*` and `user.pseudo-<hex>.*`
  (the round-3 pseudonym decision). `LocalRegistry.register` now applies
  `Token.validate()` and raises `TokenValidationError` for an unlisted prefix
  (including `anon.*` and `pseudo.*`), a Core token without exactly three
  segments or a reserved-word segment, because a registry MUST NOT register
  such a token (VCP/I §3.4.1). `PseudonymousRegistry.generate_pseudonym`
  returns 24 lowercase hex characters (was 32) so the pseudonym fits the
  username segment, and `register_pseudonymous` requires a token whose
  username carries that pseudonym. `infer_privacy_tier` returns PSEUDONYMOUS
  for the new form; the retired `anon.*` and `pseudo.*` tokens still parse
  but get the restrictive ORGANIZATIONAL tier, fail validation, and convert
  with `migrate_legacy_pseudonymous_token` (the first 24 hex characters of the
  legacy hash become the pseudonym).
- **Breaking:** a personal-state intensity is exactly one ASCII digit from 1
  to 5 (VCP/A §2.3). Python `PersonalState.decode` and Rust
  `PersonalDimension::from_wire` previously accepted `04`, `+4` (and, in
  Python, `" 4"` and non-ASCII digits); WebMCP `decodePersonalState`
  previously returned `value:suffix` as a raw value. All three now reject any
  text after `:` other than one digit 1-5, and context decoders reject the
  string as malformed.
- The synchronized `vcp-adaptation-context.schema.json` rejects a
  personal-band intensity that is not one digit 1-5 and admits a
  personal-only context beginning with `‖`. The adaptation companion docs
  pick up the VCP/A revision: the personal-only form in the ABNF and
  examples, the one-digit intensity rule, and valid RELATIONSHIP examples
  (`trusted_collaborator:professional`, `long_term:social`).
- **Breaking:** the audit privacy hash is the keyed form of VCP core audit §6:
  `"hmac-sha256:"` followed by the first 32 lowercase hex characters of
  HMAC-SHA256(K_audit, UTF-8(identifier)), replacing the salted
  `sha256:` hash. `K_audit` is the operator key passed as
  `AuditLogger(audit_key=...)` (bytes, or text encoded as UTF-8; shorter than
  32 bytes is rejected), otherwise 32 bytes from `os.urandom` generated when
  the module loads and never logged, exported or persisted. The
  `privacy_salt` argument is a deprecated alias for `audit_key` and is now
  subject to the same 32-byte minimum. Pseudonyms written by earlier
  versions do not match new ones, so purges by session do not reach entries
  exported before the upgrade.
- **Breaking:** `AuditLogger` hands `log_callback`, the return value of
  `log_verification` and `log_privacy_filter`, `get_entries()` and the purge
  tombstone event the `AuditEntry.redacted()` view: fields above the logger's
  level are `None`, matching `to_dict()`. At the default `minimal` level a
  callback no longer receives the session hash, timestamp, issuer hash,
  version, signature, checks or request ID hash. The in-memory store keeps the
  full entry so `purge_by_session` still works. `AuditEntry` fields
  `timestamp`, `session_id_hash`, `checks_passed`, `issuer_hash`, `version`
  and `manifest_signature` are now typed as optional.
- **Breaking:** the MCP `vcp_validate_token` tool applies VCP/I §3.4.1
  semantic validation after parsing. A syntactically valid token with an
  unlisted prefix, a Core token without exactly three segments or a
  reserved-word segment now reports `valid: false` with `syntax_valid: true`
  and an `error_code`; valid tokens also report `namespace_tier`. The
  `vcp-wasm` `validate_token` binding applies the same rules. WebMCP
  `vcp_chat` rejects a `constitution_id` that fails `validateIdentityToken`.
- **Breaking:** every VCP/A situational vocabulary follows the §2.2 tables
  and the synchronized schema enums exactly, in Python `SituationalDimension`,
  the MCP `vcp_encode_context` schema (now generated from those tables) and
  WebMCP `SITUATIONAL_SPECS`. TIME adds 📅 🎉 ⏰ 📆 🔄 and ☀️ is `daytime`;
  SPACE adds ⛪ 🏛️ 🏪 🌳 💻 🏠 🔒 and 🚗 is `vehicle`; COMPANY adds 👨‍🏫 👮 👴 💑
  🤝 👨‍⚕️ 🐕, 👥 is `crowd` and `strangers` is 🧑‍🤝‍🧑; OCCASION adds 💒 🏥 👨‍🏫 🎪
  ⚖️ 🗳️ 🎓 and `mourning` is ⚰️ (was 😢); ENVIRONMENT is 🥵 🥶 🌧️ 🌪️ 🔇 📢 🔥 💨
  🌫️ 🌤️ 🏔️ 🌊 (☀️ `comfortable` and 🔊 `noisy` are removed); AGENCY adds 💰 💵
  🕳️ 🏡 🔑 🎓 🆓 🏃 and `subordinate` is 👇 (was 📋); CONSTRAINTS adds 🚧 🤐 📱 🚨
  👮 📜 🏥 🔒 and `time` is ⏰ (was ⏱️). The encoders still resolve the retired
  names `midday`, `transit` and `noisy` (deprecated); `comfortable` has no
  replacement. Python `PersonalStateDimension` value sets are the VCP/A §3.1
  categories (focused, distracted, overloaded, foggy, reflective; calm, tense,
  frustrated, neutral, uplifted; rested, low_energy, fatigued, wired,
  depleted; unhurried, time_aware, pressured, critical; neutral, discomfort,
  pain, unwell, recovering), and WebMCP exports them as
  `PERSONAL_STATE_CATEGORIES`.
- **Breaking:** context decoders reject malformed strings in every binding:
  an empty group, a group that does not begin with an emoji, a dimension with
  no value, an empty personal band after `‖`, or an intensity outside 1-5.
  Python and WebMCP previously skipped empty or valueless groups, and Rust
  previously rejected groups with an unrecognized dimension emoji, which are
  now passed through. Python raises `ValueError`; WebMCP `decodeContext` throws
  `SyntaxError`. Rust `SituationalContext` and `PersonalState` gain a public
  `unknown` field, so struct literals need it or `..Default::default()`.
- **Breaking:** the synchronized `vcp-identity-token.schema.json` adds the
  VCP/I §3.4.1 semantic rule (`token.allOf`, a `domain` enum and
  `personal_prefix`), and `vcp-semantics-csm1.schema.json` spells CSM-1 with a
  hyphen; both are byte copies of VCP-Spec.
- Conformance vectors `vep-004` and `vep-009` use the RELATIONSHIP tables
  (`vep-009` now documents that an unlisted value is tolerated), and
  `ctx-006` and `ctx-007` use canonical values.
- The illustrative `csm1_to_canonical` mapping in the identity and UVC
  encoding companion docs follows VCP/I §2.3.2: three-segment Core tokens for
  the six standard personas, a namespace becomes the `:NS` suffix, and a
  Custom code has no default instead of producing a `custom.` token. No SDK
  code emits a `custom.` token.
- Tests, examples and companion docs use canonical identity prefixes
  (`vcp://family.safe.guide` replaces `vcp://core.ethics.consent`, and the
  composition examples use `school.example`, `secure.ethics.foundation` and
  `user.alice`). The adaptation companion docs reproduce VCP/A §2.1 to §2.4
  (revision 2.1.1) and regenerate the quick-reference card; their remaining
  pre-v3.1 code samples are marked historical.
- **Breaking:** the SYSTEM_CONTEXT (📡, position 9) vocabulary follows
  VCP/A §2.1: 💻 `personal_device`, 🏢 `workplace_system`, 🖥️
  `shared_terminal`, 👁️ `monitored_environment`. The SDK's former values
  (🟢 online, 🟡 degraded, 🔴 offline, 🔒 sandboxed, 🧪 testing) were never
  in the specification and are removed from Python `SituationalDimension`,
  `ContextEncoder`, the MCP server's `vcp_encode_context` input schema and
  the WebMCP `SITUATIONAL_SPECS` and `buildContext`. The encoders reject the
  old names (Python strict mode raises `ValueError`; WebMCP drops them).
  Decoders still accept any value on the wire and keep an unknown one as a
  raw string. `schemas/vcp-adaptation-context.schema.json` is synchronized
  with VCP-Spec. Rust `vcp-core` has no value vocabulary and is unchanged.
- **Breaking:** the CULTURE (🌍, position 4) vocabulary follows VCP/A §2.1:
  🔇 `high_context`, 📢 `low_context`, 🎩 `formal`, 👋 `informal`, 📊
  `hierarchical`, ⚖️ `egalitarian`, 👥 `collectivist`, 👤 `individualist`, in
  the same bindings. 😎 `casual` and 🌐 `mixed` are removed; the encoders
  still resolve the name `casual` to 👋 `informal` (deprecated), and `mixed`
  has no replacement. Python `ContextEncoder.encode(culture=...)` and WebMCP
  `buildContext({culture})` accept a list, as COMPANY and CONSTRAINTS do.
- **Breaking:** Python `AuditLogger` and `AuditEntry` default to
  `AuditLevel.MINIMAL` instead of `AuditLevel.STANDARD`, matching VCP core
  audit §3.1 and Amendment J. At `minimal` an entry carries only the audit
  level, the verification result, the bundle ID hash and the content hash; the
  timestamp, session hash, checks, issuer hash, version, signature and request
  ID hash need `standard` or higher. Pass `level=AuditLevel.STANDARD` to keep
  the old output. Field placement per level is unchanged.
- **Breaking:** scope H is named "Health" (VCP/S §2.6.1). Python
  `Scope.HEALTH` is canonical and `Scope.HEALTH.name` is `"HEALTH"`, so the MCP
  server's `vcp_parse_csm1` reports `HEALTH` and the Health/Adult conflict
  error names "Health". Rust renames `Scope::Healthcare` to `Scope::Health`,
  which serializes as `"Health"` (for example in `vcp-wasm` `parse_csm1`
  output); deserialization still accepts `"Healthcare"`. The description reads
  "Health and medical context" in both.
- **Breaking:** Python namespace tier inference follows the VCP/I §4.2 prefix
  table. `CORE_DOMAINS` is `family`, `work`, `secure`, `creative`, `reality`
  (it listed `education`, `health`, `finance`, `legal`, `safety`, `privacy`,
  `accessibility` and `environment`, and omitted `secure`, `creative` and
  `reality`). `infer_tier` maps `company`, `school` and `ngo` to
  ORGANIZATIONAL, `religion`, `culture` and `community` to COMMUNITY and `user`
  to PERSONAL, and raises `ValueError` for any other first segment instead of
  returning COMMUNITY (VCP/I §3.7.2 rejects unknown prefixes).
  `validate_namespace_access` returns `False` for such tokens. The
  hyphenated `company-*` and `user-*` forms no longer infer a tier.
  `Token.parse` stays syntactic, as the §3.4 ABNF and the identity schema
  pattern are. Registry `infer_privacy_tier` uses the same lists, so
  `education` and `health` tokens get the restrictive ORGANIZATIONAL tier
  instead of PUBLIC, and registry organizational membership checks no longer
  treat `org` as an organizational prefix.
- Tests, examples and conformance vectors use canonical namespace prefixes
  (`company.example.dept.team.policy` replaces `org.example.dept.team.policy`
  in `token-004` and `xrt-003`), and `csm1-err-014` is described as the Health
  and Adult conflict. The identity and adaptation companion documents in
  `docs/` list the five Core prefixes, `max_segments` 10, and the canonical
  CULTURE and SYSTEM_CONTEXT values.
- Python `PersonalSignal` now raises `ValueError` for a `source` outside the
  seven VCP-X-Personal §2.3 values; it previously accepted any string.
- The CSM-1 token parser in Rust accepts adherence 0 (Minimal, advisory only) on
  the P-line, as codes already did. It reads `R:none` as personal state
  declared empty, and the encoder now writes `R:none` for that state instead of
  a bare `R:` (still accepted on input). An R-line dimension with an unknown
  emoji is skipped and the rest of the line is parsed, per VCP/S §2.4.2.
- The manifest schemas accept `metadata.adherence_level` 0 (VCP/S §2.7).
  `vcp-manifest-v2.schema.json` also narrows the level from 1-9 to 0-5 and
  rejects leading zeroes in the `metadata.csm1` version, matching v1.
- **Wire format:** the Rust personal-extension enums (`PersonalDimension`,
  `SignalSource`, `LifecycleState`, `DecayCurve`) now serialize with the
  snake_case wire values of VCP-X-Personal (`cognitive_state`,
  `inferred_local`, `decaying`, `exponential`) instead of Rust's PascalCase
  variant names. JSON written with the old names no longer deserializes.
- Persona descriptions follow the VCP/S persona table. Rust `Persona::Muse`
  describes itself as "Creative challenge and provocation", matching Python.
  The WebMCP `vcp_list_personas` descriptions and use cases for all six
  personas were rewritten; Nanny now holds the child-safety and vulnerable-user
  role and Godparent the ethical-guidance role.
- WebMCP `vcp_chat` sends `constitution_id` `work.professional.assistant`
  when the caller omits one, instead of `general`, which is not a valid VCP/I
  token. It is the VCP/I §2.3.2 default token for the Ambassador persona,
  which is also the default `vcp_chat` persona. (Earlier unreleased revisions
  used `personal.growth.creative`, whose `personal` prefix is not a VCP/I
  namespace, and then `creative.growth.muse`, which belongs to the Muse
  persona.) The `vcp_chat` and `vcp_build_token` tool descriptions now say
  what the context and token actually carry.
- The messaging conformance suite id is now `messaging/messaging` (was
  `adaptation/messaging`), and its fixture moved from
  `conformance/adaptation/messaging.json` to
  `conformance/messaging/messaging.json`. The coverage manifest, feature matrix
  and messaging runner use the new id.
- The CSM-1 docs, CLI help and `vcp-wasm` bindings call the one-line form a
  "CSM-1 code" and the multi-line form a "CSM-1 token" (7 lines, then an
  optional R-line and extension lines), and describe the token header version (currently `1.0`) as opaque.
  Error messages and doc comments use American spelling ("unrecognized").

### Deprecated
- Python `Scope.HEALTHCARE`, now an alias of `Scope.HEALTH`, and Rust
  `Scope::Healthcare`, now a deprecated associated constant equal to
  `Scope::Health`.
- The CULTURE value name `casual` in Python `ContextEncoder` (which emits a
  `DeprecationWarning`) and WebMCP `buildContext`; use `informal`. Likewise
  TIME `midday` (use `daytime`), SPACE `transit` (use `vehicle`) and
  ENVIRONMENT `noisy` (use `loud`).
- Python `AuditLogger(privacy_salt=...)`; use `audit_key`.

## [4.2.0] - 2026-09-03

Published to PyPI, npm and crates.io from signed tag `v4.2.0` (see
`release/publication-state.json`).

### Changed
- WebMCP package published under the `@creedspace` npm scope as `@creedspace/vcp-sdk`; the
  `@creed-space` scope was never registered and is now a retired public term.

### Added
- `vcp-mcp-server` console script and `python/src/vcp/mcp_server.py`, exposing
  the SDK through the `[mcp]` extra with JSON-schema-validated tool inputs.
- Rust `vcp_core::strict_json` and hardened Python `parse_json_strict`
  (duplicate keys, non-finite constants, and overflowing numeric literals such
  as `1e400` are rejected before signatures are considered).
- Shared `parse_rfc3339_utc` helper used by bundle, trust, revocation, and skill
  manifest parsing so nanosecond fractions parse identically on Python 3.10+.
  Timestamps must now match the RFC 3339 grammar (`YYYY-MM-DDTHH:MM:SS[.frac]`
  plus `Z` or `±HH:MM`); looser `fromisoformat` inputs such as date-only values
  or colon-less offsets are rejected.
- WebMCP `registration.ts` cleanup contract and polyfill loader changes;
  `conformance/runners/context_parity.py` now also executes the WebMCP context
  encoder/decoder (`webmcp/scripts/run-context.mjs`), and the coverage manifest
  records those vectors as checked for WebMCP.
- Capability-negotiation fixtures for an invalid identity token
  (`IDENTITY_INVALID`), forward-compatible boolean core-feature flags, and the
  rejection of non-boolean core-feature entries.
- `schemas/vcp-conformance-aggregate-report.schema.json`; updates to the
  manifest v1, messaging v2.0, and CSM-1 schema copies.
- Mutation, fuzz, performance, property, CodeQL, dependency-review, and
  reproducible release/attestation workflows.
- `AuditLogger(privacy_salt=...)` and `AuditLogger.track_exported_path()` so
  operators can make GDPR purges match across process restarts; the default
  per-process salt only covers exports made by the same process.
- `ContextEncoder.encode(..., strict=True)`; unknown situational values now
  raise `ValueError` instead of being dropped (pass `strict=False` for the old
  behaviour).
- Complete local VCP Agent Runtime Profile Python facades for `observe@0.1.0`, `controlled@0.1.0`, and `accretive@0.1.0`, including bounded orientation, cursor deltas, normative conflict and objection, proof-first controlled execution, interruption, reconciliation, candidate-first accretion, promotion, influence, and revocation.
- Strict candidate schema and shared observe, controlled, and accretive fixtures; Rust and TypeScript portable contract facades; eight executable Python examples; runtime identity diagnostics; and the exact AX-01 through AX-24 deterministic evaluation harness.
- Rust live HTTPS transport for online status and CRL revocation checks, with
  rustls hostname verification, public address resolution and pinning, disabled
  redirects, proxies, retries, and decompression, plus bounded headers and bodies.
- Shared Python and Rust online response vectors that bind every decision to the
  requested JTI and issuer.
- Distinct `revocation_unavailable` verification outcomes. They remain
  fail-closed while no longer representing an unconfirmed result as revoked.

### Changed
- Personal-state decay defaults now carry the per-dimension `stale_threshold`
  and `fresh_window_seconds` from VCP-X-Personal §3.3 (cognitive 0.3/60s,
  emotional 0.25/60s, energy 0.2/300s, urgency 0.35/60s, body 0.15/600s) in
  Python, Rust, and WebMCP; WebMCP `DecayConfig` gained optional
  `staleThreshold`/`freshWindowSeconds`, and `personal_parity.py` now executes
  the WebMCP module (`webmcp/scripts/run-personal.mjs`) alongside Python and
  Rust, with a fixture vector exercising a non-default fresh window.
- `schemas/vcp-manifest-v2.schema.json` `metadata.persona` now uses the CSM-1
  persona registry (`nanny`, `sentinel`, `godparent`, `ambassador`, `muse`,
  `mediator`, `custom`); the non-registry `anchor` and `hotrod` values are
  gone. WebMCP default personas replace `anchor`/`steward` with `mediator`
  and `vcp_chat` defaults to `ambassador`; a repository test guards every
  persona enum against the registry.
- Python `negotiate_handshake` now answers a malformed client `version` or
  `min_version` with the canonical `VERSION_UNSUPPORTED` `vcp-error` instead
  of raising `ValueError`, matching Rust and WebMCP; WebMCP no longer treats
  an explicit `min_version: null` as the `1.0` default. A
  `malformed-client-version` negotiation fixture pins the shared behaviour.
- `schemas/vcp-identity-token.schema.json` re-synced byte-for-byte from
  VCP-Spec (canonical form keeps the namespace suffix, segments are bounded to
  32 characters, and the token object rejects unknown properties), so
  `make schema-sync` passes against the current specification.
- `Manifest.from_dict` validates the manifest shape (`vcp_version == "2.0"`,
  UUID `jti`, positive integer `token_count`, supported tokenizer, string
  fields) and `BundleBuilder.with_expires_days` accepts 1 to 90 days only.
- `TokenType.COMPETENCE_ATTESTATION` wire value is now `competence_attestation`
  (Python and TypeScript) and the manifest v2 schema lists it; the schema also
  requires unique `signed_fields` and closed `signers[]` / `stapled_proof`
  objects.
- `ContextEncodeRequest` rejects unknown fields and `DecisionType` is aligned
  across the PDP and enforcement modules.
- `StateTracker` treats EMBODIMENT `🛑` (`emergency_stop`) as an emergency and
  reports personal-state band changes as transitions; the built-in
  `adherence_escalate` and `persona_select` hooks now fire on the events
  `StateTracker` actually emits.
- `RefusalBoundaryPlugin` in `ESCALATE` mode escalates (rather than abstains)
  when no bundle is present; `AdherenceLevelPlugin` requires an integer
  adherence level in 0-5.
- WebMCP `decodeContext` uses vocabulary-based scanning (VS16 preserved, ZWJ
  sequences intact, bare dimension symbols accepted per fixture vep-011);
  `negotiate()` returns `IDENTITY_INVALID` for malformed identity tokens and
  echoes extra boolean core features like the native SDKs; `HookRegistry`,
  `TorchConsumer.receiveTorch`, `computeDecayedIntensity`, and
  `createVCPTools({personas})` validate their inputs.
- Online status responses must echo the requested JTI and issuer. Confirmed
  revocations must include a non-empty reason and a strict RFC 3339 timestamp.
- The Python HTTPS transport now enforces JSON content types, identity encoding,
  and response header limits in parity with Rust.
- Reviewed Rust and release-tooling dependencies are current. The direct
  `base64` 0.23 dependency disables its new `simd-unsafe` default and retains
  only the safe standard-library engine. These updates do not change the SDK's
  public API, wire behavior, package version, or Rust 1.87 minimum.

**Set as the version on 2026-04-22:**

### Added
- **VCP v3.2 / VEP-0004 adaptation layer** — `vcp.adaptation.context` (Python), `src/extensions/context.ts` (TypeScript), `vcp_core::situational` + `vcp_core::context` (Rust) now implement the full 18-dimension v3.2 context model:
  - 13 situational dimensions (positions 1-13): time, space, company, culture, occasion, environment, agency, constraints, system_context, **embodiment** (VEP-0004, pos 10), **proximity** (VEP-0004, pos 11), **relationship** (VEP-0004, pos 12), **formality** (VEP-0004, pos 13).
  - 5 personal-state dimensions on the R-line: cognitive_state, emotional_tone, energy_level, perceived_urgency, body_signals — each an optional `{value, intensity 1-5}`.
  - Wire-format band separator `‖` (U+2016 DOUBLE VERTICAL LINE) between situational and personal halves.
  - RELATIONSHIP is free-form: its value is a compound `{tie}:{function}` string (e.g. `colleague:professional`), not a closed emoji vocabulary.
- **Conformance classification** — `conformance_level()` method on `VCPContext` / `FullContext` (Python + TypeScript + Rust) returns `VCP-Minimal` (core 9 only), `VCP-Standard` (core + R-line), or `VCP-Extended` (any VEP-0004 dim).
- **VEP-0004 conformance fixtures** — `conformance/adaptation/context_encoding_extended.json` with 12 test vectors covering each VEP-0004 dimension in isolation, the canonical 18-dim example, VS16 parser-compatibility (↔️ qualified vs bare), and the Extended-over-Standard precedence rule.
- **JSON Schema v3.2** — `schemas/vcp-adaptation-context.schema.json` upgraded from v2 to v3.2 with nested `parsed.situational` / `parsed.personal` shape, `conformance_level` enum field, and per-dimension value definitions.

### Changed
- WebMCP package renamed from `@vcp/webmcp` to `@creedspace/vcp-sdk`; imports
  and the `/polyfill` subpath must be updated.
- **CULTURE values** are now communication styles per CSM-1 (high_context, low_context, formal, casual, mixed), not nationalities. The nationality vocabulary was never in spec and is rejected by the v3.2 encoders.
- Python `VCPContext` refactored from a plain `@dataclass` to a class with `__slots__` and backwards-compatible `dimensions=` constructor kwarg (aliases `situational=`).
- Python exports `SituationalDimension` and `PersonalStateDimension` from `vcp.adaptation`; `Dimension` remains as a backwards-compat alias for `SituationalDimension`.
- Rust `FullContext::situational` is now a 13-dimension `SituationalContext`; the enum gains `Embodiment`, `Proximity`, `Relationship`, `Formality` variants and a `position()` accessor. `ConformanceLevel` is re-exported at the crate root.

### Removed
- The deprecated VCP v3.0 **STATE** dimension (removed in v3.1; SYSTEM_CONTEXT occupies position 9 and the prior STATE enum value is no longer exposed).

## [4.1.0] - 2026-04-06

### Added
- **PDP Enforcement Module** (`vcp/enforcement.py`) — Standalone policy enforcement for VCP bundles without requiring a full safety stack. Includes `PDPPlugin` interface, `PDPEnforcer` orchestrator, and three built-in plugins: `RefusalBoundaryPlugin`, `AdherenceLevelPlugin`, `BundleExpiryPlugin`.
- **Purge Handler Registration** — `AuditLogger.register_purge_handler()` lets external sinks (Redis, database) register GDPR purge logic. Warns if `log_callback` is set without a handler.

### Fixed
- **GDPR Purge Persistence Gap** — `purge_by_session()` now scrubs exported JSON files (not just in-memory entries), with thread-safe file rewriting and tombstone receipts that include file-level evidence.
- **`datetime.utcnow()` Deprecation** — All remaining instances replaced with `datetime.now(timezone.utc)` across source and test files.
- **Thread Safety** — `export_json()` path tracking and `_purge_exported_files()` now run inside `self._lock`, closing TOCTOU race conditions.

## [4.0.0] - 2026-03-08

### Added
- **VCP v2.0 Specification Support** — Protocol version bumped from 1.0/1.2 to 2.0 across all SDKs
- **Extended Token Types** — New enums for refusal boundaries, testimony, creed adoption, and compliance attestation tokens
- **VCP/M Messaging v2.0** — Inter-agent messaging updated from v1.2 to v2.0 with context field trust model, escalation-transition severity alignment, and version negotiation
- **JSON Schema v2** — New `vcp-manifest-v2.schema.json` and `vcp-messaging-v2.0.schema.json`
- **Version Negotiation** — Python SDK adds `check_version_compatibility()` for major/minor version handling
- Python: Hook system, revocation checking, inter-agent messaging (previously unreleased)
- Rust: Hook system, trust anchor management, full transport layer (previously unreleased)
- Language-agnostic conformance test suite and runnable examples (previously unreleased)

### Changed
- `vcp_version` in bundle manifests changed from `"1.0"` to `"2.0"`
- `vcp_message` in inter-agent messages changed from `"1.2"` to `"2.0"`
- Personas updated from NZGAMRHC to NZGAMDC (previously unreleased)
- Python SDK version bumped to 4.0.0
- Rust SDK versions bumped to 4.0.0

### Fixed
- Resolved mypy type-check failures in Python SDK (previously unreleased)
- Resolved CI lint and formatting failures (previously unreleased)
- Resolved clippy warnings in Rust SDK (previously unreleased)

## [3.1.0] - 2026-02-28

### Added
- **Extension modules** for all 4 VCP v3.1 extensions:
  - Personal State — signal declaration, exponential/linear decay, lifecycle tracking
  - Relational Context — AI self-model, trust levels, standing, bias detection
  - Constitutional Consensus — Schulze method voting, pairwise matrix, strongest paths
  - Session Handoff (Torch) — generation, consumption, lineage tracking
- **Capability Negotiation** — VCP-Hello/VCP-Ack handshake protocol
- **53 conformance test vectors** across 5 categories (personal, relational, consensus, torch, negotiation)
- **Cross-SDK conformance CI** — GitHub Actions workflow testing Python, TypeScript, and Rust
- Python, TypeScript, and Rust implementations with full parity

### Changed
- Ballot model standardized to grouped `rankings: list[list[str]]` format across all SDKs
- Python LifecycleState enum uses `SET`/`STALE` (replaces `FRESH`/`BASELINE`)

## [1.1.0] - 2026-01-18

### Added
- **VCP Specification v1.1** -- R-line (Line 8) for real-time personal state in CSM-1 tokens
- **Rust SDK** (`vcp-core`, `vcp-wasm`, `vcp-cli`) -- High-performance parsing with `no_std` support and WASM bindings
- **TypeScript/WebMCP SDK** (`@vcp/webmcp`, renamed to `@creedspace/vcp-sdk` in 4.2.0) -- Browser-side VCP tool registration via `navigator.modelContext` (Chrome 145+)
- MCP-B polyfill for non-Chrome browsers
- Five WebMCP tools: `vcp_chat`, `vcp_build_token`, `vcp_parse_token`, `vcp_transmission_summary`, `vcp_list_personas`
- JSON Schema definitions for all protocol layers

### Changed
- Restructured repository for polyglot SDK support (Python, Rust, TypeScript)
- CSM-1 token format extended from 7 lines to 8 lines (R-line addition)

## [1.0.0] - 2026-01-11

### Added
- **VCP Specification v1.0** -- Complete protocol specification
- **Python SDK** -- Reference implementation with identity resolution, CSM-1 encoding, context management, and LLM integration
- Four-layer protocol stack: VCP/I (Identity), VCP/T (Transport), VCP/S (Semantics), VCP/A (Adaptation)
- Universal Value Codes (UVC) naming scheme
- Signed bundle format with Ed25519 signatures and SHA-256 content hashes
- Three-tier privacy architecture (public/consent/private)
- Six built-in personas (Muse, Sentinel, Godparent, Ambassador, Anchor, Nanny)
- VCP Demo site with interactive playground
- Academic paper draft
- MIT LICENSE, CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md
- CI workflow (Python lint/test, Rust build/test, TypeScript type check, schema validation)
- GitHub issue templates (Bug Report, Feature Request, Spec Amendment)
- Pull request template
- Dependabot configuration for all package ecosystems
- Comprehensive README with architecture diagrams, quick-start guides, and full documentation index

<!-- v4.2.0 is the first signed tag; older links use the commits that set each version. -->
[Unreleased]: https://github.com/Creed-Space/VCP-SDK/compare/v4.2.0...HEAD
[4.2.0]: https://github.com/Creed-Space/VCP-SDK/releases/tag/v4.2.0
[4.1.0]: https://github.com/Creed-Space/VCP-SDK/commits/4367ca4/CHANGELOG.md
[4.0.0]: https://github.com/Creed-Space/VCP-SDK/commits/4367ca4/CHANGELOG.md
[3.1.0]: https://github.com/Creed-Space/VCP-SDK/commits/4367ca4/CHANGELOG.md
[1.1.0]: https://github.com/Creed-Space/VCP-SDK/commit/589db58
[1.0.0]: https://github.com/Creed-Space/VCP-SDK/commits/589db58/CHANGELOG.md
