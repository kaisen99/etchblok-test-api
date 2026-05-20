---
title: Tagging and Categorization
description: Covers the Tag model, including color-coding and usage tracking across the bookmark library.
code_symbols: [SYM#e15c91e9e7eae95d052f50388a60d0bc30b3fe67, SYM#a903c58b7b9829413e7dde33ff94fc7516b965f1, SYM#8d687603253ce34b667ab707a05b20e9357dd6af]
section_id: 953711f5-3d96-475c-a763-e4d3588d2c07_tagging_and_categorization
doc_type: guide
section_type: guide
---
The tagging system in this project provides a flexible way to organize bookmarks using color-coded labels. It is implemented through a combination of data models that define the tag structure and service-layer logic that enforces business rules and maintains referential integrity.

## Core Data Structures

The system centers around the `Tag` model and the `TagColor` enumeration, both located in `app/models/tag.py`.

### The Tag Model
The `Tag` class is a lightweight container for label metadata. It includes a unique identifier, a display name, and visual properties.

```python
class Tag:
    """A label that can be attached to one or more bookmarks."""
    name: str
    color: TagColor = TagColor.GRAY
    description: str = ""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    usage_count: int = 0
```

Key features of the `Tag` model include:
*   **Automatic ID Generation**: Tags are assigned an 8-character hex ID upon creation.
*   **Usage Tracking**: The `usage_count` attribute tracks how many bookmarks are associated with the tag. While the model provides `increment_usage()` and `decrement_usage()` methods, these are currently placeholders for manual tracking or future automation.
*   **Serialization**: The `to_dict()` and `from_dict()` methods facilitate JSON communication between the API and the persistence layer.

### Color Coding
The `TagColor` enum defines the visual palette available for tags. If no color is specified during creation, the system defaults to `GRAY`.

```python
class TagColor(Enum):
    """Preset colours available for tags."""
    RED = "red"
    BLUE = "blue"
    GREEN = "green"
    YELLOW = "yellow"
    PURPLE = "purple"
    GRAY = "gray"
```

## Validation and Constraints

Tag names are subject to strict validation rules defined in `app/models/_validators.py` and enforced by the `BookmarkService`.

### Name Restrictions
The `_validate_tag_name` function ensures that tag names meet the following criteria:
1.  **Non-Empty**: Tag names cannot be empty or consist only of whitespace.
2.  **Length Limit**: Names must be **50 characters or fewer**.
3.  **Reserved Names**: To prevent conflicts with system views, the following names are strictly prohibited:
    *   `all`
    *   `untagged`
    *   `archived`
    *   `trash`

### Normalization
The `Tag` model includes a `_normalize_name()` method that returns a lowercase, stripped version of the name. This is used internally to ensure uniqueness and consistent lookups regardless of casing.

## Lifecycle Management

The `BookmarkService` in `app/services/bookmark_service.py` acts as the orchestrator for tag operations, ensuring that changes to tags are reflected across the bookmark library.

### Creating and Updating Tags
When a tag is created or updated via `create_tag` or `update_tag`, the service invokes `_validate_tag_name` before persisting the changes to the repository.

```python
def update_tag(self, tag_id: str, data: Dict[str, Any]) -> Tuple[Optional[Tag], Optional[str]]:
    """Update a tag's name or colour."""
    tag = self._repo.get_tag(tag_id)
    if not tag:
        return None, None
    if "name" in data:
        err = _validate_tag_name(data["name"])
        if err:
            return None, err
        tag.rename(data["name"])
    if "color" in data:
        tag.color = TagColor(data["color"])
    self._repo.save_tag(tag)
    return tag, None
```

### Cascading Deletes
One of the most critical responsibilities of the `BookmarkService` is handling tag deletion. When a tag is deleted, the service performs a "cascade" operation to maintain integrity:
1.  It identifies all bookmarks currently using the tag via `self._repo.get_bookmarks_with_tag(tag_id)`.
2.  It removes the tag ID from each bookmark's `tags` list.
3.  It invalidates the cache for each affected bookmark.
4.  Finally, it removes the tag record from the repository.

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

## Integration with Bookmarks

Bookmarks store tags as a list of string IDs in the `Bookmark.tags` field (defined in `app/models/bookmark.py`). The `Bookmark` class provides helper methods `add_tag(tag_id)` and `remove_tag(tag_id)` which handle the logic of adding/removing IDs and updating the `updated_at` timestamp via the internal `_touch()` method.

This ID-based relationship allows tags to be renamed or recolored without requiring updates to every associated bookmark, as the bookmarks only reference the immutable tag ID.