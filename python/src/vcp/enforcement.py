"""
VCP PDP Enforcement Module

Standalone policy enforcement for VCP bundles. Allows SDK consumers to
enforce PDP-like decisions (allow/block/transform) against constitutional
rules without depending on a full safety stack.

This module provides:
- PDPPlugin: Abstract interface for enforcement plugins
- PDPDecision: Decision result with reason and evidence
- PDPEnforcer: Orchestrator that runs plugins and produces decisions
- Built-in plugins: RefusalBoundaryPlugin, AdherenceLevelPlugin

Usage:
    from vcp.enforcement import PDPEnforcer, RefusalBoundaryPlugin, AdherenceLevelPlugin

    enforcer = PDPEnforcer()
    enforcer.register(RefusalBoundaryPlugin())
    enforcer.register(AdherenceLevelPlugin(min_adherence=3))

    decision = enforcer.evaluate(bundle, content="user prompt here")
    if decision.blocked:
        print(f"Blocked: {decision.reason}")
"""

from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from .audit import AuditLogger
from .types import EnforcementMode, VerificationResult

logger = logging.getLogger(__name__)


class DecisionType(Enum):
    """PDP decision outcomes."""

    ALLOW = "allow"
    BLOCK = "block"
    TRANSFORM = "transform"
    ESCALATE = "escalate"


@dataclass
class PDPDecision:
    """Result of a PDP evaluation."""

    decision: DecisionType
    reason: str
    plugin_id: str
    confidence: float = 1.0
    evidence: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def blocked(self) -> bool:
        return self.decision == DecisionType.BLOCK

    @property
    def allowed(self) -> bool:
        return self.decision == DecisionType.ALLOW


@dataclass
class EvaluationContext:
    """Context passed to plugins during evaluation."""

    bundle: Any  # Bundle
    content: str
    session_id: str | None = None
    user_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class PDPPlugin(ABC):
    """Abstract base class for PDP enforcement plugins.

    Implement `evaluate` to inspect a bundle and content, returning
    a PDPDecision if the plugin has an opinion, or None to abstain.
    """

    @property
    @abstractmethod
    def plugin_id(self) -> str:
        """Unique identifier for this plugin."""

    @property
    def priority(self) -> int:
        """Lower runs first. Default 100."""
        return 100

    @abstractmethod
    def evaluate(self, ctx: EvaluationContext) -> PDPDecision | None:
        """Evaluate content against this plugin's rules.

        Returns:
            PDPDecision if the plugin has a verdict, None to abstain.
        """


class RefusalBoundaryPlugin(PDPPlugin):
    """Enforces refusal boundaries declared in VCP bundles.

    Checks that the bundle's verification is valid and applies the
    enforcement mode (FAIL_CLOSED, ESCALATE, AUDIT_ONLY) from the
    bundle's refusal boundary tokens.
    """

    @property
    def plugin_id(self) -> str:
        return "refusal_boundary"

    @property
    def priority(self) -> int:
        return 10  # Run early — invalid bundles should be caught first

    def __init__(
        self,
        mode: EnforcementMode = EnforcementMode.FAIL_CLOSED,
    ) -> None:
        self._mode = mode

    def evaluate(self, ctx: EvaluationContext) -> PDPDecision | None:
        bundle = ctx.bundle
        if bundle is None:
            if self._mode == EnforcementMode.FAIL_CLOSED:
                return PDPDecision(
                    decision=DecisionType.BLOCK,
                    reason="No VCP bundle present — fail-closed",
                    plugin_id=self.plugin_id,
                )
            return None

        # Check bundle verification status if available
        verification = ctx.metadata.get("verification_result")
        if isinstance(verification, VerificationResult) and not verification.is_valid:
            if self._mode == EnforcementMode.FAIL_CLOSED:
                return PDPDecision(
                    decision=DecisionType.BLOCK,
                    reason=f"Bundle verification failed: {verification.name}",
                    plugin_id=self.plugin_id,
                    evidence={"verification_result": verification.name},
                )
            if self._mode == EnforcementMode.ESCALATE:
                return PDPDecision(
                    decision=DecisionType.ESCALATE,
                    reason=f"Bundle verification failed: {verification.name}",
                    plugin_id=self.plugin_id,
                    evidence={"verification_result": verification.name},
                )
            # AUDIT_ONLY: log but allow
            logger.warning(
                "Bundle verification failed (%s) but enforcement is AUDIT_ONLY",
                verification.name,
            )

        return None


class AdherenceLevelPlugin(PDPPlugin):
    """Enforces minimum adherence level from CSM1-encoded constitutions.

    Adherence levels (0-5):
        0: Advisory — no enforcement
        1: Soft — gentle reminders
        2: Moderate — some enforcement
        3: Active — standard enforcement
        4: Strict — strong enforcement
        5: Absolute — no overrides
    """

    @property
    def plugin_id(self) -> str:
        return "adherence_level"

    @property
    def priority(self) -> int:
        return 20

    def __init__(self, min_adherence: int = 3) -> None:
        if not 0 <= min_adherence <= 5:
            raise ValueError(f"min_adherence must be 0-5, got {min_adherence}")
        self._min_adherence = min_adherence

    def evaluate(self, ctx: EvaluationContext) -> PDPDecision | None:
        bundle = ctx.bundle
        if bundle is None:
            return None

        # Extract adherence level from bundle metadata or manifest
        adherence = ctx.metadata.get("adherence_level")
        if adherence is None:
            manifest_meta = getattr(bundle, "manifest", None)
            if manifest_meta:
                adherence = getattr(manifest_meta, "metadata", {}).get(
                    "adherence_level"
                )

        if adherence is None:
            return None

        try:
            adherence = int(adherence)
        except (ValueError, TypeError):
            return PDPDecision(
                decision=DecisionType.BLOCK,
                reason=f"Invalid adherence level: {adherence!r}",
                plugin_id=self.plugin_id,
            )

        if adherence < self._min_adherence:
            return PDPDecision(
                decision=DecisionType.BLOCK,
                reason=(
                    f"Adherence level {adherence} below minimum {self._min_adherence}"
                ),
                plugin_id=self.plugin_id,
                evidence={
                    "adherence_level": adherence,
                    "min_adherence": self._min_adherence,
                },
            )

        return None


class BundleExpiryPlugin(PDPPlugin):
    """Blocks expired bundles."""

    @property
    def plugin_id(self) -> str:
        return "bundle_expiry"

    @property
    def priority(self) -> int:
        return 5  # Run very early

    def evaluate(self, ctx: EvaluationContext) -> PDPDecision | None:
        bundle = ctx.bundle
        if bundle is None:
            return None

        manifest = getattr(bundle, "manifest", None)
        if manifest is None:
            return None

        timestamps = getattr(manifest, "timestamps", None)
        if timestamps is None:
            return None

        exp = getattr(timestamps, "exp", None)
        if exp is None:
            return None

        now = datetime.now(timezone.utc)
        if hasattr(exp, "tzinfo") and exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)

        if now > exp:
            return PDPDecision(
                decision=DecisionType.BLOCK,
                reason=f"Bundle expired at {exp.isoformat()}",
                plugin_id=self.plugin_id,
                evidence={"expired_at": exp.isoformat(), "now": now.isoformat()},
            )

        return None


@dataclass
class EnforcementResult:
    """Aggregate result from all plugins."""

    final_decision: DecisionType
    decisions: list[PDPDecision]
    duration_ms: int
    plugins_evaluated: int

    @property
    def blocked(self) -> bool:
        return self.final_decision == DecisionType.BLOCK

    @property
    def allowed(self) -> bool:
        return self.final_decision == DecisionType.ALLOW

    @property
    def blocking_reasons(self) -> list[str]:
        return [
            d.reason for d in self.decisions if d.decision == DecisionType.BLOCK
        ]


class PDPEnforcer:
    """Orchestrates PDP plugin evaluation against VCP bundles.

    Runs registered plugins in priority order. Any BLOCK decision
    causes the final result to be BLOCK (fail-closed). ESCALATE
    decisions are promoted to BLOCK if no escalation handler is set.

    Optionally integrates with AuditLogger for decision logging.
    """

    def __init__(
        self,
        audit_logger: AuditLogger | None = None,
        fail_closed: bool = True,
    ) -> None:
        self._plugins: list[PDPPlugin] = []
        self._audit_logger = audit_logger
        self._fail_closed = fail_closed

    def register(self, plugin: PDPPlugin) -> None:
        """Register an enforcement plugin."""
        self._plugins.append(plugin)
        self._plugins.sort(key=lambda p: p.priority)

    def evaluate(
        self,
        bundle: Any,
        content: str,
        session_id: str | None = None,
        user_id: str | None = None,
        **metadata: Any,
    ) -> EnforcementResult:
        """Evaluate content against all registered plugins.

        Args:
            bundle: VCP Bundle (or None if no bundle present)
            content: The content/prompt being evaluated
            session_id: Optional session identifier
            user_id: Optional user identifier
            **metadata: Additional context (e.g. verification_result, adherence_level)

        Returns:
            EnforcementResult with aggregate decision from all plugins.
        """
        start = time.monotonic()

        ctx = EvaluationContext(
            bundle=bundle,
            content=content,
            session_id=session_id,
            user_id=user_id,
            metadata=metadata,
        )

        decisions: list[PDPDecision] = []
        for plugin in self._plugins:
            try:
                decision = plugin.evaluate(ctx)
                if decision is not None:
                    decisions.append(decision)
            except Exception:
                logger.exception("Plugin %s raised an exception", plugin.plugin_id)
                if self._fail_closed:
                    decisions.append(
                        PDPDecision(
                            decision=DecisionType.BLOCK,
                            reason=f"Plugin {plugin.plugin_id} crashed — fail-closed",
                            plugin_id=plugin.plugin_id,
                            confidence=1.0,
                        )
                    )

        # Determine final decision: any BLOCK or ESCALATE → BLOCK
        final = DecisionType.ALLOW
        for d in decisions:
            if d.decision == DecisionType.BLOCK:
                final = DecisionType.BLOCK
                break
            if d.decision == DecisionType.ESCALATE:
                final = DecisionType.BLOCK  # No escalation handler → fail-closed
            if d.decision == DecisionType.TRANSFORM and final == DecisionType.ALLOW:
                final = DecisionType.TRANSFORM

        duration_ms = int((time.monotonic() - start) * 1000)

        return EnforcementResult(
            final_decision=final,
            decisions=decisions,
            duration_ms=duration_ms,
            plugins_evaluated=len(self._plugins),
        )
