import { describe, it, expect } from 'vitest';
import {
	computeDecayedIntensity,
	computeLifecycleState,
	LifecycleState,
	DEFAULT_DECAY_CONFIGS,
	type DecayConfig,
} from '../src/extensions/personal.js';

const BASE_CONFIG: DecayConfig = {
	halfLifeSeconds: 900,
	baseline: 1,
	pinned: false,
	resetOnEngagement: false,
};

const PINNED_CONFIG: DecayConfig = {
	...BASE_CONFIG,
	pinned: true,
};

function minutesAgo(minutes: number, from?: Date): Date {
	const base = from ?? new Date();
	return new Date(base.getTime() - minutes * 60 * 1000);
}

// ---------------------------------------------------------------------------
// computeDecayedIntensity
// ---------------------------------------------------------------------------

describe('computeDecayedIntensity', () => {
	it('returns declared intensity when pinned', () => {
		const result = computeDecayedIntensity(
			5,
			minutesAgo(999).toISOString(),
			PINNED_CONFIG,
		);
		expect(result).toBe(5);
	});

	it('returns declared intensity when elapsed <= 0 (future date)', () => {
		const future = new Date(Date.now() + 60_000);
		const result = computeDecayedIntensity(4, future.toISOString(), BASE_CONFIG);
		expect(result).toBe(4);
	});

	it('returns declared intensity for freshly declared signal', () => {
		const now = new Date();
		const result = computeDecayedIntensity(5, now.toISOString(), BASE_CONFIG, now);
		expect(result).toBe(5);
	});

	it('decays to roughly half at one half-life', () => {
		const now = new Date();
		const declared = minutesAgo(15, now); // 900 seconds = 1 half-life
		const result = computeDecayedIntensity(5, declared.toISOString(), BASE_CONFIG, now);
		// At one half-life: baseline + (5-1)*0.5 = 1 + 2 = 3, floor(3) = 3
		expect(result).toBe(3);
	});

	it('decays to baseline after many half-lives', () => {
		const now = new Date();
		const declared = minutesAgo(300, now); // 18000 seconds = 20 half-lives
		const result = computeDecayedIntensity(5, declared.toISOString(), BASE_CONFIG, now);
		expect(result).toBe(BASE_CONFIG.baseline);
	});

	it('never goes below baseline', () => {
		const now = new Date();
		const declared = minutesAgo(9999, now);
		const result = computeDecayedIntensity(2, declared.toISOString(), BASE_CONFIG, now);
		expect(result).toBeGreaterThanOrEqual(BASE_CONFIG.baseline);
	});

	it('accepts Date objects for declaredAt', () => {
		const now = new Date();
		const declared = minutesAgo(15, now);
		const result = computeDecayedIntensity(5, declared, BASE_CONFIG, now);
		expect(result).toBe(3);
	});

	it('works with different baseline values', () => {
		const config: DecayConfig = { ...BASE_CONFIG, baseline: 2 };
		const now = new Date();
		const declared = minutesAgo(15, now);
		// At one half-life: baseline + (5-2)*0.5 = 2 + 1.5 = 3.5, floor = 3
		const result = computeDecayedIntensity(5, declared.toISOString(), config, now);
		expect(result).toBe(3);
	});
});

// ---------------------------------------------------------------------------
// computeLifecycleState
// ---------------------------------------------------------------------------

describe('computeLifecycleState', () => {
	it('returns SET when declaredAt is in the future', () => {
		const future = new Date(Date.now() + 60_000);
		const result = computeLifecycleState(4, future.toISOString(), BASE_CONFIG);
		expect(result).toBe(LifecycleState.SET);
	});

	it('returns ACTIVE within the 60-second fresh window', () => {
		const now = new Date();
		const declared = new Date(now.getTime() - 30_000); // 30 seconds ago
		const result = computeLifecycleState(4, declared.toISOString(), BASE_CONFIG, now);
		expect(result).toBe(LifecycleState.ACTIVE);
	});

	it('returns ACTIVE for pinned signals regardless of age', () => {
		const old = minutesAgo(9999);
		const result = computeLifecycleState(4, old.toISOString(), PINNED_CONFIG);
		expect(result).toBe(LifecycleState.ACTIVE);
	});

	it('returns DECAYING after fresh window when intensity is still high', () => {
		const now = new Date();
		const declared = new Date(now.getTime() - 120_000); // 2 minutes ago
		const result = computeLifecycleState(5, declared.toISOString(), BASE_CONFIG, now);
		expect(result).toBe(LifecycleState.DECAYING);
	});

	it('returns STALE when intensity drops below 30% threshold', () => {
		const now = new Date();
		// For intensity=5, baseline=1, range=4, stale threshold = 1 + 4*0.3 = 2.2
		// Need effective intensity to be <= 2.2 but > 1
		// At ~2 half-lives: 1 + 4*0.25 = 2.0, floor = 2 > 1 and <= 2.2 => STALE
		const declared = new Date(now.getTime() - 1800_000); // 30 min = 2 half-lives
		const result = computeLifecycleState(5, declared.toISOString(), BASE_CONFIG, now);
		expect(result).toBe(LifecycleState.STALE);
	});

	it('returns EXPIRED when intensity reaches baseline', () => {
		const now = new Date();
		const declared = minutesAgo(300, now); // way past decay
		const result = computeLifecycleState(5, declared.toISOString(), BASE_CONFIG, now);
		expect(result).toBe(LifecycleState.EXPIRED);
	});
});

// ---------------------------------------------------------------------------
// DEFAULT_DECAY_CONFIGS
// ---------------------------------------------------------------------------

describe('DEFAULT_DECAY_CONFIGS', () => {
	it('has configs for all five personal dimensions', () => {
		expect(DEFAULT_DECAY_CONFIGS).toHaveProperty('perceived_urgency');
		expect(DEFAULT_DECAY_CONFIGS).toHaveProperty('body_signals');
		expect(DEFAULT_DECAY_CONFIGS).toHaveProperty('cognitive_state');
		expect(DEFAULT_DECAY_CONFIGS).toHaveProperty('emotional_tone');
		expect(DEFAULT_DECAY_CONFIGS).toHaveProperty('energy_level');
	});

	it('perceived_urgency decays fastest (15 min half-life)', () => {
		expect(DEFAULT_DECAY_CONFIGS.perceived_urgency.halfLifeSeconds).toBe(900);
	});

	it('body_signals decays slowest (4 hour half-life)', () => {
		expect(DEFAULT_DECAY_CONFIGS.body_signals.halfLifeSeconds).toBe(14400);
	});

	it('cognitive_state resets on engagement', () => {
		expect(DEFAULT_DECAY_CONFIGS.cognitive_state.resetOnEngagement).toBe(true);
	});
});
