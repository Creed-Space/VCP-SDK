/**
 * VCP Privacy Filtering
 * Core privacy logic for filtering context before sharing
 */

import type {
	VCPContext,
	PlatformManifest,
	ConsentRecord,
	FilteredContext,
	ConstraintFlags,
	StakeholderType
} from './types';
import { logAuditEntry } from './audit';

// ============================================
// Field Classification
// ============================================

/**
 * Fields that are always public (can be shared with anyone)
 */
export const PUBLIC_FIELDS = [
	'display_name',
	'goal',
	'experience',
	'learning_style',
	'pace',
	'motivation',
	'role',
	'team',
	'career_goal'
];

/**
 * Fields that require explicit consent to share
 */
export const CONSENT_REQUIRED_FIELDS = [
	'noise_mode',
	'session_length',
	'pressure_tolerance',
	'budget_range',
	'feedback_style',
	'skills_acquired',
	'current_focus',
	'struggle_areas',
	'best_times',
	'avoid_times',
	'budget_remaining_eur',
	'workload_level'
];

/**
 * Fields that are NEVER shared - influence only via boolean flags
 */
export const PRIVATE_FIELDS = [
	'family_status',
	'dependents',
	'dependent_ages',
	'childcare_hours',
	'health_conditions',
	'health_appointments',
	'financial_constraint',
	'evening_available_after',
	'work_type',
	'schedule',
	'housing',
	'neighbor_situation'
];

// ============================================
// Core Privacy Filter
// ============================================

/**
 * Get a field value from nested context structure
 */
export function getFieldValue(ctx: VCPContext, field: string): unknown {
	// Check in order of access level
	const sources = [
		ctx.public_profile,
		ctx.portable_preferences,
		ctx.current_skills,
		ctx.constraints,
		ctx.availability,
		ctx.shared_with_manager
	];

	for (const source of sources) {
		if (source && field in source) {
			return (source as Record<string, unknown>)[field];
		}
	}

	return undefined;
}

/**
 * Check if a field is in the private context
 */
export function isPrivateField(ctx: VCPContext, field: string): boolean {
	if (PRIVATE_FIELDS.includes(field)) return true;
	if (ctx.private_context && field in ctx.private_context) return true;
	return false;
}

/**
 * Filter context for a platform, respecting consent and privacy rules
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

	// Always include basic public fields
	for (const field of PUBLIC_FIELDS) {
		const value = getFieldValue(fullContext, field);
		if (value !== undefined) {
			(result.public as Record<string, unknown>)[field] = value;
			shared.push(field);
		}
	}

	// Process required fields from manifest
	for (const field of manifest.context_requirements.required) {
		if (isPrivateField(fullContext, field)) {
			// Private fields are NEVER shared directly
			withheld.push(field);
			continue;
		}

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

	// Process optional fields from manifest
	for (const field of manifest.context_requirements.optional) {
		if (isPrivateField(fullContext, field)) {
			withheld.push(field);
			continue;
		}

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

	// Add constraint flags (always boolean, never the WHY)
	result.constraints = extractConstraintFlags(fullContext);

	// Count how many private fields influenced the constraints
	const privateFieldsInfluenced = Object.values(result.constraints).filter(Boolean).length;

	// Log the sharing event
	logAuditEntry({
		id: `filter-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
		timestamp: new Date().toISOString(),
		event_type: 'context_shared',
		platform_id: manifest.platform_id,
		data_shared: [...new Set(shared)],
		data_withheld: [...new Set(withheld)],
		private_fields_influenced: privateFieldsInfluenced,
		private_fields_exposed: 0 // Always 0 by design
	});

	return result;
}

// ============================================
// Constraint Flag Extraction
// ============================================

/**
 * Extract boolean constraint flags from context
 * This is the core privacy mechanism: private details become boolean flags
 */
export function extractConstraintFlags(ctx: VCPContext): ConstraintFlags {
	const constraints = ctx.constraints || {};
	const privateCtx = ctx.private_context || {};

	return {
		time_limited:
			constraints.time_limited ||
			!!privateCtx.childcare_hours ||
			!!privateCtx.schedule_irregular,

		budget_limited:
			constraints.budget_limited || !!privateCtx.financial_constraint,

		noise_restricted:
			constraints.noise_restricted ||
			!!privateCtx.noise_sensitive ||
			!!privateCtx.neighbor_situation,

		energy_variable:
			constraints.energy_variable ||
			!!privateCtx.health_conditions ||
			!!privateCtx.schedule, // Shift work affects energy

		schedule_irregular:
			constraints.schedule_irregular ||
			!!privateCtx.schedule ||
			!!privateCtx.childcare_hours,

		mobility_limited: constraints.mobility_limited || !!privateCtx.mobility_limited,

		health_considerations:
			constraints.health_considerations ||
			!!privateCtx.health_conditions ||
			!!privateCtx.health_appointments
	};
}

// ============================================
// Stakeholder Filtering
// ============================================

/**
 * Get fields visible to a specific stakeholder type
 */
export function getStakeholderVisibleFields(
	ctx: VCPContext,
	stakeholder: StakeholderType
): string[] {
	const sharingSettings = ctx.sharing_settings?.[stakeholder];
	if (!sharingSettings) {
		// Default: only public fields
		return PUBLIC_FIELDS;
	}

	const visible = [...PUBLIC_FIELDS];

	// Add explicitly shared fields
	if (sharingSettings.share) {
		for (const field of sharingSettings.share) {
			if (!isPrivateField(ctx, field) && !visible.includes(field)) {
				visible.push(field);
			}
		}
	}

	// Remove hidden fields
	if (sharingSettings.hide) {
		return visible.filter((f) => !sharingSettings.hide?.includes(f));
	}

	return visible;
}

/**
 * Get fields hidden from a specific stakeholder type
 */
export function getStakeholderHiddenFields(
	ctx: VCPContext,
	stakeholder: StakeholderType
): string[] {
	const visibleFields = getStakeholderVisibleFields(ctx, stakeholder);

	// All private fields are always hidden
	const hidden = [...PRIVATE_FIELDS];

	// Add any consent-required fields not in visible list
	for (const field of CONSENT_REQUIRED_FIELDS) {
		if (!visibleFields.includes(field) && !hidden.includes(field)) {
			hidden.push(field);
		}
	}

	return hidden;
}

// ============================================
// Sharing Preview
// ============================================

/**
 * Preview what would be shared/withheld for a platform (before consent)
 */
export function getSharePreview(
	ctx: VCPContext,
	manifest: PlatformManifest
): { wouldShare: string[]; wouldWithhold: string[]; requiresConsent: string[] } {
	const wouldShare = [...PUBLIC_FIELDS];
	const wouldWithhold: string[] = [];
	const requiresConsent: string[] = [];

	// Check sharing settings if configured
	const platformSettings = ctx.sharing_settings?.platforms || { share: [], hide: [] };

	// Process required fields
	for (const field of manifest.context_requirements.required) {
		if (isPrivateField(ctx, field)) {
			wouldWithhold.push(field);
		} else if (platformSettings.hide?.includes(field)) {
			wouldWithhold.push(field);
		} else {
			requiresConsent.push(field);
		}
	}

	// Process optional fields
	for (const field of manifest.context_requirements.optional) {
		if (isPrivateField(ctx, field)) {
			wouldWithhold.push(field);
		} else if (platformSettings.share?.includes(field)) {
			wouldShare.push(field);
		} else {
			// Optional fields default to withheld unless explicitly shared
			wouldWithhold.push(field);
		}
	}

	// Private context fields are always withheld
	if (ctx.private_context) {
		for (const key of Object.keys(ctx.private_context)) {
			if (key !== '_note' && !wouldWithhold.includes(key)) {
				wouldWithhold.push(key);
			}
		}
	}

	return {
		wouldShare: [...new Set(wouldShare)],
		wouldWithhold: [...new Set(wouldWithhold)],
		requiresConsent: [...new Set(requiresConsent)]
	};
}

// ============================================
// Display Helpers
// ============================================

/**
 * Format field name for display
 */
export function formatFieldName(field: string): string {
	return field
		.replace(/_/g, ' ')
		.replace(/\b\w/g, (c) => c.toUpperCase());
}

/**
 * Get privacy level badge for a field
 */
export function getFieldPrivacyLevel(
	field: string
): 'public' | 'consent-required' | 'private' {
	if (PUBLIC_FIELDS.includes(field)) return 'public';
	if (PRIVATE_FIELDS.includes(field)) return 'private';
	return 'consent-required';
}

/**
 * Generate a privacy summary for display
 */
export function generatePrivacySummary(
	shared: string[],
	withheld: string[],
	privateInfluenced: number
): string {
	const parts: string[] = [];

	if (shared.length > 0) {
		parts.push(`${shared.length} fields shared`);
	}

	if (withheld.length > 0) {
		parts.push(`${withheld.length} fields kept private`);
	}

	if (privateInfluenced > 0) {
		parts.push(`${privateInfluenced} private constraints influenced recommendations (details not exposed)`);
	}

	return parts.join(' • ');
}
