import { afterEach, describe, expect, it, vi } from 'vitest';
import { registerVCPTools } from '../src/registration.js';
import type { WebMCPModelContext, WebMCPToolDefinition } from '../src/types.js';

interface RegistrationCall {
	tool: WebMCPToolDefinition;
	signal: AbortSignal | undefined;
}

function contextWith(
	register: (tool: WebMCPToolDefinition, signal: AbortSignal | undefined) => Promise<void>
): { context: WebMCPModelContext; calls: RegistrationCall[] } {
	const calls: RegistrationCall[] = [];
	return {
		calls,
		context: {
			async registerTool(tool, options) {
				calls.push({ tool, signal: options?.signal });
				await register(tool, options?.signal);
			}
		}
	};
}

function useDocumentContext(context: WebMCPModelContext): void {
	vi.stubGlobal('document', { modelContext: context });
}

afterEach(() => {
	vi.unstubAllGlobals();
});

describe('registerVCPTools', () => {
	it('awaits document.modelContext registrations and records only accepted tools', async () => {
		const accepted: string[] = [];
		const { context, calls } = contextWith(async (tool) => {
			await Promise.resolve();
			accepted.push(tool.name);
		});
		useDocumentContext(context);

		const result = await registerVCPTools({ enableChat: false });

		expect(result.api).toBe('document');
		expect(result.registered).toEqual(['vcp_list_personas']);
		expect(result.failed).toEqual([]);
		expect(accepted).toEqual(['vcp_list_personas']);
		expect(calls[0].signal?.aborted).toBe(false);
	});

	it('reports partial failure and retains cleanup ownership of accepted tools', async () => {
		const failures = vi.fn();
		const { context, calls } = contextWith(async (tool) => {
			if (tool.name === 'vcp_list_personas') throw new Error('duplicate name');
		});
		useDocumentContext(context);

		const result = await registerVCPTools({ onRegistrationError: failures });

		expect(result.registered).toEqual(['vcp_chat']);
		expect(result.failed).toEqual([
			{ name: 'vcp_list_personas', reason: 'duplicate name' }
		]);
		expect(failures).toHaveBeenCalledWith(result.failed[0]);
		expect(calls.every((call) => call.signal === calls[0].signal)).toBe(true);

		result.cleanup();
		expect(calls[0].signal?.aborted).toBe(true);
		result.cleanup();
		expect(calls[0].signal?.aborted).toBe(true);
	});

	it('reports total failure without claiming a registration', async () => {
		const { context } = contextWith(async () => {
			throw new TypeError('registration denied');
		});
		useDocumentContext(context);

		const result = await registerVCPTools();

		expect(result.registered).toEqual([]);
		expect(result.failed.map((failure) => failure.name)).toEqual([
			'vcp_chat',
			'vcp_list_personas'
		]);
	});

	it('prefers Document over the deprecated Navigator location', async () => {
		const documentRegister = vi.fn(async () => {});
		const navigatorRegister = vi.fn(async () => {});
		useDocumentContext({ registerTool: documentRegister });
		vi.stubGlobal('navigator', { modelContext: { registerTool: navigatorRegister } });

		const result = await registerVCPTools({ enableChat: false });

		expect(result.api).toBe('document');
		expect(documentRegister).toHaveBeenCalledOnce();
		expect(navigatorRegister).not.toHaveBeenCalled();
	});

	it('keeps an isolated Navigator fallback for earlier preview builds', async () => {
		vi.stubGlobal('document', {});
		const registerTool = vi.fn(async () => {});
		vi.stubGlobal('navigator', { modelContext: { registerTool } });

		const result = await registerVCPTools({ enableChat: false });

		expect(result.api).toBe('navigator');
		expect(result.registered).toEqual(['vcp_list_personas']);
	});

	it.each([
		['SSR', undefined, undefined],
		['unsupported document', {}, undefined],
		['incomplete API', { modelContext: {} }, undefined]
	])('returns an explicit unavailable result for %s', async (_name, documentValue, navigatorValue) => {
		if (documentValue !== undefined) vi.stubGlobal('document', documentValue);
		if (navigatorValue !== undefined) vi.stubGlobal('navigator', navigatorValue);

		const result = await registerVCPTools();

		expect(result).toMatchObject({ registered: [], failed: [], api: 'unavailable' });
		expect(() => result.cleanup()).not.toThrow();
	});
});
