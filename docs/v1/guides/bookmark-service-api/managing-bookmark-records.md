---
title: Managing Bookmark Records
description: How to perform core bookmark operations including creation and partial updates.
code_symbols: [SYM#fdcfaed9972e477ae4585fd1b279ac107fa534cd]
section_id: fea4ebcf-8ae9-4332-9cfa-fc3e254d9ddc_managing_bookmark_records
doc_type: how_to
---

To manage bookmark records in this application, you use the `BookmarkService` class. This service acts as a singleton facade that coordinates validation, persistence via the repository, search indexing, and cache management.

### Initializing the Service

The `BookmarkService` is implemented as a singleton to ensure shared state (like the LRU cache) across the application. You should instantiate it at the module level.

```python
from app.services.bookmark_service import BookmarkService

# Initialize the service singleton
service = BookmarkService()
```

### Creating a New Bookmark

Use the `create_bookmark` method by passing a dictionary containing at least a `url` and a `title`. This method returns a tuple containing the created `Bookmark` object and an error message (if any).

```python
data = {
    "url": "https://example.com",
    "title": "Example Domain",
    "description": "A site for examples"
}

bookmark, error = service.create_bookmark(data)

if error:
    # Handle validation errors (e.g., invalid URL or empty title)
    print(f"Failed to create bookmark: {error}")
else:
    print(f"Created bookmark with ID: {bookmark.id}")
```

### Retrieving and Listing Bookmarks

The service provides methods for both single-record retrieval and paginated listing. Single retrieval automatically checks the internal `LRUCache` before querying the repository.

#### Get a Single Bookmark
```python
bookmark = service.get_bookmark("some-uuid-string")

if not bookmark:
    print("Bookmark not found")
```

#### List with Pagination and Filtering
The `list_bookmarks` method returns a tuple of `(list, total_count)`. You can filter by status (e.g., "active", "archived", "trashed").

```python
# Get the second page of active bookmarks, 10 per page
bookmarks, total = service.list_bookmarks(page=2, per_page=10, status="active")

for b in bookmarks:
    print(f"{b.title}: {b.url}")
```

### Performing Partial Updates

The `update_bookmark` method supports partial updates. Only the keys present in the provided dictionary will be modified. The service automatically re-validates updated fields, updates the search index, and invalidates the cache entry.

```python
update_data = {"title": "New Updated Title"}
bookmark, error = service.update_bookmark("some-uuid-string", update_data)

if error:
    print(f"Update failed: {error}")
elif not bookmark:
    print("Bookmark not found")
```

### Troubleshooting and Gotchas

*	**Singleton State**: Because `BookmarkService` is a singleton, the internal `LRUCache` is shared across all requests in the same process.
*	**Automatic Indexing**: Every time you call `create_bookmark` or `update_bookmark`, the `SearchIndex` is updated. If you bypass the service and use the repository directly, your search results will become stale.
*	**Validation**: Validation for URLs and titles is performed inside the service methods before any persistence occurs. If `create_bookmark` or `update_bookmark` returns an error string, the database remains unchanged.
