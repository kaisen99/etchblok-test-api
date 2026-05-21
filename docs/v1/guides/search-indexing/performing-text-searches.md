---
title: Performing Text Searches
description: How to use the search method to find bookmarks using free-text queries and limit result sets.
code_symbols: [SYM#b0cc1ddc5c9e6b6675ff73174df52949062c8da5]
section_id: 2e4a9fdc-e9ea-43b3-9baf-203e26b200b0_performing_text_searches
doc_type: how_to
---

To perform full-text searches across bookmarks in this project, use the `BookmarkService.search` method or the `/api/bookmarks/search` REST endpoint. The search system uses an in-memory inverted index (`SearchIndex`) that ranks results based on keyword frequency in titles and descriptions.

### Searching via the Service
The `BookmarkService` provides a high-level facade for searching. It delegates the query to the `SearchIndex` and returns a list of `Bookmark` objects.

```python
from app.services.bookmark_service import BookmarkService

service = BookmarkService()

# Search for bookmarks containing "python" and "tutorial"
# Results are ranked by how often these words appear in title/description
results = service.search(query="python tutorial", limit=10)

for bookmark in results:
    print(f"Found: {bookmark.title} ({bookmark.url})")
```

### Searching via the REST API
The search functionality is exposed via a `GET` request to the `/api/bookmarks/search` endpoint.

```bash
# Search for "recipes" with a limit of 5 results
curl "http://localhost:5000/api/bookmarks/search?q=recipes&limit=5"
```

The API implementation in `app/routes/bookmarks.py` handles the request as follows:

```python
@bookmarks_bp.route("/search", methods=["GET"])
def search_bookmarks():
    query = request.args.get("q", "")
    limit = request.args.get("limit", 20, type=int)
    results = _service.search(query, limit=limit)
    return jsonify({"results": [b.to_dict() for b in results], "count": len(results)})
```

### How Search Works
The `SearchIndex` class (found in `app/services/search_service.py`) manages the search logic using the following rules:

1.  **Tokenization**: Queries and bookmark content (title + description) are converted to lowercase and split into tokens using the regex `[a-z0-9]+`.
2.  **Stop Word Removal**: Common words that do not add search value are ignored. The following stop words are filtered out: `the`, `a`, `an`, `and`, `or`, `but`, `in`, `on`, `at`, `to`, `for`, `is`, `it`.
3.  **AND Logic**: The search uses an "AND" strategy. If you search for "python tutorial", a bookmark must contain **both** "python" and "tutorial" to be included in the results.
4.  **Ranking**: Results are ranked by a simple relevance score. The score is calculated by counting the total occurrences of all query tokens within the bookmark's title and description.

### Automatic Index Updates
You do not need to manually update the search index. The `BookmarkService` automatically keeps the `SearchIndex` in sync during standard operations:

*   **Creation**: `create_bookmark` calls `self._search.index_bookmark(bookmark)`.
*   **Updates**: `update_bookmark` re-indexes the bookmark whenever the title or description changes.
*   **Initialization**: When the application starts, `SearchIndex` performs a one-time rebuild by loading up to 10,000 bookmarks from the repository.

### Troubleshooting and Limitations

#### Missing Results for Common Words
If a search query consists entirely of stop words (e.g., searching for "the and"), the `search` method will return an empty list because all tokens were filtered out.

#### Fields Not Indexed
The search index only processes the `title` and `description` fields. Queries targeting the following fields will not return results:
*   URLs (e.g., searching for "github.com")
*   Tags (e.g., searching for a tag name like "work")
*   Collection names

#### Case Sensitivity
Search is entirely case-insensitive. Both the index and the queries are normalized to lowercase during the tokenization phase in `SearchIndex._tokenize`.

#### Result Limits
The default limit for search results is 20. While you can increase this via the `limit` parameter, the system enforces an absolute maximum number of results, and the `limit` parameter cannot exceed this internal maximum. The system is optimized for small to medium datasets as the index is stored entirely in memory.
