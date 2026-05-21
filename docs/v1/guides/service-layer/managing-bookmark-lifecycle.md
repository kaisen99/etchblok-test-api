---
title: Managing Bookmark Lifecycle
description: Practical instructions for creating, updating, archiving, and deleting bookmarks, including handling validation errors and state transitions.
code_symbols: [SYM#fdcfaed9972e477ae4585fd1b279ac107fa534cd]
section_id: f39560d-c110-4f27-8546-05932e0fba52_managing_bookmark_lifecycle
doc_type: how_to
---

To manage the lifecycle of bookmarks in this application, you use the `BookmarkService`. This service acts as a singleton facade that coordinates validation, database persistence, search indexing, and cache management.

## Initializing the Bookmark Service

The `BookmarkService` is implemented as a singleton. You should obtain the shared instance by calling the class constructor.

```python
from app.services.bookmark_service import BookmarkService

# Obtain the singleton instance
service = BookmarkService()
```

## Creating a New Bookmark

To create a bookmark, pass a dictionary containing at least a `url` and a `title` to `create_bookmark`. This method returns a tuple containing the created `Bookmark` object and an error message. If the error message is not `None`, the creation failed validation.

```python
data = {
    "url": "https://example.com",
    "title": "Example Domain",
    "description": "A useful site for testing."
}

bookmark, error = service.create_bookmark(data)

if error:
    # Handle validation error (e.g., invalid URL or missing title)
    print(f"Failed to create bookmark: {error}")
else:
    print(f"Created bookmark with ID: {bookmark.id}")
```

When a bookmark is created, the service automatically:
1. Validates the URL and title.
2. Persists the bookmark to the repository.
3. Indexes the content for full-text search.
4. Invalidates any existing cache for that ID.

## Updating Bookmark Details

The `update_bookmark` method supports partial updates. Only the fields provided in the data dictionary will be modified. Like the creation method, it returns a `(bookmark, error)` tuple.

```python
update_data = {
    "title": "Updated Example Title",
    "description": "New description for this bookmark."
}

bookmark, error = service.update_bookmark("bookmark_id_123", update_data)

if error:
    # Handle validation error
    print(f"Update failed: {error}")
elif not bookmark:
    # Handle case where the bookmark ID does not exist
    print("Bookmark not found")
else:
    print(f"Successfully updated: {bookmark.title}")
```

## Retrieving and Listing Bookmarks

The service provides methods for both direct retrieval by ID and paginated listing.

### Fetching a Single Bookmark
The `get_bookmark` method checks the internal `LRUCache` before querying the repository.
```python
bookmark = service.get_bookmark("bookmark_id_123")
if bookmark:
    print(f"Retrieved: {bookmark.url}")
```

### Listing with Pagination and Filters
Use `list_bookmarks` to retrieve a subset of bookmarks. It returns a tuple of `(list_of_bookmarks, total_count)`.
```python
# Get the second page of archived bookmarks, 10 per page
bookmarks, total = service.list_bookmarks(page=2, per_page=10, status="archived")

print(f"Showing {len(bookmarks)} of {total} archived bookmarks")
for b in bookmarks:
    print(f"- {b.title}")
```

## Troubleshooting and Gotchas

### Return Type Consistency
Be aware that mutation methods in `BookmarkService` use different return patterns:
- **Create/Update**: Returns `Tuple[Optional[Bookmark], Optional[str]]`. You must check the second element for validation errors.

### Singleton State
Because `BookmarkService` is a singleton, it shares its internal `LRUCache` across the entire application.

### Search Indexing Side Effects
Every time `create_bookmark` or `update_bookmark` is called, the service triggers `self._search.index_bookmark(bookmark)`. If your search indexer is slow or unavailable, these lifecycle methods will be impacted.
