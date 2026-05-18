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

### Step A. Reset the source repo to baseline

```bash
cd ~/code/etchblok-test-api
./tests/auto_update_scenarios/reset.sh
```

This force-pushes `main` back to `auto-update-test-baseline`. Safe
because the repo is dedicated to testing — the script refuses to run
if the repo name isn't `etchblok-test-api`.

### Step B. Regenerate docs to a clean baseline (Mode A only)

Mode A assumes each scenario tests against pristine docs. After the
reset, the source code is at baseline — but the **docs repo** still
contains changes from prior scenarios you merged. Regenerate to wipe
that state:

1. In the Etchblok UI, click **Regenerate** on the continuous version
2. Wait for completion (~5-15 min)
3. Optionally: merge the resulting publish PR into the docs repo so
   the on-disk state matches DynamoDB

### Step C. Run the scenarios

```bash
./tests/auto_update_scenarios/run-all.sh
```

The driver walks scenarios 01 → 07 in order. For each:

1. Runs the scenario's `apply.sh` (modifies source files)
2. Commits with the scenario's `message.txt`
3. Pushes to `origin/main`
4. Sleeps **7 minutes** (5-min debounce + up to 5-min poller)
5. **Pauses** and prompts you to review the PR
6. You merge the PR (or close it) before pressing enter

Total wall time: ~50 minutes for all 7 scenarios.

To skip ahead to a specific scenario (e.g., debugging just #5):

```bash
./tests/auto_update_scenarios/run-all.sh 05-modify-body-same-sig
```

Scenarios before the named one are skipped.

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
- **GitHub PR list** on the docs repo — the etchblok PR appears
  (branch name like `etchblok/auto-update-{shortSha}`)
- **DynamoDB** — `autodoc_pr_outcomes` should have a new row with
  `status=open` after the workflow creates the PR

After you merge or close the PR:
- The webhook updates the row to `merged_clean`, `merged_edited`, or
  `closed_unmerged`
- The etchblok branch is auto-deleted

---

## Resetting between runs

Between runs of `run-all.sh`, do:

```bash
./tests/auto_update_scenarios/reset.sh        # source repo → baseline
# Then in the Etchblok UI: regenerate docs (Step B above)
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

---

## Mode B1 (deferred)

Once Mode A is stable, Mode B1 will:
- Skip docs regeneration between runs (state accumulates)
- Per-scenario `user_action.sh` simulates realistic close behaviors
  (merge clean / merge edited / close unmerged / leave open)
- Exercises real-world messy PR handling

Don't build Mode B1 until Mode A passes consistently. If basics are
broken, Mode B1 noise will obscure them.
