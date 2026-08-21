"""Regression tests for the scope and coverage of integrated validation."""

from __future__ import annotations

import unittest

from scripts.validate_ecosystem import checks_for, success_summary


class EcosystemValidationScopeTests(unittest.TestCase):
    def test_full_mode_runs_maintained_sdk_and_demo_coverage(self) -> None:
        commands = {
            (check.repository, check.command) for check in checks_for("full", "python")
        }
        self.assertIn(("sdk", ("make", "coverage", "PYTHON=python")), commands)
        self.assertIn(("demo", ("npm", "run", "test:coverage")), commands)
        self.assertNotIn(("demo", ("npm", "test")), commands)

    def test_completion_line_cannot_imply_five_surface_coverage(self) -> None:
        summary = success_summary("full", 42, 1.25)
        self.assertIn("Demo/Spec/SDK", summary)
        self.assertIn("Scope excludes Inspector and standalone Python SDK", summary)


if __name__ == "__main__":
    unittest.main()
