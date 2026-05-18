#!/usr/bin/env bash
# Mode A driver. Walks every scenario in order, sleeps for the
# debounce+poller window, then pauses so you can manually verify and
# merge the resulting PR before moving on.
#
# Usage:
#   ./tests/auto_update_scenarios/run-all.sh
#   ./tests/auto_update_scenarios/run-all.sh 03-delete-public-endpoint    # run from a specific scenario
#
# Expected total runtime: ~7 min per scenario × 7 = ~50 min wall time.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DEBOUNCE_SLEEP_SECONDS=420   # 5-min debounce + up to 5 min for poller

# If a starting scenario was given, skip earlier ones.
START_FROM="${1:-}"
FOUND_START="${START_FROM:+false}"
FOUND_START="${FOUND_START:-true}"

cd "$REPO_ROOT"

# Sanity check: working tree should be clean before we start applying scenarios.
if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "ERROR: working tree is dirty. Run reset.sh or commit/stash first." >&2
    exit 1
fi

for scenario_dir in "$SCRIPT_DIR"/0*-*; do
    [ -d "$scenario_dir" ] || continue
    name="$(basename "$scenario_dir")"

    if [ "$FOUND_START" = "false" ]; then
        if [ "$name" = "$START_FROM" ]; then
            FOUND_START=true
        else
            echo "Skipping $name (before $START_FROM)"
            continue
        fi
    fi

    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo "  Scenario: $name"
    echo "════════════════════════════════════════════════════════════════"

    if [ ! -f "$scenario_dir/apply.sh" ]; then
        echo "  No apply.sh in $scenario_dir, skipping." >&2
        continue
    fi
    if [ ! -f "$scenario_dir/message.txt" ]; then
        echo "  No message.txt in $scenario_dir, skipping." >&2
        continue
    fi

    echo "  Applying changes…"
    bash "$scenario_dir/apply.sh"

    # 07-debounce-burst applies + commits + pushes itself (3 commits).
    # Other scenarios just modify files; we commit+push them here.
    if [ "$name" = "07-debounce-burst" ]; then
        echo "  (burst scenario handled its own push)"
    else
        git add -A
        git commit -F "$scenario_dir/message.txt"
        git push origin main
    fi

    echo "  Pushed. Sleeping ${DEBOUNCE_SLEEP_SECONDS}s for debounce + poller…"
    sleep "$DEBOUNCE_SLEEP_SECONDS"

    echo ""
    echo "  Now go review the PR on the docs repo."
    echo "  Expected behavior is in $scenario_dir/expected.md."
    echo ""
    echo "  MODE A: merge the PR before continuing so the next scenario"
    echo "  runs against an up-to-date docs baseline."
    echo ""
    read -r -p "  Press enter when the PR is merged (or to skip)… " _
done

echo ""
echo "All scenarios complete. Run show-outcomes.sh to inspect the autodoc_pr_outcomes table."
