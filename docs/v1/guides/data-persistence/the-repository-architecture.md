---
title: The Repository Architecture
description: An overview of how the application handles data persistence using the repository pattern, focusing on the in-memory storage implementation.
code_symbols: [SYM#09a56e7acb86a9afef18a62134c27802cd473050, SYM#adb8232356346a5957ff3a1a1b7ff70581f37649]
section_id: 22d8e7aa-4b8a-49c1-b31c-4ec58b290383_the_repository_architecture
doc_type: guide
section_type: guide
---
The application employs the Repository Pattern to abstract data persistence, primarily through the `BookmarkRepository` class located in `app/db/repository.py`. This architecture decouples the core business logic from the underlying storage implementation, allowing the rest of the system to interact with data entities without concern for whether they are stored in memory, a relational database, or a document store.

## In-Memory Storage Implementation

Currently, the `BookmarkRepository` implements an in-memory storage solution using standard Python dictionaries. This approach provides high performance for development and testing but means that all data is volatile and will be lost when the application process restarts.

The repository maintains three primary internal stores:

```python
class BookmarkRepository:
    def __init__(self) -> None:
        self._bookmarks: Dict[str, Bookmark] = {}
        self._tags: Dict[str, Tag] = {}
        self._collections: Dict[str, Collection] = {}
```

These dictionaries use the entity IDs as keys, ensuring $O(1)$ lookup time for individual items.

## Core Data Entities

The repository manages three main domain models defined in the `app.models` package:

*   **Bookmark**: The central entity representing a saved URL, metadata, and associated tags.
*   **Tag**: Metadata labels that can be attached to multiple bookmarks.
*   **Collection**: Logical groupings for organizing bookmarks.

## Data Access and Persistence

The repository provides a consistent interface for CRUD (Create, Read, Update, Delete) operations across all three entity types.

### Mutation and Retrieval
Methods like `save_bookmark`, `save_tag`, and `save_collection` handle both insertion and updates. Because the storage is in-memory, these mutations are effective immediately.

```python
def save_bookmark(self, bookmark: Bookmark) -> None:
    """Insert or update a bookmark."""
    self._bookmarks[bookmark.id] = bookmark

def get_bookmark(self, bookmark_id: str) -> Optional[Bookmark]:
    """Retrieve a bookmark by ID, or None."""
    return self._bookmarks.get(bookmark_id)
```

### Hard vs. Soft Deletion
A critical distinction in this architecture is how deletions are handled. The `BookmarkRepository` performs **hard deletes**, physically removing the object from its internal dictionaries:

```python
def delete_bookmark(self, bookmark_id: str) -> bool:
    """Hard-delete a bookmark. Returns True if it existed."""
    return self._bookmarks.pop(bookmark_id, None) is not None
```

In contrast, the higher-level `BookmarkService` often implements **soft deletes** by updating a bookmark's status to `BookmarkStatus.TRASHED` instead of calling the repository's delete method.

## Advanced Querying and Pagination

The repository handles complex retrieval logic, including filtering and pagination, which keeps the service layer focused on business rules.

### Paginated Listing
The `list_bookmarks` method is the primary way to retrieve sets of bookmarks. It supports:
1.  **Status Filtering**: Filtering by `active`, `archived`, or `trashed` using the `BookmarkStatus` enum.
2.  **Sorting**: Items are automatically sorted by `created_at` in descending order.
3.  **Pagination**: Returns a specific slice of data based on `page` and `per_page` parameters.

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
The repository also provides specialized methods for cross-entity lookups, such as `get_bookmarks_with_tag(tag_id)`, which performs a linear scan of the bookmarks to find those containing a specific tag ID.

## Integration in the Application

The `BookmarkRepository` is a foundational component used by several key services:

### BookmarkService
The `BookmarkService` (found in `app/services/bookmark_service.py`) acts as a singleton that initializes and owns the repository instance. It delegates most data operations directly to the repository.

```python
def _init_services(self) -> None:
    """Bootstrap repository, cache, and search index."""
    self._repo = BookmarkRepository()
    # ... other initializations
```

### SearchIndex
The `SearchIndex` (found in `app/services/search_service.py`) depends on the repository to build and maintain its inverted index. During initialization, it uses the repository to retrieve all existing bookmarks for indexing:

```python
def _rebuild(self) -> None:
    """Rebuild the entire index from the repository."""
    self._index.clear()
    all_bookmarks, _ = self._repo.list_bookmarks(page=1, per_page=10000)
    for bookmark in all_bookmarks:
        self.index_bookmark(bookmark)
```

## Architectural Constraints

*   **No Transaction Support**: As an in-memory implementation, the repository does not support transactions or rollbacks. If a complex operation fails halfway through, previous mutations remain in the dictionaries.
*   **Thread Safety**: The current implementation does not include explicit locking mechanisms for concurrent access to the internal dictionaries.
*   **Scalability**: Methods like `list_bookmarks` and `get_bookmarks_with_tag` involve full list copies or scans, which are efficient for small to medium datasets but would require indexing in a production database implementation.