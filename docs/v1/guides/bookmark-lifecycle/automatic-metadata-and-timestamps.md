---
title: Automatic Metadata and Timestamps
description: How the Bookmark model internally manages 'created_at' and 'updated_at' fields through the '_touch' helper during lifecycle events.
code_symbols: [SYM#d731bc2f45cac29b2961ab00083bab5345db0a5e, SYM#6d5b77b3f04288620db996a9bc18b13d3bd1ad3b]
section_id: 7fd2131a-cf82-4118-8017-c12a7f9c12eb_automatic_metadata_and_timestamps
doc_type: guide
section_type: guide
---
The `Bookmark` model in `app/models/bookmark.py` is designed to be a self-managing entity that tracks its own creation and modification times. This is achieved through the use of Python dataclasses and a private helper method, `_touch()`, which ensures that the `updated_at` timestamp is synchronized with state changes.

## Core Timestamp Fields

The `Bookmark` class defines two primary timestamp fields using the `dataclasses.field` default factory. This ensures that every new bookmark instance is automatically timestamped at the moment of instantiation.

```python
# app/models/bookmark.py

class Bookmark:
    # ...
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    # ...
```

Both fields use `datetime.utcnow`, providing naive UTC timestamps. While `created_at` remains static after initialization, `updated_at` is designed to be refreshed whenever the bookmark's data or status changes.

## The _touch Helper

The internal `_touch()` method is the central mechanism for updating the modification timestamp. It is a simple helper that resets `updated_at` to the current UTC time.

```python
# app/models/bookmark.py

def _touch(self) -> None:
    """Update the modification timestamp."""
    self.updated_at = datetime.utcnow()
```

By encapsulating this logic in a single method, the codebase ensures consistent timestamping behavior across different types of updates.

## Internal Lifecycle Events

The `Bookmark` model calls `_touch()` internally within its public API methods. This means that any high-level operation performed directly on the model instance automatically triggers a timestamp update.

### Status Transitions
When a bookmark is archived, trashed, or restored, the `status` field is updated and `_touch()` is called:

```python
# app/models/bookmark.py

def archive(self) -> None:
    """Move the bookmark to the archive."""
    self.status = BookmarkStatus.ARCHIVED
    self._touch()

def trash(self) -> None:
    """Soft-delete the bookmark by moving it to the trash."""
    self.status = BookmarkStatus.TRASHED
    self._touch()
```

### Tag Management
Modifying the list of tags associated with a bookmark also counts as a modification:

```python
# app/models/bookmark.py

def add_tag(self, tag_id: str) -> bool:
    """Attach a tag. Returns False if already present."""
    if tag_id in self.tags:
        return False
    self.tags.append(tag_id)
    self._touch()
    return True
```

## Service-Level Integration

While the `Bookmark` model handles its own internal state changes, the `BookmarkService` in `app/services/bookmark_service.py` is responsible for partial updates to fields like `title`, `url`, and `description`. 

Because these fields are modified directly on the object within the service layer, the service explicitly calls `bookmark._touch()` before persisting the changes to the repository.

```python
# app/services/bookmark_service.py

def update_bookmark(self, bookmark_id: str, data: Dict[str, Any]) -> Tuple[Optional[Bookmark], Optional[str]]:
    """Partially update a bookmark."""
    bookmark = self._repo.get_bookmark(bookmark_id)
    if not bookmark:
        return None, None

    # ... field updates (title, description, url) ...

    bookmark._touch()
    self._repo.save_bookmark(bookmark)
    # ... cache and search index updates ...
    return bookmark, None
```

This pattern ensures that even when fields are updated outside of the model's own methods, the `updated_at` metadata remains accurate.

## Metadata Extensibility

In addition to timestamps, the `Bookmark` model includes a `metadata` field, which is a dictionary intended for arbitrary key/value pairs.

```python
# app/models/bookmark.py

metadata: Dict[str, Any] = field(default_factory=dict)
```

This field allows for future extensibility without requiring schema changes to the core `Bookmark` class. When the bookmark is serialized via `to_dict()`, both the timestamps (in ISO format) and the metadata dictionary are included in the output.

```python
# app/models/bookmark.py

def to_dict(self) -> Dict[str, Any]:
    """Serialise to a plain dictionary for JSON responses."""
    return {
        # ...
        "created_at": self.created_at.isoformat(),
        "updated_at": self.updated_at.isoformat(),
        "metadata": self.metadata,
    }
```