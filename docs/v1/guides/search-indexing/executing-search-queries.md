---
title: Executing Search Queries
description: How to use the search API to perform free-text searches, including details on token matching and result limits.
code_symbols: [SYM#b0cc1ddc5c9e6b6675ff73174df52949062c8da5]
section_id: 4c5c57bf-f938-4bae-bc58-b0a09ae20bda_executing_search_queries
doc_type: how_to
---

To perform free-text searches across bookmark titles and descriptions, use the `search` method provided by the `BookmarkService`. This service utilizes an in-memory inverted index to provide fast, token-based matching and relevance ranking.

### Searching via the Bookmark Service

The most direct way to execute a search is through the `BookmarkService` singleton. The service handles the interaction with the underlying `SearchIndex`.

```python
from app.services.bookmark_service import BookmarkService

service = BookmarkService()

# Search for bookmarks containing "python" and "tutorial"
# Returns a list of Bookmark objects
results = service.search(query="python tutorial", limit=10)

for bookmark in results:
    print(f"Found: {bookmark.title} ({bookmark.url})")
```

### Searching via the REST API

The search functionality is exposed via a `GET` request to the `/api/bookmarks/search` endpoint. This endpoint accepts a query string `q` and an optional `limit`.

```python
import requests

# Search via the API
response = requests.get(
    "http://localhost:5000/api/bookmarks/search",
    params={"q": "development tools", "limit": 5}
)

data = response.json()
print(f"Found {data['count']} results")
for result in data['results']:
    print(result['title'])
```

The route handler in `app/routes/bookmarks.py` delegates the request to the service:

```python
@bookmarks_bp.route("/search", methods=["GET"])
def search_bookmarks():
    query = request.args.get("q", "")
    limit = request.args.get("limit", 20, type=int)
    results = _service.search(query, limit=limit)
    return jsonify({"results": [b.to_dict() for b in results], "count": len(results)})
```

### How Search Logic Works

The `SearchIndex` class in `app.services.search_service` implements the following logic:

1.  **Tokenization**: The query and bookmark content (title + description) are converted to lowercase. Tokens are extracted using the regex `[a-z0-9]+`.
2.  **Stop Word Removal**: Common words defined in `_STOP_WORDS` (e.g., "the", "and", "is") are filtered out to improve result quality.
3.  **AND Matching**: The search uses an "AND" strategy. A bookmark must contain **all** non-stop-word tokens from the query to be included in the results.
4.  **Relevance Ranking**: Results are ranked by a score calculated in `_rank_results`. The score is the total number of times the query tokens appear in the bookmark's title and description.

```python
# Internal ranking logic in SearchIndex
def _rank_results(bookmarks: List[Bookmark], tokens: List[str]) -> List[Bookmark]:
    def score(b: Bookmark) -> int:
        text = f"{b.title} {b.description}".lower()
        return sum(text.count(t) for t in tokens)

    return sorted(bookmarks, key=score, reverse=True)
```

### Search Limits and Constraints

*   **Default Limit**: If no limit is specified, the `search` method defaults to **20** results.
*   **Internal Cap**: The system is designed for small datasets; the `SearchIndex` is entirely in-memory and is rebuilt from the `BookmarkRepository` every time the service initializes. Additionally, the `search` method enforces an internal maximum on the number of results returned, regardless of the `limit` parameter provided. This cap is defined by `MAX_SEARCH_RESULTS` in the source code.
*   **Incremental Updates**: The index is kept in sync automatically. When you call `service.create_bookmark()` or `service.update_bookmark()`, the `SearchIndex.index_bookmark()` method is called to refresh the tokens for that specific entry.

### Troubleshooting

*   **No Results for Common Words**: If your query consists only of stop words (like "the and or"), the `_tokenize` method will return an empty list, and the search will return no results.
*   **Partial Matches**: The search requires full token matches. Searching for "pyth" will not match a bookmark containing "python" because the tokens are generated based on alphanumeric boundaries.
*   **Case Sensitivity**: Search is case-insensitive as all tokens are lowercased during both indexing and querying.
