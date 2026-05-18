# 07 — Debounce burst

## Code change

Three commits pushed in ~90 seconds, each adding a comment to a
different model class (`Bookmark`, `Collection`, `Tag`). Each commit
is itself trivial; the test is whether the system **collapses** them
into a single workflow run.

## Expected pipeline behavior

- Three webhook invocations, three pending-update rows OVERWRITTEN
  (one row per repo+user — successive pushes overwrite, not append)
- The 5-minute debounce keeps the poller skipping while pushes keep
  arriving
- After ~5 min of quiet (no more pushes), the poller picks up the
  pending row and fires the workflow ONCE with the final SHA
- **One** auto-update PR opens — not three

## Expected coordinator behavior

- Diff is computed from baseline → final-SHA-after-3-commits (not from
  any intermediate state)
- All three model class changes appear in the same diff
- Any sections that GREP-match on `Bookmark`, `Collection`, or `Tag`
  may be flagged together

## Expected agent decisions

- These are pure comment additions — no public symbol changes
- Most likely outcome: workflow runs, finds no public-symbol diffs,
  exits without opening a PR (similar to scenario 06)
- If GREP flags any guide sections that mention these class names,
  the agent should return `NO_CHANGE` (comments don't affect behavior)

## Acceptable variations

- A small PR with NO_CHANGE on flagged sections is fine — that means
  GREP fired but the agent correctly declined to edit
- If `BookmarkService` calls these models and the call-graph layer
  decides to flag service-level sections, that's noisy but acceptable

## How to verify

1. Vercel logs: 3 webhook receipts, each overwriting the same pending row
2. Flyte logs: ONE invocation of `doc_auto_update_workflow` for this
   commit range, not three
3. autodoc_pr_outcomes: at most one new row from this scenario
4. If a PR opens, its diff covers all 3 commits (not just the last one)
   — this confirms the diff baseline was correctly held back, not
   advanced commit-by-commit
