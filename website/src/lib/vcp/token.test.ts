/**
 * VCP Token Encoding Tests
 */
import { describe, it, expect } from 'vitest';
import { encodeContextToCSM1, parseCSM1Token, getEmojiLegend, getTransmissionSummary } from './token';
import type { VCPContext } from './types';

const mockContext: VCPContext = {
	vcp_version: '1.0.0',
	profile_id: 'test-user',
	constitution: {
		id: 'test.constitution',
		version: '1.0.0',
		persona: 'godparent',
		adherence: 3,
		scopes: ['privacy', 'health']
	},
	public_profile: {
		display_name: 'Test User',
		goal: 'learn_guitar',
		experience: 'beginner',
		learning_style: 'hands_on',
		pace: 'steady',
		motivation: 'stress_relief'
	},
	portable_preferences: {
		noise_mode: 'quiet_preferred',
		session_length: '30_minutes',
		budget_range: 'low',
		feedback_style: 'encouraging'
	},
	constraints: {
		time_limited: true,
		budget_limited: true,
		noise_restricted: false,
		energy_variable: false,
		schedule_irregular: false
	}
};

describe('encodeContextToCSM1', () => {
	it('should encode context to CSM-1 token format', () => {
		const token = encodeContextToCSM1(mockContext);
		expect(token).toBeDefined();
		expect(typeof token).toBe('string');
		expect(token.length).toBeGreaterThan(0);
	});

	it('should include persona identifier', () => {
		const token = encodeContextToCSM1(mockContext);
		// Token should include persona reference
		expect(token.toLowerCase()).toContain('godparent');
	});

	it('should encode constraint flags', () => {
		const token = encodeContextToCSM1(mockContext);
		// Constraints should appear in token
		expect(token).toContain('time_limited');
		expect(token).toContain('budget_limited');
	});

	it('should handle missing optional fields', () => {
		const minimalContext: VCPContext = {
			vcp_version: '1.0.0',
			profile_id: 'minimal',
			constitution: {
				id: 'test',
				version: '1.0.0',
				persona: 'sentinel',
				adherence: 1,
				scopes: []
			},
			public_profile: {
				display_name: 'Minimal'
			}
		};
		const token = encodeContextToCSM1(minimalContext);
		expect(token).toBeDefined();
	});
});

describe('parseCSM1Token', () => {
	it('should parse a valid CSM-1 token', () => {
		const token = encodeContextToCSM1(mockContext);
		const parsed = parseCSM1Token(token);
		expect(parsed).toBeDefined();
		expect(typeof parsed).toBe('object');
	});

	it('should return empty object for invalid token', () => {
		const parsed = parseCSM1Token('');
		expect(parsed).toBeDefined();
		expect(Object.keys(parsed).length).toBe(0);
	});
});

describe('getEmojiLegend', () => {
	it('should return emoji legend array', () => {
		const legend = getEmojiLegend();
		expect(Array.isArray(legend)).toBe(true);
		expect(legend.length).toBeGreaterThan(0);
	});

	it('should have emoji and meaning for each item', () => {
		const legend = getEmojiLegend();
		legend.forEach((item) => {
			expect(item.emoji).toBeDefined();
			expect(item.meaning).toBeDefined();
		});
	});
});

describe('getTransmissionSummary', () => {
	it('should categorize fields into transmitted, influencing, withheld', () => {
		const summary = getTransmissionSummary(mockContext);
		expect(summary.transmitted).toBeDefined();
		expect(summary.influencing).toBeDefined();
		expect(summary.withheld).toBeDefined();
	});

	it('should include public fields in transmitted', () => {
		const summary = getTransmissionSummary(mockContext);
		expect(summary.transmitted).toContain('display_name');
	});

	it('should include constraint flags in influencing', () => {
		const summary = getTransmissionSummary(mockContext);
		expect(summary.influencing.length).toBeGreaterThan(0);
	});
});
