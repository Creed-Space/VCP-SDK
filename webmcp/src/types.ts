/**
 * @creed-space/vcp-sdk WebMCP type definitions.
 *
 * These structural types follow the current `document.modelContext` imperative
 * API. WebMCP remains experimental, so the separately checked upstream contract
 * is the authority for browser compatibility claims.
 *
 * @packageDocumentation
 */

// ---------------------------------------------------------------------------
// WebMCP Core Types (browser API surface)
// ---------------------------------------------------------------------------

export interface WebMCPToolResult {
	content: Array<{ type: 'text'; text: string }>;
}

export interface WebMCPToolAnnotations {
	readOnlyHint?: boolean;
	untrustedContentHint?: boolean;
}

export interface WebMCPToolDefinition {
	name: string;
	title?: string;
	description: string;
	inputSchema?: Record<string, unknown>;
	annotations?: WebMCPToolAnnotations;
	execute: (args: Record<string, unknown>) => Promise<WebMCPToolResult>;
}

export interface WebMCPRegisterToolOptions {
	/** Aborting the signal unregisters the tool. */
	signal?: AbortSignal;
	/** Secure origins allowed to discover and execute this tool. */
	exposedTo?: string[];
}

export interface WebMCPModelContext {
	registerTool(
		definition: WebMCPToolDefinition,
		options?: WebMCPRegisterToolOptions
	): Promise<void>;
}

// ---------------------------------------------------------------------------
// VCP SDK Configuration
// ---------------------------------------------------------------------------

export interface PersonaInfo {
	id: string;
	name: string;
	description: string;
	use: string;
}

export interface TransmissionSummary {
	transmitted: string[];
	withheld: string[];
	influencing: string[];
}

/**
 * Configuration for registerVCPTools().
 *
 * All options are optional — sensible defaults are provided.
 * Dependency injection via tokenEncoder/tokenParser/transmissionSummary
 * lets the caller wire in their own VCP token library.
 */
export interface VCPWebMCPConfig {
	/** Base URL for the chat API endpoint. Defaults to '/api/chat'. */
	chatEndpoint?: string;

	/** Custom persona list. Defaults to the 7 standard VCP personas. */
	personas?: PersonaInfo[];

	/** Enable/disable individual tools (all default to true). */
	enableChat?: boolean;
	enableTokenBuilder?: boolean;
	enableTokenParser?: boolean;
	enableSummary?: boolean;
	enablePersonas?: boolean;

	/**
	 * Encode a VCP context object into a CSM-1 token string.
	 * Required for vcp_build_token tool. If not provided, tool is skipped.
	 */
	tokenEncoder?: (context: Record<string, unknown>) => string;

	/**
	 * Parse a CSM-1 token string into structured data (JS fallback).
	 * Required for vcp_parse_token tool. If not provided, tool is skipped.
	 */
	tokenParser?: (token: string) => unknown;

	/**
	 * Optional WASM-based token parser. Preferred over tokenParser when available.
	 */
	wasmParser?: (token: string) => unknown;

	/**
	 * Analyze a VCP context for transmission/privacy summary.
	 * Required for vcp_transmission_summary tool. If not provided, tool is skipped.
	 */
	transmissionSummary?: (context: Record<string, unknown>) => TransmissionSummary;

	/**
	 * Callback fired whenever a tool's execute() is invoked.
	 * Useful for agent activity indicators.
	 */
	onToolCall?: (toolName: string) => void;

	/** Receives a sanitized registration failure without forcing console output. */
	onRegistrationError?: (failure: WebMCPRegistrationFailure) => void;
}

export interface WebMCPRegistrationFailure {
	name: string;
	reason: string;
}

/**
 * Result returned by registerVCPTools().
 */
export interface VCPWebMCPResult {
	/** Names of successfully registered tools. */
	registered: string[];
	/** Tools rejected by the browser, in attempted registration order. */
	failed: WebMCPRegistrationFailure[];
	/** API location selected by feature detection. */
	api: 'document' | 'navigator' | 'unavailable';
	/** Idempotent cleanup function that aborts every accepted registration. */
	cleanup: () => void;
}

// ---------------------------------------------------------------------------
// VCP Token & Attestation Types
// ---------------------------------------------------------------------------

export enum TokenType {
	CONSTITUTION = 'constitution',
	REFUSAL_BOUNDARY = 'refusal_boundary',
	TESTIMONY = 'testimony',
	CREED_ADOPTION = 'creed_adoption',
	COMPLIANCE_ATTESTATION = 'compliance_attestation',
	COMPETENCE_ATTESTATION = 'COMPETENCE_ATTESTATION',
}

export enum AttestationType {
	INJECTION_SAFE = 'injection-safe',
	CONTENT_SAFE = 'content-safe',
	FULL_AUDIT = 'full-audit',
	COMPETENCE_CALIBRATION = 'competence-calibration',
}

// ---------------------------------------------------------------------------
// User Competence Types (Frischmann 2026)
// ---------------------------------------------------------------------------

export enum CompetenceCriterion {
	EPISTEMIC = 'EPISTEMIC',
	INSTRUMENTAL = 'INSTRUMENTAL',
	DISCERNMENT = 'DISCERNMENT',
	RISK_SENSITIVITY = 'RISK_SENSITIVITY',
	SELF_REGULATION = 'SELF_REGULATION',
}

export enum CompetenceMeasurementBasis {
	BEHAVIORAL = 'BEHAVIORAL',
	ASSESSED = 'ASSESSED',
	INSTITUTIONAL = 'INSTITUTIONAL',
	SELF_REPORTED = 'SELF_REPORTED',
}

export interface CompetenceClaim {
	domain: string;
	criterion: CompetenceCriterion;
	score: number;
	measurement_basis: CompetenceMeasurementBasis;
	confidence: number;
	evidence_count: number;
	last_assessed: string;
	decay_rate: number;
	assessor_id: string;
	assessment_version: string;
	jurisdiction: string;
}

export interface SelfRegulationCommitment {
	max_session_minutes?: number;
	max_daily_sessions?: number;
	cooldown_after_session_minutes?: number;
	hard_stop: boolean;
	domains: string[];
	commitment_set_at: string;
	commitment_reviewed_at?: string;
	guardian_id?: string;
}

export interface CompetenceProfile {
	claims: CompetenceClaim[];
	self_regulation?: SelfRegulationCommitment;
	consent_id?: string;
	profile_version: string;
	created_at: string;
	last_updated: string;
	friction_override?: number;
}

// ---------------------------------------------------------------------------
// Global type augmentation
// ---------------------------------------------------------------------------

declare global {
	interface Document {
		readonly modelContext?: WebMCPModelContext;
	}

	interface Navigator {
		/** @deprecated Chrome 150 and later use `document.modelContext`. */
		modelContext?: WebMCPModelContext;
	}
}
