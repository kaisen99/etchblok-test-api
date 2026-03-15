---
title: Tagging and Metadata
description: How to use the Tag model to label bookmarks, including color coding and usage tracking.
code_symbols: [SYM#e15c91e9e7eae95d052f50388a60d0bc30b3fe67, SYM#8d687603253ce34b667ab707a05b20e9357dd6af, SYM#a903c58b7b9829413e7dde33ff94fc7516b965f1]
section_id: a942ce5e-b6e6-4d12-9ebb-728c24bd6f97_tagging_and_metadata
doc_type: guide
section_type: guide
---
The tagging system in this project provides a flexible way to categorize and organize bookmarks. It is built around the `Tag` model and the `TagColor` enumeration, managed primarily through the `BookmarkService`.

## Core Entities

### The Tag Model
The `Tag` class (found in `app/models/tag.py`) represents a label that can be attached to bookmarks. Each tag is uniquely identified by an 8-character hex ID and includes metadata for display and organization.

```python
class Tag:
    name: str
    color: TagColor = TagColor.GRAY
    description: str = ""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    usage_count: int = 0
```

Key features of the `Tag` model include:
- **Normalization**: The `_normalize_name()` method ensures names are compared consistently by stripping whitespace and converting to lowercase.
- **Sorting**: Tags implement the `__lt__` dunder method, allowing them to be sorted alphabetically by name (case-insensitive).
- **Serialization**: The `to_dict()` and `from_dict()` methods handle conversion for JSON API responses and persistence.

### Color Coding
Visual categorization is supported through the `TagColor` enum. When creating or updating a tag, you can assign one of the following preset colors:

```python
class TagColor(Enum):
    RED = "red"
    BLUE = "blue"
    GREEN = "green"
    YELLOW = "yellow"
    PURPLE = "purple"
    GRAY = "gray"
```

## Tag Lifecycle and Validation

Tags are managed via the `BookmarkService` in `app/services/bookmark_service.py`. This service enforces business rules and ensures data integrity across the system.

### Validation Rules
Before a tag is created or renamed, it must pass validation checks defined in `app/models/_validators.py`. The `_validate_tag_name` function enforces the following:
1.  **Length**: Tag names must be between 1 and 50 characters.
2.  **Reserved Names**: Certain names used for system filters are prohibited. These include: `all`, `untagged`, `archived`, and `trash`.
3.  **Uniqueness**: While the model doesn't enforce uniqueness internally, the service layer typically checks for existing tags before creation.

### Creation and Updates
The `BookmarkService` provides methods to handle tag data safely:

```python
# Creating a tag via the service
tag_data = {
    "name": "Research", 
    "color": "blue", 
    "description": "Academic papers"
}
tag, error = service.create_tag(tag_data)

# Updating an existing tag
update_data = {"color": "red", "name": "Urgent"}
updated_tag, error = service.update_tag(tag_id, update_data)
```

## Integration with Bookmarks

Bookmarks and tags are linked through a many-to-many relationship, implemented by storing a list of tag IDs on the `Bookmark` model.

### Association
The `Bookmark` class (in `app/models/bookmark.py`) manages its own tag associations using `add_tag(tag_id)` and `remove_tag(tag_id)`. These methods return a boolean indicating if the operation resulted in a change.

```python
def add_tag(self, tag_id: str) -> bool:
    """Attach a tag. Returns False if already present."""
    if tag_id in self.tags:
        return False
    self.tags.append(tag_id)
    self._touch()
    return True
```

### Cascade Deletion
A critical feature of the `BookmarkService` is the handling of tag deletions. When `delete_tag(tag_id)` is called, the service performs a "cascade removal" by iterating through every bookmark that uses that tag and stripping the ID from their metadata.

```python
def delete_tag(self, tag_id: str) -> bool:
    # ... find tag ...
    for bookmark in self._repo.get_bookmarks_with_tag(tag_id):
        bookmark.remove_tag(tag_id)
        self._repo.save_bookmark(bookmark)
    self._repo.delete_tag(tag_id)
    return True
```

## Arbitrary Metadata
Beyond structured tags, the `Bookmark` model includes a `metadata` field, which is a dictionary (`Dict[str, Any]`) intended for extensibility. This allows for storing arbitrary key-value pairs that don't fit into the standard schema, such as external IDs or custom flags.

## Implementation Details and Gotchas

### Usage Tracking
The `Tag` model includes `increment_usage()` and `decrement_usage()` methods and a `usage_count` attribute. However, in the current implementation of `BookmarkService`, these methods are **not** automatically called when tags are added to or removed from bookmarks. Consequently, the `usage_count` may not accurately reflect the number of bookmarks associated with a tag.

### Persistence
Tags are persisted via the `BookmarkRepository`. The repository provides methods like `list_tags()`, `get_tag(tag_id)`, and `save_tag(tag)` to interact with the underlying data store. When a tag is updated in the service, it must be explicitly saved back to the repository to persist changes.

### API Exposure
The tagging system is exposed via the `tags_bp` Blueprint in `app/routes/tags.py`. This API layer leverages the `to_dict()` method for serialization and ensures that the list of tags returned to the client is sorted alphabetically:

```python
@tags_bp.route("/", methods=["GET"])
def list_tags():
    """List all tags, sorted alphabetically."""
    tags = _service.list_tags()
    return jsonify({"tags": [t.to_dict() for t in sorted(tags)]})
```