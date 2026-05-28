---
title: The Bookmark Entity
description: An overview of the core Bookmark model, covering its lifecycle states, metadata storage, and the BookmarkStatus enumeration.
code_symbols: [SYM#d731bc2f45cac29b2961ab00083bab5345db0a5e, SYM#d570461c1ff2b0eb81e078e185a46de87938f933, SYM#6d5b77b3f04288620db996a9bc18b13d3bd1ad3b]
section_id: 88afc0d8-36cf-4a86-9adb-5a8346de9adc_the_bookmark_entity
doc_type: guide
section_type: guide
---
The `Bookmark` entity is the central domain model of the application, representing a saved URL along with its associated metadata, organizational tags, and lifecycle state. Defined in `app/models/bookmark.py`, it is implemented as a Python dataclass that encapsulates both the data and the state transition logic for bookmarks.

## Lifecycle States and Visibility

The visibility and organizational state of a bookmark are managed through the `BookmarkStatus` enumeration. This allows the system to support features like archiving and soft-deletion (trashing) without immediately removing records from the underlying storage.

```python
class BookmarkStatus(Enum):
    """Visibility status of a bookmark."""
    ACTIVE = "active"
    ARCHIVED = "archived"
    TRASHED = "trashed"
```

The `Bookmark` class provides explicit methods to transition between these states. Each transition method automatically updates the `updated_at` timestamp via an internal `_touch()` helper.

*   **`archive()`**: Sets the status to `ARCHIVED`. Used for bookmarks the user wants to keep but hide from the primary active list.
*   **`trash()`**: Sets the status to `TRASHED`. This acts as a soft-delete mechanism.
*   **`restore()`**: Reverts the status to `ACTIVE`, effectively "un-trashing" or "un-archiving" the entity.

These transitions are typically orchestrated by the `BookmarkService` in `app/services/bookmark_service.py`, which ensures the changes are persisted to the repository and the search index is updated.

## Core Attributes and Extensibility

A `Bookmark` instance tracks several key pieces of information:

| Attribute | Type | Description |
| :--- | :--- | :--- |
| `id` | `str` | A unique 12-character hex identifier generated via `uuid.uuid4().hex[:12]`. |
| `url` | `str` | The bookmarked web address. |
| `title` | `str` | A human-readable title for the bookmark. |
| `tags` | `List[str]` | A list of `Tag` IDs associated with this bookmark. |
| `metadata` | `Dict[str, Any]` | A flexible dictionary for storing arbitrary key/value pairs, allowing for future extensibility without schema changes. |

### Tag Management
Tags are managed through the `add_tag(tag_id)` and `remove_tag(tag_id)` methods. These methods return a boolean indicating whether the operation resulted in a change (e.g., `add_tag` returns `False` if the tag was already present), which helps the service layer decide if a repository save is necessary.

## Serialization and Construction

The `Bookmark` model provides two primary methods for converting between the domain object and plain Python dictionaries, which is essential for JSON API interactions.

### Construction with `from_dict`
The `from_dict` class method is the standard way to instantiate a bookmark from user input (e.g., a JSON request body). It focuses on the core user-provided fields:

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

Note that `from_dict` does not accept an `id` or `status`. These are automatically initialized to a new UUID and `BookmarkStatus.ACTIVE` respectively by the dataclass defaults.

### Serialization with `to_dict`
The `to_dict` method prepares the entity for JSON responses, converting complex types like `datetime` and `Enum` into strings:

```python
def to_dict(self) -> Dict[str, Any]:
    return {
        "id": self.id,
        "url": self.url,
        "title": self.title,
        "description": self.description,
        "tags": self.tags,
        "status": self.status.value,
        "created_at": self.created_at.isoformat(),
        "updated_at": self.updated_at.isoformat(),
        "metadata": self.metadata,
    }
```

## Integration in the Service Layer

While the `Bookmark` class handles its own internal state, the `BookmarkService` in `app/services/bookmark_service.py` manages its lifecycle within the broader system. For example, when a bookmark is updated, the service layer is responsible for:

1.  Validating the new data (using `app.models._validators`).
2.  Updating the `Bookmark` instance.
3.  Calling `_touch()` to refresh the modification timestamp.
4.  Persisting the change via `BookmarkRepository`.
5.  Invalidating the cache and updating the search index.

This separation ensures that the `Bookmark` entity remains a pure domain model focused on data integrity and state transitions, while the service layer handles side effects and infrastructure concerns.
