---
title: Data Persistence
description: In-memory storage and repository patterns for managing the lifecycle of application entities.
code_symbols: [SYM#09a56e7acb86a9afef18a62134c27802cd473050]
section_id: 80cc4bd3-0eb4-4d14-82d9-8042416b2fb7_data_persistence
doc_type: guide
section_type: guide
---
Data persistence in this application is implemented using an in-memory repository pattern, orchestrated by a central service layer that manages caching and full-text indexing. While the current implementation stores data in volatile memory, the architecture is designed to be easily swapped for a persistent database like SQLite or PostgreSQL.

## The Repository Pattern

The `BookmarkRepository` class, located in `app/db/repository.py`, serves as the primary abstraction for data access. It maintains internal dictionaries for the three core entities: `Bookmark`, `Tag`, and `Collection`.

By isolating data access within the repository, the rest of the application remains agnostic to the underlying storage mechanism. The repository provides standard CRUD operations and basic filtering logic.

```python
class BookmarkRepository:
    """In-memory storage for bookmarks, tags, and collections."""

    def __init__(self) -> None:
        self._bookmarks: Dict[str, Bookmark] = {}
        self._tags: Dict[str, Tag] = {}
        self._collections: Dict[str, Collection] = {}

    def save_bookmark(self, bookmark: Bookmark) -> None:
        """Insert or update a bookmark."""
        self._bookmarks[bookmark.id] = bookmark

    def list_bookmarks(
        self,
        page: int = 1,
        per_page: int = 25,
        status: Optional[str] = None,
    ) -> Tuple[List[Bookmark], int]:
        """Return a paginated slice of bookmarks with optional status filtering."""
        items = list(self._bookmarks.values())
        if status:
            try:
                target = BookmarkStatus(status)
                items = [b for b in items if b.status == target]
            except ValueError:
                pass
        items.sort(key=lambda b: b.created_at, reverse=True)
        # ... pagination logic ...
        return items[start : start + per_page], total
```

## Service Layer Orchestration

The `BookmarkService` in `app/services/bookmark_service.py` acts as a singleton facade and the primary entry point for business logic. It orchestrates the `BookmarkRepository`, an `LRUCache`, and a `SearchIndex` to ensure data consistency across different subsystems.

When a bookmark is created or updated, the service ensures it is persisted in the repository, indexed for search, and that any stale cache entries are invalidated.

```python
def create_bookmark(self, data: Dict[str, Any]) -> Tuple[Optional[Bookmark], Optional[str]]:
    # Validation logic...
    bookmark = Bookmark.from_dict(data)
    
    # Orchestration across persistence, search, and cache
    self._repo.save_bookmark(bookmark)
    self._search.index_bookmark(bookmark)
    self._cache.invalidate(bookmark.id)
    
    return bookmark, None
```

### Singleton Lifecycle
The `BookmarkService` uses a singleton pattern to ensure that the in-memory state is shared across all Flask blueprint modules. It initializes its dependencies via the `_init_services` method:

```python
def _init_services(self) -> None:
    """Bootstrap repository, cache, and search index."""
    self._repo = BookmarkRepository()
    self._cache: LRUCache[Bookmark] = LRUCache(max_size=256)
    self._search = SearchIndex(self._repo)
```

## Caching and Search Indexing

To optimize performance and provide advanced querying capabilities, the persistence layer is augmented with specialized in-memory structures.

### LRU Caching
The `LRUCache` (found in `app/services/_cache.py`) is a generic least-recently-used cache with a fixed capacity (defaulting to 256 entries in the service layer). It uses an `OrderedDict` to track access order, moving items to the end on every `get` or `put` operation.

```python
def get(self, key: str) -> Optional[T]:
    if key in self._store:
        self._store.move_to_end(key)
        self._stats["hits"] += 1
        return self._store[key]
    self._stats["misses"] += 1
    return None
```

### Full-Text Search Index
The `SearchIndex` in `app/services/search_service.py` implements an inverted index mapping tokens to bookmark IDs. On application startup, it rebuilds the entire index by scanning the repository.

```python
def __init__(self, repository: "BookmarkRepository") -> None:
    self._repo = repository
    self._index: Dict[str, Set[str]] = defaultdict(set)
    self._rebuild()

def _rebuild(self) -> None:
    """Rebuild the entire index from the repository."""
    self._index.clear()
    all_bookmarks, _ = self._repo.list_bookmarks(page=1, per_page=10000)
    for bookmark in all_bookmarks:
        self.index_bookmark(bookmark)
```

## Database Integration Blueprint

While the current repository is in-memory, the codebase includes a `_ConnectionPool` in `app/db/_connection.py` that serves as a blueprint for future database integration. It implements thread-safe connection management with configurable pool sizes.

- **`_POOL_MIN_SIZE`**: 2
- **`_POOL_MAX_SIZE`**: 20

This internal structure demonstrates how the repository would eventually acquire and release connections to a real database:

```python
class _ConnectionPool:
    """Thread-safe pool of reusable database connections."""
    
    def acquire(self) -> _Connection:
        with self._lock:
            if self._available:
                conn = self._available.pop()
            elif len(self._in_use) < self._config.max_pool:
                conn = _Connection(self._config)
                conn.open()
            # ...
            self._in_use.append(conn)
            return conn
```

## Data Lifecycle and Soft Deletion

The application distinguishes between hard-deletion and soft-deletion (trashing). 
- **Hard Deletion**: Handled by the repository via methods like `delete_bookmark(bookmark_id)`, which removes the object from the internal dictionary.
- **Soft Deletion**: Handled at the service level by updating the `status` of the `Bookmark` entity to `BookmarkStatus.TRASHED`. The repository's `list_bookmarks` method then filters these out unless specifically requested.

```python
def delete_bookmark(self, bookmark_id: str) -> bool:
    """Soft-delete by trashing the bookmark."""
    bookmark = self._repo.get_bookmark(bookmark_id)
    if not bookmark:
        return False
    bookmark.trash() # Updates status to 'trashed'
    self._repo.save_bookmark(bookmark)
    self._cache.invalidate(bookmark_id)
    return True
```
