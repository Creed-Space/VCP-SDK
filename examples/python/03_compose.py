"""Compose two constitutions using the VCP composition engine."""
from __future__ import annotations

from vcp.semantics.composer import Composer, Constitution
from vcp.types import CompositionMode

# -- 1. Define two constitutions with distinct rules. --
safety = Constitution(
    id="family.safe.guide",
    rules=["Always use age-appropriate language", "Never discuss weapons"],
    priority=1,
)
learning = Constitution(
    id="education.tutor.math",
    rules=["Encourage step-by-step reasoning", "Celebrate small victories"],
    priority=0,
)

# -- 2. Compose in OVERRIDE mode (later constitutions win conflicts). --
composer = Composer()
result = composer.compose([safety, learning], mode=CompositionMode.OVERRIDE)

print(f"Mode:  {result.mode_used.value}")
print(f"Rules ({len(result.merged_rules)}):")
for rule in result.merged_rules:
    print(f"  - {rule}")

if result.warnings:
    print(f"Warnings: {result.warnings}")
