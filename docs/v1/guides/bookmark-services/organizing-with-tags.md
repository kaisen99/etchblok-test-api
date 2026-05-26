---
title: Organizing with Tags
description: How to manage tags and the automated logic that ensures tags are stripped from bookmarks when a tag is deleted.
code_symbols: [SYM#fdcfaed9972e477ae4585fd1b279ac107fa534cd]
section_id: 8b1ce7ef-e3c1-4f48-876b-14f793945927_organizing_with_tags
doc_type: how_to
section_type: guide
---
To manage tags and ensure data integrity when they are removed, use the `BookmarkService` to handle the lifecycle of tags and their association with bookmarks.

### Managing Tag Lifecycle

The `BookmarkService` provides a centralized way to create, update, and delete tags while automatically maintaining referential integrity across your bookmarks.

```python
from app.services.bookmark_service import BookmarkService
from app.models.tag import TagColor

service = BookmarkService()

# 1. Create a new tag
tag_data = {
    "name": "Research",
    "color": "blue",
    "description": "Academic and technical papers"
}
tag, error = service.create_tag(tag_data)

# 2. Assign the tag to a bookmark (via update)
bookmark_id = "abc12345"
service.update_bookmark(bookmark_id, {"tags": [tag.id]})

# 3. Delete the tag and automatically strip it from all bookmarks
success = service.delete_tag(tag.id)
```

### Automated Tag Stripping

When you delete a tag using `BookmarkService.delete_tag`, the service performs an automated cleanup to ensure no bookmarks are left with "dangling" references to a non-existent tag.

The `delete_tag` method in `app/services/bookmark_service.py` implements this logic:

1.  **Lookup**: It retrieves all bookmarks associated with the tag using `BookmarkRepository.get_bookmarks_with_tag`.
2.  **Removal**: For each bookmark found, it calls `bookmark.remove_tag(tag_id)`.
3.  **Persistence**: It saves the updated bookmark back to the repository.
4.  **Cache Invalidation**: It invalidates the cache for each affected bookmark to ensure subsequent reads fetch the updated tag list.
5.  **Final Deletion**: It removes the tag entity itself from the repository.

```python
def delete_tag(self, tag_id: str) -> bool:
    """Delete a tag and strip it from all bookmarks."""
    tag = self._repo.get_tag(tag_id)
    if not tag:
        return False
    
    # Automated stripping logic
    for bookmark in self._repo.get_bookmarks_with_tag(tag_id):
        bookmark.remove_tag(tag_id)
        self._repo.save_bookmark(bookmark)
        self._cache.invalidate(bookmark.id)
        
    self._repo.delete_tag(tag_id)
    return True
```

### Updating Tag Metadata

You can modify a tag's name or color using `update_tag`. The `TagColor` enum in `app/models/tag.py` defines the allowed color values.

```python
from app.models.tag import TagColor

# Update tag name and color
update_data = {
    "name": "Deep Learning",
    "color": TagColor.PURPLE.value
}
updated_tag, error = service.update_tag(tag_id, update_data)
```

### Listing All Tags

To retrieve a list of all available tags for display or filtering, use `list_tags`.

```python
tags = service.list_tags()
for tag in tags:
    print(f"{tag.name} ({tag.color.value}): used by {tag.usage_count} bookmarks")
```

### Troubleshooting and Gotchas

*   **Manual Usage Counts**: Although the `Tag` model includes a `usage_count` attribute and methods like `increment_usage()` and `decrement_usage()`, the current `BookmarkService` implementation does not automatically call these when bookmarks are created or updated. You must manually manage these counts if your UI relies on them.
*   **Performance**: The `delete_tag` operation iterates through every bookmark containing the tag. In the current `BookmarkRepository` (which is in-memory), this is efficient, but be aware that this pattern scales linearly with the number of bookmarks using that specific tag.
*   **Cache Sync**: If you bypass `BookmarkService` and interact with `BookmarkRepository` directly to remove tags, the `LRUCache` will not be invalidated, leading to stale data in the API responses. Always use the service layer for deletions.
