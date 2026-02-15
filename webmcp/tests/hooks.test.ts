import { describe, it, expect, vi } from 'vitest';
import {
	HookRegistry,
	HookType,
	type HookDefinition,
	type HookInput,
	type HookResult,
	type HookEvent,
} from '../src/hooks.js';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Build a minimal valid HookInput for testing. */
function makeInput(overrides: Partial<HookInput> = {}): HookInput {
	return {
		context: { dimensions: {} },
		constitution: { id: 'general' },
		event: {},
		session: {},
		chainState: {},
		...overrides,
	};
}

/** Build a minimal valid HookDefinition for testing. */
function makeHook(overrides: Partial<HookDefinition> = {}): HookDefinition {
	return {
		name: 'test-hook',
		type: HookType.PreInject,
		priority: 50,
		timeoutMs: 5000,
		handler: () => ({ status: 'continue' }),
		...overrides,
	};
}

// ---------------------------------------------------------------------------
// Registration Tests
// ---------------------------------------------------------------------------

describe('HookRegistry — registration', () => {
	it('registers a valid hook successfully', () => {
		const registry = new HookRegistry();
		const hook = makeHook({ name: 'valid-hook' });

		registry.register(hook);

		const chain = registry.getChain(HookType.PreInject);
		expect(chain).toHaveLength(1);
		expect(chain[0].name).toBe('valid-hook');
	});

	it('rejects invalid hook name with spaces', () => {
		const registry = new HookRegistry();
		const hook = makeHook({ name: 'invalid hook' });

		expect(() => registry.register(hook)).toThrow(/Invalid hook name/);
	});

	it('rejects invalid hook name with uppercase', () => {
		const registry = new HookRegistry();
		const hook = makeHook({ name: 'InvalidHook' });

		expect(() => registry.register(hook)).toThrow(/Invalid hook name/);
	});

	it('rejects hook name longer than 64 characters', () => {
		const registry = new HookRegistry();
		const longName = 'a'.repeat(65);
		const hook = makeHook({ name: longName });

		expect(() => registry.register(hook)).toThrow(/Invalid hook name/);
	});

	it('rejects empty hook name', () => {
		const registry = new HookRegistry();
		const hook = makeHook({ name: '' });

		expect(() => registry.register(hook)).toThrow(/Invalid hook name/);
	});

	it('rejects priority greater than 100', () => {
		const registry = new HookRegistry();
		const hook = makeHook({ name: 'hi-pri', priority: 101 });

		expect(() => registry.register(hook)).toThrow(/Invalid priority/);
	});

	it('rejects priority less than 0', () => {
		const registry = new HookRegistry();
		const hook = makeHook({ name: 'neg-pri', priority: -1 });

		expect(() => registry.register(hook)).toThrow(/Invalid priority/);
	});

	it('rejects non-integer priority', () => {
		const registry = new HookRegistry();
		const hook = makeHook({ name: 'float-pri', priority: 50.5 });

		expect(() => registry.register(hook)).toThrow(/Invalid priority/);
	});

	it('rejects timeoutMs greater than 30000', () => {
		const registry = new HookRegistry();
		const hook = makeHook({ name: 'big-timeout', timeoutMs: 30001 });

		expect(() => registry.register(hook)).toThrow(/Invalid timeoutMs/);
	});

	it('rejects timeoutMs less than 1', () => {
		const registry = new HookRegistry();
		const hook = makeHook({ name: 'zero-timeout', timeoutMs: 0 });

		expect(() => registry.register(hook)).toThrow(/Invalid timeoutMs/);
	});

	it('rejects duplicate hook names', () => {
		const registry = new HookRegistry();
		registry.register(makeHook({ name: 'unique-hook' }));

		expect(() =>
			registry.register(makeHook({ name: 'unique-hook' }))
		).toThrow(/Duplicate hook name/);
	});

	it('rejects duplicate hook names across different types', () => {
		const registry = new HookRegistry();
		registry.register(
			makeHook({ name: 'cross-type', type: HookType.PreInject })
		);

		expect(() =>
			registry.register(
				makeHook({ name: 'cross-type', type: HookType.PostSelect })
			)
		).toThrow(/Duplicate hook name/);
	});
});

// ---------------------------------------------------------------------------
// Deregistration Tests
// ---------------------------------------------------------------------------

describe('HookRegistry — deregistration', () => {
	it('unregister returns true for existing hook', () => {
		const registry = new HookRegistry();
		registry.register(makeHook({ name: 'removable' }));

		expect(registry.unregister('removable')).toBe(true);
		expect(registry.getChain(HookType.PreInject)).toHaveLength(0);
	});

	it('unregister returns false for nonexistent hook', () => {
		const registry = new HookRegistry();

		expect(registry.unregister('does-not-exist')).toBe(false);
	});
});

// ---------------------------------------------------------------------------
// Chain Execution Tests
// ---------------------------------------------------------------------------

describe('HookRegistry — fire', () => {
	it('fire with empty chain returns completed', () => {
		const registry = new HookRegistry();
		const result = registry.fire(HookType.PreInject, makeInput());

		expect(result.completed).toBe(true);
		expect(result.results).toHaveLength(0);
		expect(result.abortedBy).toBeUndefined();
	});

	it('continue status passes through unchanged', () => {
		const registry = new HookRegistry();
		const handler = vi.fn((): HookResult => ({ status: 'continue' }));

		registry.register(makeHook({ name: 'pass-through', handler }));

		const input = makeInput({
			context: { original: true },
			constitution: { id: 'test' },
		});
		const result = registry.fire(HookType.PreInject, input);

		expect(result.completed).toBe(true);
		expect(result.modifiedContext).toEqual({ original: true });
		expect(result.modifiedConstitution).toEqual({ id: 'test' });
		expect(handler).toHaveBeenCalledOnce();
	});

	it('abort halts chain early', () => {
		const registry = new HookRegistry();
		const secondHandler = vi.fn((): HookResult => ({ status: 'continue' }));

		registry.register(
			makeHook({
				name: 'aborter',
				priority: 90,
				handler: () => ({
					status: 'abort',
					reason: 'PII detected',
				}),
			})
		);
		registry.register(
			makeHook({
				name: 'after-abort',
				priority: 10,
				handler: secondHandler,
			})
		);

		const result = registry.fire(HookType.PreInject, makeInput());

		expect(result.completed).toBe(false);
		expect(result.abortedBy).toBe('aborter');
		expect(result.abortReason).toBe('PII detected');
		// Second hook should never be called
		expect(secondHandler).not.toHaveBeenCalled();
		expect(result.results).toHaveLength(1);
	});

	it('modify passes modified data to next hook', () => {
		const registry = new HookRegistry();

		registry.register(
			makeHook({
				name: 'modifier',
				priority: 90,
				handler: () => ({
					status: 'modify',
					modifiedContext: { transformed: true },
					modifiedConstitution: { id: 'strict' },
				}),
			})
		);

		registry.register(
			makeHook({
				name: 'verifier',
				priority: 10,
				handler: (input: HookInput): HookResult => {
					// Should receive the modified data from the first hook
					expect(input.context).toEqual({ transformed: true });
					expect(input.constitution).toEqual({ id: 'strict' });
					return { status: 'continue' };
				},
			})
		);

		const result = registry.fire(HookType.PreInject, makeInput());

		expect(result.completed).toBe(true);
		expect(result.modifiedContext).toEqual({ transformed: true });
		expect(result.modifiedConstitution).toEqual({ id: 'strict' });
		expect(result.results).toHaveLength(2);
	});

	it('priority ordering: higher priority runs first', () => {
		const registry = new HookRegistry();
		const order: string[] = [];

		registry.register(
			makeHook({
				name: 'low',
				priority: 10,
				handler: () => {
					order.push('low');
					return { status: 'continue' };
				},
			})
		);

		registry.register(
			makeHook({
				name: 'high',
				priority: 90,
				handler: () => {
					order.push('high');
					return { status: 'continue' };
				},
			})
		);

		registry.register(
			makeHook({
				name: 'mid',
				priority: 50,
				handler: () => {
					order.push('mid');
					return { status: 'continue' };
				},
			})
		);

		registry.fire(HookType.PreInject, makeInput());

		expect(order).toEqual(['high', 'mid', 'low']);
	});

	it('disabled hooks are skipped', () => {
		const registry = new HookRegistry();
		const handler = vi.fn((): HookResult => ({ status: 'continue' }));

		registry.register(
			makeHook({
				name: 'disabled-hook',
				enabled: false,
				handler,
			})
		);

		const result = registry.fire(HookType.PreInject, makeInput());

		expect(result.completed).toBe(true);
		expect(handler).not.toHaveBeenCalled();
		// The disabled hook should not appear in results
		expect(result.results).toHaveLength(0);
	});

	it('exception in handler causes chain to continue', () => {
		const registry = new HookRegistry();
		const afterHandler = vi.fn((): HookResult => ({ status: 'continue' }));

		registry.register(
			makeHook({
				name: 'crasher',
				priority: 90,
				handler: () => {
					throw new Error('handler exploded');
				},
			})
		);

		registry.register(
			makeHook({
				name: 'survivor',
				priority: 10,
				handler: afterHandler,
			})
		);

		const result = registry.fire(HookType.PreInject, makeInput());

		expect(result.completed).toBe(true);
		// Chain should have continued past the exception
		expect(afterHandler).toHaveBeenCalledOnce();
		// Both hooks should have results
		expect(result.results).toHaveLength(2);
		// The crashing hook should have produced a continue result
		expect(result.results[0].result.status).toBe('continue');
	});

	it('durationMs is set on hook results', () => {
		const registry = new HookRegistry();

		registry.register(
			makeHook({
				name: 'timed',
				handler: () => ({ status: 'continue' }),
			})
		);

		const result = registry.fire(HookType.PreInject, makeInput());

		expect(result.results[0].result.durationMs).toBeTypeOf('number');
		expect(result.results[0].result.durationMs).toBeGreaterThanOrEqual(0);
	});
});

// ---------------------------------------------------------------------------
// Lifecycle Event Tests
// ---------------------------------------------------------------------------

describe('HookRegistry — lifecycle events', () => {
	it('event listener receives registered event', () => {
		const registry = new HookRegistry();
		const events: HookEvent[] = [];
		registry.addEventListener((event) => events.push(event));

		registry.register(makeHook({ name: 'observed-hook' }));

		const registeredEvents = events.filter((e) => e.type === 'registered');
		expect(registeredEvents).toHaveLength(1);
		expect(registeredEvents[0].hookName).toBe('observed-hook');
		expect(registeredEvents[0].timestamp).toBeTypeOf('number');
	});

	it('event listener receives fired and completed events', () => {
		const registry = new HookRegistry();
		const events: HookEvent[] = [];
		registry.addEventListener((event) => events.push(event));

		registry.register(makeHook({ name: 'event-hook' }));
		registry.fire(HookType.PreInject, makeInput());

		const firedEvents = events.filter((e) => e.type === 'fired');
		const completedEvents = events.filter((e) => e.type === 'completed');
		expect(firedEvents).toHaveLength(1);
		expect(firedEvents[0].hookName).toBe('event-hook');
		expect(completedEvents).toHaveLength(1);
		expect(completedEvents[0].hookName).toBe('event-hook');
	});

	it('event listener receives error event on handler exception', () => {
		const registry = new HookRegistry();
		const events: HookEvent[] = [];
		registry.addEventListener((event) => events.push(event));

		registry.register(
			makeHook({
				name: 'err-hook',
				handler: () => {
					throw new Error('boom');
				},
			})
		);
		registry.fire(HookType.PreInject, makeInput());

		const errorEvents = events.filter((e) => e.type === 'error');
		expect(errorEvents).toHaveLength(1);
		expect(errorEvents[0].hookName).toBe('err-hook');
		expect(errorEvents[0].details?.error).toBe('boom');
	});

	it('event listener receives skipped event for disabled hooks', () => {
		const registry = new HookRegistry();
		const events: HookEvent[] = [];
		registry.addEventListener((event) => events.push(event));

		registry.register(makeHook({ name: 'skip-hook', enabled: false }));
		registry.fire(HookType.PreInject, makeInput());

		const skippedEvents = events.filter((e) => e.type === 'skipped');
		expect(skippedEvents).toHaveLength(1);
		expect(skippedEvents[0].hookName).toBe('skip-hook');
		expect(skippedEvents[0].details?.reason).toBe('disabled');
	});

	it('event listener receives deregistered event', () => {
		const registry = new HookRegistry();
		const events: HookEvent[] = [];
		registry.addEventListener((event) => events.push(event));

		registry.register(makeHook({ name: 'bye-hook' }));
		registry.unregister('bye-hook');

		const deregisteredEvents = events.filter(
			(e) => e.type === 'deregistered'
		);
		expect(deregisteredEvents).toHaveLength(1);
		expect(deregisteredEvents[0].hookName).toBe('bye-hook');
	});

	it('removeEventListener stops future notifications', () => {
		const registry = new HookRegistry();
		const events: HookEvent[] = [];
		const listener = (event: HookEvent) => events.push(event);

		registry.addEventListener(listener);
		registry.register(makeHook({ name: 'first-hook' }));
		expect(events).toHaveLength(1);

		registry.removeEventListener(listener);
		registry.register(
			makeHook({ name: 'second-hook', type: HookType.PostSelect })
		);
		// Should still be 1 — no new events after removal
		expect(events).toHaveLength(1);
	});
});

// ---------------------------------------------------------------------------
// Chain State Tests
// ---------------------------------------------------------------------------

describe('HookRegistry — chain state', () => {
	it('hooks can communicate via chainState', () => {
		const registry = new HookRegistry();

		registry.register(
			makeHook({
				name: 'writer',
				priority: 90,
				handler: (input: HookInput): HookResult => {
					input.chainState['checked'] = true;
					return { status: 'continue' };
				},
			})
		);

		registry.register(
			makeHook({
				name: 'reader',
				priority: 10,
				handler: (input: HookInput): HookResult => {
					expect(input.chainState['checked']).toBe(true);
					return { status: 'continue' };
				},
			})
		);

		const result = registry.fire(HookType.PreInject, makeInput());
		expect(result.completed).toBe(true);
	});
});

// ---------------------------------------------------------------------------
// Edge Cases
// ---------------------------------------------------------------------------

describe('HookRegistry — edge cases', () => {
	it('accepts hook names at boundary (1 char and 64 chars)', () => {
		const registry = new HookRegistry();

		registry.register(makeHook({ name: 'a' }));
		registry.register(
			makeHook({
				name: 'a'.repeat(64),
				type: HookType.PostSelect,
			})
		);

		expect(registry.getChain(HookType.PreInject)).toHaveLength(1);
		expect(registry.getChain(HookType.PostSelect)).toHaveLength(1);
	});

	it('accepts priority at boundaries (0 and 100)', () => {
		const registry = new HookRegistry();

		registry.register(makeHook({ name: 'zero-pri', priority: 0 }));
		registry.register(
			makeHook({ name: 'max-pri', priority: 100 })
		);

		const chain = registry.getChain(HookType.PreInject);
		expect(chain).toHaveLength(2);
		expect(chain[0].name).toBe('max-pri');
		expect(chain[1].name).toBe('zero-pri');
	});

	it('accepts timeoutMs at boundaries (1 and 30000)', () => {
		const registry = new HookRegistry();

		registry.register(makeHook({ name: 'min-timeout', timeoutMs: 1 }));
		registry.register(
			makeHook({
				name: 'max-timeout',
				timeoutMs: 30000,
				type: HookType.PostSelect,
			})
		);

		expect(registry.getChain(HookType.PreInject)).toHaveLength(1);
		expect(registry.getChain(HookType.PostSelect)).toHaveLength(1);
	});

	it('equal priority hooks maintain registration order', () => {
		const registry = new HookRegistry();
		const order: string[] = [];

		registry.register(
			makeHook({
				name: 'first',
				priority: 50,
				handler: () => {
					order.push('first');
					return { status: 'continue' };
				},
			})
		);

		registry.register(
			makeHook({
				name: 'second',
				priority: 50,
				handler: () => {
					order.push('second');
					return { status: 'continue' };
				},
			})
		);

		registry.fire(HookType.PreInject, makeInput());

		expect(order).toEqual(['first', 'second']);
	});

	it('works with all six hook types', () => {
		const registry = new HookRegistry();
		const types = Object.values(HookType);

		for (const [idx, type] of types.entries()) {
			registry.register(
				makeHook({
					name: `hook-${idx}`,
					type: type as HookType,
				})
			);
		}

		for (const type of types) {
			const chain = registry.getChain(type as HookType);
			expect(chain).toHaveLength(1);

			const result = registry.fire(type as HookType, makeInput());
			expect(result.completed).toBe(true);
		}
	});
});
