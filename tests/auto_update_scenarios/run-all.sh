#!/usr/bin/env bash
# Mode A driver. Walks every scenario in order, sleeps for the
# debounce+poller window, then pauses so you can manually verify and
# merge the resulting PR before moving on.
#
# Usage:
#   ./tests/auto_update_scenarios/run-all.sh
#   ./tests/auto_update_scenarios/run-all.sh 03-delete-public-endpoint    # run from a specific scenario
#
# Expected total runtime: ~7 min per scenario, plus a double cycle for
# 08-pr-refresh — roughly 65-70 min wall time for all 8.

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

    # 08-pr-refresh is special: two pushes with NO merge between them, to
    # verify the second push refreshes the SAME PR instead of opening a
    # new one. It ships apply-1.sh / apply-2.sh instead of one apply.sh.
    if [ "$name" = "08-pr-refresh" ]; then
        echo "  Push 1/2: applying first change…"
        bash "$scenario_dir/apply-1.sh"
        git add -A
        git commit -F "$scenario_dir/message-1.txt"
        git push origin main
        echo "  Push 1 pushed. Sleeping ${DEBOUNCE_SLEEP_SECONDS}s for debounce + poller…"
        sleep "$DEBOUNCE_SLEEP_SECONDS"
        echo ""
        echo "  Confirm ONE auto-update PR has opened on the docs repo"
        echo "  (branch etchblok/auto-update-<version>). Note its number."
        echo "  Do NOT merge it — push 2 must land while it is still open."
        echo ""
        read -r -p "  Press enter once that PR is open (then I push change 2)… " _

        echo "  Push 2/2: applying second change…"
        bash "$scenario_dir/apply-2.sh"
        git add -A
        git commit -F "$scenario_dir/message-2.txt"
        git push origin main
        echo "  Push 2 pushed. Sleeping ${DEBOUNCE_SLEEP_SECONDS}s for debounce + poller…"
        sleep "$DEBOUNCE_SLEEP_SECONDS"
        echo ""
        echo "  Verify the SAME PR was refreshed — same number, a force-push"
        echo "  in its timeline, now covering both SearchIndex sections, and"
        echo "  still ONE row in autodoc_pr_outcomes. A second PR = failure."
        echo "  Full expectations: $scenario_dir/expected.md"
        echo "  Then merge the PR to advance the auto-update pointer."
        echo ""
        read -r -p "  Press enter once verified + merged… " _
        continue
    fi

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
    echo "  Review the PR on the docs repo — expected behavior is in"
    echo "  $scenario_dir/expected.md."
    echo ""
    echo "  MODE A: merge the PR before continuing. Merging advances the"
    echo "  auto-update pointer (autodoc_auto_update_state) — only then"
    echo "  does the next scenario diff from a fresh baseline. Skipping"
    echo "  the merge folds this change into the next scenario's PR."
    echo "  (Scenarios 04 and 06 expect no PR — nothing to merge.)"
    echo ""
    read -r -p "  Press enter to continue… " _
done

echo ""
echo "All scenarios complete. Run show-outcomes.sh to inspect the autodoc_pr_outcomes table."
