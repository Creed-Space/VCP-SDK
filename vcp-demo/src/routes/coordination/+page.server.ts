import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async () => {
	// Redirect to demos page - all categories are consolidated there
	throw redirect(301, '/demos');
};
