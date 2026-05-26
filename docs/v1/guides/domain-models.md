---
title: Domain Models
description: Core data structures and business logic for bookmarks, tags, and collections.
code_symbols: [SYM#d731bc2f45cac29b2961ab00083bab5345db0a5e, SYM#e15c91e9e7eae95d052f50388a60d0bc30b3fe67, SYM#97d8a6cbf0c47108aa2beb39fafa695229654067]
section_id: 6986c67b-18f6-4b43-8d8b-6b5106071bc0_domain_models
doc_type: explanation
section_type: guide
---
The domain models in this project define the core entities for managing bookmarks, tags, and collections. These models are implemented as Python dataclasses, providing a clean structure for data while encapsulating basic business logic.

## Core Entities

The system revolves around three primary entities: `Bookmark`, `Tag`, and `Collection`. Each entity is responsible for its own state transitions and internal consistency.

### Bookmark
The `Bookmark` class (found in `app/models/bookmark.py`) is the central entity. It represents a saved URL along with metadata like title, description, and status.

A key feature of the `Bookmark` model is its lifecycle management through the `BookmarkStatus` enum:
- **ACTIVE**: The default state for new bookmarks.
- **ARCHIVED**: For bookmarks that are no longer needed but should be kept.
- **TRASHED**: A soft-delete state.

The model includes methods to transition between these states:
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
Each `Bookmark` is assigned a unique 12-character hex UUID upon creation.

### Tag
The `Tag` class (in `app/models/tag.py`) allows for organizing bookmarks. It includes a `name`, a `color` (from the `TagColor` enum), and a `usage_count`. Tags use an 8-character hex UUID.

The model tracks how many bookmarks are associated with it, though the actual enforcement of this count is handled by the service layer:
```python
def increment_usage(self) -> int:
    """Record that a bookmark now uses this tag. Returns new count."""
    self.usage_count += 1
    return self.usage_count
```

### Collection
The `Collection` class (in `app/models/collection.py`) groups bookmarks. It supports two types defined by `CollectionType`:
1.  **MANUAL**: Users explicitly add or remove bookmark IDs.
2.  **SMART**: Bookmarks are included automatically based on a `filter_rule`.

Smart collections use a simple substring match against bookmark titles and descriptions:
```python
def _apply_filter(self, bookmarks: list) -> List[str]:
    if not self.filter_rule:
        return []
    keyword = self.filter_rule.lower()
    return [b.id for b in bookmarks if keyword in b.title.lower() or keyword in b.description.lower()]
```

## Service Layer Orchestration

The `BookmarkService` (in `app/services/bookmark_service.py`) acts as a Singleton facade that orchestrates operations across models, the repository, and the search index. It is the primary entry point for business logic.

### Validation and Creation
The service ensures that data is valid before creating domain objects. It uses internal validators (from `app/models/_validators.py`) to check URLs and titles.

```python
def create_bookmark(self, data: Dict[str, Any]) -> Tuple[Optional[Bookmark], Optional[str]]:
    error = _validate_url(data.get("url", "")) or _validate_title(data.get("title", ""))
    if error:
        return None, error

    bookmark = Bookmark.from_dict(data)
    self._repo.save_bookmark(bookmark)
    self._search.index_bookmark(bookmark)
    self._cache.invalidate(bookmark.id)
    return bookmark, None
```

### Cross-Entity Consistency
One of the most important roles of the `BookmarkService` is maintaining referential integrity. For example, when a `Tag` is deleted, the service must ensure it is removed from all bookmarks that reference it:

```python
def delete_tag(self, tag_id: str) -> bool:
    tag = self._repo.get_tag(tag_id)
    if not tag:
        return False
    for bookmark in self._repo.get_bookmarks_with_tag(tag_id):
        bookmark.remove_tag(tag_id)
        self._repo.save_bookmark(bookmark)
        self._cache.invalidate(bookmark.id)
    self._repo.delete_tag(tag_id)
    return True
```

## Storage and Persistence

The `BookmarkRepository` (in `app/db/repository.py`) provides an in-memory data store for all domain entities. It uses Python dictionaries to store objects by their IDs:

```python
class BookmarkRepository:
    def __init__(self) -> None:
        self._bookmarks: Dict[str, Bookmark] = {}
        self._tags: Dict[str, Tag] = {}
        self._collections: Dict[str, Collection] = {}
```

This design choice means that **all data is volatile** and will be lost when the application process terminates. The repository provides standard CRUD operations and basic pagination for bookmarks:

```python
def list_bookmarks(
    self,
    page: int = 1,
    per_page: int = 25,
    status: Optional[str] = None,
) -> Tuple[List[Bookmark], int]:
    items = list(self._bookmarks.values())
    # ... filtering and sorting logic ...
    start = (page - 1) * per_page
    return items[start : start + per_page], total
```

## Design Tradeoffs

The implementation of domain models in this project reflects several specific design decisions:

1.  **In-Memory Storage**: By using a dictionary-based repository instead of a persistent database, the system achieves high performance for small datasets but lacks durability.
2.  **Simple Search**: The `SearchIndex` and smart collection filters use basic substring matching. While efficient for small numbers of bookmarks, this does not support advanced features like fuzzy matching or relevance ranking.
3.  **Manual Consistency**: Because there is no relational database to handle foreign key constraints, the `BookmarkService` must manually iterate through bookmarks to clean up tags or update collections. This is visible in `delete_tag`, which performs a full scan of bookmarks via `get_bookmarks_with_tag`.
4.  **Fixed Cache Size**: The `BookmarkService` utilizes an `LRUCache` with a hardcoded `max_size` of 256, which may need adjustment if the number of active bookmarks grows significantly.
