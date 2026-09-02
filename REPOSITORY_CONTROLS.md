# Repository security controls

**Status:** repository security features and the desired `main` branch protection are applied
**Observed:** 2026-09-02 through authenticated GitHub API readback (`gh api repos/Creed-Space/VCP-SDK/branches/main/protection`)

The current `main` protection requires exactly the eleven contexts listed in
`.github/repository-policy.json` `desired.required_checks` with strict
up-to-date status checks, one approving review, stale-review dismissal,
code-owner review, last-push approval, conversation resolution, and
administrator enforcement; force pushes and deletions are blocked. No
repository ruleset exists. CodeQL analyses for `actions`,
`javascript-typescript`, `python`, and `rust` were uploaded on 2026-09-01.

Private vulnerability reporting, Dependabot alerts and security updates, secret
scanning, push protection, non-provider patterns, and validity checks are
enabled. Default workflow permissions are read-only, Actions cannot approve
pull requests, and repository metadata and topics are current.

`.github/repository-policy.json` records the desired state and the readback
that matched it. Source files cannot replace branch protection, so the probe
below remains the re-verification procedure whenever a workflow job is renamed
or the policy changes.

## Acceptance probe (re-verification)

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
