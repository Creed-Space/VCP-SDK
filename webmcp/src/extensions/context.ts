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
    values: { '🌅': 'morning', '☀️': 'midday', '🌆': 'evening', '🌙': 'night' },
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
      '🚗': 'transit',
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
      '👔': 'colleagues',
      '👨\u200d👩\u200d👧': 'family',
      '👥': 'strangers',
    },
    freeForm: false,
    isVep0004: false,
  },
  culture: {
    name: 'culture',
    symbol: '🌍',
    position: 4,
    // Communication styles per CSM1 / VCP v3.2 — NOT nationalities.
    values: {
      '🔇': 'high_context',
      '📢': 'low_context',
      '🎩': 'formal',
      '😎': 'casual',
      '🌐': 'mixed',
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
      '😢': 'mourning',
      '🚨': 'emergency',
      '💼': 'business',
    },
    freeForm: false,
    isVep0004: false,
  },
  environment: {
    name: 'environment',
    symbol: '🌡️',
    position: 6,
    values: {
      '☀️': 'comfortable',
      '🥵': 'hot',
      '🥶': 'cold',
      '🔇': 'quiet',
      '🔊': 'noisy',
    },
    freeForm: false,
    isVep0004: false,
  },
  agency: {
    name: 'agency',
    symbol: '🔷',
    position: 7,
    values: { '👑': 'leader', '🤝': 'peer', '📋': 'subordinate', '🔐': 'limited' },
    freeForm: false,
    isVep0004: false,
  },
  constraints: {
    name: 'constraints',
    symbol: '🔶',
    position: 8,
    values: { '○': 'minimal', '⚖️': 'legal', '💸': 'economic', '⏱️': 'time' },
    freeForm: false,
    isVep0004: false,
  },
  system_context: {
    name: 'system_context',
    symbol: '📡',
    position: 9,
    values: {
      '🟢': 'online',
      '🟡': 'degraded',
      '🔴': 'offline',
      '🔒': 'sandboxed',
      '🧪': 'testing',
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

export function decodePersonalState(segment: string): PersonalState {
  const idx = segment.lastIndexOf(INTENSITY_SEPARATOR);
  if (idx === -1) {
    return { value: segment, intensity: null };
  }
  const raw = segment.slice(idx + 1);
  const n = Number.parseInt(raw, 10);
  if (Number.isNaN(n) || n < 1 || n > 5 || String(n) !== raw) {
    // Not an intensity — whole segment is the value.
    return { value: segment, intensity: null };
  }
  return { value: segment.slice(0, idx), intensity: n };
}

// ────────────────────────────────────────────────────────────────────────────
// VCPContext
// ────────────────────────────────────────────────────────────────────────────

export interface VCPContext {
  readonly situational: Readonly<Partial<Record<SituationalDimension, readonly string[]>>>;
  readonly personal: Readonly<Partial<Record<PersonalStateDimension, PersonalState>>>;
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
  const situational = sitParts.join(DIM_SEPARATOR);

  const perParts: string[] = [];
  for (const dim of PERSONAL_STATE_ORDER) {
    const state = ctx.personal[dim];
    if (!state) continue;
    const spec = PERSONAL_STATE_SPECS[dim];
    perParts.push(`${spec.symbol}${encodePersonalState(state)}`);
  }
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

// Regex copied from the Python decoder. Handles most emoji + ZWJ sequences.
const EMOJI_REGEX = new RegExp(
  '[\\u{1F300}-\\u{1F9FF}]' +
    '|[\\u{1F600}-\\u{1F64F}]' +
    '|[\\u{1F680}-\\u{1F6FF}]' +
    '|[\\u{1F1E0}-\\u{1F1FF}]' +
    '|[\\u{2600}-\\u{26FF}]' +
    '|[\\u{2700}-\\u{27BF}]' +
    '|[\\u{25A0}-\\u{25FF}]' +
    '|\\u{2B50}' +
    '|\\u{274C}' +
    '|\\u{2139}' +
    '|\\u{25CB}' +
    '|(?:[\\u{1F468}-\\u{1F469}][\\u{200D}]?)+[\\u{1F466}-\\u{1F469}]?',
  'gu',
);

function extractEmojis(s: string): string[] {
  const matches = s.match(EMOJI_REGEX);
  return matches ? [...matches] : [];
}

export function decodeContext(encoded: string): VCPContext {
  if (encoded === '') return emptyContext();

  let sitPart = encoded;
  let perPart = '';
  const sepIdx = encoded.indexOf(PERSONAL_SEPARATOR);
  if (sepIdx !== -1) {
    sitPart = encoded.slice(0, sepIdx);
    perPart = encoded.slice(sepIdx + PERSONAL_SEPARATOR.length);
  }

  const situational: Partial<Record<SituationalDimension, string[]>> = {};
  for (const part of sitPart.split(DIM_SEPARATOR)) {
    if (!part) continue;
    for (const dim of SITUATIONAL_ORDER) {
      const spec = SITUATIONAL_SPECS[dim];
      if (part.startsWith(spec.symbol)) {
        const raw = part.slice(spec.symbol.length);
        if (!raw) break;
        if (spec.freeForm) {
          situational[dim] = [raw];
        } else {
          const values = extractEmojis(raw);
          situational[dim] = values.length > 0 ? values : [raw];
        }
        break;
      }
    }
  }

  const personal: Partial<Record<PersonalStateDimension, PersonalState>> = {};
  for (const part of perPart.split(DIM_SEPARATOR)) {
    if (!part) continue;
    for (const dim of PERSONAL_STATE_ORDER) {
      const spec = PERSONAL_STATE_SPECS[dim];
      if (part.startsWith(spec.symbol)) {
        const raw = part.slice(spec.symbol.length);
        if (raw) {
          personal[dim] = decodePersonalState(raw);
        }
        break;
      }
    }
  }

  return { situational, personal };
}

// ── JSON shape (matches schemas/vcp-adaptation-context.schema.json v3) ───

export interface VCPContextJSON {
  situational: Record<string, string[]>;
  personal: Record<string, { value: string; intensity: number | null }>;
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
  return { situational, personal };
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
  culture?: string;
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

function lookupEmoji(spec: SituationalDimensionSpec, value: string): string | null {
  if (!value) return null;
  // Pass-through: value is already a registered emoji.
  if (value in spec.values) return value;
  const lower = value.toLowerCase();
  for (const [emoji, name] of Object.entries(spec.values)) {
    if (name === lower) return emoji;
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
