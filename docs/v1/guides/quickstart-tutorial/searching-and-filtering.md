---
title: Searching and Filtering
description: Explore the full-text search capabilities and pagination features to efficiently find and list bookmarks.
code_symbols: [SYM#fdcfaed9972e477ae4585fd1b279ac107fa534cd]
section_id: 4f4c5861-9833-4bc3-8fe9-9fdfdf121267_searching_and_filtering
doc_type: guide
section_type: guide
---
The **kaisen99-etchblok-test-api-dcf99cc** project provides two primary ways to locate bookmarks: structured paginated listing with status filtering, and unstructured full-text search. These capabilities are orchestrated by the `BookmarkService` in `app/services/bookmark_service.py`, which coordinates between the data repository and an in-memory search index.

## Paginated Listing and Status Filtering

The `list_bookmarks` method in `BookmarkService` provides the standard way to browse bookmarks. It delegates the heavy lifting to the `BookmarkRepository` (`app/db/repository.py`), which implements pagination and status-based filtering.

### Implementation in BookmarkRepository
The repository maintains an in-memory collection of bookmarks and applies filters before slicing the results for pagination.

```python
def list_bookmarks(
    self,
    page: int = 1,
    per_page: int = 25,
    status: Optional[str] = None,
) -> Tuple[List[Bookmark], int]:
    items = list(self._bookmarks.values())
    
    # Status Filtering
    if status:
        try:
            target = BookmarkStatus(status)
            items = [b for b in items if b.status == target]
        except ValueError:
            # Invalid status strings are silently ignored
            pass
            
    # Sorting and Pagination
    items.sort(key=lambda b: b.created_at, reverse=True)
    total = len(items)
    start = (page - 1) * per_page
    return items[start : start + per_page], total
```

Key characteristics of this implementation:
- **1-Based Pagination**: The `page` parameter starts at 1.
- **Default Sorting**: Results are always returned in reverse chronological order (`created_at`).
- **Status Validation**: The `status` filter expects values corresponding to the `BookmarkStatus` enum (e.g., "active", "archived", "trashed"). If an invalid string is provided, the filter is ignored.

## Full-Text Search

For keyword-based discovery, the project implements a custom in-memory inverted index via the `SearchIndex` class in `app/services/search_service.py`.

### The Inverted Index
The `SearchIndex` maps individual tokens (words) to sets of bookmark IDs. This allows for near-instant lookups regardless of the number of bookmarks, as long as the index fits in memory.

```python
class SearchIndex:
    def __init__(self, repository: "BookmarkRepository") -> None:
        self._repo = repository
        self._index: Dict[str, Set[str]] = defaultdict(set)
        self._rebuild()
```

### Tokenization and Ranking
When a bookmark is indexed (via `index_bookmark`), the system combines the `title` and `description`, converts them to lowercase, and extracts alphanumeric tokens. Common "stop words" (like "the", "and", "is") are excluded to improve result quality.

The `search` method follows an **AND-based logic**:
1. It tokenizes the search query.
2. It finds the intersection of bookmark IDs for all tokens in the query.
3. It ranks the resulting bookmarks using `_rank_results`, which calculates a score based on how many times the query tokens appear in the bookmark's title and description.

```python
def search(self, query: str, limit: int = 20) -> List[Bookmark]:
    tokens = self._tokenize(query)
    if not tokens:
        return []

    # Intersection of all token sets (AND logic)
    candidate_ids: Set[str] = self._index.get(tokens[0], set()).copy()
    for token in tokens[1:]:
        candidate_ids &= self._index.get(token, set())

    results = [self._repo.get_bookmark(bid) for bid in candidate_ids if self._repo.get_bookmark(bid)]
    return self._rank_results(results, tokens)[:limit]
```

## Service Integration

The `BookmarkService` ensures that the search index remains synchronized with the underlying data. Whenever a bookmark is created or updated, the service automatically triggers a re-indexing operation.

```python
def create_bookmark(self, data: Dict[str, Any]) -> Tuple[Optional[Bookmark], Optional[str]]:
    # ... validation ...
    bookmark = Bookmark.from_dict(data)
    self._repo.save_bookmark(bookmark)
    self._search.index_bookmark(bookmark) # Update search index
    self._cache.invalidate(bookmark.id)
    return bookmark, None
```

## API Exposure

These features are exposed through the Flask blueprint in `app/routes/bookmarks.py`. The routes translate URL query parameters into the arguments required by the `BookmarkService`.

### Listing Example
The `GET /bookmarks/` endpoint handles pagination and status:
```python
@bookmarks_bp.route("/", methods=["GET"])
def list_bookmarks():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 25, type=int)
    status = request.args.get("status", None)
    bookmarks, total = _service.list_bookmarks(page=page, per_page=per_page, status=status)
    return jsonify({"bookmarks": [b.to_dict() for b in bookmarks], "total": total})
```

### Search Example
The `GET /bookmarks/search` endpoint handles full-text queries:
```python
@bookmarks_bp.route("/search", methods=["GET"])
def search_bookmarks():
    query = request.args.get("q", "")
    limit = request.args.get("limit", 20, type=int)
    results = _service.full_text_search(query, limit=limit)
    return jsonify({"results": [b.to_dict() for b in results], "count": len(results)})
```

Note that while the standard listing supports pagination, the `full_text_search` currently only supports a `limit` parameter and returns the top matches in a single response.
