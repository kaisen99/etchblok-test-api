---
title: Organizing with Tags and Collections
description: How to use the service to categorize bookmarks through tags and group them into collections, including handling tag deletion side effects.
code_symbols: [SYM#fdcfaed9972e477ae4585fd1b279ac107fa534cd]
section_id: 32b000ef-08b3-418e-9d58-eaa24dbcc2df_organizing_with_tags_and_collections
doc_type: how_to
section_type: guide
---
To organize bookmarks in this application, you use the `BookmarkService` to manage tags (labels) and collections (containers). The service acts as a singleton facade, ensuring that operations like tag deletion correctly update all associated bookmarks and invalidate the relevant caches.

## Categorizing Bookmarks with Tags

You can create tags and associate them with bookmarks to provide a flat categorization layer. The `BookmarkService` handles the validation and persistence of these tags.

```python
from app.services.bookmark_service import BookmarkService

service = BookmarkService()

# Create a new tag
tag_data = {"name": "Research", "color": "blue"}
tag, error = service.create_tag(tag_data)

if error:
    print(f"Failed to create tag: {error}")
else:
    print(f"Created tag: {tag.name} with ID: {tag.id}")

# List all available tags
all_tags = service.list_tags()
```

## Managing Tag Deletion Side Effects

When you delete a tag using `delete_tag`, the service automatically performs a "scrubbing" operation. It iterates through every bookmark associated with that tag, removes the reference, saves the bookmark, and invalidates the cache for each one.

```python
# Deleting a tag triggers a cascade update across bookmarks
tag_id_to_remove = "tag-123"
success = service.delete_tag(tag_id_to_remove)

if success:
    # At this point, 'tag-123' has been removed from the 
    # 'tags' list of every bookmark in the repository.
    print("Tag deleted and stripped from all bookmarks.")
```

The implementation in `app/services/bookmark_service.py` ensures data consistency by coordinating the repository and the cache:

```python
def delete_tag(self, tag_id: str) -> bool:
    """Delete a tag and strip it from all bookmarks."""
    tag = self._repo.get_tag(tag_id)
    if not tag:
        return False
    # Side effect: Clean up all bookmarks using this tag
    for bookmark in self._repo.get_bookmarks_with_tag(tag_id):
        bookmark.remove_tag(tag_id)
        self._repo.save_bookmark(bookmark)
        self._cache.invalidate(bookmark.id)
    self._repo.delete_tag(tag_id)
    return True
```

## Grouping Bookmarks into Collections

Collections allow you to group bookmarks into named sets. Unlike tags, which are properties of the bookmark itself (stored in `Bookmark.tags`), collections are distinct entities that maintain a list of bookmark IDs.

```python
# 1. Create a collection
collection_data = {"name": "Project Alpha", "description": "Resources for Alpha"}
collection, error = service.create_collection(collection_data)

# 2. Add a bookmark to the collection
if collection:
    bookmark_id = "bookmark-456"
    added = service.add_to_collection(collection.id, bookmark_id)
    
    if not added:
        print("Could not add bookmark (it might already be in the collection)")

# 3. Remove a bookmark from the collection
removed = service.remove_from_collection(collection.id, "bookmark-456")
```

## Working with Smart Collections

The system supports "smart" collections that can be defined with a `filter_rule`. While manual collections require you to call `add_to_collection`, smart collections are intended to be populated based on their rules.

```python
# Create a smart collection
smart_data = {
    "name": "Python Resources",
    "type": "smart",
    "filter_rule": "python"
}
smart_coll, error = service.create_collection(smart_data)
```

Note that `add_to_collection` will return `False` if you attempt to manually add a bookmark to a collection where `collection_type` is `SMART`. This is enforced in `app/models/collection.py`:

```python
def add_bookmark(self, bookmark_id: str) -> bool:
    if self.is_smart or bookmark_id in self.bookmark_ids:
        return False
    self.bookmark_ids.append(bookmark_id)
    return True
```

## Service Architecture and Validation

The `BookmarkService` is implemented as a singleton using the `__new__` method. This ensures that the internal `LRUCache` (limited to 256 entries) and `SearchIndex` are shared across all modules.

The service enforces strict validation before persistence:
- **Collections**: `create_collection` requires a non-empty name.
- **Tags**: `create_tag` and `update_tag` use `_validate_tag_name` to ensure tag names meet system requirements.
- **URLs/Titles**: `create_bookmark` uses `_validate_url` and `_validate_title`.

## Troubleshooting

*   **Stale Bookmark Data**: If you bypass the `BookmarkService` and write directly to the `BookmarkRepository`, the `LRUCache` will become stale. Always use the service methods for updates to ensure `self._cache.invalidate(bookmark.id)` is called.
*   **Tag Deletion Performance**: Because `delete_tag` iterates over every bookmark containing that tag, deleting a very popular tag can be a slow operation as it involves multiple repository writes and cache invalidations.
*   **Collection Membership Failures**: If `add_to_collection` returns `False`, verify that the collection is not a "smart" collection and that the bookmark is not already a member.

```python
# Check if a collection is smart before attempting manual addition
collection = service.get_collection("coll-789")
if collection and collection.is_smart:
    print("Manual additions are disabled for smart collections.")
```