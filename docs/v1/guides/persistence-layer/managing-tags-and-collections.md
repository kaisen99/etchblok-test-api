---
title: Managing Tags and Collections
description: Instructions for persisting and retrieving tags and collections, including linking bookmarks to specific tags.
code_symbols: [SYM#adb8232356346a5957ff3a1a1b7ff70581f37649]
section_id: 2eae44da-7a28-43a6-a351-9fc8659c8003_managing_tags_and_collections
doc_type: how_to
section_type: guide
---
To manage tags and collections in this system, you use the `BookmarkService` to orchestrate operations between the `BookmarkRepository`, the domain models (`Tag`, `Collection`, `Bookmark`), and the cache.

### Creating and Persisting Tags

You can create a new tag by passing a dictionary of attributes to the `BookmarkService.create_tag` method. This method validates the tag name and persists it to the repository.

```python
from app.services.bookmark_service import BookmarkService
from app.models.tag import TagColor

service = BookmarkService()

# Create a new tag
tag_data = {
    "name": "Research",
    "color": "blue",
    "description": "Academic and technical papers"
}
tag, error = service.create_tag(tag_data)

if tag:
    print(f"Created tag: {tag.name} with ID: {tag.id}")
else:
    print(f"Error: {error}")
```

### Linking Bookmarks to Tags

To associate a bookmark with a tag, you must update the `Bookmark` instance and then persist the change via the repository. The `BookmarkService` does not have a direct `add_tag_to_bookmark` method; instead, you modify the model and save it.

```python
from app.db.repository import BookmarkRepository

repo = BookmarkRepository()

# 1. Retrieve the bookmark and tag
bookmark = repo.get_bookmark("abc123def456")
tag = repo.get_tag("xyz789")

if bookmark and tag:
    # 2. Link the tag ID to the bookmark
    if bookmark.add_tag(tag.id):
        # 3. Persist the updated bookmark
        repo.save_bookmark(bookmark)
        
        # 4. (Optional) Increment usage count on the tag
        tag.increment_usage()
        repo.save_tag(tag)
```

### Managing Collections

Collections can be **manual** (where you explicitly add bookmarks) or **smart** (where bookmarks are filtered automatically).

#### Creating a Manual Collection
```python
service = BookmarkService()

collection_data = {
    "name": "Project Alpha",
    "type": "manual"
}
collection, error = service.create_collection(collection_data)

# Add a bookmark to the collection
if collection:
    success = service.add_to_collection(collection.id, "abc123def456")
```

#### Creating a Smart Collection
Smart collections use a `filter_rule` to dynamically group bookmarks based on keywords in their title or description.

```python
collection_data = {
    "name": "Python Resources",
    "type": "smart",
    "filter_rule": "python"
}
collection, error = service.create_collection(collection_data)

# Note: Smart collections do not use add_to_collection. 
# They use the _apply_filter method internally to find matches.
```

### Retrieving Bookmarks by Tag

The `BookmarkRepository` provides a specific method to find all bookmarks associated with a particular tag ID.

```python
repo = BookmarkRepository()

# Get all bookmarks with the 'Research' tag
bookmarks = repo.get_bookmarks_with_tag("xyz789")

for b in bookmarks:
    print(f"Found: {b.title} ({b.url})")
```

### Handling Tag Deletions (Cascading)

When a tag is deleted via `BookmarkService.delete_tag`, the service automatically performs a cascade to ensure data integrity. It removes the tag reference from all associated bookmarks and invalidates their cache entries before deleting the tag itself.

```python
# This will:
# 1. Find all bookmarks using this tag
# 2. Remove the tag ID from each bookmark's .tags list
# 3. Save the updated bookmarks
# 4. Invalidate the cache for those bookmarks
# 5. Delete the tag from the repository
success = service.delete_tag("xyz789")
```

### Troubleshooting and Gotchas

*   **In-Memory Storage**: The `BookmarkRepository` is currently in-memory. All tags and collections created during a session will be lost when the application restarts.
*   **ID Lengths**: When manually looking up entities, remember that IDs have specific lengths:
    *   **Bookmarks**: 12-character hex strings.
    *   **Tags**: 8-character hex strings.
    *   **Collections**: 10-character hex strings.
*   **Smart Collection Persistence**: Smart collections do not store a list of `bookmark_ids` persistently. They are intended to be populated dynamically using `Collection._apply_filter(bookmarks_list)`.
*   **Alphabetical Sorting**: When listing tags for the UI, they are typically sorted alphabetically. The `Tag` class implements `__lt__` to support this:
    ```python
    tags = service.list_tags()
    sorted_tags = sorted(tags) # Sorts by name (case-insensitive)
    ```
