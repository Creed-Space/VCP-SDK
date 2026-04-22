import { describe, it, expect } from 'vitest';
import {
  buildContext,
  conformanceLevel,
  contextFromJSON,
  contextToJSON,
  decodeContext,
  decodePersonalState,
  emptyContext,
  encodeContext,
  encodePersonalState,
  makePersonalState,
  PERSONAL_SEPARATOR,
  PERSONAL_STATE_ORDER,
  PERSONAL_STATE_SPECS,
  PersonalStateDimension,
  SITUATIONAL_ORDER,
  SITUATIONAL_SPECS,
  SituationalDimension,
  type VCPContext,
} from '../src/extensions/context.js';

// ───────────────────────────────────────────────────────────────────────────
// Specs & ordering
// ───────────────────────────────────────────────────────────────────────────

describe('SituationalDimension specs', () => {
  it('defines 13 situational dimensions with unique positions 1..13', () => {
    expect(SITUATIONAL_ORDER.length).toBe(13);
    const positions = SITUATIONAL_ORDER.map((d) => SITUATIONAL_SPECS[d].position);
    expect([...positions].sort((a, b) => a - b)).toEqual([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]);
  });

  it('SYSTEM_CONTEXT is at position 9 (replacing deprecated STATE)', () => {
    expect(SITUATIONAL_SPECS.system_context.position).toBe(9);
    // Deprecated STATE must not appear in the enum.
    expect((SituationalDimension as Record<string, unknown>).STATE).toBeUndefined();
  });

  it('VEP-0004 dims are positions 10-13', () => {
    const vep = SITUATIONAL_ORDER.filter((d) => SITUATIONAL_SPECS[d].isVep0004);
    expect(new Set(vep)).toEqual(
      new Set(['embodiment', 'proximity', 'relationship', 'formality']),
    );
    for (const dim of vep) {
      const p = SITUATIONAL_SPECS[dim].position;
      expect(p).toBeGreaterThanOrEqual(10);
      expect(p).toBeLessThanOrEqual(13);
    }
  });

  it('RELATIONSHIP is free-form; TIME is not', () => {
    expect(SITUATIONAL_SPECS.relationship.freeForm).toBe(true);
    expect(SITUATIONAL_SPECS.time.freeForm).toBe(false);
  });

  it('CULTURE encodes communication styles, not nationalities', () => {
    const names = new Set(Object.values(SITUATIONAL_SPECS.culture.values));
    const forbidden = new Set(['american', 'european', 'japanese', 'global']);
    for (const f of forbidden) expect(names.has(f)).toBe(false);
    for (const expected of ['high_context', 'low_context', 'formal']) {
      expect(names.has(expected)).toBe(true);
    }
  });
});

describe('PersonalStateDimension specs', () => {
  it('defines 5 personal-state dims with unique positions 1..5', () => {
    expect(PERSONAL_STATE_ORDER.length).toBe(5);
    const positions = PERSONAL_STATE_ORDER.map((d) => PERSONAL_STATE_SPECS[d].position);
    expect([...positions].sort((a, b) => a - b)).toEqual([1, 2, 3, 4, 5]);
  });
});

// ───────────────────────────────────────────────────────────────────────────
// PersonalState
// ───────────────────────────────────────────────────────────────────────────

describe('PersonalState', () => {
  it('round-trips value without intensity', () => {
    const ps = makePersonalState('focused');
    expect(encodePersonalState(ps)).toBe('focused');
    expect(decodePersonalState('focused')).toEqual(ps);
  });

  it('round-trips value with intensity', () => {
    const ps = makePersonalState('calm', 5);
    expect(encodePersonalState(ps)).toBe('calm:5');
    expect(decodePersonalState('calm:5')).toEqual(ps);
  });

  it('rejects out-of-range intensity', () => {
    expect(() => makePersonalState('x', 0)).toThrow(RangeError);
    expect(() => makePersonalState('x', 6)).toThrow(RangeError);
  });

  it('decodes a value containing a colon but non-numeric suffix as raw', () => {
    const ps = decodePersonalState('colleague:professional');
    // Non-numeric suffix → whole string is the value.
    expect(ps).toEqual({ value: 'colleague:professional', intensity: null });
  });
});

// ───────────────────────────────────────────────────────────────────────────
// encode / decode
// ───────────────────────────────────────────────────────────────────────────

describe('VCPContext wire format', () => {
  it('encodes a single situational dim', () => {
    const ctx: VCPContext = {
      situational: { time: ['🌅'] },
      personal: {},
    };
    expect(encodeContext(ctx)).toBe('⏰🌅');
  });

  it('uses ‖ (U+2016) to separate situational and personal bands', () => {
    const ctx: VCPContext = {
      situational: { time: ['🌅'] },
      personal: { cognitive_state: makePersonalState('focused', 4) },
    };
    const encoded = encodeContext(ctx);
    expect(encoded.includes(PERSONAL_SEPARATOR)).toBe(true);
    expect(encoded.includes('‖🧠focused:4')).toBe(true);
  });

  it('encodes a VEP-0004 RELATIONSHIP value as a free-form string', () => {
    const ctx: VCPContext = {
      situational: { relationship: ['colleague:professional'] },
      personal: {},
    };
    expect(encodeContext(ctx)).toBe('🪢colleague:professional');
  });

  it('encodes the canonical 18-dim spec example', () => {
    const ctx: VCPContext = {
      situational: {
        time: ['🌅'],
        space: ['🏢'],
        company: ['👔'],
        occasion: ['💼'],
        embodiment: ['✋'],
        proximity: ['🤏'],
        relationship: ['colleague:professional'],
        formality: ['💼'],
      },
      personal: {
        cognitive_state: makePersonalState('focused', 4),
        emotional_tone: makePersonalState('calm', 5),
        energy_level: makePersonalState('rested', 4),
        perceived_urgency: makePersonalState('unhurried', 2),
        body_signals: makePersonalState('neutral', 1),
      },
    };
    const expected =
      '⏰🌅|📍🏢|👥👔|🎭💼|🧍✋|↔️🤏|🪢colleague:professional|🎩💼' +
      PERSONAL_SEPARATOR +
      '🧠focused:4|💭calm:5|🔋rested:4|⚡unhurried:2|🩺neutral:1';
    expect(encodeContext(ctx)).toBe(expected);
  });

  it('decodes an empty string to an empty context', () => {
    const ctx = decodeContext('');
    expect(ctx).toEqual(emptyContext());
  });

  it('round-trips a core situational-only context', () => {
    const original: VCPContext = {
      situational: { time: ['🌅'], space: ['🏡'] },
      personal: {},
    };
    const decoded = decodeContext(encodeContext(original));
    expect(decoded.situational.time).toEqual(['🌅']);
    expect(decoded.situational.space).toEqual(['🏡']);
  });

  it('round-trips the full 18-dim context', () => {
    const original: VCPContext = {
      situational: {
        time: ['🌅'],
        embodiment: ['✋'],
        proximity: ['🤏'],
        relationship: ['colleague:professional'],
        formality: ['💼'],
      },
      personal: {
        cognitive_state: makePersonalState('focused', 4),
        emotional_tone: makePersonalState('calm', 5),
      },
    };
    const decoded = decodeContext(encodeContext(original));
    expect(decoded.situational.relationship).toEqual(['colleague:professional']);
    expect(decoded.situational.embodiment).toEqual(['✋']);
    expect(decoded.personal.cognitive_state).toEqual({ value: 'focused', intensity: 4 });
    expect(decoded.personal.emotional_tone).toEqual({ value: 'calm', intensity: 5 });
  });
});

// ───────────────────────────────────────────────────────────────────────────
// JSON
// ───────────────────────────────────────────────────────────────────────────

describe('VCPContext JSON', () => {
  it('serialises empty context to the v3.2 nested shape', () => {
    const data = contextToJSON(emptyContext());
    expect(data.situational).toBeDefined();
    expect(data.personal).toBeDefined();
    for (const dim of SITUATIONAL_ORDER) {
      expect(data.situational[dim]).toEqual([]);
    }
  });

  it('round-trips through JSON', () => {
    const original: VCPContext = {
      situational: { time: ['🌅'], company: ['👶'] },
      personal: { emotional_tone: makePersonalState('calm', 5) },
    };
    const data = contextToJSON(original);
    const restored = contextFromJSON(data);
    expect(restored.situational.time).toEqual(['🌅']);
    expect(restored.situational.company).toEqual(['👶']);
    expect(restored.personal.emotional_tone).toEqual({ value: 'calm', intensity: 5 });
  });

  it('accepts the legacy flat shape for situational-only contexts', () => {
    const legacy = { time: ['🌅'], space: ['🏡'] };
    const ctx = contextFromJSON(legacy);
    expect(ctx.situational.time).toEqual(['🌅']);
    expect(ctx.situational.space).toEqual(['🏡']);
  });
});

// ───────────────────────────────────────────────────────────────────────────
// Encoder (keyword-style builder)
// ───────────────────────────────────────────────────────────────────────────

describe('buildContext', () => {
  it('resolves situational names to emojis', () => {
    const ctx = buildContext({ time: 'morning', space: 'home' });
    expect(ctx.situational.time).toEqual(['🌅']);
    expect(ctx.situational.space).toEqual(['🏡']);
  });

  it('encodes RELATIONSHIP as a free-form compound string', () => {
    const ctx = buildContext({ relationship: 'colleague:professional' });
    expect(ctx.situational.relationship).toEqual(['colleague:professional']);
  });

  it('rejects legacy nationality values on CULTURE', () => {
    const ctx = buildContext({ culture: 'american' });
    expect(ctx.situational.culture).toBeUndefined();
  });

  it('accepts CULTURE communication-style values', () => {
    const ctx = buildContext({ culture: 'high_context' });
    expect(ctx.situational.culture).toEqual(['🔇']);
  });

  it('supports personal-state inline "value:intensity" strings', () => {
    const ctx = buildContext({ emotional_tone: 'calm:5' });
    expect(ctx.personal.emotional_tone).toEqual({ value: 'calm', intensity: 5 });
  });

  it('supports personal-state [value, intensity] tuples', () => {
    const ctx = buildContext({ cognitive_state: ['focused', 4] });
    expect(ctx.personal.cognitive_state).toEqual({ value: 'focused', intensity: 4 });
  });
});

// ───────────────────────────────────────────────────────────────────────────
// Conformance classification
// ───────────────────────────────────────────────────────────────────────────

describe('conformanceLevel', () => {
  it('classifies a core-only context as VCP-Minimal', () => {
    const ctx = buildContext({ time: 'morning' });
    expect(conformanceLevel(ctx)).toBe('VCP-Minimal');
  });

  it('classifies core + personal as VCP-Standard', () => {
    const ctx = buildContext({ time: 'morning', cognitive_state: 'focused:4' });
    expect(conformanceLevel(ctx)).toBe('VCP-Standard');
  });

  it('classifies any VEP-0004 dim as VCP-Extended', () => {
    const ctx = buildContext({ embodiment: 'manipulating' });
    expect(conformanceLevel(ctx)).toBe('VCP-Extended');
  });

  it('Extended wins over Standard when both apply', () => {
    const ctx = buildContext({
      formality: 'professional',
      cognitive_state: 'focused',
    });
    expect(conformanceLevel(ctx)).toBe('VCP-Extended');
  });
});

// Keep reference to avoid unused-imports linter warnings in strict modes.
void PersonalStateDimension;
