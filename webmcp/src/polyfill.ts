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
let invokingLoader = false;

export interface PolyfillLoadOptions {
	/** Bundled or pinned application-owned loader. No network URL is accepted. */
	loader?: () => Promise<void>;
	/** Optional application-owned error sink. The SDK does not log by default. */
	onError?: (error: Error) => void;
	/** Loader deadline in milliseconds. Defaults to 5000. */
	timeoutMs?: number;
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
	if (polyfillLoaded) {
		if (hasWebMCPModelContext()) return true;
		polyfillLoaded = false;
	}
	if (!isPolyfillRequested()) return false;
	if (hasWebMCPModelContext()) return true;
	if (!options.loader) return false;
	const loader = options.loader;
	const timeoutMs = options.timeoutMs ?? 5000;
	if (!Number.isInteger(timeoutMs) || timeoutMs < 1 || timeoutMs > 30000) {
		throw new RangeError('timeoutMs must be an integer from 1 to 30000');
	}

	if (loading) {
		// Awaiting the same promise from inside its own loader creates a cycle.
		// Report the still-unavailable state to a synchronous re-entrant call;
		// independent concurrent callers continue to join the shared attempt.
		if (invokingLoader) return false;
		return loading;
	}

	// Defer invocation until `loading` holds the promise. A re-entrant loader then
	// observes and joins this same attempt instead of starting a second load.
	loading = Promise.resolve().then(async () => {
		let timer: ReturnType<typeof setTimeout> | undefined;
		try {
			let attempt: Promise<void>;
			invokingLoader = true;
			try {
				attempt = loader();
			} finally {
				invokingLoader = false;
			}
			await Promise.race([
				attempt,
				new Promise<never>((_resolve, reject) => {
					timer = setTimeout(
						() => reject(new Error(`Polyfill loader timed out after ${timeoutMs}ms`)),
						timeoutMs,
					);
				}),
			]);
			if (!hasWebMCPModelContext()) {
				throw new Error(
					'Application-owned loader completed without exposing document.modelContext'
				);
			}
			polyfillLoaded = true;
			return true;
		} catch (err) {
			let error: Error;
			try {
				error = err instanceof Error ? err : new Error(String(err));
			} catch {
				error = new Error('unknown polyfill error');
			}
			try {
				options.onError?.(error);
			} catch {
				// Error sinks are observational and must not poison future retries.
			}
			return false;
		} finally {
			if (timer !== undefined) clearTimeout(timer);
			invokingLoader = false;
			loading = null;
		}
	});

	return loading;
}
