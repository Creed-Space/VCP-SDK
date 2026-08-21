"""Regression tests for the standalone SDK public-contract boundary."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.validate_public_contract import validate_standalone_python_sdk

BOUNDARY_README = """
This is a legacy standalone implementation candidate and not the
project-maintained VCP-SDK. This confirms no PyPI release or registry package name is claimed.
The maintained SDK and this candidate both use the `vcp` Python import namespace and
require separate virtual environments.
"""


class StandalonePythonSdkTests(unittest.TestCase):
    def make_candidate(self, root: Path, readme: str = BOUNDARY_README) -> None:
        (root / "src" / "vcp").mkdir(parents=True)
        (root / "pyproject.toml").write_text(
            '[project]\nname = "vcp-sdk"\nversion = "0.7.0"\n', encoding="utf-8"
        )
        (root / "README.md").write_text(readme, encoding="utf-8")

    def test_accepts_explicit_isolated_source_candidate_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_candidate(root)
            problems: list[str] = []
            self.assertEqual(
                validate_standalone_python_sdk(problems, root),
                ("vcp-sdk", "0.7.0"),
            )
            self.assertEqual(problems, [])

    def test_rejects_maintained_name_and_missing_isolation_disclosure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_candidate(root, "legacy standalone implementation candidate")
            (root / "pyproject.toml").write_text(
                '[project]\nname = "value-context-protocol"\nversion = "0.7.0"\n',
                encoding="utf-8",
            )
            problems: list[str] = []
            validate_standalone_python_sdk(problems, root)
            self.assertTrue(
                any(
                    "must not claim the maintained SDK distribution" in item
                    for item in problems
                )
            )
            self.assertTrue(
                any("separate virtual environments" in item for item in problems)
            )

    def test_rejects_registry_install_claim_in_source_only_sibling(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_candidate(root, BOUNDARY_README + "\npip install vcp\n")
            problems: list[str] = []
            validate_standalone_python_sdk(problems, root)
            self.assertTrue(
                any("registry install command" in item for item in problems)
            )


if __name__ == "__main__":
    unittest.main()
