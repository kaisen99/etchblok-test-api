---
title: Repository Architecture
description: An overview of the in-memory persistence strategy and the centralized repository pattern used to manage application data.
code_symbols: [SYM#09a56e7acb86a9afef18a62134c27802cd473050, SYM#adb8232356346a5957ff3a1a1b7ff70581f37649]
section_id: 445a1ed2-51ad-4748-8083-b01f722ea152_repository_architecture
doc_type: guide
section_type: guide
---
The repository architecture in this project centers around the `BookmarkRepository` class, which serves as a centralized, in-memory data store. It implements the Repository pattern to decouple the application's business logic from the underlying persistence mechanism, providing a consistent interface for managing bookmarks, tags, and collections.

## Centralized Data Management

The `BookmarkRepository` (located in `app/db/repository.py`) acts as the single source of truth for the application's state. It manages three primary entity types using Python dictionaries for high-performance, in-memory lookups:

*   **Bookmarks**: Stored in `self._bookmarks: Dict[str, Bookmark]`
*   **Tags**: Stored in `self._tags: Dict[str, Tag]`
*   **Collections**: Stored in `self._collections: Dict[str, Collection]`

Because the storage is in-memory, all mutation methods (like `save_bookmark` or `delete_tag`) persist changes immediately to these dictionaries. However, this also means that data is volatile and will be lost if the application process restarts.

## Core Repository Operations

The repository provides standard CRUD operations for all three entities, along with specialized methods for filtering and pagination.

### Bookmark Retrieval and Pagination
The `list_bookmarks` method implements the core logic for browsing the bookmark library. It supports:
*   **Pagination**: Uses `page` and `per_page` parameters (defaulting to 25 items per page).
*   **Status Filtering**: Allows filtering by `BookmarkStatus` (e.g., "active", "archived", "trashed").
*   **Sorting**: Automatically sorts results by `created_at` in descending order.

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

### Relationship Queries
The repository also handles simple relationship queries, such as `get_bookmarks_with_tag(tag_id)`, which performs a linear scan of the bookmarks to find those containing the specified tag ID.

## Integration and Data Flow

The `BookmarkRepository` is a foundational dependency used by higher-level services.

### Service Layer Integration
The `BookmarkService` (in `app/services/bookmark_service.py`) initializes the repository during its own bootstrap process. It treats the repository as a long-lived dependency that it calls for every data operation.

```python
# app/services/bookmark_service.py

def _init_services(self) -> None:
    """Bootstrap repository, cache, and search index."""
    self._repo = BookmarkRepository()
    self._cache: LRUCache[Bookmark] = LRUCache(max_size=256)
    self._search = SearchIndex(self._repo)
```

### Search Index Synchronization
The `SearchIndex` (in `app/services/search_service.py`) relies on the repository for two critical functions:
1.  **Initial Rebuild**: On startup, the `SearchIndex` calls `self._repo.list_bookmarks` to populate its inverted index from the existing data.
2.  **ID Resolution**: When a search is performed, the index identifies matching bookmark IDs and then uses `self._repo.get_bookmark(bid)` to resolve those IDs into full `Bookmark` objects for the final result list.

```python
# app/services/search_service.py

def search(self, query: str, limit: int = 20) -> List[Bookmark]:
    # ... tokenization and ID lookup ...
    results = []
    for bid in candidate_ids:
        bookmark = self._repo.get_bookmark(bid)
        if bookmark:
            results.append(bookmark)
    return self._rank_results(results, tokens)[:limit]
```

## Operational Considerations

### Transactional Integrity
The current implementation does not support transactions or rollbacks. If a complex operation fails halfway through (e.g., updating a bookmark but failing to update its associated tags), the repository may be left in a partially updated state.

### Testing Support
The repository includes a `_clear_all()` method specifically for testing environments. This allows tests to wipe the state between runs without re-instantiating the entire service stack.

```python
def _clear_all(self) -> None:
    """Wipe all data. Test use only."""
    self._bookmarks.clear()
    self._tags.clear()
    self._collections.clear()
```

### Diagnostics
For monitoring and debugging, the `_count_all()` method provides a quick snapshot of the current entity counts across all three storage dictionaries.
