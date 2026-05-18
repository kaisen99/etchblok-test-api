#!/usr/bin/env bash
# Add a brand-new public method (BookmarkService.bulk_delete_bookmarks)
# plus its route. Exercises: "new public symbol detected" deferral —
# the auto-updater should LOG it in the PR body but NOT auto-generate
# a new API ref section for it (that's the deferred path).

set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

python3 <<'PY'
from pathlib import Path

svc = Path("app/services/bookmark_service.py")
content = svc.read_text()

# Insert the new method right after delete_bookmark.
insert_after = (
    "    def delete_bookmark(self, bookmark_id: str) -> bool:\n"
    "        \"\"\"Soft-delete by trashing the bookmark.\"\"\"\n"
    "        bookmark = self._repo.get_bookmark(bookmark_id)\n"
    "        if not bookmark:\n"
    "            return False\n"
    "        bookmark.trash()\n"
    "        self._repo.save_bookmark(bookmark)\n"
    "        self._cache.invalidate(bookmark_id)\n"
    "        return True\n"
)
new_method = (
    "\n"
    "    def bulk_delete_bookmarks(self, bookmark_ids: List[str]) -> int:\n"
    "        \"\"\"Soft-delete multiple bookmarks in one pass.\n"
    "\n"
    "        Args:\n"
    "            bookmark_ids: IDs of bookmarks to trash.\n"
    "\n"
    "        Returns:\n"
    "            The number of bookmarks that were successfully trashed.\n"
    "            IDs not found are silently skipped.\n"
    "        \"\"\"\n"
    "        deleted = 0\n"
    "        for bid in bookmark_ids:\n"
    "            if self.delete_bookmark(bid):\n"
    "                deleted += 1\n"
    "        return deleted\n"
)
assert insert_after in content
content = content.replace(insert_after, insert_after + new_method)
svc.write_text(content)

routes = Path("app/routes/bookmarks.py")
content = routes.read_text()
# Append a new route at the end of the file.
new_route = (
    "\n\n@bookmarks_bp.route(\"/bulk-delete\", methods=[\"POST\"])\n"
    "def bulk_delete_bookmarks():\n"
    "    \"\"\"Trash multiple bookmarks in one request.\n"
    "\n"
    "    Expects a JSON body with ``ids`` (list of bookmark IDs).\n"
    "    Returns the count of bookmarks successfully trashed.\n"
    "    \"\"\"\n"
    "    data = request.get_json(force=True)\n"
    "    ids = data.get(\"ids\", [])\n"
    "    if not isinstance(ids, list):\n"
    "        return jsonify({\"error\": \"ids must be a list\"}), 400\n"
    "    count = _service.bulk_delete_bookmarks(ids)\n"
    "    return jsonify({\"deleted\": count})\n"
)
content = content.rstrip() + new_route + "\n"
routes.write_text(content)

print("04-add-new-public-method: applied")
PY
