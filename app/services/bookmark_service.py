"""Core service orchestrating bookmarks, tags, and collections.

``BookmarkService`` is the primary public interface for all business logic.
Route handlers delegate to this class rather than touching the repository
directly.
"""
from __future__ import annotations

from typing import Dict, Any, List, Optional, Tuple

from app.models.bookmark import Bookmark
from app.models.tag import Tag, TagColor
from app.models.collection import Collection
from app.models._validators import _validate_url, _validate_title, _validate_tag_name
from app.db.repository import BookmarkRepository
from app.services._cache import LRUCache
from app.services.search_service import SearchIndex


class BookmarkService:
    """Facade over the repository and search index.

    Handles validation, cache invalidation, and cross-entity operations
    (e.g. removing a tag also strips it from all bookmarks).
    """

    _instance: Optional["BookmarkService"] = None

    def __new__(cls) -> "BookmarkService":
        """Singleton — share state across blueprint modules."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_services()
        return cls._instance

    # ── Bookmark operations ─────────────────────────────────────────

    def create_bookmark(self, data: Dict[str, Any]) -> Tuple[Optional[Bookmark], Optional[str]]:
        """Validate and persist a new bookmark.

        Args:
            data: Dict with ``url``, ``title``, and optional fields.

        Returns:
            Tuple of (bookmark, None) on success or (None, error_message) on failure.
        """
        error = _validate_url(data.get("url", "")) or _validate_title(data.get("title", ""))
        if error:
            return None, error

        bookmark = Bookmark.from_dict(data)
        self._repo.save_bookmark(bookmark)
        self._search.index_bookmark(bookmark)
        self._cache.invalidate(bookmark.id)
        return bookmark, None

    def get_bookmark(self, bookmark_id: str) -> Optional[Bookmark]:
        """Retrieve a bookmark by ID, using cache when available."""
        cached = self._cache.get(bookmark_id)
        if cached is not None:
            return cached
        bookmark = self._repo.get_bookmark(bookmark_id)
        if bookmark:
            self._cache.put(bookmark.id, bookmark)
        return bookmark

    def list_bookmarks(
        self, page: int = 1, per_page: int = 25, status: Optional[str] = None
    ) -> Tuple[List[Bookmark], int]:
        """Return a paginated list of bookmarks.

        Args:
            page: 1-based page number.
            per_page: Number of items per page.
            status: Optional status filter.

        Returns:
            Tuple of (bookmarks_list, total_count).
        """
        return self._repo.list_bookmarks(page=page, per_page=per_page, status=status)

    def update_bookmark(self, bookmark_id: str, data: Dict[str, Any]) -> Tuple[Optional[Bookmark], Optional[str]]:
        """Partially update a bookmark."""
        bookmark = self._repo.get_bookmark(bookmark_id)
        if not bookmark:
            return None, None

        if "title" in data:
            err = _validate_title(data["title"])
            if err:
                return None, err
            bookmark.title = data["title"]
        if "description" in data:
            bookmark.description = data["description"]
        if "url" in data:
            err = _validate_url(data["url"])
            if err:
                return None, err
            bookmark.url = data["url"]

        bookmark._touch()
        self._repo.save_bookmark(bookmark)
        self._search.index_bookmark(bookmark)
        self._cache.invalidate(bookmark.id)
        return bookmark, None

    def delete_bookmark(self, bookmark_id: str) -> bool:
        """Soft-delete by trashing the bookmark."""
        bookmark = self._repo.get_bookmark(bookmark_id)
        if not bookmark:
            return False
        bookmark.trash()
        self._repo.save_bookmark(bookmark)
        self._cache.invalidate(bookmark_id)
        return True

    def archive_bookmark(self, bookmark_id: str) -> Optional[Bookmark]:
        """Archive a bookmark."""
        bookmark = self._repo.get_bookmark(bookmark_id)
        if not bookmark:
            return None
        bookmark.archive()
        self._repo.save_bookmark(bookmark)
        self._cache.invalidate(bookmark_id)
        return bookmark

    def restore_bookmark(self, bookmark_id: str) -> Optional[Bookmark]:
        """Restore a bookmark to active status."""
        bookmark = self._repo.get_bookmark(bookmark_id)
        if not bookmark:
            return None
        bookmark.restore()
        self._repo.save_bookmark(bookmark)
        self._cache.invalidate(bookmark_id)
        return bookmark

    def full_text_search(self, query: str, limit: int = 20) -> List[Bookmark]:
        """Full-text search across bookmark titles and descriptions."""
        return self._search.search(query, limit=limit)

    # ── Tag operations ──────────────────────────────────────────────

    def list_tags(self) -> List[Tag]:
        """Return all tags."""
        return self._repo.list_tags()

    def create_tag(self, data: Dict[str, Any]) -> Tuple[Optional[Tag], Optional[str]]:
        """Validate and persist a new tag."""
        error = _validate_tag_name(data.get("name", ""))
        if error:
            return None, error
        tag = Tag.from_dict(data)
        self._repo.save_tag(tag)
        return tag, None

    def delete_tag(self, tag_id: str) -> bool:
        """Delete a tag and strip it from all bookmarks."""
        tag = self._repo.get_tag(tag_id)
        if not tag:
            return False
        for bookmark in self._repo.get_bookmarks_with_tag(tag_id):
            bookmark.remove_tag(tag_id)
            self._repo.save_bookmark(bookmark)
            self._cache.invalidate(bookmark.id)
        self._repo.delete_tag(tag_id)
        return True

    def update_tag(self, tag_id: str, data: Dict[str, Any]) -> Tuple[Optional[Tag], Optional[str]]:
        """Update a tag's name or colour."""
        tag = self._repo.get_tag(tag_id)
        if not tag:
            return None, None
        if "name" in data:
            err = _validate_tag_name(data["name"])
            if err:
                return None, err
            tag.rename(data["name"])
        if "color" in data:
            tag.color = TagColor(data["color"])
        self._repo.save_tag(tag)
        return tag, None

    # ── Collection operations ───────────────────────────────────────

    def list_collections(self) -> List[Collection]:
        """Return all collections."""
        return self._repo.list_collections()

    def get_collection(self, collection_id: str) -> Optional[Collection]:
        """Retrieve a collection by ID."""
        return self._repo.get_collection(collection_id)

    def create_collection(self, data: Dict[str, Any]) -> Tuple[Optional[Collection], Optional[str]]:
        """Create a new collection."""
        name = data.get("name", "").strip()
        if not name:
            return None, "Collection name is required"
        collection = Collection.from_dict(data)
        self._repo.save_collection(collection)
        return collection, None

    def add_to_collection(self, collection_id: str, bookmark_id: str) -> bool:
        """Add a bookmark to a collection."""
        collection = self._repo.get_collection(collection_id)
        if not collection:
            return False
        if not collection.add_bookmark(bookmark_id):
            return False
        self._repo.save_collection(collection)
        return True

    def remove_from_collection(self, collection_id: str, bookmark_id: str) -> bool:
        """Remove a bookmark from a collection."""
        collection = self._repo.get_collection(collection_id)
        if not collection:
            return False
        if not collection.remove_bookmark(bookmark_id):
            return False
        self._repo.save_collection(collection)
        return True

    # ── Internal ────────────────────────────────────────────────────

    def _init_services(self) -> None:
        """Bootstrap repository, cache, and search index."""
        self._repo = BookmarkRepository()
        self._cache: LRUCache[Bookmark] = LRUCache(max_size=256)
        self._search = SearchIndex(self._repo)

    def _reset(self) -> None:
        """Tear down and reinitialise — used in tests only."""
        self._init_services()
