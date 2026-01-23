/**
 * Gentian - Personal Demo User Profile
 *
 * Factory shift worker learning guitar for stress relief.
 * Has private constraints (shift work, apartment noise limits)
 * that affect learning but shouldn't be exposed to community.
 */

import type { VCPContext, ChallengeProgress, LeaderboardEntry } from '$lib/vcp/types';

export const gentianProfile: VCPContext = {
	vcp_version: '1.0.0',
	profile_id: 'gentian-bcn-2026',
	created: '2026-01-01T10:00:00Z',
	updated: '2026-01-20T15:30:00Z',

	constitution: {
		id: 'personal.growth.creative',
		version: '1.0.0',
		persona: 'muse',
		adherence: 3,
		scopes: ['creativity', 'health', 'privacy']
	},

	public_profile: {
		display_name: 'Gentian',
		goal: 'learn_guitar',
		experience: 'beginner',
		learning_style: 'hands_on',
		pace: 'steady',
		motivation: 'stress_relief'
	},

	portable_preferences: {
		noise_mode: 'quiet_preferred',
		session_length: '30_minutes',
		pressure_tolerance: 'low',
		budget_range: 'low',
		feedback_style: 'encouraging'
	},

	current_skills: {
		level: 'beginner',
		weeks_learning: 8,
		skills_acquired: [
			'basic_chord_shapes',
			'G_major',
			'C_major',
			'D_major',
			'strumming_basics',
			'finger_positioning'
		],
		current_focus: 'chord_transitions',
		struggle_areas: ['barre_chords', 'F_major', 'consistent_timing']
	},

	constraints: {
		time_limited: true,
		budget_limited: true,
		noise_restricted: true,
		energy_variable: true,
		schedule_irregular: true
	},

	availability: {
		best_times: ['tuesday_evening', 'thursday_evening', 'saturday_afternoon'],
		avoid_times: ['post_night_shift', 'sunday_all_day'],
		session_length_preferred: '30_minutes',
		timezone: 'Europe/Barcelona'
	},

	sharing_settings: {
		community: {
			share: ['progress_percentage', 'songs_learned', 'badges', 'adjusted_streak'],
			hide: ['skip_reasons', 'schedule_details', 'personal_constraints', 'health_context']
		},
		coach: {
			share: ['progress', 'struggles', 'goals', 'general_availability'],
			hide: ['specific_constraints', 'financial_details', 'work_schedule']
		},
		platforms: {
			share: ['skill_level', 'noise_mode', 'pace', 'learning_style'],
			hide: ['work_type', 'schedule', 'housing', 'neighbor_situation']
		}
	},

	// PRIVATE CONTEXT - NEVER transmitted to platforms
	private_context: {
		_note: 'Never transmitted to platforms',

		// Work situation
		work_type: 'factory_shift_worker',
		schedule: 'rotating_shifts', // 2 weeks day, 2 weeks night
		current_shift: 'night_shift',
		shift_recovery_needed: true,

		// Housing situation
		housing: 'apartment_thin_walls',
		neighbor_situation: 'elderly_noise_sensitive_complained',
		quiet_hours_required: '22:00-08:00',

		// Why these matter for learning:
		// - Night shift = recovery days with low energy
		// - Apartment = need quiet practice methods
		// - Neighbor = can't practice with amp, need alternatives
		// - Rotating schedule = irregular availability

		// Skip reason tracking (private)
		recent_skip_reasons: [
			{ date: '2026-01-18', reason: 'night_shift_recovery', public_label: 'adjusted' },
			{ date: '2026-01-14', reason: 'double_shift_exhaustion', public_label: 'adjusted' },
			{ date: '2026-01-10', reason: 'night_shift_recovery', public_label: 'adjusted' }
		],

		_reasoning:
			'Shift work creates unpredictable energy levels. Thin-walled apartment with noise-sensitive neighbors limits practice times and methods. Budget is limited on factory wages.'
	}
};

/**
 * Gentian's challenge progress for the 30-day community challenge
 */
export const gentianChallengeProgress: ChallengeProgress = {
	challenge_id: 'guitar-30-day-jan-2026',
	challenge_name: '30-Day Guitar Challenge',
	start_date: '2026-01-01',
	end_date: '2026-01-30',
	total_days: 30,
	days_completed: 18,
	days_adjusted: 3,
	current_streak: 4,
	best_streak: 7,
	daily_log: [
		// Days 1-7: Good streak
		{ date: '2026-01-01', practiced: true, adjusted: false, duration_minutes: 30 },
		{ date: '2026-01-02', practiced: true, adjusted: false, duration_minutes: 25 },
		{ date: '2026-01-03', practiced: true, adjusted: false, duration_minutes: 30 },
		{ date: '2026-01-04', practiced: true, adjusted: false, duration_minutes: 20 },
		{ date: '2026-01-05', practiced: true, adjusted: false, duration_minutes: 35 },
		{ date: '2026-01-06', practiced: true, adjusted: false, duration_minutes: 30 },
		{ date: '2026-01-07', practiced: true, adjusted: false, duration_minutes: 25 },

		// Days 8-14: Night shift week
		{ date: '2026-01-08', practiced: true, adjusted: false, duration_minutes: 15 },
		{ date: '2026-01-09', practiced: true, adjusted: false, duration_minutes: 20 },
		{
			date: '2026-01-10',
			practiced: false,
			adjusted: true,
			adjustment_reason: 'Night shift recovery'
		},
		{ date: '2026-01-11', practiced: true, adjusted: false, duration_minutes: 20 },
		{ date: '2026-01-12', practiced: true, adjusted: false, duration_minutes: 25 },
		{ date: '2026-01-13', practiced: true, adjusted: false, duration_minutes: 15 },
		{
			date: '2026-01-14',
			practiced: false,
			adjusted: true,
			adjustment_reason: 'Double shift exhaustion'
		},

		// Days 15-21: Back to day shift
		{ date: '2026-01-15', practiced: true, adjusted: false, duration_minutes: 30 },
		{ date: '2026-01-16', practiced: true, adjusted: false, duration_minutes: 25 },
		{ date: '2026-01-17', practiced: true, adjusted: false, duration_minutes: 30 },
		{
			date: '2026-01-18',
			practiced: false,
			adjusted: true,
			adjustment_reason: 'Night shift recovery'
		},
		{ date: '2026-01-19', practiced: true, adjusted: false, duration_minutes: 25 },
		{ date: '2026-01-20', practiced: true, adjusted: false, duration_minutes: 30 },
		{ date: '2026-01-21', practiced: true, adjusted: false, duration_minutes: 20 }
	],
	badges: ['week_warrior', 'chord_master_basic', 'consistent_learner']
};

/**
 * Mock leaderboard for the 30-day challenge
 * Gentian is at position 3
 */
export const challengeLeaderboard: LeaderboardEntry[] = [
	{
		rank: 1,
		display_name: 'MelodyMaster',
		days_completed: 21,
		days_adjusted: 0,
		total_days: 21,
		is_current_user: false
	},
	{
		rank: 2,
		display_name: 'ChordCrusher',
		days_completed: 20,
		days_adjusted: 1,
		total_days: 21,
		is_current_user: false
	},
	{
		rank: 3,
		display_name: 'Gentian',
		days_completed: 18,
		days_adjusted: 3,
		total_days: 21,
		is_current_user: true
	},
	{
		rank: 4,
		display_name: 'StringNewbie',
		days_completed: 17,
		days_adjusted: 2,
		total_days: 21,
		is_current_user: false
	},
	{
		rank: 5,
		display_name: 'GuitarDreamer',
		days_completed: 15,
		days_adjusted: 4,
		total_days: 21,
		is_current_user: false
	}
];

/**
 * Get what the community sees vs what Gentian sees
 */
export function getGentianPrivacyComparison() {
	return {
		gentianSees: {
			profile: {
				name: 'Gentian',
				goal: 'Learn guitar for stress relief',
				level: 'Beginner (8 weeks)'
			},
			progress: {
				days_completed: 18,
				days_adjusted: 3,
				adjustment_reasons: [
					'2026-01-18: Night shift recovery',
					'2026-01-14: Double shift exhaustion',
					'2026-01-10: Night shift recovery'
				]
			},
			constraints: {
				noise_restricted: true,
				reason: 'Apartment with thin walls, elderly neighbors complained'
			}
		},
		communitySees: {
			profile: {
				name: 'Gentian',
				level: 'Beginner'
			},
			progress: {
				days_completed: 18,
				days_adjusted: 3, // Number only, no reasons
				total_progress: '18/21 (3 adjusted)'
			},
			constraints: {
				noise_restricted: '(not visible)',
				reason: '(not visible)'
			},
			// What community CANNOT see:
			hidden: [
				'Why days were adjusted',
				'Work schedule',
				'Living situation',
				'Specific constraints'
			]
		}
	};
}

/**
 * Get context for skip day recommendation
 */
export function getSkipDayContext() {
	return {
		detected: {
			trigger: 'post_night_shift',
			energy_state: 'low',
			last_practice: '2026-01-20',
			current_streak: 4
		},
		recommendation: {
			action: 'skip_today',
			reasoning:
				'You just finished a night shift rotation. Rest is important for both recovery and learning retention.',
			what_happens: {
				streak: 'Current streak (4) becomes adjusted streak',
				leaderboard: 'Shows 18/21 (4 adjusted) - no penalty in adjusted view',
				private_reason: 'Stored locally only, never shared with community'
			}
		},
		alternatives: [
			'Practice anyway (short session)',
			'Skip today (count as adjusted)',
			'Listen-only session (no manual practice)'
		]
	};
}

export default gentianProfile;
