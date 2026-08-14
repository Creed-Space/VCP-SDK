/** Register VCP tools through the current WebMCP imperative API. */

import type {
	VCPWebMCPConfig,
	VCPWebMCPResult,
	WebMCPModelContext,
	WebMCPRegistrationFailure
} from './types.js';
import { createVCPTools } from './tools.js';

function emptyResult(): VCPWebMCPResult {
	return {
		registered: [],
		failed: [],
		api: 'unavailable',
		cleanup: () => {}
	};
}

function registrationFailure(name: string, error: unknown): WebMCPRegistrationFailure {
	return {
		name,
		reason: error instanceof Error ? error.message : String(error)
	};
}

function findModelContext(): {
	context: WebMCPModelContext;
	api: 'document' | 'navigator';
} | null {
	if (
		typeof document !== 'undefined' &&
		document.modelContext &&
		typeof document.modelContext.registerTool === 'function'
	) {
		return { context: document.modelContext, api: 'document' };
	}

	// Chrome exposed the preview API on Navigator before moving it to Document.
	// Keep this compatibility path isolated so it can be removed deliberately.
	if (
		typeof navigator !== 'undefined' &&
		navigator.modelContext &&
		typeof navigator.modelContext.registerTool === 'function'
	) {
		return { context: navigator.modelContext, api: 'navigator' };
	}

	return null;
}

/**
 * Register VCP tools with `document.modelContext`.
 *
 * Registration is sequential and awaited. A rejected tool is reported in
 * `failed`; previously accepted tools remain owned by the returned cleanup
 * function. Cleanup is idempotent and uses the AbortSignal lifecycle required
 * by the current WebMCP API.
 */
export async function registerVCPTools(
	config: VCPWebMCPConfig = {}
): Promise<VCPWebMCPResult> {
	const resolved = findModelContext();
	if (!resolved) return emptyResult();

	const controller = new AbortController();
	const registered: string[] = [];
	const failed: WebMCPRegistrationFailure[] = [];

	for (const tool of createVCPTools(config)) {
		try {
			await resolved.context.registerTool(tool, { signal: controller.signal });
			registered.push(tool.name);
		} catch (error) {
			const failure = registrationFailure(tool.name, error);
			failed.push(failure);
			config.onRegistrationError?.(failure);
		}
	}

	let cleaned = false;
	return {
		registered,
		failed,
		api: resolved.api,
		cleanup() {
			if (cleaned) return;
			cleaned = true;
			controller.abort();
		}
	};
}
