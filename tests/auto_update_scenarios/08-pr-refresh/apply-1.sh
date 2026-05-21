#!/usr/bin/env bash
# 08-pr-refresh, push 1 of 2.
# Behavioral body change to SearchIndex.search — cap results at the
# module-level MAX_SEARCH_RESULTS ceiling. Same signature, body only.
#
# SearchIndex (app/services/search_service.py) is deliberately a class
# that scenarios 01-07 never touch, so this scenario is resilient no
# matter how much earlier scenarios have mutated the source.

set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

python3 <<'PY'
from pathlib import Path

svc = Path("app/services/search_service.py")
content = svc.read_text()
anchor = "        return self._rank_results(results, tokens)[:limit]"
assert anchor in content, "SearchIndex.search return line not at expected state"
content = content.replace(
    anchor,
    "        return self._rank_results(results, tokens)[:min(limit, MAX_SEARCH_RESULTS)]",
)
svc.write_text(content)

print("08-pr-refresh push 1: applied (SearchIndex.search result cap)")
PY
