---
title: Categorization with Tags
description: Explains the Tag model, including how to manage display names, usage counts, and visual color assignments.
code_symbols: [SYM#e15c91e9e7eae95d052f50388a60d0bc30b3fe67, SYM#8d687603253ce34b667ab707a05b20e9357dd6af, SYM#a903c58b7b9829413e7dde33ff94fc7516b965f1]
section_id: c0701eba-2c61-4e71-934a-9f49e5a7da7d_categorization_with_tags
doc_type: guide
section_type: guide
---
In this system, tags serve as the primary mechanism for organizing bookmarks. The implementation focuses on providing a flexible labeling system with built-in usage tracking and visual customization.

## The Tag Model

The core of the categorization system is the `Tag` class located in `app/models/tag.py`. Each tag is a unique entity that can be associated with multiple bookmarks.

```python
class Tag:
    name: str
    color: TagColor = TagColor.GRAY
    description: str = ""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    usage_count: int = 0
```

### Key Attributes
- **Identity**: Every tag is assigned a unique 8-character hexadecimal ID generated via `uuid.uuid4().hex[:8]`.
- **Naming**: Tags have a display name which is used for sorting and identification. The `__lt__` dunder method allows tags to be sorted alphabetically by name (case-insensitive).
- **Usage Tracking**: The `usage_count` attribute tracks how many bookmarks are currently associated with the tag. This is managed through `increment_usage()` and `decrement_usage()` methods.

## Visual Categorization

To aid in UI rendering and visual distinction, the system provides a set of preset colors via the `TagColor` enum.

```python
class TagColor(Enum):
    RED = "red"
    BLUE = "blue"
    GREEN = "green"
    YELLOW = "yellow"
    PURPLE = "purple"
    GRAY = "gray"
```

When a tag is created without a specified color, it defaults to `TagColor.GRAY`. These colors are serialized as their string values (e.g., `"red"`) when converted to a dictionary for API responses.

## Tag Lifecycle and Validation

Tags are typically managed through the `BookmarkService` in `app/services/bookmark_service.py`, which ensures that all business rules and validations are applied before persistence.

### Validation Rules
The system enforces several constraints on tag names via the `rename()` method and the internal `_validate_tag_name` helper:

1.  **Length**: Tag names must be between 1 and 50 characters.
2.  **Reserved Names**: Certain names are reserved for system use and cannot be assigned to user-created tags. These include:
    *   `all`
    *   `untagged`
    *   `archived`
    *   `trash`
3.  **Normalization**: The `_normalize_name()` method provides a stripped, lowercase version of the name, which is used for uniqueness checks and validation.

### Usage Management
The `usage_count` is not updated by the `Tag` class itself but is triggered by the service layer when bookmarks are modified.

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

The `decrement_usage` method includes a safety check using `max(0, ...)` to ensure the count never becomes negative, maintaining data integrity even if synchronization issues occur.

## Serialization

The `Tag` class provides standard methods for converting to and from dictionary formats, facilitating easy integration with the database and API layers.

-   **`to_dict()`**: Serializes the tag into a JSON-safe dictionary, converting the `TagColor` enum to its underlying string value.
-   **`from_dict()`**: A class method that reconstructs a `Tag` instance from a dictionary. It safely handles the conversion of color strings back into `TagColor` enum members, defaulting to `GRAY` if the color is missing.

```python
# Example of tag serialization
tag = Tag(name="Research", color=TagColor.BLUE)
data = tag.to_dict()
# Result: {'id': '...', 'name': 'Research', 'color': 'blue', 'description': '', 'usage_count': 0}
```
