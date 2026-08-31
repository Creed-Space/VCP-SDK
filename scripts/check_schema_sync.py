#!/usr/bin/env python3
"""Compare canonical schema copies between exact VCP-Spec and VCP-SDK checkouts."""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

COMMON = (
    "vcp-adaptation-context.schema.json",
    "vcp-agent-runtime-profile-v0.1.schema.json",
    "vcp-identity-token.schema.json",
    "vcp-manifest-v1.schema.json",
    "vcp-semantics-csm1.schema.json",
)
SPEC_ONLY = (
    "vcp-capability-handshake.schema.json",
    "vcp-messaging-v1.2.schema.json",
)
SDK_ONLY = (
    "vcp-manifest-v2.schema.json",
    "vcp-messaging-v2.0.schema.json",
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:12]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", required=True, type=Path, help="VCP-Spec checkout")
    parser.add_argument("--sdk", required=True, type=Path, help="VCP-SDK checkout")
    args = parser.parse_args()

    spec = args.spec.resolve() / "schemas"
    sdk = args.sdk.resolve() / "schemas"
    failures: list[str] = []

    for name in COMMON:
        left = spec / name
        right = sdk / name
        if not left.is_file():
            failures.append(f"Spec is missing common schema: {name}")
            continue
        if not right.is_file():
            failures.append(f"SDK is missing common schema: {name}")
            continue
        left_data = left.read_bytes()
        right_data = right.read_bytes()
        if left_data != right_data:
            failures.append(
                f"{name} differs: Spec {digest(left_data)}, SDK {digest(right_data)}"
            )
        else:
            print(f"schema sync OK: {name} ({digest(left_data)})")

    for name in SPEC_ONLY:
        if not (spec / name).is_file():
            failures.append(f"Spec-owned schema is missing: {name}")
        if (sdk / name).exists():
            failures.append(
                f"Spec-owned schema is unexpectedly duplicated in SDK: {name}"
            )

    for name in SDK_ONLY:
        if not (sdk / name).is_file():
            failures.append(f"SDK-owned candidate schema is missing: {name}")
        if (spec / name).exists():
            failures.append(
                f"SDK-owned candidate schema is unexpectedly duplicated in Spec: {name}"
            )

    if failures:
        for failure in failures:
            print(f"ERROR: {failure}", file=sys.stderr)
        return 1
    print("Schema ownership and byte synchronization passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
