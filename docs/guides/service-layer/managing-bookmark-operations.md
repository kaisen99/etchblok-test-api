---
title: Managing Bookmark Operations
description: Practical instructions on creating, updating, and deleting bookmarks, including validation logic and state management such as archiving and restoration.
code_symbols: [SYM#fdcfaed9972e477ae4585fd1b279ac107fa534cd]
section_id: 2baff010-02e5-49ae-aec0-9ca974f3a1c4_managing_bookmark_operations
doc_type: how_to
---

Manage the lifecycle of bookmarks, tags, and collections using the `BookmarkService`. This service acts as a singleton facade that orchestrates validation, persistence via the repository, caching, and search indexing.

## Creating a Bookmark

To create a new bookmark, provide a dictionary containing at least a `url` and `title`. The service validates these fields and automatically updates the search index and cache.

```python
from app.services.bookmark_service import BookmarkService

service = BookmarkService()
data = {
    "url": "https://github.com",
    "title": "GitHub",
    "description": "Where the world builds software"
}

bookmark, error = service.create_bookmark(data)

if error:
    # Handle validation errors (e.g., invalid URL or empty title)
    print(f"Error: {error}")
else:
    print(f"Created bookmark with ID: {bookmark.id}")
```

The `create_bookmark` method returns a tuple of `(Bookmark, None)` on success or `(None, error_message)` if validation fails.

## Updating and State Management

The `BookmarkService` supports partial updates and explicit state transitions like archiving and trashing.

### Partial Updates
Use `update_bookmark` to modify specific fields. The service re-validates any provided `url` or `title` and updates the `updated_at` timestamp via the internal `_touch()` method.

```python
update_data = {"title": "GitHub - Build Software"}
bookmark, error = service.update_bookmark(bookmark_id, update_data)

if not bookmark:
    print("Bookmark not found")
elif error:
    print(f"Update failed: {error}")
```

### Archiving and Restoration
Manage the visibility and status of bookmarks without deleting them.

```python
# Archive a bookmark
archived = service.archive_bookmark(bookmark_id)

# Restore to active status
restored = service.restore_bookmark(bookmark_id)
```

### Soft Deletion (Trashing)
The `delete_bookmark` method performs a soft-delete by moving the bookmark to a "trashed" status. It does not immediately remove the record from the repository.

```python
success = service.delete_bookmark(bookmark_id)
if success:
    print("Bookmark moved to trash")
```

## Organizing with Tags and Collections

The service handles cross-entity consistency, such as ensuring that deleting a tag removes it from all associated bookmarks.

### Managing Tags
When a tag is deleted, the service iterates through all bookmarks containing that tag, removes the reference, and invalidates their cache entries.

```python
# Create a tag
tag, error = service.create_tag({"name": "Development", "color": "blue"})

# Delete a tag (automatically strips it from all bookmarks)
service.delete_tag(tag.id)
```

### Managing Collections
Collections allow you to group bookmarks. Use the service to manage these relationships.

```python
# Create a collection
collection, error = service.create_collection({"name": "Reading List"})

# Add a bookmark to the collection
service.add_to_collection(collection.id, bookmark_id)

# Remove a bookmark from the collection
service.remove_from_collection(collection.id, bookmark_id)
```

## Listing and Searching

The service provides paginated access to bookmarks and integrates with a full-text search index.

### Paginated Listing
Filter bookmarks by status (e.g., "active", "archived", "trashed") and use pagination to manage large result sets.

```python
# List the first 25 active bookmarks
bookmarks, total_count = service.list_bookmarks(page=1, per_page=25, status="active")
```

### Full-Text Search
Search across bookmark titles and descriptions using the integrated search index.

```python
results = service.full_text_search(query="software", limit=10)
for b in results:
    print(f"Found: {b.title}")
```

## Troubleshooting and Gotchas

- **Singleton Instance**: `BookmarkService` is a singleton. Calling `BookmarkService()` always returns the same instance, sharing the `LRUCache` and `SearchIndex` across your application.
- **Cache Invalidation**: The service automatically invalidates the cache on `update`, `delete`, `archive`, and `restore`. If you bypass the service and use the repository directly, the cache may become stale.
- **Tag Cleanup**: Deleting a tag via `delete_tag` is an $O(N)$ operation where $N$ is the number of bookmarks using that tag. This ensures data consistency but can be resource-intensive if a tag is extremely common.
- **Validation Logic**: Validation for URLs and titles is centralized. `create_bookmark` and `update_bookmark` will both fail if the URL format is invalid or the title is empty.
