import { afterEach, describe, expect, it, vi } from 'vitest';

afterEach(() => {
	Reflect.deleteProperty(globalThis, 'window');
	Reflect.deleteProperty(globalThis, 'document');
	Reflect.deleteProperty(globalThis, 'navigator');
	vi.restoreAllMocks();
	vi.resetModules();
	vi.useRealTimers();
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

	it('rechecks a previously loaded contract and reloads after it disappears', async () => {
		setWindow('?webmcp=polyfill');
		const expose = () => {
			Object.defineProperty(globalThis, 'document', {
				configurable: true,
				value: { modelContext: { registerTool: vi.fn(async () => undefined) } },
			});
		};
		const first = vi.fn(async () => expose());
		const second = vi.fn(async () => expose());
		const { loadPolyfillIfRequested } = await import('../src/polyfill.js');

		expect(await loadPolyfillIfRequested({ loader: first })).toBe(true);
		Reflect.deleteProperty(globalThis, 'document');
		expect(await loadPolyfillIfRequested({ loader: second })).toBe(true);
		expect(first).toHaveBeenCalledOnce();
		expect(second).toHaveBeenCalledOnce();
	});

	it('does not deadlock when a loader synchronously re-enters the API', async () => {
		setWindow('?webmcp=polyfill');
		const module = await import('../src/polyfill.js');
		const nested: boolean[] = [];
		const loader = vi.fn(async () => {
			nested.push(await module.loadPolyfillIfRequested({ loader }));
			Object.defineProperty(globalThis, 'document', {
				configurable: true,
				value: { modelContext: { registerTool: vi.fn(async () => undefined) } },
			});
		});
		expect(await module.loadPolyfillIfRequested({ loader })).toBe(true);
		expect(nested).toEqual([false]);
		expect(loader).toHaveBeenCalledOnce();
	});

	it('times out a loader that never settles and permits a later retry', async () => {
		vi.useFakeTimers();
		setWindow('?webmcp=polyfill');
		const { loadPolyfillIfRequested } = await import('../src/polyfill.js');
		const errors: Error[] = [];
		const pending = loadPolyfillIfRequested({
			loader: async () => new Promise<void>(() => {}),
			timeoutMs: 10,
			onError: (error) => errors.push(error),
		});
		await vi.advanceTimersByTimeAsync(10);
		expect(await pending).toBe(false);
		expect(errors[0].message).toBe('Polyfill loader timed out after 10ms');

		const retry = loadPolyfillIfRequested({
			loader: async () => {
				Object.defineProperty(globalThis, 'document', {
					configurable: true,
					value: { modelContext: { registerTool: vi.fn(async () => undefined) } },
				});
			},
		});
		await vi.runAllTimersAsync();
		expect(await retry).toBe(true);
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

	it('isolates a throwing error sink and still permits retry', async () => {
		setWindow('?webmcp=polyfill');
		const { loadPolyfillIfRequested } = await import('../src/polyfill.js');
		expect(
			await loadPolyfillIfRequested({
				loader: async () => {
					throw new Error('blocked');
				},
				onError: () => {
					throw new Error('sink failed');
				},
			}),
		).toBe(false);
		expect(
			await loadPolyfillIfRequested({
				loader: async () => {
					Object.defineProperty(globalThis, 'document', {
						configurable: true,
						value: { modelContext: { registerTool: vi.fn(async () => undefined) } },
					});
				},
			}),
		).toBe(true);
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
