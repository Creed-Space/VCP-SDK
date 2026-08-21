"""Regression tests for strict schema format validation without optional extras."""

from __future__ import annotations

import unittest

from scripts.jsonschema_formats import is_rfc3339_date_time, strict_format_checker


class DateTimeFormatTests(unittest.TestCase):
    def test_accepts_valid_rfc3339_calendar_and_offset_boundaries(self) -> None:
        for value in (
            "2024-02-29T23:59:59Z",
            "2026-01-01t00:00:00.123456789z",
            "2026-01-01T00:00:00-00:00",
            "9999-12-31T23:59:59+23:59",
        ):
            with self.subTest(value=value):
                self.assertTrue(is_rfc3339_date_time(value))

    def test_rejects_impossible_calendar_clock_and_offset_values(self) -> None:
        for value in (
            "0000-01-01T00:00:00Z",
            "2026-02-29T00:00:00Z",
            "2026-01-01T24:00:00Z",
            "2026-01-01T23:59:60Z",
            "2026-01-01T00:00:00+24:00",
            "2026-01-01T00:00:00+00:60",
        ):
            with self.subTest(value=value):
                self.assertFalse(is_rfc3339_date_time(value))

    def test_checker_registers_date_time_even_without_optional_dependency(self) -> None:
        checker = strict_format_checker()
        self.assertIn("date-time", checker.checkers)
        self.assertFalse(checker.conforms("2026-02-29T00:00:00Z", "date-time"))


if __name__ == "__main__":
    unittest.main()
