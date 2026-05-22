#!/usr/bin/env bash
# Reset the test repo to a clean baseline for an auto-update test run.
#
# Resets BOTH halves of the baseline so they can't drift apart:
#   1. git      — main -> the BASELINE_TAG commit (force-push)
#   2. DynamoDB — autodoc_auto_update_state.last_commit_sha -> that same commit
#
# Step 2 matters: without it, reset.sh's own force-push triggers the
# auto-updater from a stale pointer — you get a spurious PR, and every
# scenario then diffs from the wrong baseline.
#
# Destructive — force-pushes to origin. Only safe on the dedicated test repo.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASELINE_TAG="$(cat "$SCRIPT_DIR/BASELINE_TAG" | tr -d '[:space:]')"

if [ -z "$BASELINE_TAG" ]; then
    echo "ERROR: $SCRIPT_DIR/BASELINE_TAG is empty. Set it to the baseline tag name." >&2
    exit 1
fi

# Pointer key — identifies the autodoc_auto_update_state row to reseed.
if [ -z "${ETCHBLOK_PROJECT_ID:-}" ] || [ -z "${ETCHBLOK_VERSION_ID:-}" ]; then
    echo "ERROR: set ETCHBLOK_PROJECT_ID and ETCHBLOK_VERSION_ID first —" >&2
    echo "reset.sh reseeds the auto-update pointer and needs them:" >&2
    echo "  export ETCHBLOK_PROJECT_ID='<owner_id>#<repo_id>'" >&2
    echo "  export ETCHBLOK_VERSION_ID='v1'" >&2
    echo "(they match project_id / version_id on your autodoc_pr_outcomes rows)" >&2
    exit 1
fi

for cmd in git aws; do
    command -v "$cmd" >/dev/null 2>&1 || { echo "ERROR: '$cmd' not in PATH." >&2; exit 1; }
done

# Sanity check: don't run this in any repo that isn't etchblok-test-api
REPO_NAME="$(basename "$(git rev-parse --show-toplevel)")"
if [ "$REPO_NAME" != "etchblok-test-api" ]; then
    echo "ERROR: reset.sh refuses to run in '$REPO_NAME'. Only safe in etchblok-test-api." >&2
    exit 1
fi

# 1. Reset the source branch.
echo "Resetting main → $BASELINE_TAG (force-push)…"
git fetch --tags
git checkout main
git reset --hard "$BASELINE_TAG"
git push origin main --force-with-lease
BASELINE_SHA="$(git rev-parse HEAD)"

# 2. Reseed the auto-update pointer to that same commit, so reset.sh's own
#    force-push lands as a no-op cycle (baseline == latest), not a spurious PR.
echo "Reseeding autodoc_auto_update_state → ${BASELINE_SHA:0:8}…"
aws dynamodb put-item \
    --region "${AWS_REGION:-us-east-1}" \
    --table-name autodoc_auto_update_state \
    --item "{\"project_id\": {\"S\": \"$ETCHBLOK_PROJECT_ID\"}, \"version_id\": {\"S\": \"$ETCHBLOK_VERSION_ID\"}, \"last_commit_sha\": {\"S\": \"$BASELINE_SHA\"}, \"updated_at\": {\"N\": \"0\"}}"

echo "Done — source + pointer both at $BASELINE_TAG (${BASELINE_SHA:0:8})."
