---
title: Persistence Layer
description: Data access objects and repositories responsible for in-memory storage and entity lifecycle management.
code_symbols: [SYM#09a56e7acb86a9afef18a62134c27802cd473050]
section_id: 4e572c41-bdc4-4ee1-9379-b4b9b6345d18_persistence_layer
doc_type: explanation
section_type: guide
---
The persistence layer in this project is designed around an in-memory repository pattern, providing a clean abstraction for data access while maintaining high performance for small-to-medium datasets. This approach decouples the business logic from the underlying storage mechanism, allowing the application to operate without an external database dependency while providing a clear path for future migration to persistent storage.

## The Repository Pattern

The central component of the persistence layer is the `BookmarkRepository` located in `app/db/repository.py`. It serves as a Data Access Object (DAO) for the three primary domain entities: `Bookmark`, `Tag`, and `Collection`.

### In-Memory Storage
The repository uses standard Python dictionaries to store entities, keyed by their unique identifiers. This ensures $O(1)$ lookup times for individual items.

```python
# app/db/repository.py

class BookmarkRepository:
    def __init__(self) -> None:
        self._bookmarks: Dict[str, Bookmark] = {}
        self._tags: Dict[str, Tag] = {}
        self._collections: Dict[str, Collection] = {}
```

Because the storage is in-memory, all mutation methods like `save_bookmark` or `delete_tag` persist changes immediately to the internal state. However, this data is ephemeral and is lost when the application process restarts.

### Pagination and Filtering
The repository implements basic pagination and filtering logic within the `list_bookmarks` method. It returns a tuple containing the requested slice of items and the total count of matching items, which is a common pattern for supporting frontend pagination controls.

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
            pass
    items.sort(key=lambda b: b.created_at, reverse=True)
    total = len(items)
    start = (page - 1) * per_page
    return items[start : start + per_page], total
```

## Full-Text Search Indexing

To support efficient searching without a traditional database's `LIKE` or `MATCH` queries, the project implements a `SearchIndex` in `app/services/search_service.py`. This class maintains an inverted index that maps lowercase tokens to sets of bookmark IDs.

### Index Lifecycle
The `SearchIndex` is tightly coupled with the `BookmarkRepository`. Upon initialization, it performs a full rebuild by iterating through all bookmarks in the repository.

```python
# app/services/search_service.py

class SearchIndex:
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

### Search Execution
When a search is performed via `search()`, the index AND-es the tokens from the query. It then retrieves the actual `Bookmark` objects from the repository using the IDs found in the index.

```python
# app/services/search_service.py

def search(self, query: str, limit: int = 20) -> List[Bookmark]:
    tokens = self._tokenize(query)
    # ... logic to find candidate_ids ...
    results = []
    for bid in candidate_ids:
        bookmark = self._repo.get_bookmark(bid)
        if bookmark:
            results.append(bookmark)
    return self._rank_results(results, tokens)[:limit]
```

## Internal Connection Pooling Stub

While the current implementation is strictly in-memory, the codebase includes an internal `_ConnectionPool` and `_Connection` class in `app/db/_connection.py`. These classes are marked as internal (prefixed with underscores) and serve as a "future-proofing" stub.

The `_ConnectionPool` is designed to be thread-safe, using a `threading.Lock` to manage a pool of reusable connections. This structure suggests that the project is prepared to transition to a thread-safe database driver (like `psycopg2` or `sqlite3`) in the future without significant architectural changes to the repository layer.

## Service Layer Orchestration

The `BookmarkService` in `app/services/bookmark_service.py` acts as a facade that orchestrates the repository and the search index. It ensures that when data is modified in the repository, the search index is updated accordingly.

```python
# app/services/bookmark_service.py

def _init_services(self) -> None:
    """Bootstrap repository, cache, and search index."""
    self._repo = BookmarkRepository()
    self._cache: LRUCache[Bookmark] = LRUCache(max_size=256)
    self._search = SearchIndex(self._repo)
```

This orchestration ensures that the persistence layer remains a passive data store, while the service layer handles the side effects of data mutations, such as cache invalidation and search index updates.

## Design Tradeoffs

1.  **Volatility**: The most significant tradeoff is the lack of durability. Since data is stored in-memory, it does not survive application restarts. This is suitable for the current "test-api" scope but would require the implementation of the `_ConnectionPool` for production use.
2.  **Memory Usage**: As the number of bookmarks grows, memory consumption increases linearly. The `SearchIndex` also duplicates some data (tokens) in memory to facilitate fast lookups.
3.  **Initialization Overhead**: The `SearchIndex` rebuilds itself on startup. While fast for the current limit of 10,000 items, this would become a bottleneck for significantly larger datasets.
