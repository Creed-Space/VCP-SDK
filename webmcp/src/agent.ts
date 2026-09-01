/**
 * Agent-intuitive VCP Agent Runtime Profile contracts.
 *
 * This module is a source candidate. It performs no implicit network access and
 * carries no authority. Hosts inject controlled and accretive services.
 */

export type AgentProfile =
	| 'observe@0.1.0'
	| 'controlled@0.1.0'
	| 'accretive@0.1.0';

export interface AgentRuntimeProfileOffer {
	kind: 'agent_runtime_profile_offer';
	version: '0.1.0';
	required: readonly AgentProfile[];
	optional: readonly AgentProfile[];
}

export interface AgentRuntimeProfileAcknowledgement {
	kind: 'agent_runtime_profile_ack';
	version: '0.1.0';
	selected: readonly AgentProfile[];
	unsupported_optional: readonly AgentProfile[];
	bootstrap_ref: string;
	capability_catalog_digest: string;
	principal_session_ref: string;
	event_binding: 'cursor' | 'stream' | 'poll';
	expires_at: string;
}

export type AgentResultStatus =
	| 'ready'
	| 'degraded'
	| 'awaiting_review'
	| 'blocked'
	| 'unavailable'
	| 'stale'
	| 'conflicting'
	| 'budget_exhausted'
	| 'indeterminate'
	| 'failed';

export type EffectClass =
	| 'pure_local'
	| 'state_read'
	| 'sensitive_egress'
	| 'reversible_write'
	| 'communication'
	| 'financial'
	| 'legal'
	| 'physical';

export interface ResourceBudget {
	wall_time_ms: number | null;
	tokens: number | null;
	external_calls: number | null;
	money_minor: number | null;
	human_interruptions: number | null;
	reserve_fraction: number;
	model_calls: number | null;
	local_compute_ms: number | null;
	bytes: number | null;
	sensitive_egress_bytes: number | null;
	privacy_units: number | null;
	risk_units: number | null;
	welfare_load_units: number | null;
}

export interface SituationView {
	kind: 'situation_view';
	version: '0.1.0';
	situation_id: string;
	goal: string;
	principal_ref: string;
	known_claim_refs: readonly string[];
	unknowns: readonly string[];
	conflict_refs: readonly string[];
	normative_context_ref: string;
	authority_refs: readonly string[];
	budget: ResourceBudget;
	active_work_refs: readonly string[];
	control_operations: readonly string[];
	affordance_refs: readonly string[];
	omissions: readonly unknown[];
	as_of: string;
	cursor: string;
	dependency_digest: string;
	digest: string;
}

export interface ActionIntent {
	kind: 'action_intent';
	version: '0.1.0';
	intent_id: string;
	run_ref: string;
	step_ref: string;
	affordance_ref: string;
	arguments_digest: string;
	destination: string;
	context_digest: string;
	policy_digest: string;
	descriptor_digest: string;
	requested_at: string;
	digest: string;
	schema_digest: string;
	effect_class: EffectClass;
	situation_digest: string;
	expected_postconditions: readonly string[];
	resource_ceiling: ResourceBudget;
	idempotency_scope: string;
	requested_authority: string;
}

export interface ExecutionReceipt {
	kind: 'execution_receipt';
	version: '0.1.0';
	receipt_id: string;
	attempt_ref: string;
	effect_status:
		| 'none'
		| 'accepted'
		| 'observed'
		| 'failed'
		| 'possible'
		| 'indeterminate'
		| 'compensated';
	provider_ref: string | null;
	evidence_refs: readonly string[];
	observed_at: string;
	reconcile_ref: string | null;
	digest: string;
}

export interface AccretionCandidate {
	kind: 'accretion_candidate';
	version: '0.1.0';
	candidate_id: string;
	candidate_kind: string;
	content: unknown;
	scope: readonly string[];
	provenance_refs: readonly string[];
	validation_status: string;
	review_required: boolean;
	expires_at?: string | null;
	digest: string;
	source_run_ref: string;
	supporting_evidence_refs: readonly string[];
	contradicting_evidence_refs: readonly string[];
	sensitivity: string;
	confidence: number;
	invalidation_triggers: readonly string[];
	revalidation: string;
	promotion_policy: string;
	expected_utility: number;
	rollback: string;
	quarantine_status: string;
	dependency_digest: string;
}

export interface PromotionRecord {
	kind: 'promotion_record';
	version: '0.1.0';
	promotion_id: string;
	candidate_ref: string;
	promoted_asset_ref: string;
	authority_ref: string;
	decision_ref: string;
	promoted_at: string;
	expires_at?: string | null;
	revocation_ref: string;
	digest: string;
	evidence_refs: readonly string[];
	validation_results: readonly string[];
	scope: readonly string[];
	promoted_content_digest: string;
	dependency_digest: string;
}

export type AgentArtifact =
	| SituationView
	| ActionIntent
	| ExecutionReceipt
	| AccretionCandidate
	| PromotionRecord;

export type AgentRuntimeDocument =
	| AgentRuntimeProfileOffer
	| AgentRuntimeProfileAcknowledgement
	| AgentArtifact;

export interface AgentFailure {
	code: string;
	category: string;
	summary: string;
	retry: string;
}

export interface AgentResult<T> {
	status: AgentResultStatus;
	value: T | null;
	failure: AgentFailure | null;
	warnings: readonly string[];
	evidence_refs: readonly string[];
}

const ARTIFACT_KEYS: Record<AgentArtifact['kind'], ReadonlySet<string>> = {
	situation_view: new Set([
		'kind', 'version', 'situation_id', 'goal', 'principal_ref',
		'known_claim_refs', 'unknowns', 'conflict_refs', 'normative_context_ref',
		'authority_refs', 'budget', 'active_work_refs', 'control_operations',
		'affordance_refs', 'omissions', 'as_of', 'cursor', 'dependency_digest', 'digest'
	]),
	action_intent: new Set([
		'kind', 'version', 'intent_id', 'run_ref', 'step_ref', 'affordance_ref',
		'arguments_digest', 'destination', 'context_digest', 'policy_digest',
		'descriptor_digest', 'requested_at', 'digest', 'schema_digest', 'effect_class',
		'situation_digest', 'expected_postconditions', 'resource_ceiling',
		'idempotency_scope', 'requested_authority'
	]),
	execution_receipt: new Set([
		'kind', 'version', 'receipt_id', 'attempt_ref', 'effect_status', 'provider_ref',
		'evidence_refs', 'observed_at', 'reconcile_ref', 'digest'
	]),
	accretion_candidate: new Set([
		'kind', 'version', 'candidate_id', 'candidate_kind', 'content', 'scope',
		'provenance_refs', 'validation_status', 'review_required', 'expires_at',
		'digest', 'source_run_ref', 'supporting_evidence_refs',
		'contradicting_evidence_refs', 'sensitivity', 'confidence',
		'invalidation_triggers', 'revalidation', 'promotion_policy',
		'expected_utility', 'rollback', 'quarantine_status', 'dependency_digest'
	]),
	promotion_record: new Set([
		'kind', 'version', 'promotion_id', 'candidate_ref', 'promoted_asset_ref',
		'authority_ref', 'decision_ref', 'promoted_at', 'expires_at',
		'revocation_ref', 'digest', 'evidence_refs', 'validation_results', 'scope',
		'promoted_content_digest', 'dependency_digest'
	])
};

const NEGOTIATION_KEYS: Record<
	AgentRuntimeProfileOffer['kind'] | AgentRuntimeProfileAcknowledgement['kind'],
	ReadonlySet<string>
> = {
	agent_runtime_profile_offer: new Set(['kind', 'version', 'required', 'optional']),
	agent_runtime_profile_ack: new Set([
		'kind', 'version', 'selected', 'unsupported_optional', 'bootstrap_ref',
		'capability_catalog_digest', 'principal_session_ref', 'event_binding', 'expires_at'
	])
};

const PROFILE_IDS = new Set<AgentProfile>([
	'observe@0.1.0',
	'controlled@0.1.0',
	'accretive@0.1.0'
]);

function objectValue(input: unknown): Record<string, unknown> {
	if (typeof input !== 'object' || input === null || Array.isArray(input)) {
		throw new TypeError('agent artifact must be an object');
	}
	return input as Record<string, unknown>;
}

/** Parse a portable artifact without accepting undeclared authority fields. */
export function parseAgentArtifact(input: unknown): AgentArtifact {
	const document = parseAgentRuntimeDocument(input);
	if (
		document.kind === 'agent_runtime_profile_offer' ||
		document.kind === 'agent_runtime_profile_ack'
	) {
		throw new TypeError('expected an agent artifact, received negotiation metadata');
	}
	return document;
}

/** Parse a portable runtime document, including exact profile negotiation. */
export function parseAgentRuntimeDocument(input: unknown): AgentRuntimeDocument {
	const value = objectValue(input);
	const kind = value.kind;
	if (
		typeof kind !== 'string' ||
		(!(kind in ARTIFACT_KEYS) && !(kind in NEGOTIATION_KEYS))
	) {
		throw new TypeError('unsupported agent runtime document kind');
	}
	const keys = kind in ARTIFACT_KEYS
		? ARTIFACT_KEYS[kind as AgentArtifact['kind']]
		: NEGOTIATION_KEYS[kind as keyof typeof NEGOTIATION_KEYS];
	for (const key of Object.keys(value)) {
		if (!keys.has(key)) throw new TypeError(`undeclared field: ${key}`);
	}
	if (value.version !== '0.1.0') {
		throw new TypeError('unsupported agent artifact version');
	}
	if (kind === 'agent_runtime_profile_offer') {
		const required = exactProfiles(value.required, 'required');
		const optional = exactProfiles(value.optional, 'optional');
		if (new Set([...required, ...optional]).size !== required.length + optional.length) {
			throw new TypeError('profile offer entries must be unique');
		}
		return value as unknown as AgentRuntimeProfileOffer;
	}
	if (kind === 'agent_runtime_profile_ack') {
		const selected = exactProfiles(value.selected, 'selected');
		exactProfiles(value.unsupported_optional, 'unsupported_optional');
		if (selected.length === 0) throw new TypeError('selected must not be empty');
		if (
			typeof value.capability_catalog_digest !== 'string' ||
			!/^sha256:[a-f0-9]{64}$/.test(value.capability_catalog_digest)
		) throw new TypeError('invalid capability catalog digest');
		if (!['cursor', 'stream', 'poll'].includes(String(value.event_binding))) {
			throw new TypeError('invalid event binding');
		}
		for (const field of ['bootstrap_ref', 'principal_session_ref', 'expires_at'] as const) {
			if (typeof value[field] !== 'string' || value[field].length === 0) {
				throw new TypeError(`invalid ${field}`);
			}
		}
		return value as unknown as AgentRuntimeProfileAcknowledgement;
	}
	if (typeof value.digest !== 'string' || !/^sha256:[a-f0-9]{64}$/.test(value.digest)) {
		throw new TypeError('invalid artifact digest');
	}
	return value as unknown as AgentArtifact;
}

function exactProfiles(value: unknown, field: string): AgentProfile[] {
	if (!Array.isArray(value) || value.length > 3) {
		throw new TypeError(`${field} must be an array of at most three profiles`);
	}
	if (value.some((profile) => typeof profile !== 'string' || !PROFILE_IDS.has(profile as AgentProfile))) {
		throw new TypeError(`${field} contains an unsupported profile`);
	}
	if (new Set(value).size !== value.length) throw new TypeError(`${field} profiles must be unique`);
	return value as AgentProfile[];
}

/**
 * Exhaustively handle every expected operational state.
 *
 * Working if adding a new status causes a TypeScript error at each call site.
 */
export function matchAgentResult<T, R>(
	result: AgentResult<T>,
	handlers: { [K in AgentResultStatus]: (result: AgentResult<T> & { status: K }) => R }
): R {
	const handler = handlers[result.status] as (
		value: AgentResult<T> & { status: typeof result.status }
	) => R;
	return handler(result as AgentResult<T> & { status: typeof result.status });
}

const OBSERVE_BUDGET: ResourceBudget = {
	wall_time_ms: 2_000,
	tokens: 4_000,
	external_calls: 0,
	money_minor: 0,
	human_interruptions: 0,
	reserve_fraction: 0.2,
	model_calls: 0,
	local_compute_ms: 500,
	bytes: 65_536,
	sensitive_egress_bytes: 0,
	privacy_units: 0,
	risk_units: 0,
	welfare_load_units: 0
};

async function sha256(value: string): Promise<string> {
	const bytes = new TextEncoder().encode(value);
	const digest = await globalThis.crypto.subtle.digest('SHA-256', bytes);
	return 'sha256:' + Array.from(new Uint8Array(digest), byte =>
		byte.toString(16).padStart(2, '0')
	).join('');
}

/** No-network local orientation facade for browser and WebMCP consumers. */
export class LocalAgentRuntime {
	readonly profile: AgentProfile = 'observe@0.1.0';

	async bootstrap(goal: string, budget: ResourceBudget = OBSERVE_BUDGET): Promise<AgentResult<SituationView>> {
		if (goal.length === 0) throw new TypeError('goal must not be empty');
		const dependency = await sha256(JSON.stringify({ goal, budget, profile: this.profile }));
		const suffix = dependency.slice(7, 23);
		const viewWithoutDigest = {
			kind: 'situation_view' as const,
			version: '0.1.0' as const,
			situation_id: `situation.web.${suffix}`,
			goal,
			principal_ref: 'vcp:artifact:principal:web-observer',
			known_claim_refs: [] as readonly string[],
			unknowns: ['host policy state', 'deployment state'] as readonly string[],
			conflict_refs: [] as readonly string[],
			normative_context_ref: 'vcp:artifact:normative:web-observe',
			authority_refs: ['vcp:artifact:authority:local-read'] as readonly string[],
			budget,
			active_work_refs: [] as readonly string[],
			control_operations: [] as readonly string[],
			affordance_refs: [
				`vcp:artifact:affordance:inspect.assurance.${suffix}`
			] as readonly string[],
			omissions: [
				{ field: 'host authority', reason: 'unavailable' }
			] as readonly unknown[],
			as_of: '1970-01-01T00:00:00Z',
			cursor: 'cursor.web.0',
			dependency_digest: dependency
		};
		const digest = await sha256(JSON.stringify(viewWithoutDigest));
		const view: SituationView = { ...viewWithoutDigest, digest };
		return {
			status: 'ready',
			value: view,
			failure: null,
			warnings: [],
			evidence_refs: []
		};
	}
}
