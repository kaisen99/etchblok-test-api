---
title: Executing Search Queries
description: Provides instructions on using the search method to find bookmarks based on free-text input.
code_symbols: [SYM#b0cc1ddc5c9e6b6675ff73174df52949062c8da5]
section_id: d730b3df-7695-4210-ba0c-52da3f139e1a_executing_search_queries
doc_type: how_to
section_type: guide
---
To find bookmarks based on free-text input in this project, you use the `SearchIndex` service, which is typically accessed through the `BookmarkService` facade. The search engine performs an "AND" search across bookmark titles and descriptions, ranking results by relevance.

### Searching via the Service Layer

The most common way to execute a search is using the `full_text_search` method on the `BookmarkService` singleton. This method delegates the query to the underlying `SearchIndex`.

```python
from app.services.bookmark_service import BookmarkService

# Get the service instance
service = BookmarkService()

# Search for bookmarks containing both "python" and "tutorial"
# Results are limited to 20 by default
results = service.full_text_search("python tutorial", limit=10)

for bookmark in results:
    print(f"Found: {bookmark.title} ({bookmark.url})")
```

### How the Search Logic Works

The `SearchIndex.search` method in `app/services/search_service.py` implements the following logic:

1.  **Tokenization**: The query string is split into lowercase tokens.
2.  **Stop Word Filtering**: Common words (e.g., "the", "and", "is") are removed to improve relevance.
3.  **AND Logic**: Only bookmarks that contain **all** non-stop-word tokens from the query are returned.
4.  **Ranking**: Results are ordered by the total number of times the query tokens appear in the bookmark's title and description combined.

```python
# Internal implementation detail from SearchIndex.search
def search(self, query: str, limit: int = 20) -> List[Bookmark]:
    tokens = self._tokenize(query)
    if not tokens:
        return []

    # Start with IDs matching the first token
    candidate_ids: Set[str] = self._index.get(tokens[0], set()).copy()
    
    # Intersect with IDs matching subsequent tokens (AND logic)
    for token in tokens[1:]:
        candidate_ids &= self._index.get(token, set())

    # ... ranking and returning results ...
```

### Searching via the API

The search functionality is exposed via the `/api/bookmarks/search` endpoint. This route accepts a query parameter `q` for the search string and an optional `limit`.

```python
# Example API Request
# GET /api/bookmarks/search?q=development+tools&limit=5

@bookmarks_bp.route("/search", methods=["GET"])
def search_bookmarks():
    query = request.args.get("q", "")
    limit = request.args.get("limit", 20, type=int)
    
    # Calls the service layer
    results = _service.full_text_search(query, limit=limit)
    
    return jsonify({
        "results": [b.to_dict() for b in results], 
        "count": len(results)
    })
```

### Automatic Index Maintenance

You do not need to manually update the search index when modifying bookmarks. The `BookmarkService` automatically synchronizes the `SearchIndex` during create and update operations:

*   **Creation**: `service.create_bookmark(data)` calls `self._search.index_bookmark(bookmark)`.
*   **Updates**: `service.update_bookmark(id, data)` re-indexes the bookmark to reflect changes in title or description.
*   **Initialization**: When the application starts, `SearchIndex` calls `_rebuild()` to load all existing bookmarks from the `BookmarkRepository` into the in-memory index.

### Troubleshooting and Limitations

*   **Stop Words**: If your search query consists only of stop words (e.g., searching for "the"), the search will return an empty list because the tokens are filtered out before the query is executed.
*   **In-Memory Index**: The `SearchIndex` is entirely in-memory. While it rebuilds from the database on startup, any direct database modifications made outside of the `BookmarkService` will not be reflected in search results until the service is restarted or the bookmark is updated via the service.
*   **Exact Token Matching**: The search matches whole tokens. Searching for "pyth" will not match a bookmark titled "Python" unless the tokenizer specifically splits it that way (which it currently does not; it uses a regex `\w+`).
