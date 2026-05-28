---
title: Service Initialization and Caching
description: Understanding the singleton pattern and the internal bootstrapping of the repository and LRU cache.
code_symbols: [SYM#dd5fd545693e00d6c0b38892bbd18ed4afa136a1, SYM#fdcfaed9972e477ae4585fd1b279ac107fa534cd]
section_id: ea3d6dea-95b4-48b7-a293-0e8159516516_service_initialization_and_caching
doc_type: guide
section_type: guide
---
The `BookmarkService` acts as the central orchestration layer for the application, managing the lifecycle of data across the repository, search index, and cache. Because the application relies on an in-memory data store, the service is implemented as a singleton to ensure that state is shared consistently across different Flask blueprints.

## Singleton Implementation and State Sharing

The `BookmarkService` uses the `__new__` method to implement the singleton pattern. This ensures that every time `BookmarkService()` is called—whether in `app/routes/bookmarks.py`, `app/routes/tags.py`, or `app/routes/collections.py`—the same instance is returned.

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

By instantiating the service at the module level in route files, the application maintains a single source of truth for the duration of the process:

```python
# app/routes/bookmarks.py
from app.services.bookmark_service import BookmarkService

bookmarks_bp = Blueprint("bookmarks", __name__)
_service = BookmarkService()
```

## Internal Component Bootstrapping

When the singleton instance is first created, it triggers the `_init_services` method. This method is responsible for bootstrapping the three core internal components that the service orchestrates:

1.  **`BookmarkRepository`**: The in-memory data store for all entities.
2.  **`LRUCache`**: A specialized cache for `Bookmark` objects.
3.  **`SearchIndex`**: The full-text search engine, which is initialized with a reference to the repository.

```python
def _init_services(self) -> None:
    """Bootstrap repository, cache, and search index."""
    self._repo = BookmarkRepository()
    self._cache: LRUCache[Bookmark] = LRUCache(max_size=256)
    self._search = SearchIndex(self._repo)
```

The service also provides a `_reset` method, primarily used in test suites to clear the in-memory state by re-running the initialization logic.

## Caching Strategy and Read-Through Logic

The application employs a **read-through caching** strategy for individual bookmark lookups. The `LRUCache` (defined in `app/services/_cache.py`) uses a `collections.OrderedDict` to track the least-recently-used items. When a bookmark is requested via `get_bookmark`, the service first checks the cache. If the item is missing, it retrieves it from the repository and populates the cache for future requests.

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

The `LRUCache` is configured with a `max_size` of 256. When this limit is reached, the `put` method automatically evicts the oldest entry:

```python
# app/services/_cache.py
def put(self, key: str, value: T) -> None:
    if key in self._store:
        self._store.move_to_end(key)
    self._store[key] = value
    if len(self._store) > self._max_size:
        self._store.popitem(last=False) # Evict oldest
```

## Cache Invalidation and Data Consistency

Because the `BookmarkService` is a facade over multiple components, it is responsible for maintaining consistency between the `BookmarkRepository` (the source of truth) and the `LRUCache`. 

The service performs **manual cache invalidation** on every mutation. Any operation that modifies a bookmark—such as creation, updating, archiving, or deleting—explicitly calls `self._cache.invalidate(id)`.

### Example: Updating a Bookmark
When a bookmark is updated, the service updates the repository, re-indexes the item for search, and removes the stale entry from the cache:

```python
def update_bookmark(self, bookmark_id: str, data: Dict[str, Any]) -> Tuple[Optional[Bookmark], Optional[str]]:
    # ... validation and repository update logic ...
    self._repo.save_bookmark(bookmark)
    self._search.index_bookmark(bookmark)
    self._cache.invalidate(bookmark.id) # Ensure next read is fresh
    return bookmark, None
```

### Cross-Entity Invalidation
The service also handles complex invalidations where a change to one entity affects others. For instance, when a `Tag` is deleted, the service must iterate through all bookmarks containing that tag, remove the tag reference, save the updated bookmark, and invalidate the cache for every affected bookmark:

```python
def delete_tag(self, tag_id: str) -> bool:
    tag = self._repo.get_tag(tag_id)
    if not tag:
        return False
    
    # Strip tag from all bookmarks and invalidate their cache entries
    for bookmark in self._repo.get_bookmarks_with_tag(tag_id):
        bookmark.remove_tag(tag_id)
        self._repo.save_bookmark(bookmark)
        self._cache.invalidate(bookmark.id)
        
    self._repo.delete_tag(tag_id)
    return True
```
