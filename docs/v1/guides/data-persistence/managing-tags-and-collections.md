---
title: Managing Tags and Collections
description: Instructions on how to persist and manage metadata entities like tags and collections.
code_symbols: [SYM#adb8232356346a5957ff3a1a1b7ff70581f37649]
section_id: 778aa659-e3d3-4aeb-a555-0a737ba94c39_managing_tags_and_collections
doc_type: how_to
section_type: guide
---
To manage metadata like tags and collections, you use the `BookmarkService` facade, which orchestrates updates across the `BookmarkRepository`, search index, and cache.

### Creating and Managing Tags

Tags are created by passing a dictionary of attributes to the `BookmarkService.create_tag` method. The service validates the input and persists the `Tag` entity to the `BookmarkRepository`.

```python
from app.services.bookmark_service import BookmarkService
from app.models.tag import TagColor

service = BookmarkService()

# Create a new tag
tag_data = {
    "name": "Research",
    "color": "blue",
    "description": "Academic papers and articles"
}
tag, error = service.create_tag(tag_data)

if tag:
    print(f"Created tag: {tag.name} (ID: {tag.id})")
```

#### Cascading Tag Deletion
When a tag is deleted via `BookmarkService.delete_tag`, the system automatically performs a cascading update. It removes the tag ID from all associated bookmarks, saves the updated bookmarks back to the repository, and invalidates their cache entries.

```python
# Deleting a tag triggers a cascade to all associated bookmarks
success = service.delete_tag("tag_id_123")
```

The underlying logic in `BookmarkService` ensures data consistency:
```python
def delete_tag(self, tag_id: str) -> bool:
    """Delete a tag and strip it from all bookmarks."""
    tag = self._repo.get_tag(tag_id)
    if not tag:
        return False
    for bookmark in self._repo.get_bookmarks_with_tag(tag_id):
        bookmark.remove_tag(tag_id)
        self._repo.save_bookmark(bookmark)
        self._cache.invalidate(bookmark.id)
    self._repo.delete_tag(tag_id)
    return True
```

### Organizing with Collections

Collections allow you to group bookmarks. You can create a collection and then add or remove bookmarks using their unique IDs.

```python
# Create a manual collection
collection_data = {
    "name": "Project Alpha",
    "collection_type": "manual"
}
collection, error = service.create_collection(collection_data)

# Add a bookmark to the collection
if collection:
    service.add_to_collection(collection.id, "bookmark_id_456")
```

### Working with Smart Collections

The system supports two types of collections defined in `CollectionType`:
1.  **MANUAL**: Bookmarks are added and removed explicitly by the user.
2.  **SMART**: Bookmarks are included automatically based on a `filter_rule`.

#### Smart Collection Constraints
You cannot manually add bookmarks to a smart collection. The `Collection.add_bookmark` method (and consequently `BookmarkService.add_to_collection`) will return `False` if attempted.

```python
from app.models.collection import CollectionType

# Creating a smart collection
smart_data = {
    "name": "Recent PDF's",
    "collection_type": "smart",
    "filter_rule": "extension:pdf"
}
smart_collection, _ = service.create_collection(smart_data)

# This will fail because it's a smart collection
success = service.add_to_collection(smart_collection.id, "some_id") 
# success will be False
```

### Persistence and Constraints

The `BookmarkRepository` serves as the persistence layer. In the current implementation, it uses in-memory dictionaries (`_tags` and `_collections`), meaning data is lost when the application restarts.

Key constraints to keep in mind:
- **Tag Names**: Must be non-empty and are limited to 50 characters (validated in `Tag.rename`).
- **Collection Names**: Required for creation in `BookmarkService.create_collection`.
- **In-Memory**: All mutation methods in `BookmarkRepository` (like `save_tag` and `save_collection`) persist immediately to the internal dictionaries.

```python
class BookmarkRepository:
    def __init__(self) -> None:
        self._bookmarks: Dict[str, Bookmark] = {}
        self._tags: Dict[str, Tag] = {}
        self._collections: Dict[str, Collection] = {}

    def save_tag(self, tag: Tag) -> None:
        """Insert or update a tag."""
        self._tags[tag.id] = tag
```

### Troubleshooting

- **Data Loss**: If the application crashes or restarts, all tags and collections are wiped because `BookmarkRepository` is in-memory.
- **Manual Add Failures**: If `add_to_collection` returns `False`, verify that the collection is not a `SMART` type and that the bookmark is not already present in the collection.
- **Tag Usage Counts**: The `Tag` model maintains a `usage_count`, but this must be manually incremented or decremented when bookmarks are updated outside of the `BookmarkService` cascading logic.
