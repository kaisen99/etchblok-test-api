---
title: Tagging and Metadata
description: Learn how to use tags to label bookmarks, including color customization and usage tracking.
code_symbols: [SYM#e15c91e9e7eae95d052f50388a60d0bc30b3fe67]
section_id: 13f1196f-730e-424a-a337-be193fb7c0cf_tagging_and_metadata
doc_type: guide
section_type: guide
---
In this system, tagging and metadata provide a flexible way to organize and extend bookmark data. Tags are global entities that can be shared across multiple bookmarks, while metadata allows for arbitrary key-value pairs to be attached to individual bookmarks.

## The Tag Model

Tags are represented by the `Tag` dataclass in `app/models/tag.py`. Each tag consists of a unique name, a color for UI categorization, and an optional description.

```python
@dataclass
class Tag:
    name: str
    color: TagColor = TagColor.GRAY
    description: str = ""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    usage_count: int = 0
```

### Color Customization
The `TagColor` enum defines a set of preset colors that can be assigned to tags to help with visual organization:

*   `RED`
*   `BLUE`
*   `GREEN`
*   `YELLOW`
*   `PURPLE`
*   `GRAY` (Default)

### Validation and Constraints
Tag names are subject to specific validation rules enforced in `app/models/_validators.py` via the `_validate_tag_name` function:

1.  **Length**: Tag names must be between 1 and 50 characters.
2.  **Reserved Names**: Certain names are reserved for system use and cannot be used as tag names: `all`, `untagged`, `archived`, and `trash`.
3.  **Uniqueness**: While the model doesn't enforce uniqueness internally, the `BookmarkService` typically manages tags as unique entities within the repository.

## Labeling Bookmarks

The `Bookmark` model in `app/models/bookmark.py` maintains a list of tag IDs rather than full tag objects. This decoupling allows tags to be managed independently of the bookmarks they label.

### Associating Tags
You can add or remove tags from a bookmark using the `add_tag` and `remove_tag` methods. These methods return a boolean indicating whether the operation resulted in a change.

```python
def add_tag(self, tag_id: str) -> bool:
    """Attach a tag. Returns False if already present."""
    if tag_id in self.tags:
        return False
    self.tags.append(tag_id)
    self._touch()
    return True
```

### Automatic Cleanup
When a tag is deleted via the `BookmarkService.delete_tag` method, the service automatically iterates through all bookmarks containing that tag ID and removes the reference. This ensures that bookmarks do not point to non-existent tags.

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

## Metadata for Extensibility

For data that does not fit into the standard bookmark fields (URL, title, description, tags), the `Bookmark` model includes a `metadata` field. This is a raw dictionary (`Dict[str, Any]`) that can store arbitrary key-value pairs.

```python
@dataclass
class Bookmark:
    # ... other fields ...
    metadata: Dict[str, Any] = field(default_factory=dict)
```

The system does not perform server-side validation on the contents of the `metadata` dictionary, making it an ideal place for client-specific data or experimental features.

## Usage Tracking

The `Tag` model includes a `usage_count` attribute and helper methods `increment_usage()` and `decrement_usage()`. 

> [!NOTE]
> In the current implementation of `BookmarkService`, these usage tracking methods are not automatically called when tags are added to or removed from bookmarks. The `usage_count` may require manual updates or a future service-level integration to accurately reflect the number of bookmarks using a specific tag.

## Sorting and Display
Tags implement the `__lt__` dunder method, which allows them to be sorted alphabetically by name (case-insensitive) when retrieved in lists:

```python
def __lt__(self, other: "Tag") -> bool:
    """Allow sorting tags alphabetically by name."""
    return self.name.lower() < other.name.lower()
```