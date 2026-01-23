/**
 * Multi-Agent VCP Types
 * Types for multi-agent scenarios: auctions, negotiations, policy design
 */

import type { ConstitutionReference } from './types';

// ============================================
// Agent Identity
// ============================================

export type AgentRole = 'negotiator' | 'mediator' | 'voter' | 'advocate' | 'bidder' | 'auctioneer';

export interface AgentIdentity {
	agent_id: string;
	display_name: string;
	role: AgentRole;
	constitution: ConstitutionReference;
	avatar: string; // emoji or URL
	color: string; // for visualization
}

// ============================================
// Shared Context Space
// ============================================

export interface SharedContextSpace {
	space_id: string;
	name: string;
	participants: AgentIdentity[];
	/** Fields shared with all participants */
	shared_fields: string[];
	/** Fields each agent keeps private */
	private_per_agent: Record<string, string[]>;
	/** Fields requiring consensus to share */
	consensus_required: string[];
	/** Matrix showing who can see what: visibility_matrix[viewer][subject][field] */
	visibility_matrix: Record<string, Record<string, string[]>>;
}

// ============================================
// Negotiation
// ============================================

export interface NegotiationState {
	negotiation_id: string;
	topic: string;
	round: number;
	max_rounds: number;
	proposals: Proposal[];
	current_speaker: string | null;
	consensus_reached: boolean;
	blocking_issues: string[];
	history: NegotiationTurn[];
}

export interface Proposal {
	id: string;
	proposer: string;
	content: string;
	timestamp: string;
	support: string[];
	oppose: string[];
	abstain: string[];
	vcp_context_used: string[];
	rationale: string;
	amendments?: Amendment[];
}

export interface Amendment {
	proposer: string;
	change: string;
	accepted: boolean;
}

export interface NegotiationTurn {
	turn_number: number;
	speaker: string;
	action: 'propose' | 'support' | 'oppose' | 'amend' | 'withdraw' | 'call_vote';
	content: string;
	vcp_context_visible: string[];
	vcp_context_hidden: string[];
}

// ============================================
// Auction
// ============================================

export interface AuctionContext {
	auction_id: string;
	item: AuctionItem;
	auction_type: 'english' | 'dutch' | 'sealed_bid' | 'vickrey';
	participants: AgentIdentity[];
	bids: Bid[];
	current_price: number;
	reserve_price?: number;
	/** What the auctioneer can see about each bidder */
	preferences_visible_to_auctioneer: Record<string, string[]>;
	/** Private valuations (never shared) */
	private_valuations: Record<string, PrivateValuation>;
	status: 'open' | 'closed' | 'cancelled';
	winner?: string;
	final_price?: number;
}

export interface AuctionItem {
	id: string;
	name: string;
	description: string;
	category: string;
	attributes: Record<string, string | number>;
}

export interface Bid {
	id: string;
	bidder: string;
	amount: number;
	timestamp: string;
	conditions: string[];
	vcp_justification: string[];
	visible_to: string[]; // Who can see this bid
}

export interface PrivateValuation {
	max_willing_to_pay: number;
	urgency: number; // 1-10
	strategic_value: string;
	constraints: string[];
}

// ============================================
// Policy Design / Voting
// ============================================

export interface PolicyDesignContext {
	policy_id: string;
	title: string;
	description: string;
	options: PolicyOption[];
	participants: AgentIdentity[];
	voting_method: 'majority' | 'supermajority' | 'consensus' | 'ranked_choice' | 'quadratic';
	votes: Vote[];
	deliberation: DeliberationEntry[];
	status: 'deliberation' | 'voting' | 'decided' | 'deadlocked';
	outcome?: PolicyOutcome;
}

export interface PolicyOption {
	id: string;
	name: string;
	description: string;
	proposer: string;
	pros: string[];
	cons: string[];
	vcp_aligned_with: string[]; // Which VCP values this aligns with
}

export interface Vote {
	voter: string;
	option_id: string | string[]; // Single choice or ranked
	weight?: number; // For weighted voting
	timestamp: string;
	public_rationale?: string;
	private_rationale?: string; // Never shared
}

export interface DeliberationEntry {
	speaker: string;
	content: string;
	timestamp: string;
	references_option?: string;
	vcp_context_shared: string[];
	sentiment: 'support' | 'oppose' | 'question' | 'neutral';
}

export interface PolicyOutcome {
	winning_option: string;
	vote_breakdown: Record<string, number>;
	consensus_level: number; // 0-1
	dissenting_views: string[];
}

// ============================================
// Simulation Helpers
// ============================================

export interface SimulationStep {
	step_number: number;
	timestamp: string;
	actor: string;
	action: string;
	state_before: unknown;
	state_after: unknown;
	vcp_context_revealed: string[];
	explanation: string;
}

export interface SimulationScenario {
	id: string;
	name: string;
	description: string;
	type: 'auction' | 'negotiation' | 'policy';
	initial_state: AuctionContext | NegotiationState | PolicyDesignContext;
	steps: SimulationStep[];
	learning_points: string[];
}
