# 02 — Add optional parameter

## Code change

`BookmarkService.create_bookmark` gains a `tags: Optional[List[str]] = None`
parameter; body adds a tag-attachment loop when `tags` is provided.

## Expected pipeline behavior

- One auto-update PR opens within ~10 min
- `autodoc_pr_outcomes` row created with `status=open`

## Expected coordinator flags

- `BookmarkService.create_bookmark` → CHANGED (sig_hash + body_hash differ)
- Anything that calls `create_bookmark` (POST `/api/bookmarks` route) →
  potentially flagged via call graph (no signature break, but body changed)

## Expected agent decisions

- API ref section for `create_bookmark` → `UPDATED`
  - New param documented in the "Parameters" table
  - Behavior description mentions tags are applied if supplied
- Route handler section → `NO_CHANGE` is acceptable (caller signature
  still works) OR `UPDATED` if the docs explain creation arguments

## Acceptable variations

- The agent may add a usage example showing the new param
- It may not catch this is "backwards-compatible" and over-warn — that's fine

## How to verify

1. PR body lists "create_bookmark" in the affected sections
2. PR diff shows surgical edit to the API ref — new param, no full rewrite
3. The route handler section is either NO_CHANGE or a minimal touch
