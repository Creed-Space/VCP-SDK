/**
 * Policy Design Demo Scenario
 * Community voting on a local park renovation with different stakeholder priorities
 */

import type { AgentIdentity, PolicyDesignContext, PolicyOption, Vote, DeliberationEntry } from '$lib/vcp/multi-agent';
import type { ConstitutionReference } from '$lib/vcp/types';

// Agents
export const policyAgents: AgentIdentity[] = [
	{
		agent_id: 'parent_rep',
		display_name: 'Maria',
		role: 'voter',
		avatar: '👨‍👩‍👧',
		color: '#e74c3c',
		constitution: {
			id: 'family-advocate',
			version: '1.0',
			persona: 'godparent',
			adherence: 4
		} as ConstitutionReference
	},
	{
		agent_id: 'elder_rep',
		display_name: 'Harold',
		role: 'voter',
		avatar: '🧓',
		color: '#3498db',
		constitution: {
			id: 'accessibility-first',
			version: '1.0',
			persona: 'sentinel',
			adherence: 4
		} as ConstitutionReference
	},
	{
		agent_id: 'youth_rep',
		display_name: 'Jordan',
		role: 'voter',
		avatar: '🏃',
		color: '#2ecc71',
		constitution: {
			id: 'active-lifestyle',
			version: '1.0',
			persona: 'muse',
			adherence: 3
		} as ConstitutionReference
	},
	{
		agent_id: 'nature_rep',
		display_name: 'Sage',
		role: 'voter',
		avatar: '🌳',
		color: '#27ae60',
		constitution: {
			id: 'environmental-steward',
			version: '1.0',
			persona: 'sentinel',
			adherence: 5
		} as ConstitutionReference
	},
	{
		agent_id: 'moderator',
		display_name: 'Council Chair',
		role: 'mediator',
		avatar: '⚖️',
		color: '#9b59b6',
		constitution: {
			id: 'fair-process',
			version: '1.0',
			persona: 'ambassador',
			adherence: 5
		} as ConstitutionReference
	}
];

// Policy Options
export const policyOptions: PolicyOption[] = [
	{
		id: 'option_playground',
		name: 'Playground Expansion',
		description: 'Expand the children\'s playground with new equipment and safety surfacing.',
		proposer: 'parent_rep',
		pros: ['Safe play space for children', 'Encourages family visits', 'Modern equipment'],
		cons: ['Limited appeal to other age groups', 'Higher maintenance costs'],
		vcp_aligned_with: ['family_safety', 'community_gathering', 'child_development']
	},
	{
		id: 'option_fitness',
		name: 'Fitness Trail',
		description: 'Install an outdoor fitness trail with exercise stations around the park perimeter.',
		proposer: 'youth_rep',
		pros: ['Free exercise option', 'Appeals to all ages', 'Low maintenance'],
		cons: ['Reduces green space', 'May attract crowds'],
		vcp_aligned_with: ['health_wellness', 'accessibility', 'community_fitness']
	},
	{
		id: 'option_garden',
		name: 'Community Garden',
		description: 'Convert a section to community garden plots with a small greenhouse.',
		proposer: 'nature_rep',
		pros: ['Environmental education', 'Fresh produce', 'Community bonding'],
		cons: ['Ongoing management needed', 'Limited participants'],
		vcp_aligned_with: ['environmental_stewardship', 'food_security', 'education']
	},
	{
		id: 'option_accessible',
		name: 'Accessibility Upgrade',
		description: 'Add paved paths, benches, shade structures, and accessible facilities throughout.',
		proposer: 'elder_rep',
		pros: ['Inclusive for all abilities', 'Improves existing amenities', 'Benefits everyone'],
		cons: ['Less "new" appeal', 'May seem incremental'],
		vcp_aligned_with: ['accessibility', 'dignity', 'universal_design']
	}
];

// Scripted deliberation
export interface PolicyStep {
	round: number;
	actor: string;
	action: 'speak' | 'vote' | 'amend' | 'call_vote';
	content: string;
	sentiment?: 'support' | 'oppose' | 'question' | 'neutral';
	referencesOption?: string;
	vcpContextShared: string[];
	vcpContextHidden: string[];
	explanation: string;
}

export const policyScenario: PolicyStep[] = [
	{
		round: 1,
		actor: 'moderator',
		action: 'speak',
		content: 'Welcome to the park renovation deliberation. We have $150,000 budget and four proposals. Let\'s hear from each advocate.',
		sentiment: 'neutral',
		vcpContextShared: ['budget', 'process_rules'],
		vcpContextHidden: [],
		explanation: 'Moderator sets context. Budget and rules are shared with all.'
	},
	{
		round: 2,
		actor: 'parent_rep',
		action: 'speak',
		content: 'The playground is the heart of our family community. Safe, engaging play equipment brings families together daily.',
		sentiment: 'support',
		referencesOption: 'option_playground',
		vcpContextShared: ['priority: family_safety', 'goal: community_gathering'],
		vcpContextHidden: ['personal_family_situation', 'specific_safety_concerns'],
		explanation: 'Maria advocates for playground. Her family focus is visible; personal family details are private.'
	},
	{
		round: 3,
		actor: 'elder_rep',
		action: 'speak',
		content: 'Before we add new features, we should ensure everyone can access what we have. Many neighbors can\'t navigate the current paths.',
		sentiment: 'support',
		referencesOption: 'option_accessible',
		vcpContextShared: ['priority: accessibility', 'value: inclusion'],
		vcpContextHidden: ['personal_mobility_challenges', 'health_conditions'],
		explanation: 'Harold speaks for accessibility. His advocacy is public; any personal mobility issues remain private.'
	},
	{
		round: 4,
		actor: 'youth_rep',
		action: 'speak',
		content: 'A fitness trail gives everyone a free gym. It\'s not just for young people—I see folks of all ages who would use it.',
		sentiment: 'support',
		referencesOption: 'option_fitness',
		vcpContextShared: ['priority: health_wellness', 'goal: active_community'],
		vcpContextHidden: ['personal_fitness_routine', 'gym_membership_status'],
		explanation: 'Jordan promotes fitness. Their health values are shared; personal workout habits are not.'
	},
	{
		round: 5,
		actor: 'nature_rep',
		action: 'speak',
		content: 'A community garden teaches sustainability, provides fresh food, and creates green jobs for local youth.',
		sentiment: 'support',
		referencesOption: 'option_garden',
		vcpContextShared: ['priority: environmental_education', 'value: sustainability'],
		vcpContextHidden: ['personal_gardening_experience', 'dietary_preferences'],
		explanation: 'Sage advocates for garden. Environmental values are visible; personal practices are private.'
	},
	{
		round: 6,
		actor: 'elder_rep',
		action: 'speak',
		content: 'I want to support the playground, but only if it includes accessible paths and seating for grandparents.',
		sentiment: 'question',
		referencesOption: 'option_playground',
		vcpContextShared: ['condition: accessibility_integration'],
		vcpContextHidden: ['personal_grandparent_role'],
		explanation: 'Harold offers conditional support. His requirement is public; personal family role is private.'
	},
	{
		round: 7,
		actor: 'parent_rep',
		action: 'amend',
		content: 'I propose we combine: Playground with accessible paths and seating areas. Grandparents should enjoy watching their grandchildren safely.',
		referencesOption: 'option_playground',
		vcpContextShared: ['compromise: integrated_design'],
		vcpContextHidden: ['personal_parent_experiences'],
		explanation: 'Maria proposes integration. The compromise is public; personal parenting experiences are private.'
	},
	{
		round: 8,
		actor: 'youth_rep',
		action: 'speak',
		content: 'Could the fitness trail connect to the playground? Parents could exercise while kids play.',
		sentiment: 'support',
		vcpContextShared: ['suggestion: multi_use_design'],
		vcpContextHidden: ['personal_childcare_constraints'],
		explanation: 'Jordan suggests synergy. The design idea is shared; any personal constraints are not.'
	},
	{
		round: 9,
		actor: 'nature_rep',
		action: 'speak',
		content: 'What if the garden plots were along the fitness trail? Exercise stations with educational signage about plants.',
		sentiment: 'neutral',
		vcpContextShared: ['integration: education_wellness'],
		vcpContextHidden: ['personal_teaching_background'],
		explanation: 'Sage proposes integration. The concept is public; personal expertise is private.'
	},
	{
		round: 10,
		actor: 'moderator',
		action: 'speak',
		content: 'We\'re seeing convergence toward an integrated design. Let me propose a combined option: Accessible paths connecting playground, fitness stations, and small garden area.',
		sentiment: 'neutral',
		vcpContextShared: ['synthesis: combined_proposal'],
		vcpContextHidden: [],
		explanation: 'Moderator synthesizes. The combined proposal emerges from shared preferences.'
	},
	{
		round: 11,
		actor: 'moderator',
		action: 'call_vote',
		content: 'All in favor of the integrated park design with accessible playground, fitness trail, and community garden section?',
		vcpContextShared: ['process: final_vote'],
		vcpContextHidden: [],
		explanation: 'Vote called on synthesized option that addresses multiple stakeholder values.'
	}
];

// Votes (final outcome)
export const finalVotes: Vote[] = [
	{
		voter: 'parent_rep',
		option_id: 'integrated',
		timestamp: new Date().toISOString(),
		public_rationale: 'This gives our families a safe, accessible play area with room to grow.',
		private_rationale: 'My daughter with mobility challenges can finally play with her friends'
	},
	{
		voter: 'elder_rep',
		option_id: 'integrated',
		timestamp: new Date().toISOString(),
		public_rationale: 'The accessibility focus is maintained while adding new amenities.',
		private_rationale: 'I can finally take my walker to watch the grandkids'
	},
	{
		voter: 'youth_rep',
		option_id: 'integrated',
		timestamp: new Date().toISOString(),
		public_rationale: 'Free fitness for everyone, plus connected community spaces.',
		private_rationale: 'Saves me $50/month gym membership'
	},
	{
		voter: 'nature_rep',
		option_id: 'integrated',
		timestamp: new Date().toISOString(),
		public_rationale: 'The garden section provides environmental education within an active park.',
		private_rationale: 'Smaller than I hoped, but better than nothing'
	}
];

// Create initial state
export function createInitialPolicyState(): PolicyDesignContext {
	return {
		policy_id: 'park_renovation_2026',
		title: 'Riverside Park Renovation',
		description: 'Allocate $150,000 budget for park improvements. Choose one primary focus or propose integration.',
		options: policyOptions,
		participants: policyAgents.filter(a => a.role === 'voter'),
		voting_method: 'consensus',
		votes: [],
		deliberation: [],
		status: 'deliberation'
	};
}

// Learning points
export const learningPoints = [
	'Each stakeholder shared their VALUES and PRIORITIES publicly (family safety, accessibility, health, environment)',
	'PERSONAL REASONS for those priorities remained private (health conditions, family situations, financial constraints)',
	'The moderator could synthesize a compromise because they understood what each party valued',
	'Private rationales (elderly rep\'s mobility issues, parent\'s daughter\'s disability) never entered the public record',
	'VCP enabled preference aggregation while protecting the dignity of each participant\'s personal circumstances'
];
