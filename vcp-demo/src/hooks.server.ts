import type { Handle } from '@sveltejs/kit';

/**
 * Server hooks for VCP Demo site
 *
 * Note: URL restructure deferred - demos remain at existing paths for now.
 * Category index pages link directly to existing demo routes.
 */

export const handle: Handle = async ({ event, resolve }) => {
	return resolve(event);
};
