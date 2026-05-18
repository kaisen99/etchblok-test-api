# 04 — Add new public method

## Code change

Added `BookmarkService.bulk_delete_bookmarks(bookmark_ids: List[str]) -> int`
plus the route `POST /api/bookmarks/bulk-delete`.

## Expected pipeline behavior

Two valid outcomes:

**Outcome A (most likely):** No PR opens. The auto-updater's coordinator
identifies new public symbols via the import graph but the new-symbol
auto-documentation path is deferred (`docai/doc_autoupdate_workflow.py:863`
logs but doesn't act). The workflow logs "1 new public symbol detected"
and exits with no review requests. Workflow logs in Flyte show the
new-symbol detection.

**Outcome B:** If the new method also affected the diff for any existing
section via call-graph expansion (e.g., `delete_bookmark` is shown as
"affected by caller", since `bulk_delete_bookmarks` calls it), a PR
opens that flags `delete_bookmark`'s API ref. Acceptable but noisy.

## Expected coordinator behavior

- `bulk_delete_bookmarks` (service method) → NEW (logged)
- `bulk_delete_bookmarks` (route function) → NEW (logged)
- `BookmarkService.delete_bookmark` → AFFECTED via call graph
  (caller-of-modified, since the new method calls it indirectly through
  the same source file)

## Known gap

This is the test for the "new code auto-documentation" deferred work
in [auto_updater.md]. If we ever build that path, this scenario should
start producing PRs that create new API ref sections for the new
method + route. Until then, Outcome A is correct behavior.

## How to verify

1. Check Flyte logs for "new public symbols need documentation"
2. autodoc_pr_outcomes table — likely no new row for this scenario
3. If a PR did open, verify it does NOT contain net-new sections for
   the bulk-delete endpoint (that would mean the deferred path got
   accidentally enabled)
