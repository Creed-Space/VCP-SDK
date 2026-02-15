/**
 * Audience Store
 * Manages the current audience mode (developer, business, general)
 * for layered content presentation
 */

import { writable } from 'svelte/store';

export type AudienceType = 'developer' | 'business' | 'general';

const STORAGE_KEY = 'vcp_audience';

function getInitialAudience(): AudienceType {
	if (typeof window === 'undefined') return 'general';
	const stored = localStorage.getItem(STORAGE_KEY);
	if (stored && ['developer', 'business', 'general'].includes(stored)) {
		return stored as AudienceType;
	}
	return 'general';
}

function createAudienceStore() {
	const { subscribe, set, update } = writable<AudienceType>(getInitialAudience());

	return {
		subscribe,
		set: (value: AudienceType) => {
			if (typeof window !== 'undefined') {
				localStorage.setItem(STORAGE_KEY, value);
			}
			set(value);
		},
		toggle: () => {
			update((current) => {
				const order: AudienceType[] = ['general', 'business', 'developer'];
				const nextIndex = (order.indexOf(current) + 1) % order.length;
				const next = order[nextIndex];
				if (typeof window !== 'undefined') {
					localStorage.setItem(STORAGE_KEY, next);
				}
				return next;
			});
		}
	};
}

export const audience = createAudienceStore();

// Audience metadata for display
export const AUDIENCE_META: Record<AudienceType, { label: string; icon: string; description: string }> = {
	general: {
		label: 'Everyone',
		icon: '👥',
		description: 'Accessible explanations for all'
	},
	business: {
		label: 'Business',
		icon: '💼',
		description: 'Value propositions and case studies'
	},
	developer: {
		label: 'Developer',
		icon: '🛠️',
		description: 'Technical details and API docs'
	}
};
