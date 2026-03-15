---
title: Search and Retrieval Strategies
description: A guide to listing and searching bookmarks, covering pagination, status filtering, and full-text search integration.
code_symbols: [SYM#fdcfaed9972e477ae4585fd1b279ac107fa534cd]
section_id: 553cce87-f329-40a5-b865-dee1d3ea3d42_search_and_retrieval_strategies
doc_type: guide
section_type: guide
---
The `BookmarkService` in `app/services/bookmark_service.py` serves as the central orchestration layer for all search and retrieval operations. It abstracts the complexities of interacting with the underlying in-memory repository, the full-text search index, and the performance-optimizing cache.

## Paginated Listing and Status Filtering

The primary method for retrieving multiple bookmarks is `list_bookmarks`. This method delegates the heavy lifting to the `BookmarkRepository` in `app/db/repository.py`, which implements pagination and filtering logic on the in-memory dataset.

### Pagination Logic
The repository calculates the slice of bookmarks to return based on the `page` and `per_page` parameters. It also returns the total count of matching items, which is essential for front-end pagination controls.

```python
# app/db/repository.py

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
            # Invalid status strings are silently ignored
            pass
    items.sort(key=lambda b: b.created_at, reverse=True)
    total = len(items)
    start = (page - 1) * per_page
    return items[start : start + per_page], total
```

### Status Filtering
Bookmarks in this system transition between three states defined in `app.models.bookmark.BookmarkStatus`: `active`, `archived`, and `trashed`. The `list_bookmarks` method allows filtering by these states. If an invalid status string is provided, the filter is ignored, and all bookmarks (regardless of status) are returned.

## Full-Text Search Integration

For free-text queries, the `BookmarkService` utilizes a dedicated `SearchIndex` (found in `app/services/search_service.py`). This is an in-memory inverted index that maps tokens to bookmark IDs.

### Tokenization and Matching
The `SearchIndex` processes both the bookmark metadata (title and description) and the search query using a simple regex-based tokenizer. It filters out common stop words (e.g., "the", "and", "is") to improve relevance.

The search implementation uses an **AND-based matching strategy**: a bookmark only appears in the results if it contains *all* tokens present in the search query.

```python
# app/services/search_service.py

def search(self, query: str, limit: int = 20) -> List[Bookmark]:
    tokens = self._tokenize(query)
    if not tokens:
        return []

    # Start with candidates matching the first token
    candidate_ids: Set[str] = self._index.get(tokens[0], set()).copy()
    
    # Intersect with candidates matching subsequent tokens (AND logic)
    for token in tokens[1:]:
        candidate_ids &= self._index.get(token, set())

    results = []
    for bid in candidate_ids:
        bookmark = self._repo.get_bookmark(bid)
        if bookmark:
            results.append(bookmark)

    return self._rank_results(results, tokens)[:limit]
```

### Relevance Ranking
Results are not returned in arbitrary order. The `_rank_results` method calculates a basic relevance score by counting the total occurrences of all query tokens within the bookmark's title and description.

## Direct Retrieval and Caching

When a specific bookmark is requested by its ID via `get_bookmark`, the `BookmarkService` employs an `LRUCache` (Least Recently Used) to minimize repository lookups.

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

The cache is automatically invalidated whenever a bookmark is updated, deleted, archived, or restored, ensuring that stale data is never served. For example, in `update_bookmark`:

```python
self._repo.save_bookmark(bookmark)
self._search.index_bookmark(bookmark) # Update search index
self._cache.invalidate(bookmark.id)    # Clear cache
```

## Retrieval Considerations

### Singleton State
The `BookmarkService` is implemented as a singleton. This ensures that the `LRUCache` and `SearchIndex` are shared across all request handlers in the application, maintaining a consistent view of the data.

### Index Lifecycle
The `SearchIndex` is rebuilt from the `BookmarkRepository` every time the `BookmarkService` is initialized. While efficient for the current in-memory implementation, this process involves scanning all bookmarks:

```python
# app/services/search_service.py

def _rebuild(self) -> None:
    """Rebuild the entire index from the repository."""
    self._index.clear()
    all_bookmarks, _ = self._repo.list_bookmarks(page=1, per_page=10000)
    for bookmark in all_bookmarks:
        self.index_bookmark(bookmark)
```

### Soft-Delete Impact
The `delete_bookmark` method performs a "soft-delete" by moving the bookmark to the `trashed` status. Because `list_bookmarks` returns all bookmarks by default if no status is specified, developers must explicitly filter for `status="active"` if they wish to exclude trashed or archived items from their results.

### Search Limits
While the `SearchIndex` has a hard limit of `MAX_SEARCH_RESULTS = 100`, the `BookmarkService.search` method defaults to returning only the top 20 results. This can be adjusted via the `limit` parameter in the API request.

```python
# app/routes/bookmarks.py

@bookmarks_bp.route("/search", methods=["GET"])
def search_bookmarks():
    query = request.args.get("q", "")
    limit = request.args.get("limit", 20, type=int)
    results = _service.search(query, limit=limit)
    return jsonify({"results": [b.to_dict() for b in results], "count": len(results)})
```