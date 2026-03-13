---
title: Persistence Layer
description: Low-level data access patterns and repository implementations for storing and retrieving application entities.
code_symbols: [SYM#09a56e7acb86a9afef18a62134c27802cd473050]
section_id: 3c187e26-822e-4d1e-a6be-979bd3239895_persistence_layer
doc_type: guide
section_type: guide
---
The persistence layer in this application provides a clean abstraction over data storage, allowing the service layer to interact with entities without concern for the underlying storage mechanism. Currently, the system uses an in-memory implementation, though it includes internal infrastructure for future database integration.

## Bookmark Repository

The `BookmarkRepository` class in `app/db/repository.py` is the central data access point. It manages the lifecycle of three primary entities: `Bookmark`, `Tag`, and `Collection`.

### In-Memory Storage
The repository uses Python dictionaries to store entities by their unique IDs. This implementation is volatile; all data is lost when the application process restarts.

```python
class BookmarkRepository:
    """In-memory storage for bookmarks, tags, and collections."""

    def __init__(self) -> None:
        self._bookmarks: Dict[str, Bookmark] = {}
        self._tags: Dict[str, Tag] = {}
        self._collections: Dict[str, Collection] = {}
```

### Data Access Patterns
The repository implements standard CRUD operations for all entities. Mutation methods like `save_bookmark` or `save_tag` persist changes immediately to the internal dictionaries.

#### Pagination and Filtering
The `list_bookmarks` method provides a paginated view of the stored bookmarks. It supports filtering by status and returns a tuple containing the requested slice and the total count of matching items.

Key characteristics of the pagination logic:
- **1-based indexing**: The `page` argument starts at 1.
- **Status Filtering**: It uses the `BookmarkStatus` enum to filter. If an invalid status string is provided, the filter is silently ignored.
- **Sorting**: Results are always sorted by `created_at` in descending order.

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
            pass # Invalid status strings are ignored
    items.sort(key=lambda b: b.created_at, reverse=True)
    total = len(items)
    # 1-based pagination calculation
    start = (page - 1) * per_page
    return items[start : start + per_page], total
```

#### Specialized Queries
Beyond basic CRUD, the repository provides specialized retrieval methods such as `get_bookmarks_with_tag(tag_id)`. This method performs a linear scan over the in-memory bookmarks to find those containing a specific tag ID. This is used by the `BookmarkService` to perform cascading updates, such as stripping a tag from all bookmarks when that tag is deleted.

## Search Integration

The repository serves as the primary data source for the `SearchIndex` in `app/services/search_service.py`. When the search index is initialized, it performs a full scan of the repository to build its internal inverted index.

```python
# app/services/search_service.py

def _rebuild(self) -> None:
    """Rebuild the entire index from the repository."""
    self._index.clear()
    # Repository used to fetch all existing bookmarks
    all_bookmarks, _ = self._repo.list_bookmarks(page=1, per_page=10000)
    for bookmark in all_bookmarks:
        self.index_bookmark(bookmark)
```

During search operations, the `SearchIndex` retrieves the actual `Bookmark` objects from the repository using the IDs found in its index:

```python
def search(self, query: str, limit: int = 20) -> List[Bookmark]:
    # ... tokenization and candidate lookup ...
    results = []
    for bid in candidate_ids:
        bookmark = self._repo.get_bookmark(bid)
        if bookmark:
            results.append(bookmark)
    return self._rank_results(results, tokens)[:limit]
```

## Internal Database Infrastructure

The codebase includes a low-level database connection management system in `app/db/_connection.py`. While these classes are not currently utilized by the `BookmarkRepository`, they provide the foundation for future SQL-based persistence.

### Connection Management
- **`_Connection`**: Represents a single database connection. It includes basic transaction support with `begin_transaction`, `commit`, and `rollback` methods.
- **`_ConnectionPool`**: A thread-safe pool that manages a collection of `_Connection` objects. It uses a `threading.Lock` to coordinate access and maintains a configurable number of minimum and maximum connections.

These classes are prefixed with an underscore to indicate they are internal implementation details and should not be accessed directly by the service layer.

## Service Lifecycle

The `BookmarkRepository` is typically instantiated as a singleton-like member within the `BookmarkService`. During initialization, the service bootstraps the repository and passes it to other components.

In `app/services/bookmark_service.py`:
```python
def _init_services(self) -> None:
    """Bootstrap repository, cache, and search index."""
    self._repo = BookmarkRepository()
    self._cache: LRUCache[Bookmark] = LRUCache(max_size=256)
    self._search = SearchIndex(self._repo)
```

This architecture ensures that the `BookmarkService` remains the primary entry point for business logic, while the `BookmarkRepository` handles the mechanics of data retrieval and storage.

### Diagnostics and Testing
The repository includes internal helpers for system health and testing:
- **`_count_all()`**: Returns a dictionary of entity counts (bookmarks, tags, collections) for diagnostic purposes.
- **`_clear_all()`**: Wipes all internal dictionaries. This is used in test suites to ensure a clean state between test cases.

```python
# app/db/repository.py

def _clear_all(self) -> None:
    """Wipe all data. Test use only."""
    self._bookmarks.clear()
    self._tags.clear()
    self._collections.clear()
```