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

  it('rejects any intensity that is not exactly one digit 1-5 (VCP/A 2.3)', () => {
    for (const segment of ['colleague:professional', 'focused:04', 'focused:0', 'focused:6', 'focused:+4', 'focused:', 'focused:٤']) {
      expect(() => decodePersonalState(segment)).toThrow(SyntaxError);
    }
    expect(decodePersonalState('focused:4')).toEqual({ value: 'focused', intensity: 4 });
    expect(() => decodeContext('‖🧠focused:04')).toThrow(SyntaxError);
  });

  it('decodes a personal-only context that begins with the separator', () => {
    const ctx = decodeContext('‖🧠focused:4|💭calm');
    expect(ctx.situational).toEqual({});
    expect(ctx.personal.cognitive_state).toEqual({ value: 'focused', intensity: 4 });
    expect(encodeContext(ctx)).toBe('‖🧠focused:4|💭calm');
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
  it('serializes empty context to the v3.2 nested shape', () => {
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

describe('decodeContext vocabulary scanning', () => {
  it('preserves VS16 and keeps ⏰ in constraints', () => {
    const ctx = decodeContext('🔶⚖️⏰');
    expect(ctx.situational.constraints).toEqual(['⚖️', '⏰']);
  });

  it('preserves VS16 in environment values', () => {
    expect(decodeContext('🌡️🌧️').situational.environment).toEqual(['🌧️']);
  });

  it('does not split ZWJ family sequences', () => {
    expect(decodeContext('👥👨‍👩‍👧👶').situational.company).toEqual(['👨‍👩‍👧', '👶']);
  });

  it('accepts bare (VS16-less) dimension symbols per vep-011', () => {
    expect(decodeContext('↔🌐').situational.proximity).toEqual(['🌐']);
    expect(decodeContext('🌡🌧').situational.environment).toEqual(['🌧️']);
  });

  it('falls back to the raw part for unknown values', () => {
    expect(decodeContext('⏰🦄').situational.time).toEqual(['🦄']);
  });

  it('round-trips every vocabulary value through encode/decode', () => {
    for (const dim of SITUATIONAL_ORDER) {
      const spec = SITUATIONAL_SPECS[dim];
      if (spec.freeForm) continue;
      for (const emoji of Object.keys(spec.values)) {
        const ctx: VCPContext = { situational: { [dim]: [emoji] }, personal: {} };
        expect(decodeContext(encodeContext(ctx))).toEqual(ctx);
      }
    }
  });
});

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

  it('CULTURE vocabulary matches VCP/A §2.1', () => {
    expect(SITUATIONAL_SPECS.culture.values).toEqual({
      '🔇': 'high_context',
      '📢': 'low_context',
      '🎩': 'formal',
      '👋': 'informal',
      '📊': 'hierarchical',
      '⚖️': 'egalitarian',
      '👥': 'collectivist',
      '👤': 'individualist',
    });
  });

  it('SYSTEM_CONTEXT vocabulary matches VCP/A §2.1', () => {
    expect(SITUATIONAL_SPECS.system_context.values).toEqual({
      '💻': 'personal_device',
      '🏢': 'workplace_system',
      '🖥️': 'shared_terminal',
      '👁️': 'monitored_environment',
    });
  });

  it('resolves the deprecated CULTURE name casual to informal', () => {
    expect(buildContext({ culture: 'casual' }).situational.culture).toEqual(['👋']);
    expect(buildContext({ culture: 'mixed' }).situational.culture).toBeUndefined();
  });

  it('drops retired SYSTEM_CONTEXT names', () => {
    for (const retired of ['online', 'degraded', 'offline', 'sandboxed', 'testing']) {
      expect(buildContext({ system_context: retired }).situational.system_context).toBeUndefined();
    }
  });

  it('encodes and decodes the canonical CULTURE and SYSTEM_CONTEXT values', () => {
    const ctx = buildContext({
      culture: ['hierarchical', 'collectivist'],
      system_context: 'monitored_environment',
    });
    const wire = encodeContext(ctx);
    expect(wire).toBe('🌍📊👥|📡👁️');
    const decoded = decodeContext(wire);
    expect(decoded.situational.culture).toEqual(['📊', '👥']);
    expect(decoded.situational.system_context).toEqual(['👁️']);
    expect(decodeContext('📡🖥').situational.system_context).toEqual(['🖥️']);
  });

  it('tolerates retired values on the wire', () => {
    const decoded = decodeContext('🌍😎|📡🟢');
    expect(decoded.situational.culture).toEqual(['😎']);
    expect(decoded.situational.system_context).toEqual(['🟢']);
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

// ───────────────────────────────────────────────────────────────────────────
// VCP/A §2.2 vocabularies and §2.3 forward compatibility
// ───────────────────────────────────────────────────────────────────────────

import { readFileSync } from 'node:fs';
import { validateContextWire, PERSONAL_STATE_CATEGORIES } from '../src/extensions/context.js';

const schemaDefinitions = JSON.parse(
  readFileSync(new URL('../../schemas/vcp-adaptation-context.schema.json', import.meta.url), 'utf8'),
).definitions as Record<string, { enum?: string[] }>;

describe('vocabularies match the synchronized schema', () => {
  for (const dim of SITUATIONAL_ORDER) {
    if (SITUATIONAL_SPECS[dim].freeForm) continue;
    it(`${dim} equals the schema enum`, () => {
      expect(Object.keys(SITUATIONAL_SPECS[dim].values)).toEqual(
        schemaDefinitions[`${dim}_values`].enum,
      );
    });
  }
  for (const dim of PERSONAL_STATE_ORDER) {
    it(`${dim} categories equal the schema enum`, () => {
      expect([...PERSONAL_STATE_CATEGORIES[dim]]).toEqual(schemaDefinitions[`${dim}_values`].enum);
    });
  }

  it('resolves renamed value names and drops removed ones', () => {
    expect(buildContext({ time: 'midday' }).situational.time).toEqual(['☀️']);
    expect(buildContext({ space: 'transit' }).situational.space).toEqual(['🚗']);
    expect(buildContext({ environment: 'noisy' }).situational.environment).toEqual(['📢']);
    expect(buildContext({ environment: 'comfortable' }).situational.environment).toBeUndefined();
    expect(
      encodeContext(
        buildContext({
          company: 'strangers',
          occasion: 'mourning',
          agency: 'subordinate',
          constraints: 'time',
        }),
      ),
    ).toBe('👥🧑\u200d🤝\u200d🧑|🎭⚰️|🔷👇|🔶⏰');
  });
});

describe('forward-compatible decoding (VCP/A 2.3)', () => {
  it('keeps unknown values raw and re-encodes them', () => {
    const ctx = decodeContext('🎭😢|🔷📋|🔶⏱️');
    expect(ctx.situational.occasion).toEqual(['😢']);
    expect(encodeContext(ctx)).toBe('🎭😢|🔷📋|🔶⏱️');
  });

  it('passes unknown dimension groups through', () => {
    const wire = '⏰🌅|🦄sparkle|📍🏡‖🧠focused:4|🪐orbit:2';
    const ctx = decodeContext(wire);
    expect(ctx.unknown).toEqual({ situational: ['🦄sparkle'], personal: ['🪐orbit:2'] });
    expect(encodeContext(ctx)).toBe('⏰🌅|📍🏡|🦄sparkle‖🧠focused:4|🪐orbit:2');
    expect(contextFromJSON(contextToJSON(ctx))).toEqual(ctx);
    expect(conformanceLevel(decodeContext('🦄sparkle'))).toBe('VCP-Minimal');
  });

  it.each(['⏰🌅||📍🏡', '⏰🌅|', '⏰', '⏰🌅‖', '‖🧠focused:4|', '‖🧠', '‖🧠focused:9', 'abc', '⏰🌅‖focused'])(
    'rejects malformed %s',
    (wire) => {
      expect(() => decodeContext(wire)).toThrow(SyntaxError);
    },
  );

  it('reports unknowns in strict validation', () => {
    expect(validateContextWire('⏰🌅|📍🏡|🎭⚰️‖🧠focused:4')).toEqual([]);
    expect(
      validateContextWire('🎭😢|🦄sparkle|🪢friend:gaming‖🧠scattered|🪐orbit'),
    ).toEqual([
      "unknown situational dimension group: '🦄sparkle'",
      "unknown occasion value: '😢'",
      "unknown relationship value: 'friend:gaming'",
      "unknown personal dimension group: '🪐orbit'",
      "unknown cognitive_state category: 'scattered'",
    ]);
    expect(validateContextWire('⏰🌅||📍🏡')[0]).toMatch(/^malformed:/);
  });
});
