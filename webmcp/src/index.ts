/**
 * @creed-space/vcp-sdk
 *
 * Register VCP capabilities as discoverable tools for AI agents through the
 * experimental WebMCP `document.modelContext` imperative API.
 *
 * Usage:
 *   import { registerVCPTools } from '@creed-space/vcp-sdk';
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
	WebMCPToolExecuteOptions,
	WebMCPToolResult,
	WebMCPToolAnnotations,
	WebMCPRegisterToolOptions,
	WebMCPRegistrationFailure,
	WebMCPModelContext
} from './types.js';

export { createVCPTools } from './tools.js';
export { registerVCPTools } from './registration.js';

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
	NormOrigin,
	TrendDirection,
	SelfModelScaffold,
	hasUncertaintyMarkers,
	getAllDimensions,
	createDefaultRelationalContext,
	SchulzeElection,
	TorchGenerator,
	TorchConsumer,
	createEmptyLineage,
	appendToLineage,
	VCPExtension,
	VCPCapability,
	negotiate,
	createFullHello,
} from './extensions/index.js';

export type {
	DimensionReport,
	AISelfModel,
	RelationalNorm,
	TorchState,
	RelationalContext,
	VCPHello,
	VCPCoreFeatures,
	VCPServerCapabilities,
	VCPAck,
	VCPError,
	VCPNegotiationResult,
} from './extensions/index.js';

export {
	LocalAgentRuntime,
	matchAgentResult,
	parseAgentArtifact,
	parseAgentRuntimeDocument,
} from './agent.js';

export type {
	AccretionCandidate,
	ActionIntent,
	AgentArtifact,
	AgentRuntimeDocument,
	AgentRuntimeProfileAcknowledgement,
	AgentRuntimeProfileOffer,
	AgentFailure,
	AgentProfile,
	AgentResult,
	AgentResultStatus,
	EffectClass as AgentEffectClass,
	ExecutionReceipt,
	PromotionRecord,
	ResourceBudget as AgentResourceBudget,
	SituationView as AgentSituationView,
} from './agent.js';
