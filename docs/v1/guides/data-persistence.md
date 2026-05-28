---
title: Data Persistence
description: The repository layer responsible for in-memory storage and CRUD operations for all system entities.
code_symbols: [SYM#09a56e7acb86a9afef18a62134c27802cd473050]
section_id: a04dbb78-b377-4b71-82cd-c17807d04c81_data_persistence
doc_type: explanation
section_type: guide
---
The data persistence layer in this project is built around the **Repository Pattern**, providing a clean abstraction between the business logic and the underlying storage mechanism. This design allows the service layer to interact with domain entities without needing to know whether they are stored in memory, a local file, or a remote database.

### The Repository Abstraction

The central component of this layer is the `BookmarkRepository` class located in `app/db/repository.py`. It serves as the primary interface for all CRUD (Create, Read, Update, Delete) operations involving the system's core entities: Bookmarks, Tags, and Collections.

The repository is initialized within the `BookmarkService` and shared with other components like the `SearchIndex`:

```python
# From app/services/bookmark_service.py
def _init_services(self) -> None:
    """Bootstrap repository, cache, and search index."""
    self._repo = BookmarkRepository()
    self._cache: LRUCache[Bookmark] = LRUCache(max_size=256)
    self._search = SearchIndex(self._repo)
```

### In-Memory Storage Strategy

Currently, the system implements an in-memory storage strategy. Data is held in private dictionary attributes within the `BookmarkRepository` instance, keyed by the entity's unique ID.

```python
# From app/db/repository.py
class BookmarkRepository:
    def __init__(self) -> None:
        self._bookmarks: Dict[str, Bookmark] = {}
        self._tags: Dict[str, Tag] = {}
        self._collections: Dict[str, Collection] = {}
```

This approach offers high performance for read and write operations but introduces a significant constraint: **persistence is ephemeral**. All data is lost when the application process restarts. To mitigate this in a production environment, the repository would need to be swapped with a persistent implementation (e.g., using SQLAlchemy or a direct database driver).

### Querying and Pagination

Because the data is stored in memory, the repository performs querying and pagination by manipulating Python lists. The `list_bookmarks` method demonstrates how filtering by status and pagination are handled:

```python
# From app/db/repository.py
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

This implementation highlights a performance tradeoff: for every paginated request, the repository creates a full list of all bookmarks, sorts them, and then slices the result. While efficient for small datasets, this pattern would become a bottleneck as the number of bookmarks grows into the thousands or millions.

### Future-Proofing with Connection Stubs

Although the current repository is in-memory, the codebase includes a blueprint for future database integration in `app/db/_connection.py`. This module defines an internal `_ConnectionPool` and `_Connection` class, which simulate a thread-safe pool of database connections.

The `_ConnectionPool` is designed with standard database management features:
- **Pre-warming**: Initializing a minimum number of connections (`min_pool`).
- **Thread Safety**: Using `threading.Lock` to manage concurrent access to connections.
- **Transaction Support**: The `_Connection` class includes stubs for `begin_transaction`, `commit`, and `rollback`.

These classes are currently marked as internal (prefixed with underscores) and are not yet integrated into the `BookmarkRepository`, serving instead as a structural guide for future development.

### Design Tradeoffs: Hard vs. Soft Deletion

A notable design choice in this project is the separation of "hard" and "soft" deletion responsibilities between the repository and service layers.

1.  **Repository Layer**: The `BookmarkRepository.delete_bookmark` method performs a **hard delete**, physically removing the object from the internal dictionary.
    ```python
    # From app/db/repository.py
    def delete_bookmark(self, bookmark_id: str) -> bool:
        """Hard-delete a bookmark. Returns True if it existed."""
        return self._bookmarks.pop(bookmark_id, None) is not None
    ```

2.  **Service Layer**: The `BookmarkService.delete_bookmark` method implements a **soft delete**. Instead of calling the repository's delete method, it updates the bookmark's status to "trashed" and saves the change.
    ```python
    # From app/services/bookmark_service.py
    def delete_bookmark(self, bookmark_id: str) -> bool:
        """Soft-delete by trashing the bookmark."""
        bookmark = self._repo.get_bookmark(bookmark_id)
        if not bookmark:
            return False
        bookmark.trash()
        self._repo.save_bookmark(bookmark)
        self._cache.invalidate(bookmark_id)
        return True
    ```

This distinction allows the application to support "Trash" and "Restore" functionality at the business logic level while maintaining a simple, standard CRUD interface at the data access level.
