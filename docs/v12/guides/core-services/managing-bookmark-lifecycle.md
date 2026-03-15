---
title: Managing Bookmark Lifecycle
description: Practical instructions for creating, updating, archiving, and deleting bookmarks using the service's core methods.
code_symbols: [SYM#fdcfaed9972e477ae4585fd1b279ac107fa534cd]
section_id: b38ca5c2-6a4a-475c-be86-e2c1a42a34b9_managing_bookmark_lifecycle
doc_type: how_to
section_type: guide
---
To manage the lifecycle of bookmarks in this application, use the **BookmarkService** class. This service acts as a facade that coordinates operations between the database repository, the search index, and the internal LRU cache.

### Creating a New Bookmark

To create a bookmark, pass a dictionary containing at least a `url` and a `title` to the `create_bookmark` method. The service performs validation and returns a tuple containing the created object and an error message (if any).

```python
from app.services.bookmark_service import BookmarkService

service = BookmarkService()

data = {
    "url": "https://example.com",
    "title": "Example Domain",
    "description": "A useful starting point for web examples."
}

bookmark, error = service.create_bookmark(data)

if error:
    # Validation failed (e.g., invalid URL or empty title)
    print(f"Validation failed: {error}")
else:
    print(f"Created bookmark with ID: {bookmark.id}")
```

The service automatically handles:
1. **Validation**: Checks the URL and Title format using internal validators.
2. **Persistence**: Saves the bookmark to the `BookmarkRepository`.
3. **Indexing**: Adds the bookmark to the `SearchIndex` for full-text search.
4. **Cache Management**: Invalidates any existing cache entry for that ID.

### Retrieving and Searching Bookmarks

The service provides methods for both direct retrieval (with caching) and full-text search.

#### Direct Retrieval and Listing
`get_bookmark` first checks the internal `LRUCache` before querying the repository.

```python
# Single retrieval (uses cache)
bookmark = service.get_bookmark("some-uuid-123")

# Paginated listing with optional status filter
bookmarks, total_count = service.list_bookmarks(page=1, per_page=10, status="active")
```

#### Full-Text Search
The `search` method queries the `SearchIndex` to find bookmarks based on their content.

```python
results = service.search("example query", limit=10)
for bookmark in results:
    print(bookmark.title)
```

### Updating and Lifecycle Transitions

The `update_bookmark` method supports partial updates. You only need to provide the fields you wish to change. For status changes, use the dedicated lifecycle methods.

```python
service = BookmarkService()
bookmark_id = "some-uuid-123"

# Partial update
update_data = {"title": "Updated Example Title"}
bookmark, error = service.update_bookmark(bookmark_id, update_data)

# Archive a bookmark
archived = service.archive_bookmark(bookmark_id)

# Restore a bookmark to active status
restored = service.restore_bookmark(bookmark_id)
```

When you update a bookmark, the service calls `bookmark._touch()` to refresh the `updated_at` timestamp before persisting changes and updating the search index.

### Soft-Deleting Bookmarks

The `delete_bookmark` method performs a **soft-delete**. It does not remove the record from the database; instead, it moves the bookmark to a "trashed" status.

```python
service = BookmarkService()
success = service.delete_bookmark("some-uuid-123")

if not success:
    print("Could not delete: Bookmark not found")
```

### Organizing Bookmarks with Tags and Collections

The service also manages the relationship between bookmarks, tags, and collections, ensuring data integrity across these entities.

#### Managing Collections
You can group bookmarks into collections using the following methods:

```python
service = BookmarkService()

# Create a collection
collection, error = service.create_collection({"name": "Research Project"})

# Add a bookmark to the collection
if collection:
    service.add_to_collection(collection.id, "bookmark-uuid-123")

# Remove a bookmark from the collection
service.remove_from_collection(collection.id, "bookmark-uuid-123")
```

#### Tag Integrity
When a tag is deleted, the service automatically strips that tag from all bookmarks that were using it and invalidates their cache entries.

```python
# This will remove the tag from all associated bookmarks before deleting the tag itself
service.delete_tag("tag-uuid-456")
```

### Troubleshooting and Gotchas

*   **Singleton Pattern**: `BookmarkService` is a singleton. Calling `BookmarkService()` multiple times returns the same instance, sharing the same `LRUCache` and `SearchIndex` state across your application.
*   **Validation Errors**: Both `create_bookmark` and `update_bookmark` return a `(result, error)` tuple. Always check the second element; if it is not `None`, the operation failed validation.
*   **Cache Invalidation**: The service automatically invalidates the cache on every write operation (`update`, `delete`, `archive`). If you bypass the service and write directly to the repository, the cache will become stale.
*   **Soft-Delete vs. Hard-Delete**: There is no hard-delete method in the `BookmarkService`. To permanently remove a bookmark, you would need to interact with the `BookmarkRepository` directly, though this is not standard practice in this application.