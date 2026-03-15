---
title: Updating the Search Index
description: Instructions on how to keep the search index synchronized by adding, updating, or removing bookmarks as they change in the repository.
code_symbols: [SYM#b0cc1ddc5c9e6b6675ff73174df52949062c8da5]
section_id: 6a7a481f-8cfd-47ae-a5c9-c7ff73c577e1_updating_the_search_index
doc_type: how_to
section_type: guide
---
To keep the search index synchronized with your bookmark repository, you must manually update the `SearchIndex` whenever a bookmark is created, modified, or deleted. In this project, the `BookmarkService` acts as the primary orchestrator for these updates.

## Synchronizing the Index in BookmarkService

The most common way to update the search index is by calling `index_bookmark` within the `BookmarkService` methods. This ensures that any changes to a bookmark's title or description are immediately reflected in search results.

```python
from app.services.bookmark_service import BookmarkService
from app.models.bookmark import Bookmark

service = BookmarkService()

# 1. Adding a new bookmark to the index
data = {"url": "https://example.com", "title": "Example Site", "description": "A useful site"}
bookmark, error = service.create_bookmark(data)
# Internally calls: self._search.index_bookmark(bookmark)

# 2. Updating an existing bookmark in the index
update_data = {"title": "Updated Example Site"}
updated_bookmark, error = service.update_bookmark(bookmark.id, update_data)
# Internally calls: self._search.index_bookmark(updated_bookmark)

# 3. Searching the updated index
results = service.search("Updated")
```

### Adding or Updating a Bookmark

The `SearchIndex.index_bookmark(bookmark)` method handles both new bookmarks and updates to existing ones. It first removes any existing entries for the bookmark's ID before re-tokenizing the title and description.

```python
# From app/services/search_service.py

def index_bookmark(self, bookmark: Bookmark) -> None:
    """Add or update a bookmark in the index."""
    # Remove old tokens first to prevent stale search results
    self._remove_bookmark_from_index(bookmark.id)
    
    # Tokenize title and description
    tokens = self._tokenize(f"{bookmark.title} {bookmark.description}")
    for token in tokens:
        self._index[token].add(bookmark.id)
```

### Removing a Bookmark

To completely remove a bookmark from the search results, use the `remove_bookmark(bookmark_id)` method. This is essential when a bookmark is permanently deleted from the repository.

```python
# From app/services/search_service.py

def remove_bookmark(self, bookmark_id: str) -> None:
    """Remove a bookmark from the index."""
    self._remove_bookmark_from_index(bookmark_id)
```

### Search Logic and Ranking

When you call `search(query)`, the `SearchIndex` applies an **AND** strategy. This means a bookmark must contain *all* tokens from the query to be returned. Results are then ranked by the frequency of those tokens in the bookmark's title and description.

```python
# Example of how search is performed internally
# From app/services/search_service.py

def search(self, query: str, limit: int = 20) -> List[Bookmark]:
    tokens = self._tokenize(query)
    if not tokens:
        return []

    # Start with IDs matching the first token
    candidate_ids: Set[str] = self._index.get(tokens[0], set()).copy()
    
    # Intersect with IDs matching subsequent tokens (AND logic)
    for token in tokens[1:]:
        candidate_ids &= self._index.get(token, set())

    # Retrieve and rank results
    results = []
    for bid in candidate_ids:
        bookmark = self._repo.get_bookmark(bid)
        if bookmark:
            results.append(bookmark)

    return self._rank_results(results, tokens)[:limit]
```

## Initialization and Rebuilding

The `SearchIndex` is an in-memory component. It automatically performs a full rebuild from the `BookmarkRepository` when the application starts or when the `BookmarkService` is initialized.

```python
# From app/services/search_service.py

def __init__(self, repository: "BookmarkRepository") -> None:
    self._repo = repository
    self._index: Dict[str, Set[str]] = defaultdict(set)
    self._rebuild()

def _rebuild(self) -> None:
    """Rebuild the entire index from the repository."""
    self._index.clear()
    # Fetches all bookmarks from the DB and indexes them
    all_bookmarks, _ = self._repo.list_bookmarks(page=1, per_page=10000)
    for bookmark in all_bookmarks:
        self.index_bookmark(bookmark)
```

## Troubleshooting

### Soft-Deleted Bookmarks Still Appear in Search
In the current implementation of `BookmarkService.delete_bookmark`, bookmarks are "trashed" (soft-deleted) but are **not** removed from the `SearchIndex`.

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
    # NOTE: self._search.remove_bookmark(bookmark_id) is NOT called here
    return True
```

If you need to exclude trashed bookmarks from search results immediately, you must manually call `service._search.remove_bookmark(bookmark_id)` or wait for an application restart to trigger a rebuild.

### Tokenization Limits
The indexer uses a simple regex `[a-z0-9]+` and removes common English stop words (e.g., "the", "and"). Special characters and non-alphanumeric symbols are ignored during indexing and searching.