---
title: Your First Bookmark Lifecycle
description: A step-by-step tutorial for beginners that covers creating a bookmark, updating its metadata, and eventually moving it to the trash.
code_symbols: [SYM#dd5fd545693e00d6c0b38892bbd18ed4afa136a1, SYM#d731bc2f45cac29b2961ab00083bab5345db0a5e, SYM#fdcfaed9972e477ae4585fd1b279ac107fa534cd, SYM#d570461c1ff2b0eb81e078e185a46de87938f933, SYM#6d5b77b3f04288620db996a9bc18b13d3bd1ad3b]
section_id: 9c935236-d5f2-4a14-a191-1234ef79a1d2_your_first_bookmark_lifecycle
doc_type: tutorial
section_type: guide
---
In this tutorial, you will learn how to manage the complete lifecycle of a bookmark using the core services of this API. You will walk through creating a new bookmark, updating its metadata, archiving it for later, and finally moving it to the trash.

### Prerequisites

To follow this tutorial, you need to have the application environment set up so you can import the service and model classes.

```python
from app.services.bookmark_service import BookmarkService
from app.models.bookmark import BookmarkStatus

# Initialize the singleton service
service = BookmarkService()
```

### Step 1: Creating a Bookmark

The first step is to persist a new URL. You use the `create_bookmark` method, which accepts a dictionary containing the bookmark's data.

```python
data = {
    "url": "https://www.python.org",
    "title": "Python Programming Language",
    "description": "The official home of the Python Programming Language"
}

bookmark, error = service.create_bookmark(data)

if error:
    print(f"Failed to create bookmark: {error}")
else:
    print(f"Created bookmark with ID: {bookmark.id}")
    print(f"Current Status: {bookmark.status.value}")
```

When you call `create_bookmark`, the service performs several actions:
1.  **Validation**: It runs `_validate_url` and `_validate_title` to ensure the data is well-formed.
2.  **Persistence**: It saves the bookmark to the `BookmarkRepository`.
3.  **Indexing**: It adds the bookmark to the `SearchIndex` for full-text search.
4.  **Caching**: It invalidates any existing cache for this ID to ensure consistency.

### Step 2: Updating Metadata

As your needs change, you might want to update the title or description. The `update_bookmark` method allows for partial updates.

```python
update_data = {
    "description": "Updated description for the Python homepage."
}

updated_bookmark, error = service.update_bookmark(bookmark.id, update_data)

if updated_bookmark:
    print(f"New description: {updated_bookmark.description}")
    print(f"Last updated at: {updated_bookmark.updated_at}")
```

The service automatically calls `bookmark._touch()` during an update, which refreshes the `updated_at` timestamp. Like the creation step, this also updates the search index and invalidates the cache.

### Step 3: Archiving the Bookmark

If you no longer need a bookmark actively but want to keep it, you can move it to the archive. This changes its status without removing it from the system.

```python
archived_bookmark = service.archive_bookmark(bookmark.id)

if archived_bookmark:
    print(f"Status after archiving: {archived_bookmark.status}")
    # Output: Status after archiving: BookmarkStatus.ARCHIVED
```

The `archive_bookmark` method transitions the status to `BookmarkStatus.ARCHIVED`. Archived bookmarks are typically excluded from default listings unless a status filter is applied in `list_bookmarks`.

### Step 4: Moving to the Trash

When you want to delete a bookmark, the API performs a "soft-delete" by moving it to the trash.

```python
success = service.delete_bookmark(bookmark.id)

if success:
    # Fetch the bookmark again to verify its status
    trashed_bookmark = service.get_bookmark(bookmark.id)
    print(f"Status in trash: {trashed_bookmark.status}")
    # Output: Status in trash: BookmarkStatus.TRASHED
```

The `delete_bookmark` method calls `bookmark.trash()`, setting the status to `BookmarkStatus.TRASHED`. This allows you to recover the bookmark later if the deletion was accidental.

### Step 5: Restoring a Bookmark

If you change your mind, you can bring a bookmark back to the `ACTIVE` state using `restore_bookmark`.

```python
restored_bookmark = service.restore_bookmark(bookmark.id)

if restored_bookmark:
    print(f"Restored status: {restored_bookmark.status}")
    # Output: Restored status: BookmarkStatus.ACTIVE
```

### Complete Lifecycle Example

Here is the full sequence of operations in a single script:

```python
from app.services.bookmark_service import BookmarkService

service = BookmarkService()

# 1. Create
bookmark, _ = service.create_bookmark({
    "url": "https://github.com",
    "title": "GitHub"
})

# 2. Update
service.update_bookmark(bookmark.id, {"description": "Where world builds software"})

# 3. Archive
service.archive_bookmark(bookmark.id)

# 4. Trash (Soft-delete)
service.delete_bookmark(bookmark.id)

# 5. Restore
service.restore_bookmark(bookmark.id)

# Final check
final_bookmark = service.get_bookmark(bookmark.id)
print(f"Final Lifecycle State: {final_bookmark}")
```

By using the `BookmarkService`, you ensure that every state change is correctly validated, persisted, indexed for search, and updated in the cache.