---
title: Architecture and Caching Strategy
description: An explanation of the service's design as a facade, its singleton lifecycle, and the use of LRU caching for performance optimization.
code_symbols: [SYM#fdcfaed9972e477ae4585fd1b279ac107fa534cd]
section_id: 5aea3ed1-73ce-488a-bb20-e7e70e99382c_architecture_and_caching_strategy
doc_type: explanation
---

The architecture of the bookmarking service is built around a centralized facade and a singleton lifecycle. This design ensures that complex operations involving data persistence, full-text search, and performance optimization are coordinated from a single point of truth, while maintaining a shared state across the application's various modules.

## The Service Facade Pattern

The `BookmarkService` class in `app/services/bookmark_service.py` acts as a **Facade**. It provides a simplified interface for the API layer (Flask blueprints) to interact with the underlying subsystems. Instead of the routes directly managing database queries, search indexing, or cache logic, they delegate these responsibilities to the service.

This centralization is critical for maintaining data consistency. For example, when a bookmark is created, the service ensures it is simultaneously persisted to the repository, added to the search index, and handled by the cache:

```python
def create_bookmark(self, data: Dict[str, Any]) -> Tuple[Optional[Bookmark], Optional[str]]:
    # ... validation logic ...
    bookmark = Bookmark.from_dict(data)
    self._repo.save_bookmark(bookmark)      # Persistence
    self._search.index_bookmark(bookmark)   # Search Indexing
    self._cache.invalidate(bookmark.id)     # Cache Management
    return bookmark, None
```

## Singleton Lifecycle and Shared State

The `BookmarkService` is implemented as a singleton using the `__new__` method. This design choice is driven by the need to share stateful components—specifically the in-memory `SearchIndex` and the `LRUCache`—across different Flask blueprints.

```python
_instance: Optional["BookmarkService"] = None

def __new__(cls) -> "BookmarkService":
    """Singleton — share state across blueprint modules."""
    if cls._instance is None:
        cls._instance = super().__new__(cls)
        cls._instance._init_services()
    return cls._instance
```

By ensuring only one instance of the service exists, the application avoids the overhead of rebuilding the search index (which happens on initialization in `SearchIndex._rebuild`) for every request. It also ensures that a cache hit in the `bookmarks` blueprint benefits from a previous write or read performed in the `collections` blueprint.

## Caching Strategy

The service employs a **Least-Recently-Used (LRU)** caching strategy to optimize read performance for frequently accessed bookmarks.

### Implementation Details
The cache is implemented in `app/services/_cache.py` using a `collections.OrderedDict`. This allows for $O(1)$ access and eviction. When the cache reaches its capacity (configured to **256 entries** in `BookmarkService._init_services`), the oldest entry is automatically evicted.

### Read-Through and Write-Invalidate
The service implements a **Read-Through** pattern in `get_bookmark`. If a bookmark is not in the cache, it is fetched from the repository and then stored in the cache for future requests:

```python
def get_bookmark(self, bookmark_id: str) -> Optional[Bookmark]:
    cached = self._cache.get(bookmark_id)
    if cached is not None:
        return cached
    bookmark = self._repo.get_bookmark(bookmark_id)
    if bookmark:
        self._cache.put(bookmark.id, bookmark)
    return bookmark
```

For write operations (`delete_bookmark`, `archive_bookmark`), the service uses a **Write-Invalidate** strategy. Rather than updating the cache with new data, it explicitly removes the stale entry using `self._cache.invalidate(bookmark_id)`. This approach prioritizes data correctness and simplicity over the slight performance gain of a write-through update.

## Tradeoffs and Constraints

While this architecture provides a clean API and high performance for small-to-medium datasets, it introduces specific tradeoffs:

1.  **Memory Bound**: Both the `LRUCache` and the `SearchIndex` reside in memory. As the number of bookmarks grows, the memory footprint of the singleton service increases. The `SearchIndex` specifically rebuilds the entire index from the repository on startup, which may lead to slower cold starts as the database scales.
2.  **Manual Invalidation**: The "Write-Invalidate" pattern relies on the developer manually calling `self._cache.invalidate()` in every method that modifies a bookmark. Failure to do so results in stale data being served to the API.
3.  **Concurrency**: As a singleton in a typical Flask environment, the service assumes a thread-safe environment or relies on the underlying `OrderedDict` and repository implementations to handle concurrent access safely.
