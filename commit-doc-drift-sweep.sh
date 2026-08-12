#!/usr/bin/env bash
# Commits + pushes this session's doc drift sweep in VCP-SDK.
# This is the doc-only update on top of the v3.2/VEP-0004 work the
# earlier sessions already pushed.
#
# Run from repo root: bash commit-doc-drift-sweep.sh
set -euo pipefail

cd "$(dirname "$0")"

rm -f .git/index.lock
find .git/objects -name 'tmp_obj_*' -delete 2>/dev/null || true

BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "On branch: ${BRANCH}"

FILES=(
  docs/VCP_OVERVIEW.md
  docs/VCP_NEWCOMER_GUIDE.md
  docs/VCP_CONTEXT_DATA_FLOW.md
  docs/VCP_IMPLEMENTATION_GUIDE.md
  docs/VCP_INTEGRATION.md
  docs/context/VCP_CONTEXT_SPECIFICATION.md
  docs/adaptation/VCP_ADAPTATION.md
  python/src/mcp/vcp_server.py
)

git add "${FILES[@]}"

echo
echo "Staged for commit:"
git diff --cached --stat
echo
echo "Press Enter to commit + push..."
read -r

git commit -m "docs: CULTURE drift sweep + v3.2 emoji showcase block

- Replace nationality-based CULTURE values across user-facing docs with
  spec-aligned communication styles (high_context/low_context/formal/
  casual/mixed). Includes the 12-row CULTURE table in
  VCP_CONTEXT_SPECIFICATION.md.
- Modernise the v3.0 emoji showcase block (Appendix A) in
  VCP_CONTEXT_SPECIFICATION.md and VCP_ADAPTATION.md to the current
  18-dim model: drop deprecated STATE-as-situational, add SYSTEM_CONTEXT
  at position 9, add the four VEP-0004 dimensions (EMBODIMENT, PROXIMITY,
  RELATIONSHIP, FORMALITY), and list the 5 personal-state R-line
  dimensions.
- Update python/src/mcp/vcp_server.py docstring (LLM-facing) so the
  CULTURE dimension list it advertises matches the v3.2 encoder."

git push origin "${BRANCH}"

echo
echo "Done."
git log --oneline -n 1
