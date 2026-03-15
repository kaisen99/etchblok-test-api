---
title: Organizing with Tags and Collections
description: How to use the repository to manage tags and collections, and how to retrieve bookmarks associated with specific tags.
code_symbols: [SYM#adb8232356346a5957ff3a1a1b7ff70581f37649]
section_id: 4b9cebfe-f96d-4c5a-8334-7af97b767a6b_organizing_with_tags_and_collections
doc_type: how_to
section_type: guide
---
Organize bookmarks by grouping them into collections or labeling them with tags. This project uses the `BookmarkRepository` for in-memory storage and the `BookmarkService` to orchestrate relationships between these entities.

## Managing Tags

Tags are labels that can be applied to multiple bookmarks. Use the `BookmarkService` to create tags and the `BookmarkRepository` to retrieve bookmarks associated with them.

```python
from app.services.bookmark_service import BookmarkService
from app.models.tag import TagColor

service = BookmarkService()

# 1. Create a new tag
tag_data = {
    "name": "Research",
    "color": TagColor.BLUE.value,
    "description": "Academic papers and articles"
}
tag, error = service.create_tag(tag_data)

# 2. Create a bookmark with the tag
bookmark_data = {
    "url": "https://example.com/paper",
    "title": "A Great Research Paper",
    "tags": [tag.id]
}
bookmark, error = service.create_bookmark(bookmark_data)

# 3. Retrieve bookmarks with a specific tag
# Note: This is performed directly on the repository
bookmarks = service._repo.get_bookmarks_with_tag(tag.id)
```

### Tag Cleanup and Integrity
When a tag is deleted via `BookmarkService.delete_tag`, the service automatically iterates through all associated bookmarks to remove the tag reference and invalidates the cache for those bookmarks.

```python
# From app/services/bookmark_service.py
def delete_tag(self, tag_id: str) -> bool:
    """Delete a tag and strip it from all bookmarks."""
    tag = self._repo.get_tag(tag_id)
    if not tag:
        return False
    # Clean up references in bookmarks
    for bookmark in self._repo.get_bookmarks_with_tag(tag_id):
        bookmark.remove_tag(tag_id)
        self._repo.save_bookmark(bookmark)
        self._cache.invalidate(bookmark.id)
    # Remove the tag itself
    self._repo.delete_tag(tag_id)
    return True
```

## Managing Collections

Collections group bookmarks into named sets. They can be **Manual** (explicitly managed) or **Smart** (populated by rules).

### Manual Collections
Manual collections require you to explicitly add or remove bookmark IDs.

```python
# Create a manual collection
collection_data = {"name": "Read Later", "type": "manual"}
collection, _ = service.create_collection(collection_data)

# Add a bookmark to the collection
# This uses Collection.add_bookmark internally
success = service.add_to_collection(collection.id, "bookmark_123")
```

### Smart Collections
Smart collections use a `filter_rule` to dynamically identify bookmarks based on their title or description.

```python
from app.models.collection import Collection, CollectionType

# Define a smart collection for 'Python' related content
smart_col = Collection(
    name="Python Resources",
    collection_type=CollectionType.SMART,
    filter_rule="python"
)

# The model provides a helper to evaluate the rule against a list of bookmarks
# From app/models/collection.py
def _apply_filter(self, bookmarks: list) -> List[str]:
    if not self.filter_rule:
        return []
    keyword = self.filter_rule.lower()
    return [b.id for b in bookmarks if keyword in b.title.lower() or keyword in b.description.lower()]
```

## Retrieving Bookmarks by Tag

To find all bookmarks that share a specific tag, use the `get_bookmarks_with_tag` method in the `BookmarkRepository`. This method performs a linear scan of the in-memory bookmark store.

```python
# From app/db/repository.py
def get_bookmarks_with_tag(self, tag_id: str) -> List[Bookmark]:
    """Return all bookmarks that have a specific tag attached."""
    return [b for b in self._bookmarks.values() if tag_id in b.tags]
```

## Troubleshooting

### Data Persistence
The `BookmarkRepository` is strictly in-memory. All tags, collections, and their associations are lost when the application process restarts.

### Tag Update Limitations
The `BookmarkService.update_bookmark` method currently only supports updating `title`, `description`, and `url`. Tags can only be set during bookmark creation via `create_bookmark`.

### Collection Validation
The `BookmarkService.add_to_collection` method validates that the collection exists, but it does **not** currently verify if the `bookmark_id` being added exists in the repository.

```python
# From app/services/bookmark_service.py
def add_to_collection(self, collection_id: str, bookmark_id: str) -> bool:
    collection = self._repo.get_collection(collection_id)
    if not collection:
        return False
    # bookmark_id existence is not checked here
    if not collection.add_bookmark(bookmark_id):
        return False
    self._repo.save_collection(collection)
    return True
```

### Smart Collection Population
While the `Collection` model contains an `_apply_filter` method, the `BookmarkService` does not automatically populate the `bookmark_ids` list for smart collections during standard retrieval. You must manually trigger the filter logic if you need to resolve the IDs for a smart collection.