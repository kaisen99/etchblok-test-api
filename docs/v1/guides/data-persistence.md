---
title: Data Persistence
description: Details on the repository pattern and in-memory storage mechanisms for persisting application state.
code_symbols: [SYM#09a56e7acb86a9afef18a62134c27802cd473050]
section_id: 07463a1d-32b5-4154-8cd8-351147cd926b_data_persistence
doc_type: explanation
section_type: guide
---
Data persistence in this project is implemented using the **Repository Pattern**, which decouples the business logic from the underlying storage mechanism. While the current implementation relies on in-memory storage, the architecture is designed to support a transition to a persistent database with minimal changes to the service layer.

## The Repository Pattern

The `BookmarkRepository` class in `app/db/repository.py` serves as the single source of truth for data access. It provides a clean abstraction for CRUD operations on the core domain entities: `Bookmark`, `Tag`, and `Collection`.

By centralizing data access, the `BookmarkService` (located in `app/services/bookmark_service.py`) does not need to manage the specifics of how data is stored or retrieved. Instead, it interacts with the repository through high-level methods like `save_bookmark` or `list_bookmarks`.

```python
# app/db/repository.py

class BookmarkRepository:
    """In-memory storage for bookmarks, tags, and collections."""

    def __init__(self) -> None:
        self._bookmarks: Dict[str, Bookmark] = {}
        self._tags: Dict[str, Tag] = {}
        self._collections: Dict[str, Collection] = {}

    def save_bookmark(self, bookmark: Bookmark) -> None:
        """Insert or update a bookmark."""
        self._bookmarks[bookmark.id] = bookmark

    def get_bookmark(self, bookmark_id: str) -> Optional[Bookmark]:
        """Retrieve a bookmark by ID, or None."""
        return self._bookmarks.get(bookmark_id)
```

## In-Memory Storage Mechanism

The current persistence layer uses standard Python dictionaries (`dict`) to store entities in memory. This approach offers high performance for development and testing but introduces several constraints:

1.  **Volatility**: All data is lost when the application process restarts.
2.  **Manual Indexing**: Relationships between entities (e.g., which bookmarks have a specific tag) must be managed manually. For example, `get_bookmarks_with_tag` performs a linear scan over all bookmarks:
    ```python
    def get_bookmarks_with_tag(self, tag_id: str) -> List[Bookmark]:
        """Return all bookmarks that have a specific tag attached."""
        return [b for b in self._bookmarks.values() if tag_id in b.tags]
    ```
3.  **In-Memory Pagination**: Pagination logic in `list_bookmarks` involves slicing a list of all items in memory, which may become a performance bottleneck as the dataset grows.

## Entity State Management

Entities themselves are responsible for managing their internal state transitions, which are then persisted by the repository. The `Bookmark` dataclass in `app/models/bookmark.py` includes methods for archiving, trashing, and restoring bookmarks.

```python
# app/models/bookmark.py

@dataclass
class Bookmark:
    # ... fields ...
    status: BookmarkStatus = BookmarkStatus.ACTIVE

    def archive(self) -> None:
        """Move the bookmark to the archive."""
        self.status = BookmarkStatus.ARCHIVED
        self._touch()

    def trash(self) -> None:
        """Soft-delete the bookmark by moving it to the trash."""
        self.status = BookmarkStatus.TRASHED
        self._touch()
```

When the `BookmarkService` performs an operation like `delete_bookmark`, it retrieves the entity, invokes the state transition method, and then calls the repository to save the updated state.

## Future Persistence: Connection Stubs

The codebase includes an internal module `app/db/_connection.py` that defines a `_ConnectionPool` and `_Connection` class. These are currently stubs and are not utilized by the `BookmarkRepository`. However, they serve as a blueprint for integrating a SQL-based database (like PostgreSQL or SQLite) in the future.

The `_ConnectionPool` is designed to be thread-safe and manages a pool of reusable connections, demonstrating how the project intends to handle resource management in a production environment.

```python
# app/db/_connection.py

class _ConnectionPool:
    """Thread-safe pool of reusable database connections."""

    def __init__(self, config: Optional[_ConnectionConfig] = None) -> None:
        self._config = config or _ConnectionConfig()
        self._available: List[_Connection] = []
        self._in_use: List[_Connection] = []
        self._lock = threading.Lock()
        self.__init_pool()
```

## Tradeoffs and Design Decisions

The choice of an in-memory repository reflects a "design for change" philosophy. By implementing the Repository Pattern early, the developers have isolated the storage concerns. 

One notable tradeoff is the handling of cross-entity updates. For instance, when a `Tag` is deleted, the `BookmarkService` must manually iterate through all bookmarks associated with that tag to remove the reference. In a relational database, this could be handled via foreign key constraints or a join table, but in the current in-memory implementation, it is an $O(N)$ operation managed by the service layer:

```python
# app/services/bookmark_service.py

def delete_tag(self, tag_id: str) -> bool:
    """Delete a tag and strip it from all bookmarks."""
    tag = self._repo.get_tag(tag_id)
    if not tag:
        return False
    for bookmark in self._repo.get_bookmarks_with_tag(tag_id):
        bookmark.remove_tag(tag_id)
        self._repo.save_bookmark(bookmark)
        self._cache.invalidate(bookmark.id)
    self._repo.delete_tag(tag_id)
    return True
```

This design prioritizes architectural clarity and ease of testing over immediate persistence, providing a solid foundation for future scaling.