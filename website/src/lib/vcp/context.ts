/**
 * VCP Context Store
 * Manages user context with localStorage persistence and privacy filtering
 */

import { writable, derived, get, type Readable, type Writable } from 'svelte/store';
import type {
	VCPContext,
	PublicProfile,
	ConstraintFlags,
	FilteredContext,
	PlatformManifest,
	ConsentRecord,
	PortablePreferences
} from './types';
import { logAuditEntry } from './audit';

// ============================================
// Storage Keys
// ============================================

const CONTEXT_STORAGE_KEY = 'vcp_context';
const CONSENT_STORAGE_KEY = 'vcp_consents';

// ============================================
// Helper Functions
// ============================================

function isBrowser(): boolean {
	return typeof window !== 'undefined' && typeof localStorage !== 'undefined';
}

function loadFromStorage<T>(key: string): T | null {
	if (!isBrowser()) return null;
	try {
		const stored = localStorage.getItem(key);
		return stored ? JSON.parse(stored) : null;
	} catch {
		console.warn(`Failed to load ${key} from localStorage`);
		return null;
	}
}

function saveToStorage<T>(key: string, value: T | null): void {
	if (!isBrowser()) return;
	try {
		if (value) {
			localStorage.setItem(key, JSON.stringify(value));
		} else {
			localStorage.removeItem(key);
		}
	} catch {
		console.warn(`Failed to save ${key} to localStorage`);
	}
}

// ============================================
// Context Store
// ============================================

function createContextStore(): Writable<VCPContext | null> & {
	clear: () => void;
	updateField: <K extends keyof VCPContext>(key: K, value: VCPContext[K]) => void;
} {
	const initial = loadFromStorage<VCPContext>(CONTEXT_STORAGE_KEY);
	const { subscribe, set, update } = writable<VCPContext | null>(initial);

	return {
		subscribe,
		set: (ctx: VCPContext | null) => {
			set(ctx);
			saveToStorage(CONTEXT_STORAGE_KEY, ctx);
		},
		update: (fn) => {
			update((current) => {
				const newValue = fn(current);
				saveToStorage(CONTEXT_STORAGE_KEY, newValue);
				return newValue;
			});
		},
		clear: () => {
			set(null);
			saveToStorage(CONTEXT_STORAGE_KEY, null);
		},
		updateField: <K extends keyof VCPContext>(key: K, value: VCPContext[K]) => {
			update((current) => {
				if (!current) return current;
				const updated = { ...current, [key]: value, updated: new Date().toISOString() };
				saveToStorage(CONTEXT_STORAGE_KEY, updated);
				return updated;
			});
		}
	};
}

export const vcpContext = createContextStore();

// ============================================
// Derived Stores
// ============================================

/**
 * Public profile only - safe to share with any platform
 */
export const publicContext: Readable<Partial<PublicProfile> | null> = derived(vcpContext, ($ctx) => {
	if (!$ctx) return null;
	return {
		display_name: $ctx.public_profile?.display_name,
		goal: $ctx.public_profile?.goal,
		experience: $ctx.public_profile?.experience,
		learning_style: $ctx.public_profile?.learning_style,
		pace: $ctx.public_profile?.pace,
		motivation: $ctx.public_profile?.motivation,
		role: $ctx.public_profile?.role,
		team: $ctx.public_profile?.team,
		career_goal: $ctx.public_profile?.career_goal
	};
});

/**
 * Constraint flags as booleans - no private details exposed
 */
export const influenceFlags: Readable<ConstraintFlags | null> = derived(vcpContext, ($ctx) => {
	if (!$ctx) return null;

	// Convert private context to boolean flags
	const private_ctx = $ctx.private_context || {};
	const constraints = $ctx.constraints || {};

	return {
		time_limited: constraints.time_limited ?? !!private_ctx.schedule_irregular,
		budget_limited: constraints.budget_limited ?? !!private_ctx.financial_constraint,
		noise_restricted: constraints.noise_restricted ?? !!private_ctx.noise_sensitive,
		energy_variable: constraints.energy_variable ?? !!private_ctx.energy_variable,
		schedule_irregular: constraints.schedule_irregular ?? !!private_ctx.schedule_irregular,
		mobility_limited: constraints.mobility_limited ?? !!private_ctx.mobility_limited,
		health_considerations: constraints.health_considerations ?? !!private_ctx.health_conditions
	};
});

// ============================================
// Consent Management
// ============================================

function createConsentStore(): Writable<Record<string, ConsentRecord>> & {
	grantConsent: (
		platformId: string,
		requiredFields: string[],
		optionalFields: string[]
	) => ConsentRecord;
	revokeConsent: (platformId: string) => void;
	hasConsent: (platformId: string) => boolean;
	getConsent: (platformId: string) => ConsentRecord | null;
} {
	const initial = loadFromStorage<Record<string, ConsentRecord>>(CONSENT_STORAGE_KEY) || {};
	const { subscribe, set, update } = writable<Record<string, ConsentRecord>>(initial);

	return {
		subscribe,
		set,
		update,
		grantConsent: (
			platformId: string,
			requiredFields: string[],
			optionalFields: string[]
		): ConsentRecord => {
			const consent: ConsentRecord = {
				platform_id: platformId,
				granted_at: new Date().toISOString(),
				required_fields: requiredFields,
				optional_fields: optionalFields
			};

			update((consents) => {
				const updated = { ...consents, [platformId]: consent };
				saveToStorage(CONSENT_STORAGE_KEY, updated);
				return updated;
			});

			logAuditEntry({
				id: `consent-${Date.now()}`,
				timestamp: new Date().toISOString(),
				event_type: 'consent_granted',
				platform_id: platformId,
				data_shared: [...requiredFields, ...optionalFields],
				data_withheld: [],
				private_fields_influenced: 0,
				private_fields_exposed: 0
			});

			return consent;
		},
		revokeConsent: (platformId: string) => {
			update((consents) => {
				const { [platformId]: _, ...rest } = consents;
				saveToStorage(CONSENT_STORAGE_KEY, rest);
				return rest;
			});

			logAuditEntry({
				id: `consent-revoke-${Date.now()}`,
				timestamp: new Date().toISOString(),
				event_type: 'consent_revoked',
				platform_id: platformId,
				data_shared: [],
				data_withheld: [],
				private_fields_influenced: 0,
				private_fields_exposed: 0
			});
		},
		hasConsent: (platformId: string): boolean => {
			const consents = get({ subscribe });
			return !!consents[platformId];
		},
		getConsent: (platformId: string): ConsentRecord | null => {
			const consents = get({ subscribe });
			return consents[platformId] || null;
		}
	};
}

export const vcpConsents = createConsentStore();

// ============================================
// Privacy Filtering
// ============================================

/**
 * Get a field value from the context by field name
 */
function getFieldValue(ctx: VCPContext, field: string): unknown {
	// Check public profile
	if (field in (ctx.public_profile || {})) {
		return (ctx.public_profile as Record<string, unknown>)[field];
	}
	// Check portable preferences
	if (field in (ctx.portable_preferences || {})) {
		return (ctx.portable_preferences as Record<string, unknown>)[field];
	}
	// Check current skills
	if (field in (ctx.current_skills || {})) {
		return (ctx.current_skills as Record<string, unknown>)[field];
	}
	// Check constraints (as booleans)
	if (field in (ctx.constraints || {})) {
		return (ctx.constraints as Record<string, unknown>)[field];
	}
	// Check availability
	if (field in (ctx.availability || {})) {
		return (ctx.availability as Record<string, unknown>)[field];
	}
	// Check shared_with_manager (professional)
	if (field in (ctx.shared_with_manager || {})) {
		return (ctx.shared_with_manager as Record<string, unknown>)[field];
	}
	return undefined;
}

/**
 * Filter context for a specific platform based on manifest and consent
 */
export function filterContextForPlatform(
	fullContext: VCPContext,
	manifest: PlatformManifest,
	consent: ConsentRecord
): FilteredContext {
	const result: FilteredContext = {
		public: {},
		preferences: {},
		constraints: {}
	};

	const shared: string[] = [];
	const withheld: string[] = [];

	// Always include basic public profile
	result.public = {
		display_name: fullContext.public_profile?.display_name,
		goal: fullContext.public_profile?.goal,
		experience: fullContext.public_profile?.experience
	};
	shared.push('display_name', 'goal', 'experience');

	// Process required fields
	for (const field of manifest.context_requirements.required) {
		if (consent.required_fields.includes(field)) {
			const value = getFieldValue(fullContext, field);
			if (value !== undefined) {
				(result.preferences as Record<string, unknown>)[field] = value;
				shared.push(field);
			}
		} else {
			withheld.push(field);
		}
	}

	// Process optional fields
	for (const field of manifest.context_requirements.optional) {
		if (consent.optional_fields.includes(field)) {
			const value = getFieldValue(fullContext, field);
			if (value !== undefined) {
				(result.preferences as Record<string, unknown>)[field] = value;
				shared.push(field);
			}
		} else {
			withheld.push(field);
		}
	}

	// Add constraint flags (always boolean, never details)
	const privateCtx = fullContext.private_context || {};
	const constraints = fullContext.constraints || {};

	result.constraints = {
		time_limited: constraints.time_limited ?? !!privateCtx.schedule_irregular,
		budget_limited: constraints.budget_limited ?? !!privateCtx.financial_constraint,
		noise_restricted: constraints.noise_restricted ?? !!privateCtx.noise_sensitive,
		energy_variable: constraints.energy_variable ?? !!privateCtx.energy_variable
	};

	const privateFieldsInfluenced = Object.values(result.constraints).filter(Boolean).length;

	// Log to audit
	logAuditEntry({
		id: `share-${Date.now()}`,
		timestamp: new Date().toISOString(),
		event_type: 'context_shared',
		platform_id: manifest.platform_id,
		data_shared: shared,
		data_withheld: withheld,
		private_fields_influenced: privateFieldsInfluenced,
		private_fields_exposed: 0 // Always 0 by design
	});

	return result;
}

/**
 * Get list of fields that would be shared vs withheld for a platform
 */
export function getSharePreview(
	fullContext: VCPContext,
	manifest: PlatformManifest
): { wouldShare: string[]; wouldWithhold: string[] } {
	const wouldShare: string[] = ['display_name', 'goal', 'experience']; // Always public
	const wouldWithhold: string[] = [];

	// Check sharing settings
	const sharingSettings = fullContext.sharing_settings?.platforms || {
		share: [],
		hide: []
	};
	const shareList = sharingSettings.share || [];
	const hideList = sharingSettings.hide || [];

	for (const field of manifest.context_requirements.required) {
		if (hideList.includes(field)) {
			wouldWithhold.push(field);
		} else {
			wouldShare.push(field);
		}
	}

	for (const field of manifest.context_requirements.optional) {
		if (shareList.includes(field)) {
			wouldShare.push(field);
		} else {
			wouldWithhold.push(field);
		}
	}

	// Private context is always withheld
	if (fullContext.private_context) {
		const privateKeys = Object.keys(fullContext.private_context).filter((k) => k !== '_note');
		wouldWithhold.push(...privateKeys);
	}

	return { wouldShare, wouldWithhold };
}

// ============================================
// Context Creation Helpers
// ============================================

/**
 * Create a new VCP context with defaults
 */
export function createContext(profile: Partial<PublicProfile>, profileId?: string): VCPContext {
	const now = new Date().toISOString();
	return {
		vcp_version: '1.0.0',
		profile_id: profileId || `user-${Date.now()}`,
		created: now,
		updated: now,
		constitution: {
			id: 'personal.growth.creative',
			version: '1.0.0',
			persona: 'muse',
			adherence: 3,
			scopes: ['creativity', 'health', 'privacy']
		},
		public_profile: profile,
		portable_preferences: {},
		constraints: {},
		sharing_settings: {}
	};
}

/**
 * Update context with new values, preserving existing
 */
export function mergeContext(existing: VCPContext, updates: Partial<VCPContext>): VCPContext {
	return {
		...existing,
		...updates,
		public_profile: {
			...existing.public_profile,
			...updates.public_profile
		},
		portable_preferences: {
			...existing.portable_preferences,
			...updates.portable_preferences
		},
		constraints: {
			...existing.constraints,
			...updates.constraints
		},
		updated: new Date().toISOString()
	};
}
