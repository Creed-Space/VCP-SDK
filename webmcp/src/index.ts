/**
 * @vcp/webmcp
 *
 * Register VCP capabilities as discoverable tools for AI agents via
 * the navigator.modelContext API (Chrome 145+, W3C Draft 2026-02-10).
 *
 * Usage:
 *   import { registerVCPTools } from '@vcp/webmcp';
 *   const { registered, cleanup } = await registerVCPTools({
 *     chatEndpoint: '/api/chat',
 *     tokenEncoder: encodeContextToCSM1,
 *     tokenParser: parseCSM1Token,
 *     transmissionSummary: getTransmissionSummary,
 *   });
 *
 * @packageDocumentation
 */

export type {
	VCPWebMCPConfig,
	VCPWebMCPResult,
	PersonaInfo,
	TransmissionSummary,
	WebMCPToolDefinition,
	WebMCPToolResult,
	WebMCPToolRegistration,
	WebMCPModelContext
} from './types.js';

export { createVCPTools } from './tools.js';

export {
	HookRegistry,
	HookType,
} from './hooks.js';

export type {
	ResultStatus,
	HookInput,
	HookResult,
	HookHandler,
	HookDefinition,
	ChainHookResult,
	ChainResult,
	HookEvent,
	HookEventListener,
} from './hooks.js';

// VCP v3.1 Extensions
export {
	PersonalDimension,
	computeDecayedIntensity,
	computeLifecycleState,
	TrustLevel,
	StandingLevel,
	SelfModelScaffold,
	createDefaultRelationalContext,
	SchulzeElection,
	TorchGenerator,
	TorchConsumer,
	createEmptyLineage,
	appendToLineage,
	VCPCapability,
	negotiate,
	createFullHello,
} from './extensions/index.js';

import type { VCPWebMCPConfig, VCPWebMCPResult, WebMCPToolRegistration } from './types.js';
import { createVCPTools } from './tools.js';

const EMPTY_RESULT: VCPWebMCPResult = {
	registered: [],
	cleanup: () => {}
};

/**
 * Register VCP tools with navigator.modelContext.
 *
 * Safe to call during SSR (returns immediately) and in browsers without
 * WebMCP support (returns empty result, no errors logged).
 *
 * @param config - Optional configuration for tool selection and dependencies
 * @returns Promise resolving to registered tool names and a cleanup function
 */
export async function registerVCPTools(
	config: VCPWebMCPConfig = {}
): Promise<VCPWebMCPResult> {
	// SSR guard
	if (typeof window === 'undefined') return EMPTY_RESULT;

	// Feature detection
	if (!navigator.modelContext?.registerTool) return EMPTY_RESULT;

	const tools = createVCPTools(config);
	const registrations: WebMCPToolRegistration[] = [];
	const registered: string[] = [];

	for (const tool of tools) {
		try {
			const reg = navigator.modelContext.registerTool(tool);
			registrations.push(reg);
			registered.push(tool.name);
		} catch (err) {
			console.warn(`[@vcp/webmcp] Failed to register ${tool.name}:`, err);
		}
	}

	if (registered.length > 0) {
		console.log(
			`[@vcp/webmcp] Registered ${registered.length} tools: ${registered.join(', ')}`
		);
	}

	return {
		registered,
		cleanup() {
			for (const reg of registrations) {
				try {
					reg.unregister();
				} catch {
					// already unregistered or browser cleaned up
				}
			}
		}
	};
}
