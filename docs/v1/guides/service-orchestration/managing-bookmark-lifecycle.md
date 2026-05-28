---
title: Managing Bookmark Lifecycle
description: How to perform CRUD operations on bookmarks, including validation, persistence, and automatic search indexing.
code_symbols: [SYM#fdcfaed9972e477ae4585fd1b279ac107fa534cd]
section_id: b846f611-eb4c-4b95-aefb-5483dd244df3_managing_bookmark_lifecycle
doc_type: how_to
section_type: guide
---
To manage the lifecycle of bookmarks in this application, you use the `BookmarkService` class. This service acts as a singleton facade that orchestrates validation, persistence via the repository, caching, and automatic search indexing.

## Creating a Bookmark

To create a new bookmark, pass a dictionary containing at least a `url` and `title` to the `create_bookmark` method. The service performs validation and automatically indexes the new entry for search.

```python
from app.services.bookmark_service import BookmarkService

service = BookmarkService()

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

The `create_bookmark` method returns a tuple of `(Bookmark, None)` on success or `(None, error_message)` if validation fails. Internally, it calls `_validate_url` and `_validate_title` before persisting the object.

## Retrieving and Listing Bookmarks

The service provides methods for both single-item retrieval and paginated listing.

### Fetching by ID
Retrieval via `get_bookmark` automatically utilizes an internal `LRUCache` to reduce database hits.

```python
bookmark = service.get_bookmark("some-uuid-string")
if bookmark:
    print(bookmark.title)
```

### Paginated Listing
Use `list_bookmarks` to retrieve sets of bookmarks with optional status filtering.

```python
# Get the first page of active bookmarks
bookmarks, total_count = service.list_bookmarks(page=1, per_page=25, status="active")

for b in bookmarks:
    print(f"{b.title}: {b.url}")
```

## Updating Bookmark Metadata

Updates are performed partially using the `update_bookmark` method. Like creation, this method triggers re-validation and updates the search index.

```python
update_data = {"title": "Updated Title"}
bookmark, error = service.update_bookmark("some-uuid-string", update_data)

if error:
    print(f"Update failed: {error}")
elif not bookmark:
    print("Bookmark not found")
```

## Managing Status: Archive, Trash, and Restore

The application uses a status-based lifecycle defined in `BookmarkStatus` (Active, Archived, Trashed). Note that `delete_bookmark` performs a **soft-delete** by moving the item to the trash.

```python
# Archive a bookmark
service.archive_bookmark("some-uuid-string")

# Soft-delete (move to trash)
service.delete_bookmark("some-uuid-string")

# Restore to active status
service.restore_bookmark("some-uuid-string")
```

Each of these operations invalidates the cache for that specific bookmark ID to ensure consistency.

## Searching Bookmarks

The `BookmarkService` maintains an in-memory `SearchIndex`. This index is updated automatically during `create_bookmark` and `update_bookmark` calls.

```python
# Perform a full-text search
results = service.search(query="example", limit=10)

for result in results:
    print(f"Found: {result.title}")
```

## Troubleshooting and Gotchas

### Singleton State
`BookmarkService` is implemented as a singleton. If you are writing tests, use the internal `_reset()` method to clear the repository, cache, and search index between test cases to ensure isolation.

### In-Memory Search Index
The search index is stored in memory and is rebuilt from the repository only when the service is initialized. If the underlying database is modified outside of the `BookmarkService` (e.g., via direct database scripts), the search index will be out of sync until the application restarts.

### Tag Deletion Side Effects
When you delete a tag using `delete_tag(tag_id)`, the service performs a cross-entity operation. It iterates through every bookmark containing that tag, removes the tag reference, saves the bookmark, and invalidates its cache entry. This can be an expensive operation if a tag is associated with a large number of bookmarks.
