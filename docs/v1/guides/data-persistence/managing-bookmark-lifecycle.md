---
title: Managing Bookmark Lifecycle
description: How to perform CRUD operations on bookmarks, including handling status transitions and hard-deletion.
code_symbols: [SYM#adb8232356346a5957ff3a1a1b7ff70581f37649]
section_id: 0bbdef84-5588-4b77-877b-ed966dcca19b_managing_bookmark_lifecycle
doc_type: how_to
section_type: guide
---
To manage the lifecycle of bookmarks in this project, you should primarily use the `BookmarkService` facade. This service coordinates between the `BookmarkRepository` for persistence, the `SearchIndex` for full-text search, and an `LRUCache` for performance.

## Creating and Updating Bookmarks

To create a new bookmark, use the `create_bookmark` method. This method performs validation on the URL and title before persisting the entity and indexing it for search.

```python
from app.services.bookmark_service import BookmarkService

service = BookmarkService()

# Create a new bookmark
data = {
    "url": "https://example.com",
    "title": "Example Domain",
    "description": "A site for examples"
}
bookmark, error = service.create_bookmark(data)

if error:
    print(f"Failed to create: {error}")
else:
    print(f"Created bookmark: {bookmark.id}")

# Partially update an existing bookmark
update_data = {"title": "Updated Example Title"}
updated_bookmark, error = service.update_bookmark(bookmark.id, update_data)
```

The `update_bookmark` method in `BookmarkService` automatically calls `_touch()` on the `Bookmark` model to update the `updated_at` timestamp and invalidates the cache for that specific ID.

## Managing Status Transitions

Bookmarks in this system follow a state machine defined by the `BookmarkStatus` enum in `app/models/bookmark.py`. You can transition bookmarks between `ACTIVE`, `ARCHIVED`, and `TRASHED` states.

### Archiving and Restoring
Use the service methods to move bookmarks in and out of the archive.

```python
# Move to ARCHIVED status
archived = service.archive_bookmark(bookmark_id)

# Restore to ACTIVE status (works for both archived and trashed bookmarks)
restored = service.restore_bookmark(bookmark_id)
```

### Soft-Deletion (Trashing)
The `BookmarkService.delete_bookmark` method performs a **soft-delete** by moving the bookmark to the trash.

```python
# Soft-delete (sets status to BookmarkStatus.TRASHED)
success = service.delete_bookmark(bookmark_id)
```

## Listing and Filtering Bookmarks

The `list_bookmarks` method provides paginated access to bookmarks and allows filtering by their status.

```python
# List the first 10 active bookmarks
bookmarks, total = service.list_bookmarks(page=1, per_page=10, status="active")

for b in bookmarks:
    print(f"[{b.status.value}] {b.title} - {b.url}")

# List trashed bookmarks
trashed_items, total_trashed = service.list_bookmarks(status="trashed")
```

Note that the `page` parameter is **1-based**. The repository sorts results by `created_at` in descending order by default.

## Hard Deletion

If you need to permanently remove a bookmark from the system (bypassing the trash), you must interact with the `BookmarkRepository` directly. 

> [!WARNING]
> Hard-deletion is irreversible and does not automatically update the `SearchIndex`. You should typically prefer the soft-delete provided by `BookmarkService`.

```python
from app.db.repository import BookmarkRepository

# Access the repository via the service instance (internal access)
repo = service._repo

# Permanently remove from in-memory storage
existed = repo.delete_bookmark(bookmark_id)

if existed:
    # Manually invalidate cache to ensure consistency
    service._cache.invalidate(bookmark_id)
```

## Troubleshooting

### Data Persistence
The `BookmarkRepository` is an **in-memory** implementation. All data is lost when the application process restarts. For production use, the repository would need to be replaced with a persistent database implementation.

### Search Index Sync
When performing low-level operations directly on the `BookmarkRepository` (like hard-deletion), the `SearchIndex` is not automatically updated. The `BookmarkService` methods handle this synchronization for you during standard CRUD operations.

### Status Validation
The `list_bookmarks` method validates the `status` string against the `BookmarkStatus` enum. If an invalid status string is provided, the filter is ignored, and all bookmarks are returned.
