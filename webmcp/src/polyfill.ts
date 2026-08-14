/**
 * @creed-space/vcp-sdk — MCP-B Polyfill Loader
 *
 * Conditionally invokes a caller-supplied polyfill loader to populate the
 * current `document.modelContext` contract. The legacy Navigator location is
 * accepted only for compatibility with earlier preview implementations.
 *
 * Gated behind ?webmcp=polyfill query param. No-op otherwise.
 *
 * @see https://docs.mcp-b.ai/
 * @see https://github.com/WebMCP-org/npm-packages
 */

let polyfillLoaded = false;
let loading: Promise<boolean> | null = null;

export interface PolyfillLoadOptions {
	/** Bundled or pinned application-owned loader. No network URL is accepted. */
	loader?: () => Promise<void>;
	/** Optional application-owned error sink. The SDK does not log by default. */
	onError?: (error: Error) => void;
}

/** Return true only when a usable current or legacy WebMCP API is present. */
export function hasWebMCPModelContext(): boolean {
	const current =
		typeof document !== 'undefined' &&
		document.modelContext &&
		typeof document.modelContext.registerTool === 'function';
	if (current) return true;

	return Boolean(
		typeof navigator !== 'undefined' &&
			navigator.modelContext &&
			typeof navigator.modelContext.registerTool === 'function'
	);
}

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
 * The SDK never injects a remote script. Applications that opt in must supply
 * a bundled or otherwise application-controlled loader. Returns true if that
 * loader completed, false if loading was not requested, unavailable, or failed.
 *
 * Safe to call multiple times — only loads once.
 */
export async function loadPolyfillIfRequested(
	options: PolyfillLoadOptions = {}
): Promise<boolean> {
	if (typeof window === 'undefined') return false;
	if (polyfillLoaded) return true;
	if (!isPolyfillRequested()) return false;
	if (hasWebMCPModelContext()) return true;
	if (!options.loader) return false;
	const loader = options.loader;

	if (loading) return loading;

	loading = (async () => {
		try {
			await loader();
			if (!hasWebMCPModelContext()) {
				throw new Error(
					'Application-owned loader completed without exposing document.modelContext'
				);
			}
			polyfillLoaded = true;
			return true;
		} catch (err) {
			const error = err instanceof Error ? err : new Error(String(err));
			options.onError?.(error);
			loading = null;
			return false;
		}
	})();

	return loading;
}
