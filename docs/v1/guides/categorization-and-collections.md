---
title: Categorization and Collections
description: Organize bookmarks using tags and group them into manual or smart collections based on automated filter rules.
code_symbols: [SYM#e15c91e9e7eae95d052f50388a60d0bc30b3fe67, SYM#97d8a6cbf0c47108aa2beb39fafa695229654067, SYM#dd5fd545693e00d6c0b38892bbd18ed4afa136a1]
section_id: c84bac94-5fa7-449e-985a-f4f52ef70cd6_categorization_and_collections
doc_type: guide
section_type: guide
---
The **kaisen99-etchblok-test-api-851c354** codebase provides two primary mechanisms for organizing bookmarks: **Tags** for flexible, many-to-many labeling, and **Collections** for grouping bookmarks into curated or automated lists.

## Tags

Tags are lightweight labels used to categorize bookmarks across different topics. Each tag is represented by the `Tag` class in `app/models/tag.py` and includes visual attributes for UI rendering.

### Tag Attributes and Colors
Tags are defined with a name, an optional description, and a color from the `TagColor` enumeration. The available colors are:
- `RED`, `BLUE`, `GREEN`, `YELLOW`, `PURPLE`, `GRAY` (default)

The `Tag` model also tracks its own usage via the `usage_count` attribute, which is updated as bookmarks are associated with or removed from the tag.

### Tag Management and Validation
The `BookmarkService` in `app/services/bookmark_service.py` manages the lifecycle of tags. It enforces validation rules such as:
- **Name Length**: Tag names must be between 1 and 50 characters (enforced by `Tag.rename`).
- **Uniqueness**: Names are typically normalized (lowercased and stripped) for uniqueness checks.

When a tag is deleted via `BookmarkService.delete_tag`, the service ensures data integrity by scanning all bookmarks and stripping the deleted tag ID from their metadata before removing the tag from the repository.

```python
# From app/services/bookmark_service.py
def delete_tag(self, tag_id: str) -> bool:
    """Delete a tag and strip it from all bookmarks."""
    tag = self._repo.get_tag(tag_id)
    if not tag:
        return False
    # Clean up bookmarks using this tag
    for bookmark in self._repo.get_bookmarks_with_tag(tag_id):
        bookmark.remove_tag(tag_id)
        self._repo.save_bookmark(bookmark)
        self._cache.invalidate(bookmark.id)
    self._repo.delete_tag(tag_id)
    return True
```

## Collections

Collections, defined in `app/models/collection.py`, allow users to group bookmarks into named sets. Unlike tags, collections maintain an ordered list of bookmark IDs and can be pinned to the top of the user's sidebar.

### Manual Collections
Manual collections (`CollectionType.MANUAL`) are curated lists where bookmarks are explicitly added or removed. 
- **Adding**: Use `Collection.add_bookmark(bookmark_id)`. This method returns `False` if the bookmark is already present or if the collection is a Smart collection.
- **Reordering**: The `reorder(bookmark_ids)` method allows changing the display order of bookmarks. It requires the provided list of IDs to exactly match the existing set of IDs in the collection to prevent accidental data loss.

### Smart Collections
Smart collections (`CollectionType.SMART`) are automated groups defined by a `filter_rule`. Instead of manual membership, these collections use a keyword-based rule to identify matching bookmarks.

The core logic for smart filtering resides in the `_apply_filter` method:

```python
# From app/models/collection.py
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

Currently, smart collection filtering is limited to case-insensitive keyword matching within the bookmark's title and description.

## Service Integration

The `BookmarkService` acts as the central facade for all categorization operations, coordinating between the `BookmarkRepository` and the individual models.

### Creating a Collection
When creating a collection via the API, the service handles the initialization of the correct type based on the provided data:

```python
# From app/routes/collections.py
@collections_bp.route("/", methods=["POST"])
def create_collection():
    data = request.get_json(force=True)
    collection, error = _service.create_collection(data)
    if error:
        return jsonify({"error": error}), 400
    return jsonify(collection.to_dict()), 201
```

### Membership Operations
The service provides methods like `add_to_collection` and `remove_from_collection` which encapsulate the logic of retrieving the collection from the repository, performing the model-level update, and persisting the changes back to the repository.

```python
# From app/services/bookmark_service.py
def add_to_collection(self, collection_id: str, bookmark_id: str) -> bool:
    """Add a bookmark to a collection."""
    collection = self._repo.get_collection(collection_id)
    if not collection:
        return False
    if not collection.add_bookmark(bookmark_id):
        return False
    self._repo.save_collection(collection)
    return True
```

This architecture ensures that business rules—such as preventing manual additions to smart collections—are enforced consistently across the application.