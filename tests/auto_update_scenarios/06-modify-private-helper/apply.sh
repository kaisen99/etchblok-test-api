#!/usr/bin/env bash
# Modify the body of BookmarkService._init_services (private — leading
# underscore). Same signature, same callers. Exercises: private symbols
# should NOT trigger any sections being flagged — the auto-updater
# focuses on public API surface.

set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

python3 <<'PY'
from pathlib import Path

svc = Path("app/services/bookmark_service.py")
content = svc.read_text()

old = (
    "    def _init_services(self) -> None:\n"
    "        \"\"\"Bootstrap repository, cache, and search index.\"\"\"\n"
    "        self._repo = BookmarkRepository()\n"
    "        self._cache: LRUCache[Bookmark] = LRUCache(max_size=256)\n"
    "        self._search = SearchIndex(self._repo)\n"
)
new = (
    "    def _init_services(self) -> None:\n"
    "        \"\"\"Bootstrap repository, cache, and search index.\"\"\"\n"
    "        self._repo = BookmarkRepository()\n"
    "        # Raised from 256 to 512 — production workload kept evicting hot bookmarks.\n"
    "        self._cache: LRUCache[Bookmark] = LRUCache(max_size=512)\n"
    "        self._search = SearchIndex(self._repo)\n"
)
assert old in content, "_init_services not at expected baseline shape"
content = content.replace(old, new)
svc.write_text(content)

print("06-modify-private-helper: applied")
PY
