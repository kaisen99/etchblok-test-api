---
title: Managing Tags and Collections
description: A guide to persisting organizational entities like tags and collections alongside bookmarks.
code_symbols: [SYM#adb8232356346a5957ff3a1a1b7ff70581f37649]
section_id: 70c6fe2d-82a1-4b2c-9b4e-ef781363119f_managing_tags_and_collections
doc_type: how_to
section_type: guide
---
Organizing bookmarks in this project is handled through **Tags** and **Collections**. These entities are persisted in the `BookmarkRepository` and managed via the `BookmarkService` to ensure data integrity across the system.

## Managing Tags

Tags are labels that can be attached to multiple bookmarks. They include metadata like colors and usage counts.

### Creating and Updating Tags

To create or update a tag, use the `BookmarkService`. It handles validation (via `_validate_tag_name`) before persisting the entity to the repository.

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

# Update an existing tag
update_data = {"color": "purple"}
updated_tag, error = service.update_tag(tag.id, update_data)
```

### Assigning Tags to Bookmarks

Tags are associated with bookmarks by storing the `tag_id` in the `Bookmark.tags` list. When you modify a bookmark's tags, you must save the bookmark back to the repository.

```python
from app.db.repository import BookmarkRepository

repo = BookmarkRepository()
bookmark = repo.get_bookmark("bookmark_123")

# Add a tag to a bookmark
if bookmark.add_tag("tag_research"):
    repo.save_bookmark(bookmark)

# Retrieve all bookmarks with a specific tag
bookmarks = repo.get_bookmarks_with_tag("tag_research")
```

### Deleting Tags and Maintaining Integrity

When a tag is deleted via `BookmarkService.delete_tag`, the service automatically iterates through all associated bookmarks to remove the tag reference and invalidates the cache for each affected bookmark.

```python
# This method handles the cleanup of tag references in bookmarks
success = service.delete_tag("tag_research")
```

## Managing Collections

Collections allow you to group bookmarks either manually or automatically using "Smart" filters.

### Manual Collections

Manual collections require you to explicitly add or remove bookmark IDs.

```python
# Create a manual collection
collection_data = {
    "name": "Project Alpha",
    "type": "manual"
}
collection, error = service.create_collection(collection_data)

# Add a bookmark to the collection
success = service.add_to_collection(collection.id, "bookmark_123")

# Remove a bookmark
success = service.remove_from_collection(collection.id, "bookmark_123")
```

### Smart Collections

Smart collections use a `filter_rule` to dynamically group bookmarks based on keywords found in their titles or descriptions.

```python
# Create a smart collection for "Python" related bookmarks
smart_data = {
    "name": "Python Resources",
    "type": "smart",
    "filter_rule": "python"
}
smart_collection, error = service.create_collection(smart_data)

# The filtering logic is implemented in Collection._apply_filter
# It checks if the keyword exists in the title or description (case-insensitive)
```

### Reordering and Pinning

You can pin collections to the top of the UI or reorder the bookmarks within a manual collection.

```python
collection = repo.get_collection("coll_456")

# Pin the collection
collection.pin()
repo.save_collection(collection)

# Reorder bookmarks (Manual collections only)
new_order = ["bookmark_C", "bookmark_A", "bookmark_B"]
collection.reorder(new_order)
repo.save_collection(collection)
```

## Troubleshooting and Gotchas

### In-Memory Persistence
The `BookmarkRepository` stores all data in-memory using dictionaries (`self._bookmarks`, `self._tags`, `self._collections`). **Data will be lost when the application restarts.** For production use, this repository would need to be replaced with a database-backed implementation.

### Performance of Tag Deletion
The `BookmarkService.delete_tag` method performs a linear scan over all bookmarks to find those containing the tag:

```python
for bookmark in self._repo.get_bookmarks_with_tag(tag_id):
    bookmark.remove_tag(tag_id)
    self._repo.save_bookmark(bookmark)
    self._cache.invalidate(bookmark.id)
```

In the current `BookmarkRepository` implementation, `get_bookmarks_with_tag` iterates through every bookmark in memory. This may cause performance degradation if the number of bookmarks is very large.

### Smart Collection Limitations
The `Collection._apply_filter` method currently only supports simple keyword matching. It does not support complex queries, boolean logic, or filtering by other attributes like status or creation date.