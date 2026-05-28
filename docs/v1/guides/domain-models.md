---
title: Domain Models
description: Core data structures representing bookmarks, tags, and collections, including their metadata and serialization logic.
code_symbols: [SYM#d731bc2f45cac29b2961ab00083bab5345db0a5e, SYM#e15c91e9e7eae95d052f50388a60d0bc30b3fe67, SYM#97d8a6cbf0c47108aa2beb39fafa695229654067]
section_id: e48ba199-e683-4177-a1e6-a09f64b8fb0a_domain_models
doc_type: explanation
section_type: guide
---
The domain models in this project serve as the central source of truth for data structures and business logic. Implemented primarily using Python's `dataclasses`, these models encapsulate the state and behavior of bookmarks, tags, and collections while providing consistent serialization patterns for the API layer.

## Core Entities and Dataclasses

The project utilizes `dataclasses` to define its primary entities. This choice provides a concise syntax for defining data-heavy objects while automatically generating standard methods like `__init__` and `__repr__`.

### The Bookmark Entity
The `Bookmark` class in `app/models/bookmark.py` is the most complex entity. It manages not only the URL and metadata but also the lifecycle state of the saved content.

```python
@dataclass
class Bookmark:
    url: str
    title: str
    description: str = ""
    tags: List[str] = field(default_factory=list)
    status: BookmarkStatus = BookmarkStatus.ACTIVE
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
```

The model includes explicit state transition methods that ensure the `updated_at` timestamp is refreshed via an internal `_touch()` helper whenever the status changes:

*   `archive()`: Sets status to `BookmarkStatus.ARCHIVED`.
*   `trash()`: Sets status to `BookmarkStatus.TRASHED` (soft-delete).
*   `restore()`: Returns the bookmark to `BookmarkStatus.ACTIVE`.

### Tag Management
The `Tag` model in `app/models/tag.py` handles categorization. Unlike bookmarks, tags maintain a `usage_count` to track how many bookmarks are associated with them. This count is managed through `increment_usage()` and `decrement_usage()` methods, which are typically called by the service layer during bookmark updates.

Tags also include a `TagColor` enum to support UI-level customization and a `_normalize_name()` method to facilitate uniqueness checks by stripping whitespace and casing.

## Collections: Manual vs. Smart

The `Collection` model in `app/models/collection.py` supports two distinct organizational strategies defined by the `CollectionType` enum:

1.  **Manual Collections**: Users explicitly add or remove bookmark IDs using `add_bookmark()` and `remove_bookmark()`. These collections support custom ordering via the `reorder()` method, which validates that the new list of IDs exactly matches the existing set.
2.  **Smart Collections**: These are dynamic groups defined by a `filter_rule`. They do not allow manual addition of bookmarks (the `add_bookmark` method returns `False` for smart collections).

The logic for smart collections is encapsulated in the `_apply_filter` method:

```python
def _apply_filter(self, bookmarks: list) -> List[str]:
    if not self.filter_rule:
        return []
    keyword = self.filter_rule.lower()
    return [b.id for b in bookmarks if keyword in b.title.lower() or keyword in b.description.lower()]
```

This implementation uses a naive case-insensitive substring match against the bookmark's title and description to determine membership.

## Serialization and Data Integrity

The models implement a consistent interface for moving data between the application and external interfaces (like the database or API).

### Serialization Logic
Each model provides a `to_dict()` method for JSON serialization and a `from_dict()` class method for instantiation from request payloads. 

A notable design choice in `Bookmark.from_dict` is its restrictiveness: it only accepts `url`, `title`, `description`, and `tags`. Internal fields like `id`, `status`, and timestamps are intentionally omitted from this method to prevent clients from overriding system-generated metadata during creation.

### Validation Constraints
The `app/models/_validators.py` module provides internal helpers that enforce business rules across the models. These include:

*   **URL Validation**: A regex-based check in `_validate_url` ensuring proper protocol and format.
*   **Reserved Names**: The `_RESERVED_TAG_NAMES` constant prevents users from creating tags named "all", "untagged", "archived", or "trash", as these names are reserved for system-level filtering.
*   **Length Limits**: Titles are capped at 256 characters, and descriptions at 2048 characters.

## Implementation Tradeoffs

Several design decisions in the domain models reflect specific tradeoffs:

*   **Truncated Identifiers**: The project uses truncated UUIDs for IDs (e.g., `uuid.uuid4().hex[:12]` for bookmarks and `[:8]` for tags). While this results in shorter, more user-friendly URLs and identifiers, it increases the theoretical risk of collisions compared to full 128-bit UUIDs.
*   **Naive Filtering**: The smart collection filtering logic is limited to basic substring matching. It does not support complex boolean logic (AND/OR) or tag-based filtering within the `filter_rule` itself.
*   **In-Memory State**: The `usage_count` on the `Tag` model is a cached value. If the database and the model instances fall out of sync, the `usage_count` may reflect inaccurate data until a full recount is performed.
