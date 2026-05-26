---
title: Managing Bookmark Lifecycle
description: Instructions on creating, retrieving, updating, and deleting bookmarks, including how the service handles soft-deletion and archiving.
code_symbols: [SYM#fdcfaed9972e477ae4585fd1b279ac107fa534cd]
section_id: 96ca48b4-caf5-4106-8d77-a641a1384bdd_managing_bookmark_lifecycle
doc_type: how_to
section_type: guide
---
To manage the lifecycle of bookmarks in this application, you use the `BookmarkService` class. This service acts as a facade that coordinates validation, persistence via the `BookmarkRepository`, full-text indexing via the `SearchIndex`, and caching via an `LRUCache`.

### Creating a Bookmark

To create a new bookmark, pass a dictionary containing at least a `url` and `title` to the `create_bookmark` method. The service validates these fields before persisting the entity.

```python
from app.services.bookmark_service import BookmarkService

service = BookmarkService()

data = {
    "url": "https://example.com",
    "title": "Example Domain",
    "description": "A site for examples"
}

bookmark, error = service.create_bookmark(data)

if error:
    print(f"Validation failed: {error}")
else:
    print(f"Created bookmark with ID: {bookmark.id}")
```

When a bookmark is created:
1.  The URL and title are validated using `_validate_url` and `_validate_title` from `app.models._validators`.
2.  The bookmark is saved to the `BookmarkRepository`.
3.  The bookmark is added to the `SearchIndex` for full-text search.
4.  The cache entry for this ID is invalidated to ensure consistency.

### Retrieving and Listing Bookmarks

The service provides methods for both single-item retrieval and paginated listing. Single-item retrieval automatically utilizes an internal `LRUCache`.

```python
# Retrieve a single bookmark by ID (uses cache)
bookmark = service.get_bookmark("some-uuid-123")

# List bookmarks with pagination and status filtering
# Status can be "active", "archived", or "trashed"
bookmarks, total_count = service.list_bookmarks(page=1, per_page=25, status="active")
```

### Updating a Bookmark

The `update_bookmark` method supports partial updates. Only the fields provided in the data dictionary will be modified.

```python
update_data = {
    "title": "Updated Example Title",
    "description": "New description for the bookmark"
}

bookmark, error = service.update_bookmark("some-uuid-123", update_data)

if error:
    # Handle validation error (e.g., invalid URL or empty title)
    pass
elif not bookmark:
    # Handle case where bookmark ID does not exist
    pass
```

Updating a bookmark triggers a re-index in the `SearchIndex` and invalidates the `LRUCache` entry for that ID.

### Managing Status: Archiving, Trashing, and Restoring

The application implements a soft-deletion pattern. Bookmarks are not immediately removed from the database; instead, their status is updated.

#### Soft-Deleting (Trashing)
Use `delete_bookmark` to move a bookmark to the "trashed" state.

```python
# Soft-deletes the bookmark
success = service.delete_bookmark("some-uuid-123")

if not success:
    print("Bookmark not found")
```

#### Archiving
Use `archive_bookmark` to move a bookmark to the "archived" state.

```python
bookmark = service.archive_bookmark("some-uuid-123")
```

#### Restoring
Use `restore_bookmark` to return a bookmark to the "active" state from either the trash or the archive.

```python
bookmark = service.restore_bookmark("some-uuid-123")
```

### Troubleshooting and Gotchas

*   **Singleton Pattern**: `BookmarkService` is a singleton. Calling `BookmarkService()` always returns the same instance, sharing the `LRUCache` and `BookmarkRepository` across the entire application.
*   **In-Memory Persistence**: The current `BookmarkRepository` implementation is in-memory. All bookmarks, tags, and collections will be lost when the application restarts.
*   **Soft-Deletion**: The `delete_bookmark` method performs a soft-delete by calling `bookmark.trash()`. There is currently no service method for permanent hard-deletion.
*   **Cache Invalidation**: The service manually manages cache invalidation during `update_bookmark`, `delete_bookmark`, and `archive_bookmark` calls. If you bypass the service and interact with the repository directly, the cache may become stale.
