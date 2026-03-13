---
title: Domain Models
description: Core entities representing the system's data structures, including bookmarks, tags, and collections.
code_symbols: [SYM#d731bc2f45cac29b2961ab00083bab5345db0a5e, SYM#e15c91e9e7eae95d052f50388a60d0bc30b3fe67, SYM#97d8a6cbf0c47108aa2beb39fafa695229654067]
section_id: 46bb54a6-341f-46da-abb4-746d60e6a8f2_domain_models
doc_type: explanation
section_type: guide
---
The domain models in this project serve as the foundational building blocks for the Etchblok API, defining the structure and behavior of bookmarks, tags, and collections. By utilizing Python's `dataclasses`, the implementation ensures that these core entities are both lightweight and expressive, encapsulating both data and the immediate logic required to maintain internal consistency.

## Core Entities and Lifecycle

The system revolves around three primary entities, each with a distinct role and a specific identification strategy using truncated UUIDs to balance uniqueness with readability.

### Bookmark
The `Bookmark` class (found in `app/models/bookmark.py`) is the central entity. It tracks a URL along with user-provided metadata and system-managed state.

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

A key design choice in the `Bookmark` model is the management of its lifecycle through the `BookmarkStatus` enum (`ACTIVE`, `ARCHIVED`, `TRASHED`). Instead of hard-deleting records, the model provides `archive()`, `trash()`, and `restore()` methods. These methods update the `status` and trigger an internal `_touch()` helper to refresh the `updated_at` timestamp, ensuring the audit trail remains accurate.

### Tag
The `Tag` model (`app/models/tag.py`) provides a flat organizational structure. Unlike bookmarks, tags use an 8-character ID and include a `usage_count` to track how many bookmarks reference them. This count is managed via `increment_usage()` and `decrement_usage()` methods. The model also supports visual customization through the `TagColor` enum, which includes presets like `RED`, `BLUE`, `GREEN`, `YELLOW`, `PURPLE`, and `GRAY`.

### Collection
The `Collection` model (`app/models/collection.py`) introduces a grouping mechanism with a 10-character ID. It supports two distinct modes defined by `CollectionType`:
- **MANUAL**: Users explicitly add or remove bookmark IDs via `add_bookmark()` and `remove_bookmark()`.
- **SMART**: Bookmarks are dynamically associated based on a `filter_rule`.

## Serialization and Instantiation Patterns

The codebase enforces a strict separation between the internal model state and external data representations (like JSON). Every model implements a pair of methods for this purpose:

1.  **`to_dict()`**: Serializes the entity into a JSON-safe dictionary. This is used extensively in the route handlers (e.g., `app/routes/bookmarks.py`) to prepare API responses.
2.  **`from_dict()`**: A class method used to instantiate models from incoming request data.

A significant constraint is visible in the `Bookmark.from_dict` implementation:

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

By only mapping a subset of fields, the model prevents clients from manually setting system-controlled attributes like `id`, `status`, or `created_at` during the creation process. This ensures that the `id` is always generated using the `uuid4().hex[:12]` logic defined in the dataclass field factory.

## Logic and Constraints

The models are not just data containers; they enforce business rules and maintain integrity:

*   **Smart Collection Integrity**: In `Collection.add_bookmark`, the model returns `False` if the collection is of type `SMART`. This prevents manual overrides from corrupting the rule-based nature of smart collections.
*   **Reordering Constraints**: The `Collection.reorder(bookmark_ids)` method validates that the new list of IDs is a perfect permutation of the existing list. If the sets do not match exactly, it raises a `ValueError`, preventing accidental loss of bookmark references.
*   **Tag Validation**: The `Tag.rename()` method enforces a 50-character limit and prevents empty names. Additional validation for reserved names (like `all`, `untagged`, `archived`, `trash`) is handled in the service layer using constants defined in `app/models/_validators.py`.

## Design Tradeoffs

### Identification Strategy
The use of truncated hex UUIDs is a specific tradeoff. While it significantly improves the aesthetics of the API URLs and reduces payload size, it theoretically increases the risk of collisions compared to full 32-character UUIDs. For the scale of this application, the 12-character (Bookmark) and 8-character (Tag) IDs provide a collision space that is considered acceptable.

### Logic Placement
The project follows a pattern where "internal" state logic lives in the model, while "cross-entity" logic lives in the service layer. For example:
*   **Model Logic**: `Collection._apply_filter` encapsulates how a smart collection identifies matching bookmarks based on its `filter_rule`.
*   **Service Logic**: `BookmarkService` handles the complexity of removing a Tag ID from all associated Bookmarks when a Tag is deleted, as this requires coordination across multiple entities and the repository.

### Validation Layers
Validation is split between the models and the service layer. While models like `Tag` perform basic length checks, more complex validation (like URL format or reserved name checks) is deferred to the service layer. This keeps the models focused on data structure while the services handle the business policy. For instance, `Bookmark` contains a name-mangled `__validate_url` method, but the primary URL validation is executed in `app/services/bookmark_service.py` before the model is even instantiated.