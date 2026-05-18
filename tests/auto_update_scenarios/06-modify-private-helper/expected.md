# 06 — Modify private helper

## Code change

`BookmarkService._init_services` (leading underscore = private) body
changed: LRU cache size 256 → 512. Signature unchanged. No public API
impact.

## Expected pipeline behavior

**Expected: no PR opens.**

The coordinator filters to public symbols when computing affected
sections. A private method body change shouldn't flag any sections —
nothing visible to users changed.

## Expected coordinator behavior

- `_init_services` detected as changed in raw diff (body_hash differs)
- But filtered out as non-public — no review requests generated
- Workflow runs to completion with zero updated sections
- `create_doc_update_pr` returns None ("no updated sections, skipping PR")

## Acceptable variations

- The auto-updater MAY still write to `autodoc_auto_update_state` to
  advance the baseline SHA even though no PR opens — that's correct
  behavior, otherwise the next scenario would diff from a stale baseline

## Failure modes to watch for

If a PR DOES open for this scenario, it indicates either:
- The public-only filter isn't being applied (bug)
- The grep layer false-positived on a guide that happens to mention
  `_init_services` or `LRUCache` (acceptable noise, but the agent
  should return NO_CHANGE on those)

If a PR opens with NO_CHANGE everywhere, that's the grep-layer
false-positive case — also expected behavior in the worst case.

## How to verify

1. Flyte logs: workflow runs, "no updated sections, skipping PR"
2. autodoc_pr_outcomes table — no new row from this scenario
3. autodoc_auto_update_state — baseline SHA advanced to this commit
