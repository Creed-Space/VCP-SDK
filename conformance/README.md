# VCP conformance corpus

This directory contains authored, language-neutral fixtures and checked runners
for the Value-Context Protocol source candidate. The corpus currently contains
27 JSON fixtures and 337 cases. Presence in the corpus is not a pass.
[`coverage-manifest.json`](coverage-manifest.json) is the machine-readable
authority for every vector's source, applicability, runner, fixture hash, and
Python, Rust, and WebMCP status.

The status vocabulary is deliberately strict:

| Status | Meaning |
|:---|:---|
| `checked` | The named runner executed the vector against that implementation. |
| `unsupported` | The implementation does not claim the profile. This is not a pass. |
| `not_applicable` | The vector is documentation-only or outside that implementation surface. |

A local `checked` result establishes behavior only for the exact source
fingerprint in its report. It does not establish independent implementation,
certification, registry publication, deployed behavior, or third-party
attestation.

## Coverage map

| Directory | Coverage | Checked runner |
|:---|:---|:---|
| `identity/` | Token parsing, canonicalization, hierarchy, and patterns | `identity_parity.py` |
| `transport/` | Content, hashes, JCS manifests, signatures, bundles, temporal and content policy | `transport_parity.py` |
| `semantics/` | CSM-1, personas, and layered composition | `csm1_parity.py`, `persona_parity.py`, `composition_parity.py` |
| `adaptation/` | Context encoding, lifecycle, and messaging | `context_parity.py`, `state_machine_conformance.py`, `messaging_conformance.py` |
| `interop/` | Complete signed bundles and cross-implementation roundtrips | `interop_parity.py` |
| `security/` | Revocation responses and fail-closed scope decisions | `security_parity.py` |
| `extensions/` | Negotiation, consensus, personal, competence, relational, torch, and drafts | Profile-specific runners |
| `runners/` | Executable checks and aggregate reporting | `run_all.py` |

Welfare and stateless MCP fixtures are draft profiles without claimed SDK
implementations. They remain visibly `unsupported`, rather than being counted
as passes. WebMCP capability-negotiation and relational behavior vectors run
through the declared cross-runtime conformance runners. Separately, the packed
npm artifact is imported and exercised against the experimental
`document.modelContext` lifecycle.

## Run the complete gate

From the repository root, using the locked development environment:

```bash
python3 scripts/generate_conformance_coverage.py --check
python3 conformance/runners/run_all.py
```

Or run:

```bash
make conformance PYTHON=/path/to/locked/python
```

The aggregate runner builds the Rust CLI once, executes all checked profiles,
runs the packed WebMCP artifact smoke test, and writes:

```text
conformance/reports/latest.json
conformance/reports/badge.json
conformance/reports/profiles/*.json
```

The generated badge is labelled `VCP local suite`, remains non-publishable, and
contains source identity, issue time, 30-day expiry, supersession, and
revocation fields. `scripts/validate_conformance_claim.py` rejects an expired,
revoked, superseded, or publicly enabled source-only claim. The publication
state currently prohibits public conformance badges.

The aggregate report is validated by
`schemas/vcp-conformance-aggregate-report.schema.json`. It binds results to the
Git HEAD, dirty-tree flag, complete source fingerprint, fixture hashes,
coverage-manifest hash, tool versions, commands, bounded output, and per-profile
structured reports. Generated reports are ignored local evidence. CI uploads
them as candidate-bound artifacts. The badge is generated from the aggregate
result and cannot overstate it.

To intentionally refresh vector coverage after adding or changing a fixture:

```bash
make conformance-coverage PYTHON=/path/to/locked/python
python3 scripts/generate_conformance_coverage.py --check
```

## Fixture format

Most protocol files use a `vectors` array. Extensions use `test_cases`. Every
case has a stable ID, description, input or procedure, and expected outcome.
Fixture-level `suite` and `version` fields identify the profile. The generated
coverage manifest supplies the canonical Spec pointer and execution status.

Situational context dimensions are pipe-separated. U+2016 DOUBLE VERTICAL LINE
separates situational and personal bands. Personal fields use the canonical
names `cognitive_state`, `emotional_tone`, `energy_level`,
`perceived_urgency`, and `body_signals`, each with `value` and `intensity`.

## Maintaining the corpus

1. Link semantic changes to a canonical Spec section or accepted VEP.
2. Update positive, negative, boundary, malformed, and roundtrip cases together.
3. Preserve stable IDs and retain versioned historical fixtures when semantics differ.
4. Update every affected implementation and checked runner.
5. Regenerate `coverage-manifest.json`; its `--check` mode must pass.
6. Run the aggregate gate and all language, package, schema-sync, and repository checks.
7. Record immutable Spec and SDK commits before making any conformance claim.
8. Run installed-artifact verification for release candidates; source checks do not prove shipped artifacts.

## Licence

The fixture corpus is distributed under CC BY 4.0. SDK package code remains
under the root MIT licence. The final file-class licensing matrix remains an
authorized legal-review gate and must be confirmed before publication.
