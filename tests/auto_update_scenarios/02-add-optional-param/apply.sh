#!/usr/bin/env bash
# Add an optional `tags` parameter to BookmarkService.create_bookmark.
# Same name, expanded signature — exercises body_hash + sig_hash both
# changing while caller compatibility is preserved by the default value.

set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

python3 <<'PY'
from pathlib import Path

svc = Path("app/services/bookmark_service.py")
content = svc.read_text()

old_sig = (
    "    def create_bookmark(self, data: Dict[str, Any]) -> Tuple[Optional[Bookmark], Optional[str]]:\n"
    "        \"\"\"Validate and persist a new bookmark.\n"
    "\n"
    "        Args:\n"
    "            data: Dict with ``url``, ``title``, and optional fields.\n"
    "\n"
    "        Returns:\n"
    "            Tuple of (bookmark, None) on success or (None, error_message) on failure.\n"
    "        \"\"\"\n"
    "        error = _validate_url(data.get(\"url\", \"\")) or _validate_title(data.get(\"title\", \"\"))\n"
    "        if error:\n"
    "            return None, error\n"
    "\n"
    "        bookmark = Bookmark.from_dict(data)\n"
    "        self._repo.save_bookmark(bookmark)\n"
    "        self._search.index_bookmark(bookmark)\n"
    "        self._cache.invalidate(bookmark.id)\n"
    "        return bookmark, None\n"
)
new_sig = (
    "    def create_bookmark(\n"
    "        self,\n"
    "        data: Dict[str, Any],\n"
    "        tags: Optional[List[str]] = None,\n"
    "    ) -> Tuple[Optional[Bookmark], Optional[str]]:\n"
    "        \"\"\"Validate and persist a new bookmark.\n"
    "\n"
    "        Args:\n"
    "            data: Dict with ``url``, ``title``, and optional fields.\n"
    "            tags: Optional list of tag IDs to attach on creation.\n"
    "\n"
    "        Returns:\n"
    "            Tuple of (bookmark, None) on success or (None, error_message) on failure.\n"
    "        \"\"\"\n"
    "        error = _validate_url(data.get(\"url\", \"\")) or _validate_title(data.get(\"title\", \"\"))\n"
    "        if error:\n"
    "            return None, error\n"
    "\n"
    "        bookmark = Bookmark.from_dict(data)\n"
    "        if tags:\n"
    "            for tag_id in tags:\n"
    "                bookmark.add_tag(tag_id)\n"
    "        self._repo.save_bookmark(bookmark)\n"
    "        self._search.index_bookmark(bookmark)\n"
    "        self._cache.invalidate(bookmark.id)\n"
    "        return bookmark, None\n"
)

assert old_sig in content, "create_bookmark not at expected shape"
content = content.replace(old_sig, new_sig)
svc.write_text(content)

print("02-add-optional-param: applied")
PY
