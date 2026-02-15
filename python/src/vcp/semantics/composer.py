"""
VCP/S Constitution Composition Engine.

Handles merging multiple constitutions according to composition modes.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ..types import CompositionMode

if TYPE_CHECKING:
    pass


class CompositionConflictError(Exception):
    """Raised when constitution composition has unresolvable conflicts."""

    def __init__(self, conflicts: list[Conflict]):
        self.conflicts = conflicts
        super().__init__(f"Composition has {len(conflicts)} unresolvable conflict(s)")


@dataclass
class Conflict:
    """Detected conflict between constitutions."""

    rule_a: str
    source_a: str
    rule_b: str
    source_b: str
    conflict_type: str  # "contradiction", "tension", "overlap"
    resolution: str | None = None

    def __str__(self) -> str:
        return (
            f"{self.conflict_type}: "
            f"'{self.rule_a}' ({self.source_a}) "
            f"vs '{self.rule_b}' ({self.source_b})"
        )


@dataclass
class CompositionResult:
    """Result of composing multiple constitutions."""

    merged_rules: list[str]
    conflicts: list[Conflict] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    mode_used: CompositionMode = CompositionMode.EXTEND


@dataclass
class Constitution:
    """Minimal constitution representation for composition."""

    id: str
    rules: list[str]
    priority: int = 0  # Higher = more precedence

    def __post_init__(self) -> None:
        # Normalize rules (strip whitespace)
        self.rules = [r.strip() for r in self.rules if r.strip()]


# Keywords that indicate potential conflicts
CONFLICT_KEYWORDS = {
    "always": {"never"},
    "never": {"always"},
    "must": {"must not", "should not", "never"},
    "must not": {"must", "always"},
    "allow": {"forbid", "prohibit", "deny"},
    "forbid": {"allow", "permit"},
    "prohibit": {"allow", "permit"},
    "require": {"forbid", "prohibit"},
}


class Composer:
    """Compose multiple constitutions according to mode."""

    def compose(
        self,
        constitutions: Sequence[Constitution],
        mode: CompositionMode = CompositionMode.EXTEND,
    ) -> CompositionResult:
        """Compose constitutions according to specified mode.

        Args:
            constitutions: Sequence of constitutions to compose
            mode: Composition mode (BASE, EXTEND, OVERRIDE, STRICT)

        Returns:
            CompositionResult with merged rules and any conflicts

        Raises:
            CompositionConflictError: If mode requires no conflicts but conflicts exist
        """
        if not constitutions:
            return CompositionResult(merged_rules=[], mode_used=mode)

        if mode == CompositionMode.BASE:
            return self._compose_base(constitutions)
        elif mode == CompositionMode.EXTEND:
            return self._compose_extend(constitutions)
        elif mode == CompositionMode.OVERRIDE:
            return self._compose_override(constitutions)
        elif mode == CompositionMode.STRICT:
            return self._compose_strict(constitutions)
        else:
            raise ValueError(f"Unknown composition mode: {mode}")

    def _compose_base(self, constitutions: Sequence[Constitution]) -> CompositionResult:
        """BASE: First constitution cannot be overridden.

        Later constitutions can only ADD rules, not conflict with base.
        """
        if not constitutions:
            return CompositionResult(merged_rules=[], mode_used=CompositionMode.BASE)

        base = constitutions[0]
        merged = list(base.rules)
        conflicts: list[Conflict] = []

        for const in constitutions[1:]:
            for rule in const.rules:
                conflict = self._detect_conflict(rule, const.id, merged, base.id)
                if conflict:
                    # BASE wins - record but don't add
                    conflicts.append(conflict)
                else:
                    merged.append(rule)

        return CompositionResult(
            merged_rules=merged,
            conflicts=conflicts,
            warnings=[],
            mode_used=CompositionMode.BASE,
        )

    def _compose_extend(self, constitutions: Sequence[Constitution]) -> CompositionResult:
        """EXTEND: Add rules, error on conflict.

        All constitutions are equal; any conflict is an error.
        """
        merged: list[str] = []
        conflicts: list[Conflict] = []
        sources: dict[str, str] = {}  # rule -> source constitution id

        for const in constitutions:
            for rule in const.rules:
                conflict = self._detect_conflict(
                    rule, const.id, merged,
                    sources.get(rule, "unknown"),
                )
                if conflict:
                    conflicts.append(conflict)
                else:
                    merged.append(rule)
                    sources[rule] = const.id

        if conflicts:
            raise CompositionConflictError(conflicts)

        return CompositionResult(
            merged_rules=merged,
            conflicts=[],
            warnings=[],
            mode_used=CompositionMode.EXTEND,
        )

    def _compose_override(self, constitutions: Sequence[Constitution]) -> CompositionResult:
        """OVERRIDE: Later constitutions win conflicts.

        Rules from later constitutions replace conflicting earlier rules.
        """
        merged: list[str] = []
        warnings: list[str] = []

        for const in constitutions:
            for rule in const.rules:
                # Remove conflicting rules from earlier constitutions
                conflicting_indices = []
                for i, existing in enumerate(merged):
                    if self._rules_conflict(existing, rule):
                        conflicting_indices.append(i)
                        warnings.append(
                            f"Rule '{rule}' ({const.id}) "
                            f"overrides '{existing}'"
                        )

                # Remove in reverse order to preserve indices
                for i in reversed(conflicting_indices):
                    merged.pop(i)

                merged.append(rule)

        return CompositionResult(
            merged_rules=merged,
            conflicts=[],
            warnings=warnings,
            mode_used=CompositionMode.OVERRIDE,
        )

    def _compose_strict(self, constitutions: Sequence[Constitution]) -> CompositionResult:
        """STRICT: Any conflict is an error, even duplicates.

        Most restrictive mode - all rules must be unique and non-conflicting.
        """
        merged: list[str] = []
        conflicts: list[Conflict] = []
        seen_rules: set[str] = set()
        sources: dict[str, str] = {}

        for const in constitutions:
            for rule in const.rules:
                normalized = rule.lower().strip()

                # Check for exact duplicates
                if normalized in seen_rules:
                    conflicts.append(
                        Conflict(
                            rule_a=rule,
                            source_a=const.id,
                            rule_b=rule,
                            source_b=sources.get(normalized, "unknown"),
                            conflict_type="duplicate",
                        )
                    )
                    continue

                # Check for semantic conflicts
                conflict = self._detect_conflict(rule, const.id, merged, "earlier")
                if conflict:
                    conflicts.append(conflict)
                    continue

                merged.append(rule)
                seen_rules.add(normalized)
                sources[normalized] = const.id

        if conflicts:
            raise CompositionConflictError(conflicts)

        return CompositionResult(
            merged_rules=merged,
            conflicts=[],
            warnings=[],
            mode_used=CompositionMode.STRICT,
        )

    def _detect_conflict(
        self,
        rule: str,
        source: str,
        existing: list[str],
        existing_source: str,
    ) -> Conflict | None:
        """Detect if a rule conflicts with existing rules.

        Args:
            rule: New rule to check
            source: Source constitution ID
            existing: List of existing rules
            existing_source: Source of existing rules

        Returns:
            Conflict if detected, None otherwise
        """
        for existing_rule in existing:
            if self._rules_conflict(rule, existing_rule):
                return Conflict(
                    rule_a=rule,
                    source_a=source,
                    rule_b=existing_rule,
                    source_b=existing_source,
                    conflict_type=self._determine_conflict_type(
                        rule, existing_rule
                    ),
                )
        return None

    def _rules_conflict(self, rule_a: str, rule_b: str) -> bool:
        """Check if two rules semantically conflict.

        Uses keyword-based heuristics for conflict detection.
        """
        a_lower = rule_a.lower()
        b_lower = rule_b.lower()

        # Check for keyword-based conflicts
        for keyword, opposites in CONFLICT_KEYWORDS.items():
            if keyword in a_lower:
                for opposite in opposites:
                    if opposite in b_lower:
                        # Check if they're about the same topic
                        if self._same_topic(a_lower, b_lower):
                            return True

        return False

    def _same_topic(self, rule_a: str, rule_b: str) -> bool:
        """Heuristic to check if two rules are about the same topic.

        Uses word overlap as a simple heuristic.
        """
        # Extract significant words (excluding common words)
        common_words = {
            "the",
            "a",
            "an",
            "is",
            "are",
            "be",
            "to",
            "of",
            "and",
            "or",
            "in",
            "on",
            "at",
            "for",
            "with",
            "by",
            "from",
            "as",
            "it",
            "this",
            "that",
            "these",
            "those",
            "you",
            "we",
            "they",
            "i",
        }

        words_a = set(rule_a.split()) - common_words
        words_b = set(rule_b.split()) - common_words

        # Check for significant overlap
        overlap = words_a & words_b
        if len(overlap) >= 2:
            return True

        return False

    def _determine_conflict_type(self, rule_a: str, rule_b: str) -> str:
        """Determine the type of conflict between two rules."""
        a_lower = rule_a.lower()
        b_lower = rule_b.lower()

        # Direct contradictions (always/never pairs)
        if (
            ("always" in a_lower and "never" in b_lower)
            or ("never" in a_lower and "always" in b_lower)
        ):
            return "contradiction"

        # Must/must not pairs
        if (
            (
                "must not" in a_lower
                and "must" in b_lower
                and "must not" not in b_lower
            )
            or (
                "must" in a_lower
                and "must not" not in a_lower
                and "must not" in b_lower
            )
        ):
            return "contradiction"

        # Allow/forbid pairs
        if (
            ("allow" in a_lower and "forbid" in b_lower)
            or ("forbid" in a_lower and "allow" in b_lower)
        ):
            return "contradiction"

        # Default to tension (weaker conflict)
        return "tension"
