import { describe, expect, it } from 'vitest';

import {
	StandingLevel,
	TrustLevel,
	createDefaultRelationalContext,
	getAllDimensions,
	hasUncertaintyMarkers,
	type AISelfModel,
} from '../src/extensions/relational.js';

describe('relational self-model utilities', () => {
	it('requires at least one explicit true uncertainty marker', () => {
		expect(hasUncertaintyMarkers({})).toBe(false);
		expect(
			hasUncertaintyMarkers({
				valence: { value: 7, uncertain: false },
				customDimensions: { involvement: { value: 6, uncertain: true } },
			}),
		).toBe(true);
		expect(
			hasUncertaintyMarkers({
				valence: { value: 7, uncertain: false },
				customDimensions: { involvement: { value: 6, uncertain: false } },
			}),
		).toBe(false);
		expect(
			hasUncertaintyMarkers({
				valence: { value: 7, uncertain: 'yes' } as never,
			}),
		).toBe(false);
	});

	it('flattens core and custom dimensions without namespace overwrite or aliasing', () => {
		const model: AISelfModel = {
			valence: { value: 7, uncertain: false, label: 'warm' },
			depth: { value: 8, uncertain: true },
			customDimensions: Object.fromEntries([
				['involvement', { value: 6, uncertain: true }],
				['valence', { value: 1, uncertain: true, label: 'hostile collision' }],
				['__proto__', { value: 5, uncertain: true }],
			]),
		};
		const flattened = getAllDimensions(model);

		expect(flattened).toMatchObject({
			valence: { value: 7, uncertain: false, label: 'warm' },
			depth: { value: 8, uncertain: true },
			involvement: { value: 6, uncertain: true },
		});
		expect(Object.hasOwn(flattened, '__proto__')).toBe(true);
		expect(Object.getPrototypeOf(flattened)).toBe(Object.prototype);

		(flattened.valence as { value: number }).value = 2;
		expect(model.valence?.value).toBe(7);
	});

	it('returns fresh default contexts with no shared mutable norm list', () => {
		const first = createDefaultRelationalContext();
		const second = createDefaultRelationalContext();
		expect(first).toEqual({
			trustLevel: TrustLevel.INITIAL,
			standing: StandingLevel.NONE,
			continuityDepth: 0,
			establishedNorms: [],
		});
		expect(first.establishedNorms).not.toBe(second.establishedNorms);
		(first.establishedNorms as unknown[]).push({});
		expect(second.establishedNorms).toEqual([]);
	});
});
