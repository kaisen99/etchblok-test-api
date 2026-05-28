---
title: Service Orchestration
description: The central business logic layer that coordinates operations between repositories, search indices, and caching mechanisms.
code_symbols: [SYM#dd5fd545693e00d6c0b38892bbd18ed4afa136a1]
section_id: 3a01591d-4db9-41d6-a73c-f7cc6c6fb300_service_orchestration
doc_type: guide
section_type: guide
---
The service orchestration layer in this application is centered around the `BookmarkService` class. It acts as a **Facade** that coordinates business logic across the data repository, an in-memory search index, and a least-recently-used (LRU) cache.

## The BookmarkService Orchestrator

The `BookmarkService` (found in `app/services/bookmark_service.py`) is implemented as a Singleton to ensure that stateful components like the search index and cache are shared across all request handlers. It is the primary entry point for all business operations, abstracting the underlying complexity of data persistence and performance optimizations from the route handlers.

### Core Dependencies

When initialized, the `BookmarkService` bootstraps three internal components:

1.  **`BookmarkRepository`**: Handles low-level data persistence.
2.  **`LRUCache`**: A fixed-capacity cache (default 256 entries) used to speed up individual bookmark lookups.
3.  **`SearchIndex`**: An in-memory inverted index that provides full-text search capabilities.

```python
# app/services/bookmark_service.py

def _init_services(self) -> None:
    """Bootstrap repository, cache, and search index."""
    self._repo = BookmarkRepository()
    self._cache: LRUCache[Bookmark] = LRUCache(max_size=256)
    self._search = SearchIndex(self._repo)
```

## Coordination of Operations

The service ensures consistency across its components by orchestrating updates. For example, when a bookmark is created or updated, the service must update the repository, refresh the search index, and invalidate any stale cache entries.

### Example: Creating a Bookmark

The `create_bookmark` method demonstrates this orchestration. It first performs validation using internal validators (like `_validate_url`), then persists the entity, and finally updates the auxiliary systems.

```python
# app/services/bookmark_service.py

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

    # 4. Cache Invalidation
    self._cache.invalidate(bookmark.id)
    
    return bookmark, None
```

### Example: Cached Retrieval

For read operations, the service implements a "cache-aside" pattern. It attempts to retrieve the bookmark from the `LRUCache` before falling back to the `BookmarkRepository`.

```python
# app/services/bookmark_service.py

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

## Cross-Entity Orchestration

One of the primary roles of the `BookmarkService` is managing complex operations that span multiple entities. A key example is `delete_tag`, which must not only remove the tag itself but also strip it from every bookmark that references it.

```python
# app/services/bookmark_service.py

def delete_tag(self, tag_id: str) -> bool:
    """Delete a tag and strip it from all bookmarks."""
    tag = self._repo.get_tag(tag_id)
    if not tag:
        return False
    
    # Cascade: Update all bookmarks containing this tag
    for bookmark in self._repo.get_bookmarks_with_tag(tag_id):
        bookmark.remove_tag(tag_id)
        self._repo.save_bookmark(bookmark)
        self._cache.invalidate(bookmark.id)
        
    self._repo.delete_tag(tag_id)
    return True
```

## Search Index Lifecycle

The `SearchIndex` (in `app/services/search_service.py`) is an in-memory component that is automatically rebuilt from the repository during the service's initialization. This ensures that the search functionality is available immediately upon application startup, though it may introduce a slight delay as the dataset grows.

The service delegates search queries directly to this index:

```python
# app/services/bookmark_service.py

def search(self, query: str, limit: int = 20) -> List[Bookmark]:
    """Full-text search across bookmarks."""
    return self._search.search(query, limit=limit)
```

## Error Handling Pattern

The service layer adopts a consistent error handling pattern by returning a `Tuple[Optional[Entity], Optional[str]]`. This allows route handlers to easily distinguish between a successful operation, a validation error, and a "not found" state.

In `app/routes/bookmarks.py`, this pattern is used to return appropriate HTTP status codes:

```python
@bookmarks_bp.route("/", methods=["POST"])
def create_bookmark():
    data = request.get_json(force=True)
    bookmark, error = _service.create_bookmark(data)
    if error:
        # Validation error
        return jsonify({"error": error}), 400
    return jsonify(bookmark.to_dict()), 201
```

This separation of concerns ensures that the route handlers remain thin, focusing only on HTTP request/response processing, while the `BookmarkService` manages the integrity and performance of the business logic.
