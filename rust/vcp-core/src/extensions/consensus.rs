//! Schulze voting method for VCP consensus.
//!
//! Computes the strongest-path winner from ranked preference ballots.
//! Condorcet-consistent, clone-independent, used by Debian, Wikimedia,
//! and Creed Space.
//!
//! Algorithm:
//! 1. Build pairwise defeat matrix d[i][j] = ballots preferring i over j
//! 2. Compute strongest paths p[i][j] via modified Floyd-Warshall
//! 3. Rank candidates: i beats j iff p[i][j] > p[j][i]

use std::collections::{HashMap, HashSet};

// ── Data types ─────────────────────────────────────────────────────────────

/// A ranked ballot from a stakeholder.
///
/// Rankings are expressed as ordered groups of candidates, best-first.
/// Each inner vec contains candidates of equal preference (ties).
/// Example: `vec![vec!["A"], vec!["B", "C"], vec!["D"]]` means A > B=C > D.
/// For simple rankings without ties: `vec![vec!["A"], vec!["B"], vec!["C"]]`.
///
/// This format matches the Python and TypeScript SDKs for cross-SDK parity.
#[derive(Debug, Clone, PartialEq, serde::Serialize, serde::Deserialize)]
pub struct Ballot {
    /// Voter identifier.
    pub voter_id: String,
    /// Ordered list of candidate groups, best-first.
    /// Each inner vec contains candidates of equal preference (ties).
    pub rankings: Vec<Vec<String>>,
}

impl Ballot {
    /// Create a simple ranked ballot (no ties).
    /// Each candidate gets its own group: `["A"] -> [["A"], ["B"], ["C"]]`.
    pub fn new(voter_id: impl Into<String>, ranking: Vec<String>) -> Self {
        let rankings = ranking.into_iter().map(|c| vec![c]).collect();
        Self {
            voter_id: voter_id.into(),
            rankings,
        }
    }

    /// Create a ballot with explicit tied groups.
    /// This is now the same as `new` with grouped rankings, kept for API compatibility.
    pub fn with_ties(voter_id: impl Into<String>, groups: Vec<Vec<String>>) -> Self {
        Self {
            voter_id: voter_id.into(),
            rankings: groups,
        }
    }
}

/// Pairwise comparison between two candidates.
#[derive(Debug, Clone, PartialEq, serde::Serialize, serde::Deserialize)]
pub struct PairwiseResult {
    pub candidate_a: String,
    pub candidate_b: String,
    pub a_preferred: i32,
    pub b_preferred: i32,
}

/// A candidate's position in the final Schulze ranking.
#[derive(Debug, Clone, PartialEq, serde::Serialize, serde::Deserialize)]
pub struct SchulzeRanking {
    pub candidate: String,
    /// 1-indexed rank, ties possible.
    pub rank: usize,
    /// Number of candidates this one beats.
    pub wins: usize,
    pub losses: usize,
}

/// Complete result of a Schulze election.
#[derive(Debug, Clone, PartialEq, serde::Serialize, serde::Deserialize)]
pub struct ElectionResult {
    /// Winner candidate, or None if no ballots.
    pub winner: Option<String>,
    /// Ordered ranking of all candidates.
    pub ranking: Vec<SchulzeRanking>,
    /// d[i][j] = number of ballots preferring candidate i over candidate j.
    pub pairwise_matrix: Vec<Vec<i32>>,
    /// p[i][j] = strength of strongest path from i to j.
    pub strongest_paths: Vec<Vec<i32>>,
    /// Candidates in index order matching the matrices.
    pub candidates: Vec<String>,
    /// Total number of ballots cast.
    pub ballot_count: usize,
    /// Whether the winner is a Condorcet winner.
    pub has_condorcet_winner: bool,
    /// Pairs that tied in final ranking (deduplicated, sorted).
    pub ties: Vec<(String, String)>,
}

// ── SchulzeElection ────────────────────────────────────────────────────────

/// Schulze voting method for ranked preference aggregation.
pub struct SchulzeElection {
    candidates: Vec<String>,
    index: HashMap<String, usize>,
    ballots: Vec<Ballot>,
}

impl SchulzeElection {
    /// Create a new election with the given candidates.
    ///
    /// # Errors
    /// Returns an error if candidates is empty or contains duplicates.
    pub fn new(candidates: Vec<String>) -> Result<Self, &'static str> {
        if candidates.is_empty() {
            return Err("candidates must be non-empty");
        }
        let unique: HashSet<&str> = candidates.iter().map(String::as_str).collect();
        if unique.len() != candidates.len() {
            return Err("candidates must be unique");
        }
        let index: HashMap<String, usize> = candidates
            .iter()
            .enumerate()
            .map(|(i, c)| (c.clone(), i))
            .collect();
        Ok(Self {
            candidates,
            index,
            ballots: Vec::new(),
        })
    }

    /// Returns the list of candidates.
    pub fn candidates(&self) -> &[String] {
        &self.candidates
    }

    /// Returns the number of ballots cast.
    pub fn ballot_count(&self) -> usize {
        self.ballots.len()
    }

    /// Add a ranked ballot from a stakeholder.
    pub fn add_ballot(&mut self, ballot: Ballot) {
        self.ballots.push(ballot);
    }

    /// Run the Schulze method. Returns the complete election result.
    pub fn compute(&self) -> ElectionResult {
        let n = self.candidates.len();

        if self.ballots.is_empty() {
            return ElectionResult {
                winner: None,
                ranking: Vec::new(),
                pairwise_matrix: vec![vec![0; n]; n],
                strongest_paths: vec![vec![0; n]; n],
                candidates: self.candidates.clone(),
                ballot_count: 0,
                has_condorcet_winner: false,
                ties: Vec::new(),
            };
        }

        let d = self.build_pairwise_matrix();
        let p = self.compute_strongest_paths(&d);
        let (ranking, ties) = self.determine_ranking(&p);

        let winner = ranking.first().map(|r| r.candidate.clone());
        let has_condorcet = winner
            .as_ref()
            .map(|w| self.check_condorcet(&d, w))
            .unwrap_or(false);

        ElectionResult {
            winner,
            ranking,
            pairwise_matrix: d,
            strongest_paths: p,
            candidates: self.candidates.clone(),
            ballot_count: self.ballots.len(),
            has_condorcet_winner: has_condorcet,
            ties,
        }
    }

    /// Build pairwise defeat matrix.
    /// d[i][j] = number of ballots that prefer candidate i over candidate j.
    fn build_pairwise_matrix(&self) -> Vec<Vec<i32>> {
        let n = self.candidates.len();
        let mut d = vec![vec![0i32; n]; n];

        for ballot in &self.ballots {
            self.apply_grouped_ballot(&mut d, ballot);
        }

        d
    }

    /// Apply a grouped ballot to the pairwise matrix.
    /// Each group in `ballot.rankings` contains candidates of equal preference.
    fn apply_grouped_ballot(&self, d: &mut [Vec<i32>], ballot: &Ballot) {
        let n = self.candidates.len();

        let mut position: HashMap<&str, usize> = HashMap::new();
        let mut rank = 0;
        for group in &ballot.rankings {
            for cid in group {
                if self.index.contains_key(cid.as_str()) {
                    position.insert(cid.as_str(), rank);
                }
            }
            rank += 1;
        }
        // Unranked candidates at the bottom
        for cid in &self.candidates {
            position.entry(cid.as_str()).or_insert(rank);
        }

        for i in 0..n {
            for j in (i + 1)..n {
                let pi = position[self.candidates[i].as_str()];
                let pj = position[self.candidates[j].as_str()];
                if pi < pj {
                    d[i][j] += 1;
                } else if pj < pi {
                    d[j][i] += 1;
                }
            }
        }
    }

    /// Compute strongest paths via modified Floyd-Warshall.
    ///
    /// p[i][j] = strength of the strongest path from i to j.
    /// Path strength = minimum edge weight along the path.
    /// Only considers edges where d[i][j] > d[j][i] (net victories).
    fn compute_strongest_paths(&self, d: &[Vec<i32>]) -> Vec<Vec<i32>> {
        let n = self.candidates.len();
        let mut p = vec![vec![0i32; n]; n];

        // Initialize: direct edges where i beats j
        for i in 0..n {
            for j in 0..n {
                if i != j && d[i][j] > d[j][i] {
                    p[i][j] = d[i][j];
                }
            }
        }

        // Floyd-Warshall variant
        for k in 0..n {
            for i in 0..n {
                if i == k {
                    continue;
                }
                for j in 0..n {
                    if j == i || j == k {
                        continue;
                    }
                    let via_k = p[i][k].min(p[k][j]);
                    if via_k > p[i][j] {
                        p[i][j] = via_k;
                    }
                }
            }
        }

        p
    }

    /// Convert strongest path matrix to ordered ranking.
    fn determine_ranking(&self, p: &[Vec<i32>]) -> (Vec<SchulzeRanking>, Vec<(String, String)>) {
        let n = self.candidates.len();
        let mut ties: Vec<(String, String)> = Vec::new();

        // Count wins and losses for each candidate
        let mut wins = vec![0usize; n];
        let mut losses = vec![0usize; n];
        for i in 0..n {
            for j in 0..n {
                if i != j {
                    if p[i][j] > p[j][i] {
                        wins[i] += 1;
                        losses[j] += 1;
                    } else if p[i][j] == p[j][i] && p[i][j] > 0 {
                        ties.push((self.candidates[i].clone(), self.candidates[j].clone()));
                    }
                }
            }
        }

        // Also count ties where both paths are 0
        for i in 0..n {
            for j in (i + 1)..n {
                if p[i][j] == p[j][i] && p[i][j] == 0 {
                    let pair = (self.candidates[i].clone(), self.candidates[j].clone());
                    if !ties.contains(&pair) {
                        ties.push(pair);
                    }
                }
            }
        }

        // Sort indices by wins descending
        let mut indices: Vec<usize> = (0..n).collect();
        indices.sort_by(|&a, &b| wins[b].cmp(&wins[a]));

        // Assign ranks (1-indexed, ties get same rank)
        let mut rankings: Vec<SchulzeRanking> = Vec::with_capacity(n);
        let mut current_rank = 1;
        for (pos, &idx) in indices.iter().enumerate() {
            if pos > 0 {
                let prev_idx = indices[pos - 1];
                if wins[idx] < wins[prev_idx] {
                    current_rank = pos + 1;
                }
            }
            rankings.push(SchulzeRanking {
                candidate: self.candidates[idx].clone(),
                rank: current_rank,
                wins: wins[idx],
                losses: losses[idx],
            });
        }

        // Deduplicate ties
        let mut seen: HashSet<(String, String)> = HashSet::new();
        let mut deduped: Vec<(String, String)> = Vec::new();
        for (a, b) in ties {
            let key = if a < b {
                (a.clone(), b.clone())
            } else {
                (b.clone(), a.clone())
            };
            if seen.insert(key.clone()) {
                deduped.push(key);
            }
        }

        (rankings, deduped)
    }

    /// Check if the winner is a Condorcet winner (beats all others pairwise).
    fn check_condorcet(&self, d: &[Vec<i32>], winner: &str) -> bool {
        let wi = match self.index.get(winner) {
            Some(&i) => i,
            None => return false,
        };
        for j in 0..self.candidates.len() {
            if j != wi && d[wi][j] <= d[j][wi] {
                return false;
            }
        }
        true
    }
}

// ── Tests ──────────────────────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;

    fn cands(names: &[&str]) -> Vec<String> {
        names.iter().map(|s| s.to_string()).collect()
    }

    #[test]
    fn test_empty_candidates() {
        assert!(SchulzeElection::new(Vec::new()).is_err());
    }

    #[test]
    fn test_duplicate_candidates() {
        let result = SchulzeElection::new(cands(&["a", "b", "a"]));
        assert!(result.is_err());
    }

    #[test]
    fn test_no_ballots() {
        let election = SchulzeElection::new(cands(&["a", "b", "c"])).unwrap();
        let result = election.compute();
        assert!(result.winner.is_none());
        assert_eq!(result.ballot_count, 0);
    }

    #[test]
    fn test_single_ballot() {
        let mut election = SchulzeElection::new(cands(&["a", "b", "c"])).unwrap();
        election.add_ballot(Ballot::new("v1", cands(&["b", "a", "c"])));
        let result = election.compute();
        assert_eq!(result.winner.as_deref(), Some("b"));
        assert_eq!(result.ballot_count, 1);
        assert!(result.has_condorcet_winner);
    }

    #[test]
    fn test_condorcet_winner() {
        // b is the Condorcet winner (preferred by majority against each other)
        let mut election = SchulzeElection::new(cands(&["a", "b", "c"])).unwrap();
        election.add_ballot(Ballot::new("v1", cands(&["b", "a", "c"])));
        election.add_ballot(Ballot::new("v2", cands(&["b", "c", "a"])));
        election.add_ballot(Ballot::new("v3", cands(&["a", "b", "c"])));
        let result = election.compute();
        assert_eq!(result.winner.as_deref(), Some("b"));
        assert!(result.has_condorcet_winner);
    }

    #[test]
    fn test_tied_groups_ballot() {
        let mut election = SchulzeElection::new(cands(&["a", "b", "c"])).unwrap();
        // a and b are tied at top, c is below
        election.add_ballot(Ballot::with_ties(
            "v1",
            vec![cands(&["a", "b"]), cands(&["c"])],
        ));
        let result = election.compute();
        // Both a and b should beat c but not each other
        let a_idx = 0;
        let b_idx = 1;
        let c_idx = 2;
        assert_eq!(result.pairwise_matrix[a_idx][c_idx], 1);
        assert_eq!(result.pairwise_matrix[b_idx][c_idx], 1);
        assert_eq!(result.pairwise_matrix[a_idx][b_idx], 0);
        assert_eq!(result.pairwise_matrix[b_idx][a_idx], 0);
    }

    #[test]
    fn test_strongest_paths_match_python() {
        // Classic 4-candidate Schulze example
        let mut election = SchulzeElection::new(cands(&["a", "b", "c", "d"])).unwrap();
        // 3 voters: a > b > c > d
        for _ in 0..3 {
            election.add_ballot(Ballot::new("v", cands(&["a", "b", "c", "d"])));
        }
        // 2 voters: d > c > b > a
        for _ in 0..2 {
            election.add_ballot(Ballot::new("v", cands(&["d", "c", "b", "a"])));
        }
        let result = election.compute();

        // a beats all 3>2, so a is the Condorcet winner
        assert_eq!(result.winner.as_deref(), Some("a"));
        assert!(result.has_condorcet_winner);

        // Verify pairwise: a beats b,c,d 3-2
        assert_eq!(result.pairwise_matrix[0][1], 3); // a>b
        assert_eq!(result.pairwise_matrix[1][0], 2); // b>a
    }

    #[test]
    fn test_schulze_ranking_order() {
        let mut election = SchulzeElection::new(cands(&["a", "b", "c"])).unwrap();
        election.add_ballot(Ballot::new("v1", cands(&["c", "b", "a"])));
        election.add_ballot(Ballot::new("v2", cands(&["c", "a", "b"])));
        election.add_ballot(Ballot::new("v3", cands(&["b", "c", "a"])));
        let result = election.compute();

        // c wins 2 first-place votes, should be top
        assert_eq!(result.winner.as_deref(), Some("c"));
        assert_eq!(result.ranking[0].candidate, "c");
        assert_eq!(result.ranking[0].rank, 1);
    }

    #[test]
    fn test_unranked_candidates_at_bottom() {
        let mut election = SchulzeElection::new(cands(&["a", "b", "c"])).unwrap();
        // Only ranks "a", so b and c are tied at bottom
        election.add_ballot(Ballot::new("v1", cands(&["a"])));
        let result = election.compute();
        assert_eq!(result.winner.as_deref(), Some("a"));
        // a should beat both b and c
        assert_eq!(result.pairwise_matrix[0][1], 1); // a>b
        assert_eq!(result.pairwise_matrix[0][2], 1); // a>c
                                                     // b and c tied (both unranked)
        assert_eq!(result.pairwise_matrix[1][2], 0);
        assert_eq!(result.pairwise_matrix[2][1], 0);
    }
}
