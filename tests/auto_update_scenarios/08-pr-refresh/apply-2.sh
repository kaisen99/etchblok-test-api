#!/usr/bin/env bash
# 08-pr-refresh, push 2 of 2.
# Behavioral body change to SearchIndex.index_bookmark — tokenize the
# title twice so title matches outrank description-only matches. Same
# signature, body only.
#
# Pushed WITHOUT merging push 1's PR. The auto-updater should refresh
# the SAME open PR (force-push the stable branch), not open a second
# one — that is the behavior this scenario exists to verify.

set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

python3 <<'PY'
from pathlib import Path

svc = Path("app/services/search_service.py")
content = svc.read_text()
anchor = '        tokens = self._tokenize(f"{bookmark.title} {bookmark.description}")'
assert anchor in content, "SearchIndex.index_bookmark tokenize line not at expected state"
content = content.replace(
    anchor,
    '        tokens = self._tokenize(f"{bookmark.title} {bookmark.title} {bookmark.description}")',
)
svc.write_text(content)

print("08-pr-refresh push 2: applied (SearchIndex.index_bookmark title weighting)")
PY
