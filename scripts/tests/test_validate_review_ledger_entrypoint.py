"""Regression coverage for the review-ledger command entry point."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class ReviewLedgerEntrypointTests(unittest.TestCase):
    def test_direct_script_invocation_resolves_local_schema_helpers(self) -> None:
        result = subprocess.run(
            (sys.executable, "scripts/validate_review_ledger.py"),
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("review ledger validation passed", result.stdout.lower())


if __name__ == "__main__":
    unittest.main()
