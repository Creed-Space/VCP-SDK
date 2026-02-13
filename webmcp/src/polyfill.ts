/**
 * @vcp/webmcp — MCP-B Polyfill Loader
 *
 * Conditionally loads the @mcp-b/global polyfill to populate
 * navigator.modelContext in browsers without native WebMCP support.
 *
 * Gated behind ?webmcp=polyfill query param. No-op otherwise.
 *
 * @see https://docs.mcp-b.ai/
 * @see https://github.com/WebMCP-org/npm-packages
 */

let polyfillLoaded = false;
let loading: Promise<boolean> | null = null;

/**
 * Check if the polyfill was requested via URL query param.
 */
export function isPolyfillRequested(): boolean {
	if (typeof window === 'undefined') return false;
	const params = new URLSearchParams(window.location.search);
	return params.get('webmcp') === 'polyfill';
}

/**
 * Load the MCP-B polyfill if requested via ?webmcp=polyfill.
 *
 * Loads the polyfill script from CDN, which populates navigator.modelContext.
 * Returns true if the polyfill was loaded, false if not needed or failed.
 *
 * Safe to call multiple times — only loads once.
 */
export async function loadPolyfillIfRequested(): Promise<boolean> {
	if (typeof window === 'undefined') return false;
	if (polyfillLoaded) return true;
	if (!isPolyfillRequested()) return false;

	if (loading) return loading;

	loading = (async () => {
		try {
			// Load the @mcp-b/global polyfill via dynamic script injection.
			// This populates navigator.modelContext with the reference implementation.
			await new Promise<void>((resolve, reject) => {
				const script = document.createElement('script');
				script.type = 'module';
				script.src = 'https://cdn.jsdelivr.net/npm/@mcp-b/global/dist/index.js';
				script.async = true;
				script.onload = () => resolve();
				script.onerror = () => reject(new Error('Failed to load MCP-B polyfill'));
				document.head.appendChild(script);
			});

			polyfillLoaded = true;
			console.log('[@vcp/webmcp] MCP-B polyfill loaded via ?webmcp=polyfill');
			return true;
		} catch (err) {
			console.warn('[@vcp/webmcp] MCP-B polyfill failed to load:', err);
			return false;
		}
	})();

	return loading;
}
