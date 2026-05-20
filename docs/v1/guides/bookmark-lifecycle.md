---
title: Bookmark Lifecycle
description: Guides on creating, updating, archiving, and managing the status of bookmarks through the service layer.
code_symbols: [SYM#dd5fd545693e00d6c0b38892bbd18ed4afa136a1, SYM#d731bc2f45cac29b2961ab00083bab5345db0a5e]
section_id: 8cbf9fbf-75ae-4318-aaae-141c8f19ffab_bookmark_lifecycle
doc_type: guide
section_type: guide
---
The bookmark lifecycle in this application is managed through a layered architecture where the `BookmarkService` acts as a facade, orchestrating the `Bookmark` domain entity, the `BookmarkRepository` for persistence, and auxiliary services like `SearchIndex` and `LRUCache`.

## Core Lifecycle Entities

The lifecycle is driven by three primary components:

1.  **`Bookmark` (app/models/bookmark.py)**: The domain entity that encapsulates state and business rules. It manages its own status transitions and metadata updates.
2.  **`BookmarkStatus` (app/models/bookmark.py)**: An enumeration defining the three valid states for a bookmark: `ACTIVE`, `ARCHIVED`, and `TRASHED`.
3.  **`BookmarkService` (app/services/bookmark_service.py)**: A singleton service that provides the public API for bookmark operations, ensuring that validation, persistence, and indexing happen in the correct order.

## Creation and Validation

Bookmarks are created via `BookmarkService.create_bookmark(data)`. This method performs several critical steps:

1.  **Validation**: It uses internal helpers from `app.models._validators` to check the URL format and title length.
2.  **Instantiation**: If valid, it creates a `Bookmark` instance using `Bookmark.from_dict(data)`.
3.  **Persistence & Indexing**: The service saves the entity to the `BookmarkRepository`, adds it to the `SearchIndex` for full-text search, and invalidates any existing cache entries for that ID.

```python
# Example of creation logic in BookmarkService
def create_bookmark(self, data: Dict[str, Any]) -> Tuple[Optional[Bookmark], Optional[str]]:
    error = _validate_url(data.get("url", "")) or _validate_title(data.get("title", ""))
    if error:
        return None, error

    bookmark = Bookmark.from_dict(data)
    self._repo.save_bookmark(bookmark)
    self._search.index_bookmark(bookmark)
    self._cache.invalidate(bookmark.id)
    return bookmark, None
```

## State Management

The `Bookmark` entity manages its own state transitions through dedicated methods. These methods update the `status` attribute and call `_touch()` to refresh the `updated_at` timestamp.

| Transition | Method | Resulting Status |
| :--- | :--- | :--- |
| Archive | `bookmark.archive()` | `BookmarkStatus.ARCHIVED` |
| Trash (Soft-delete) | `bookmark.trash()` | `BookmarkStatus.TRASHED` |
| Restore | `bookmark.restore()` | `BookmarkStatus.ACTIVE` |

The `BookmarkService` wraps these transitions to ensure the repository is updated and the cache is invalidated:

```python
# app/services/bookmark_service.py
def archive_bookmark(self, bookmark_id: str) -> Optional[Bookmark]:
    bookmark = self._repo.get_bookmark(bookmark_id)
    if not bookmark:
        return None
    bookmark.archive()
    self._repo.save_bookmark(bookmark)
    self._cache.invalidate(bookmark_id)
    return bookmark
```

## Retrieval and Caching

The `BookmarkService` implements a read-through cache strategy using an `LRUCache`. When `get_bookmark(id)` is called, the service first checks the cache before querying the `BookmarkRepository`.

```python
def get_bookmark(self, bookmark_id: str) -> Optional[Bookmark]:
    cached = self._cache.get(bookmark_id)
    if cached is not None:
        return cached
    bookmark = self._repo.get_bookmark(bookmark_id)
    if bookmark:
        self._cache.put(bookmark.id, bookmark)
    return bookmark
```

For listing multiple bookmarks, `list_bookmarks` supports pagination and status filtering, delegating the query to the repository:

```python
def list_bookmarks(
    self, page: int = 1, per_page: int = 25, status: Optional[str] = None
) -> Tuple[List[Bookmark], int]:
    return self._repo.list_bookmarks(page=page, per_page=per_page, status=status)
```

## Updates and Metadata

Updates are handled partially via `update_bookmark`. The service retrieves the existing entity, applies changes to specific fields (URL, title, or description), and triggers the `_touch()` method to update the modification timestamp.

The `Bookmark` entity also supports tag management through `add_tag` and `remove_tag`. A notable lifecycle event occurs when a **Tag** is deleted: the `BookmarkService.delete_tag` method performs a cascading operation, stripping the tag from all associated bookmarks before removing the tag itself.

## Soft-Delete vs. Hard-Delete

This codebase distinguishes between "trashing" and "deleting":

*   **Soft-Delete (Trash)**: Performed by `BookmarkService.delete_bookmark`. It changes the status to `TRASHED`. The bookmark remains in the repository and can be restored later.
*   **Hard-Delete**: Performed directly by `BookmarkRepository.delete_bookmark(id)`. This removes the record entirely from the in-memory storage. The service layer generally avoids this to prevent accidental data loss, preferring the soft-delete lifecycle.

```python
# Soft-delete implementation in BookmarkService
def delete_bookmark(self, bookmark_id: str) -> bool:
    bookmark = self._repo.get_bookmark(bookmark_id)
    if not bookmark:
        return False
    bookmark.trash() # Changes status to TRASHED
    self._repo.save_bookmark(bookmark)
    self._cache.invalidate(bookmark_id)
    return True
```