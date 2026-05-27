---
title: Persistence Layer
description: In-memory data storage and repository patterns for managing the persistence of bookmarks, tags, and collections.
code_symbols: [SYM#09a56e7acb86a9afef18a62134c27802cd473050]
section_id: 25da6f7b-9c8f-4915-abcf-d0b1c862dc8a_persistence_layer
doc_type: guide
section_type: guide
---
The persistence layer in this project is built around an in-memory repository pattern, designed to provide a clean abstraction over data storage. While the current implementation resides entirely in memory, the architecture is structured to allow for future transitions to persistent databases like SQLite or PostgreSQL without altering the service layer logic.

## The Repository Pattern

The central hub for data access is the `BookmarkRepository` class located in `app/db/repository.py`. It acts as a mediator between the domain models and the underlying storage mechanism.

### In-Memory Storage
The repository maintains three primary collections using Python dictionaries, where keys are unique identifiers (UUIDs) and values are the domain model instances:

```python
class BookmarkRepository:
    def __init__(self) -> None:
        self._bookmarks: Dict[str, Bookmark] = {}
        self._tags: Dict[str, Tag] = {}
        self._collections: Dict[str, Collection] = {}
```

### CRUD Operations
The repository provides standard CRUD methods for each entity. These methods perform immediate mutations on the internal dictionaries. For example, the bookmark operations are implemented as follows:

```python
def save_bookmark(self, bookmark: Bookmark) -> None:
    """Insert or update a bookmark."""
    self._bookmarks[bookmark.id] = bookmark

def get_bookmark(self, bookmark_id: str) -> Optional[Bookmark]:
    """Retrieve a bookmark by ID, or None."""
    return self._bookmarks.get(bookmark_id)

def delete_bookmark(self, bookmark_id: str) -> bool:
    """Hard-delete a bookmark. Returns True if it existed."""
    return self._bookmarks.pop(bookmark_id, None) is not None
```

## Domain Models and Serialization

Persistence is managed using three core domain entities found in the `app/models/` directory. Each model is implemented as a Python `dataclass` and includes methods for serialization to and from dictionaries, facilitating both storage and API communication.

### Core Entities
- **Bookmark (`app/models/bookmark.py`)**: Represents a saved URL with metadata, status (Active, Archived, Trashed), and a list of associated tag IDs.
- **Tag (`app/models/tag.py`)**: Represents a label with a name and color. It tracks its own `usage_count` across bookmarks.
- **Collection (`app/models/collection.py`)**: Groups bookmarks. It supports **Manual** collections (explicit ID lists) and **Smart** collections (dynamic filtering based on a `filter_rule`).

### Serialization Example
The `Bookmark` model uses `to_dict` for serialization and a class method `from_dict` for instantiation from raw data:

```python
def to_dict(self) -> Dict[str, Any]:
    return {
        "id": self.id,
        "url": self.url,
        "title": self.title,
        "tags": self.tags,
        "status": self.status.value,
        "created_at": self.created_at.isoformat(),
        # ... other fields
    }
```

## Search and Indexing

To support full-text search without a traditional database, the project implements a `SearchIndex` in `app/services/search_service.py`. This is an inverted index that maps tokens (words) to bookmark IDs.

The index is initialized by scanning the repository and is updated incrementally whenever bookmarks are saved or removed:

```python
class SearchIndex:
    def __init__(self, repository: "BookmarkRepository") -> None:
        self._repo = repository
        self._index: Dict[str, Set[str]] = defaultdict(set)
        self._rebuild()

    def index_bookmark(self, bookmark: Bookmark) -> None:
        self._remove_bookmark_from_index(bookmark.id)
        tokens = self._tokenize(f"{bookmark.title} {bookmark.description}")
        for token in tokens:
            self._index[token].add(bookmark.id)
```

## Caching Layer

Performance for frequent lookups is optimized using an `LRUCache` (Least-Recently-Used) found in `app/services/_cache.py`. The `BookmarkService` uses this cache to store `Bookmark` objects, reducing the need to query the repository directly for repeated requests.

The cache is automatically invalidated when a bookmark is updated or deleted to ensure data consistency:

```python
# app/services/bookmark_service.py
def update_bookmark(self, bookmark_id: str, data: dict) -> Optional[Bookmark]:
    bookmark = self._repo.get_bookmark(bookmark_id)
    if bookmark:
        # ... update logic ...
        self._repo.save_bookmark(bookmark)
        self._cache.put(bookmark.id, bookmark)  # Update cache
        self._search.index_bookmark(bookmark)   # Update search index
    return bookmark
```

## Data Integrity and Lifecycle

Because the repository is in-memory and lacks built-in relational constraints, the `BookmarkService` in `app/services/bookmark_service.py` is responsible for maintaining data integrity across different entities.

For instance, when a `Tag` is deleted, the service layer must iterate through all associated bookmarks to remove the tag reference and update the cache:

```python
def delete_tag(self, tag_id: str) -> bool:
    tag = self._repo.get_tag(tag_id)
    if not tag:
        return False
    # Clean up references in bookmarks
    for bookmark in self._repo.get_bookmarks_with_tag(tag_id):
        bookmark.remove_tag(tag_id)
        self._repo.save_bookmark(bookmark)
        self._cache.invalidate(bookmark.id)
    self._repo.delete_tag(tag_id)
    return True
```

## Limitations and Considerations

- **Volatility**: All data is stored in volatile memory. Restarting the application process results in the loss of all bookmarks, tags, and collections.
- **No Transactions**: The `BookmarkRepository` does not support atomic transactions. If a multi-step operation (like the tag deletion shown above) fails midway, the data may be left in an inconsistent state.
- **Scaling**: The `SearchIndex` is rebuilt entirely on startup, which may impact initialization time as the number of bookmarks grows.
