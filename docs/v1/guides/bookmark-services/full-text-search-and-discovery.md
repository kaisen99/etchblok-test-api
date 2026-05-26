---
title: Full-Text Search and Discovery
description: Explains how to utilize the search index to perform full-text queries across bookmark titles and descriptions.
code_symbols: [SYM#fdcfaed9972e477ae4585fd1b279ac107fa534cd]
section_id: 3e175b94-1c2c-4e8a-9407-006429b1ab96_full-text_search_and_discovery
doc_type: guide
section_type: guide
---
The search functionality in this project provides full-text discovery across bookmark titles and descriptions. It is implemented using an in-memory inverted index that prioritizes speed and simplicity for small-to-medium datasets.

## The Search Facade

The `BookmarkService` class in `app/services/bookmark_service.py` serves as the primary interface for search operations. It abstracts the underlying search engine logic from the rest of the application.

The core method for discovery is `full_text_search`:

```python
def full_text_search(self, query: str, limit: int = 20) -> List[Bookmark]:
    """Full-text search across bookmark titles and descriptions."""
    return self._search.search(query, limit=limit)
```

This method delegates the actual query execution to the `SearchIndex` instance, which is initialized as part of the service's internal bootstrap process (`_init_services`).

## In-Memory Indexing Logic

The search engine is powered by the `SearchIndex` class located in `app/services/search_service.py`. It maintains an inverted index—a dictionary mapping specific tokens (words) to sets of bookmark IDs.

### Tokenization and Filtering
When a bookmark is indexed or a search query is processed, the text is passed through the `_tokenize` method:

1.  **Normalization**: Text is converted to lowercase.
2.  **Extraction**: Tokens are extracted using the regex `[a-z0-9]+`.
3.  **Stop Word Removal**: Common words like "the", "and", and "is" (defined in `_STOP_WORDS`) are filtered out to improve result relevance.

### Matching Strategy
The search implementation uses **AND logic**. For a bookmark to appear in the results, it must contain *all* the non-stop-word tokens provided in the search query.

```python
# From SearchIndex.search in app/services/search_service.py
candidate_ids: Set[str] = self._index.get(tokens[0], set()).copy()
for token in tokens[1:]:
    candidate_ids &= self._index.get(token, set())
```

### Ranking and Relevance
Results are not returned in arbitrary order. The `_rank_results` method calculates a relevance score for each match based on the frequency of the search tokens within the bookmark's title and description:

```python
@staticmethod
def _rank_results(bookmarks: List[Bookmark], tokens: List[str]) -> List[Bookmark]:
    """Rank results by number of token occurrences in title + description."""
    def score(b: Bookmark) -> int:
        text = f"{b.title} {b.description}".lower()
        return sum(text.count(t) for t in tokens)

    return sorted(bookmarks, key=score, reverse=True)
```

## Index Lifecycle and Persistence

The search index is strictly in-memory and its lifecycle is tied to the application process.

### Initialization
When `BookmarkService` starts, the `SearchIndex` performs a full rebuild by fetching all existing bookmarks from the `BookmarkRepository`:

```python
def _rebuild(self) -> None:
    """Rebuild the entire index from the repository."""
    self._index.clear()
    all_bookmarks, _ = self._repo.list_bookmarks(page=1, per_page=10000)
    for bookmark in all_bookmarks:
        self.index_bookmark(bookmark)
```

### Incremental Updates
To ensure the index remains fresh without requiring a full rebuild, `BookmarkService` triggers incremental updates during mutation operations:

*   **Creation**: `create_bookmark` calls `self._search.index_bookmark(bookmark)` after persisting to the database.
*   **Updates**: `update_bookmark` re-indexes the bookmark whenever its metadata changes.

### Important Limitation: Soft Deletes
In this codebase, `delete_bookmark` performs a "soft-delete" by moving the bookmark to the trash (calling `bookmark.trash()`). Currently, `BookmarkService.delete_bookmark` does **not** remove the bookmark from the `SearchIndex`. Consequently, trashed bookmarks may still appear in search results until the application is restarted or the index is explicitly cleared.

## API Integration

The search capability is exposed via the `/api/bookmarks/search` endpoint in `app/routes/bookmarks.py`. It accepts a query string `q` and an optional `limit`.

```python
@bookmarks_bp.route("/search", methods=["GET"])
def search_bookmarks():
    query = request.args.get("q", "")
    limit = request.args.get("limit", 20, type=int)
    results = _service.full_text_search(query, limit=limit)
    return jsonify({"results": [b.to_dict() for b in results], "count": len(results)})
```

This endpoint allows clients to perform real-time discovery across the entire bookmark library using the relevance-ranked results provided by the `SearchIndex`.
