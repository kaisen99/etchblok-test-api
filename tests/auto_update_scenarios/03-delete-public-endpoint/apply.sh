#!/usr/bin/env bash
# Delete BookmarkService.restore_bookmark plus its public route handler.
# Exercises: DELETE action path on a fully-removed public symbol.

set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

python3 <<'PY'
from pathlib import Path

svc = Path("app/services/bookmark_service.py")
content = svc.read_text()
old_method = (
    "    def restore_bookmark(self, bookmark_id: str) -> Optional[Bookmark]:\n"
    "        \"\"\"Restore a bookmark to active status.\"\"\"\n"
    "        bookmark = self._repo.get_bookmark(bookmark_id)\n"
    "        if not bookmark:\n"
    "            return None\n"
    "        bookmark.restore()\n"
    "        self._repo.save_bookmark(bookmark)\n"
    "        self._cache.invalidate(bookmark_id)\n"
    "        return bookmark\n"
    "\n"
)
assert old_method in content, "restore_bookmark not at expected shape"
content = content.replace(old_method, "")
svc.write_text(content)

routes = Path("app/routes/bookmarks.py")
content = routes.read_text()
old_route = (
    "\n\n@bookmarks_bp.route(\"/<bookmark_id>/restore\", methods=[\"POST\"])\n"
    "def restore_bookmark(bookmark_id: str):\n"
    "    \"\"\"Restore a bookmark from archive or trash.\"\"\"\n"
    "    bookmark = _service.restore_bookmark(bookmark_id)\n"
    "    if not bookmark:\n"
    "        return jsonify({\"error\": \"Bookmark not found\"}), 404\n"
    "    return jsonify(bookmark.to_dict())\n"
)
assert old_route in content, "restore route not at expected shape"
content = content.replace(old_route, "")
routes.write_text(content)

print("03-delete-public-endpoint: applied")
PY
