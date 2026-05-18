#!/usr/bin/env bash
# Rename BookmarkService.search → BookmarkService.full_text_search.
# Updates both the definition and its caller in the routes module.
# Exercises: symbol-diff seeing rename as delete + new.

set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

python3 <<'PY'
from pathlib import Path

svc = Path("app/services/bookmark_service.py")
content = svc.read_text()
assert "def search(self, query: str, limit: int = 20)" in content, "search() not at expected signature"
content = content.replace(
    "def search(self, query: str, limit: int = 20) -> List[Bookmark]:\n"
    "        \"\"\"Full-text search across bookmarks.\"\"\"\n"
    "        return self._search.search(query, limit=limit)",
    "def full_text_search(self, query: str, limit: int = 20) -> List[Bookmark]:\n"
    "        \"\"\"Full-text search across bookmark titles and descriptions.\"\"\"\n"
    "        return self._search.search(query, limit=limit)",
)
svc.write_text(content)

routes = Path("app/routes/bookmarks.py")
content = routes.read_text()
assert "_service.search(query, limit=limit)" in content, "caller not at expected line"
content = content.replace(
    "_service.search(query, limit=limit)",
    "_service.full_text_search(query, limit=limit)",
)
routes.write_text(content)

print("01-rename-public-method: applied")
PY
