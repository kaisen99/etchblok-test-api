---
title: Search and Discovery
description: A guide to the full-text search capabilities and how the service leverages the search index for title and description queries.
code_symbols: [SYM#fdcfaed9972e477ae4585fd1b279ac107fa534cd]
section_id: a3323d05-267f-4dd3-bd9a-d08f7f83558d_search_and_discovery
doc_type: guide
---

The `BookmarkService` acts as the primary interface for search and discovery within the application. It leverages an internal `SearchIndex` to provide full-text search capabilities across bookmark titles and descriptions, ensuring that users can find content efficiently.

## The Search Indexing Lifecycle

The search index is an in-memory inverted index that maps specific tokens (words) to bookmark IDs. This index is managed automatically by the `BookmarkService` during the lifecycle of a bookmark.

### Automatic Indexing
When a bookmark is created or updated through the service, it is automatically synchronized with the search index. This ensures that the search results are always up-to-date with the latest content in the repository.

```python
# From app/services/bookmark_service.py
def create_bookmark(self, data: Dict[str, Any]) -> Tuple[Optional[Bookmark], Optional[str]]:
    # ... validation and persistence ...
    bookmark = Bookmark.from_dict(data)
    self._repo.save_bookmark(bookmark)
    
    # The service ensures the search index is updated immediately
    self._search.index_bookmark(bookmark)
    
    self._cache.invalidate(bookmark.id)
    return bookmark, None
```

### Index Rebuilding
Because the `SearchIndex` is an in-memory structure, it is rebuilt from the `BookmarkRepository` whenever the `BookmarkService` is initialized. This typically happens once during the application startup because the service is implemented as a singleton.

```python
# From app/services/search_service.py
def _rebuild(self) -> None:
    """Rebuild the entire index from the repository."""
    self._index.clear()
    all_bookmarks, _ = self._repo.list_bookmarks(page=1, per_page=10000)
    for bookmark in all_bookmarks:
        self.index_bookmark(bookmark)
```

## Search Logic and Tokenization

The search implementation in `SearchIndex` (found in `app/services/search_service.py`) uses a specific set of rules to process queries and index content.

### Tokenization and Filtering
Text from titles and descriptions is converted to lowercase and split into alphanumeric tokens using the regex `[a-z0-9]+`. To improve search quality, common "stop words" (e.g., "the", "and", "is") are filtered out and ignored.

### AND-based Matching
Search queries are restrictive. If a user searches for multiple terms, the engine finds bookmarks that contain **all** of those terms. This is implemented using set intersection of the bookmark IDs associated with each token.

```python
# From app/services/search_service.py
def search(self, query: str, limit: int = 20) -> List[Bookmark]:
    tokens = self._tokenize(query)
    if not tokens:
        return []

    # Start with candidates for the first token
    candidate_ids: Set[str] = self._index.get(tokens[0], set()).copy()
    
    # Intersect with candidates for subsequent tokens (AND logic)
    for token in tokens[1:]:
        candidate_ids &= self._index.get(token, set())
    
    # ... retrieval and ranking ...
```

## Ranking and Relevance

Results are not returned in arbitrary order. The `SearchIndex` ranks matches based on the frequency of the search tokens within the bookmark's title and description. The `_rank_results` method calculates a score for each candidate bookmark to ensure the most relevant results appear first.

```python
# From app/services/search_service.py
@staticmethod
def _rank_results(bookmarks: List[Bookmark], tokens: List[str]) -> List[Bookmark]:
    """Rank results by number of token occurrences in title + description."""
    def score(b: Bookmark) -> int:
        text = f"{b.title} {b.description}".lower()
        return sum(text.count(t) for t in tokens)

    return sorted(bookmarks, key=score, reverse=True)
```

## API Integration

The search capability is exposed via the `/bookmarks/search` endpoint. The route handler in `app/routes/bookmarks.py` demonstrates how the API layer interfaces with the `BookmarkService` to perform a search.

```python
# From app/routes/bookmarks.py
@bookmarks_bp.route("/search", methods=["GET"])
def search_bookmarks():
    """Full-text search across bookmark titles and descriptions."""
    query = request.args.get("q", "")
    limit = request.args.get("limit", 20, type=int)
    
    # The service handles the interaction with the SearchIndex
    results = _service.search(query, limit=limit)
    
    return jsonify({
        "results": [b.to_dict() for b in results],
        "count": len(results)
    })
```

## Implementation Details

*   **Singleton Pattern**: `BookmarkService` uses a singleton pattern (`__new__`) to ensure that the same `SearchIndex` instance is shared across all Flask blueprints, maintaining a consistent search state throughout the application lifecycle.
*   **In-Memory Performance**: The `SearchIndex` is entirely in-memory, providing high performance for queries. However, this means the index is lost if the application restarts and must be rebuilt from the repository.
*   **Synchronous Updates**: Indexing is performed synchronously during bookmark creation and updates. This ensures immediate consistency for search results after a write operation.
