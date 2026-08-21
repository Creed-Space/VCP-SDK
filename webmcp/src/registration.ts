/** Register VCP tools through the current WebMCP imperative API. */

import type {
	VCPWebMCPConfig,
	VCPWebMCPResult,
	WebMCPModelContext,
	WebMCPRegistrationFailure
} from './types.js';
import { createVCPTools } from './tools.js';

const DEFAULT_REGISTRATION_TIMEOUT_MS = 5000;

function isRecord(value: unknown): value is Record<string, unknown> {
	return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function safeErrorMessage(error: unknown): string {
	try {
		if (error instanceof Error && typeof error.message === 'string') return error.message;
		return String(error);
	} catch {
		return 'unknown registration error';
	}
}

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
		reason: safeErrorMessage(error)
	};
}

async function registerWithTimeout(
	operation: Promise<void>,
	timeoutMs: number,
): Promise<void> {
	let timer: ReturnType<typeof setTimeout> | undefined;
	try {
		await Promise.race([
			operation,
			new Promise<never>((_resolve, reject) => {
				timer = setTimeout(
					() => reject(new Error(`registration timed out after ${timeoutMs}ms`)),
					timeoutMs,
				);
			}),
		]);
	} finally {
		if (timer !== undefined) clearTimeout(timer);
	}
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
	const safeConfig: VCPWebMCPConfig = isRecord(config) ? config : {};
	const timeoutMs = safeConfig.registrationTimeoutMs ?? DEFAULT_REGISTRATION_TIMEOUT_MS;
	if (!Number.isInteger(timeoutMs) || timeoutMs < 1 || timeoutMs > 30000) {
		throw new RangeError('registrationTimeoutMs must be an integer from 1 to 30000');
	}

	const ownedControllers: AbortController[] = [];
	const registered: string[] = [];
	const failed: WebMCPRegistrationFailure[] = [];

	for (const tool of createVCPTools(safeConfig)) {
		const controller = new AbortController();
		try {
			await registerWithTimeout(
				resolved.context.registerTool(tool, { signal: controller.signal }),
				timeoutMs,
			);
			registered.push(tool.name);
			ownedControllers.push(controller);
		} catch (error) {
			controller.abort();
			const failure = registrationFailure(tool.name, error);
			failed.push(failure);
			try {
				safeConfig.onRegistrationError?.(failure);
			} catch {
				// Error reporting cannot interrupt ownership of later registrations.
			}
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
			for (const controller of ownedControllers) controller.abort();
		}
	};
}
