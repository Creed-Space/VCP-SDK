/**
 * VCP/A Adaptation Layer context encoder (v3.2) — TypeScript.
 *
 * Mirrors `vcp.adaptation.context` in the Python SDK:
 * 13 situational dimensions (incl. VEP-0004 positions 10-13)
 * plus 5 personal-state dimensions (R-line) with optional 1-5 intensity.
 *
 * Wire format:
 *   <situational>‖<personal>
 * where ‖ is U+2016 DOUBLE VERTICAL LINE. The personal band and its
 * separator are omitted when no personal dimensions are set.
 *
 * Example:
 *   ⏰🌅|📍🏢|👥👔|🎭💼|🧍✋|↔️🤏|🪢colleague:professional|🎩💼‖🧠focused:4|💭calm:5
 *
 * The categorical value vocabularies for personal-state dims are canonically
 * defined in ./personal.ts (decay-aware model). This module is purely the
 * wire-format encoder and treats personal values as opaque strings.
 */

// ────────────────────────────────────────────────────────────────────────────
// Wire-format constants
// ────────────────────────────────────────────────────────────────────────────

export const PERSONAL_SEPARATOR = '\u2016'; // ‖
export const DIM_SEPARATOR = '|';
export const INTENSITY_SEPARATOR = ':';

// ────────────────────────────────────────────────────────────────────────────
// Situational dimensions
// ────────────────────────────────────────────────────────────────────────────

export const SituationalDimension = {
  TIME: 'time',
  SPACE: 'space',
  COMPANY: 'company',
  CULTURE: 'culture',
  OCCASION: 'occasion',
  ENVIRONMENT: 'environment',
  AGENCY: 'agency',
  CONSTRAINTS: 'constraints',
  SYSTEM_CONTEXT: 'system_context',
  // VEP-0004 (positions 10-13)
  EMBODIMENT: 'embodiment',
  PROXIMITY: 'proximity',
  RELATIONSHIP: 'relationship',
  FORMALITY: 'formality',
} as const;

export type SituationalDimension =
  (typeof SituationalDimension)[keyof typeof SituationalDimension];

export interface SituationalDimensionSpec {
  readonly name: SituationalDimension;
  readonly symbol: string;
  readonly position: number;
  /** Emoji → human-readable value name. Empty for free-form dims. */
  readonly values: Readonly<Record<string, string>>;
  /** Whether this dim accepts raw-string values (RELATIONSHIP compound). */
  readonly freeForm: boolean;
  /** Whether this dim was introduced in VEP-0004 (positions 10-13). */
  readonly isVep0004: boolean;
}

export const SITUATIONAL_SPECS: Readonly<
  Record<SituationalDimension, SituationalDimensionSpec>
> = {
  time: {
    name: 'time',
    symbol: '⏰',
    position: 1,
    values: {
      '🌅': 'morning',
      '☀️': 'daytime',
      '🌆': 'evening',
      '🌙': 'night',
      '📅': 'weekday',
      '🎉': 'weekend',
      '⏰': 'time_pressure',
      '📆': 'scheduled',
      '🔄': 'recurring',
    },
    freeForm: false,
    isVep0004: false,
  },
  space: {
    name: 'space',
    symbol: '📍',
    position: 2,
    values: {
      '🏡': 'home',
      '🏢': 'office',
      '🏫': 'school',
      '🏥': 'hospital',
      '⛪': 'religious',
      '🏛️': 'government',
      '🏪': 'commercial',
      '🚗': 'vehicle',
      '🌳': 'outdoor',
      '💻': 'digital',
      '🏠': 'shared_space',
      '🔒': 'secure_facility',
    },
    freeForm: false,
    isVep0004: false,
  },
  company: {
    name: 'company',
    symbol: '👥',
    position: 3,
    values: {
      '👤': 'alone',
      '👶': 'children',
      '👨\u200d👩\u200d👧': 'family',
      '👔': 'colleagues',
      '👨\u200d🏫': 'teacher',
      '👮': 'authority',
      '👴': 'elders',
      '💑': 'partner',
      '🤝': 'peers',
      '👨\u200d⚕️': 'professional',
      '🧑\u200d🤝\u200d🧑': 'strangers',
      '👥': 'crowd',
      '🐕': 'pets',
    },
    freeForm: false,
    isVep0004: false,
  },
  culture: {
    name: 'culture',
    symbol: '🌍',
    position: 4,
    // Communication styles per VCP/A §2.1 and §2.2, NOT nationalities.
    values: {
      '🔇': 'high_context',
      '📢': 'low_context',
      '🎩': 'formal',
      '👋': 'informal',
      '📊': 'hierarchical',
      '⚖️': 'egalitarian',
      '👥': 'collectivist',
      '👤': 'individualist',
    },
    freeForm: false,
    isVep0004: false,
  },
  occasion: {
    name: 'occasion',
    symbol: '🎭',
    position: 5,
    values: {
      '➖': 'normal',
      '🎂': 'celebration',
      '💼': 'business',
      '⚰️': 'mourning',
      '💒': 'ceremony',
      '🏥': 'medical',
      '🚨': 'emergency',
      '👨\u200d🏫': 'educational',
      '🎪': 'entertainment',
      '⚖️': 'legal',
      '🗳️': 'political',
      '🎓': 'graduation',
    },
    freeForm: false,
    isVep0004: false,
  },
  environment: {
    name: 'environment',
    symbol: '🌡️',
    position: 6,
    values: {
      '🥵': 'hot',
      '🥶': 'cold',
      '🌧️': 'wet',
      '🌪️': 'dangerous',
      '🔇': 'quiet',
      '📢': 'loud',
      '🔥': 'fire',
      '💨': 'windy',
      '🌫️': 'poor_visibility',
      '🌤️': 'outdoors',
      '🏔️': 'high_altitude',
      '🌊': 'near_water',
    },
    freeForm: false,
    isVep0004: false,
  },
  agency: {
    name: 'agency',
    symbol: '🔷',
    position: 7,
    values: {
      '👑': 'leader',
      '🤝': 'peer',
      '👇': 'subordinate',
      '💰': 'wealthy',
      '💵': 'adequate',
      '🕳️': 'scarce',
      '🏡': 'owner',
      '🔑': 'authorized',
      '🎓': 'expert',
      '🆓': 'autonomous',
      '🔐': 'limited',
      '🏃': 'mobile',
    },
    freeForm: false,
    isVep0004: false,
  },
  constraints: {
    name: 'constraints',
    symbol: '🔶',
    position: 8,
    values: {
      '○': 'minimal',
      '🚧': 'physical',
      '⚖️': 'legal',
      '💸': 'economic',
      '⏰': 'time',
      '🤐': 'social',
      '📱': 'surveillance',
      '🚨': 'emergency',
      '👮': 'enforcement',
      '📜': 'contractual',
      '🏥': 'medical',
      '🔒': 'confidential',
    },
    freeForm: false,
    isVep0004: false,
  },
  system_context: {
    name: 'system_context',
    symbol: '📡',
    position: 9,
    // Computing environment per VCP/A §2.1 and §2.2.
    values: {
      '💻': 'personal_device',
      '🏢': 'workplace_system',
      '🖥️': 'shared_terminal',
      '👁️': 'monitored_environment',
    },
    freeForm: false,
    isVep0004: false,
  },
  embodiment: {
    name: 'embodiment',
    symbol: '🧍',
    position: 10,
    values: {
      '🪑': 'stationary',
      '🚶': 'navigating',
      '✋': 'manipulating',
      '📦': 'carrying',
      '🛑': 'emergency_stop',
    },
    freeForm: false,
    isVep0004: true,
  },
  proximity: {
    name: 'proximity',
    symbol: '↔️',
    position: 11,
    values: {
      '🌐': 'distant',
      '🏠': 'same_room',
      '👣': 'nearby',
      '🤏': 'close',
      '👆': 'contact',
    },
    freeForm: false,
    isVep0004: true,
  },
  relationship: {
    name: 'relationship',
    symbol: '🪢',
    position: 12,
    // Free-form compound: "{tie}:{function}"
    values: {},
    freeForm: true,
    isVep0004: true,
  },
  formality: {
    name: 'formality',
    symbol: '🎩',
    position: 13,
    values: {
      '😎': 'casual',
      '💼': 'professional',
      '🎓': 'formal',
      '🏛️': 'ceremonial',
    },
    freeForm: false,
    isVep0004: true,
  },
};

/** Situational dims in canonical position order. */
export const SITUATIONAL_ORDER: readonly SituationalDimension[] = [
  'time',
  'space',
  'company',
  'culture',
  'occasion',
  'environment',
  'agency',
  'constraints',
  'system_context',
  'embodiment',
  'proximity',
  'relationship',
  'formality',
];

// ────────────────────────────────────────────────────────────────────────────
// Personal-state dimensions (R-line)
// ────────────────────────────────────────────────────────────────────────────

export const PersonalStateDimension = {
  COGNITIVE_STATE: 'cognitive_state',
  EMOTIONAL_TONE: 'emotional_tone',
  ENERGY_LEVEL: 'energy_level',
  PERCEIVED_URGENCY: 'perceived_urgency',
  BODY_SIGNALS: 'body_signals',
} as const;

export type PersonalStateDimension =
  (typeof PersonalStateDimension)[keyof typeof PersonalStateDimension];

export interface PersonalStateDimensionSpec {
  readonly name: PersonalStateDimension;
  readonly symbol: string;
  readonly position: number;
}

export const PERSONAL_STATE_SPECS: Readonly<
  Record<PersonalStateDimension, PersonalStateDimensionSpec>
> = {
  cognitive_state: { name: 'cognitive_state', symbol: '🧠', position: 1 },
  emotional_tone: { name: 'emotional_tone', symbol: '💭', position: 2 },
  energy_level: { name: 'energy_level', symbol: '🔋', position: 3 },
  perceived_urgency: { name: 'perceived_urgency', symbol: '⚡', position: 4 },
  body_signals: { name: 'body_signals', symbol: '🩺', position: 5 },
};

export const PERSONAL_STATE_ORDER: readonly PersonalStateDimension[] = [
  'cognitive_state',
  'emotional_tone',
  'energy_level',
  'perceived_urgency',
  'body_signals',
];

/** A personal-state value with optional 1-5 intensity. */
export interface PersonalState {
  readonly value: string;
  readonly intensity: number | null;
}

export function makePersonalState(
  value: string,
  intensity: number | null = null,
): PersonalState {
  if (intensity !== null && (intensity < 1 || intensity > 5 || !Number.isInteger(intensity))) {
    throw new RangeError(
      `PersonalState intensity must be an integer 1-5 or null, got ${String(intensity)}`,
    );
  }
  return { value, intensity };
}

export function encodePersonalState(state: PersonalState): string {
  if (state.intensity === null) {
    return state.value;
  }
  return `${state.value}${INTENSITY_SEPARATOR}${state.intensity}`;
}

/**
 * Decode a personal-state segment such as `focused:4` or `calm`. An intensity
 * is exactly one digit from 1 to 5 (VCP/A §2.3); `04`, `0`, `6`, `+4` or any
 * other text after `:` throws a `SyntaxError`.
 */
export function decodePersonalState(segment: string): PersonalState {
  const idx = segment.lastIndexOf(INTENSITY_SEPARATOR);
  if (idx === -1) {
    return { value: segment, intensity: null };
  }
  const raw = segment.slice(idx + 1);
  if (!/^[1-5]$/.test(raw)) {
    throw new SyntaxError(`personal-state intensity must be one digit 1-5, got '${raw}'`);
  }
  return { value: segment.slice(0, idx), intensity: Number(raw) };
}

// ────────────────────────────────────────────────────────────────────────────
// VCPContext
// ────────────────────────────────────────────────────────────────────────────

export interface VCPContext {
  readonly situational: Readonly<Partial<Record<SituationalDimension, readonly string[]>>>;
  readonly personal: Readonly<Partial<Record<PersonalStateDimension, PersonalState>>>;
  /**
   * Raw groups whose dimension symbol is not recognized, in order, so a relay
   * passes them through unchanged (VCP/A §2.3). They take no part in
   * adaptation. Omitted when there are none.
   */
  readonly unknown?: {
    readonly situational: readonly string[];
    readonly personal: readonly string[];
  };
}

export function emptyContext(): VCPContext {
  return { situational: {}, personal: {} };
}

// ── Wire encode ──────────────────────────────────────────────────────────

export function encodeContext(ctx: VCPContext): string {
  const sitParts: string[] = [];
  for (const dim of SITUATIONAL_ORDER) {
    const values = ctx.situational[dim];
    if (!values || values.length === 0) continue;
    const spec = SITUATIONAL_SPECS[dim];
    sitParts.push(`${spec.symbol}${values.join('')}`);
  }
  // Unknown dimension groups are relayed unchanged (VCP/A §2.3).
  sitParts.push(...(ctx.unknown?.situational ?? []));
  const situational = sitParts.join(DIM_SEPARATOR);

  const perParts: string[] = [];
  for (const dim of PERSONAL_STATE_ORDER) {
    const state = ctx.personal[dim];
    if (!state) continue;
    const spec = PERSONAL_STATE_SPECS[dim];
    perParts.push(`${spec.symbol}${encodePersonalState(state)}`);
  }
  perParts.push(...(ctx.unknown?.personal ?? []));
  if (perParts.length === 0) {
    return situational;
  }
  const personal = perParts.join(DIM_SEPARATOR);
  if (situational === '') {
    return PERSONAL_SEPARATOR + personal;
  }
  return `${situational}${PERSONAL_SEPARATOR}${personal}`;
}

// ── Wire decode ──────────────────────────────────────────────────────────

const VS16 = '\uFE0F';

/**
 * Return the content after a dimension symbol, accepting both the canonical
 * VS16-qualified symbol and its bare form (fixture vep-011: parsers MUST
 * accept both). Mirrors the Python `_after_dimension_symbol`.
 */
function afterDimensionSymbol(part: string, symbol: string): string | null {
  const candidates = [...new Set([symbol, symbol.replaceAll(VS16, '')])].sort(
    (a, b) => b.length - a.length,
  );
  for (const candidate of candidates) {
    if (part.startsWith(candidate)) return part.slice(candidate.length);
  }
  return null;
}

/**
 * Decode a finite vocabulary without splitting ZWJ sequences or dropping
 * VS16-qualified symbols. Mirrors the Python `_extract_known_values`: the
 * scanner takes the longest alias at each position and returns [] as soon as
 * an unknown value is encountered so the caller can fall back to the raw part.
 */
function extractKnownValues(raw: string, spec: SituationalDimensionSpec): string[] {
  const aliases: Array<[alias: string, canonical: string]> = [];
  for (const canonical of Object.keys(spec.values)) {
    aliases.push([canonical, canonical]);
    const bare = canonical.replaceAll(VS16, '');
    if (bare !== canonical) aliases.push([bare, canonical]);
  }
  aliases.sort((a, b) => b[0].length - a[0].length);

  const values: string[] = [];
  let cursor = 0;
  while (cursor < raw.length) {
    const match = aliases.find(([alias]) => raw.startsWith(alias, cursor));
    if (!match) return [];
    values.push(match[1]);
    cursor += match[0].length;
  }
  return values;
}

/**
 * Decode a context wire string.
 *
 * Receivers are forward compatible (VCP/A §2.3): a value outside the §2.2 or
 * §3.1 vocabularies is kept as a raw string, and a group whose dimension
 * symbol is not recognized is kept in `unknown` and re-encoded unchanged. A
 * malformed string (an empty group, a group that does not begin with an
 * emoji, a dimension with no value, an intensity outside 1-5) throws a
 * `SyntaxError`. Use {@link validateContextWire} for
 * strict validation.
 */
export function decodeContext(encoded: string): VCPContext {
  if (encoded === '') return emptyContext();

  let sitPart = encoded;
  let perPart = '';
  const sepIdx = encoded.indexOf(PERSONAL_SEPARATOR);
  if (sepIdx !== -1) {
    sitPart = encoded.slice(0, sepIdx);
    perPart = encoded.slice(sepIdx + PERSONAL_SEPARATOR.length);
    if (perPart === '') throw new SyntaxError('personal band is empty after the separator');
  }

  const situational: Partial<Record<SituationalDimension, string[]>> = {};
  const unknownSituational: string[] = [];
  if (sitPart !== '') {
    for (const part of sitPart.split(DIM_SEPARATOR)) {
      if (!part) throw new SyntaxError('situational band contains an empty group');
      let matched = false;
      for (const dim of SITUATIONAL_ORDER) {
        const spec = SITUATIONAL_SPECS[dim];
        const raw = afterDimensionSymbol(part, spec.symbol);
        if (raw === null) continue;
        matched = true;
        if (!raw) throw new SyntaxError(`situational dimension ${dim} has no value`);
        if (spec.freeForm) {
          situational[dim] = [raw];
        } else {
          const values = extractKnownValues(raw, spec);
          // Unknown value: keep the raw text (VCP/A §2.3).
          situational[dim] = values.length > 0 ? values : [raw];
        }
        break;
      }
      if (!matched) {
        if (part.charCodeAt(0) < 0x80) {
          throw new SyntaxError(`situational group must start with a dimension emoji: ${part}`);
        }
        unknownSituational.push(part);
      }
    }
  }

  const personal: Partial<Record<PersonalStateDimension, PersonalState>> = {};
  const unknownPersonal: string[] = [];
  if (perPart !== '') {
    for (const part of perPart.split(DIM_SEPARATOR)) {
      if (!part) throw new SyntaxError('personal band contains an empty group');
      const dim = PERSONAL_STATE_ORDER.find((candidate) =>
        part.startsWith(PERSONAL_STATE_SPECS[candidate].symbol),
      );
      if (dim === undefined) {
        if (part.charCodeAt(0) < 0x80) {
          throw new SyntaxError(`personal group must start with a dimension emoji: ${part}`);
        }
        unknownPersonal.push(part);
        continue;
      }
      const raw = part.slice(PERSONAL_STATE_SPECS[dim].symbol.length);
      if (!raw) throw new SyntaxError(`personal dimension ${dim} has no value`);
      personal[dim] = decodePersonalState(raw);
    }
  }

  const context: VCPContext = { situational, personal };
  if (unknownSituational.length > 0 || unknownPersonal.length > 0) {
    return { ...context, unknown: { situational: unknownSituational, personal: unknownPersonal } };
  }
  return context;
}

/** RELATIONSHIP vocabulary (VCP/A §2.2, schema `relationship_value`). */
const RELATIONSHIP_CANONICAL =
  /^(?:(?:stranger|acquaintance|colleague|friend|family|intimate|long_term|trusted_collaborator)(?::(?:transactional|professional|educational|therapeutic|social|intimate|adversarial))?|:(?:transactional|professional|educational|therapeutic|social|intimate|adversarial))$/;

/** Canonical personal-state categories (VCP/A §3.1). */
export const PERSONAL_STATE_CATEGORIES: Readonly<Record<PersonalStateDimension, readonly string[]>> = {
  cognitive_state: ['focused', 'distracted', 'overloaded', 'foggy', 'reflective'],
  emotional_tone: ['calm', 'tense', 'frustrated', 'neutral', 'uplifted'],
  energy_level: ['rested', 'low_energy', 'fatigued', 'wired', 'depleted'],
  perceived_urgency: ['unhurried', 'time_aware', 'pressured', 'critical'],
  body_signals: ['neutral', 'discomfort', 'pain', 'unwell', 'recovering'],
};

/**
 * Strictly validate a context wire string (VCP/A §2.3). Returns one message
 * per unknown value or dimension group, or a single `malformed:` message; an
 * empty array means the string uses only canonical vocabulary. Mirrors the
 * Python `validate_context_wire`.
 */
export function validateContextWire(encoded: string): string[] {
  let context: VCPContext;
  try {
    context = decodeContext(encoded);
  } catch (error) {
    return [`malformed: ${error instanceof Error ? error.message : String(error)}`];
  }
  const issues: string[] = [];
  for (const group of context.unknown?.situational ?? []) {
    issues.push(`unknown situational dimension group: '${group}'`);
  }
  for (const dim of Object.keys(context.situational) as SituationalDimension[]) {
    const spec = SITUATIONAL_SPECS[dim];
    for (const value of context.situational[dim] ?? []) {
      const known = spec.freeForm
        ? RELATIONSHIP_CANONICAL.test(value)
        : Object.prototype.hasOwnProperty.call(spec.values, value);
      if (!known) issues.push(`unknown ${dim} value: '${value}'`);
    }
  }
  for (const group of context.unknown?.personal ?? []) {
    issues.push(`unknown personal dimension group: '${group}'`);
  }
  for (const dim of Object.keys(context.personal) as PersonalStateDimension[]) {
    const state = context.personal[dim];
    if (state && !PERSONAL_STATE_CATEGORIES[dim].includes(state.value)) {
      issues.push(`unknown ${dim} category: '${state.value}'`);
    }
  }
  return issues;
}

// ── JSON shape ───────────────────────────────────────────────────────────
// VCPContextJSON is the cross-SDK serialization shape shared with the Python
// `VCPContext.to_json()` output and the conformance fixtures' `input` objects.
// It is NOT the `parsed` object of schemas/vcp-adaptation-context.schema.json
// (that document wraps the wire string as `context` and omits empty arrays).

export interface VCPContextJSON {
  situational: Record<string, string[]>;
  personal: Record<string, { value: string; intensity: number | null }>;
  /** Present only when the context carries unknown dimension groups. */
  unknown?: { situational: string[]; personal: string[] };
}

export function contextToJSON(ctx: VCPContext): VCPContextJSON {
  const situational: Record<string, string[]> = {};
  for (const dim of SITUATIONAL_ORDER) {
    situational[dim] = [...(ctx.situational[dim] ?? [])];
  }
  const personal: Record<string, { value: string; intensity: number | null }> = {};
  for (const dim of PERSONAL_STATE_ORDER) {
    const state = ctx.personal[dim];
    if (state) {
      personal[dim] = { value: state.value, intensity: state.intensity };
    }
  }
  const json: VCPContextJSON = { situational, personal };
  if (ctx.unknown && (ctx.unknown.situational.length > 0 || ctx.unknown.personal.length > 0)) {
    json.unknown = {
      situational: [...ctx.unknown.situational],
      personal: [...ctx.unknown.personal],
    };
  }
  return json;
}

export function contextFromJSON(data: unknown): VCPContext {
  if (!data || typeof data !== 'object') return emptyContext();
  const obj = data as Record<string, unknown>;
  const situational: Partial<Record<SituationalDimension, string[]>> = {};
  const personal: Partial<Record<PersonalStateDimension, PersonalState>> = {};

  // Accept v3.2 nested shape or legacy flat shape.
  const sitSrc = (obj.situational && typeof obj.situational === 'object'
    ? (obj.situational as Record<string, unknown>)
    : obj) as Record<string, unknown>;
  const perSrc =
    obj.personal && typeof obj.personal === 'object'
      ? (obj.personal as Record<string, unknown>)
      : {};

  for (const dim of SITUATIONAL_ORDER) {
    const raw = sitSrc[dim];
    if (Array.isArray(raw) && raw.length > 0) {
      situational[dim] = raw.map(String);
    } else if (typeof raw === 'string' && raw) {
      situational[dim] = [raw];
    }
  }
  for (const dim of PERSONAL_STATE_ORDER) {
    const raw = perSrc[dim];
    if (!raw) continue;
    if (typeof raw === 'string') {
      personal[dim] = decodePersonalState(raw);
    } else if (typeof raw === 'object') {
      const { value, intensity } = raw as { value?: unknown; intensity?: unknown };
      if (typeof value === 'string') {
        personal[dim] = makePersonalState(
          value,
          typeof intensity === 'number' ? intensity : null,
        );
      }
    }
  }
  const unknown = obj.unknown as { situational?: unknown; personal?: unknown } | undefined;
  const strings = (value: unknown): string[] =>
    Array.isArray(value) ? value.filter((item): item is string => typeof item === 'string' && item !== '') : [];
  const unknownSituational = strings(unknown?.situational);
  const unknownPersonal = strings(unknown?.personal);
  if (unknownSituational.length > 0 || unknownPersonal.length > 0) {
    return { situational, personal, unknown: { situational: unknownSituational, personal: unknownPersonal } };
  }
  return { situational, personal };
}

// ── Conformance classification ───────────────────────────────────────────

export type ConformanceLevel = 'VCP-Minimal' | 'VCP-Standard' | 'VCP-Extended';

export function conformanceLevel(ctx: VCPContext): ConformanceLevel {
  for (const dim of SITUATIONAL_ORDER) {
    if (SITUATIONAL_SPECS[dim].isVep0004 && ctx.situational[dim]?.length) {
      return 'VCP-Extended';
    }
  }
  for (const dim of PERSONAL_STATE_ORDER) {
    if (ctx.personal[dim]) {
      return 'VCP-Standard';
    }
  }
  return 'VCP-Minimal';
}

// ── Encoder (keyword-style builder, mirrors Python ContextEncoder) ───────

export interface EncoderInput {
  // Core 9 situational
  time?: string;
  space?: string;
  company?: string | string[];
  culture?: string | string[];
  occasion?: string;
  environment?: string;
  agency?: string;
  constraints?: string | string[];
  system_context?: string;
  // VEP-0004
  embodiment?: string;
  proximity?: string;
  /** Raw compound "{tie}:{function}" */
  relationship?: string;
  formality?: string;
  // Personal-state (R-line). Either a bare value string ("focused"),
  // a "value:intensity" string ("focused:4"), or [value, intensity].
  cognitive_state?: string | [string, number];
  emotional_tone?: string | [string, number];
  energy_level?: string | [string, number];
  perceived_urgency?: string | [string, number];
  body_signals?: string | [string, number];
}

/**
 * Retired value names that {@link buildContext} still resolves to the
 * canonical VCP/A §2.2 value that replaced them. Deprecated: pass the
 * canonical name. The retired CULTURE `mixed`, ENVIRONMENT `comfortable` and
 * every retired SYSTEM_CONTEXT value (online, degraded, offline, sandboxed,
 * testing) have no equivalent and are dropped like any other unknown name.
 */
const DEPRECATED_VALUE_NAMES: Readonly<
  Partial<Record<SituationalDimension, Readonly<Record<string, string>>>>
> = {
  time: { midday: 'daytime' },
  space: { transit: 'vehicle' },
  culture: { casual: 'informal' },
  environment: { noisy: 'loud' },
};

function lookupEmoji(spec: SituationalDimensionSpec, value: string): string | null {
  if (!value) return null;
  // Pass-through: value is already a registered emoji.
  if (Object.prototype.hasOwnProperty.call(spec.values, value)) return value;
  const lower = value.toLowerCase();
  for (const [emoji, name] of Object.entries(spec.values)) {
    if (name === lower) return emoji;
  }
  const aliases = DEPRECATED_VALUE_NAMES[spec.name];
  if (aliases && Object.prototype.hasOwnProperty.call(aliases, lower)) {
    return lookupEmoji(spec, aliases[lower]);
  }
  return null;
}

export function buildContext(input: EncoderInput): VCPContext {
  const situational: Partial<Record<SituationalDimension, string[]>> = {};
  const personal: Partial<Record<PersonalStateDimension, PersonalState>> = {};

  const sitEntries: Array<[SituationalDimension, string | string[] | undefined]> = [
    ['time', input.time],
    ['space', input.space],
    ['company', input.company],
    ['culture', input.culture],
    ['occasion', input.occasion],
    ['environment', input.environment],
    ['agency', input.agency],
    ['constraints', input.constraints],
    ['system_context', input.system_context],
    ['embodiment', input.embodiment],
    ['proximity', input.proximity],
    ['relationship', input.relationship],
    ['formality', input.formality],
  ];

  for (const [dim, value] of sitEntries) {
    if (value === undefined || value === null) continue;
    const spec = SITUATIONAL_SPECS[dim];
    if (spec.freeForm) {
      if (typeof value === 'string') situational[dim] = [value];
      continue;
    }
    if (typeof value === 'string') {
      const emoji = lookupEmoji(spec, value);
      if (emoji) situational[dim] = [emoji];
    } else if (Array.isArray(value)) {
      const emojis = value
        .map((v) => lookupEmoji(spec, v))
        .filter((v): v is string => v !== null);
      if (emojis.length > 0) situational[dim] = emojis;
    }
  }

  const perEntries: Array<[PersonalStateDimension, string | [string, number] | undefined]> = [
    ['cognitive_state', input.cognitive_state],
    ['emotional_tone', input.emotional_tone],
    ['energy_level', input.energy_level],
    ['perceived_urgency', input.perceived_urgency],
    ['body_signals', input.body_signals],
  ];

  for (const [dim, raw] of perEntries) {
    if (raw === undefined || raw === null) continue;
    if (Array.isArray(raw)) {
      const [val, intensity] = raw;
      personal[dim] = makePersonalState(val, intensity);
    } else if (typeof raw === 'string') {
      personal[dim] = decodePersonalState(raw);
    }
  }

  return { situational, personal };
}
