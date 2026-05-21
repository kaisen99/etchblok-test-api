---
title: Service Layer Design and Singleton Pattern
description: An explanation of the architectural decisions behind using a Singleton facade to coordinate repositories, search indices, and caches.
code_symbols: [SYM#dd5fd545693e00d6c0b38892bbd18ed4afa136a1, SYM#fdcfaed9972e477ae4585fd1b279ac107fa534cd]
section_id: 595c3f26-7b96-48e8-88f1-74dec2bf01bf_service_layer_design_and_singleton_pattern
doc_type: explanation
---

The architecture of the **kaisen99-etchblok-test-api-f5f8018** codebase relies on a centralized service layer that acts as the brain of the application. At the heart of this layer is the `BookmarkService`, which implements a Singleton Facade pattern to coordinate data persistence, search indexing, and performance optimization.

## The Singleton Facade Pattern

The `BookmarkService` is designed as a Singleton to ensure that a single, consistent state is maintained across the entire application. Because this project uses in-memory storage, having multiple instances of the service would lead to fragmented data where different parts of the API see different versions of the "database."

The implementation in `app/services/bookmark_service.py` uses the `__new__` method to intercept instance creation:

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

This design allows Flask blueprints, such as those in `app/routes/bookmarks.py`, to simply instantiate the service locally while actually sharing the same underlying state:

```python
# app/routes/bookmarks.py
from app.services.bookmark_service import BookmarkService

bookmarks_bp = Blueprint("bookmarks", __name__)
_service = BookmarkService()  # Returns the shared global instance
```

## Orchestration of Sub-Services

The `BookmarkService` acts as a Facade, hiding the complexity of multiple internal components from the API routes. It coordinates three primary sub-services initialized in `_init_services`:

1.  **`BookmarkRepository`**: Handles the raw in-memory storage of bookmarks, tags, and collections.
2.  **`SearchIndex`**: Maintains an inverted index for full-text search capabilities.
3.  **`LRUCache`**: Provides a Least-Recently-Used cache to speed up frequent lookups.

### Request Lifecycle Coordination

When a write operation occurs, the service ensures all three components stay in sync. For example, the `create_bookmark` method performs a sequence of coordinated actions:

```python
def create_bookmark(self, data: Dict[str, Any]) -> Tuple[Optional[Bookmark], Optional[str]]:
    # 1. Validation
    error = _validate_url(data.get("url", "")) or _validate_title(data.get("title", ""))
    if error:
        return None, error

    # 2. Persistence
    bookmark = Bookmark.from_dict(data)
    self._repo.save_bookmark(bookmark)

    # 3. Search Indexing
    self._search.index_bookmark(bookmark)

    # 4. Cache Management
    self._cache.invalidate(bookmark.id)
    
    return bookmark, None
```

This orchestration ensures that a newly created bookmark is immediately searchable and that any stale cached data is removed.

## Design Tradeoffs and Constraints

The architectural choices in `BookmarkService` reflect specific tradeoffs between simplicity and performance:

*   **Manual Cache Invalidation**: The service is responsible for calling `self._cache.invalidate(id)` after every update. While this provides fine-grained control, it introduces a risk: if a developer adds a new update method but forgets to invalidate the cache, the API will serve stale data.
*   **In-Memory Lifecycle**: The Singleton pattern effectively manages state for the duration of the process, but because the `BookmarkRepository` is in-memory, all data is lost when the server restarts. The `BookmarkService` includes a `_reset()` method specifically for testing environments to clear this state between test runs.
