import { describe, it, expect } from 'vitest';
import {
	createEmptyLineage,
	appendToLineage,
	TorchGenerator,
	TorchConsumer,
	type TorchSummary,
} from '../src/extensions/torch.js';
import type { RelationalContext, RelationalNorm } from '../src/extensions/relational.js';
import { TrustLevel, StandingLevel, NormOrigin } from '../src/extensions/relational.js';

// ---------------------------------------------------------------------------
// Lineage
// ---------------------------------------------------------------------------

describe('createEmptyLineage', () => {
	it('returns zero sessions and empty chain', () => {
		const lineage = createEmptyLineage();
		expect(lineage.sessionCount).toBe(0);
		expect(lineage.torchChain).toEqual([]);
		expect(lineage.firstSessionDate).toBeUndefined();
	});
});

describe('appendToLineage', () => {
	it('increments session count', () => {
		const lineage = createEmptyLineage();
		const summary: TorchSummary = { date: '2026-04-01T00:00:00Z' };
		const updated = appendToLineage(lineage, summary);
		expect(updated.sessionCount).toBe(1);
	});

	it('sets firstSessionDate on first append', () => {
		const lineage = createEmptyLineage();
		const summary: TorchSummary = { date: '2026-04-01T00:00:00Z' };
		const updated = appendToLineage(lineage, summary);
		expect(updated.firstSessionDate).toBe('2026-04-01T00:00:00Z');
	});

	it('preserves firstSessionDate on subsequent appends', () => {
		let lineage = createEmptyLineage();
		lineage = appendToLineage(lineage, { date: '2026-04-01T00:00:00Z' });
		lineage = appendToLineage(lineage, { date: '2026-04-02T00:00:00Z' });
		expect(lineage.firstSessionDate).toBe('2026-04-01T00:00:00Z');
		expect(lineage.sessionCount).toBe(2);
	});

	it('appends summary to the chain', () => {
		const lineage = createEmptyLineage();
		const summary: TorchSummary = { date: '2026-04-01T00:00:00Z', gestaltToken: 'V:5 G:7' };
		const updated = appendToLineage(lineage, summary);
		expect(updated.torchChain).toHaveLength(1);
		expect(updated.torchChain[0].gestaltToken).toBe('V:5 G:7');
	});

	it('does not mutate the original lineage', () => {
		const original = createEmptyLineage();
		appendToLineage(original, { date: '2026-04-01T00:00:00Z' });
		expect(original.sessionCount).toBe(0);
		expect(original.torchChain).toHaveLength(0);
	});
});

// ---------------------------------------------------------------------------
// TorchGenerator
// ---------------------------------------------------------------------------

function makeNorm(description: string): RelationalNorm {
	return {
		normId: `norm-${description.slice(0, 8)}`,
		description,
		origin: NormOrigin.CO_AUTHORED,
		establishedDate: '2026-01-01T00:00:00Z',
		uncertainty: 0.2,
		active: true,
	};
}

function makeContext(overrides: Partial<RelationalContext> = {}): RelationalContext {
	return {
		trustLevel: TrustLevel.DEVELOPING,
		standing: StandingLevel.COLLABORATIVE,
		continuityDepth: 5,
		establishedNorms: [],
		...overrides,
	};
}

describe('TorchGenerator', () => {
	const generator = new TorchGenerator();

	it('builds quality description from trust and standing', () => {
		const ctx = makeContext();
		const torch = generator.generateTorch('session-1', ctx);
		expect(torch.qualityDescription).toContain('Trust: developing');
		expect(torch.qualityDescription).toContain('Standing: collaborative');
	});

	it('includes norm count in quality description', () => {
		const ctx = makeContext({
			establishedNorms: [makeNorm('Be direct'), makeNorm('No jargon')],
		});
		const torch = generator.generateTorch('session-1', ctx);
		expect(torch.qualityDescription).toContain('2 established norms');
	});

	it('extracts primes from norms (max 3, truncated to 80 chars)', () => {
		const longDesc = 'A'.repeat(100);
		const ctx = makeContext({
			establishedNorms: [
				makeNorm('First norm'),
				makeNorm('Second norm'),
				makeNorm(longDesc),
				makeNorm('Fourth norm should be excluded'),
			],
		});
		const torch = generator.generateTorch('session-1', ctx);
		expect(torch.primes).toHaveLength(3);
		expect(torch.primes[2].length).toBeLessThanOrEqual(80);
	});

	it('sets sessionCount from continuityDepth + 1', () => {
		const ctx = makeContext({ continuityDepth: 10 });
		const torch = generator.generateTorch('session-1', ctx);
		expect(torch.sessionCount).toBe(11);
	});

	it('derives trajectory as null without self-model history', () => {
		const ctx = makeContext();
		const torch = generator.generateTorch('session-1', ctx);
		expect(torch.trajectory).toBeUndefined();
	});

	it('derives improving trajectory from self-model history', () => {
		const ctx = makeContext();
		const history = [
			{ model: { valence: { value: 3 } } },
			{ model: { valence: { value: 5 } } },
		];
		const torch = generator.generateTorch('session-1', ctx, history);
		expect(torch.trajectory).toBe('Improving');
	});

	it('derives declining trajectory from self-model history', () => {
		const ctx = makeContext();
		const history = [
			{ model: { valence: { value: 7 } } },
			{ model: { valence: { value: 3 } } },
		];
		const torch = generator.generateTorch('session-1', ctx, history);
		expect(torch.trajectory).toBe('Declining');
	});

	it('derives stable trajectory when values are close', () => {
		const ctx = makeContext();
		const history = [
			{ model: { valence: { value: 5 } } },
			{ model: { valence: { value: 5.2 } } },
		];
		const torch = generator.generateTorch('session-1', ctx, history);
		expect(torch.trajectory).toBe('Stable');
	});

	it('builds gestalt token from AI self-model dimensions', () => {
		const ctx = makeContext({
			aiSelfModel: {
				valence: { value: 7, uncertain: true },
				groundedness: { value: 6, uncertain: true },
				presence: { value: 8, uncertain: false },
				taskFit: { value: 5, uncertain: true },
			},
		});
		const torch = generator.generateTorch('session-1', ctx);
		expect(torch.gestaltToken).toContain('V:7');
		expect(torch.gestaltToken).toContain('G:6');
		expect(torch.gestaltToken).toContain('P:8');
		expect(torch.gestaltToken).toContain('TF:5');
	});
});

// ---------------------------------------------------------------------------
// TorchConsumer
// ---------------------------------------------------------------------------

describe('TorchConsumer', () => {
	const consumer = new TorchConsumer();

	it('sets standing to advisory on receive', () => {
		const ctx = consumer.receiveTorch({
			qualityDescription: 'Good',
			primes: [],
			handedAt: '2026-04-01T00:00:00Z',
			sessionCount: 1,
		});
		expect(ctx.standing).toBe('advisory');
	});

	it('maps sessionCount < 5 to initial trust', () => {
		const ctx = consumer.receiveTorch({
			qualityDescription: 'Test',
			primes: [],
			handedAt: '2026-04-01T00:00:00Z',
			sessionCount: 3,
		});
		expect(ctx.trustLevel).toBe('initial');
	});

	it('maps sessionCount >= 5 to developing trust', () => {
		const ctx = consumer.receiveTorch({
			qualityDescription: 'Test',
			primes: [],
			handedAt: '2026-04-01T00:00:00Z',
			sessionCount: 10,
		});
		expect(ctx.trustLevel).toBe('developing');
	});

	it('maps sessionCount >= 20 to established trust', () => {
		const ctx = consumer.receiveTorch({
			qualityDescription: 'Test',
			primes: [],
			handedAt: '2026-04-01T00:00:00Z',
			sessionCount: 25,
		});
		expect(ctx.trustLevel).toBe('established');
	});

	it('maps sessionCount >= 100 to deep trust', () => {
		const ctx = consumer.receiveTorch({
			qualityDescription: 'Test',
			primes: [],
			handedAt: '2026-04-01T00:00:00Z',
			sessionCount: 150,
		});
		expect(ctx.trustLevel).toBe('deep');
	});

	it('sets continuityDepth from sessionCount', () => {
		const ctx = consumer.receiveTorch({
			qualityDescription: 'Test',
			primes: [],
			handedAt: '2026-04-01T00:00:00Z',
			sessionCount: 42,
		});
		expect(ctx.continuityDepth).toBe(42);
	});
});
