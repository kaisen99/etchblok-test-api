---
title: Domain Models
description: Core entities representing bookmarks, tags, and collections, including their metadata and state transitions.
code_symbols: [SYM#d731bc2f45cac29b2961ab00083bab5345db0a5e, SYM#97d8a6cbf0c47108aa2beb39fafa695229654067, SYM#e15c91e9e7eae95d052f50388a60d0bc30b3fe67]
section_id: 2b89a92c-4d1a-40b2-bf76-dc070458998f_domain_models
doc_type: explanation
section_type: guide
---
The domain models in this project serve as the core source of truth for the application's business logic. Implemented using Python's `dataclasses`, these entities encapsulate both the state and the fundamental behaviors of bookmarks, tags, and collections.

## The Bookmark Entity

The `Bookmark` class in `app/models/bookmark.py` is the central entity of the system. It represents a saved URL along with its associated metadata and organizational state.

### Lifecycle and State Transitions
A bookmark's visibility is managed through the `BookmarkStatus` enum, which defines three states: `ACTIVE`, `ARCHIVED`, and `TRASHED`. The model provides explicit methods to transition between these states, ensuring that the `updated_at` timestamp is always synchronized via the internal `_touch()` helper.

```python
def archive(self) -> None:
    """Move the bookmark to the archive."""
    self.status = BookmarkStatus.ARCHIVED
    self._touch()

def trash(self) -> None:
    """Soft-delete the bookmark by moving it to the trash."""
    self.status = BookmarkStatus.TRASHED
    self._touch()
```

### Identity and Metadata
Bookmarks use a unique 12-character hex string for their ID, generated upon instantiation. They also support an extensible `metadata` dictionary for storing arbitrary key/value pairs, allowing the model to adapt to different types of content without schema changes.

## Tags and Organization

The `Tag` model in `app/models/tag.py` provides a flexible labeling system. Unlike bookmarks, tags are lightweight entities focused on categorization and UI presentation.

### Usage Tracking
Tags maintain a `usage_count` to track how many bookmarks are currently associated with them. This count is updated via `increment_usage()` and `decrement_usage()` methods, which are typically orchestrated by the service layer when tags are added to or removed from bookmarks.

### Visual Representation
The `TagColor` enum provides a set of predefined colors (`RED`, `BLUE`, `GREEN`, `YELLOW`, `PURPLE`, `GRAY`) used for UI rendering. By default, new tags are assigned `TagColor.GRAY`.

```python
@dataclass
class Tag:
    name: str
    color: TagColor = TagColor.GRAY
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    usage_count: int = 0
```

## Collections: Manual vs. Smart

Collections, defined in `app/models/collection.py`, allow for higher-level grouping of bookmarks. The system distinguishes between two types of collections via the `CollectionType` enum.

### Manual Collections
In a `MANUAL` collection, users explicitly add or remove bookmark IDs. The model supports custom ordering through the `reorder()` method, which validates that the new list of IDs matches the existing set to prevent data loss.

### Smart Collections
`SMART` collections are dynamic. They use a `filter_rule` (a simple keyword string) to automatically include bookmarks. The `_apply_filter()` method implements this logic by checking for the keyword within bookmark titles and descriptions:

```python
def _apply_filter(self, bookmarks: list) -> List[str]:
    if not self.filter_rule:
        return []
    keyword = self.filter_rule.lower()
    return [b.id for b in bookmarks if keyword in b.title.lower() or keyword in b.description.lower()]
```

Note that `add_bookmark()` will return `False` if called on a smart collection, as their membership is governed strictly by the filter rule.

## Data Integrity and Validation

The project maintains data integrity through a combination of model-level methods and internal validation helpers in `app/models/_validators.py`.

### Validation Constraints
- **Reserved Names**: Certain tag names like `all`, `untagged`, `archived`, and `trash` are reserved and cannot be used for user-created tags.
- **Length Limits**: Titles are capped at 256 characters (`_MAX_TITLE_LENGTH`), descriptions at 2048 (`_MAX_DESCRIPTION_LENGTH`), and tag names at 50 characters.
- **URL Format**: A regex-based validator ensures that bookmarks contain valid `http` or `https` URLs.

### Serialization
Every domain model implements `to_dict()` and `from_dict()` methods. This pattern ensures a clean separation between the internal domain representation and the external JSON format used by the API routes. The `from_dict()` methods are designed to be resilient, often providing default values for optional fields like descriptions or tags.

```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> "Bookmark":
    return cls(
        url=data["url"],
        title=data["title"],
        description=data.get("description", ""),
        tags=data.get("tags", []),
    )
```
