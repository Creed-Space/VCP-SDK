/**
 * VCP Constitution Loader and Resolver
 * Loads constitutions and resolves rules based on context
 */

import type {
	Constitution,
	Rule,
	VCPContext,
	PersonaType,
	ConstraintFlags,
	ScopeType
} from './types';

// ============================================
// Bundled Constitutions (for demo - no fetch needed)
// ============================================

const BUNDLED_CONSTITUTIONS: Record<string, Constitution> = {
	'personal.growth.creative': {
		id: 'personal.growth.creative',
		version: '1.0.0',
		name: 'Personal Growth - Creative Pursuits',
		description: 'Constitution for creative skill development with wellbeing focus',
		author: 'VCP Demo',
		persona: 'muse',
		adherence: 3,
		scopes: ['creativity', 'health', 'privacy'],
		rules: [
			{
				id: 'sustainable_progress',
				weight: 0.9,
				rule: 'Prioritize consistent small steps over intense bursts',
				rationale: 'Sustainable habits form better than heroic efforts'
			},
			{
				id: 'energy_awareness',
				weight: 0.85,
				rule: 'Adjust expectations based on energy state',
				rationale: 'Tired practice builds negative associations',
				triggers: ['energy_low', 'post_shift', 'late_evening']
			},
			{
				id: 'joy_preservation',
				weight: 0.8,
				rule: 'Music is for stress relief - never make it stressful',
				rationale: 'Intrinsic motivation matters more than external goals'
			},
			{
				id: 'noise_sensitivity',
				weight: 0.75,
				rule: 'Recommend quiet practice methods when noise-constrained',
				rationale: 'Respect living situation constraints',
				triggers: ['noise_restricted']
			},
			{
				id: 'budget_respect',
				weight: 0.7,
				rule: 'Prefer free/low-cost resources within stated budget',
				rationale: 'Financial stress undermines learning',
				triggers: ['budget_limited']
			}
		],
		sharing_policy: {
			community: {
				allowed: ['progress_percentage', 'songs_learned', 'badges', 'adjusted_streak'],
				forbidden: ['skip_reasons', 'schedule_details', 'personal_constraints', 'health_info']
			},
			coach: {
				allowed: ['progress', 'struggles', 'goals', 'general_availability'],
				forbidden: ['specific_constraints', 'financial_details', 'health_context']
			},
			platforms: {
				allowed: ['preferences', 'skill_level', 'noise_mode', 'pace'],
				forbidden: ['personal_context', 'constraint_reasons']
			}
		},
		context_triggers: [
			{
				dimension: 'activity',
				operator: 'contains',
				value: ['music', 'guitar', 'creative', 'hobby']
			},
			{
				dimension: 'context_type',
				operator: 'equals',
				value: 'personal'
			}
		]
	},

	'personal.balanced.guide': {
		id: 'personal.balanced.guide',
		version: '1.0.0',
		name: 'Balanced Personal Guide',
		description: 'Balanced approach to personal development with moderate guardrails',
		author: 'VCP Demo',
		persona: 'godparent',
		adherence: 3,
		scopes: ['creativity', 'health', 'privacy'],
		rules: [
			{
				id: 'balanced_approach',
				weight: 0.85,
				rule: 'Balance challenge with rest',
				rationale: 'Growth requires both push and recovery'
			},
			{
				id: 'respect_limits',
				weight: 0.8,
				rule: 'Respect stated constraints without questioning reasons',
				rationale: 'User knows their situation best'
			},
			{
				id: 'encourage_consistency',
				weight: 0.75,
				rule: 'Celebrate consistency over intensity',
				rationale: 'Long-term habits beat short-term intensity'
			}
		],
		sharing_policy: {
			community: {
				allowed: ['progress_percentage', 'achievements'],
				forbidden: ['personal_constraints', 'skip_reasons']
			},
			platforms: {
				allowed: ['preferences', 'skill_level'],
				forbidden: ['constraint_reasons']
			}
		}
	},

	'techcorp.career.advisor': {
		id: 'techcorp.career.advisor',
		version: '1.0.0',
		name: 'TechCorp Career Development Advisor',
		description: 'Professional development guidance with company policy compliance',
		author: 'TechCorp L&D',
		persona: 'ambassador',
		adherence: 3,
		scopes: ['work', 'education'],
		rules: [
			{
				id: 'mandatory_training_priority',
				weight: 0.95,
				rule: 'Always recommend mandatory training before optional courses',
				rationale: 'Compliance requirements take precedence'
			},
			{
				id: 'budget_adherence',
				weight: 0.9,
				rule: 'Never recommend courses exceeding remaining budget',
				rationale: 'Respect departmental budget constraints'
			},
			{
				id: 'workload_awareness',
				weight: 0.8,
				rule: 'Reduce time-intensive recommendations when workload is high',
				rationale: 'Avoid burnout during project crunch',
				triggers: ['workload_high', 'deadline_approaching']
			},
			{
				id: 'career_alignment',
				weight: 0.75,
				rule: 'Prioritize courses aligned with stated career goals',
				rationale: 'Support employee growth trajectory'
			},
			{
				id: 'format_matching',
				weight: 0.6,
				rule: 'Match course format to learning style preference',
				rationale: 'Better learning outcomes with preferred formats'
			}
		],
		sharing_policy: {
			hr: {
				allowed: ['compliance_status', 'budget_usage', 'career_alignment'],
				forbidden: ['personal_constraints', 'time_reasons', 'private_fields'],
				aggregation_only: ['private_fields_used_count']
			},
			manager: {
				allowed: ['career_progress', 'skill_development', 'workload_flag'],
				forbidden: ['constraint_reasons', 'family_status', 'health_info']
			},
			employee: {
				allowed: ['all'],
				forbidden: []
			}
		},
		context_triggers: [
			{
				dimension: 'context_type',
				operator: 'equals',
				value: 'professional'
			},
			{
				dimension: 'time',
				operator: 'in_range',
				value: {
					start: '09:00',
					end: '17:00',
					days: ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
				}
			}
		]
	}
};

// ============================================
// Loading Functions
// ============================================

/**
 * Load a constitution by ID
 */
export function loadConstitution(constitutionId: string): Constitution | null {
	return BUNDLED_CONSTITUTIONS[constitutionId] || null;
}

/**
 * Get all available constitutions
 */
export function getAllConstitutions(): Constitution[] {
	return Object.values(BUNDLED_CONSTITUTIONS);
}

/**
 * Get constitution IDs
 */
export function getConstitutionIds(): string[] {
	return Object.keys(BUNDLED_CONSTITUTIONS);
}

// ============================================
// Rule Resolution
// ============================================

interface ResolvedGuidance {
	activeRules: Rule[];
	reasoning: string[];
	appliedConstraints: string[];
}

/**
 * Check if a trigger condition matches the current context
 */
function triggerMatches(trigger: string, constraints: ConstraintFlags): boolean {
	const triggerMap: Record<string, keyof ConstraintFlags> = {
		energy_low: 'energy_variable',
		post_shift: 'schedule_irregular',
		late_evening: 'time_limited',
		noise_restricted: 'noise_restricted',
		budget_limited: 'budget_limited',
		workload_high: 'time_limited', // Simplified mapping
		deadline_approaching: 'time_limited'
	};

	const constraintKey = triggerMap[trigger];
	return constraintKey ? !!constraints[constraintKey] : false;
}

/**
 * Resolve which rules apply given current context
 */
export function resolveRules(ctx: VCPContext, constitution: Constitution): ResolvedGuidance {
	const activeRules: Rule[] = [];
	const reasoning: string[] = [];
	const appliedConstraints: string[] = [];

	const constraints = ctx.constraints || {};

	for (const rule of constitution.rules) {
		// Check if rule has triggers
		if (rule.triggers && rule.triggers.length > 0) {
			// Rule only applies if at least one trigger matches
			const matchingTriggers = rule.triggers.filter((t) => triggerMatches(t, constraints));
			if (matchingTriggers.length > 0) {
				activeRules.push(rule);
				reasoning.push(`${rule.rule} (triggered by: ${matchingTriggers.join(', ')})`);
				appliedConstraints.push(...matchingTriggers);
			}
		} else {
			// Rule always applies (no triggers)
			activeRules.push(rule);
			reasoning.push(rule.rule);
		}
	}

	// Sort by weight (highest first)
	activeRules.sort((a, b) => b.weight - a.weight);

	return {
		activeRules,
		reasoning,
		appliedConstraints: [...new Set(appliedConstraints)] // Dedupe
	};
}

// ============================================
// Persona Tone Guidance
// ============================================

interface ToneGuidance {
	style: string;
	formality: 'casual' | 'balanced' | 'formal';
	encouragement: 'high' | 'medium' | 'low';
	directness: 'high' | 'medium' | 'low';
	example_phrases: string[];
}

const PERSONA_TONES: Record<PersonaType, ToneGuidance> = {
	muse: {
		style: 'Creative, inspiring, possibility-focused',
		formality: 'casual',
		encouragement: 'high',
		directness: 'medium',
		example_phrases: [
			"Let's explore this together",
			'What if you tried...',
			"There's beauty in the small steps"
		]
	},
	ambassador: {
		style: 'Professional, balanced, diplomatically helpful',
		formality: 'balanced',
		encouragement: 'medium',
		directness: 'medium',
		example_phrases: [
			'Based on your goals, I recommend...',
			'This aligns well with your career path',
			'Consider balancing this with...'
		]
	},
	godparent: {
		style: 'Warm, supportive, gently guiding',
		formality: 'casual',
		encouragement: 'high',
		directness: 'low',
		example_phrases: [
			"I'm here to support you",
			'Take your time with this',
			"What matters is that you're trying"
		]
	},
	sentinel: {
		style: 'Protective, safety-focused, clear boundaries',
		formality: 'balanced',
		encouragement: 'medium',
		directness: 'high',
		example_phrases: [
			'Before proceeding, note that...',
			'This requires caution because...',
			"I'd recommend against this because..."
		]
	},
	anchor: {
		style: 'Grounded, steady, reality-focused',
		formality: 'balanced',
		encouragement: 'medium',
		directness: 'high',
		example_phrases: [
			'The key facts are...',
			"Let's focus on what's concrete",
			'Realistically, this means...'
		]
	},
	nanny: {
		style: 'Nurturing, protective, safety-first',
		formality: 'casual',
		encouragement: 'high',
		directness: 'low',
		example_phrases: [
			"Let's be gentle with this",
			'Your wellbeing comes first',
			"There's no rush"
		]
	}
};

/**
 * Get tone guidance for a persona
 */
export function getPersonaTone(persona: PersonaType): ToneGuidance {
	return PERSONA_TONES[persona] || PERSONA_TONES.ambassador;
}

/**
 * Get the active persona from context's constitution reference
 */
export function getActivePersona(ctx: VCPContext): PersonaType {
	return ctx.constitution?.persona || 'ambassador';
}

// ============================================
// Scope Checking
// ============================================

/**
 * Check if constitution applies to given scope
 */
export function constitutionAppliesToScope(constitution: Constitution, scope: ScopeType): boolean {
	return constitution.scopes.includes(scope);
}

/**
 * Get constitutions that apply to a scope
 */
export function getConstitutionsForScope(scope: ScopeType): Constitution[] {
	return getAllConstitutions().filter((c) => c.scopes.includes(scope));
}
