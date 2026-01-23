/**
 * VCP Privacy Filtering Tests
 */
import { describe, it, expect } from 'vitest';
import {
	PUBLIC_FIELDS,
	PRIVATE_FIELDS,
	CONSENT_REQUIRED_FIELDS,
	extractConstraintFlags,
	isPrivateField,
	getFieldValue,
	formatFieldName,
	getFieldPrivacyLevel,
	generatePrivacySummary
} from './privacy';
import type { VCPContext } from './types';

const mockContext: VCPContext = {
	vcp_version: '1.0.0',
	profile_id: 'test-user',
	constitution: {
		id: 'test.constitution',
		version: '1.0.0',
		persona: 'godparent',
		adherence: 3,
		scopes: ['privacy']
	},
	public_profile: {
		display_name: 'Test User',
		goal: 'learn_guitar',
		experience: 'beginner'
	},
	constraints: {
		time_limited: true,
		budget_limited: false,
		noise_restricted: true
	},
	private_context: {
		_note: 'Private context',
		health_conditions: 'chronic_fatigue',
		financial_constraint: true
	}
};

describe('Field Classifications', () => {
	it('should have non-overlapping field lists', () => {
		const publicSet = new Set(PUBLIC_FIELDS);
		const privateSet = new Set(PRIVATE_FIELDS);
		const consentSet = new Set(CONSENT_REQUIRED_FIELDS);

		// No overlap between public and private
		PUBLIC_FIELDS.forEach((field) => {
			expect(privateSet.has(field)).toBe(false);
		});

		// No overlap between private and consent-required
		PRIVATE_FIELDS.forEach((field) => {
			expect(consentSet.has(field)).toBe(false);
		});
	});

	it('should include expected public fields', () => {
		expect(PUBLIC_FIELDS).toContain('display_name');
		expect(PUBLIC_FIELDS).toContain('goal');
		expect(PUBLIC_FIELDS).toContain('experience');
	});

	it('should include expected private fields', () => {
		expect(PRIVATE_FIELDS).toContain('health_conditions');
		expect(PRIVATE_FIELDS).toContain('financial_constraint');
		expect(PRIVATE_FIELDS).toContain('family_status');
	});
});

describe('isPrivateField', () => {
	it('should return true for fields in PRIVATE_FIELDS', () => {
		expect(isPrivateField(mockContext, 'health_conditions')).toBe(true);
		expect(isPrivateField(mockContext, 'financial_constraint')).toBe(true);
	});

	it('should return true for fields in private_context', () => {
		expect(isPrivateField(mockContext, 'health_conditions')).toBe(true);
	});

	it('should return false for public fields', () => {
		expect(isPrivateField(mockContext, 'display_name')).toBe(false);
		expect(isPrivateField(mockContext, 'goal')).toBe(false);
	});
});

describe('getFieldValue', () => {
	it('should retrieve values from public_profile', () => {
		expect(getFieldValue(mockContext, 'display_name')).toBe('Test User');
		expect(getFieldValue(mockContext, 'goal')).toBe('learn_guitar');
	});

	it('should retrieve values from constraints', () => {
		expect(getFieldValue(mockContext, 'time_limited')).toBe(true);
		expect(getFieldValue(mockContext, 'budget_limited')).toBe(false);
	});

	it('should return undefined for non-existent fields', () => {
		expect(getFieldValue(mockContext, 'nonexistent_field')).toBeUndefined();
	});
});

describe('extractConstraintFlags', () => {
	it('should extract boolean constraint flags', () => {
		const flags = extractConstraintFlags(mockContext);
		expect(flags.time_limited).toBe(true);
		expect(flags.noise_restricted).toBe(true);
	});

	it('should infer constraints from private context', () => {
		const flags = extractConstraintFlags(mockContext);
		// health_conditions should trigger health_considerations
		expect(flags.health_considerations).toBe(true);
		// financial_constraint should trigger budget_limited
		expect(flags.budget_limited).toBe(true);
	});

	it('should never expose private field values', () => {
		const flags = extractConstraintFlags(mockContext);
		// All values should be booleans
		Object.values(flags).forEach((value) => {
			expect(typeof value).toBe('boolean');
		});
	});
});

describe('formatFieldName', () => {
	it('should convert snake_case to Title Case', () => {
		expect(formatFieldName('display_name')).toBe('Display Name');
		expect(formatFieldName('learning_style')).toBe('Learning Style');
	});

	it('should handle single words', () => {
		expect(formatFieldName('goal')).toBe('Goal');
	});
});

describe('getFieldPrivacyLevel', () => {
	it('should return "public" for public fields', () => {
		expect(getFieldPrivacyLevel('display_name')).toBe('public');
		expect(getFieldPrivacyLevel('goal')).toBe('public');
	});

	it('should return "private" for private fields', () => {
		expect(getFieldPrivacyLevel('health_conditions')).toBe('private');
		expect(getFieldPrivacyLevel('financial_constraint')).toBe('private');
	});

	it('should return "consent-required" for other fields', () => {
		expect(getFieldPrivacyLevel('noise_mode')).toBe('consent-required');
		expect(getFieldPrivacyLevel('budget_range')).toBe('consent-required');
	});
});

describe('generatePrivacySummary', () => {
	it('should generate human-readable summary', () => {
		const summary = generatePrivacySummary(['field1', 'field2'], ['field3'], 2);
		expect(summary).toContain('2 fields shared');
		expect(summary).toContain('1 fields kept private');
		expect(summary).toContain('2 private constraints influenced');
	});

	it('should handle empty arrays', () => {
		const summary = generatePrivacySummary([], [], 0);
		expect(summary).toBe('');
	});
});
