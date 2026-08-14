# Dependency maintenance policy

Status: maintained candidate policy
Owner: SDK maintainers
Last reviewed: 2026-08-14

Dependabot runs weekly for Python, Rust, root validation tooling, WebMCP, and
GitHub Actions. Compatible minor and patch updates are grouped per ecosystem so
the queue remains bounded and each candidate receives the complete relevant
test matrix.

Major updates remain individual changes. They require release-note review,
compatibility analysis, security-advisory review, installed-artifact checks,
and an explicit semver decision when public behavior or minimum runtimes change.
Security updates may bypass the weekly cadence and grouping when delay creates
material exposure.

An update is closed as superseded only when the candidate lockfile contains an
equal or newer reviewed version and the pull request's exact ecosystem checks
pass on the candidate. A rejection records the affected package, reason,
security consequence, review date, and revisit trigger. An old or conflicting
pull request is not evidence that the underlying update was addressed.

GitHub Actions remain pinned to immutable commit SHAs. Dependabot may update
those pins, but maintainers must verify the advertised release tag and upstream
repository identity before merge.
