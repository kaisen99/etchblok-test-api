---
title: Searching for Bookmarks
description: Instructions on using the search API to query the index with free-text strings and handle ranked results.
code_symbols: [SYM#b0cc1ddc5c9e6b6675ff73174df52949062c8da5]
section_id: cb278b38-d86c-484c-8622-9101ddc73c9e_searching_for_bookmarks
doc_type: how_to
section_type: guide
---
To search for bookmarks by title or description, use the `BookmarkService.full_text_search` method or the `/api/bookmarks/search` endpoint. This system uses an in-memory inverted index that ranks results based on keyword frequency.

### Searching via the API

The most common way to search is via a `GET` request to the search endpoint.

```python
import requests

# Search for bookmarks containing "python" and "tutorial"
response = requests.get(
    "http://localhost:5000/api/bookmarks/search",
    params={"q": "python tutorial", "limit": 10}
)

results = response.json()
for bookmark in results["results"]:
    print(f"{bookmark['title']}: {bookmark['url']}")
```

The API route in `app/routes/bookmarks.py` delegates the query to the underlying service:

```python
@bookmarks_bp.route("/search", methods=["GET"])
def search_bookmarks():
    query = request.args.get("q", "")
    limit = request.args.get("limit", 20, type=int)
    results = _service.full_text_search(query, limit=limit)
    return jsonify({"results": [b.to_dict() for b in results], "count": len(results)})
```

### Searching via the Service

If you are working within the application code, use the `BookmarkService` singleton to perform searches.

```python
from app.services.bookmark_service import BookmarkService

service = BookmarkService()
# Returns a list of Bookmark model instances
results = service.full_text_search("machine learning", limit=5)

for bookmark in results:
    print(f"Found: {bookmark.title}")
```

### How Search Works

The search functionality is powered by the `SearchIndex` class in `app/services/search_service.py`. It implements a simple but effective full-text search:

1.  **Tokenization**: The query is split into lowercase tokens using the regex `[a-z0-9]+`.
2.  **Stop Word Filtering**: Common words like "the", "and", "is", and "for" are removed (defined in `_STOP_WORDS`).
3.  **AND Logic**: The search requires **all** non-stop-word tokens to be present in either the title or the description of the bookmark.
4.  **Ranking**: Results are ranked by the total number of times the query tokens appear in the combined title and description.

#### Example of Ranking Logic
The `_rank_results` method calculates a score based on token frequency:

```python
@staticmethod
def _rank_results(bookmarks: List[Bookmark], tokens: List[str]) -> List[Bookmark]:
    """Rank results by number of token occurrences in title + description."""
    def score(b: Bookmark) -> int:
        text = f"{b.title} {b.description}".lower()
        return sum(text.count(t) for t in tokens)

    return sorted(bookmarks, key=score, reverse=True)
```

### Index Maintenance

The `SearchIndex` is kept in sync automatically by the `BookmarkService`:
*   **Initialization**: When the service starts, `SearchIndex._rebuild()` loads up to 10,000 bookmarks from the `BookmarkRepository`.
*   **Updates**: Every time `create_bookmark` or `update_bookmark` is called, the service triggers `self._search.index_bookmark(bookmark)`, which refreshes the tokens for that specific ID.
*   **Deletions**: Currently, the index is updated incrementally during creation and updates.

### Troubleshooting

#### No results for common words
If you search for a query like "the", you will receive zero results. This is because "the" is a stop word and is filtered out before the index is queried.

#### Missing results in multi-word queries
Because the engine uses `AND` logic, a search for "Python Javascript" will only return bookmarks that contain **both** words. If a bookmark only contains "Python", it will be excluded from the results.

#### Search results are stale
The index is in-memory. If you modify the underlying database directly without going through the `BookmarkService`, the search index will not reflect those changes until the application is restarted. Always use `BookmarkService.update_bookmark` to ensure the index remains accurate.
