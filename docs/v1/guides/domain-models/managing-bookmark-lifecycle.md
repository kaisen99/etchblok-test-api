---
title: Managing Bookmark Lifecycle
description: Instructions on how to programmatically archive, trash, and restore bookmarks using the internal status API.
code_symbols: [SYM#d731bc2f45cac29b2961ab00083bab5345db0a5e, SYM#d570461c1ff2b0eb81e078e185a46de87938f933, SYM#6d5b77b3f04288620db996a9bc18b13d3bd1ad3b]
section_id: f9d4e295-c46d-4bb1-a1e2-ad1d7d01e379_managing_bookmark_lifecycle
doc_type: how_to
section_type: guide
---
To programmatically manage the lifecycle of a bookmark in this system, you use the status-transition methods provided by the `Bookmark` model or the orchestrated methods in the `BookmarkService`.

### Transitioning Bookmark Status

You can change a bookmark's visibility by calling `archive()`, `trash()`, or `restore()` on a `Bookmark` instance. These methods automatically update the `status` attribute using the `BookmarkStatus` enum and refresh the `updated_at` timestamp via the internal `_touch()` helper.

```python
from app.models.bookmark import Bookmark, BookmarkStatus

# Create a new active bookmark
bookmark = Bookmark(url="https://example.com", title="Example")
print(bookmark.status)  # BookmarkStatus.ACTIVE

# Archive the bookmark
bookmark.archive()
print(bookmark.status)  # BookmarkStatus.ARCHIVED

# Move to trash (soft-delete)
bookmark.trash()
print(bookmark.status)  # BookmarkStatus.TRASHED

# Restore to active status
bookmark.restore()
print(bookmark.status)  # BookmarkStatus.ACTIVE
```

### Orchestrating Lifecycle Changes with BookmarkService

In a production environment, you should use the `BookmarkService` to ensure that status changes are persisted to the repository and that the internal cache is invalidated.

The `BookmarkService` provides high-level methods that handle the retrieval, transition, and saving of bookmarks:

```python
from app.services.bookmark_service import BookmarkService

service = BookmarkService()
bookmark_id = "some-id-123"

# Archive a bookmark and persist changes
archived_bookmark = service.archive_bookmark(bookmark_id)

# Soft-delete a bookmark (moves it to TRASHED status)
success = service.delete_bookmark(bookmark_id)

# Restore a bookmark from trash or archive to ACTIVE status
restored_bookmark = service.restore_bookmark(bookmark_id)
```

### Filtering Bookmarks by Status

When retrieving bookmarks, you can filter the results based on their current lifecycle state. The `BookmarkRepository` and `BookmarkService` support a `status` filter string (matching the values in `BookmarkStatus`).

```python
# List only archived bookmarks
archived_list, total = service.list_bookmarks(status="archived")

# List only trashed bookmarks
trashed_list, total = service.list_bookmarks(status="trashed")
```

### API Integration

The lifecycle transitions are exposed via the following REST endpoints in `app/routes/bookmarks.py`:

| Action | Method | Endpoint | Description |
| :--- | :--- | :--- | :--- |
| **Archive** | `POST` | `/api/bookmarks/<id>/archive` | Moves bookmark to `archived` status. |
| **Trash** | `DELETE` | `/api/bookmarks/<id>` | **Soft-delete**: Moves bookmark to `trashed` status. |
| **Restore** | `POST` | `/api/bookmarks/<id>/restore` | Moves bookmark back to `active` status. |

### Troubleshooting and Gotchas

*   **Soft-Delete Behavior**: The `DELETE` method in the API and the `delete_bookmark` method in the service do **not** remove the record from the database. They perform a soft-delete by calling `bookmark.trash()`.
*   **Timestamp Updates**: Every lifecycle method (`archive`, `trash`, `restore`) calls the private `_touch()` method, which sets `updated_at` to `datetime.utcnow()`.
*   **Serialization Limits**: The `Bookmark.from_dict()` method is designed for creating new bookmarks from user input. It only parses `url`, `title`, `description`, and `tags`. It does **not** restore the `status` or `timestamps` from the dictionary; these will default to `ACTIVE` and the current time, respectively.
*   **Cache Invalidation**: When using the `BookmarkService` methods, the internal `LRUCache` is automatically invalidated for the specific `bookmark_id` to ensure subsequent reads fetch the updated status from the repository.
