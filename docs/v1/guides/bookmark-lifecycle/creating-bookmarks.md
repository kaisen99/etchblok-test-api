---
title: Creating Bookmarks
description: A practical guide on using the BookmarkService to validate, create, and persist new bookmarks while ensuring cache consistency.
code_symbols: [SYM#dd5fd545693e00d6c0b38892bbd18ed4afa136a1, SYM#fdcfaed9972e477ae4585fd1b279ac107fa534cd, SYM#6d5b77b3f04288620db996a9bc18b13d3bd1ad3b]
section_id: 4abf97d7-bce5-46a8-9261-f95fbc65dece_creating_bookmarks
doc_type: how_to
section_type: guide
---
To create a new bookmark in this project, use the `BookmarkService` singleton to validate the input, persist the record, and update the search index and cache.

### Basic Bookmark Creation

The most common way to create a bookmark is by passing a dictionary containing at least a `url` and a `title` to the `create_bookmark` method.

```python
from app.services.bookmark_service import BookmarkService

# Get the singleton instance
service = BookmarkService()

data = {
    "url": "https://example.com",
    "title": "Example Domain"
}

bookmark, error = service.create_bookmark(data)

if error:
    print(f"Validation failed: {error}")
else:
    print(f"Created bookmark with ID: {bookmark.id}")
```

### Handling Validation and Errors

The `create_bookmark` method returns a tuple: `(Optional[Bookmark], Optional[str])`. You must check the second element for an error message before proceeding. Validation is performed using internal helpers `_validate_url` and `_validate_title`.

```python
def create_bookmark_handler(request_data):
    service = BookmarkService()
    
    # The service handles validation of 'url' and 'title'
    bookmark, error = service.create_bookmark(request_data)
    
    if error:
        # Return error message (e.g., "Invalid URL format")
        return {"error": error}, 400
        
    # Success: return the serialized bookmark
    return bookmark.to_dict(), 201
```

### Creating with Optional Fields

The `Bookmark` model supports additional fields like `description`, `tags`, and `metadata`. These can be passed directly in the input dictionary.

```python
data = {
    "url": "https://github.com",
    "title": "GitHub",
    "description": "Where the world builds software",
    "tags": ["development", "git"],
    "metadata": {
        "priority": "high",
        "source": "browser-extension"
    }
}

bookmark, error = service.create_bookmark(data)
```

### Side Effects of Creation

When you call `create_bookmark`, the `BookmarkService` performs several operations to ensure system-wide consistency:

1.  **Validation**: Checks the URL and title.
2.  **Persistence**: Saves the `Bookmark` instance to the `BookmarkRepository`.
3.  **Indexing**: Adds the bookmark to the `SearchIndex` for full-text search.
4.  **Cache Invalidation**: Invalidates the cache for the new bookmark ID to prevent stale reads.

The implementation in `app/services/bookmark_service.py` follows this flow:

```python
def create_bookmark(self, data: Dict[str, Any]) -> Tuple[Optional[Bookmark], Optional[str]]:
    error = _validate_url(data.get("url", "")) or _validate_title(data.get("title", ""))
    if error:
        return None, error

    bookmark = Bookmark.from_dict(data)
    self._repo.save_bookmark(bookmark)
    self._search.index_bookmark(bookmark)
    self._cache.invalidate(bookmark.id)
    return bookmark, None
```

### Troubleshooting and Gotchas

*   **Validation Bypass**: Creating a `Bookmark` directly via the constructor or `Bookmark.from_dict` bypasses the URL and title validation logic. Always use `BookmarkService.create_bookmark` for external input.
*   **Singleton State**: `BookmarkService` is a singleton. If you are writing tests, use the internal `_reset()` method to clear the repository and cache between test cases.
*   **ID Generation**: The `Bookmark` model generates a 12-character hex ID automatically using `uuid.uuid4().hex[:12]`. You do not need to provide an ID in the input data.
*   **Manual Property Updates**: If you update properties on a `Bookmark` object directly (outside of service methods), you must call `bookmark._touch()` to update the `updated_at` timestamp and manually save it via the repository to trigger indexing.