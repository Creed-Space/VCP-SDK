"""Regression tests for repository JSON ingestion invariants."""

from __future__ import annotations

import unittest

from scripts.validate_repo import (
    DuplicateJsonKeyError,
    NonFiniteJsonNumberError,
    strict_json_loads,
)


class StrictJsonTests(unittest.TestCase):
    def test_accepts_same_key_in_distinct_objects(self) -> None:
        self.assertEqual(
            strict_json_loads('{"left":{"id":1},"right":{"id":2}}'),
            {"left": {"id": 1}, "right": {"id": 2}},
        )

    def test_rejects_literal_and_escaped_duplicate_keys(self) -> None:
        with self.assertRaisesRegex(DuplicateJsonKeyError, "duplicate object key 'id'"):
            strict_json_loads('{"\\u0069d":1,"id":2}')

    def test_rejects_exponents_that_overflow_runtime_float_range(self) -> None:
        with self.assertRaisesRegex(NonFiniteJsonNumberError, "non-finite number"):
            strict_json_loads('{"maximum":1e999}')


if __name__ == "__main__":
    unittest.main()
