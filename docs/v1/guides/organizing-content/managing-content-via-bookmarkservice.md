---
title: Managing Content via BookmarkService
description: How to use the BookmarkService facade to create, update, and delete tags and collections.
code_symbols: [SYM#dd5fd545693e00d6c0b38892bbd18ed4afa136a1, SYM#fdcfaed9972e477ae4585fd1b279ac107fa534cd]
section_id: 298f759e-1589-4e7c-bc4a-5f0c41dae334_managing_content_via_bookmarkservice
doc_type: how_to
section_type: guide
---
The `BookmarkService` acts as the central facade for managing bookmarks, tags, and collections. It orchestrates business logic, including validation, persistence via the repository, search indexing, and cache management.

### Accessing the Service Instance

The `BookmarkService` is implemented as a singleton to ensure consistent state (like the search index and cache) across the application. You should instantiate it at the module level in your route handlers.

```python
from app.services.bookmark_service import BookmarkService

# Obtain the singleton instance
_service = BookmarkService()
```

### Managing Bookmarks

The service provides methods for the full lifecycle of a bookmark. Methods that perform validation return a tuple of `(result, error_message)`.

#### Creating and Updating Bookmarks
When creating or updating, the service automatically validates the URL and title, updates the search index, and invalidates the cache.

```python
# Creating a bookmark
data = {
    "url": "https://example.com",
    "title": "Example Domain",
    "description": "A useful example site"
}
bookmark, error = _service.create_bookmark(data)

if error:
    print(f"Validation failed: {error}")
else:
    print(f"Created bookmark: {bookmark.id}")

# Updating a bookmark
update_data = {"title": "New Title"}
updated_bookmark, error = _service.update_bookmark(bookmark.id, update_data)
```

#### Searching Bookmarks
The service provides a `full_text_search` method that queries the internal `SearchIndex` across bookmark titles and descriptions.

```python
results = _service.full_text_search("example", limit=10)
for b in results:
    print(b.title)
```

### Managing Tags

Tags are managed through the service to ensure that deletions are handled safely across the entire system.

#### Creating Tags
Tag names are validated against a set of reserved keywords.

```python
tag_data = {"name": "Research", "color": "blue"}
tag, error = _service.create_tag(tag_data)

if error:
    # Error might be "Tag name is required" or "'all' is a reserved tag name"
    print(f"Error: {error}")
```

#### Deleting Tags and Cleanup
When you delete a tag via `delete_tag`, the service automatically removes that tag from all bookmarks that currently use it and invalidates their cache entries.

```python
# This removes the tag from the system and all associated bookmarks
success = _service.delete_tag("tag-id-123")
```

### Organizing with Collections

Collections allow you to group bookmarks. The service handles the logic for adding and removing bookmarks from these groups.

```python
# Create a collection
collection, error = _service.create_collection({"name": "Project Alpha"})

if collection:
    # Add a bookmark to the collection
    success = _service.add_to_collection(collection.id, "bookmark-id-456")
    
    if not success:
        print("Collection not found or bookmark already in collection")

# Remove a bookmark
_service.remove_from_collection(collection.id, "bookmark-id-456")
```

### Troubleshooting and Constraints

*   **Reserved Tag Names**: You cannot create tags named `all`, `untagged`, `archived`, or `trash`. These are reserved for system filters.
*   **Validation Limits**: 
    *   Titles are limited to 256 characters.
    *   Descriptions are limited to 2048 characters.
    *   Tag names are limited to 50 characters.
*   **Singleton State in Tests**: Because `BookmarkService` is a singleton, state persists between tests. Use the internal `_reset()` method in your test setup/teardown to clear the repository, cache, and search index.
    ```python
    def setup_method(self):
        BookmarkService()._reset()
    ```
*   **Soft Deletion**: The `delete_bookmark` method performs a "soft delete" by moving the bookmark to the trash. Use `restore_bookmark` to bring it back or `archive_bookmark` to move it to the archive.
