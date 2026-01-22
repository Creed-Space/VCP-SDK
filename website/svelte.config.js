import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	preprocess: vitePreprocess(),
	kit: {
		adapter: adapter({
			pages: 'build',
			assets: 'build',
			fallback: '404.html',
			precompress: false,
			strict: true
		}),
		paths: {
			// For GitHub Pages - will be set by GitHub Actions
			// Leave empty for custom domain (valuecontextprotocol.org)
			base: process.env.BASE_PATH || ''
		},
		prerender: {
			handleHttpError: ({ path, message }) => {
				// Ignore missing favicon - we use an SVG one
				if (path === '/favicon.ico') {
					return;
				}
				// Ignore links to docs pages that are coming soon
				if (path.startsWith('/docs/') && !path.includes('getting-started') && !path.includes('concepts') && !path.includes('csm1-specification') && !path.includes('api-reference')) {
					console.warn(`Skipping prerender for coming soon doc: ${path}`);
					return;
				}
				throw new Error(message);
			}
		}
	}
};

export default config;
