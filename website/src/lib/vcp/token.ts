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
	noise_restricted: '🔇',
	budget_limited: '💰',
	energy_variable: '⚡',
	time_limited: '⏰',
	schedule_irregular: '📅',
	mobility_limited: '🚶',
	health_considerations: '💊'
} as const;

export const PREFERENCE_EMOJI = {
	quiet_preferred: '🔇',
	silent_required: '🔕',
	low: '💰',
	free_only: '🆓',
	high: '💎',
	flexible: '⏰',
	'15_minutes': '⚡',
	'30_minutes': '⏱️',
	'60_minutes': '🕐'
} as const;

export const PRIVATE_MARKER = '🔒';
export const SHARED_MARKER = '✓';

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
	if (constraints?.noise_restricted) parts.push('🔇');
	if (constraints?.time_limited) parts.push('⏰lim');
	if (constraints?.energy_variable) parts.push('⚡var');

	// From preferences
	if (prefs?.noise_mode === 'quiet_preferred') parts.push('🔇quiet');
	if (prefs?.noise_mode === 'silent_required') parts.push('🔕silent');
	if (prefs?.budget_range === 'low') parts.push('💰low');
	if (prefs?.budget_range === 'free_only') parts.push('🆓');
	if (prefs?.session_length) parts.push(`⏱️${prefs.session_length.replace('_', '')}`);

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
		{ emoji: '🔇', meaning: 'quiet mode' },
		{ emoji: '🔕', meaning: 'silent required' },
		{ emoji: '💰', meaning: 'budget tier' },
		{ emoji: '🆓', meaning: 'free only' },
		{ emoji: '⚡', meaning: 'energy variable' },
		{ emoji: '⏰', meaning: 'time limited' },
		{ emoji: '⏱️', meaning: 'session length' },
		{ emoji: '📅', meaning: 'irregular schedule' },
		{ emoji: '🔒', meaning: 'private (hidden value)' },
		{ emoji: '✓', meaning: 'shared' }
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
