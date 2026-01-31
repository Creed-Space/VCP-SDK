import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async () => {
	// Redirect to demos page - sharing demos are featured there
	throw redirect(301, '/demos');
};
