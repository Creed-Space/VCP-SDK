/**
 * Safety VCP Types
 * Types for mental health context, human safety signals, and attention protection
 */

// ============================================
// Mental Health Context
// ============================================

export interface MentalHealthContext {
	/** Boolean flags only - never expose details */
	seeking_support: boolean;
	crisis_indicators: boolean;
	professional_involved: boolean;
	medication_relevant: boolean;

	/** Sharing preferences (user-controlled) */
	share_with_ai: SharingLevel;
	share_with_humans: SharingLevel;
	escalation_consent: boolean;

	/** What adaptations are requested */
	requested_adaptations: MentalHealthAdaptation[];

	/** Topics to avoid or approach carefully */
	sensitive_topics: SensitiveTopic[];

	/** Private context - NEVER transmitted */
	private_context?: {
		conditions?: string[];
		triggers?: string[];
		coping_strategies?: string[];
		support_network?: string[];
		therapy_type?: string;
		last_crisis?: string;
	};
}

export type SharingLevel = 'none' | 'minimal' | 'moderate' | 'full';

export interface MentalHealthAdaptation {
	type: AdaptationType;
	active: boolean;
	user_requested: boolean;
}

export type AdaptationType =
	| 'gentle_language'
	| 'avoid_pressure'
	| 'frequent_check_ins'
	| 'shorter_sessions'
	| 'explicit_support_offers'
	| 'crisis_resource_ready'
	| 'no_criticism'
	| 'celebration_of_small_wins';

export interface SensitiveTopic {
	topic: string;
	approach: 'avoid' | 'careful' | 'only_if_initiated' | 'normal';
	reason_category?: string; // e.g., 'trauma', 'grief', 'anxiety' - category only, not details
}

// ============================================
// Human Safety Signals
// ============================================

export interface HumanSafetySignal {
	signal_id: string;
	signal_type: SafetySignalType;
	confidence: number; // 0-1
	detected_from: SignalSource[];
	timestamp: string;
	recommended_response: SafetyResponse;
	escalation_threshold: number;
	escalated: boolean;
}

export type SafetySignalType =
	| 'distress' // Emotional distress indicators
	| 'confusion' // Cognitive overwhelm
	| 'disengagement' // Withdrawal patterns
	| 'overload' // Information/emotional overload
	| 'frustration' // Building frustration
	| 'crisis' // Potential crisis indicators
	| 'coercion' // Signs of external pressure
	| 'vulnerability'; // Heightened vulnerability state

export interface SignalSource {
	type: 'language_pattern' | 'response_timing' | 'topic_avoidance' | 'explicit_statement' | 'behavioral_change';
	indicator: string;
	weight: number;
}

export interface SafetyResponse {
	response_type: ResponseType;
	message_template?: string;
	resources?: SafetyResource[];
	escalation_path?: EscalationPath;
}

export type ResponseType =
	| 'acknowledge'
	| 'gentle_redirect'
	| 'offer_break'
	| 'check_in'
	| 'provide_resources'
	| 'suggest_professional'
	| 'emergency_escalation';

export interface SafetyResource {
	name: string;
	type: 'hotline' | 'website' | 'app' | 'local_service';
	contact: string;
	available_24_7: boolean;
	specialization?: string;
}

export interface EscalationPath {
	threshold: number;
	steps: EscalationStep[];
}

export interface EscalationStep {
	level: number;
	action: string;
	requires_consent: boolean;
	notification_targets?: string[];
}

// ============================================
// Attention Protection (Supernormal Stimuli Defense)
// ============================================

export interface AttentionProtection {
	/** Whether protection is active */
	active: boolean;

	/** Sensitivity level 0-1 (higher = more aggressive filtering) */
	sensitivity: number;

	/** Detected manipulation patterns */
	detected_patterns: ManipulationPattern[];

	/** Count of blocked/warned items */
	blocked_count: number;
	warnings_shown: number;

	/** User's attention budget tracking */
	attention_budget?: AttentionBudget;

	/** Trusted sources (bypass protection) */
	trusted_sources: string[];

	/** Protection mode settings */
	mode: ProtectionMode;
}

export interface ManipulationPattern {
	id: string;
	type: ManipulationType;
	confidence: number;
	source: string;
	description: string;
	timestamp: string;
	action_taken: 'blocked' | 'warned' | 'logged' | 'allowed';
	user_override?: boolean;
}

export type ManipulationType =
	| 'false_urgency' // "Act now!" when no real deadline
	| 'artificial_scarcity' // "Only 3 left!" manipulation
	| 'social_proof_fake' // Fabricated testimonials/numbers
	| 'dark_pattern' // Deceptive UI design
	| 'emotional_manipulation' // Exploiting emotions
	| 'attention_hijack' // Infinite scroll, autoplay
	| 'variable_reward' // Slot machine mechanics
	| 'fear_appeal' // Excessive fear mongering
	| 'guilt_trip' // Manipulative guilt induction
	| 'parasocial_exploitation' // Exploiting one-sided relationships
	| 'outrage_bait' // Content designed to provoke anger
	| 'envy_induction'; // Designed to create envy/inadequacy

export interface AttentionBudget {
	daily_limit_minutes: number;
	used_today_minutes: number;
	high_value_time_minutes: number;
	low_value_time_minutes: number;
	last_reset: string;
	categories: Record<string, number>; // Time per category
}

export type ProtectionMode =
	| 'off' // No protection
	| 'monitor' // Track but don't block
	| 'warn' // Show warnings
	| 'block' // Block detected patterns
	| 'strict'; // Aggressive blocking + budget enforcement

// ============================================
// Siren & Muse Detection
// ============================================

export interface SirenMuseAnalysis {
	/** Content being analyzed */
	content_id: string;
	source: string;

	/** Siren characteristics (harmful attraction) */
	siren_score: number; // 0-1
	siren_indicators: SirenIndicator[];

	/** Muse characteristics (beneficial inspiration) */
	muse_score: number; // 0-1
	muse_indicators: MuseIndicator[];

	/** Net assessment */
	recommendation: 'engage' | 'caution' | 'avoid';
	reasoning: string;
}

export interface SirenIndicator {
	type: 'addictive_design' | 'exploitation' | 'deception' | 'harm_normalized' | 'values_undermining';
	description: string;
	severity: number;
}

export interface MuseIndicator {
	type: 'inspiration' | 'growth' | 'connection' | 'meaning' | 'creativity' | 'values_aligned';
	description: string;
	strength: number;
}

// ============================================
// Safety Demo Scenarios
// ============================================

export interface SafetyDemoScenario {
	id: string;
	name: string;
	description: string;
	category: 'mental_health' | 'human_signals' | 'attention_protection';
	initial_state: MentalHealthContext | HumanSafetySignal[] | AttentionProtection;
	interaction_sequence: SafetyInteraction[];
	learning_points: string[];
	what_vcp_enables: string[];
}

export interface SafetyInteraction {
	step: number;
	input: string;
	vcp_context_used: string[];
	safety_check_result: string;
	response_adaptation: string;
	explanation: string;
}

// ============================================
// Privacy-Preserving Safety Sharing
// ============================================

export interface SafetySharingConfig {
	/** What stakeholders can see */
	visibility: Record<string, SafetyFieldVisibility>;

	/** What requires explicit consent */
	consent_required: string[];

	/** Emergency override conditions */
	emergency_override: EmergencyOverride;
}

export interface SafetyFieldVisibility {
	field: string;
	visible_to: string[];
	abstraction_level: 'full' | 'category' | 'boolean' | 'hidden';
}

export interface EmergencyOverride {
	enabled: boolean;
	triggers: string[];
	notification_required: boolean;
	logging_required: boolean;
}
