---
title: Organizing Data with Tags and Collections
description: Instructions on how to persist tags and collections and maintain relationships between them and bookmarks.
code_symbols: [SYM#adb8232356346a5957ff3a1a1b7ff70581f37649]
section_id: 6e8a13bb-acaa-453c-a0ba-b4b2147c39ff_organizing_data_with_tags_and_collections
doc_type: how_to
section_type: guide
---
Organizing bookmarks in this system is handled through two primary mechanisms: **Tags** for flat, multi-label categorization and **Collections** for hierarchical or rule-based grouping. These relationships are managed by the `BookmarkService`, which ensures data integrity across the `BookmarkRepository`.

## Working with Tags

Tags are independent entities that can be associated with any number of bookmarks. The relationship is stored on the `Bookmark` model as a list of tag IDs.

### Creating and Attaching Tags

To organize a bookmark with a tag, you first ensure the tag exists and then add its ID to the bookmark's `tags` list.

```python
from app.services.bookmark_service import BookmarkService
from app.db.repository import BookmarkRepository

service = BookmarkService()
repo = BookmarkRepository()

# 1. Create a new tag
tag_data = {"name": "Research", "color": "blue"}
tag, error = service.create_tag(tag_data)

if tag:
    # 2. Retrieve the bookmark
    bookmark = repo.get_bookmark("bookmark-id-123")
    
    if bookmark:
        # 3. Attach the tag ID to the bookmark
        bookmark.add_tag(tag.id)
        
        # 4. Persist the change
        repo.save_bookmark(bookmark)
```

### Maintaining Integrity on Deletion

When a tag is deleted, the system must remove references to that tag from all bookmarks to prevent "dangling" tag IDs. The `BookmarkService.delete_tag` method handles this automatically by iterating through all bookmarks associated with the tag.

```python
# app/services/bookmark_service.py

def delete_tag(self, tag_id: str) -> bool:
    """Delete a tag and strip it from all bookmarks."""
    tag = self._repo.get_tag(tag_id)
    if not tag:
        return False
        
    # Find all bookmarks using this tag and remove the reference
    for bookmark in self._repo.get_bookmarks_with_tag(tag_id):
        bookmark.remove_tag(tag_id)
        self._repo.save_bookmark(bookmark)
        self._cache.invalidate(bookmark.id)
        
    # Finally, remove the tag entity itself
    self._repo.delete_tag(tag_id)
    return True
```

## Organizing with Collections

Collections provide two ways to group bookmarks: **Manual** (explicitly added) and **Smart** (automatically populated via filters).

### Manual Collections

Manual collections store an ordered list of bookmark IDs. Use the `BookmarkService` to manage membership, which ensures the collection exists before attempting to modify it.

```python
from app.services.bookmark_service import BookmarkService

service = BookmarkService()

# Add a bookmark to a manual collection
success = service.add_to_collection(
    collection_id="manual-col-id", 
    bookmark_id="bookmark-id-123"
)

# Remove a bookmark from a manual collection
success = service.remove_from_collection(
    collection_id="manual-col-id", 
    bookmark_id="bookmark-id-123"
)
```

### Smart Collections

Smart collections do not store bookmark IDs directly. Instead, they use a `filter_rule` to dynamically select bookmarks based on their `title` or `description`.

The filtering logic is implemented in `Collection._apply_filter`:

```python
# app/models/collection.py

def _apply_filter(self, bookmarks: list) -> List[str]:
    """Evaluate the filter_rule against a list of bookmarks."""
    if not self.filter_rule:
        return []
    keyword = self.filter_rule.lower()
    return [
        b.id for b in bookmarks 
        if keyword in b.title.lower() or keyword in b.description.lower()
    ]
```

To create a smart collection, set the `type` to `smart` and provide a `filter_rule`:

```python
collection_data = {
    "name": "Python Articles",
    "type": "smart",
    "filter_rule": "python"
}
collection, error = service.create_collection(collection_data)
```

## Persistence and Integrity Details

*   **In-Memory Storage**: The `BookmarkRepository` uses Python dictionaries (`self._bookmarks`, `self._tags`, `self._collections`) for storage. Data is lost when the application process terminates.
*   **Referential Integrity**: The repository does not enforce foreign key constraints. Integrity (such as ensuring a `tag_id` added to a bookmark actually exists) is the responsibility of the `BookmarkService` layer.
*   **Usage Tracking**: The `Tag` model includes a `usage_count` field and `increment_usage()`/`decrement_usage()` methods. However, these must be called manually when adding or removing tags from bookmarks, as the current `BookmarkService` implementation does not automatically update these counts during bookmark updates.
