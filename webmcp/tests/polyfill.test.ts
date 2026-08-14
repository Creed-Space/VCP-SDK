import { afterEach, describe, expect, it, vi } from 'vitest';

afterEach(() => {
	Reflect.deleteProperty(globalThis, 'window');
	Reflect.deleteProperty(globalThis, 'document');
	Reflect.deleteProperty(globalThis, 'navigator');
	vi.restoreAllMocks();
	vi.resetModules();
});

function setWindow(search: string): void {
	Object.defineProperty(globalThis, 'window', {
		configurable: true,
		value: { location: { search } },
	});
}

describe('application-owned polyfill loading', () => {
	it('does nothing during server-side rendering', async () => {
		const { loadPolyfillIfRequested } = await import('../src/polyfill.js');
		expect(await loadPolyfillIfRequested({ loader: vi.fn() })).toBe(false);
	});

	it('does nothing when the query parameter is absent', async () => {
		setWindow('');
		const loader = vi.fn(async () => undefined);
		const { loadPolyfillIfRequested } = await import('../src/polyfill.js');
		expect(await loadPolyfillIfRequested({ loader })).toBe(false);
		expect(loader).not.toHaveBeenCalled();
	});

	it('requires an explicit caller-owned loader without logging', async () => {
		setWindow('?webmcp=polyfill');
		const { loadPolyfillIfRequested } = await import('../src/polyfill.js');
		expect(await loadPolyfillIfRequested()).toBe(false);
	});

	it('coalesces concurrent calls and loads once', async () => {
		setWindow('?webmcp=polyfill');
		const loader = vi.fn(async () => {
			Object.defineProperty(globalThis, 'document', {
				configurable: true,
				value: { modelContext: { registerTool: vi.fn(async () => undefined) } }
			});
		});
		const { loadPolyfillIfRequested } = await import('../src/polyfill.js');
		const results = await Promise.all([
			loadPolyfillIfRequested({ loader }),
			loadPolyfillIfRequested({ loader }),
		]);
		expect(results).toEqual([true, true]);
		expect(loader).toHaveBeenCalledTimes(1);
	});

	it('allows a retry after a failed loader', async () => {
		setWindow('?webmcp=polyfill');
		const first = vi.fn(async () => {
			throw new Error('blocked');
		});
		const second = vi.fn(async () => {
			Object.defineProperty(globalThis, 'document', {
				configurable: true,
				value: { modelContext: { registerTool: vi.fn(async () => undefined) } }
			});
		});
		const { loadPolyfillIfRequested } = await import('../src/polyfill.js');
		const errors: Error[] = [];
		expect(
			await loadPolyfillIfRequested({ loader: first, onError: (error) => errors.push(error) })
		).toBe(false);
		expect(errors[0].message).toBe('blocked');
		expect(await loadPolyfillIfRequested({ loader: second })).toBe(true);
	});

	it('rejects a loader that does not expose the WebMCP contract', async () => {
		setWindow('?webmcp=polyfill');
		const errors: Error[] = [];
		const { loadPolyfillIfRequested } = await import('../src/polyfill.js');
		expect(
			await loadPolyfillIfRequested({
				loader: async () => undefined,
				onError: (error) => errors.push(error)
			})
		).toBe(false);
		expect(errors[0].message).toContain('document.modelContext');
	});

	it('accepts the isolated legacy Navigator contract', async () => {
		setWindow('?webmcp=polyfill');
		Object.defineProperty(globalThis, 'navigator', {
			configurable: true,
			value: { modelContext: { registerTool: vi.fn(async () => undefined) } }
		});
		const loader = vi.fn(async () => undefined);
		const { loadPolyfillIfRequested } = await import('../src/polyfill.js');
		expect(await loadPolyfillIfRequested({ loader })).toBe(true);
		expect(loader).not.toHaveBeenCalled();
	});
});
