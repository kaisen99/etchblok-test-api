---
title: Managing Bookmark States
description: How to transition bookmarks between active, archived, and trashed states using the built-in lifecycle methods.
code_symbols: [SYM#d731bc2f45cac29b2961ab00083bab5345db0a5e, SYM#6d5b77b3f04288620db996a9bc18b13d3bd1ad3b, SYM#d570461c1ff2b0eb81e078e185a46de87938f933]
section_id: 1d328c16-c394-4ed5-9ec9-9553a0561fd4_managing_bookmark_states
doc_type: how_to
section_type: guide
---
To manage the lifecycle of a bookmark in this system, you transition its state between active, archived, and trashed using the `Bookmark` model's lifecycle methods and the `BookmarkService` for persistence.

### Transitioning Bookmark States

The most common way to change a bookmark's state is through the `BookmarkService`, which ensures the change is persisted to the database and the cache is invalidated.

```python
from app.services.bookmark_service import BookmarkService

service = BookmarkService()

# Archive a bookmark
archived_bookmark = service.archive_bookmark("bookmark_id_123")

# Soft-delete (trash) a bookmark
success = service.delete_bookmark("bookmark_id_123")

# Restore a bookmark to ACTIVE status
restored_bookmark = service.restore_bookmark("bookmark_id_123")
```

### Understanding Bookmark States

The system uses the `BookmarkStatus` enum (defined in `app/models/bookmark.py`) to track visibility:

*   `ACTIVE`: The default state for new bookmarks.
*   `ARCHIVED`: For bookmarks that are saved but no longer in the primary view.
*   `TRASHED`: A "soft-deleted" state.

The `Bookmark` class provides internal methods that update the `status` attribute and automatically refresh the `updated_at` timestamp via the private `_touch()` helper:

```python
# Internal implementation in app/models/bookmark.py
def archive(self) -> None:
    self.status = BookmarkStatus.ARCHIVED
    self._touch()

def trash(self) -> None:
    self.status = BookmarkStatus.TRASHED
    self._touch()

def restore(self) -> None:
    self.status = BookmarkStatus.ACTIVE
    self._touch()
```

### Filtering Bookmarks by Status

When retrieving bookmarks, you can filter the results by their current status using the `list_bookmarks` method in the service layer.

```python
from app.services.bookmark_service import BookmarkService
from app.models.bookmark import BookmarkStatus

service = BookmarkService()

# List only archived bookmarks
archived_list, total = service.list_bookmarks(status=BookmarkStatus.ARCHIVED.value)

# List only trashed bookmarks
trash_bin, total = service.list_bookmarks(status=BookmarkStatus.TRASHED.value)
```

### Triggering Transitions via API

The REST API exposes these transitions through specific endpoints. For example, the archive functionality is triggered via a `POST` request:

```python
# app/routes/bookmarks.py
@bookmarks_bp.route("/<bookmark_id>/archive", methods=["POST"])
def archive_bookmark(bookmark_id: str):
    """Archive a bookmark."""
    bookmark = _service.archive_bookmark(bookmark_id)
    if not bookmark:
        return jsonify({"error": "Bookmark not found"}), 404
    return jsonify(bookmark.to_dict())
```

### Troubleshooting: Soft-delete vs. Hard-delete

A common point of confusion is the difference between "deleting" a bookmark in the service layer versus the repository layer:

*   **Service Layer (`BookmarkService.delete_bookmark`)**: Performs a **soft-delete**. It calls `bookmark.trash()`, moving the bookmark to the `TRASHED` state. This is the recommended method for standard application logic.
*   **Repository Layer (`BookmarkRepository.delete_bookmark`)**: Performs a **hard-delete**. It physically removes the record from the underlying storage. This should only be used for permanent cleanup or GDPR-style deletions.

Always use the `BookmarkService` for state transitions to ensure that the `SearchIndex` and `LRUCache` are correctly updated.
