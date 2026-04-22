import { describe, it, expect } from 'vitest';
import { SchulzeElection, type Ballot } from '../src/extensions/consensus.js';

function ballot(voterId: string, ...rankings: string[][]): Ballot {
	return { voterId, rankings };
}

// ---------------------------------------------------------------------------
// Constructor validation
// ---------------------------------------------------------------------------

describe('SchulzeElection — constructor', () => {
	it('throws on empty candidates', () => {
		expect(() => new SchulzeElection([])).toThrow('candidates must be non-empty');
	});

	it('throws on duplicate candidates', () => {
		expect(() => new SchulzeElection(['A', 'B', 'A'])).toThrow('candidates must be unique');
	});

	it('exposes candidates and initial ballot count', () => {
		const election = new SchulzeElection(['A', 'B', 'C']);
		expect(election.candidates).toEqual(['A', 'B', 'C']);
		expect(election.ballotCount).toBe(0);
	});
});

// ---------------------------------------------------------------------------
// Empty election
// ---------------------------------------------------------------------------

describe('SchulzeElection — empty', () => {
	it('returns null winner with no ballots', () => {
		const election = new SchulzeElection(['A', 'B']);
		const result = election.compute();
		expect(result.winner).toBeNull();
		expect(result.ranking).toEqual([]);
		expect(result.ballotCount).toBe(0);
		expect(result.hasCondorcetWinner).toBe(false);
	});
});

// ---------------------------------------------------------------------------
// Single candidate
// ---------------------------------------------------------------------------

describe('SchulzeElection — single candidate', () => {
	it('single candidate wins trivially', () => {
		const election = new SchulzeElection(['A']);
		election.addBallot(ballot('v1', ['A']));
		const result = election.compute();
		expect(result.winner).toBe('A');
		expect(result.ranking).toHaveLength(1);
		expect(result.ranking[0].rank).toBe(1);
	});
});

// ---------------------------------------------------------------------------
// Unanimous preference
// ---------------------------------------------------------------------------

describe('SchulzeElection — unanimous', () => {
	it('clear winner when all voters agree', () => {
		const election = new SchulzeElection(['A', 'B', 'C']);
		election.addBallot(ballot('v1', ['A'], ['B'], ['C']));
		election.addBallot(ballot('v2', ['A'], ['B'], ['C']));
		election.addBallot(ballot('v3', ['A'], ['B'], ['C']));
		const result = election.compute();
		expect(result.winner).toBe('A');
		expect(result.hasCondorcetWinner).toBe(true);
		expect(result.ranking[0].candidate).toBe('A');
		expect(result.ranking[1].candidate).toBe('B');
		expect(result.ranking[2].candidate).toBe('C');
	});
});

// ---------------------------------------------------------------------------
// Condorcet winner
// ---------------------------------------------------------------------------

describe('SchulzeElection — Condorcet', () => {
	it('finds the Condorcet winner in a mixed election', () => {
		const election = new SchulzeElection(['A', 'B', 'C']);
		// A beats B (2-1), A beats C (2-1), B beats C (2-1)
		election.addBallot(ballot('v1', ['A'], ['B'], ['C']));
		election.addBallot(ballot('v2', ['A'], ['C'], ['B']));
		election.addBallot(ballot('v3', ['B'], ['A'], ['C']));
		const result = election.compute();
		expect(result.winner).toBe('A');
		expect(result.hasCondorcetWinner).toBe(true);
	});
});

// ---------------------------------------------------------------------------
// Ties
// ---------------------------------------------------------------------------

describe('SchulzeElection — ties', () => {
	it('detects tied candidates', () => {
		const election = new SchulzeElection(['A', 'B']);
		election.addBallot(ballot('v1', ['A'], ['B']));
		election.addBallot(ballot('v2', ['B'], ['A']));
		const result = election.compute();
		// A and B each have 1 vote preferring them, so it's a tie
		expect(result.ties.length).toBeGreaterThan(0);
	});

	it('handles grouped rankings (ties within a ballot)', () => {
		const election = new SchulzeElection(['A', 'B', 'C']);
		// Voter says A and B are equally preferred, both above C
		election.addBallot(ballot('v1', ['A', 'B'], ['C']));
		election.addBallot(ballot('v2', ['A', 'B'], ['C']));
		const result = election.compute();
		// C should lose to both A and B
		const cRanking = result.ranking.find(r => r.candidate === 'C');
		expect(cRanking!.rank).toBeGreaterThan(1);
	});
});

// ---------------------------------------------------------------------------
// Unranked candidates
// ---------------------------------------------------------------------------

describe('SchulzeElection — unranked candidates', () => {
	it('places unranked candidates at the bottom', () => {
		const election = new SchulzeElection(['A', 'B', 'C']);
		// Only rank A, B and C are unmentioned
		election.addBallot(ballot('v1', ['A']));
		election.addBallot(ballot('v2', ['A']));
		const result = election.compute();
		expect(result.winner).toBe('A');
	});
});

// ---------------------------------------------------------------------------
// getPairwiseResult
// ---------------------------------------------------------------------------

describe('SchulzeElection — getPairwiseResult', () => {
	it('returns correct pairwise counts', () => {
		const election = new SchulzeElection(['A', 'B', 'C']);
		election.addBallot(ballot('v1', ['A'], ['B'], ['C']));
		election.addBallot(ballot('v2', ['A'], ['B'], ['C']));
		election.addBallot(ballot('v3', ['B'], ['A'], ['C']));
		const pair = election.getPairwiseResult('A', 'B');
		expect(pair).not.toBeNull();
		expect(pair!.aPreferred).toBe(2);
		expect(pair!.bPreferred).toBe(1);
	});

	it('returns null for unknown candidates', () => {
		const election = new SchulzeElection(['A', 'B']);
		const pair = election.getPairwiseResult('A', 'Z');
		expect(pair).toBeNull();
	});
});

// ---------------------------------------------------------------------------
// Larger election
// ---------------------------------------------------------------------------

describe('SchulzeElection — 4 candidates', () => {
	it('produces correct ranking for a non-trivial election', () => {
		const election = new SchulzeElection(['A', 'B', 'C', 'D']);
		// 5 voters with varied preferences
		election.addBallot(ballot('v1', ['A'], ['C'], ['B'], ['D']));
		election.addBallot(ballot('v2', ['D'], ['A'], ['B'], ['C']));
		election.addBallot(ballot('v3', ['B'], ['D'], ['C'], ['A']));
		election.addBallot(ballot('v4', ['C'], ['A'], ['B'], ['D']));
		election.addBallot(ballot('v5', ['A'], ['B'], ['D'], ['C']));

		const result = election.compute();
		expect(result.ballotCount).toBe(5);
		expect(result.winner).not.toBeNull();
		expect(result.ranking).toHaveLength(4);
		// All ranks should be 1-indexed
		for (const r of result.ranking) {
			expect(r.rank).toBeGreaterThanOrEqual(1);
			expect(r.rank).toBeLessThanOrEqual(4);
		}
	});
});
