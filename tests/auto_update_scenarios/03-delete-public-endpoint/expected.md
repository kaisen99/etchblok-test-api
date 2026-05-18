# 03 — Delete public endpoint

## Code change

Removed `BookmarkService.restore_bookmark` and its route handler
`POST /api/bookmarks/<id>/restore`.

## Expected pipeline behavior

- One auto-update PR opens within ~10 min
- `autodoc_pr_outcomes` row created with `status=open`

## Expected coordinator flags

- `BookmarkService.restore_bookmark` → DELETED
- Route function `restore_bookmark` → DELETED
- Any guide section that mentions "restore" by name → flagged via GREP

## Expected agent decisions

- API ref section for `restore_bookmark` (service method) → `DELETE`
- API ref section for the route → `DELETE`
- Guide mentions of restore → `UPDATED` (remove the reference) or
  `NO_CHANGE` if the guide didn't actually depend on the endpoint

## Acceptable variations

- Agent may keep one section as a "removed in this version" stub
  rather than deleting outright
- If the docs had an endpoints index page, agent may UPDATE that to
  remove the entry rather than DELETE the index itself

## How to verify

1. PR diff includes file deletions for the API ref sections
2. PR body lists the DELETE action for at least one section
3. No orphan references to "restore" remain in the docs after merge
