---
title: In-Memory Storage Design
description: A discussion on the design choices behind the in-memory storage implementation and considerations for future database integration.
code_symbols: [SYM#09a56e7acb86a9afef18a62134c27802cd473050, SYM#adb8232356346a5957ff3a1a1b7ff70581f37649]
section_id: f3fd40cc-3d49-432b-b9a6-68f0f2675472_in-memory_storage_design
doc_type: explanation
section_type: guide
---
The **kaisen99-etchblok-test-api-7ee56a2** codebase utilizes a Repository pattern to decouple business logic from data persistence. At the heart of this design is the `BookmarkRepository` class, which currently implements an in-memory storage engine. This approach serves as a high-performance, volatile data store that mimics the behavior of a persistent database while providing a clear path for future migration to a relational system like PostgreSQL.

## Data Access Abstraction

The `BookmarkRepository` (found in `app/db/repository.py`) acts as a clean abstraction layer. By isolating data access within this class, the rest of the application—specifically the `BookmarkService`—remains agnostic to the underlying storage mechanism. 

The repository manages three primary entities:
- **Bookmarks**: Stored in `self._bookmarks`
- **Tags**: Stored in `self._tags`
- **Collections**: Stored in `self._collections`

Each of these is implemented as a Python dictionary where the key is the entity's unique ID (a string) and the value is the model instance.

```python
class BookmarkRepository:
    def __init__(self) -> None:
        self._bookmarks: Dict[str, Bookmark] = {}
        self._tags: Dict[str, Tag] = {}
        self._collections: Dict[str, Collection] = {}
```

## Immediate Persistence and Transactionality

In its current in-memory form, the repository follows an "immediate persistence" model. Because operations on Python dictionaries are synchronous and local to the process, methods like `save_bookmark` or `delete_tag` update the state instantly.

However, the implementation acknowledges the limitations of this design. A comment in the `BookmarkRepository` docstring notes: *"For a real database you'd add transaction support here."* 

Evidence of planned transaction support can be found in the internal `app/db/_connection.py` module, which defines a `_Connection` class with methods for managing transaction depth:

```python
class _Connection:
    def begin_transaction(self) -> None:
        """Start a new transaction (supports nesting via savepoints)."""
        self._transaction_depth += 1

    def commit(self) -> None:
        """Commit the current transaction."""
        if self._transaction_depth > 0:
            self._transaction_depth -= 1
```

While the `BookmarkRepository` does not yet utilize this `_ConnectionPool`, the infrastructure for connection management and transaction nesting is already architected.

## Query Logic and Pagination

The repository is responsible for more than just simple CRUD; it also implements the application's filtering and pagination logic. The `list_bookmarks` method demonstrates how the in-memory store handles complex queries that would typically be offloaded to SQL.

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

This implementation highlights a significant tradeoff: **performance vs. scale**. While in-memory sorting and slicing are extremely fast for small datasets, they require loading all bookmarks into memory and performing an $O(N \log N)$ sort on every request. In a persistent database implementation, this logic would be replaced by `ORDER BY`, `LIMIT`, and `OFFSET` clauses in a SQL query.

## Cross-Entity Integrity

The repository design also handles relationships between entities, though it relies on the service layer to maintain referential integrity. For example, when a tag is deleted, the `BookmarkService` must coordinate with the repository to update all affected bookmarks.

In `app/services/bookmark_service.py`, the `delete_tag` method illustrates this interaction:

```python
def delete_tag(self, tag_id: str) -> bool:
    """Delete a tag and strip it from all bookmarks."""
    tag = self._repo.get_tag(tag_id)
    if not tag:
        return False
    # Update all bookmarks that used this tag
    for bookmark in self._repo.get_bookmarks_with_tag(tag_id):
        bookmark.remove_tag(tag_id)
        self._repo.save_bookmark(bookmark)
    self._repo.delete_tag(tag_id)
    return True
```

The repository provides the specialized `get_bookmarks_with_tag` helper to facilitate these cross-entity operations efficiently within the in-memory constraints.

## Design Tradeoffs and Future Considerations

The current in-memory storage design involves several deliberate tradeoffs:

1.  **Volatility**: Data is lost whenever the application process restarts. This is acceptable for the current testing/development phase but necessitates the transition to the `_ConnectionPool` logic defined in `app/db/_connection.py` for production use.
2.  **Memory Usage**: As the number of bookmarks grows, the memory footprint of the application increases linearly. 
3.  **Concurrency**: The current implementation does not use locks for dictionary access. While Python's Global Interpreter Lock (GIL) provides some protection for basic operations, a multi-threaded environment would require the thread-safe mechanisms seen in `_ConnectionPool._lock`.

The presence of `_ConnectionConfig` with default values for `host`, `port`, and `database` ("pagemark") indicates that the project is prepared to switch to a persistent backend with minimal changes to the `BookmarkService` logic.