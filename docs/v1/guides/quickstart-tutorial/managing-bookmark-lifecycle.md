---
title: Managing Bookmark Lifecycle
description: How to archive, trash, and restore bookmarks to manage their visibility and status within the system.
code_symbols: [SYM#fdcfaed9972e477ae4585fd1b279ac107fa534cd, SYM#d570461c1ff2b0eb81e078e185a46de87938f933, SYM#6d5b77b3f04288620db996a9bc18b13d3bd1ad3b]
section_id: a1c40615-ea82-4f7e-9764-e71815d0e0b5_managing_bookmark_lifecycle
doc_type: how_to
section_type: guide
---
To manage the visibility and lifecycle of a bookmark, use the `BookmarkService` to transition between the three states defined in `BookmarkStatus`: `ACTIVE`, `ARCHIVED`, and `TRASHED`.

## Transitioning Bookmark Status

The `BookmarkService` provides high-level methods to change a bookmark's status. These methods automatically handle repository persistence and cache invalidation.

```python
from app.services.bookmark_service import BookmarkService

service = BookmarkService()
bookmark_id = "abc123def456"

# 1. Archive a bookmark (moves to ARCHIVED status)
archived_bookmark = service.archive_bookmark(bookmark_id)

# 2. Soft-delete a bookmark (moves to TRASHED status)
success = service.delete_bookmark(bookmark_id)

# 3. Restore a bookmark (moves back to ACTIVE status)
restored_bookmark = service.restore_bookmark(bookmark_id)
```

### How Status Transitions Work
When you call these service methods, they invoke the corresponding transition methods on the `Bookmark` model:

*   **`archive()`**: Sets `status` to `BookmarkStatus.ARCHIVED`.
*   **`trash()`**: Sets `status` to `BookmarkStatus.TRASHED`.
*   **`restore()`**: Sets `status` to `BookmarkStatus.ACTIVE`.

Each of these methods also calls a private `_touch()` helper to update the `updated_at` timestamp of the bookmark.

## Filtering Bookmarks by Status

You can retrieve bookmarks based on their current lifecycle state by passing a status string to the `list_bookmarks` method.

```python
from app.services.bookmark_service import BookmarkService

service = BookmarkService()

# List only archived bookmarks
archived_list, total = service.list_bookmarks(status="archived", page=1, per_page=10)

# List only trashed bookmarks
trash_list, total = service.list_bookmarks(status="trashed")

# List active bookmarks (default visibility)
active_list, total = service.list_bookmarks(status="active")
```

The `BookmarkRepository` validates the status string against the `BookmarkStatus` enum. If an invalid status string is provided, the filter is ignored, and all bookmarks are returned.

## REST API Integration

If you are building an API layer, you can map these service calls to POST endpoints as seen in `app/routes/bookmarks.py`:

```python
from flask import Blueprint, jsonify
from app.services.bookmark_service import BookmarkService

bookmarks_bp = Blueprint("bookmarks", __name__)
_service = BookmarkService()

@bookmarks_bp.route("/<bookmark_id>/archive", methods=["POST"])
def archive_bookmark(bookmark_id: str):
    bookmark = _service.archive_bookmark(bookmark_id)
    if not bookmark:
        return jsonify({"error": "Bookmark not found"}), 404
    return jsonify(bookmark.to_dict())

@bookmarks_bp.route("/<bookmark_id>/restore", methods=["POST"])
def restore_bookmark(bookmark_id: str):
    bookmark = _service.restore_bookmark(bookmark_id)
    if not bookmark:
        return jsonify({"error": "Bookmark not found"}), 404
    return jsonify(bookmark.to_dict())
```

## Troubleshooting and Gotchas

### Soft-Delete vs. Hard-Delete
In this codebase, `BookmarkService.delete_bookmark()` performs a **soft-delete**. It calls `bookmark.trash()`, which keeps the record in the database but changes its status to `TRASHED`. 

If you need to permanently remove a bookmark from the system, you must call the repository directly, as the service does not expose a hard-delete method:

```python
# Permanent removal (Hard-delete)
# Note: This bypasses service-level cache invalidation
service._repo.delete_bookmark(bookmark_id)
```

### Status Persistence in `from_dict`
The `Bookmark.from_dict()` method is designed for creating new bookmarks from user input. It does **not** extract the `status` or timestamps from the provided dictionary; it always initializes new instances with `BookmarkStatus.ACTIVE` and current timestamps.

### Invalid Status Filters
The `BookmarkRepository.list_bookmarks` method uses a `try/except` block when parsing the status filter. If you pass a string that does not exist in `BookmarkStatus` (e.g., `status="deleted"`), the repository silently ignores the filter and returns bookmarks of all statuses.
