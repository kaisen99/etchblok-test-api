---
title: Tagging and Metadata
description: How to use the Tag model to organize content, including color customization and usage tracking.
code_symbols: [SYM#e15c91e9e7eae95d052f50388a60d0bc30b3fe67, SYM#a903c58b7b9829413e7dde33ff94fc7516b965f1, SYM#8d687603253ce34b667ab707a05b20e9357dd6af]
section_id: d40f22ce-929d-4f33-aae3-4a28076f4ddf_tagging_and_metadata
doc_type: guide
section_type: guide
---
The tagging system in this project provides a flexible way to organize bookmarks using unique labels. Tags are managed as independent entities and associated with bookmarks via unique identifiers, allowing for efficient filtering and visual categorization.

## The Tag Model

The core of the tagging system is the `Tag` class defined in `app/models/tag.py`. It is a lightweight data structure that tracks metadata and usage statistics.

```python
class Tag:
    """A label that can be attached to one or more bookmarks."""

    name: str
    color: TagColor = TagColor.GRAY
    description: str = ""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    usage_count: int = 0
```

### Key Attributes
- **ID**: An 8-character hex string generated from a UUID. This is used to reference the tag within the `Bookmark` model.
- **Name**: The display name of the tag. It must be unique per user and is used for sorting.
- **Usage Count**: An integer tracking how many bookmarks are currently associated with this tag.
- **Color**: A `TagColor` enum value used for UI rendering.

## Visual Customization

To support visual organization, the `TagColor` enum in `app/models/tag.py` provides a set of preset colors.

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

When a tag is serialized via `to_dict()`, the color is exported as its string value (e.g., `"blue"`), making it easy for frontend consumers to apply CSS classes or styles based on the tag's intent.

## Validation and Constraints

The system enforces strict rules on tag names to ensure data integrity and prevent collisions with system-reserved keywords.

### Name Length and Format
The `rename()` method in the `Tag` class validates that names are not empty and do not exceed 50 characters:

```python
def rename(self, new_name: str) -> None:
    new_name = new_name.strip()
    if not new_name:
        raise ValueError("Tag name cannot be empty")
    if len(new_name) > 50:
        raise ValueError("Tag name cannot exceed 50 characters")
    self.name = new_name
```

### Reserved Names
Certain names are reserved for system use (typically for virtual folders or filters) and cannot be used as tag names. These are defined in `app/models/_validators.py`:
- `all`
- `untagged`
- `archived`
- `trash`

## Relationship with Bookmarks

Bookmarks do not store full `Tag` objects; instead, they maintain a list of tag IDs. This decoupling allows tags to be renamed or recolored without requiring updates to every associated bookmark.

In `app/models/bookmark.py`, the relationship is managed through the `tags` attribute and helper methods:

```python
@dataclass
class Bookmark:
    # ...
    tags: List[str] = field(default_factory=list)

    def add_tag(self, tag_id: str) -> bool:
        """Attach a tag. Returns False if already present."""
        if tag_id in self.tags:
            return False
        self.tags.append(tag_id)
        self._touch()
        return True
```

## Usage Tracking and Lifecycle

The `Tag` model includes methods to track how often it is used. This is useful for identifying popular tags or cleaning up unused ones.

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

> [!NOTE]
> In the current implementation, these methods must be called manually by the service layer (e.g., `BookmarkService`) when tags are added to or removed from bookmarks.

### Sorting
Tags are designed to be displayed alphabetically. The `Tag` class implements the `__lt__` dunder method to facilitate case-insensitive sorting:

```python
def __lt__(self, other: "Tag") -> bool:
    """Allow sorting tags alphabetically by name."""
    return self.name.lower() < other.name.lower()
```

This allows developers to simply call `sorted(list_of_tags)` to get a consistent, user-friendly order for UI presentation.
