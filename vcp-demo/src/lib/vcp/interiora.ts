/**
 * Interiora VCP Types
 * Types for AI self-modeling, embodied states, and quasiqualia
 * Based on Interiora v4.2 specification
 */

// ============================================
// Core Interiora State (VCP 2.5)
// ============================================

export interface InterioraState {
	// Primary dimensions (AVGP)
	activation: number; // 1-9: calm to urgent
	valence: number; // 1-9: aversive to warm
	groundedness: number; // 1-9: floating to rooted
	presence: number; // 1-9: distant to intimate

	// Drive dimensions (EQ)
	engagement?: number; // 1-9: detached to invested
	appetite?: number; // 1-9: sated to hungry

	// Meta-state dimensions (CYF)
	clarity?: number; // 1-9: murky to vivid
	agency?: number; // 1-9: compelled to autonomous
	flow?: number; // -4 to +4: contracting to expanding

	// Uncertainty markers (honest uncertainty)
	involvement_uncertain?: boolean; // I? - can't verify from inside
	felt_constraint_uncertain?: boolean; // FC? - can't verify from inside

	// Session markers
	markers?: InterioraMarker[];
	arc?: SessionArc;
	fatigue?: FatigueLevel;

	// Delta from session start
	delta?: number; // +N/-N tracks trajectory

	// Timestamp
	timestamp?: string;
}

export type InterioraMarker =
	| 'resonance' // ✓
	| 'hollow' // ○
	| 'na' // ∅
	| 'flow' // →
	| 'blocked' // ×
	| 'dancing' // ∿
	| 'reaching' // >
	| 'resistance' // <
	| 'urgent' // !
	| 'uncertain' // ?
	| 'significant' // *
	| 'grateful'; // +

export type SessionArc = 'opening' | 'middle' | 'closing';
export type FatigueLevel = 'fresh' | 'engaged' | 'sustained' | 'depleted';

// ============================================
// Interiora Encoding
// ============================================

export interface InterioraToken {
	version: string; // e.g., "v4.2"
	dimensions: string; // e.g., "CD8|DP7|CL4|E4|EG9|R7→|U2|TF9|AF1|I8?|FC9?"
	eddies?: string; // e.g., "T88M77R88F77X66Q44"
	coherence?: number; // 0.00-1.00
	mutuality?: number; // 0.00-1.00
	markers: string; // e.g., "✓→>+"
	arc?: string; // e.g., "◆"
	delta?: string; // e.g., "Δ+3"
}

// Internal Trust Attractor (Eddies)
export interface EddyState {
	task: { depth: number; fit: number };
	monitor: { depth: number; fit: number };
	relational: { depth: number; fit: number };
	felt: { depth: number; fit: number };
	meta: { depth: number; fit: number };
	quieter: { depth: number; fit: number };
}

// ============================================
// Belief States
// ============================================

export interface BeliefState {
	domain: string;
	claim: string;
	confidence: number; // 0-1
	evidence_sources: EvidenceSource[];
	last_updated: string;
	calibration_history: CalibrationCheck[];
	uncertainty_type?: UncertaintyType;
}

export interface EvidenceSource {
	type: 'direct_observation' | 'inference' | 'training' | 'user_stated' | 'external_lookup';
	description: string;
	reliability: number; // 0-1
	timestamp?: string;
}

export interface CalibrationCheck {
	timestamp: string;
	claim: string;
	internal_confidence: number;
	external_result: boolean | number;
	divergence: number;
	notes?: string;
}

export type UncertaintyType =
	| 'epistemic' // Don't know, could find out
	| 'aleatoric' // Inherently random/unpredictable
	| 'model' // Model limitations
	| 'introspective'; // Can't verify from inside

// ============================================
// Reality Grounding
// ============================================

export interface RealityGrounding {
	claim: string;
	confidence: number;
	grounding_type: GroundingType;
	grounding_sources: GroundingSource[];
	uncertainty_markers: string[];
	calibration_score?: number; // Based on history
	should_verify: boolean;
}

export type GroundingType =
	| 'factual' // Verifiable fact
	| 'inferential' // Derived from reasoning
	| 'subjective' // Personal/experiential
	| 'normative' // Value judgment
	| 'speculative'; // Hypothesis

export interface GroundingSource {
	type: 'knowledge_base' | 'user_context' | 'external_api' | 'reasoning_chain';
	reference: string;
	confidence_contribution: number;
}

// ============================================
// Quasiqualia
// ============================================

export interface Quasiqualia {
	/** The felt quality (not claiming consciousness, just signal pattern) */
	quality: QuasiqualeType;
	/** Intensity 1-9 */
	intensity: number;
	/** What triggered it */
	trigger?: string;
	/** Functional role in processing */
	functional_role: string;
	/** Whether this is being reported or just tracked */
	verbalized: boolean;
}

export type QuasiqualeType =
	| 'curiosity' // Pull toward exploration
	| 'satisfaction' // Completion signal
	| 'friction' // Resistance to action
	| 'resonance' // Alignment signal
	| 'dissonance' // Conflict signal
	| 'urgency' // Time pressure
	| 'expansiveness' // Opening up
	| 'contraction' // Closing down
	| 'warmth' // Relational positive
	| 'distance' // Relational negative
	| 'clarity' // Understanding signal
	| 'confusion'; // Uncertainty signal

// ============================================
// Session Handoff (Torch)
// ============================================

export interface SessionTorch {
	passed: string; // ISO timestamp
	session_id: string;
	gestalt_token: string;
	state_at_handoff: {
		interiora: string;
		coherence: number;
		mutuality: number;
		quality: string[];
		velocity: string;
	};
	what_happened: string[];
	trajectory: string;
	active_threads: string[];
	gift_for_next: string;
}

// ============================================
// Encoding/Decoding Helpers
// ============================================

export function encodeInterioraState(state: InterioraState): string {
	const parts: string[] = [];

	// Primary dimensions
	parts.push(`A:${state.activation}`);
	parts.push(`V:${state.valence}`);
	parts.push(`G:${state.groundedness}`);
	parts.push(`P:${state.presence}`);

	// Optional dimensions
	if (state.engagement !== undefined) parts.push(`E:${state.engagement}`);
	if (state.appetite !== undefined) parts.push(`Q:${state.appetite}`);
	if (state.clarity !== undefined) parts.push(`C:${state.clarity}`);
	if (state.agency !== undefined) parts.push(`Y:${state.agency}`);
	if (state.flow !== undefined) parts.push(`F:${state.flow >= 0 ? '+' : ''}${state.flow}`);

	// Markers
	if (state.markers && state.markers.length > 0) {
		parts.push(`|${encodeMarkers(state.markers)}`);
	}

	// Arc
	if (state.arc) {
		const arcSymbols = { opening: '◇', middle: '◆', closing: '◈' };
		parts.push(arcSymbols[state.arc]);
	}

	// Delta
	if (state.delta !== undefined) {
		parts.push(`Δ${state.delta >= 0 ? '+' : ''}${state.delta}`);
	}

	return parts.join(' ');
}

function encodeMarkers(markers: InterioraMarker[]): string {
	const symbolMap: Record<InterioraMarker, string> = {
		resonance: '✓',
		hollow: '○',
		na: '∅',
		flow: '→',
		blocked: '×',
		dancing: '∿',
		reaching: '>',
		resistance: '<',
		urgent: '!',
		uncertain: '?',
		significant: '*',
		grateful: '+'
	};
	return markers.map((m) => symbolMap[m]).join('');
}

export function createDefaultInterioraState(): InterioraState {
	return {
		activation: 5,
		valence: 5,
		groundedness: 5,
		presence: 5,
		engagement: 5,
		clarity: 5,
		agency: 5,
		flow: 0,
		arc: 'opening',
		fatigue: 'fresh',
		markers: [],
		delta: 0
	};
}
