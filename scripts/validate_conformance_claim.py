#!/usr/bin/env python3
"""Validate expiry, supersession, revocation, and publication policy for a claim."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def timestamp(value: object, field: str) -> datetime:
    if not isinstance(value, str):
        raise TypeError(f"{field} must be a date-time string")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError(f"{field} must include a timezone")
    return parsed.astimezone(UTC)


def validate_claim(
    claim: dict[str, Any],
    publication_state: dict[str, Any],
    now: datetime,
) -> list[str]:
    errors: list[str] = []
    try:
        issued = timestamp(claim.get("issued_at"), "issued_at")
        expires = timestamp(claim.get("expires_at"), "expires_at")
    except (TypeError, ValueError) as error:
        return [str(error)]
    if expires <= issued:
        errors.append("expires_at must be after issued_at")
    if now >= expires:
        errors.append("claim is expired")
    if claim.get("revoked_at") is not None:
        try:
            timestamp(claim["revoked_at"], "revoked_at")
        except (TypeError, ValueError) as error:
            errors.append(str(error))
        errors.append("claim is revoked")
    if claim.get("superseded_by") is not None:
        errors.append("claim is superseded")
    if claim.get("status") != "local-source-evidence":
        errors.append("unrecognized claim status")
    if claim.get("publishable") is not False:
        errors.append("local source evidence must not be marked publishable")
    badges_allowed = publication_state.get("public_copy_policy", {}).get(
        "published_badges_allowed"
    )
    if badges_allowed is not False:
        errors.append("publication state does not explicitly prohibit current badges")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("claim_file", type=Path)
    parser.add_argument(
        "--publication-state",
        type=Path,
        default=Path("release/publication-state.json"),
    )
    parser.add_argument("--at", help="Override current time with an RFC 3339 value")
    args = parser.parse_args()
    document = json.loads(args.claim_file.read_text(encoding="utf-8"))
    claim = document.get("claim", document)
    if not isinstance(claim, dict):
        print("claim document does not contain an object")
        return 1
    publication_state = json.loads(args.publication_state.read_text(encoding="utf-8"))
    now = timestamp(args.at, "--at") if args.at else datetime.now(UTC)
    errors = validate_claim(claim, publication_state, now)
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        return 1
    print("Conformance claim is current, local-only, and publication-blocked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
