# 05 — Modify body, same signature

## Code change

`BookmarkService.search` body now lowercases + strips the query and
short-circuits empty input. Signature unchanged.

## Expected pipeline behavior

- One auto-update PR opens within ~10 min
- `autodoc_pr_outcomes` row created with `status=open`

## Expected coordinator flags

- `BookmarkService.search` → CHANGED (body_hash differs, sig_hash same)
- `search_bookmarks` route → may be flagged via call graph (it invokes
  `_service.search`), but no actual behavior change at the route level

## Expected agent decisions

- API ref section for `BookmarkService.search` → `UPDATED`
  - Description now mentions the normalization behavior
  - Should NOT rewrite from scratch — surgical edit per the minimum-change rule
- Route handler section → `NO_CHANGE` (route behavior unchanged from
  caller perspective)
- Any guide that explains the search flow → likely `UPDATED` if it
  documented the query format, otherwise `NO_CHANGE`

## Acceptable variations

- Agent may add a usage note about case-insensitivity
- May not catch every guide that touches this — surface area depends
  on what guides exist

## How to verify

1. PR diff to the search API ref: small additive change, not a rewrite
2. Route handler section either NO_CHANGE or a docstring touch only
3. Compare diff size to scenarios 01-03 — should be smaller (single section
   updated, single behavior described)
