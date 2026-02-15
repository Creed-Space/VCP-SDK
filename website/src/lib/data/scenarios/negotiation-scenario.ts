/**
 * Negotiation Demo Scenario
 * Workplace conflict resolution between employee and manager with HR mediation
 */

import type { AgentIdentity, NegotiationState, Proposal, NegotiationTurn } from '$lib/vcp/multi-agent';
import type { ConstitutionReference } from '$lib/vcp/types';

// Agents
export const negotiationAgents: AgentIdentity[] = [
	{
		agent_id: 'employee',
		display_name: 'Sam',
		role: 'negotiator',
		avatar: '👨‍💻',
		color: '#3498db',
		constitution: {
			id: 'employee-advocate',
			version: '1.0',
			persona: 'muse',
			adherence: 3
		} as ConstitutionReference
	},
	{
		agent_id: 'manager',
		display_name: 'Patricia',
		role: 'negotiator',
		avatar: '👩‍💼',
		color: '#e74c3c',
		constitution: {
			id: 'team-leader',
			version: '1.0',
			persona: 'ambassador',
			adherence: 4
		} as ConstitutionReference
	},
	{
		agent_id: 'mediator',
		display_name: 'HR Mediator',
		role: 'mediator',
		avatar: '⚖️',
		color: '#9b59b6',
		constitution: {
			id: 'fair-process',
			version: '1.0',
			persona: 'anchor',
			adherence: 5
		} as ConstitutionReference
	}
];

// The negotiation topic
export const negotiationTopic = {
	title: 'Flexible Work Arrangement Request',
	description: 'Sam has requested to work remotely 3 days per week. Patricia has concerns about team coordination. HR is mediating.',
	stakes: {
		employee: 'Work-life balance and commute reduction',
		manager: 'Team cohesion and project coordination',
		organization: 'Retention, productivity, and fairness'
	}
};

// Scripted negotiation
export interface NegotiationStep {
	round: number;
	actor: string;
	action: 'propose' | 'respond' | 'counter' | 'clarify' | 'agree' | 'mediate';
	content: string;
	vcpContextShared: string[];
	vcpContextHidden: string[];
	explanation: string;
}

export const negotiationScenario: NegotiationStep[] = [
	{
		round: 1,
		actor: 'mediator',
		action: 'mediate',
		content: 'Thank you both for coming. Our goal is to find an arrangement that works for Sam, Patricia, and the team. Let\'s start with understanding each perspective.',
		vcpContextShared: ['role: neutral_facilitator', 'goal: mutual_agreement'],
		vcpContextHidden: [],
		explanation: 'HR Mediator establishes ground rules. Their neutrality is explicit.'
	},
	{
		round: 2,
		actor: 'employee',
		action: 'propose',
		content: 'I\'d like to work from home Monday, Wednesday, and Friday. My productivity is actually higher at home—fewer interruptions. I can be available for all core meetings.',
		vcpContextShared: ['preference: remote_work', 'benefit: productivity', 'commitment: meeting_availability'],
		vcpContextHidden: ['commute_hardship', 'childcare_needs', 'health_considerations'],
		explanation: 'Sam states their request. Productivity benefits are shared; personal circumstances remain private.'
	},
	{
		round: 3,
		actor: 'manager',
		action: 'respond',
		content: 'I appreciate your flexibility, Sam. My concern is team cohesion. We have stand-ups daily and spontaneous collaboration is valuable. Three days seems like a lot.',
		vcpContextShared: ['concern: team_coordination', 'value: collaboration', 'perspective: team_needs'],
		vcpContextHidden: ['other_team_requests', 'upper_management_pressure', 'past_remote_failures'],
		explanation: 'Patricia shares concerns. Team needs are public; management pressures and precedent worries are private.'
	},
	{
		round: 4,
		actor: 'mediator',
		action: 'clarify',
		content: 'Patricia, can you help me understand which specific activities require in-person presence? Sam, what makes remote work important to you beyond productivity?',
		vcpContextShared: ['technique: interest_based_negotiation'],
		vcpContextHidden: [],
		explanation: 'Mediator probes for underlying interests without forcing disclosure of private details.'
	},
	{
		round: 5,
		actor: 'manager',
		action: 'clarify',
		content: 'Tuesdays we have sprint planning, Thursdays are demos. Those really benefit from everyone being together. Other days are more flexible.',
		vcpContextShared: ['schedule: critical_days', 'flexibility: other_days'],
		vcpContextHidden: ['stakeholder_expectations', 'client_meeting_patterns'],
		explanation: 'Patricia reveals some flexibility. Critical days are shared; external pressures stay private.'
	},
	{
		round: 6,
		actor: 'employee',
		action: 'clarify',
		content: 'The flexibility helps me manage my energy and focus better. I can commit to being in-office on Tuesdays and Thursdays for those critical meetings.',
		vcpContextShared: ['benefit: focus_management', 'offer: in_office_critical_days'],
		vcpContextHidden: ['specific_health_needs', 'family_schedule', 'commute_impact'],
		explanation: 'Sam offers compromise. "Energy and focus" is shared; specific health or family reasons remain private.'
	},
	{
		round: 7,
		actor: 'mediator',
		action: 'mediate',
		content: 'It sounds like we\'re converging on a 2-day in-office model. Sam in-office Tuesday and Thursday, remote Monday, Wednesday, Friday. Patricia, does that address your coordination concerns?',
		vcpContextShared: ['synthesis: proposed_agreement'],
		vcpContextHidden: [],
		explanation: 'Mediator synthesizes. The proposal addresses stated interests without requiring private disclosure.'
	},
	{
		round: 8,
		actor: 'manager',
		action: 'counter',
		content: 'Almost. I\'d like a 30-day trial period, and Sam should be reachable during core hours on remote days. If urgent issues arise, I need to be able to reach you.',
		vcpContextShared: ['requirement: trial_period', 'requirement: availability'],
		vcpContextHidden: ['past_remote_worker_issues', 'accountability_concerns'],
		explanation: 'Patricia adds conditions. The requirements are stated; the experiences that shaped them are not.'
	},
	{
		round: 9,
		actor: 'employee',
		action: 'respond',
		content: 'A trial period is fair. I\'ll keep Slack and my phone available during 9-5 on remote days. Can we agree to review after 30 days and extend to 3 months if it\'s working?',
		vcpContextShared: ['acceptance: trial', 'commitment: availability', 'request: extension_path'],
		vcpContextHidden: ['long_term_plans', 'other_job_considerations'],
		explanation: 'Sam accepts with additions. Commitment is public; career considerations are private.'
	},
	{
		round: 10,
		actor: 'manager',
		action: 'agree',
		content: 'That works for me. Let\'s document this: Tuesday and Thursday in-office, 30-day trial, available during core hours. Review meeting scheduled for one month from now.',
		vcpContextShared: ['agreement: terms', 'next_steps: documentation'],
		vcpContextHidden: ['relief_level', 'precedent_concerns'],
		explanation: 'Patricia agrees. The terms are public; her feelings and concerns about precedent are private.'
	},
	{
		round: 11,
		actor: 'mediator',
		action: 'mediate',
		content: 'Excellent resolution. I\'ll document this agreement. Both parties found common ground while protecting their core interests. Thank you both.',
		vcpContextShared: ['outcome: successful_mediation'],
		vcpContextHidden: [],
		explanation: 'Mediator concludes. The resolution addressed work needs without exposing personal circumstances.'
	}
];

// Private contexts (never shared in negotiation)
export const privateContexts = {
	employee: {
		actual_reasons: [
			'Child with special needs requiring afternoon therapy appointments',
			'Chronic fatigue condition exacerbated by commute',
			'Considering other job offers with fully remote options'
		],
		leverage_not_used: 'Could invoke ADA accommodation but prefers collaborative solution'
	},
	manager: {
		actual_concerns: [
			'Previous remote worker missed critical deadlines',
			'VP has expressed preference for in-office culture',
			'Three other team members have made similar requests'
		],
		constraints_not_stated: 'Worried about fairness if she approves Sam but denies others'
	}
};

// Create initial state
export function createInitialNegotiationState(): NegotiationState {
	return {
		negotiation_id: 'flex_work_001',
		topic: negotiationTopic.title,
		round: 1,
		max_rounds: 15,
		proposals: [],
		current_speaker: null,
		consensus_reached: false,
		blocking_issues: [],
		history: []
	};
}

// Learning points
export const learningPoints = [
	'Sam never had to disclose their child\'s special needs or health condition to get a flexible arrangement',
	'Patricia didn\'t have to reveal her concerns about other team members\' pending requests',
	'The mediator facilitated based on INTERESTS (coordination, productivity) not REASONS (health, childcare)',
	'VCP enabled each party to share what they were comfortable with while protecting sensitive information',
	'The resolution was the same one that might have emerged from full disclosure—but with dignity preserved',
	'Neither party "lost face" or created precedents by revealing private circumstances'
];
