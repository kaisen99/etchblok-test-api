#!/usr/bin/env bash
# Reset main to the baseline tag. Destructive — force-pushes to origin.
# Only safe to run on this dedicated test repo.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASELINE_TAG="$(cat "$SCRIPT_DIR/BASELINE_TAG" | tr -d '[:space:]')"

if [ -z "$BASELINE_TAG" ]; then
    echo "ERROR: $SCRIPT_DIR/BASELINE_TAG is empty. Set it to the baseline tag name." >&2
    exit 1
fi

# Sanity check: don't run this in any repo that isn't etchblok-test-api
REPO_NAME="$(basename "$(git rev-parse --show-toplevel)")"
if [ "$REPO_NAME" != "etchblok-test-api" ]; then
    echo "ERROR: reset.sh refuses to run in '$REPO_NAME'. Only safe in etchblok-test-api." >&2
    exit 1
fi

echo "Resetting main → $BASELINE_TAG (force-push)…"
git fetch --tags
git checkout main
git reset --hard "$BASELINE_TAG"
git push origin main --force-with-lease

echo "Done. Working tree is now at $BASELINE_TAG."
echo "Remember: regenerate docs in the Etchblok UI for a clean Mode A run."
