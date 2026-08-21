"""Regression tests for maintained aggregate gate coverage."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class MakefileContractTests(unittest.TestCase):
    def test_webmcp_gate_runs_branch_aware_coverage(self) -> None:
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
        webmcp_target = makefile.split("\nwebmcp:\n", 1)[1].split("\n\n", 1)[0]
        self.assertIn("npm run test:coverage", webmcp_target)
        self.assertIn("npm run test:packed", webmcp_target)
        self.assertNotIn("npm test", webmcp_target)


if __name__ == "__main__":
    unittest.main()
