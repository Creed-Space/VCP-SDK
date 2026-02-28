/**
 * VCP 3.1 Schulze Voting Method
 *
 * Computes the strongest-path winner from ranked preference ballots.
 * Condorcet-consistent, clone-independent. Used by Debian, Wikimedia, and Creed Space.
 *
 * Algorithm:
 * 1. Build pairwise defeat matrix d[i][j] = ballots preferring i over j
 * 2. Compute strongest paths p[i][j] via modified Floyd-Warshall
 * 3. Rank candidates: i beats j iff p[i][j] > p[j][i]
 *
 * Produces identical results to the Python SDK for the same inputs.
 */

// === Interfaces ===

export interface Ballot {
  readonly voterId: string;
  /**
   * Ordered list of candidate groups, best-first.
   * Each inner array contains candidates of equal preference (ties).
   * Example: [["A"], ["B", "C"], ["D"]] means A > B=C > D.
   * For simple rankings without ties: [["A"], ["B"], ["C"]].
   *
   * This format matches the Python and Rust SDKs for cross-SDK parity.
   */
  readonly rankings: readonly (readonly string[])[];
}

export interface SchulzeRanking {
  readonly candidate: string;
  /** 1-indexed rank, ties possible */
  readonly rank: number;
  readonly wins: number;
  readonly losses: number;
}

export interface PairwiseResult {
  readonly candidateA: string;
  readonly candidateB: string;
  readonly aPreferred: number;
  readonly bPreferred: number;
}

export interface ElectionResult {
  readonly winner: string | null;
  readonly ranking: readonly SchulzeRanking[];
  readonly pairwiseMatrix: readonly (readonly number[])[];
  readonly strongestPaths: readonly (readonly number[])[];
  readonly candidates: readonly string[];
  readonly ballotCount: number;
  readonly hasCondorcetWinner: boolean;
  readonly ties: readonly (readonly [string, string])[];
}

// === Schulze Election Class ===

export class SchulzeElection {
  private readonly _candidates: readonly string[];
  private readonly _ballots: Ballot[] = [];
  private readonly _index: ReadonlyMap<string, number>;

  constructor(candidates: readonly string[]) {
    if (candidates.length === 0) {
      throw new Error('candidates must be non-empty');
    }
    if (new Set(candidates).size !== candidates.length) {
      throw new Error('candidates must be unique');
    }
    this._candidates = [...candidates];
    this._index = new Map(candidates.map((c, i) => [c, i]));
  }

  get candidates(): readonly string[] {
    return this._candidates;
  }

  get ballotCount(): number {
    return this._ballots.length;
  }

  addBallot(ballot: Ballot): void {
    this._ballots.push(ballot);
  }

  compute(): ElectionResult {
    const n = this._candidates.length;

    if (this._ballots.length === 0) {
      return {
        winner: null,
        ranking: [],
        pairwiseMatrix: this._emptyMatrix(n),
        strongestPaths: this._emptyMatrix(n),
        candidates: [...this._candidates],
        ballotCount: 0,
        hasCondorcetWinner: false,
        ties: [],
      };
    }

    const d = this._buildPairwiseMatrix();
    const p = this._computeStrongestPaths(d);
    const { ranking, ties } = this._determineRanking(p);

    const winner = ranking.length > 0 ? ranking[0].candidate : null;
    const hasCondorcet = winner !== null ? this._checkCondorcet(d, winner) : false;

    return {
      winner,
      ranking,
      pairwiseMatrix: d,
      strongestPaths: p,
      candidates: [...this._candidates],
      ballotCount: this._ballots.length,
      hasCondorcetWinner: hasCondorcet,
      ties,
    };
  }

  /**
   * Get pairwise comparison between two specific candidates.
   * Must be called after compute() for meaningful results.
   */
  getPairwiseResult(candidateA: string, candidateB: string): PairwiseResult | null {
    const ia = this._index.get(candidateA);
    const ib = this._index.get(candidateB);
    if (ia === undefined || ib === undefined) return null;

    const d = this._buildPairwiseMatrix();
    return {
      candidateA,
      candidateB,
      aPreferred: d[ia][ib],
      bPreferred: d[ib][ia],
    };
  }

  // === Private Methods ===

  private _emptyMatrix(n: number): number[][] {
    return Array.from({ length: n }, () => Array.from({ length: n }, () => 0));
  }

  private _buildPairwiseMatrix(): number[][] {
    const n = this._candidates.length;
    const d = this._emptyMatrix(n);

    for (const ballot of this._ballots) {
      this._applyGroupedBallot(d, ballot);
    }

    return d;
  }

  private _applyGroupedBallot(d: number[][], ballot: Ballot): void {
    const n = this._candidates.length;
    const position = new Map<string, number>();
    let rank = 0;

    for (const group of ballot.rankings) {
      for (const cid of group) {
        if (this._index.has(cid)) {
          position.set(cid, rank);
        }
      }
      rank++;
    }

    // Unranked candidates at the bottom
    for (const cid of this._candidates) {
      if (!position.has(cid)) {
        position.set(cid, rank);
      }
    }

    for (let i = 0; i < n; i++) {
      for (let j = i + 1; j < n; j++) {
        const ci = this._candidates[i];
        const cj = this._candidates[j];
        const pi = position.get(ci)!;
        const pj = position.get(cj)!;
        if (pi < pj) {
          d[i][j] += 1;
        } else if (pj < pi) {
          d[j][i] += 1;
        }
      }
    }
  }

  private _computeStrongestPaths(d: number[][]): number[][] {
    const n = this._candidates.length;
    const p = this._emptyMatrix(n);

    // Initialize: direct edges where i beats j
    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n; j++) {
        if (i !== j && d[i][j] > d[j][i]) {
          p[i][j] = d[i][j];
        }
      }
    }

    // Floyd-Warshall: strongest path = max over intermediaries of
    // min(strength to intermediate, intermediate to target)
    for (let k = 0; k < n; k++) {
      for (let i = 0; i < n; i++) {
        if (i === k) continue;
        for (let j = 0; j < n; j++) {
          if (j === i || j === k) continue;
          const viaK = Math.min(p[i][k], p[k][j]);
          if (viaK > p[i][j]) {
            p[i][j] = viaK;
          }
        }
      }
    }

    return p;
  }

  private _determineRanking(
    p: number[][],
  ): { ranking: SchulzeRanking[]; ties: [string, string][] } {
    const n = this._candidates.length;
    const rawTies: [string, string][] = [];

    const wins = new Array(n).fill(0);
    const losses = new Array(n).fill(0);

    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n; j++) {
        if (i !== j) {
          if (p[i][j] > p[j][i]) {
            wins[i]++;
            losses[j]++;
          } else if (p[i][j] === p[j][i] && p[i][j] > 0) {
            rawTies.push([this._candidates[i], this._candidates[j]]);
          }
        }
      }
    }

    // Also count ties where both paths are 0
    for (let i = 0; i < n; i++) {
      for (let j = i + 1; j < n; j++) {
        if (p[i][j] === p[j][i] && p[i][j] === 0) {
          rawTies.push([this._candidates[i], this._candidates[j]]);
        }
      }
    }

    // Sort by wins descending
    const indices = Array.from({ length: n }, (_, i) => i);
    indices.sort((a, b) => wins[b] - wins[a]);

    // Assign ranks (1-indexed, ties get same rank)
    const ranking: SchulzeRanking[] = [];
    let currentRank = 1;
    for (let pos = 0; pos < indices.length; pos++) {
      const idx = indices[pos];
      if (pos > 0) {
        const prevIdx = indices[pos - 1];
        if (wins[idx] < wins[prevIdx]) {
          currentRank = pos + 1;
        }
      }
      ranking.push({
        candidate: this._candidates[idx],
        rank: currentRank,
        wins: wins[idx],
        losses: losses[idx],
      });
    }

    // Deduplicate ties
    const seen = new Set<string>();
    const dedupedTies: [string, string][] = [];
    for (const [a, b] of rawTies) {
      const key = a < b ? `${a}|${b}` : `${b}|${a}`;
      if (!seen.has(key)) {
        seen.add(key);
        dedupedTies.push(a < b ? [a, b] : [b, a]);
      }
    }

    return { ranking, ties: dedupedTies };
  }

  private _checkCondorcet(d: number[][], winner: string): boolean {
    const wi = this._index.get(winner);
    if (wi === undefined) return false;
    for (let j = 0; j < this._candidates.length; j++) {
      if (j !== wi && d[wi][j] <= d[j][wi]) {
        return false;
      }
    }
    return true;
  }
}
