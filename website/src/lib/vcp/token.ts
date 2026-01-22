/**
 * VCP Token Encoding - CSM-1 (Compact State Message) Format
 *
 * Encodes VCP context into a compact, human-readable token format
 * using emoji shortcodes for constraints and privacy markers.
 *
 * Format:
 * VCP:<version>:<profile_id>
 * C:<constitution_id>@<version>
 * P:<persona>:<adherence>
 * G:<goal>:<experience>:<learning_style>
 * X:<constraint_flags>
 * F:<active_flags>
 * S:<private_markers>
 */

import type { VCPContext, ConstraintFlags, PortablePreferences } from './types';

// ============================================
// Emoji Shortcodes
// ============================================

export const CONSTRAINT_EMOJI = {
	noise_restricted: '<i class="fa-solid fa-volume-xmark" aria-hidden="true"></i>',
	budget_limited: '<i class="fa-solid fa-coins" aria-hidden="true"></i>',
	energy_variable: '<i class="fa-solid fa-bolt" aria-hidden="true"></i>',
	time_limited: '⏰',
	schedule_irregular: '<i class="fa-solid fa-calendar" aria-hidden="true"></i>',
	mobility_limited: '<i class="fa-solid fa-person-walking" aria-hidden="true"></i>',
	health_considerations: '<i class="fa-solid fa-pills" aria-hidden="true"></i>'
} as const;

export const PREFERENCE_EMOJI = {
	quiet_preferred: '<i class="fa-solid fa-volume-xmark" aria-hidden="true"></i>',
	silent_required: '<i class="fa-solid fa-bell-slash" aria-hidden="true"></i>',
	low: '<i class="fa-solid fa-coins" aria-hidden="true"></i>',
	free_only: '🆓',
	high: '<i class="fa-solid fa-gem" aria-hidden="true"></i>',
	flexible: '⏰',
	'15_minutes': '<i class="fa-solid fa-bolt" aria-hidden="true"></i>',
	'30_minutes': '<i class="fa-solid fa-stopwatch" aria-hidden="true"></i>',
	'60_minutes': '<i class="fa-solid fa-clock" aria-hidden="true"></i>'
} as const;

export const PRIVATE_MARKER = '<i class="fa-solid fa-lock" aria-hidden="true"></i>';
export const SHARED_MARKER = '<i class="fa-solid fa-check" aria-hidden="true"></i>';

// ============================================
// CSM-1 Encoding
// ============================================

/**
 * Encode a VCP context into CSM-1 format
 */
export function encodeContextToCSM1(ctx: VCPContext): string {
	const lines: string[] = [];

	// Line 1: VCP header
	lines.push(`VCP:${ctx.vcp_version}:${ctx.profile_id}`);

	// Line 2: Constitution reference
	lines.push(`C:${ctx.constitution.id}@${ctx.constitution.version}`);

	// Line 3: Persona and adherence
	lines.push(`P:${ctx.constitution.persona || 'muse'}:${ctx.constitution.adherence || 3}`);

	// Line 4: Goal context
	const goal = ctx.public_profile?.goal || 'unset';
	const experience = ctx.public_profile?.experience || 'beginner';
	const style = ctx.public_profile?.learning_style || 'mixed';
	lines.push(`G:${goal}:${experience}:${style}`);

	// Line 5: Constraint flags with emoji
	lines.push(encodeConstraints(ctx.constraints, ctx.portable_preferences));

	// Line 6: Active flags
	lines.push(encodeActiveFlags(ctx.constraints));

	// Line 7: Private markers (show categories, not values)
	lines.push(encodePrivateMarkers(ctx.private_context));

	return lines.join('\n');
}

/**
 * Encode constraint flags with emoji shortcodes
 */
function encodeConstraints(
	constraints?: ConstraintFlags,
	prefs?: PortablePreferences
): string {
	const parts: string[] = [];

	// From constraints
	if (constraints?.noise_restricted) parts.push('<i class="fa-solid fa-volume-xmark" aria-hidden="true"></i>');
	if (constraints?.time_limited) parts.push('⏰lim');
	if (constraints?.energy_variable) parts.push('<i class="fa-solid fa-bolt" aria-hidden="true"></i>var');

	// From preferences
	if (prefs?.noise_mode === 'quiet_preferred') parts.push('<i class="fa-solid fa-volume-xmark" aria-hidden="true"></i>quiet');
	if (prefs?.noise_mode === 'silent_required') parts.push('<i class="fa-solid fa-bell-slash" aria-hidden="true"></i>silent');
	if (prefs?.budget_range === 'low') parts.push('<i class="fa-solid fa-coins" aria-hidden="true"></i>low');
	if (prefs?.budget_range === 'free_only') parts.push('🆓');
	if (prefs?.session_length) parts.push(`<i class="fa-solid fa-stopwatch" aria-hidden="true"></i>${prefs.session_length.replace('_', '')}`);

	if (parts.length === 0) {
		return 'X:none';
	}

	return `X:${parts.join(':')}`;
}

/**
 * Encode which flags are currently active
 */
function encodeActiveFlags(constraints?: ConstraintFlags): string {
	const flags: string[] = [];

	if (constraints?.time_limited) flags.push('time_limited');
	if (constraints?.noise_restricted) flags.push('noise_restricted');
	if (constraints?.budget_limited) flags.push('budget_limited');
	if (constraints?.energy_variable) flags.push('energy_variable');
	if (constraints?.schedule_irregular) flags.push('schedule_irregular');

	if (flags.length === 0) {
		return 'F:none';
	}

	return `F:${flags.join('|')}`;
}

/**
 * Encode private context markers (categories only, never values)
 */
function encodePrivateMarkers(privateContext?: Record<string, unknown>): string {
	if (!privateContext) {
		return 'S:none';
	}

	const markers: string[] = [];
	const keys = Object.keys(privateContext).filter(
		(k) => k !== '_note' && k !== '_reasoning'
	);

	// Group by category prefix
	const categories = new Set<string>();
	for (const key of keys) {
		// Extract category from key (e.g., work_type -> work)
		const category = key.split('_')[0];
		categories.add(category);
	}

	for (const cat of categories) {
		markers.push(`${PRIVATE_MARKER}${cat}`);
	}

	if (markers.length === 0) {
		return 'S:none';
	}

	return `S:${markers.join('|')}`;
}

// ============================================
// Display Formatting
// ============================================

/**
 * Format CSM-1 token for display with box drawing
 */
export function formatTokenForDisplay(csm1: string): string {
	const lines = csm1.split('\n');
	const maxLen = Math.max(...lines.map((l) => l.length), 40);

	const border = '─'.repeat(maxLen + 2);
	const formatted = lines.map((l) => `│ ${l.padEnd(maxLen)} │`).join('\n');

	return `┌${border}┐\n${formatted}\n└${border}┘`;
}

/**
 * Get emoji legend for display
 */
export function getEmojiLegend(): { emoji: string; meaning: string }[] {
	return [
		{ emoji: '<i class="fa-solid fa-volume-xmark" aria-hidden="true"></i>', meaning: 'quiet mode' },
		{ emoji: '<i class="fa-solid fa-bell-slash" aria-hidden="true"></i>', meaning: 'silent required' },
		{ emoji: '<i class="fa-solid fa-coins" aria-hidden="true"></i>', meaning: 'budget tier' },
		{ emoji: '🆓', meaning: 'free only' },
		{ emoji: '<i class="fa-solid fa-bolt" aria-hidden="true"></i>', meaning: 'energy variable' },
		{ emoji: '⏰', meaning: 'time limited' },
		{ emoji: '<i class="fa-solid fa-stopwatch" aria-hidden="true"></i>', meaning: 'session length' },
		{ emoji: '<i class="fa-solid fa-calendar" aria-hidden="true"></i>', meaning: 'irregular schedule' },
		{ emoji: '<i class="fa-solid fa-lock" aria-hidden="true"></i>', meaning: 'private (hidden value)' },
		{ emoji: '<i class="fa-solid fa-check" aria-hidden="true"></i>', meaning: 'shared' }
	];
}

/**
 * Parse CSM-1 token back into components (for display/debugging)
 */
export function parseCSM1Token(token: string): Record<string, string> {
	const lines = token.split('\n');
	const parsed: Record<string, string> = {};

	for (const line of lines) {
		const [key, ...rest] = line.split(':');
		if (key && rest.length > 0) {
			parsed[key] = rest.join(':');
		}
	}

	return parsed;
}

/**
 * Get what would be transmitted vs withheld for a context
 */
export function getTransmissionSummary(ctx: VCPContext): {
	transmitted: string[];
	withheld: string[];
	influencing: string[];
} {
	const transmitted: string[] = [];
	const withheld: string[] = [];
	const influencing: string[] = [];

	// Public profile - transmitted
	if (ctx.public_profile) {
		for (const [key, value] of Object.entries(ctx.public_profile)) {
			if (value !== undefined && value !== null) {
				transmitted.push(key);
			}
		}
	}

	// Constraints - transmitted as flags, influencing decisions
	if (ctx.constraints) {
		for (const [key, value] of Object.entries(ctx.constraints)) {
			if (value === true) {
				influencing.push(key);
			}
		}
	}

	// Private context - withheld
	if (ctx.private_context) {
		for (const key of Object.keys(ctx.private_context)) {
			if (key !== '_note' && key !== '_reasoning') {
				withheld.push(key);
			}
		}
	}

	return { transmitted, withheld, influencing };
}

export default {
	encodeContextToCSM1,
	formatTokenForDisplay,
	getEmojiLegend,
	parseCSM1Token,
	getTransmissionSummary,
	CONSTRAINT_EMOJI,
	PRIVATE_MARKER,
	SHARED_MARKER
};
