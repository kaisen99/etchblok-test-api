---
title: Archiving and Restoring Bookmarks
description: Instructions on transitioning bookmarks between active and archived states, including the impact on the search index and cache.
code_symbols: [SYM#dd5fd545693e00d6c0b38892bbd18ed4afa136a1, SYM#fdcfaed9972e477ae4585fd1b279ac107fa534cd, SYM#6d5b77b3f04288620db996a9bc18b13d3bd1ad3b]
section_id: 84a35b1c-3cc5-4a5e-ae4f-c5f762c479f3_archiving_and_restoring_bookmarks
doc_type: how_to
section_type: guide
---
To manage the lifecycle of a bookmark, you can transition it between active, archived, and trashed states using the `BookmarkService`. These operations update the bookmark's status, persist the change to the repository, and invalidate the local cache.

### Archive a Bookmark

To move a bookmark to the archive, use the `archive_bookmark` method. This sets the status to `BookmarkStatus.ARCHIVED`.

```python
from app.services.bookmark_service import BookmarkService

service = BookmarkService()
bookmark_id = "a1b2c3d4e5f6"

# Archive the bookmark
archived_bookmark = service.archive_bookmark(bookmark_id)

if archived_bookmark:
    print(f"Status: {archived_bookmark.status}")  # BookmarkStatus.ARCHIVED
```

The `BookmarkService.archive_bookmark` method performs three key actions:
1. Calls `bookmark.archive()` on the model, which updates the `status` and refreshes the `updated_at` timestamp via `_touch()`.
2. Persists the change using `self._repo.save_bookmark(bookmark)`.
3. Invalidates the cache for that ID via `self._cache.invalidate(bookmark_id)`.

### Restore a Bookmark

To return an archived or trashed bookmark to the active state, use `restore_bookmark`. This sets the status back to `BookmarkStatus.ACTIVE`.

```python
from app.services.bookmark_service import BookmarkService

service = BookmarkService()
bookmark_id = "a1b2c3d4e5f6"

# Restore to active status
restored_bookmark = service.restore_bookmark(bookmark_id)

if restored_bookmark:
    print(f"Status: {restored_bookmark.status}")  # BookmarkStatus.ACTIVE
```

### Soft-Delete (Trash) a Bookmark

The system uses a "trash" state for soft-deletion. Use `delete_bookmark` to move a bookmark to the trash.

```python
from app.services.bookmark_service import BookmarkService

service = BookmarkService()
bookmark_id = "a1b2c3d4e5f6"

# Soft-delete the bookmark
success = service.delete_bookmark(bookmark_id)
```

Unlike `archive_bookmark`, `delete_bookmark` returns a boolean indicating success rather than the updated object. Internally, it calls `bookmark.trash()`, which sets the status to `BookmarkStatus.TRASHED`.

### Filtering by Status

When listing bookmarks, you can filter the results by their current status. This is useful for displaying only archived items or excluding trashed items from the main view.

```python
from app.services.bookmark_service import BookmarkService
from app.models.bookmark import BookmarkStatus

service = BookmarkService()

# List only archived bookmarks
archived_list, total = service.list_bookmarks(status=BookmarkStatus.ARCHIVED.value)

# List only active bookmarks
active_list, total = service.list_bookmarks(status=BookmarkStatus.ACTIVE.value)
```

### Troubleshooting and Impact

#### Search Index Persistence
A critical behavior of the `BookmarkService` is that archiving or trashing a bookmark **does not** remove it from the `SearchIndex`. The search index is only updated during `create_bookmark` and `update_bookmark`. 

This means that if you perform a full-text search using `service.full_text_search(query)`, archived and trashed bookmarks will still appear in the results. You must manually filter the search results by the `status` attribute if you wish to exclude them.

#### Cache Invalidation
The `BookmarkService` automatically calls `self._cache.invalidate(bookmark_id)` during archive, restore, and delete operations. This ensures that subsequent calls to `get_bookmark(bookmark_id)` fetch the fresh state from the repository rather than returning a stale version from the `LRUCache`.

#### Status Enum Values
If you are interacting with the API or repository directly, ensure you use the string values defined in `BookmarkStatus`:
- `ACTIVE`: `"active"`
- `ARCHIVED`: `"archived"`
- `TRASHED`: `"trashed"`