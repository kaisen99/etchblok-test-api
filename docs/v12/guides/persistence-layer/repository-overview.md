---
title: Repository Overview
description: An overview of the persistence layer architecture and the role of the BookmarkRepository in managing application data.
code_symbols: [SYM#09a56e7acb86a9afef18a62134c27802cd473050, SYM#adb8232356346a5957ff3a1a1b7ff70581f37649]
section_id: 7dd0ca2a-c5d1-4218-b299-a46654627823_repository_overview
doc_type: guide
section_type: guide
---
The `BookmarkRepository` class, located in `app/db/repository.py`, serves as the central persistence abstraction for the application. It provides a clean interface for managing the lifecycle of bookmarks, tags, and collections, decoupling the business logic in the service layer from the underlying data storage implementation.

## The Persistence Abstraction

In this codebase, the repository acts as an in-memory data store. While it mimics the interface of a traditional database repository, it stores all data in volatile memory using Python dictionaries. This design allows for rapid prototyping and testing without the overhead of managing an external database process.

The repository is responsible for:
- **Identity Management**: Storing and retrieving entities by their unique string IDs.
- **Filtering and Pagination**: Providing sliced views of the bookmark collection based on status and creation time.
- **Relationship Resolution**: Finding bookmarks associated with specific tags.

## In-Memory Data Structures

The `BookmarkRepository` maintains three primary internal collections. Each collection uses a dictionary where the key is the entity's ID and the value is the model instance itself (e.g., `Bookmark`, `Tag`, or `Collection`).

```python
class BookmarkRepository:
    def __init__(self) -> None:
        self._bookmarks: Dict[str, Bookmark] = {}
        self._tags: Dict[str, Tag] = {}
        self._collections: Dict[str, Collection] = {}
```

Because the storage is in-memory, all "save" operations persist immediately to these dictionaries. However, this also means that all data is lost when the application process terminates.

## Bookmark Management

The repository provides standard CRUD operations for the `Bookmark` model, but it also includes specialized logic for listing and filtering.

### CRUD Operations
The `save_bookmark` method handles both creation and updates. If a bookmark with the same ID already exists, it is overwritten.

```python
def save_bookmark(self, bookmark: Bookmark) -> None:
    """Insert or update a bookmark."""
    self._bookmarks[bookmark.id] = bookmark

def get_bookmark(self, bookmark_id: str) -> Optional[Bookmark]:
    """Retrieve a bookmark by ID, or None."""
    return self._bookmarks.get(bookmark_id)
```

### Filtering and Pagination
The `list_bookmarks` method implements the core logic for the application's main feed. It supports:
1.  **Status Filtering**: Filtering by `BookmarkStatus` (e.g., "active", "archived", "trashed").
2.  **Chronological Sorting**: Items are always sorted by `created_at` in descending order.
3.  **Pagination**: Using `page` and `per_page` parameters to return a specific slice of data.

```python
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
            pass
    items.sort(key=lambda b: b.created_at, reverse=True)
    total = len(items)
    start = (page - 1) * per_page
    return items[start : start + per_page], total
```

## Tag and Collection Management

Tags and collections follow a simpler CRUD pattern compared to bookmarks. They are primarily used to organize bookmarks, and the repository provides methods to manage these entities independently.

```python
def get_bookmarks_with_tag(self, tag_id: str) -> List[Bookmark]:
    """Return all bookmarks that have a specific tag attached."""
    return [b for b in self._bookmarks.values() if tag_id in b.tags]
```

The `get_bookmarks_with_tag` method demonstrates how the repository handles relationships. Since the `Bookmark` model stores tag IDs in a list, the repository performs a linear scan of all bookmarks to find matches.

## Integration with Services

The `BookmarkRepository` is a foundational component used by higher-level services.

### BookmarkService
The `BookmarkService` (in `app/services/bookmark_service.py`) instantiates the repository as a singleton during its own initialization. It delegates all data persistence tasks to the repository.

```python
def _init_services(self) -> None:
    """Bootstrap repository, cache, and search index."""
    self._repo = BookmarkRepository()
    # ...
    self._search = SearchIndex(self._repo)
```

### SearchIndex
The `SearchIndex` (in `app/services/search_service.py`) depends on the repository to bootstrap its inverted index. On startup, it calls `list_bookmarks` with a large `per_page` value to ingest all existing data.

```python
def _rebuild(self) -> None:
    """Rebuild the entire index from the repository."""
    self._index.clear()
    # Requesting a large page size to effectively get all bookmarks
    all_bookmarks, _ = self._repo.list_bookmarks(page=1, per_page=10000)
    for bookmark in all_bookmarks:
        self.index_bookmark(bookmark)
```

## Implementation Considerations

### Performance and Scaling
Because the repository performs sorting and filtering in-memory using Python's `list.sort()` and list comprehensions, performance may degrade as the number of bookmarks grows significantly. For the current scope of the application, this approach provides low-latency access without the complexity of SQL queries.

### Transactions and Data Integrity
The current implementation does not support transactions. Each call to a `save_*` or `delete_*` method is atomic relative to the dictionary operation, but there is no mechanism to roll back multiple changes if a complex operation fails mid-way in the service layer.

Furthermore, the repository relies on the caller (typically `BookmarkService`) to ensure data consistency. For example, deleting a tag via `delete_tag` removes the tag from the repository's internal dictionary but does not automatically remove that tag ID from the `tags` list of existing bookmarks.

### Diagnostics and Testing
The repository includes internal helpers like `_count_all()` and `_clear_all()`. These are intended for use in unit tests and system diagnostics to verify the state of the in-memory store without exposing the raw dictionaries.

```python
def _count_all(self) -> Dict[str, int]:
    """Return entity counts. Used for diagnostics."""
    return {
        "bookmarks": len(self._bookmarks),
        "tags": len(self._tags),
        "collections": len(self._collections),
    }

def _clear_all(self) -> None:
    """Wipe all data. Test use only."""
    self._bookmarks.clear()
    self._tags.clear()
    self._collections.clear()
```