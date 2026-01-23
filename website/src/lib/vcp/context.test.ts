/**
 * VCP Context Store Tests
 */
import { describe, it, expect, vi } from 'vitest';
import { createContext, mergeContext } from './context';
import type { VCPContext, PublicProfile } from './types';

describe('createContext', () => {
	it('should create a context with required fields', () => {
		const profile: Partial<PublicProfile> = {
			display_name: 'Test User'
		};
		const context = createContext(profile);

		expect(context).toBeDefined();
		expect(context.vcp_version).toBeDefined();
		expect(context.profile_id).toBeDefined();
		expect(context.public_profile?.display_name).toBe('Test User');
	});

	it('should use provided profile_id', () => {
		const profile: Partial<PublicProfile> = {
			display_name: 'Test User'
		};
		const context = createContext(profile, 'custom-id');

		expect(context.profile_id).toBe('custom-id');
	});

	it('should include default constitution', () => {
		const profile: Partial<PublicProfile> = {};
		const context = createContext(profile);

		expect(context.constitution).toBeDefined();
		expect(context.constitution.persona).toBeDefined();
	});
});

describe('mergeContext', () => {
	const baseContext: VCPContext = {
		vcp_version: '1.0.0',
		profile_id: 'test-user',
		constitution: {
			id: 'test',
			version: '1.0.0',
			persona: 'godparent',
			adherence: 3,
			scopes: []
		},
		public_profile: {
			display_name: 'Original Name',
			goal: 'original_goal'
		}
	};

	it('should merge updates into existing context', () => {
		const updates: Partial<VCPContext> = {
			public_profile: {
				display_name: 'Updated Name'
			}
		};

		const merged = mergeContext(baseContext, updates);

		expect(merged.public_profile?.display_name).toBe('Updated Name');
	});

	it('should preserve fields not in updates', () => {
		const updates: Partial<VCPContext> = {
			public_profile: {
				display_name: 'Updated Name'
			}
		};

		const merged = mergeContext(baseContext, updates);

		expect(merged.profile_id).toBe('test-user');
		expect(merged.constitution.persona).toBe('godparent');
	});

	it('should handle empty updates', () => {
		const merged = mergeContext(baseContext, {});

		expect(merged.public_profile?.display_name).toBe('Original Name');
	});
});
