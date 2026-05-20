---
title: Bookmark Lifecycle and States
description: Explains the core Bookmark entity, its attributes, and the transitions between Active, Archived, and Trashed states.
code_symbols: [SYM#d731bc2f45cac29b2961ab00083bab5345db0a5e, SYM#d570461c1ff2b0eb81e078e185a46de87938f933, SYM#6d5b77b3f04288620db996a9bc18b13d3bd1ad3b]
section_id: c2a246e3-bbc1-40d8-920d-418b8d45ed00_bookmark_lifecycle_and_states
doc_type: guide
section_type: guide
---
The `Bookmark` entity in this project is more than a simple URL container; it is a state-aware domain object that manages its own visibility and lifecycle. This lifecycle is governed by the `BookmarkStatus` enumeration and a set of transition methods that ensure metadata consistency.

## Core States and the BookmarkStatus Enum

Every bookmark exists in one of three mutually exclusive states defined in `app/models/bookmark.py`:

*   **`ACTIVE`**: The default state for new bookmarks. These are visible in the main feed and search results.
*   **`ARCHIVED`**: For bookmarks that are no longer current but should be preserved.
*   **`TRASHED`**: A "soft-delete" state. Bookmarks in this state are hidden from standard views but can be restored or permanently deleted.

```python
class BookmarkStatus(Enum):
    """Visibility status of a bookmark."""
    ACTIVE = "active"
    ARCHIVED = "archived"
    TRASHED = "trashed"
```

## State Transitions

The `Bookmark` class provides explicit methods to transition between these states. These methods are responsible for updating the `status` attribute and refreshing the `updated_at` timestamp via the internal `_touch()` helper.

### Archiving and Trashing
When a bookmark is archived or trashed, its status is updated, and it is effectively moved out of the primary "Active" pool.

```python
# From app/models/bookmark.py
def archive(self) -> None:
    """Move the bookmark to the archive."""
    self.status = BookmarkStatus.ARCHIVED
    self._touch()

def trash(self) -> None:
    """Soft-delete the bookmark by moving it to the trash."""
    self.status = BookmarkStatus.TRASHED
    self._touch()
```

### Restoration
The `restore()` method is the inverse of both `archive()` and `trash()`, returning the bookmark to the `ACTIVE` state regardless of its previous status.

```python
def restore(self) -> None:
    """Restore a trashed or archived bookmark to active status."""
    self.status = BookmarkStatus.ACTIVE
    self._touch()
```

## Soft-Delete vs. Hard-Delete

This project implements a soft-delete pattern at the service layer. When a user "deletes" a bookmark via the API, the `BookmarkService` does not remove the record from storage. Instead, it invokes the `trash()` method.

```python
# From app/services/bookmark_service.py
def delete_bookmark(self, bookmark_id: str) -> bool:
    """Soft-delete by trashing the bookmark."""
    bookmark = self._repo.get_bookmark(bookmark_id)
    if not bookmark:
        return False
    bookmark.trash()
    self._repo.save_bookmark(bookmark)
    self._cache.invalidate(bookmark_id)
    return True
```

A **hard-delete** (permanent removal) is only possible by calling `BookmarkRepository.delete_bookmark(bookmark_id)` directly, which is currently not exposed through the public `BookmarkService` or API routes.

## Automatic Metadata Management

The `Bookmark` lifecycle includes automatic tracking of modifications. Every state transition (archive, trash, restore) and every tag modification (`add_tag`, `remove_tag`) triggers the `_touch()` method.

```python
def _touch(self) -> None:
    """Update the modification timestamp."""
    self.updated_at = datetime.utcnow()
```

This ensures that the `updated_at` field accurately reflects the last time the bookmark's state or associations were changed.

## Filtering by Status

The `BookmarkRepository` handles the retrieval of bookmarks based on their lifecycle state. When listing bookmarks, the `status` string provided by the service layer is converted into a `BookmarkStatus` enum member to filter the results.

```python
# From app/db/repository.py
def list_bookmarks(self, page: int = 1, per_page: int = 25, status: Optional[str] = None):
    items = list(self._bookmarks.values())
    if status:
        try:
            target = BookmarkStatus(status)
            items = [b for b in items if b.status == target]
        except ValueError:
            # If an invalid status string is passed, the filter is ignored
            pass
    # ... pagination and sorting ...
```

## Creation and Hydration

When creating a new bookmark using `Bookmark.from_dict(data)`, the system ignores any status or ID provided in the input dictionary. This ensures that all new bookmarks start as `ACTIVE` with a fresh, system-generated 12-character hex ID.

```python
# From app/models/bookmark.py
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> "Bookmark":
    return cls(
        url=data["url"],
        title=data["title"],
        description=data.get("description", ""),
        tags=data.get("tags", []),
    )
```

Note that `from_dict` is intended for **creation** from user input. For full hydration (e.g., loading from a database), the attributes like `status`, `id`, and `created_at` must be set manually or via the class constructor, as they are not extracted by this method.