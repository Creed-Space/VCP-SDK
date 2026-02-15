# Governance

This document describes the governance model for the Value-Context Protocol (VCP) specification and SDK.

## Maintainers

| Name | Role | GitHub |
|------|------|--------|
| Nell Watson | Lead maintainer | [@nellwatson](https://github.com/nellwatson) |
| Creed Space Team | Core contributors | [@Creed-Space](https://github.com/Creed-Space) |

## Change Categories

Changes to the VCP specification and SDK follow different approval processes depending on scope and risk:

| Category | Examples | Approval |
|----------|----------|----------|
| **Typo / Docs** | Spelling fix, clarification, broken link | 1 reviewer |
| **Bug Fix** | SDK correctness fix, test addition | 1 maintainer review + CI green |
| **SDK Enhancement** | New helper function, performance improvement | 1 maintainer review + CI green |
| **Spec Addition** | New field, new layer feature, new schema | VEP process (see below) |
| **Breaking Change** | Field removal, semantic change, format change | All maintainers + VEP process |

## VCP Enhancement Proposals (VEPs)

Significant specification changes follow the VEP process:

### Lifecycle

1. **Submit** -- Open a [Spec Amendment](https://github.com/Creed-Space/vcp-sdk/issues/new?template=spec_amendment.yml) issue describing the proposed change, motivation, and backward-compatibility impact.

2. **Triage** -- A maintainer assigns a VEP number (e.g., VEP-0001) and labels the issue.

3. **Discussion** -- 7-14 day discussion period. Community feedback is collected on the issue. Breaking changes require a minimum 14-day discussion period.

4. **Decision** -- Maintainers review and decide: **accepted**, **revised**, or **declined**. The decision and rationale are recorded on the issue.

5. **Implementation** -- Accepted VEPs are implemented via pull request. The PR must include:
   - Specification text updates
   - SDK implementation (Python reference + at least one other SDK)
   - Tests covering the new behavior
   - Schema updates if applicable

6. **Release** -- Changes are included in the next specification version.

### VEP Numbering

VEPs are numbered sequentially: VEP-0001, VEP-0002, etc. The issue title is prefixed with the VEP number once assigned.

## Decision Records

Significant architectural decisions are recorded as comments on the relevant VEP issue or in `docs/decisions/` for cross-cutting concerns.

## Process for Contributors

See [CONTRIBUTING.md](./CONTRIBUTING.md) for development setup, coding standards, and pull request guidelines.

## Amendments

This governance document can be updated through the standard PR process with approval from at least one maintainer.
