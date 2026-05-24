# Testing Approach

<!-- wiki:type = system -->
<!-- wiki:scope = vcp-sdk -->
<!-- wiki:created = 2026-05-23 -->
<!-- wiki:updated = 2026-05-23 -->
<!-- wiki:status = active -->

## Summary

VCP-SDK has three test layers: per-module unit tests in `python/tests/vcp/`, cross-language conformance tests in `conformance/`, and integration examples in `examples/`. The goal is cross-implementation consistency: Python and Rust must produce identical results for identical inputs. (VCP-SDK directory listing; VCP-SDK/CLAUDE.md "Testing")

## Python Test Structure (`python/tests/`)

Organized by layer, mirroring `src/vcp/`:

```
python/tests/
├── conftest.py           # Fixtures for standalone testing
├── vcp/
│   ├── identity/         # Layer 1 tests
│   ├── semantics/        # Layer 3 tests
│   ├── adaptation/       # Layer 4 tests
│   ├── extensions/       # VCP-X-* tests
│   └── hooks/            # Hook system tests
├── test_messaging.py     # VCP/M inter-agent messaging
├── test_metrics.py       # Telemetry
├── test_privacy.py       # Context opacity
├── test_revocation.py    # Bundle revocation
└── test_vectors.py       # Cross-language test vectors
```

(python/tests/vcp/ directory listing)

## Conformance Tests (`conformance/`)

Cross-language conformance organized by layer:

```
conformance/
├── identity/      # Identity layer vectors
├── semantics/     # Semantics layer vectors
├── adaptation/    # Adaptation layer vectors
├── extensions/    # Extension vectors
├── interop/       # Cross-implementation interop tests
└── transport/     # Transport layer vectors
```

(conformance/ directory listing)

The conformance tests define shared test vectors that both Python and Rust must pass. `test_vectors.py` in the Python test suite loads these vectors. This is the primary mechanism ensuring protocol-level compatibility.

## Run Commands

```bash
# All Python tests
pytest tests/

# By layer
pytest tests/vcp/identity/
pytest tests/vcp/semantics/

# With coverage
pytest --cov=src/vcp tests/

# Specific modules
pytest tests/test_vectors.py    # cross-language conformance
```
(VCP-SDK/CLAUDE.md "Testing")

## `conftest.py` Design

`tests/conftest.py` provides basic fixtures for standalone testing — specifically to handle that `integrations/` has Creed Space PDP dependencies. The conftest isolates these so the core SDK tests run without external dependencies. (VCP-SDK/CLAUDE.md "Important Notes")

## Important Constraints

- `integrations/safety_stack/` has Creed Space PDP dependencies — not standalone
- Some tests may reference Creed Space fixtures (conftest.py provides stubs)
- Constitution content is NOT in this repo (VCP transports constitutions, doesn't define them)

(VCP-SDK/CLAUDE.md "Important Notes")

## What Is NOT Tested Here

- Interiora self-modeling scaffold (separate system using VCP)
- Bilateral alignment implementation (informs design, not code)
- Constitution content validity

## Provenance

- Sources consulted: `python/tests/vcp/` directory listing; `conformance/` directory listing; VCP-SDK/CLAUDE.md "Testing" and "Important Notes"
- Last verified against sources: 2026-05-23

## See Also

- [[vcp-sdk:systems/python-sdk-modules]] — modules being tested
- [[vcp-sdk:systems/rust-implementation]] — Rust crate whose behavior conformance tests verify
- [[vcp-sdk:flows/bundle-sign-verify]] — primary flow covered by transport tests
