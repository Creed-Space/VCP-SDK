"""VCP 3.1 Schulze Consensus Voting Extension.

Pure-Python implementation of the Schulze voting method for ranked
preference aggregation. Used by the Constitutional Consensus Primitive
for multi-stakeholder deliberation.

Algorithm:
1. Build pairwise defeat matrix d[i][j] = ballots preferring i over j
2. Compute strongest paths p[i][j] via modified Floyd-Warshall
3. Rank candidates: i beats j iff p[i][j] > p[j][i]

No external dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Ballot:
    """A ranked ballot from a stakeholder.

    Args:
        voter_id: Identifier for the voter.
        rankings: Ordered list of candidate-group lists, best-first.
            Each inner list contains candidates of equal preference (ties).
            Example: [["A"], ["B", "C"], ["D"]] means A > B=C > D.
            For simple rankings without ties: [["A"], ["B"], ["C"]].
    """

    voter_id: str
    rankings: list[list[str]]

    def __post_init__(self) -> None:
        if not self.rankings:
            raise ValueError("rankings must be non-empty")
        seen: set[str] = set()
        for group in self.rankings:
            if not group:
                raise ValueError("Each ranking group must be non-empty")
            for candidate in group:
                if candidate in seen:
                    raise ValueError(f"Duplicate candidate: {candidate}")
                seen.add(candidate)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to plain dict."""
        return {
            "voter_id": self.voter_id,
            "rankings": self.rankings,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Ballot:
        """Deserialize from dict."""
        return cls(
            voter_id=data["voter_id"],
            rankings=data["rankings"],
        )


@dataclass(frozen=True)
class PairwiseResult:
    """Pairwise comparison between two candidates.

    Args:
        candidate_a: First candidate.
        candidate_b: Second candidate.
        margin: Net margin of a over b (positive = a preferred).
    """

    candidate_a: str
    candidate_b: str
    margin: int


@dataclass(frozen=True)
class SchulzeRanking:
    """A candidate's position in the final Schulze ranking.

    Args:
        candidate: Candidate identifier.
        rank: 1-indexed rank (ties possible).
        wins: Number of candidates this one beats.
        losses: Number of candidates that beat this one.
    """

    candidate: str
    rank: int
    wins: int
    losses: int


@dataclass
class ElectionResult:
    """Complete result of a Schulze election.

    Args:
        ranking: Ordered list of candidate rankings.
        pairwise_matrix: Raw pairwise preference counts.
        strongest_paths: Strongest path matrix after Floyd-Warshall.
        dissent_notes: Notes on ties or contentious outcomes.
    """

    ranking: list[SchulzeRanking]
    pairwise_matrix: list[list[int]]
    strongest_paths: list[list[int]]
    dissent_notes: list[str] = field(default_factory=list)

    @property
    def winner(self) -> str | None:
        """The top-ranked candidate, or None if no ballots."""
        return self.ranking[0].candidate if self.ranking else None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to plain dict."""
        return {
            "ranking": [
                {
                    "candidate": r.candidate,
                    "rank": r.rank,
                    "wins": r.wins,
                    "losses": r.losses,
                }
                for r in self.ranking
            ],
            "pairwise_matrix": self.pairwise_matrix,
            "strongest_paths": self.strongest_paths,
            "dissent_notes": self.dissent_notes,
        }


class SchulzeElection:
    """Schulze voting method for ranked preference aggregation.

    Condorcet-consistent, clone-independent. Used by Debian, Wikimedia,
    and Creed Space.

    Example:
        >>> election = SchulzeElection(["A", "B", "C"])
        >>> election.add_ballot(Ballot(voter_id="v1", rankings=[["A"], ["B"], ["C"]]))
        >>> election.add_ballot(Ballot(voter_id="v2", rankings=[["B"], ["C"], ["A"]]))
        >>> election.add_ballot(Ballot(voter_id="v3", rankings=[["A"], ["C"], ["B"]]))
        >>> result = election.compute()
        >>> result.winner
        'A'
    """

    def __init__(self, candidates: list[str]) -> None:
        """Initialize election with candidate list.

        Args:
            candidates: List of unique candidate identifiers.

        Raises:
            ValueError: If candidates is empty or contains duplicates.
        """
        if not candidates:
            raise ValueError("candidates must be non-empty")
        if len(candidates) != len(set(candidates)):
            raise ValueError("candidates must be unique")
        self._candidates = list(candidates)
        self._ballots: list[Ballot] = []
        self._index = {c: i for i, c in enumerate(self._candidates)}

    @property
    def candidates(self) -> list[str]:
        """Return copy of candidate list."""
        return list(self._candidates)

    @property
    def ballot_count(self) -> int:
        """Number of ballots cast."""
        return len(self._ballots)

    def add_ballot(self, ballot: Ballot) -> None:
        """Add a ranked ballot from a stakeholder.

        Args:
            ballot: Ranked ballot to add.
        """
        self._ballots.append(ballot)

    def compute(self) -> ElectionResult:
        """Run Schulze method. Returns full ranking with pairwise data.

        Returns:
            ElectionResult with winner, ranking, matrices, and dissent notes.
        """
        n = len(self._candidates)

        if not self._ballots:
            return ElectionResult(
                ranking=[],
                pairwise_matrix=[[0] * n for _ in range(n)],
                strongest_paths=[[0] * n for _ in range(n)],
                dissent_notes=["No ballots cast"],
            )

        d = self._build_pairwise_matrix()
        p = self._compute_strongest_paths(d)
        ranking, dissent = self._determine_ranking(p)

        return ElectionResult(
            ranking=ranking,
            pairwise_matrix=d,
            strongest_paths=p,
            dissent_notes=dissent,
        )

    def _build_pairwise_matrix(self) -> list[list[int]]:
        """Count pairwise preferences from all ballots.

        d[i][j] = number of ballots that prefer candidate i over candidate j.
        """
        n = len(self._candidates)
        d = [[0] * n for _ in range(n)]

        for ballot in self._ballots:
            # Build position map from tied groups
            position: dict[str, int] = {}
            rank = 0
            for group in ballot.rankings:
                for cid in group:
                    if cid in self._index:
                        position[cid] = rank
                rank += 1

            # Unranked candidates at the bottom
            for cid in self._candidates:
                if cid not in position:
                    position[cid] = rank

            for i in range(n):
                for j in range(i + 1, n):
                    ci = self._candidates[i]
                    cj = self._candidates[j]
                    pi = position[ci]
                    pj = position[cj]
                    if pi < pj:
                        d[i][j] += 1
                    elif pj < pi:
                        d[j][i] += 1

        return d

    def _compute_strongest_paths(self, d: list[list[int]]) -> list[list[int]]:
        """Compute strongest paths via modified Floyd-Warshall.

        p[i][j] = strength of the strongest path from i to j.
        Path strength = minimum edge weight along the path.
        Only considers edges where d[i][j] > d[j][i] (net victories).
        """
        n = len(self._candidates)
        p = [[0] * n for _ in range(n)]

        # Initialize: direct edges where i beats j
        for i in range(n):
            for j in range(n):
                if i != j and d[i][j] > d[j][i]:
                    p[i][j] = d[i][j]

        # Floyd-Warshall variant
        for k in range(n):
            for i in range(n):
                if i == k:
                    continue
                for j in range(n):
                    if j in (i, k):
                        continue
                    via_k = min(p[i][k], p[k][j])
                    if via_k > p[i][j]:
                        p[i][j] = via_k

        return p

    def _determine_ranking(self, p: list[list[int]]) -> tuple[list[SchulzeRanking], list[str]]:
        """Convert strongest path matrix to ordered ranking.

        Candidate i beats j iff p[i][j] > p[j][i].
        """
        n = len(self._candidates)
        dissent: list[str] = []

        wins = [0] * n
        losses = [0] * n
        for i in range(n):
            for j in range(n):
                if i != j:
                    if p[i][j] > p[j][i]:
                        wins[i] += 1
                        losses[j] += 1
                    elif p[i][j] == p[j][i] and p[i][j] > 0:
                        dissent.append(
                            f"Tie between {self._candidates[i]} and {self._candidates[j]}"
                        )

        # Sort by wins descending
        indices = list(range(n))
        indices.sort(key=lambda i: wins[i], reverse=True)

        # Assign ranks (1-indexed, ties get same rank)
        rankings: list[SchulzeRanking] = []
        current_rank = 1
        for pos, idx in enumerate(indices):
            if pos > 0:
                prev_idx = indices[pos - 1]
                if wins[idx] < wins[prev_idx]:
                    current_rank = pos + 1
            rankings.append(
                SchulzeRanking(
                    candidate=self._candidates[idx],
                    rank=current_rank,
                    wins=wins[idx],
                    losses=losses[idx],
                )
            )

        # Deduplicate dissent notes
        seen: set[str] = set()
        deduped: list[str] = []
        for note in dissent:
            parts = note.replace("Tie between ", "").split(" and ")
            key = " and ".join(sorted(parts))
            if key not in seen:
                seen.add(key)
                deduped.append(note)

        return rankings, deduped
