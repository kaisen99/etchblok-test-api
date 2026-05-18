#!/usr/bin/env bash
# Modify body of BookmarkService.search without changing the signature.
# Adds query normalization (lowercase + strip) before delegating.
# Exercises: body_hash diff drives flagging, sig_hash unchanged.

set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

python3 <<'PY'
from pathlib import Path

svc = Path("app/services/bookmark_service.py")
content = svc.read_text()

old = (
    "    def search(self, query: str, limit: int = 20) -> List[Bookmark]:\n"
    "        \"\"\"Full-text search across bookmarks.\"\"\"\n"
    "        return self._search.search(query, limit=limit)\n"
)
new = (
    "    def search(self, query: str, limit: int = 20) -> List[Bookmark]:\n"
    "        \"\"\"Full-text search across bookmarks.\n"
    "\n"
    "        The query is lowercased and stripped before delegation so callers\n"
    "        do not need to normalize themselves.\n"
    "        \"\"\"\n"
    "        normalized = query.lower().strip()\n"
    "        if not normalized:\n"
    "            return []\n"
    "        return self._search.search(normalized, limit=limit)\n"
)
assert old in content, "search() not at expected baseline shape"
content = content.replace(old, new)
svc.write_text(content)

print("05-modify-body-same-sig: applied")
PY
