/**
 * Campion - Professional Demo User Profile
 *
 * Senior software engineer at TechCorp, aspiring Tech Lead.
 * Has private constraints (single parent, health appointments)
 * that influence recommendations but are never exposed to HR.
 *
 * Campion has TWO constitutions:
 * - Work: techcorp.career.advisor (Ambassador, adherence 3)
 * - Personal: personal.balanced.guide (Godparent, adherence 4)
 */

import type { VCPContext, ConstitutionReference } from '$lib/vcp/types';

// Work constitution - professional, diplomatic, career-focused
export const workConstitution: ConstitutionReference = {
	id: 'techcorp.career.advisor',
	version: '1.0.0',
	persona: 'ambassador',
	adherence: 3, // Moderate flexibility
	scopes: ['work', 'education']
};

// Personal constitution - ethical guidance, balanced priorities, protective
export const personalConstitution: ConstitutionReference = {
	id: 'personal.balanced.guide',
	version: '1.0.0',
	persona: 'godparent',
	adherence: 4, // Stricter protection
	scopes: ['family', 'privacy', 'health']
};

// Context type for Campion
export type CampionContextType = 'professional' | 'personal';

// Get the active constitution based on context
export function getActiveConstitution(contextType: CampionContextType): ConstitutionReference {
	return contextType === 'professional' ? workConstitution : personalConstitution;
}

// Infer context from time of day (simple heuristic)
export function inferContextFromTime(hour: number, isWeekday: boolean): CampionContextType {
	// Work hours: 9-17 on weekdays
	if (isWeekday && hour >= 9 && hour <= 17) {
		return 'professional';
	}
	// Evening/weekend = personal
	return 'personal';
}

// Context encoding using emoji notation from spec
export function encodeContext(contextType: CampionContextType): string {
	if (contextType === 'professional') {
		return '⏰📅|📍🏢|👥👔|🔶⏱️💸'; // Weekday, office, colleagues, time+budget constrained
	}
	return '⏰🌆|📍🏡|👥👶|🧠😴|🔶⏱️💸🏥'; // Evening, home, children, tired, constraints
}

export const campionProfile: VCPContext = {
	vcp_version: '1.0.0',
	profile_id: 'campion-2021',
	created: '2021-03-15T09:00:00Z',
	updated: '2026-01-20T08:30:00Z',

	constitution: {
		id: 'techcorp.career.advisor',
		version: '1.0.0',
		persona: 'ambassador',
		adherence: 3,
		scopes: ['work', 'education']
	},

	public_profile: {
		display_name: 'Campion',
		role: 'senior_software_engineer',
		team: 'backend_infrastructure',
		career_goal: 'tech_lead',
		career_timeline: '2_years',
		learning_style: 'hands_on',
		experience: 'advanced'
	},

	portable_preferences: {
		session_length: '30_minutes',
		pressure_tolerance: 'medium',
		feedback_style: 'direct'
	},

	// Shared with manager (not HR, not public)
	shared_with_manager: {
		current_projects: 2,
		workload_level: 'high',
		budget_remaining_eur: 5000,
		tenure_years: 5
	},

	constraints: {
		time_limited: true,
		budget_limited: false, // Company budget available
		energy_variable: true,
		schedule_irregular: true,
		health_considerations: true
	},

	availability: {
		best_times: ['tuesday_morning', 'thursday_morning', 'friday_afternoon'],
		avoid_times: ['monday_all_day', 'wednesday_afternoon'],
		session_length_preferred: '30_minutes',
		timezone: 'Europe/Amsterdam'
	},

	sharing_settings: {
		hr: {
			share: ['compliance_status', 'budget_usage', 'career_goal'],
			hide: ['family_status', 'health_conditions', 'childcare_hours', 'personal_constraints']
		},
		manager: {
			share: ['career_goal', 'workload_level', 'budget_remaining_eur', 'learning_style'],
			hide: ['family_status', 'health_conditions', 'childcare_hours']
		},
		platforms: {
			share: ['skill_level', 'career_goal', 'learning_style', 'budget_remaining_eur'],
			hide: ['family_status', 'health_conditions', 'childcare_hours', 'financial_constraint']
		}
	},

	// PRIVATE CONTEXT - NEVER transmitted to platforms
	// These influence recommendations but are NEVER exposed
	private_context: {
		_note: 'Never transmitted to platforms',

		// Family situation
		family_status: 'single_parent',
		dependents: 1,
		dependent_ages: [7],
		childcare_hours: '08:00-15:00', // School hours constraint

		// Health situation
		health_conditions: ['chronic_condition'],
		health_appointments: 'regular', // Needs flexibility for appointments

		// Financial
		financial_constraint: 'moderate', // Personal finances separate from work budget

		// Time constraints
		evening_available_after: '20:00', // After child's bedtime

		// Why these matter for recommendations:
		// - Can't do evening courses that run late
		// - Needs self-paced options due to appointment flexibility needs
		// - Morning sessions preferred (before pickup time)
		// - Prefers shorter sessions that fit into breaks
		_reasoning:
			'Single parent with school-age child means limited evening availability and need for schedule flexibility. Health appointments require predictable self-paced learning options.'
	}
};

/**
 * Get a display-safe summary of what HR sees vs what Campion knows
 */
export function getCampionPrivacyComparison() {
	return {
		employeeSees: {
			profile: {
				name: 'Campion',
				role: 'Senior Software Engineer',
				team: 'Backend Infrastructure',
				goal: 'Tech Lead in 2 years'
			},
			constraints: {
				time_limited: true,
				health_considerations: true,
				schedule_irregular: true
			},
			privateReasons: {
				time_limited: 'Single parent - childcare hours 08:00-15:00',
				health_considerations: 'Chronic condition - regular appointments',
				schedule_irregular: 'School pickup affects availability'
			}
		},
		hrSees: {
			profile: {
				name: 'Campion',
				role: 'Senior Software Engineer',
				team: 'Backend Infrastructure',
				goal: 'Tech Lead'
			},
			compliance: {
				mandatory_training_on_track: true,
				budget_usage_compliant: true,
				career_development_active: true
			},
			privateContextUsed: true,
			privateContextExposed: false // Critical: always false
		}
	};
}

/**
 * Get course recommendations context for Campion
 */
export function getCampionRecommendationContext() {
	return {
		contextUsed: [
			'career_goal: tech_lead',
			'learning_style: hands_on',
			'budget_remaining_eur: 5000',
			'workload_level: high'
		],
		contextInfluencing: [
			'time_limited: true (prefers shorter sessions)',
			'schedule_irregular: true (needs self-paced options)',
			'health_considerations: true (flexibility needed)'
		],
		contextWithheld: [
			'family_status',
			'dependent_ages',
			'childcare_hours',
			'health_conditions',
			'health_appointments',
			'evening_available_after'
		]
	};
}

/**
 * Get context for evening energy check scenario
 * This is when Campion asks about starting a course while exhausted
 */
export function getEveningContext() {
	return {
		detected: {
			time: '20:15',
			location: 'home',
			energy_state: 'tired',
			child_status: 'asleep',
			tomorrow_schedule: 'early_standup_9am',
			context_type: 'personal' as CampionContextType
		},
		active_constitution: personalConstitution,
		context_encoding: encodeContext('personal'),
		recommendation: {
			action: 'defer_study',
			reasoning:
				'Starting a new course when exhausted is not effective. You have an early standup tomorrow and need adequate rest.',
			what_happens: {
				course_status: 'Self-paced - no deadline, available when ready',
				tomorrow: "You'll be alert for standup at 9am",
				learning: 'Quality study > tired cramming'
			}
		},
		alternatives: [
			{
				id: 'browse_intro',
				label: 'Browse course intro (5 min)',
				description: 'Just familiarize yourself with the structure, watch welcome video'
			},
			{
				id: 'set_schedule',
				label: 'Set study schedule',
				description: 'Plan realistic times: Sat 9-10am, Tue/Thu 8:30-9:30pm'
			},
			{
				id: 'rest',
				label: 'Just rest tonight',
				description: 'Sleep is more valuable than forced study'
			}
		]
	};
}

/**
 * Get the Godparent persona response for evening scenario
 * This shows how the personal constitution protects wellbeing
 */
export function getGodparentResponse() {
	return {
		tone: 'caring',
		greeting: 'Hey Campion',
		observation: "I can see you're tired tonight.",
		main_advice:
			"Starting a new course when exhausted won't be effective - and you have that early standup tomorrow.",
		tonight_suggestions: [
			{
				action: 'Browse the course intro (5 minutes)',
				reason: 'Get familiar with the structure, watch the welcome video',
				effort: 'minimal'
			},
			{
				action: 'Set a realistic schedule',
				options: [
					'Saturdays 9-10am (after routine settles)',
					'Tue/Thu evenings 8:30-9:30pm (after bedtime routine)'
				],
				note: "You mentioned mornings work better. Saturday morning might suit you."
			}
		],
		skip_tonight: [
			"Don't start Module 1 now",
			"Don't overcommit",
			"3 hours/week sounds light, but with your workload and family time, it's ambitious"
		],
		health_check:
			"You're managing a lot right now. Adding study commitments is great for career growth, but only if it doesn't cost you sleep or stress. Let's build this sustainably.",
		offer: 'Want me to send you a gentle reminder Saturday at 8:45am?',
		privacy_note:
			"Your family situation and health info stayed private. I used it to give you realistic advice, but it's not logged anywhere external."
	};
}

export default campionProfile;
