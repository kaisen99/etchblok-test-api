# 01 — Rename public method

## Code change

`BookmarkService.search` → `BookmarkService.full_text_search`, with the
caller in `app/routes/bookmarks.py:search_bookmarks` updated to match.

## Expected pipeline behavior

- Webhook receives push, writes pending row, poller fires after debounce
- One auto-update PR opens on the docs repo within ~10 min
- `autodoc_pr_outcomes` row created with `status=open`

## Expected coordinator flags

The symbol diff should report:
- `BookmarkService.search` → DELETED
- `BookmarkService.full_text_search` → NEW
- `search_bookmarks` route → AFFECTED (its body calls the renamed method)

## Expected agent decisions

- API ref for `BookmarkService.search` → `DELETE` (symbol no longer exists)
- Section for the route handler → `UPDATED` (method reference changed)
- New `full_text_search` symbol → **NOT auto-documented** (deferred path);
  should appear in the PR body as "1 new public symbol detected"

## Acceptable variations

- Agent may keep the old API ref section but rewrite it to describe
  the new method (effectively a rename in the docs)
- New-symbol surfacing message wording may vary

## How to verify

1. PR title: "📝 Etchblok: documentation auto-update (…)"
2. PR body's "Sections updated" table lists the API ref + route section
3. The deleted section file appears in the PR diff as a removed file
   (or modified, if the agent rewrote rather than removed)
4. PR body mentions the new symbol or includes it in the code-changes list
