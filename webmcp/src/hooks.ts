/**
 * @vcp/webmcp — VCP Hook System
 *
 * Lightweight browser-side implementation of the VCP Hook System
 * (VCP/A Layer 4) for intercepting and modifying the constitutional
 * adaptation pipeline.
 *
 * Provides a deterministic, priority-ordered hook registry and executor.
 * All execution is synchronous — designed for browser contexts where
 * hooks must complete within the same call frame.
 *
 * @see VCP_HOOKS.md specification for full semantics
 * @packageDocumentation
 */

// ---------------------------------------------------------------------------
// Enums & Literal Types
// ---------------------------------------------------------------------------

/** The six VCP hook types, each corresponding to a pipeline interception point. */
export enum HookType {
	/** Before a constitution is injected into LLM context. */
	PreInject = 'pre_inject',
	/** After the adaptation layer has selected a constitution. */
	PostSelect = 'post_select',
	/** A state machine transition in the context tracker. */
	OnTransition = 'on_transition',
	/** A conflict is detected during constitution composition. */
	OnConflict = 'on_conflict',
	/** A rule violation is detected in LLM output. */
	OnViolation = 'on_violation',
	/** A timer fires at a configured interval. */
	Periodic = 'periodic',
}

/** Result status controlling pipeline flow after a hook executes. */
export type ResultStatus = 'continue' | 'abort' | 'modify';

// ---------------------------------------------------------------------------
// Hook I/O Interfaces
// ---------------------------------------------------------------------------

/** Input provided to hook handlers during chain execution. */
export interface HookInput {
	/** The current VCP context object. */
	readonly context: unknown;
	/** The active or candidate constitution. */
	readonly constitution: unknown;
	/** Type-specific event payload. */
	readonly event: unknown;
	/** Session metadata (id, scope, timestamps). */
	readonly session: Record<string, unknown>;
	/** Mutable state passed along the hook chain. Reset per chain execution. */
	readonly chainState: Record<string, unknown>;
}

/** Structured result returned by a hook handler. */
export interface HookResult {
	/** Controls pipeline flow: continue, abort, or modify. */
	readonly status: ResultStatus;
	/** Replacement context when status is 'modify'. */
	readonly modifiedContext?: unknown;
	/** Replacement constitution when status is 'modify'. */
	readonly modifiedConstitution?: unknown;
	/** Human-readable justification. Required when status is 'abort'. */
	readonly reason?: string;
	/** Arbitrary metadata attached to the pipeline event for audit. */
	readonly annotations?: Record<string, unknown>;
	/** Actual execution time in milliseconds. Set by the runtime. */
	durationMs?: number;
}

// ---------------------------------------------------------------------------
// Hook Definition
// ---------------------------------------------------------------------------

/** Synchronous hook handler function signature. */
export type HookHandler = (input: HookInput) => HookResult;

/**
 * A registered hook definition.
 *
 * Defines the hook's identity, type, priority, handler, timeout,
 * and optional metadata. Validated at registration time.
 */
export interface HookDefinition {
	/** Unique name within the registry. Pattern: [a-z0-9_-]{1,64} */
	readonly name: string;
	/** Which pipeline interception point this hook targets. */
	readonly type: HookType;
	/** Execution priority. 0-100 inclusive; higher runs first. */
	readonly priority: number;
	/** The function to execute when the hook fires. */
	readonly handler: HookHandler;
	/** Maximum execution time in milliseconds. Range: 1-30000. */
	readonly timeoutMs: number;
	/** Whether the hook is active. Disabled hooks are skipped. Defaults to true. */
	readonly enabled?: boolean;
	/** Human-readable purpose description. */
	readonly description?: string;
	/** Arbitrary key-value pairs for tooling. */
	readonly metadata?: Record<string, unknown>;
}

// ---------------------------------------------------------------------------
// Chain Result
// ---------------------------------------------------------------------------

/** Individual hook execution result within a chain. */
export interface ChainHookResult {
	/** Name of the hook that produced this result. */
	readonly hookName: string;
	/** The result returned by the hook handler. */
	readonly result: HookResult;
}

/** Result of executing a complete hook chain. */
export interface ChainResult {
	/** Whether the chain ran to completion without an abort. */
	readonly completed: boolean;
	/** Name of the hook that aborted the chain, if any. */
	readonly abortedBy?: string;
	/** Human-readable reason for the abort, if any. */
	readonly abortReason?: string;
	/** Final (possibly modified) context after chain execution. */
	readonly modifiedContext?: unknown;
	/** Final (possibly modified) constitution after chain execution. */
	readonly modifiedConstitution?: unknown;
	/** Ordered list of individual hook results. */
	readonly results: readonly ChainHookResult[];
}

// ---------------------------------------------------------------------------
// Lifecycle Events
// ---------------------------------------------------------------------------

/** Lifecycle event emitted by the registry during hook operations. */
export interface HookEvent {
	/** Type of lifecycle event. */
	readonly type:
		| 'registered'
		| 'deregistered'
		| 'fired'
		| 'completed'
		| 'timeout'
		| 'error'
		| 'skipped';
	/** Name of the hook involved. */
	readonly hookName: string;
	/** Unix timestamp (ms) when the event occurred. */
	readonly timestamp: number;
	/** Additional event-specific details. */
	readonly details?: Record<string, unknown>;
}

/** Listener callback for hook lifecycle events. */
export type HookEventListener = (event: HookEvent) => void;

// ---------------------------------------------------------------------------
// Validation
// ---------------------------------------------------------------------------

/** Name pattern: lowercase alphanumeric, hyphens, underscores. 1-64 chars. */
const HOOK_NAME_PATTERN = /^[a-z0-9_-]{1,64}$/;

/** Set of valid HookType values for runtime validation. */
const VALID_HOOK_TYPES = new Set<string>(Object.values(HookType));

/**
 * Validate a hook definition. Throws a descriptive Error on failure.
 *
 * @param hook - The hook definition to validate
 * @throws Error if any validation check fails
 */
function validateHookDefinition(hook: HookDefinition): void {
	if (!HOOK_NAME_PATTERN.test(hook.name)) {
		throw new Error(
			`Invalid hook name: '${hook.name}'. ` +
				`Must match [a-z0-9_-]{1,64}.`
		);
	}

	if (!VALID_HOOK_TYPES.has(hook.type)) {
		throw new Error(
			`Invalid hook type: '${hook.type}'. ` +
				`Must be one of: ${[...VALID_HOOK_TYPES].join(', ')}.`
		);
	}

	if (
		!Number.isInteger(hook.priority) ||
		hook.priority < 0 ||
		hook.priority > 100
	) {
		throw new Error(
			`Invalid priority: ${hook.priority}. Must be an integer in [0, 100].`
		);
	}

	if (
		!Number.isInteger(hook.timeoutMs) ||
		hook.timeoutMs < 1 ||
		hook.timeoutMs > 30000
	) {
		throw new Error(
			`Invalid timeoutMs: ${hook.timeoutMs}. Must be an integer in [1, 30000].`
		);
	}

	if (typeof hook.handler !== 'function') {
		throw new Error('Hook handler must be a function.');
	}
}

// ---------------------------------------------------------------------------
// HookRegistry
// ---------------------------------------------------------------------------

/**
 * Central hook registry and executor.
 *
 * Manages hook registration, chain assembly, and deterministic execution.
 * Designed for browser-side use -- all chain execution is synchronous.
 *
 * @example
 * ```ts
 * const registry = new HookRegistry();
 *
 * registry.register({
 *   name: 'audit-selection',
 *   type: HookType.PostSelect,
 *   priority: 50,
 *   timeoutMs: 2000,
 *   handler: (input) => {
 *     console.log('Selected:', input.constitution);
 *     return { status: 'continue' };
 *   },
 * });
 *
 * const result = registry.fire(HookType.PostSelect, {
 *   context: { dimensions: {} },
 *   constitution: { id: 'general' },
 *   event: {},
 *   session: {},
 *   chainState: {},
 * });
 * ```
 */
export class HookRegistry {
	private readonly hooks: Map<HookType, HookDefinition[]> = new Map();
	private readonly listeners: HookEventListener[] = [];

	constructor() {
		for (const type of Object.values(HookType)) {
			this.hooks.set(type as HookType, []);
		}
	}

	/**
	 * Register a hook. Throws on invalid definition or duplicate name.
	 *
	 * @param hook - The hook definition to register
	 * @throws Error if validation fails or name is already registered
	 */
	register(hook: HookDefinition): void {
		validateHookDefinition(hook);

		// Check for duplicate name across ALL hook types
		for (const chain of this.hooks.values()) {
			if (chain.some((h) => h.name === hook.name)) {
				throw new Error(
					`Duplicate hook name: '${hook.name}'. Names must be unique across all types.`
				);
			}
		}

		const chain = this.hooks.get(hook.type);
		if (!chain) {
			throw new Error(`No chain found for hook type: '${hook.type}'.`);
		}

		// Insert maintaining descending priority order.
		// Equal priority: earlier registration comes first (append after existing same-priority hooks).
		let insertIdx = chain.length;
		for (let i = 0; i < chain.length; i++) {
			if (chain[i].priority < hook.priority) {
				insertIdx = i;
				break;
			}
		}
		chain.splice(insertIdx, 0, hook);

		this.emit({
			type: 'registered',
			hookName: hook.name,
			timestamp: Date.now(),
			details: { hookType: hook.type, priority: hook.priority },
		});
	}

	/**
	 * Remove a hook by name.
	 *
	 * @param name - The unique name of the hook to remove
	 * @returns true if the hook was found and removed, false otherwise
	 */
	unregister(name: string): boolean {
		for (const [type, chain] of this.hooks.entries()) {
			const idx = chain.findIndex((h) => h.name === name);
			if (idx !== -1) {
				chain.splice(idx, 1);
				this.emit({
					type: 'deregistered',
					hookName: name,
					timestamp: Date.now(),
					details: { hookType: type },
				});
				return true;
			}
		}
		return false;
	}

	/**
	 * Get the ordered chain for a hook type.
	 * Returns hooks sorted by priority descending (higher runs first).
	 *
	 * @param type - The hook type to retrieve the chain for
	 * @returns Readonly array of hook definitions in execution order
	 */
	getChain(type: HookType): readonly HookDefinition[] {
		return this.hooks.get(type) ?? [];
	}

	/**
	 * Execute the hook chain for a given type.
	 *
	 * Hooks execute sequentially in priority order (descending).
	 * - `continue`: pass through unchanged
	 * - `abort`: halt chain, return aborted result
	 * - `modify`: pass modified context/constitution to next hook
	 *
	 * Disabled hooks are skipped. Exceptions in handlers are caught
	 * and treated as `continue` (fail-open). Timeouts are enforced
	 * via Date.now() comparison.
	 *
	 * @param type - The hook type to fire
	 * @param input - The input payload for hook handlers
	 * @returns The chain execution result
	 */
	fire(type: HookType, input: HookInput): ChainResult {
		const chain = this.hooks.get(type) ?? [];
		const results: ChainHookResult[] = [];

		let currentContext = input.context;
		let currentConstitution = input.constitution;
		const chainState: Record<string, unknown> = { ...input.chainState };

		for (const hook of chain) {
			// Skip disabled hooks
			if (hook.enabled === false) {
				this.emit({
					type: 'skipped',
					hookName: hook.name,
					timestamp: Date.now(),
					details: { reason: 'disabled' },
				});
				continue;
			}

			const hookInput: HookInput = {
				context: currentContext,
				constitution: currentConstitution,
				event: input.event,
				session: input.session,
				chainState,
			};

			this.emit({
				type: 'fired',
				hookName: hook.name,
				timestamp: Date.now(),
			});

			const startTime = Date.now();
			let result: HookResult;

			try {
				result = hook.handler(hookInput);

				// Timeout check: since handlers are synchronous, we check
				// elapsed time after return. A truly blocking handler that
				// exceeds timeoutMs is detected here.
				const elapsed = Date.now() - startTime;
				if (elapsed > hook.timeoutMs) {
					this.emit({
						type: 'timeout',
						hookName: hook.name,
						timestamp: Date.now(),
						details: {
							timeoutMs: hook.timeoutMs,
							elapsedMs: elapsed,
						},
					});
					// Per spec: timed-out hook treated as { status: "continue" }
					result = { status: 'continue' };
				}
			} catch (err) {
				const elapsed = Date.now() - startTime;
				this.emit({
					type: 'error',
					hookName: hook.name,
					timestamp: Date.now(),
					details: {
						error:
							err instanceof Error ? err.message : String(err),
						elapsedMs: elapsed,
					},
				});
				// Per spec: exceptions treated as { status: "continue" }
				result = { status: 'continue' };
			}

			const durationMs = Date.now() - startTime;
			result = { ...result, durationMs };

			results.push({ hookName: hook.name, result });

			this.emit({
				type: 'completed',
				hookName: hook.name,
				timestamp: Date.now(),
				details: { status: result.status, durationMs },
			});

			// Process result status
			if (result.status === 'abort') {
				return {
					completed: false,
					abortedBy: hook.name,
					abortReason: result.reason,
					modifiedContext: currentContext,
					modifiedConstitution: currentConstitution,
					results,
				};
			}

			if (result.status === 'modify') {
				if (result.modifiedContext !== undefined) {
					currentContext = result.modifiedContext;
				}
				if (result.modifiedConstitution !== undefined) {
					currentConstitution = result.modifiedConstitution;
				}
			}
		}

		return {
			completed: true,
			modifiedContext: currentContext,
			modifiedConstitution: currentConstitution,
			results,
		};
	}

	/**
	 * Add a lifecycle event listener.
	 *
	 * @param listener - Callback invoked for each lifecycle event
	 */
	addEventListener(listener: HookEventListener): void {
		this.listeners.push(listener);
	}

	/**
	 * Remove a lifecycle event listener.
	 *
	 * @param listener - The previously added listener to remove
	 * @returns true if the listener was found and removed
	 */
	removeEventListener(listener: HookEventListener): boolean {
		const idx = this.listeners.indexOf(listener);
		if (idx !== -1) {
			this.listeners.splice(idx, 1);
			return true;
		}
		return false;
	}

	/**
	 * Emit a lifecycle event to all registered listeners.
	 * Listener exceptions are caught silently to prevent cascading failures.
	 */
	private emit(event: HookEvent): void {
		for (const listener of this.listeners) {
			try {
				listener(event);
			} catch {
				// Listener errors must not break the hook system
			}
		}
	}
}
