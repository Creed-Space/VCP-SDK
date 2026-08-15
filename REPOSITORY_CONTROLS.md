# Repository security controls

**Status:** repository security features applied; branch protection pending candidate integration
**Observed:** 2026-08-15 through authenticated GitHub API changes and readback

The current `main` protection exists, but its required contexts are stale:
`Python SDK (3.12)`, `Rust SDK`, `TypeScript / WebMCP SDK`, and
`Validate JSON Schemas`. Conversation resolution, administrator enforcement,
code-owner review, last-push approval, and signed commits are not required. No
repository ruleset exists.

Private vulnerability reporting, Dependabot alerts and security updates, secret
scanning, push protection, non-provider patterns, and validity checks are
enabled. Default workflow permissions are read-only, Actions cannot approve
pull requests, and repository metadata and topics are current. Code scanning
reports no completed analysis before this candidate is integrated.

The candidate adds CodeQL and dependency-review workflows and records the
intended final state in `.github/repository-policy.json`. Source files cannot
safely replace branch protection. The stale protection is retained until the
candidate is integrated so future context names cannot deadlock the present
merge. An authorized repository administrator must apply the final policy after
the candidate workflows produce their exact context names.

## Acceptance probe

1. Read `.github/repository-policy.json` from the immutable candidate.
2. Confirm every listed context has completed at least once on `main`.
3. Replace stale contexts with the listed current contexts.
4. Enable pull requests, one approval, stale-review dismissal, code-owner and
   last-push approval, conversation resolution, administrator enforcement, and
   force-push and deletion blocks.
5. Confirm dependency graph, Dependabot alerts and security updates, secret
   scanning, push protection, non-provider patterns, and validity checks remain
   enabled. Confirm CodeQL has uploaded analysis.
6. Keep default workflow permissions read-only. Grant job-specific permissions
   only inside reviewed workflows.
7. Open a test pull request. Demonstrate that missing checks, unresolved
   conversation, absent review, a secret push, and a vulnerable dependency are
   blocked.
8. Retain API readback, check-run URLs, and the test pull request as external
   evidence.

Working signal: `external_state_applied` is updated only after readback evidence
matches every desired field, and no stale context can permanently block or
silently bypass a merge.
