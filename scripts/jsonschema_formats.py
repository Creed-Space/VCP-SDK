"""Dependency-free strict format checks used by repository JSON Schemas."""

from __future__ import annotations

import re
from datetime import datetime, timezone

from jsonschema import FormatChecker

RFC3339_DATE_TIME = re.compile(
    r"^(?P<year>[0-9]{4})-(?P<month>[0-9]{2})-(?P<day>[0-9]{2})"
    r"[Tt](?P<hour>[0-9]{2}):(?P<minute>[0-9]{2}):(?P<second>[0-9]{2})"
    r"(?:\.[0-9]+)?(?P<zone>[Zz]|[+-][0-9]{2}:[0-9]{2})$"
)


def is_rfc3339_date_time(value: object) -> bool:
    """Return whether a string is a semantically valid RFC 3339 date-time."""
    if not isinstance(value, str):
        return True
    match = RFC3339_DATE_TIME.fullmatch(value)
    if match is None:
        return False
    parts = {
        name: int(match[name])
        for name in (
            "year",
            "month",
            "day",
            "hour",
            "minute",
            "second",
        )
    }
    if parts["second"] > 59:
        return False
    try:
        datetime(
            parts["year"],
            parts["month"],
            parts["day"],
            parts["hour"],
            parts["minute"],
            parts["second"],
            tzinfo=timezone.utc,
        )
    except ValueError:
        return False
    zone = match["zone"]
    if zone not in {"Z", "z"}:
        return int(zone[1:3]) <= 23 and int(zone[4:6]) <= 59
    return True


def strict_format_checker() -> FormatChecker:
    """Return a checker that never silently omits RFC 3339 validation."""
    checker = FormatChecker()
    checker.checks("date-time")(is_rfc3339_date_time)
    return checker
