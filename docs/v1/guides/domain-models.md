---
title: Domain Models
description: Explore the core data structures representing bookmarks, tags, and collections that form the backbone of the application.
code_symbols: [SYM#d731bc2f45cac29b2961ab00083bab5345db0a5e, SYM#e15c91e9e7eae95d052f50388a60d0bc30b3fe67, SYM#97d8a6cbf0c47108aa2beb39fafa695229654067]
section_id: 203a0311-ff15-4da3-a519-8def46a9e902_domain_models
doc_type: explanation
section_type: guide
---
Domain models in this application are implemented as Python `dataclasses`, providing a clean, type-hinted structure for the core business entities. These models—Bookmarks, Tags, and Collections—encapsulate both the data and the fundamental state-transition logic of the system.

## The Bookmark Entity

The `Bookmark` class (defined in `app/models/bookmark.py`) is the central entity of the application. It represents a saved URL along with its metadata and organizational state.

### Lifecycle and Status
A bookmark's visibility is managed through the `BookmarkStatus` enum, which supports three states:
*   `ACTIVE`: The default state for new bookmarks.
*   `ARCHIVED`: For bookmarks that are no longer needed in the main view but should be preserved.
*   `TRASHED`: A soft-delete state.

The model provides explicit methods for these transitions, ensuring that the `updated_at` timestamp is always refreshed via a private `_touch()` helper:

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

### Identification
Bookmarks are identified by a 12-character hex string generated using `uuid.uuid4().hex[:12]`. This provides a unique, URL-friendly identifier that is shorter than a full UUID while maintaining a low collision probability for the expected scale of the application.

## The Tag Entity

Tags (defined in `app/models/tag.py`) provide a flat organizational structure. Each `Tag` consists of a name, a `TagColor` enum (e.g., `RED`, `GREEN`, `BLUE`), and a `usage_count`.

### Validation and Constraints
Tag names are subject to strict validation rules defined in `app/models/_validators.py`. They cannot be empty, must be under 50 characters, and cannot use reserved names such as `all`, `untagged`, `archived`, or `trash`.

The model handles its own renaming logic to ensure these constraints are met:

```python
# app/models/tag.py

def rename(self, new_name: str) -> None:
    """Rename the tag with validation."""
    new_name = new_name.strip()
    if not new_name:
        raise ValueError("Tag name cannot be empty")
    if len(new_name) > 50:
        raise ValueError("Tag name cannot exceed 50 characters")
    self.name = new_name
```

### Usage Tracking
To optimize UI rendering (such as showing the number of bookmarks per tag in a sidebar), the `Tag` model tracks its own usage via `increment_usage()` and `decrement_usage()` methods. These counts are updated by the `BookmarkService` whenever tags are attached to or removed from bookmarks.

## The Collection Entity

Collections (defined in `app/models/collection.py`) allow for grouping bookmarks. The system distinguishes between two types of collections via the `CollectionType` enum:

### Manual Collections
In a `MANUAL` collection, users explicitly add or remove bookmark IDs. These collections support custom ordering through the `reorder()` method, which validates that the new list of IDs matches the existing set exactly.

### Smart Collections
`SMART` collections are dynamic. They use a `filter_rule` (a simple keyword string) to automatically include bookmarks. The logic for this is contained within the `_apply_filter` method:

```python
# app/models/collection.py

def _apply_filter(self, bookmarks: list) -> List[str]:
    """Evaluate the filter_rule against a list of bookmarks."""
    if not self.filter_rule:
        return []
    keyword = self.filter_rule.lower()
    return [b.id for b in bookmarks if keyword in b.title.lower() or keyword in b.description.lower()]
```

Note that `add_bookmark()` will return `False` if called on a smart collection, as membership is governed strictly by the filter rule.

## Implementation Patterns

### Serialization and Deserialization
Every domain model implements `to_dict()` and `from_dict()` methods. This pattern decouples the internal data structure from the API representation. For example, `to_dict()` handles the conversion of `datetime` objects to ISO-formatted strings and `Enum` members to their raw values.

### Cross-Entity Consistency
While the models manage their own internal state, the `BookmarkService` (in `app/services/bookmark_service.py`) is responsible for maintaining consistency across different entities. A primary example is the `delete_tag` operation:

```python
# app/services/bookmark_service.py

def delete_tag(self, tag_id: str) -> bool:
    """Delete a tag and strip it from all bookmarks."""
    tag = self._repo.get_tag(tag_id)
    if not tag:
        return False
    # Cross-entity cleanup
    for bookmark in self._repo.get_bookmarks_with_tag(tag_id):
        bookmark.remove_tag(tag_id)
        self._repo.save_bookmark(bookmark)
        self._cache.invalidate(bookmark.id)
    self._repo.delete_tag(tag_id)
    return True
```

This design choice keeps the domain models focused on their own data while the service layer orchestrates complex interactions that span multiple repositories or caches.