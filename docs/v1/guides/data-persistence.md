---
title: Data Persistence
description: In-memory storage and repository patterns for managing entity lifecycles.
code_symbols: [SYM#09a56e7acb86a9afef18a62134c27802cd473050]
section_id: d31dfeb9-376c-4541-b490-51147aaf5703_data_persistence
doc_type: explanation
section_type: guide
---
Data persistence in this project is implemented using an in-memory repository pattern, providing a clean abstraction that decouples the core business logic from the underlying storage mechanism. While the current implementation is volatile, the architecture is designed to transition to a persistent database with minimal changes to the service layer.

## The Repository Pattern

The `BookmarkRepository` class in `app/db/repository.py` serves as the centralized data access layer. It manages the lifecycle of three primary entities: `Bookmark`, `Tag`, and `Collection`. By encapsulating all storage operations within this class, the rest of the application remains agnostic of whether data is stored in memory or a relational database.

The repository uses internal dictionaries to store entities by their unique identifiers:

```python
class BookmarkRepository:
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

Beyond simple CRUD operations, the repository implements basic filtering and pagination logic. For example, `list_bookmarks` handles status-based filtering and pagination in-memory:

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

## Domain Entities and Serialization

The system relies on three core domain models defined in `app/models/`: `Bookmark`, `Tag`, and `Collection`. These are implemented as Python dataclasses, which simplifies state management and provides built-in support for equality and representation.

To facilitate integration with the Flask API layer and the repository, each model implements `to_dict` and `from_dict` methods. This pattern ensures that serialization logic remains within the domain entity rather than leaking into the service or controller layers.

For instance, the `Bookmark` entity in `app/models/bookmark.py` manages its own state transitions (like archiving or trashing) and serialization:

```python
@dataclass
class Bookmark:
    url: str
    title: str
    # ... other fields
    status: BookmarkStatus = BookmarkStatus.ACTIVE

    def archive(self) -> None:
        self.status = BookmarkStatus.ARCHIVED
        self._touch()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "url": self.url,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            # ...
        }
```

## Service Layer Orchestration

The `BookmarkService` in `app/services/bookmark_service.py` acts as a facade over the repository. It is responsible for orchestrating data persistence with other cross-cutting concerns such as caching and search indexing. 

When a bookmark is created or updated, the service ensures it is saved to the repository, added to the `SearchIndex`, and that any relevant entries in the `LRUCache` are invalidated:

```python
def create_bookmark(self, data: Dict[str, Any]) -> Tuple[Optional[Bookmark], Optional[str]]:
    # ... validation logic ...
    bookmark = Bookmark.from_dict(data)
    self._repo.save_bookmark(bookmark)
    self._search.index_bookmark(bookmark)
    self._cache.invalidate(bookmark.id)
    return bookmark, None
```

This orchestration ensures that the repository remains a "dumb" data store while the service layer manages the complex interactions between different system components.

## Architectural Future-Proofing

Although the current implementation is in-memory, the codebase includes a thread-safe connection pool stub in `app/db/_connection.py`. This `_ConnectionPool` class demonstrates how the system is prepared for a real database integration. It manages a pool of `_Connection` objects, supporting operations like `acquire`, `release`, and basic transaction management.

```python
class _ConnectionPool:
    def __init__(self, config: Optional[_ConnectionConfig] = None) -> None:
        self._config = config or _ConnectionConfig()
        self._available: List[_Connection] = []
        self._in_use: List[_Connection] = []
        self._lock = threading.Lock()
        self.__init_pool()

    def acquire(self) -> _Connection:
        with self._lock:
            # ... logic to borrow or create a connection ...
```

The presence of this pool, along with the repository abstraction, allows the application to scale to a persistent backend (like PostgreSQL or SQLite) by simply swapping the `BookmarkRepository` implementation without modifying the `BookmarkService`.

## Trade-offs and Constraints

The current in-memory approach involves several design trade-offs:

*   **Volatility**: All data is lost when the application process restarts. This is suitable for testing and demonstration but requires a persistent implementation for production use.
*   **Lack of Transactions**: While the `_Connection` stub includes `begin_transaction` and `commit` methods, the `BookmarkRepository` currently lacks atomic multi-entity updates. For example, deleting a tag requires iterating through bookmarks and updating them individually, which is not currently wrapped in a transaction.
*   **Performance of Smart Collections**: Smart collections in `app/models/collection.py` evaluate filter rules by iterating over the entire bookmark set in-memory. As the dataset grows, this O(n) operation may become a bottleneck compared to indexed database queries.
*   **Search Index Initialization**: The `SearchIndex` is rebuilt from the repository every time the `BookmarkService` is initialized. In a large-scale system, this would be replaced by a persistent search engine like Elasticsearch or a database-backed full-text search.
