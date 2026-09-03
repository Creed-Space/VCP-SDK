# VCP-SDK Repository Guide

This repository contains the Python, Rust, and WebMCP implementations of the
Value Context Protocol. VCP-Spec owns normative protocol text. VCP-Demo-Site owns
the maintained interactive demonstration.

## Layout

* `python/`: the `value-context-protocol` distribution, imported as `vcp`
* `rust/`: the `vcp-core`, `vcp-cli`, and `vcp-wasm` workspace
* `webmcp/`: the `@creedspace/vcp-sdk` browser package
* `schemas/`: synchronized and SDK-owned schema copies
* `conformance/`: authored language-neutral fixtures and checked runners
* `examples/`: runnable integration examples
* `website/`: archive notice for the retired partial site copy

## Required checks

Run `make validate` for repository contracts, then the full checks documented
in [CONTRIBUTING.md](CONTRIBUTING.md) for each touched package. Schema changes
also require `scripts/check_schema_sync.py` against the exact Spec candidate.

Verification, trust, revocation, privacy, replay, budget, and hook failures must
remain fail closed. Tests and examples may use generated keys, but committed
private keys and live credentials are forbidden.
