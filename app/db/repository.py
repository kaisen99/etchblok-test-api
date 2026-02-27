"""In-memory repository implementing the data access pattern.

Provides a clean abstraction over storage so the service layer doesn't
need to know whether data lives in memory, SQLite, or a remote database.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from app.models.bookmark import Bookmark, BookmarkStatus
from app.models.tag import Tag
from app.models.collection import Collection


class BookmarkRepository:
    """In-memory storage for bookmarks, tags, and collections.

    All mutation methods persist immediately (since this is in-memory).
    For a real database you'd add transaction support here.
    """

    def __init__(self) -> None:
        self._bookmarks: Dict[str, Bookmark] = {}
        self._tags: Dict[str, Tag] = {}
        self._collections: Dict[str, Collection] = {}

    # ── Bookmark CRUD ───────────────────────────────────────────────

    def save_bookmark(self, bookmark: Bookmark) -> None:
        """Insert or update a bookmark."""
        self._bookmarks[bookmark.id] = bookmark

    def get_bookmark(self, bookmark_id: str) -> Optional[Bookmark]:
        """Retrieve a bookmark by ID, or None."""
        return self._bookmarks.get(bookmark_id)

    def delete_bookmark(self, bookmark_id: str) -> bool:
        """Hard-delete a bookmark. Returns True if it existed."""
        return self._bookmarks.pop(bookmark_id, None) is not None

    def list_bookmarks(
        self,
        page: int = 1,
        per_page: int = 25,
        status: Optional[str] = None,
    ) -> Tuple[List[Bookmark], int]:
        """Return a paginated slice of bookmarks.

        Args:
            page: 1-based page index.
            per_page: Number of items per page.
            status: Optional status filter string (active, archived, trashed).

        Returns:
            Tuple of (page_items, total_matching_count).
        """
        items = list(self._bookmarks.values())
        if status:
            try:
                target = BookmarkStatus(status)
                items = [b for b in items if b.status == target]
            except ValueError:
                pass
        items.sort(key=lambda b: b.created_at, reverse=True)
        total = len(items)
        start = (page - 1) * per_page
        return items[start : start + per_page], total

    def get_bookmarks_with_tag(self, tag_id: str) -> List[Bookmark]:
        """Return all bookmarks that have a specific tag attached."""
        return [b for b in self._bookmarks.values() if tag_id in b.tags]

    # ── Tag CRUD ────────────────────────────────────────────────────

    def save_tag(self, tag: Tag) -> None:
        """Insert or update a tag."""
        self._tags[tag.id] = tag

    def get_tag(self, tag_id: str) -> Optional[Tag]:
        """Retrieve a tag by ID, or None."""
        return self._tags.get(tag_id)

    def delete_tag(self, tag_id: str) -> bool:
        """Hard-delete a tag."""
        return self._tags.pop(tag_id, None) is not None

    def list_tags(self) -> List[Tag]:
        """Return all tags."""
        return list(self._tags.values())

    # ── Collection CRUD ─────────────────────────────────────────────

    def save_collection(self, collection: Collection) -> None:
        """Insert or update a collection."""
        self._collections[collection.id] = collection

    def get_collection(self, collection_id: str) -> Optional[Collection]:
        """Retrieve a collection by ID, or None."""
        return self._collections.get(collection_id)

    def delete_collection(self, collection_id: str) -> bool:
        """Hard-delete a collection."""
        return self._collections.pop(collection_id, None) is not None

    def list_collections(self) -> List[Collection]:
        """Return all collections."""
        return list(self._collections.values())

    # ── Internal helpers ────────────────────────────────────────────

    def _count_all(self) -> Dict[str, int]:
        """Return entity counts. Used for diagnostics."""
        return {
            "bookmarks": len(self._bookmarks),
            "tags": len(self._tags),
            "collections": len(self._collections),
        }

    def _clear_all(self) -> None:
        """Wipe all data. Test use only."""
        self._bookmarks.clear()
        self._tags.clear()
        self._collections.clear()
