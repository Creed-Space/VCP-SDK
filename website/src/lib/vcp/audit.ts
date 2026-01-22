/**
 * VCP Audit Trail
 * Logs all data sharing events with dual-view support
 */

import { writable, derived, get, type Readable, type Writable } from 'svelte/store';
import type { AuditEntry, StakeholderAuditEntry, StakeholderType, AuditEventType } from './types';

// ============================================
// Storage
// ============================================

const AUDIT_STORAGE_KEY = 'vcp_audit_trail';

function isBrowser(): boolean {
	return typeof window !== 'undefined' && typeof localStorage !== 'undefined';
}

function loadAuditFromStorage(): AuditEntry[] {
	if (!isBrowser()) return [];
	try {
		const stored = localStorage.getItem(AUDIT_STORAGE_KEY);
		return stored ? JSON.parse(stored) : [];
	} catch {
		return [];
	}
}

function saveAuditToStorage(entries: AuditEntry[]): void {
	if (!isBrowser()) return;
	try {
		// Keep only last 100 entries to prevent storage bloat
		const trimmed = entries.slice(-100);
		localStorage.setItem(AUDIT_STORAGE_KEY, JSON.stringify(trimmed));
	} catch {
		console.warn('Failed to save audit trail to localStorage');
	}
}

// ============================================
// Audit Store
// ============================================

interface AuditStore extends Writable<AuditEntry[]> {
	clear: () => void;
	getByPlatform: (platformId: string) => AuditEntry[];
	getByEventType: (eventType: AuditEventType) => AuditEntry[];
	getToday: () => AuditEntry[];
}

function createAuditStore(): AuditStore {
	const initial = loadAuditFromStorage();
	const { subscribe, set, update } = writable<AuditEntry[]>(initial);

	return {
		subscribe,
		set: (entries: AuditEntry[]) => {
			set(entries);
			saveAuditToStorage(entries);
		},
		update,
		clear: () => {
			set([]);
			saveAuditToStorage([]);
		},
		getByPlatform: (platformId: string): AuditEntry[] => {
			const entries = get({ subscribe });
			return entries.filter((e) => e.platform_id === platformId);
		},
		getByEventType: (eventType: AuditEventType): AuditEntry[] => {
			const entries = get({ subscribe });
			return entries.filter((e) => e.event_type === eventType);
		},
		getToday: (): AuditEntry[] => {
			const entries = get({ subscribe });
			const today = new Date().toISOString().split('T')[0];
			return entries.filter((e) => e.timestamp.startsWith(today));
		}
	};
}

export const auditTrail = createAuditStore();

// ============================================
// Logging Functions
// ============================================

/**
 * Log an audit entry
 */
export function logAuditEntry(entry: AuditEntry): void {
	auditTrail.update((entries) => {
		const updated = [...entries, entry];
		saveAuditToStorage(updated);
		return updated;
	});
}

/**
 * Create a context_shared audit entry
 */
export function logContextShared(
	platformId: string,
	shared: string[],
	withheld: string[],
	privateInfluenced: number
): AuditEntry {
	const entry: AuditEntry = {
		id: `share-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
		timestamp: new Date().toISOString(),
		event_type: 'context_shared',
		platform_id: platformId,
		data_shared: shared,
		data_withheld: withheld,
		private_fields_influenced: privateInfluenced,
		private_fields_exposed: 0 // Always 0 by design
	};
	logAuditEntry(entry);
	return entry;
}

/**
 * Create a recommendation_generated audit entry
 */
export function logRecommendation(
	platformId: string,
	contextUsed: string[],
	contextWithheld: string[],
	details?: Record<string, unknown>
): AuditEntry {
	const entry: AuditEntry = {
		id: `rec-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
		timestamp: new Date().toISOString(),
		event_type: 'recommendation_generated',
		platform_id: platformId,
		data_shared: contextUsed,
		data_withheld: contextWithheld,
		private_fields_influenced: contextWithheld.length > 0 ? 1 : 0,
		private_fields_exposed: 0,
		details
	};
	logAuditEntry(entry);
	return entry;
}

/**
 * Create an adjustment_recorded audit entry (for skip days)
 */
export function logAdjustment(
	platformId: string,
	publicReason: string,
	privateDetails: Record<string, unknown>
): AuditEntry {
	const entry: AuditEntry = {
		id: `adj-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
		timestamp: new Date().toISOString(),
		event_type: 'adjustment_recorded',
		platform_id: platformId,
		data_shared: ['adjustment_count', 'adjustment_date'],
		data_withheld: Object.keys(privateDetails),
		private_fields_influenced: 1,
		private_fields_exposed: 0,
		details: {
			public_summary: publicReason,
			// Private details stored but never exposed to platforms
			_private: privateDetails
		}
	};
	logAuditEntry(entry);
	return entry;
}

// ============================================
// Derived Views
// ============================================

/**
 * Today's audit entries
 */
export const todayAudit: Readable<AuditEntry[]> = derived(auditTrail, ($entries) => {
	const today = new Date().toISOString().split('T')[0];
	return $entries.filter((e) => e.timestamp.startsWith(today));
});

/**
 * Unique platforms in audit trail
 */
export const auditedPlatforms: Readable<string[]> = derived(auditTrail, ($entries) => {
	const platforms = new Set($entries.map((e) => e.platform_id).filter(Boolean));
	return Array.from(platforms) as string[];
});

// ============================================
// Stakeholder Views
// ============================================

/**
 * Generate stakeholder-appropriate view of audit entries
 * Key feature: removes all private detail while showing compliance
 */
export function getStakeholderView(
	entries: AuditEntry[],
	stakeholderType: StakeholderType
): StakeholderAuditEntry[] {
	return entries.map((entry) => {
		// Base stakeholder entry - stripped of private information
		const stakeholderEntry: StakeholderAuditEntry = {
			timestamp: entry.timestamp,
			event_type: entry.event_type,
			private_context_used: (entry.private_fields_influenced ?? 0) > 0,
			private_context_exposed: false // Always false by design
		};

		// Add stakeholder-specific compliance info
		switch (stakeholderType) {
			case 'hr':
				stakeholderEntry.compliance_status = {
					policy_followed: true,
					budget_compliant: entry.details?.budget_compliant as boolean | undefined ?? true,
					mandatory_addressed: entry.details?.mandatory_addressed as boolean | undefined ?? true
				};
				break;

			case 'manager':
				stakeholderEntry.compliance_status = {
					policy_followed: true,
					budget_compliant: entry.details?.budget_compliant as boolean | undefined ?? true
				};
				// Manager sees slightly more but still no private reasons
				break;

			case 'community':
				// Community sees the least - just progress summaries
				stakeholderEntry.progress_summary = entry.details?.progress_summary as string | undefined;
				// No compliance info, no field counts
				break;

			case 'coach':
				// Coach sees progress but not personal constraints
				stakeholderEntry.progress_summary = entry.details?.progress_summary as string | undefined;
				break;

			case 'employee':
				// Employee sees everything (their own data)
				// But this function is for other stakeholders, so use getFullView instead
				break;
		}

		return stakeholderEntry;
	});
}

/**
 * Get full audit view for the user themselves
 */
export function getFullView(entries: AuditEntry[]): AuditEntry[] {
	// User sees everything about their own data
	return entries;
}

/**
 * Generate comparison view: what user sees vs what stakeholder sees
 */
export function getComparisonView(
	entries: AuditEntry[],
	stakeholderType: StakeholderType
): { userView: AuditEntry[]; stakeholderView: StakeholderAuditEntry[] } {
	return {
		userView: getFullView(entries),
		stakeholderView: getStakeholderView(entries, stakeholderType)
	};
}

// ============================================
// Summary Statistics
// ============================================

interface AuditSummary {
	totalEvents: number;
	eventsByType: Record<AuditEventType, number>;
	platformsAccessed: string[];
	fieldsSharedCount: number;
	fieldsWithheldCount: number;
	privateInfluencedCount: number;
	privateExposedCount: number; // Should always be 0
}

/**
 * Generate summary statistics for audit entries
 */
export function getAuditSummary(entries: AuditEntry[]): AuditSummary {
	const eventsByType: Record<string, number> = {};
	const platforms = new Set<string>();
	let fieldsShared = 0;
	let fieldsWithheld = 0;
	let privateInfluenced = 0;
	let privateExposed = 0;

	for (const entry of entries) {
		// Count event types
		eventsByType[entry.event_type] = (eventsByType[entry.event_type] || 0) + 1;

		// Track platforms
		if (entry.platform_id) {
			platforms.add(entry.platform_id);
		}

		// Count fields
		fieldsShared += entry.data_shared?.length || 0;
		fieldsWithheld += entry.data_withheld?.length || 0;
		privateInfluenced += entry.private_fields_influenced || 0;
		privateExposed += entry.private_fields_exposed || 0;
	}

	return {
		totalEvents: entries.length,
		eventsByType: eventsByType as Record<AuditEventType, number>,
		platformsAccessed: Array.from(platforms),
		fieldsSharedCount: fieldsShared,
		fieldsWithheldCount: fieldsWithheld,
		privateInfluencedCount: privateInfluenced,
		privateExposedCount: privateExposed // Should always be 0
	};
}
