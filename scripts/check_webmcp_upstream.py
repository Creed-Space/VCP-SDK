#!/usr/bin/env python3
"""Compare the reviewed WebMCP contract with the bounded upstream source."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT = ROOT / "webmcp" / "upstream-contract.json"
ALLOWED_HOST = "raw.githubusercontent.com"
USER_AGENT = "VCP-WebMCP-contract-watcher/1"


def load_contract(path: Path) -> dict[str, Any]:
    """Load and validate the small checked-in watcher contract."""
    contract = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(contract, dict):
        raise TypeError("contract must be a JSON object")
    required = {
        "schema",
        "reviewed_at",
        "upstream_commit",
        "source_url",
        "sha256",
        "maximum_bytes",
        "required_fragments",
        "forbidden_fragments",
    }
    if set(contract) != required:
        raise ValueError(
            f"contract fields differ: missing={sorted(required - set(contract))}, "
            f"unexpected={sorted(set(contract) - required)}"
        )
    if contract["schema"] != "vcp-webmcp-upstream-contract/1":
        raise ValueError("unsupported contract schema")
    source = urlsplit(contract["source_url"])
    if source.scheme != "https" or source.hostname != ALLOWED_HOST:
        raise ValueError("source URL must use HTTPS on raw.githubusercontent.com")
    if not isinstance(contract["maximum_bytes"], int) or not (
        1 <= contract["maximum_bytes"] <= 4 * 1024 * 1024
    ):
        raise ValueError("maximum_bytes must be between 1 byte and 4 MiB")
    if not isinstance(contract["sha256"], str) or len(contract["sha256"]) != 64:
        raise ValueError("sha256 must be a 64-character digest")
    for field in ("required_fragments", "forbidden_fragments"):
        values = contract[field]
        if (
            not isinstance(values, list)
            or any(not isinstance(value, str) or not value for value in values)
            or len(values) != len(set(values))
        ):
            raise ValueError(f"{field} must be a unique list of non-empty strings")
    return contract


def fetch_source(url: str, maximum_bytes: int) -> bytes:
    """Fetch one exact HTTPS resource with bounded memory and no redirect trust."""
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/plain"})
    with urlopen(request, timeout=30) as response:
        if response.geturl() != url:
            raise ValueError(
                f"upstream redirected to an unreviewed URL: {response.geturl()}"
            )
        declared = response.headers.get("Content-Length")
        if declared is not None and int(declared) > maximum_bytes:
            raise ValueError("upstream Content-Length exceeds the configured bound")
        data = response.read(maximum_bytes + 1)
    if len(data) > maximum_bytes:
        raise ValueError("upstream body exceeds the configured bound")
    return data


def evaluate(source: bytes, contract: dict[str, Any]) -> dict[str, Any]:
    """Return bounded semantic and byte-drift evidence without copying source text."""
    decoded = source.decode("utf-8")
    observed = hashlib.sha256(source).hexdigest()
    missing = [
        fragment
        for fragment in contract["required_fragments"]
        if fragment not in decoded
    ]
    forbidden = [
        fragment for fragment in contract["forbidden_fragments"] if fragment in decoded
    ]
    matched = observed == contract["sha256"] and not missing and not forbidden
    return {
        "schema": "vcp-webmcp-upstream-check/1",
        "status": "matched" if matched else "drift",
        "source_url": contract["source_url"],
        "reviewed_at": contract["reviewed_at"],
        "expected_upstream_commit": contract["upstream_commit"],
        "expected_sha256": contract["sha256"],
        "observed_sha256": observed,
        "observed_bytes": len(source),
        "missing_required_fragments": missing,
        "present_forbidden_fragments": forbidden,
        "claim_update_performed": False,
    }


def write_result(path: Path | None, result: dict[str, Any]) -> None:
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if path is None:
        print(encoded, end="")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(encoded, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--source-file", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        contract = load_contract(args.contract)
        source = (
            args.source_file.read_bytes()
            if args.source_file is not None
            else fetch_source(contract["source_url"], contract["maximum_bytes"])
        )
        result = evaluate(source, contract)
    except (
        OSError,
        TypeError,
        UnicodeError,
        ValueError,
        json.JSONDecodeError,
        HTTPError,
        URLError,
    ) as exc:
        result = {
            "schema": "vcp-webmcp-upstream-check/1",
            "status": "error",
            "error_type": type(exc).__name__,
            "error": str(exc)[:500],
            "claim_update_performed": False,
        }
        write_result(args.output, result)
        print(
            f"ERROR: WebMCP upstream check could not complete: {exc}", file=sys.stderr
        )
        return 2
    write_result(args.output, result)
    if result["status"] != "matched":
        print(
            "WebMCP upstream contract changed; review the bounded JSON evidence.",
            file=sys.stderr,
        )
        return 3
    print(f"WebMCP upstream contract matched {result['observed_sha256'][:12]}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
