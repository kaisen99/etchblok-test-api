---
title: Service Architecture and Caching
description: A technical deep-dive into the internal initialization of the repository, LRU cache, and search index, and how they maintain data consistency.
code_symbols: [SYM#dd5fd545693e00d6c0b38892bbd18ed4afa136a1, SYM#fdcfaed9972e477ae4585fd1b279ac107fa534cd]
section_id: 6241308e-990f-4989-902c-b0c6567b4573_service_architecture_and_caching
doc_type: explanation
section_type: guide
---
The `BookmarkService` serves as the central orchestration layer for the application, acting as a singleton facade that coordinates between persistent storage, high-performance caching, and full-text search. This architecture is designed to provide a unified API for the Flask blueprints while ensuring that data remains consistent across three distinct internal subsystems.

## The Singleton Facade Pattern

The `BookmarkService` is implemented as a singleton to ensure that state—specifically the in-memory cache and search index—is shared across all request contexts within the Flask application. This is achieved using the `__new__` method to control instantiation:

```python
class BookmarkService:
    _instance: Optional["BookmarkService"] = None

    def __new__(cls) -> "BookmarkService":
        """Singleton — share state across blueprint modules."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_services()
        return cls._instance
```

When the service is first initialized, the `_init_services` method bootstraps the three core components:
1.  **`BookmarkRepository`**: The primary source of truth for persistent data.
2.  **`LRUCache`**: A performance-oriented layer for single-entity lookups.
3.  **`SearchIndex`**: An in-memory inverted index for full-text discovery.

## Caching Strategy and Implementation

The application uses a **read-through caching** pattern for individual bookmark retrieval. The `LRUCache` (found in `app/services/_cache.py`) is a generic implementation backed by an `OrderedDict`, which allows for $O(1)$ access and eviction.

In `BookmarkService.get_bookmark`, the service first checks the cache before falling back to the repository:

```python
def get_bookmark(self, bookmark_id: str) -> Optional[Bookmark]:
    """Retrieve a bookmark by ID, using cache when available."""
    cached = self._cache.get(bookmark_id)
    if cached is not None:
        return cached
    bookmark = self._repo.get_bookmark(bookmark_id)
    if bookmark:
        self._cache.put(bookmark.id, bookmark)
    return bookmark
```

The cache is initialized with a `max_size` of 256 in the service layer. When the capacity is exceeded, the least-recently-used item is evicted via `self._store.popitem(last=False)`.

## Data Consistency and Invalidation

Maintaining consistency between the repository, the cache, and the search index is a manual responsibility of the `BookmarkService`. Because the cache and search index are in-memory structures, every mutation operation must explicitly synchronize them.

### Mutation Workflow
Whenever a bookmark is created, updated, or deleted, the service follows a strict sequence:
1.  **Persist**: Save the change to the `BookmarkRepository`.
2.  **Index**: Update the `SearchIndex` (for creates and updates).
3.  **Invalidate**: Remove the stale entry from the `LRUCache`.

For example, in `update_bookmark`:
```python
self._repo.save_bookmark(bookmark)
self._search.index_bookmark(bookmark)
self._cache.invalidate(bookmark.id)
```

### Cross-Entity Consistency
A more complex consistency challenge occurs during tag deletion. Since bookmarks store tag IDs, deleting a tag requires cleaning up all bookmarks that reference it. The `BookmarkService` handles this by iterating through affected bookmarks, updating them, and invalidating their respective cache entries:

```python
def delete_tag(self, tag_id: str) -> bool:
    # ... lookup tag ...
    for bookmark in self._repo.get_bookmarks_with_tag(tag_id):
        bookmark.remove_tag(tag_id)
        self._repo.save_bookmark(bookmark)
        self._cache.invalidate(bookmark.id)
    self._repo.delete_tag(tag_id)
    return True
```

## Search Indexing Mechanism

The `SearchIndex` (in `app/services/search_service.py`) provides full-text search capabilities without requiring an external search engine. It functions as an inverted index, mapping tokens (words) to sets of bookmark IDs.

### Initialization and Rebuilding
On startup, the `SearchIndex` performs a full rebuild by fetching all bookmarks from the repository:
```python
def _rebuild(self) -> None:
    """Rebuild the entire index from the repository."""
    self._index.clear()
    all_bookmarks, _ = self._repo.list_bookmarks(page=1, per_page=10000)
    for bookmark in all_bookmarks:
        self.index_bookmark(bookmark)
```

### Incremental Updates
To avoid expensive full rebuilds during runtime, the index supports incremental updates via `index_bookmark(bookmark)`. This method first removes the old version of the bookmark from the index and then re-tokenizes the title and description to map the new content.

## Design Tradeoffs and Constraints

The current architecture prioritizes simplicity and performance for small-to-medium datasets, but introduces specific tradeoffs:

*   **Memory Footprint**: Both the `LRUCache` and `SearchIndex` reside entirely in memory. As the number of bookmarks grows, the memory usage of the application will increase linearly.
*   **Startup Latency**: The `SearchIndex` rebuilds itself on every application start. For very large repositories, this could lead to significant delays before the service is ready to handle requests.
*   **Manual Invalidation Risk**: The reliance on manual cache invalidation (e.g., calling `self._cache.invalidate` in every mutation method) creates a risk of stale data if a developer adds a new mutation path but forgets to include the invalidation logic.
*   **Search Ranking**: The `SearchIndex` uses a basic frequency-based ranking (`_rank_results`) and token AND-ing. While efficient, it lacks advanced features like fuzzy matching or BM25 ranking found in dedicated search engines.
