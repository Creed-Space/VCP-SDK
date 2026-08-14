# Repository security controls

**Status:** desired state recorded; external application pending
**Observed:** 2026-08-14 through read-only GitHub API calls

The current `main` protection exists, but its required contexts are stale:
`Python SDK (3.12)`, `Rust SDK`, `TypeScript / WebMCP SDK`, and
`Validate JSON Schemas`. Conversation resolution, administrator enforcement,
code-owner review, last-push approval, and signed commits are not required.
No repository ruleset exists. Secret scanning is disabled. Code scanning reports
no analysis.

The candidate adds immutable CodeQL and dependency-review workflows and records
the intended external state in `.github/repository-policy.json`. Source files
cannot enable GitHub features or safely replace branch protection. An authorized
repository administrator must apply the policy after the candidate workflows
have produced their exact context names, then read the settings back and test a
pull request.

## Acceptance probe

1. Read `.github/repository-policy.json` from the immutable candidate.
2. Confirm every listed context has completed at least once on `main`.
3. Replace stale contexts with the listed current contexts.
4. Enable pull requests, one approval, stale-review dismissal, code-owner and
   last-push approval, conversation resolution, administrator enforcement, and
   force-push and deletion blocks.
5. Enable dependency graph, Dependabot alerts and security updates, secret
   scanning, push protection, validity checks, and CodeQL.
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
