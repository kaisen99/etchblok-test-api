---
title: Soft Deletion and the Trash Mechanism
description: An explanation of the design choice behind soft-deletion (trashing) versus permanent removal, and how the service handles these operations.
code_symbols: [SYM#dd5fd545693e00d6c0b38892bbd18ed4afa136a1, SYM#fdcfaed9972e477ae4585fd1b279ac107fa534cd, SYM#6d5b77b3f04288620db996a9bc18b13d3bd1ad3b]
section_id: 80160c51-b0b1-4430-afb8-44acaf5bdc61_soft_deletion_and_the_trash_mechanism
doc_type: explanation
section_type: guide
---
The **kaisen99-etchblok-test-api-851c354** codebase implements a robust state management system for bookmarks, prioritizing data retention through a "soft-delete" or "trash" mechanism. Instead of immediately purging data from the system, the application transitions entities through different lifecycle states, allowing for recovery and archival.

## The Bookmark Lifecycle

The lifecycle of a bookmark is governed by the `BookmarkStatus` enumeration found in `app/models/bookmark.py`. A bookmark can exist in one of three states:

*   `ACTIVE`: The default state for new bookmarks. They are visible in standard listings and search results.
*   `ARCHIVED`: For bookmarks the user wants to keep but hide from the primary view.
*   `TRASHED`: The "soft-deleted" state. Bookmarks in this state are effectively in a recycle bin, awaiting either restoration or eventual permanent removal.

### State Transitions in the Model

The `Bookmark` class provides explicit methods to handle these transitions. Each method updates the `status` attribute and invokes the private `_touch()` helper to ensure the `updated_at` timestamp reflects the change:

```python
# app/models/bookmark.py

def archive(self) -> None:
    """Move the bookmark to the archive."""
    self.status = BookmarkStatus.ARCHIVED
    self._touch()

def trash(self) -> None:
    """Soft-delete the bookmark by moving it to the trash."""
    self.status = BookmarkStatus.TRASHED
    self._touch()

def restore(self) -> None:
    """Restore a trashed or archived bookmark to active status."""
    self.status = BookmarkStatus.ACTIVE
    self._touch()
```

## Soft-Deletion via the Service Layer

The `BookmarkService` acts as the orchestrator for these state changes. When a delete request is received (typically via the `DELETE /api/bookmarks/<id>` endpoint), the service does not invoke a removal from the database. Instead, it performs a soft-delete by updating the bookmark's status. Similarly, archiving a bookmark is also handled at this layer.

```python
# app/services/bookmark_service.py

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
```

This implementation ensures that:
1.  The entity remains in the `BookmarkRepository`.
2.  The `updated_at` timestamp is refreshed.
3.  The local `LRUCache` is invalidated to prevent stale "ACTIVE" data from being served.

## Hard vs. Soft Deletion Tradeoffs

There is a notable distinction between the `BookmarkService` and the `BookmarkRepository` regarding deletion. The `BookmarkRepository` (in `app/db/repository.py`) provides a `delete_bookmark` method that performs a **hard-delete**, removing the object entirely from the internal dictionary:

```python
# app/db/repository.py

def delete_bookmark(self, bookmark_id: str) -> bool:
    """Hard-delete a bookmark. Returns True if it existed."""
    return self._bookmarks.pop(bookmark_id, None) is not None
```

The design choice in this project is to **avoid using this repository method** in the standard application flow. By using the service-level soft-delete, the system gains several advantages:
*   **Accidental Loss Prevention**: Users can restore bookmarks they deleted by mistake.
*   **Auditability**: The `updated_at` and `status` fields provide a history of the entity's lifecycle.
*   **Simplified Relationships**: Hard-deleting a bookmark might leave orphaned references in collections or search indexes; soft-deletion allows these systems to filter by status instead of handling missing references.

## Filtering and Restoration

The "Trash" mechanism is supported by the repository's ability to filter by status. The `list_bookmarks` method in `BookmarkRepository` accepts a `status` string, which it attempts to map to the `BookmarkStatus` enum:

```python
# app/db/repository.py

def list_bookmarks(self, page: int = 1, per_page: int = 25, status: Optional[str] = None):
    items = list(self._bookmarks.values())
    if status:
        try:
            target = BookmarkStatus(status)
            items = [b for b in items if b.status == target]
        except ValueError:
            pass # Invalid status strings are ignored
    # ... pagination logic ...
```

Restoration is equally straightforward. The `BookmarkService.restore_bookmark` method retrieves the trashed entity and calls its `restore()` method, moving it back to the `ACTIVE` state. This unified approach to state management ensures that whether a bookmark was archived or trashed, the path back to "Active" is consistent.
