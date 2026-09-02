"""Tests for VCP 3.1 Schulze Consensus Voting Extension."""

from __future__ import annotations

import pytest

from vcp.extensions.consensus import (
    Ballot,
    SchulzeElection,
)


class TestBallot:
    """Tests for Ballot dataclass."""

    def test_valid_ballot(self) -> None:
        ballot = Ballot(voter_id="v1", rankings=[["A"], ["B"], ["C"]])
        assert ballot.voter_id == "v1"
        assert len(ballot.rankings) == 3

    def test_tied_rankings(self) -> None:
        ballot = Ballot(voter_id="v1", rankings=[["A", "B"], ["C"]])
        assert len(ballot.rankings) == 2
        assert len(ballot.rankings[0]) == 2

    def test_empty_rankings(self) -> None:
        with pytest.raises(ValueError, match="rankings must be non-empty"):
            Ballot(voter_id="v1", rankings=[])

    def test_empty_group(self) -> None:
        with pytest.raises(ValueError, match="Each ranking group must be non-empty"):
            Ballot(voter_id="v1", rankings=[["A"], []])

    def test_duplicate_candidate(self) -> None:
        with pytest.raises(ValueError, match="Duplicate candidate"):
            Ballot(voter_id="v1", rankings=[["A"], ["A"]])

    @pytest.mark.parametrize(
        ("voter_id", "rankings"),
        [
            ("", [["A"]]),
            (7, [["A"]]),
            ("v1", "A"),
            ("v1", [7]),
            ("v1", [[7]]),
            ("v1", [[""]]),
        ],
    )
    def test_malformed_ballot_shape_is_rejected(self, voter_id: object, rankings: object) -> None:
        with pytest.raises(ValueError):
            Ballot(voter_id=voter_id, rankings=rankings)  # type: ignore[arg-type]

    def test_ballot_identifier_and_candidate_count_limits(self) -> None:
        with pytest.raises(ValueError, match="1 to 256"):
            Ballot(voter_id="v" * 257, rankings=[["A"]])
        with pytest.raises(ValueError, match="1 to 256"):
            Ballot(voter_id="v", rankings=[["A" * 257]])
        with pytest.raises(ValueError, match="256-candidate"):
            Ballot(
                voter_id="v",
                rankings=[[f"C{index}"] for index in range(257)],
            )

    def test_from_dict_requires_an_object(self) -> None:
        with pytest.raises(TypeError, match="object"):
            Ballot.from_dict([])  # type: ignore[arg-type]

    def test_ballot_snapshots_nested_rankings_and_serialization(self) -> None:
        rankings = [["A"], ["B"]]
        ballot = Ballot(voter_id="v1", rankings=rankings)
        rankings[0][0] = "mutated"
        serialized = ballot.to_dict()
        serialized["rankings"][0][0] = "also-mutated"
        assert ballot.rankings == [["A"], ["B"]]

    def test_to_dict(self) -> None:
        ballot = Ballot(voter_id="v1", rankings=[["A"], ["B"]])
        d = ballot.to_dict()
        assert d["voter_id"] == "v1"
        assert d["rankings"] == [["A"], ["B"]]

    def test_from_dict(self) -> None:
        data = {"voter_id": "v2", "rankings": [["X"], ["Y", "Z"]]}
        ballot = Ballot.from_dict(data)
        assert ballot.voter_id == "v2"
        assert ballot.rankings == [["X"], ["Y", "Z"]]


class TestSchulzeElection:
    """Tests for SchulzeElection class."""

    def test_empty_candidates(self) -> None:
        with pytest.raises(ValueError, match="candidates must be non-empty"):
            SchulzeElection([])

    def test_duplicate_candidates(self) -> None:
        with pytest.raises(ValueError, match="candidates must be unique"):
            SchulzeElection(["A", "A", "B"])

    @pytest.mark.parametrize("candidates", [None, "ABC", ["A", ""], ["A", 7]])
    def test_malformed_candidate_sets_are_rejected(self, candidates: object) -> None:
        with pytest.raises(ValueError):
            SchulzeElection(candidates)  # type: ignore[arg-type]

    def test_election_candidate_count_and_identifier_limits(self) -> None:
        election = SchulzeElection([f"C{index}" for index in range(256)])
        assert len(election.candidates) == 256
        with pytest.raises(ValueError, match="more than 256"):
            SchulzeElection([f"C{index}" for index in range(257)])
        with pytest.raises(ValueError, match="1 to 256"):
            SchulzeElection(["C" * 257])

    def test_unknown_candidate_ballot_is_rejected_without_corrupting_state(self) -> None:
        election = SchulzeElection(["A", "B"])
        with pytest.raises(ValueError, match="unknown candidates: C"):
            election.add_ballot(Ballot(voter_id="v1", rankings=[["A"], ["C"]]))
        assert election.ballot_count == 0

    def test_wrong_ballot_object_is_rejected(self) -> None:
        election = SchulzeElection(["A", "B"])
        with pytest.raises(TypeError, match="Ballot"):
            election.add_ballot({"voter_id": "v1"})  # type: ignore[arg-type]

    def test_election_snapshots_ballot_before_storage(self) -> None:
        election = SchulzeElection(["A", "B"])
        ballot = Ballot(voter_id="v1", rankings=[["A"], ["B"]])
        election.add_ballot(ballot)
        ballot.rankings.reverse()
        assert election.compute().winner == "A"

    def test_ballot_resource_limit_rejects_before_mutation(self) -> None:
        election = SchulzeElection(["A"])
        ballot = Ballot(voter_id="v", rankings=[["A"]])
        for _ in range(10_000):
            election.add_ballot(ballot)
        with pytest.raises(ValueError, match="10000"):
            election.add_ballot(ballot)
        assert election.ballot_count == 10_000

    def test_no_ballots(self) -> None:
        election = SchulzeElection(["A", "B", "C"])
        result = election.compute()
        assert result.winner is None
        assert result.ranking == []
        assert "No ballots cast" in result.dissent_notes

    def test_single_ballot(self) -> None:
        election = SchulzeElection(["A", "B", "C"])
        election.add_ballot(Ballot(voter_id="v1", rankings=[["A"], ["B"], ["C"]]))
        result = election.compute()
        assert result.winner == "A"
        assert result.ranking[0].candidate == "A"
        assert result.ranking[0].rank == 1

    def test_unanimous_winner(self) -> None:
        election = SchulzeElection(["A", "B", "C"])
        for i in range(5):
            election.add_ballot(Ballot(voter_id=f"v{i}", rankings=[["A"], ["B"], ["C"]]))
        result = election.compute()
        assert result.winner == "A"
        assert result.ranking[0].wins == 2  # beats B and C

    def test_condorcet_winner(self) -> None:
        """Test classic Condorcet scenario: A beats everyone pairwise."""
        election = SchulzeElection(["A", "B", "C"])
        # 3 voters prefer A > B > C
        for _ in range(3):
            election.add_ballot(Ballot(voter_id="v", rankings=[["A"], ["B"], ["C"]]))
        # 2 voters prefer B > C > A
        for _ in range(2):
            election.add_ballot(Ballot(voter_id="v", rankings=[["B"], ["C"], ["A"]]))
        result = election.compute()
        # A beats B (3-2), A beats C (3-2), B beats C (5-0)
        assert result.winner == "A"

    def test_schulze_resolves_condorcet_cycle(self) -> None:
        """Test that Schulze resolves a Condorcet paradox (A>B>C>A cycle)."""
        election = SchulzeElection(["A", "B", "C"])
        # A > B > C: 3 voters
        for _ in range(3):
            election.add_ballot(Ballot(voter_id="v", rankings=[["A"], ["B"], ["C"]]))
        # B > C > A: 2 voters
        for _ in range(2):
            election.add_ballot(Ballot(voter_id="v", rankings=[["B"], ["C"], ["A"]]))
        # C > A > B: 2 voters
        for _ in range(2):
            election.add_ballot(Ballot(voter_id="v", rankings=[["C"], ["A"], ["B"]]))
        result = election.compute()
        # Schulze produces a winner even in cycles
        assert result.winner is not None
        assert len(result.ranking) == 3

    def test_tied_groups_in_ballot(self) -> None:
        """Test ballots with tied candidates in a group."""
        election = SchulzeElection(["A", "B", "C"])
        # Voter says A and B are equally preferred, both above C
        election.add_ballot(Ballot(voter_id="v1", rankings=[["A", "B"], ["C"]]))
        election.add_ballot(Ballot(voter_id="v2", rankings=[["A"], ["B"], ["C"]]))
        result = election.compute()
        assert result.winner == "A"

    def test_unranked_candidates_at_bottom(self) -> None:
        """Candidates not mentioned in ballot are tied at bottom."""
        election = SchulzeElection(["A", "B", "C", "D"])
        # Only mention A and B -- C and D at bottom
        election.add_ballot(Ballot(voter_id="v1", rankings=[["A"], ["B"]]))
        result = election.compute()
        # A should beat B, C, D. B should beat C, D.
        assert result.ranking[0].candidate == "A"

    def test_ballot_count(self) -> None:
        election = SchulzeElection(["X", "Y"])
        assert election.ballot_count == 0
        election.add_ballot(Ballot(voter_id="v1", rankings=[["X"], ["Y"]]))
        assert election.ballot_count == 1

    def test_candidates_property(self) -> None:
        election = SchulzeElection(["A", "B", "C"])
        assert election.candidates == ["A", "B", "C"]
        # Should be a copy
        election.candidates.append("D")
        assert election.candidates == ["A", "B", "C"]

    def test_pairwise_matrix_dimensions(self) -> None:
        election = SchulzeElection(["A", "B", "C"])
        election.add_ballot(Ballot(voter_id="v1", rankings=[["A"], ["B"], ["C"]]))
        result = election.compute()
        assert len(result.pairwise_matrix) == 3
        assert all(len(row) == 3 for row in result.pairwise_matrix)

    def test_strongest_paths_matrix_dimensions(self) -> None:
        election = SchulzeElection(["A", "B"])
        election.add_ballot(Ballot(voter_id="v1", rankings=[["A"], ["B"]]))
        result = election.compute()
        assert len(result.strongest_paths) == 2
        assert all(len(row) == 2 for row in result.strongest_paths)

    def test_election_result_to_dict(self) -> None:
        election = SchulzeElection(["A", "B"])
        election.add_ballot(Ballot(voter_id="v1", rankings=[["A"], ["B"]]))
        result = election.compute()
        d = result.to_dict()
        assert "ranking" in d
        assert "pairwise_matrix" in d
        assert "strongest_paths" in d

    def test_wikipedia_schulze_example(self) -> None:
        """Classic Wikipedia Schulze example with 5 candidates and 45 voters."""
        election = SchulzeElection(["A", "B", "C", "D", "E"])
        # 5 voters: A > C > B > E > D
        for _ in range(5):
            election.add_ballot(Ballot(voter_id="v", rankings=[["A"], ["C"], ["B"], ["E"], ["D"]]))
        # 5 voters: A > D > E > C > B
        for _ in range(5):
            election.add_ballot(Ballot(voter_id="v", rankings=[["A"], ["D"], ["E"], ["C"], ["B"]]))
        # 8 voters: B > E > D > A > C
        for _ in range(8):
            election.add_ballot(Ballot(voter_id="v", rankings=[["B"], ["E"], ["D"], ["A"], ["C"]]))
        # 3 voters: C > A > B > E > D
        for _ in range(3):
            election.add_ballot(Ballot(voter_id="v", rankings=[["C"], ["A"], ["B"], ["E"], ["D"]]))
        # 7 voters: C > A > E > B > D
        for _ in range(7):
            election.add_ballot(Ballot(voter_id="v", rankings=[["C"], ["A"], ["E"], ["B"], ["D"]]))
        # 2 voters: C > B > A > D > E
        for _ in range(2):
            election.add_ballot(Ballot(voter_id="v", rankings=[["C"], ["B"], ["A"], ["D"], ["E"]]))
        # 7 voters: D > C > E > B > A
        for _ in range(7):
            election.add_ballot(Ballot(voter_id="v", rankings=[["D"], ["C"], ["E"], ["B"], ["A"]]))
        # 8 voters: E > B > A > D > C
        for _ in range(8):
            election.add_ballot(Ballot(voter_id="v", rankings=[["E"], ["B"], ["A"], ["D"], ["C"]]))
        result = election.compute()
        assert result.winner == "E"
        assert election.ballot_count == 45
