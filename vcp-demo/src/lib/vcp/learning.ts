/**
 * Learning VCP Types
 * Types for adaptive learning paths, cognitive load, and personalized teaching
 */

import type { VCPContext, ExperienceLevel } from './types';

// ============================================
// Learning Preferences
// ============================================

export interface LearningPreferences {
	/** Domains the learner relates to well */
	preferred_analogies: string[]; // e.g., ['sports', 'cooking', 'music', 'gardening']

	/** How they best absorb information */
	modality_preferences: ModalityPreference[];

	/** How sensitive they are to pacing */
	pace_sensitivity: number; // 0-1: how much to adjust for load

	/** Appetite for challenge */
	challenge_appetite: number; // 1-9

	/** How much feedback they want */
	feedback_granularity: 'high' | 'medium' | 'low';

	/** Preferred learning time chunks */
	session_duration_preference: number; // minutes

	/** Break frequency preference */
	break_frequency: 'frequent' | 'moderate' | 'minimal';

	/** How they handle errors */
	error_tolerance: 'high' | 'medium' | 'low';

	/** Prefer theory first or practice first */
	theory_practice_balance: 'theory_first' | 'practice_first' | 'interleaved';
}

export interface ModalityPreference {
	type: 'visual' | 'auditory' | 'kinesthetic' | 'reading' | 'social';
	effectiveness: number; // 0-1: how well this works for them
	current_availability: boolean; // e.g., can't watch video right now
	notes?: string;
}

// ============================================
// Cognitive Load
// ============================================

export interface CognitiveLoadState {
	/** Overall current load 0-1 */
	current_load: number;

	/** Load from material complexity (unavoidable) */
	intrinsic_load: number;

	/** Load from poor presentation (should minimize) */
	extraneous_load: number;

	/** Load from active learning (beneficial) */
	germane_load: number;

	/** Time-based degradation factor */
	fatigue_factor: number;

	/** When they last took a break */
	last_break: string; // ISO timestamp

	/** Time spent in current session */
	session_duration_minutes: number;

	/** Estimated capacity remaining */
	capacity_remaining: number; // 0-1

	/** Signals suggesting overload */
	overload_indicators: OverloadIndicator[];
}

export interface OverloadIndicator {
	type: 'response_time_increase' | 'error_rate_increase' | 'engagement_drop' | 'explicit_signal';
	severity: number; // 0-1
	timestamp: string;
}

// ============================================
// Mastery Tracking
// ============================================

export interface MasteryLevel {
	topic_id: string;
	topic_name: string;
	level: ExperienceLevel;
	confidence: number; // 0-1: how confident in this assessment
	last_assessed: string;
	assessment_method: 'self_report' | 'quiz' | 'demonstration' | 'inferred';
	prerequisites_met: boolean;
	time_to_next_level?: number; // estimated hours
	decay_risk: number; // 0-1: likelihood of forgetting
}

export interface LearningPath {
	path_id: string;
	name: string;
	description: string;
	topics: LearningTopic[];
	current_position: number;
	estimated_total_hours: number;
	completed_hours: number;
	personalization_applied: string[];
}

export interface LearningTopic {
	topic_id: string;
	name: string;
	prerequisites: string[];
	estimated_hours: number;
	difficulty: number; // 1-5
	modalities_available: string[];
	analogies_available: string[];
	mastery_threshold: number; // 0-1
}

// ============================================
// Adaptive Content
// ============================================

export interface AdaptiveContentRequest {
	topic_id: string;
	learner_context: LearnerContext;
	constraints: ContentConstraints;
}

export interface LearnerContext extends Partial<VCPContext> {
	learning_preferences: LearningPreferences;
	cognitive_load_state: CognitiveLoadState;
	current_mastery: Record<string, MasteryLevel>;
	recent_errors: RecentError[];
	session_goals: string[];
}

export interface ContentConstraints {
	max_duration_minutes: number;
	available_modalities: string[];
	noise_restricted: boolean;
	mobile_only: boolean;
	offline_required: boolean;
}

export interface RecentError {
	topic_id: string;
	error_type: string;
	timestamp: string;
	remediation_shown: boolean;
}

export interface AdaptedContent {
	content_id: string;
	topic_id: string;
	format: ContentFormat;
	estimated_duration: number;
	difficulty_adjusted: number;
	analogies_used: string[];
	adaptations_applied: Adaptation[];
	cognitive_load_estimate: number;
}

export interface ContentFormat {
	type: 'text' | 'video' | 'interactive' | 'audio' | 'quiz' | 'exercise';
	length: 'micro' | 'short' | 'medium' | 'long';
	interaction_level: 'passive' | 'active' | 'highly_interactive';
}

export interface Adaptation {
	type: AdaptationType;
	reason: string;
	original_value?: string;
	adapted_value?: string;
}

export type AdaptationType =
	| 'difficulty_reduction'
	| 'difficulty_increase'
	| 'analogy_substitution'
	| 'modality_change'
	| 'pace_adjustment'
	| 'chunking'
	| 'scaffolding_added'
	| 'examples_increased'
	| 'practice_added'
	// Prosaic-driven adaptations
	| 'content_compression'
	| 'session_modification'
	| 'feedback_adjustment';

// ============================================
// Learning Session
// ============================================

export interface LearningSession {
	session_id: string;
	learner_id: string;
	started: string;
	ended?: string;
	topics_covered: string[];
	cognitive_load_timeline: CognitiveLoadSnapshot[];
	adaptations_made: Adaptation[];
	mastery_changes: MasteryChange[];
	session_rating?: number;
	learner_feedback?: string;
}

export interface CognitiveLoadSnapshot {
	timestamp: string;
	load: number;
	trigger?: string;
}

export interface MasteryChange {
	topic_id: string;
	before: ExperienceLevel;
	after: ExperienceLevel;
	confidence_change: number;
}

// ============================================
// Demo Scenarios
// ============================================

export interface LearningDemoScenario {
	id: string;
	name: string;
	description: string;
	initial_learner: LearnerContext;
	content_sequence: AdaptedContent[];
	expected_adaptations: string[];
	learning_points: string[];
}
