---
title: Domain Model Architecture
description: An overview of the core entities—Bookmarks, Tags, and Collections—and how they interact to form the application's data layer.
code_symbols: [SYM#d731bc2f45cac29b2961ab00083bab5345db0a5e, SYM#e15c91e9e7eae95d052f50388a60d0bc30b3fe67, SYM#97d8a6cbf0c47108aa2beb39fafa695229654067]
section_id: a7412723-0650-4e98-b0fa-92c7d395c8a2_domain_model_architecture
doc_type: explanation
section_type: guide
---
The application's data layer is built around three primary domain entities: **Bookmarks**, **Tags**, and **Collections**. These entities are implemented as Python dataclasses in the `app/models` directory, providing a clean separation between data structure and the business logic orchestrated by the service layer.

## Core Entities

### Bookmark
The `Bookmark` class (found in `app/models/bookmark.py`) is the central entity. It represents a saved URL along with user-provided metadata. 

Key characteristics include:
- **ID-based Tagging**: Instead of holding full `Tag` objects, a `Bookmark` maintains a list of tag IDs (`tags: List[str]`). This decoupling allows tags to be managed independently.
- **Status Management**: Every bookmark has a `BookmarkStatus` (ACTIVE, ARCHIVED, or TRASHED). The model provides explicit methods like `archive()`, `trash()`, and `restore()` to transition between these states.
- **Metadata**: An arbitrary `metadata` dictionary allows for future extensibility without modifying the core schema.

```python
@dataclass
class Bookmark:
    url: str
    title: str
    description: str = ""
    tags: List[str] = field(default_factory=list)
    status: BookmarkStatus = BookmarkStatus.ACTIVE
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    # ...
```

### Tag
The `Tag` class (`app/models/tag.py`) provides a way to categorize bookmarks. It includes a `name`, a `color` (from the `TagColor` enum), and a `usage_count`. The `usage_count` is an optimization used to track how many bookmarks are currently associated with the tag without performing a full repository scan.

### Collection
The `Collection` class (`app/models/collection.py`) groups bookmarks into named sets. It supports two distinct operational modes defined by `CollectionType`:
- **MANUAL**: Users explicitly add or remove bookmark IDs using `add_bookmark()` and `remove_bookmark()`.
- **SMART**: The collection is auto-populated based on a `filter_rule`. The `_apply_filter` method performs a keyword match against bookmark titles and descriptions to determine membership.

```python
def _apply_filter(self, bookmarks: list) -> List[str]:
    if not self.filter_rule:
        return []
    keyword = self.filter_rule.lower()
    return [b.id for b in bookmarks if keyword in b.title.lower() or keyword in b.description.lower()]
```

## Orchestration and Consistency

While the models contain internal state logic (like updating `updated_at` via `_touch()`), the `BookmarkService` in `app/services/bookmark_service.py` acts as the primary facade for the domain. It ensures that operations affecting multiple entities remain consistent.

### Cross-Entity Cleanup
A critical responsibility of the `BookmarkService` is managing the relationship between tags and bookmarks. For example, when a tag is deleted, the service must ensure that the tag ID is removed from every bookmark that references it.

```python
def delete_tag(self, tag_id: str) -> bool:
    tag = self._repo.get_tag(tag_id)
    if not tag:
        return False
    # Ensure consistency across all bookmarks using this tag
    for bookmark in self._repo.get_bookmarks_with_tag(tag_id):
        bookmark.remove_tag(tag_id)
        self._repo.save_bookmark(bookmark)
        self._cache.invalidate(bookmark.id)
    self._repo.delete_tag(tag_id)
    return True
```

### Validation Constraints
The domain model enforces strict validation rules via `app/models/_validators.py`. These constraints are applied in the service layer before any model is instantiated or persisted:
- **Reserved Names**: Tag names such as `all`, `untagged`, `archived`, and `trash` are reserved for system use and cannot be used for custom tags.
- **Length Limits**: Titles are capped at 256 characters (`_MAX_TITLE_LENGTH`), and descriptions at 2048 characters (`_MAX_DESCRIPTION_LENGTH`).
- **URL Integrity**: URLs must match a specific regex pattern (`_URL_PATTERN`) ensuring they use `http` or `https` protocols.

## State Transitions and Soft Deletion
The architecture favors soft deletion for bookmarks. When a user deletes a bookmark via `BookmarkService.delete_bookmark()`, the system does not remove the record from the repository. Instead, it calls `bookmark.trash()`, which updates the status to `BookmarkStatus.TRASHED`. This allows for a "Trash" feature where items can be restored later using `restore_bookmark()`. Hard deletion is reserved for the repository layer and is not exposed through the standard service API.
