/**
 * Campion - Professional Demo User Profile
 *
 * Senior software engineer at TechCorp, aspiring Tech Lead.
 * Has private constraints (single parent, health appointments)
 * that influence recommendations but are never exposed to HR.
 */

import type { VCPContext } from '$lib/vcp/types';

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

export default campionProfile;
