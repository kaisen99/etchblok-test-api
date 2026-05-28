---
title: Tag Usage Tracking
description: How the system maintains usage counts and ensures tag uniqueness through normalization and increment/decrement methods.
code_symbols: [SYM#e15c91e9e7eae95d052f50388a60d0bc30b3fe67, SYM#a903c58b7b9829413e7dde33ff94fc7516b965f1]
section_id: d08ecffc-382c-480f-82a7-a9c57abb7399_tag_usage_tracking
doc_type: guide
section_type: guide
---
The system manages tags as independent entities that can be associated with multiple bookmarks. Central to this management is the `Tag` model, which provides built-in mechanisms for tracking how many bookmarks reference a specific tag and ensuring tag names remain consistent and valid.

## The Tag Model

The `Tag` class, defined in `app/models/tag.py`, is the primary entity for categorization. It tracks metadata such as a display name, a visual color (via the `TagColor` enum), and a `usage_count`.

```python
class Tag:
    name: str
    color: TagColor = TagColor.GRAY
    description: str = ""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    usage_count: int = 0
```

### Usage Tracking Methods

The `Tag` model provides two explicit methods for managing its lifecycle relative to bookmarks:

*   `increment_usage()`: Increases the `usage_count` by 1.
*   `decrement_usage()`: Decreases the `usage_count` by 1, ensuring the count never drops below zero.

These methods return the new count, allowing for immediate feedback during operations.

```python
def increment_usage(self) -> int:
    """Record that a bookmark now uses this tag. Returns new count."""
    self.usage_count += 1
    return self.usage_count

def decrement_usage(self) -> int:
    """Record that a bookmark removed this tag. Returns new count."""
    self.usage_count = max(0, self.usage_count - 1)
    return self.usage_count
```

## Normalization and Validation

To ensure uniqueness and prevent collisions with system-level views, the system employs both internal normalization and external validation.

### Name Normalization
The `Tag` class includes a `_normalize_name()` method. This is used to create a consistent version of the tag name for comparison by stripping whitespace and converting the string to lowercase.

```python
def _normalize_name(self) -> str:
    """Return a lowered, stripped version for uniqueness checks."""
    return self.name.strip().lower()
```

### Validation Rules
Before a tag is persisted via the `BookmarkService`, its name is validated using the `_validate_tag_name` helper found in `app/models/_validators.py`. This function enforces several constraints:

1.  **Non-empty**: Names cannot be empty or just whitespace.
2.  **Length**: Names are limited to a maximum of 50 characters.
3.  **Reserved Keywords**: Names cannot match system-reserved keywords used for filtering, such as `all`, `untagged`, `archived`, or `trash`.

```python
_RESERVED_TAG_NAMES = frozenset({"all", "untagged", "archived", "trash"})

def _validate_tag_name(name: str) -> Optional[str]:
    normalized = name.strip().lower()
    if not normalized:
        return "Tag name is required"
    if normalized in _RESERVED_TAG_NAMES:
        return f"'{name}' is a reserved tag name"
    if len(normalized) > 50:
        return "Tag name must be 50 characters or fewer"
    return None
```

## Implementation Considerations

While the `Tag` model provides the infrastructure for usage tracking, the current implementation in `app/models/bookmark.py` and `app/services/bookmark_service.py` requires manual orchestration to keep these counts accurate.

### Bookmark Association
The `Bookmark` model stores associations as a list of string IDs (`tags: List[str]`). When a tag is added or removed from a bookmark using `Bookmark.add_tag(tag_id)` or `Bookmark.remove_tag(tag_id)`, the `Bookmark` instance does not have access to the `Tag` object itself and therefore cannot call `increment_usage()` or `decrement_usage()`.

### Service Layer Responsibility
In the current architecture, the `BookmarkService` is responsible for coordinating these updates. For example, when a tag is deleted, the service iterates through bookmarks to remove the reference, but it does not currently decrement the usage count of other tags or automatically update the count when a bookmark is created.

Developers interacting with the `Tag` model should be aware that `usage_count` reflects the state of the `Tag` object in memory or the database, and must be explicitly updated when the relationship between a bookmark and a tag changes.
