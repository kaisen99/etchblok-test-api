# 08 — PR refresh (two pushes, no merge between)

## What this scenario tests

The single-PR design: one stable PR per version on the branch
`etchblok/auto-update-{version}`. A second push *before the first PR is
merged* must **refresh the same PR** (force-push the branch, update the
description + comments), not open a second PR.

This is the only scenario that exercises the PR-refresh path —
`run-all.sh` merges every other scenario's PR immediately, so each of
them gets a fresh PR and the refresh code is never hit.

## Code changes

Both touch `SearchIndex` in `app/services/search_service.py` — a class
no other scenario modifies, so this scenario is resilient to whatever
01-07 did to the source.

- **Push 1**: `SearchIndex.search` body — cap results at `MAX_SEARCH_RESULTS`
- **Push 2**: `SearchIndex.index_bookmark` body — tokenize the title twice

Both are body-only changes (signatures unchanged) — the `body_hash`
diff path, same category as scenario 05.

## Expected pipeline behavior

**After push 1** (~10 min):
- One auto-update PR opens on branch `etchblok/auto-update-{version}`
- `autodoc_pr_outcomes` has one row, `status=open`, for that PR number
- The PR updates the `SearchIndex.search` API ref section

**After push 2** (~10 min, push 1's PR still open / unmerged):
- **No new PR.** The same PR number from push 1 is force-pushed and
  refreshed.
- Its description + per-section comments are regenerated.
- It now contains **both** sections — `SearchIndex.search` *and*
  `SearchIndex.index_bookmark`.
- `autodoc_pr_outcomes` still has **one** row for this branch (upserted),
  not two.

**After you merge the PR:**
- The GitHub webhook advances `autodoc_auto_update_state.last_commit_sha`
  to push 2's commit (read off the `pr_outcomes` row's `source_commit_sha`).
- The `etchblok/auto-update-{version}` branch is auto-deleted.

## How to verify

1. After push 1: note the PR number (call it `#N`).
2. After push 2: the open PR is **still `#N`** — refreshed, not replaced.
   GitHub shows a force-push event in the PR timeline.
3. `#N`'s file diff covers both `SearchIndex` sections.
4. The docs repo has exactly **one** open `etchblok/auto-update-*` branch.
5. `show-outcomes.sh`: one `open` row for this branch, not two.
6. After merge: `autodoc_auto_update_state` for this version points at
   push 2's commit SHA.

## Failure signature

If a **second PR** opens after push 2 instead of `#N` refreshing, the
single-PR path is broken — check `_find_open_pr` in `github_pr_creator.py`
(branch-name mismatch, or the open-PR query failing).

## Acceptable variations

- Agent wording / which exact lines change in each section may vary.
- The `MAX_SEARCH_RESULTS` cap may be described in the "Returns" prose
  or a separate note — either is fine.
