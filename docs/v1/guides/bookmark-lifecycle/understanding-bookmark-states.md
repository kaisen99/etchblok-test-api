---
title: Understanding Bookmark States
description: An overview of the BookmarkStatus enumeration and how it defines the visibility and lifecycle phase of a bookmark within the system.
code_symbols: [SYM#d731bc2f45cac29b2961ab00083bab5345db0a5e, SYM#d570461c1ff2b0eb81e078e185a46de87938f933, SYM#6d5b77b3f04288620db996a9bc18b13d3bd1ad3b]
section_id: 6c23e46d-745d-4a82-9f3f-ccd130ff1d19_understanding_bookmark_states
doc_type: guide
section_type: guide
---
In this system, bookmarks are managed through a defined lifecycle that determines their visibility and availability. This lifecycle is governed by the `BookmarkStatus` enumeration and implemented within the `Bookmark` domain model.

## The BookmarkStatus Enumeration

The `BookmarkStatus` enum, located in `app/models/bookmark.py`, defines three distinct states for a bookmark:

```python
class BookmarkStatus(Enum):
    """Visibility status of a bookmark."""

    ACTIVE = "active"
    ARCHIVED = "archived"
    TRASHED = "trashed"
```

*   **ACTIVE**: The default state for new bookmarks. These are visible in standard listings and search results.
*   **ARCHIVED**: Used for bookmarks that the user wants to keep but remove from the primary view.
*   **TRASHED**: A "soft-deleted" state. Bookmarks in this state are typically hidden from the user but remain in the database for potential restoration.

## Managing State Transitions

The `Bookmark` class provides explicit methods to transition between these states. Every state transition automatically updates the `updated_at` timestamp via the internal `_touch()` helper.

### Archiving and Restoring
To move a bookmark out of the active view or bring it back, the `archive()` and `restore()` methods are used:

```python
# app/models/bookmark.py

def archive(self) -> None:
    """Move the bookmark to the archive."""
    self.status = BookmarkStatus.ARCHIVED
    self._touch()

def restore(self) -> None:
    """Restore a trashed or archived bookmark to active status."""
    self.status = BookmarkStatus.ACTIVE
    self._touch()
```

### Soft Deletion (Trashing)
The system implements a soft-delete pattern. Instead of immediately removing a record from storage, the `trash()` method marks it as trashed:

```python
# app/models/bookmark.py

def trash(self) -> None:
    """Soft-delete the bookmark by moving it to the trash."""
    self.status = BookmarkStatus.TRASHED
    self._touch()
```

## Visibility and Filtering

The `BookmarkRepository` in `app/db/repository.py` uses these statuses to filter results when listing bookmarks. The `list_bookmarks` method accepts an optional `status` string, which it attempts to convert into a `BookmarkStatus` member.

```python
# app/db/repository.py

def list_bookmarks(
    self,
    page: int = 1,
    per_page: int = 25,
    status: Optional[str] = None,
) -> Tuple[List[Bookmark], int]:
    items = list(self._bookmarks.values())
    if status:
        try:
            target = BookmarkStatus(status)
            items = [b for b in items if b.status == target]
        except ValueError:
            # If an invalid status string is provided, the filter is ignored
            pass
    # ... pagination and sorting logic ...
```

## Soft vs. Hard Deletion

It is important to distinguish between the "delete" operations at different layers of the application:

1.  **Service Layer (Soft-Delete)**: The `BookmarkService.delete_bookmark` method performs a soft-delete by calling `bookmark.trash()`. This preserves the data in the repository.
2.  **Repository Layer (Hard-Delete)**: The `BookmarkRepository.delete_bookmark` method performs a hard-delete by removing the bookmark from the internal storage dictionary (`self._bookmarks.pop(bookmark_id)`).

In standard API usage, the service layer's soft-delete is preferred to allow for the `restore()` functionality.

## Serialization and Persistence

When a bookmark is serialized for a JSON response via `to_dict()`, the status is converted to its string value:

```python
# app/models/bookmark.py

def to_dict(self) -> Dict[str, Any]:
    return {
        "id": self.id,
        "url": self.url,
        "status": self.status.value,  # Serializes to "active", "archived", or "trashed"
        # ... other fields ...
    }
```

Conversely, the `from_dict()` class method does **not** accept a status. New bookmarks created via `from_dict()` always default to `BookmarkStatus.ACTIVE`, ensuring that the lifecycle always begins from a consistent starting point.