---
title: Managing Bookmark Lifecycle
description: Step-by-step instructions for creating, retrieving, updating, and performing soft-deletes on bookmark entities.
code_symbols: [SYM#fdcfaed9972e477ae4585fd1b279ac107fa534cd]
section_id: 7f83fbc9-f18d-4441-ba4d-51cc21b1348b_managing_bookmark_lifecycle
doc_type: how_to
section_type: guide
---
To manage the lifecycle of bookmarks—including creation, retrieval, updates, and soft-deletes—you use the `BookmarkService`. This service acts as a singleton facade that orchestrates operations across the repository, search index, and cache.

### Accessing the Service

The `BookmarkService` is implemented as a singleton. You should instantiate it at the module level to share state across your application components.

```python
from app.services.bookmark_service import BookmarkService

# Obtain the singleton instance
service = BookmarkService()
```

### Creating a Bookmark

To create a bookmark, pass a dictionary containing at least a `url` and a `title`. The service performs validation and returns a tuple containing the created `Bookmark` object and an error message (if any).

```python
data = {
    "url": "https://example.com",
    "title": "Example Domain",
    "description": "A useful example site"
}

bookmark, error = service.create_bookmark(data)

if error:
    # Handle validation errors (e.g., invalid URL or empty title)
    print(f"Failed to create bookmark: {error}")
else:
    print(f"Created bookmark with ID: {bookmark.id}")
```

When a bookmark is created, the service automatically:
1. Validates the `url` and `title`.
2. Persists the entity via `BookmarkRepository`.
3. Indexes the content in the `SearchIndex`.
4. Invalidates any existing cache entry for that ID.

### Retrieving Bookmarks

You can retrieve a single bookmark by its ID or fetch a paginated list with optional status filtering.

#### Single Retrieval (Cached)
The `get_bookmark` method checks the internal `LRUCache` before querying the repository.

```python
bookmark_id = "some-uuid"
bookmark = service.get_bookmark(bookmark_id)

if not bookmark:
    print("Bookmark not found")
```

#### Paginated Listing and Filtering
Use `list_bookmarks` to retrieve sets of bookmarks. You can filter by status using the strings `"active"`, `"archived"`, or `"trashed"`.

```python
# Get the first page of archived bookmarks
bookmarks, total_count = service.list_bookmarks(
    page=1, 
    per_page=25, 
    status="archived"
)

print(f"Found {total_count} archived bookmarks.")
```

### Updating and State Transitions

The service provides methods for partial updates and explicit state transitions like archiving or restoring.

#### Partial Updates
The `update_bookmark` method accepts a dictionary of fields to change. It automatically updates the `updated_at` timestamp and refreshes the search index.

```python
updates = {"title": "New Improved Title"}
bookmark, error = service.update_bookmark(bookmark_id, updates)

if error:
    print(f"Update failed: {error}")
```

#### Archiving and Restoring
State transitions are handled by specific methods that manage the underlying entity status and cache invalidation.

```python
# Move to archive
archived_bookmark = service.archive_bookmark(bookmark_id)

# Restore to active status (from archive or trash)
restored_bookmark = service.restore_bookmark(bookmark_id)
```

### Soft-Deleting Bookmarks

In this project, `delete_bookmark` performs a **soft-delete**. It moves the bookmark to the "trash" status rather than removing it from the database.

```python
success = service.delete_bookmark(bookmark_id)

if not success:
    print("Could not delete: Bookmark does not exist")
```

### Troubleshooting

#### Shared State in Tests
Because `BookmarkService` is a singleton, state persists between test cases. If you are writing unit tests, use the internal `_reset()` method in your setup or teardown to ensure a clean environment.

```python
def setup_function():
    service = BookmarkService()
    service._reset()  # Reinitializes repo, cache, and search index
```

#### Validation Failures
The service does not raise exceptions for invalid data. Instead, it follows a Go-like return pattern: `(Result, Error)`. Always check if the second element of the tuple is not `None` before proceeding with the result.

#### Tag Side Effects
When you delete a tag using `service.delete_tag(tag_id)`, the service iterates through every bookmark containing that tag to remove the reference and invalidates their cache entries. This can be a heavy operation if many bookmarks share the same tag.
