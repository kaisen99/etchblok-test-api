---
title: Repository Architecture
description: An overview of the in-memory data persistence layer and the design decisions behind using the Repository pattern for state management.
code_symbols: [SYM#09a56e7acb86a9afef18a62134c27802cd473050, SYM#adb8232356346a5957ff3a1a1b7ff70581f37649]
section_id: ec8a2bd6-f7f0-47dd-9574-09148852574f_repository_architecture
doc_type: explanation
section_type: guide
---
The **kaisen99-etchblok-test-api-a5c223b** project utilizes the Repository pattern to manage its data persistence layer. By abstracting the storage mechanism into a dedicated class, the application decouples business logic from the underlying data structure, facilitating easier testing and providing a clear path for future migration to a persistent database.

## Design Philosophy

The core of the persistence layer is the `BookmarkRepository` class located in `app/db/repository.py`. It serves as an in-memory data store, managing three primary entities: `Bookmark`, `Tag`, and `Collection`. 

The decision to use a Repository pattern here serves two main purposes:
1.  **Abstraction of Storage**: The service layer (specifically `BookmarkService`) interacts with high-level methods like `save_bookmark` or `list_bookmarks` without needing to know that the data is currently stored in Python dictionaries.
2.  **Centralized State**: It provides a single source of truth for the application's state, which is shared across different services, such as the search indexing logic.

## In-Memory Implementation

The repository implements persistence using standard Python dictionaries. This approach is highly performant for the current scope but introduces specific constraints, most notably that all data is volatile and lost when the application process restarts.

```python
class BookmarkRepository:
    def __init__(self) -> None:
        self._bookmarks: Dict[str, Bookmark] = {}
        self._tags: Dict[str, Tag] = {}
        self._collections: Dict[str, Collection] = {}
```

### Immediate Persistence and Transactions
Unlike a traditional database repository that might use a "Unit of Work" pattern or explicit transaction commits, `BookmarkRepository` mutations persist immediately. Methods like `save_bookmark` directly update the internal dictionary:

```python
def save_bookmark(self, bookmark: Bookmark) -> None:
    """Insert or update a bookmark."""
    self._bookmarks[bookmark.id] = bookmark
```

This design simplifies the implementation but means there is no built-in support for rolling back changes if a multi-step operation fails in the service layer.

## Querying and Pagination

The repository handles data retrieval through both direct ID lookups and collection-based queries. A notable implementation detail is the `list_bookmarks` method, which provides pagination and filtering by status.

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

### Tradeoffs in Querying
Because the data is in-memory, pagination is achieved by converting the entire dictionary of values into a list and then slicing it. While efficient for small to medium datasets, this approach would become a bottleneck if the dataset grew significantly, as it requires $O(N \log N)$ time for sorting and $O(N)$ space for the intermediate list on every request.

## Service Integration and Referential Integrity

The `BookmarkRepository` is a "dumb" storage layer; it does not enforce referential integrity or complex business rules. These responsibilities are delegated to the `BookmarkService` in `app/services/bookmark_service.py`.

For example, when a `Tag` is deleted, the repository provides the `get_bookmarks_with_tag` helper, but the service layer is responsible for iterating through those bookmarks and removing the tag reference before finally deleting the tag itself:

```python
# app/services/bookmark_service.py
def delete_tag(self, tag_id: str) -> bool:
    tag = self._repo.get_tag(tag_id)
    if not tag:
        return False
    # Service layer handles the "cascade" logic
    for bookmark in self._repo.get_bookmarks_with_tag(tag_id):
        bookmark.remove_tag(tag_id)
        self._repo.save_bookmark(bookmark)
        self._cache.invalidate(bookmark.id)
    self._repo.delete_tag(tag_id)
    return True
```

### Search Index Collaboration
The repository also supports the `SearchIndex` (found in `app/services/search_service.py`). The search index maintains an inverted mapping of tokens to IDs, but it relies on the repository to resolve those IDs back into full `Bookmark` objects during a search:

```python
# app/services/search_service.py
for bid in candidate_ids:
    bookmark = self._repo.get_bookmark(bid)
    if bookmark:
        results.append(bookmark)
```

## Hard vs. Soft Deletion

A key distinction in the architecture is how deletions are handled. The `BookmarkRepository` only implements "hard" deletes via the `pop` method:

```python
def delete_bookmark(self, bookmark_id: str) -> bool:
    """Hard-delete a bookmark. Returns True if it existed."""
    return self._bookmarks.pop(bookmark_id, None) is not None
```

However, the application's business logic (via `BookmarkService.delete_bookmark`) prefers "soft" deletes. It updates the bookmark's status to `trashed` and calls `save_bookmark` instead of `delete_bookmark`. This allows the repository to remain a generic CRUD interface while the service layer defines the specific lifecycle of the data.
