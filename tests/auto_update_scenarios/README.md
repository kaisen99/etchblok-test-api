# Auto-Update Scenarios — Mode A Runbook

Reproducible UX test suite for the Etchblok auto-updater. Each
scenario pushes one specific kind of code change to `main` and we
verify the pipeline opens (or correctly doesn't open) a doc PR.

This is **Mode A** — deterministic baseline tests. Mode B1 (realistic
mixed PR outcomes) is deferred until Mode A is reliable.

---

## Scenarios at a glance

| # | Scenario | What it tests | PR expected? |
|---|---|---|---|
| 01 | Rename public method | Symbol diff sees rename as delete + new | Yes |
| 02 | Add optional param | Surgical edit to existing API ref | Yes |
| 03 | Delete public endpoint | `DELETE` action path on affected section | Yes |
| 04 | Add new public method | "New symbol" deferred path | **No** (gap test) |
| 05 | Modify body, same sig | `body_hash` diff, call-graph expansion | Yes |
| 06 | Modify private helper | Private symbols filter | **No** (gap test) |
| 07 | Debounce burst | 3 commits in 90s collapse to one run | Maybe (likely no public diff) |
| 08 | PR refresh | 2 pushes, no merge between — same PR refreshed | Yes (one, refreshed) |

---

## How the single-PR model works

The auto-updater keeps **one stable PR per version**, on the branch
`etchblok/auto-update-{version}`. Each cycle rebuilds that branch from
the published docs plus every doc change since the last merge,
force-pushes it, and refreshes the existing PR (or opens it the first
time).

Two consequences for testing:

- **The pointer advances only on merge.** `autodoc_auto_update_state`
  — the commit the published docs reflect — moves forward *only* when a
  PR is merged (the webhook does it). Creating or closing a PR does not
  move it. So in Mode A you **must merge** each scenario's PR before the
  next scenario, or the next diff runs from the same baseline and the
  changes pile into one PR.

- **Content is read from the published docs branch.** The agent edits
  the live docs on that branch, not an internal snapshot. That is why
  regenerating alone is not enough — you must also **publish** so the
  branch reflects the generation (Step B).

Scenario 08 pushes twice with no merge between to confirm the refresh
path. Every other scenario merges immediately, so each gets its own
fresh PR and never exercises the refresh.

---

## First-time setup (do this once, ever)

### 1. Commit the test scaffolding

```bash
cd ~/code/etchblok-test-api
git add tests/
git commit -m "Add auto-update test scaffolding"
```

### 2. Create the baseline tag

The baseline is what `reset.sh` rolls back to. Make sure HEAD is at
the state you want every test run to start from.

```bash
git tag auto-update-test-baseline
git push origin main auto-update-test-baseline
```

The tag name must match `BASELINE_TAG` in this directory. If you want
a different name, edit `BASELINE_TAG` to match.

### 3. Configure Etchblok

In the Etchblok UI for this repo:
- Create a **continuous** version tracking `main`
- Set the publishing target (e.g., `etchblok-test-api-docs`)
- Set `apiRefExcludeRegex` to `^tests/` so the scaffolding itself
  isn't documented
- Save settings

### 4. Generate the initial docs

Click **Generate** in the Etchblok UI. Wait for completion (~5-15 min).
Open the published docs site and confirm the result looks reasonable —
you should see API refs for `BookmarkService`, route handlers, etc.

You only do steps 1-4 once.

---

## Running a test cycle

Each cycle = reset → regenerate docs → run all 7 scenarios → review
outcomes.

### Step A. Reset source + pointer to baseline

```bash
export ETCHBLOK_PROJECT_ID='<owner_id>#<repo_id>'   # once per shell
export ETCHBLOK_VERSION_ID='v1'
cd ~/code/etchblok-test-api
./tests/auto_update_scenarios/reset.sh
```

`reset.sh` resets **both** halves of the baseline so they can't drift:
- **git** — force-pushes `main` back to `auto-update-test-baseline`
- **DynamoDB** — reseeds `autodoc_auto_update_state` to that same commit

The pointer reseed is what makes reset.sh's own force-push a no-op
cycle rather than a spurious PR. `ETCHBLOK_PROJECT_ID` / `ETCHBLOK_VERSION_ID`
match the `project_id` / `version_id` on your `autodoc_pr_outcomes` rows.
The script refuses to run outside `etchblok-test-api`.

### Step B. Check the docs baseline (Mode A)

Step A already reseeded the pointer. The one thing left to confirm: the
**published docs branch must reflect the baseline source** — the
auto-updater reads section content from it.

If the docs were generated from pristine baseline source and no
auto-update PR has been *merged* into the docs branch, it's already
correct — **nothing to do, go to Step C.**

Only regenerate + publish if the docs branch does **not** match the
baseline — e.g. it was generated while scenario changes were applied
(the `BookmarkService` API ref says `full_text_search` instead of
`search`), or a scenario's PR was merged into the docs branch:

1. In the Etchblok UI, click **Regenerate** on the continuous version
2. Wait for completion (~5-15 min)
3. **Publish**, and make sure it lands on the docs branch — the
   auto-updater reads content from that branch, so the generation must
   actually be on it

### Step C. Run the scenarios

```bash
./tests/auto_update_scenarios/run-all.sh
```

The driver walks scenarios 01 → 08 in order. For each:

1. Runs the scenario's `apply.sh` (modifies source files)
2. Commits with the scenario's `message.txt`
3. Pushes to `origin/main`
4. Sleeps **7 minutes** (5-min debounce + up to 5-min poller)
5. **Pauses** and prompts you to review the PR
6. You **merge** the PR before pressing enter — merging is what
   advances the auto-update pointer (see "How the single-PR model
   works"). If you skip it, the change folds into the next PR.

Scenario 08 is special — it pushes twice with no merge between, so it
runs two cycles (~14 min) and pauses once in the middle.

Total wall time: ~70 minutes for all 8 scenarios.

To skip ahead to a specific scenario (e.g., debugging just #8):

```bash
./tests/auto_update_scenarios/run-all.sh 08-pr-refresh
```

Scenarios before the named one are skipped — this is also how you run
the PR-refresh test on its own.

### Step D. Inspect outcomes

```bash
./tests/auto_update_scenarios/show-outcomes.sh
```

Dumps `autodoc_pr_outcomes` rows from the last 6 hours, grouped by
status. Use `WINDOW_HOURS=24 ./show-outcomes.sh` to widen the window.

Compare against each scenario's `expected.md`:

```bash
less tests/auto_update_scenarios/01-rename-public-method/expected.md
```

---

## What to observe while a scenario runs

During the 7-min sleep, watch these in another terminal/tab:

- **Vercel function logs** for `/api/webhook/github` — should show the
  push event received and pending row written
- **DynamoDB** — `autodoc_pending_updates` table should have a row for
  this repo with `status=pending`; after debounce it transitions to
  `processing` then disappears (or stays as `completed`)
- **Flyte console** — `poll_and_run_auto_updates` fires every 5 min;
  look for an invocation of `doc_auto_update_workflow`
- **GitHub PR list** on the docs repo — the etchblok PR appears on
  branch `etchblok/auto-update-{version}` (one stable branch per
  version, reused and force-pushed across cycles)
- **DynamoDB** — `autodoc_pr_outcomes` should have a row with
  `status=open` after the workflow creates the PR (upserted, so a
  refreshed PR keeps the same row)

After you merge the PR:
- The webhook updates the row to `merged_clean` or `merged_edited`
- The webhook advances `autodoc_auto_update_state.last_commit_sha` to
  the commit the PR covered — this pointer move is what lets the next
  scenario diff from a fresh baseline
- The `etchblok/auto-update-{version}` branch is auto-deleted

After you close a PR **without merging**:
- The row becomes `closed_unmerged` and the pointer does **not** move —
  the change correctly returns in the next cycle's PR

---

## Resetting between runs

Between runs of `run-all.sh`, do:

```bash
./tests/auto_update_scenarios/reset.sh        # source repo → baseline
# Then do Step B — usually just reseed the pointer; regenerate only
# if the docs no longer match the baseline.
```

You do **not** need to manually delete anything from
`autodoc_pr_outcomes` between runs — old rows stay around and the
daily stale-cleanup cron eventually marks orphans `stale_abandoned`.
`show-outcomes.sh` filters by `created_at` so old rows from prior
runs don't clutter the output.

---

## Troubleshooting

### A scenario was pushed but no PR opened after 10 minutes

Possible causes (in order of likelihood):

1. **No publishing settings** — the workflow logs
   `"no published_settings configured ... Skipping PR creation"`.
   Check the Etchblok UI for the repo's publishing config.

2. **The workflow ran but found no public diff** — expected for
   scenarios 04, 06, and possibly 07. Confirm via Flyte logs:
   `"no updated sections, skipping PR"`.

3. **Webhook signature failed** — Vercel logs show
   `"Webhook signature verification failed"`. Check that
   `GITHUB_WEBHOOK_SECRET` matches between GitHub App config and
   Vercel env.

4. **The poller hasn't fired yet** — the Flyte cron is every 5 min,
   so worst case is 5 min + 5 min debounce = 10 min. Wait longer.

### A PR opened but for the wrong scenario

Probably accumulated state from a previous run. Did you reset between
runs (Step A + Step B)? Run `reset.sh`, regenerate docs in the UI,
then re-run.

### Two PRs opened when scenario 08 expected one refreshed

Push 2 was supposed to refresh push 1's PR, not open a new one. Either:

1. **Push 1's PR was already merged** when push 2 ran — then a fresh PR
   is correct. Don't merge push 1's PR until after push 2.
2. **The single-PR path is broken** — check `_find_open_pr` in
   `github_pr_creator.py` (branch-name mismatch, or the open-PR query
   failing).

### A scenario's change showed up in the next scenario's PR

You skipped the merge. The pointer (`autodoc_auto_update_state`) only
advances on merge, so the unmerged change stays in the diff window and
folds into the next PR. Merge each scenario's PR before continuing.

### `reset.sh` refuses to run

The script has a sanity check that the working repo's basename is
`etchblok-test-api`. If you cloned it elsewhere or renamed it, the
script bails. Edit the check in `reset.sh` to your repo's name.

### Scenario's `apply.sh` fails with assertion error

The scenario's anchor text doesn't match the current state of the
source. Either:
- The source moved since the scaffolding was written (rebase your tests
  against latest source structure)
- You forgot to run `reset.sh` first (state is from a previous scenario)

Run `reset.sh` and retry. If it still fails, inspect the Python
heredoc in the scenario's `apply.sh` and adjust the anchor strings.

---

## File-by-file reference

| File | Purpose |
|---|---|
| `BASELINE_TAG` | The git tag name `reset.sh` rolls back to |
| `reset.sh` | Force-pushes main to baseline tag |
| `run-all.sh` | Mode A driver — applies each scenario with pauses |
| `show-outcomes.sh` | Dumps recent rows from autodoc_pr_outcomes |
| `0N-*/apply.sh` | Mutates source files for scenario N |
| `0N-*/message.txt` | Commit message for scenario N |
| `0N-*/expected.md` | Human-readable expected pipeline behavior |

Scenario `08-pr-refresh` is the exception: it ships `apply-1.sh` +
`apply-2.sh` and `message-1.txt` + `message-2.txt` (two pushes) instead
of a single `apply.sh` / `message.txt`.

---

## Mode B1 (deferred)

Once Mode A is stable, Mode B1 will:
- Skip docs regeneration between runs (state accumulates)
- Per-scenario `user_action.sh` simulates realistic close behaviors
  (merge clean / merge edited / close unmerged / leave open)
- Exercises real-world messy PR handling

Don't build Mode B1 until Mode A passes consistently. If basics are
broken, Mode B1 noise will obscure them.
