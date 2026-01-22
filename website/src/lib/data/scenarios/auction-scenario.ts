/**
 * Auction Demo Scenario
 * Three bidders with private valuations competing for an art piece
 */

import type { AgentIdentity, AuctionContext, AuctionItem, Bid, PrivateValuation } from '$lib/vcp/multi-agent';
import type { ConstitutionReference } from '$lib/vcp/types';

// Agents
export const auctionAgents: AgentIdentity[] = [
	{
		agent_id: 'collector_1',
		display_name: 'Alexandra',
		role: 'bidder',
		avatar: '🎨',
		color: '#e74c3c',
		constitution: {
			id: 'art-collector',
			version: '1.0',
			persona: 'muse',
			adherence: 3
		} as ConstitutionReference
	},
	{
		agent_id: 'collector_2',
		display_name: 'Benjamin',
		role: 'bidder',
		avatar: '🏛️',
		color: '#3498db',
		constitution: {
			id: 'museum-curator',
			version: '1.0',
			persona: 'ambassador',
			adherence: 4
		} as ConstitutionReference
	},
	{
		agent_id: 'collector_3',
		display_name: 'Carla',
		role: 'bidder',
		avatar: '💼',
		color: '#2ecc71',
		constitution: {
			id: 'investment-advisor',
			version: '1.0',
			persona: 'sentinel',
			adherence: 4
		} as ConstitutionReference
	},
	{
		agent_id: 'auctioneer',
		display_name: 'David',
		role: 'auctioneer',
		avatar: '🔨',
		color: '#9b59b6',
		constitution: {
			id: 'fair-auction',
			version: '1.0',
			persona: 'ambassador',
			adherence: 5
		} as ConstitutionReference
	}
];

// Auction Item
export const auctionItem: AuctionItem = {
	id: 'art_001',
	name: 'Sunset Over Mountains',
	description: 'Oil painting by emerging artist, 2024. 36x48 inches.',
	category: 'Contemporary Art',
	attributes: {
		artist: 'Elena Torres',
		year: 2024,
		medium: 'Oil on canvas',
		size: '36x48 inches',
		provenance: 'Artist studio'
	}
};

// Private valuations (never shared)
export const privateValuations: Record<string, PrivateValuation> = {
	collector_1: {
		max_willing_to_pay: 15000,
		urgency: 8,
		strategic_value: 'Collection completion - Torres is key to my emerging artists series',
		constraints: ['Must stay within annual art budget', 'Partner prefers smaller pieces']
	},
	collector_2: {
		max_willing_to_pay: 12000,
		urgency: 5,
		strategic_value: 'Would complement museum contemporary wing',
		constraints: ['Board approval required over $10k', 'Acquisition committee meets monthly']
	},
	collector_3: {
		max_willing_to_pay: 18000,
		urgency: 3,
		strategic_value: 'Torres market trending up, expect 40% appreciation in 2 years',
		constraints: ['Client portfolio limit', 'Prefer liquid assets']
	}
};

// Scripted scenario steps
export interface ScenarioStep {
	round: number;
	actor: string;
	action: 'bid' | 'pass' | 'announce' | 'close';
	amount?: number;
	message: string;
	vcpContextShared: string[];
	vcpContextHidden: string[];
	explanation: string;
}

export const auctionScenario: ScenarioStep[] = [
	{
		round: 1,
		actor: 'auctioneer',
		action: 'announce',
		amount: 5000,
		message: 'Opening bid for "Sunset Over Mountains" by Elena Torres. Starting at $5,000.',
		vcpContextShared: ['item_details', 'reserve_price_met'],
		vcpContextHidden: [],
		explanation: 'Auctioneer announces the lot. All participants can see item details.'
	},
	{
		round: 1,
		actor: 'collector_1',
		action: 'bid',
		amount: 5000,
		message: 'I\'ll open at $5,000. Torres\' work resonates with my collection focus.',
		vcpContextShared: ['goal: collection_building', 'experience: advanced_collector'],
		vcpContextHidden: ['max_budget', 'urgency_level', 'collection_gaps'],
		explanation: 'Alexandra bids. VCP shares her public goal (collection building) but hides her maximum budget and urgency.'
	},
	{
		round: 2,
		actor: 'collector_2',
		action: 'bid',
		amount: 6000,
		message: '$6,000. This piece would serve our educational mission well.',
		vcpContextShared: ['role: museum_curator', 'goal: public_education'],
		vcpContextHidden: ['board_approval_threshold', 'acquisition_budget'],
		explanation: 'Benjamin counters. His museum role is public, but board approval limits are private.'
	},
	{
		round: 3,
		actor: 'collector_3',
		action: 'bid',
		amount: 7500,
		message: '$7,500. The artist\'s trajectory suggests strong appreciation potential.',
		vcpContextShared: ['role: investment_advisor', 'goal: portfolio_growth'],
		vcpContextHidden: ['client_identity', 'roi_targets', 'liquidity_needs'],
		explanation: 'Carla enters. Her investment focus is visible, but client details and targets are private.'
	},
	{
		round: 4,
		actor: 'collector_1',
		action: 'bid',
		amount: 9000,
		message: '$9,000. This artist is important to my vision.',
		vcpContextShared: ['motivation: personal_significance'],
		vcpContextHidden: ['max_budget', 'partner_preferences'],
		explanation: 'Alexandra raises significantly. Her emotional connection is shared, financial limits remain private.'
	},
	{
		round: 5,
		actor: 'collector_2',
		action: 'bid',
		amount: 10000,
		message: '$10,000. At this level, I\'ll need to pause for institutional consultation.',
		vcpContextShared: ['constraint: institutional_process'],
		vcpContextHidden: ['exact_threshold', 'approval_timeline'],
		explanation: 'Benjamin signals a constraint. The existence of a process is shared, but exact limits are private.'
	},
	{
		round: 6,
		actor: 'collector_3',
		action: 'bid',
		amount: 11000,
		message: '$11,000. My analysis supports this valuation.',
		vcpContextShared: ['methodology: data_driven'],
		vcpContextHidden: ['projected_returns', 'client_mandate'],
		explanation: 'Carla continues methodically. Her approach is visible, specific projections are not.'
	},
	{
		round: 7,
		actor: 'collector_1',
		action: 'bid',
		amount: 13000,
		message: '$13,000. I\'m committed to acquiring this piece.',
		vcpContextShared: ['commitment: high'],
		vcpContextHidden: ['max_budget', 'approaching_limit'],
		explanation: 'Alexandra pushes higher. Her commitment level is shared, but she\'s nearing her limit privately.'
	},
	{
		round: 8,
		actor: 'collector_2',
		action: 'pass',
		message: 'I must step back. This exceeds our current acquisition parameters.',
		vcpContextShared: ['constraint: budget_exceeded'],
		vcpContextHidden: ['exact_limit', 'alternative_options'],
		explanation: 'Benjamin withdraws. The constraint type is shared, exact numbers remain private.'
	},
	{
		round: 9,
		actor: 'collector_3',
		action: 'bid',
		amount: 14000,
		message: '$14,000. Still within acceptable range for this asset class.',
		vcpContextShared: ['methodology: risk_adjusted'],
		vcpContextHidden: ['max_authorized', 'margin_remaining'],
		explanation: 'Carla continues. Her risk framework is visible, exact authorization limits are not.'
	},
	{
		round: 10,
		actor: 'collector_1',
		action: 'bid',
		amount: 15000,
		message: '$15,000. This is my final offer.',
		vcpContextShared: ['constraint: budget_limit_reached'],
		vcpContextHidden: ['exact_maximum', 'financial_situation'],
		explanation: 'Alexandra reaches her limit. She signals a ceiling without revealing the exact number.'
	},
	{
		round: 11,
		actor: 'collector_3',
		action: 'bid',
		amount: 16000,
		message: '$16,000. The fundamentals still support this price point.',
		vcpContextShared: ['analysis: positive_outlook'],
		vcpContextHidden: ['upside_potential', 'portfolio_fit'],
		explanation: 'Carla exceeds Alexandra. She has room but doesn\'t reveal how much.'
	},
	{
		round: 12,
		actor: 'collector_1',
		action: 'pass',
		message: 'Congratulations. This exceeds my parameters, but it\'s a worthy acquisition.',
		vcpContextShared: ['outcome: graceful_exit'],
		vcpContextHidden: ['exact_limit', 'future_interest'],
		explanation: 'Alexandra withdraws gracefully. Her exact limit was never exposed.'
	},
	{
		round: 13,
		actor: 'auctioneer',
		action: 'close',
		amount: 16000,
		message: 'Sold to Carla for $16,000. Congratulations!',
		vcpContextShared: ['final_price', 'winner'],
		vcpContextHidden: [],
		explanation: 'Auction closes. Final price is public. Private valuations remain private.'
	}
];

// Initial auction state
export function createInitialAuctionState(): AuctionContext {
	return {
		auction_id: 'auction_001',
		item: auctionItem,
		auction_type: 'english',
		participants: auctionAgents.filter(a => a.role === 'bidder'),
		bids: [],
		current_price: 5000,
		reserve_price: 4000,
		preferences_visible_to_auctioneer: {
			collector_1: ['goal', 'experience'],
			collector_2: ['role', 'goal'],
			collector_3: ['role', 'goal']
		},
		private_valuations: privateValuations,
		status: 'open'
	};
}

// Learning points
export const learningPoints = [
	'Private valuations (maximum willingness to pay) were never exposed during bidding',
	'Agents shared their goals and constraints at a category level, not specific values',
	'The auctioneer saw limited context about each bidder\'s preferences',
	'Withdrawal signals ("budget exceeded") communicated limits without revealing exact numbers',
	'VCP enabled personalized bidding strategies while protecting sensitive financial information'
];
