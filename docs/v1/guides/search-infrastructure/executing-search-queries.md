---
title: Executing Search Queries
description: How to use the SearchIndex API to perform full-text searches with automatic tokenization and result ranking.
code_symbols: [SYM#b0cc1ddc5c9e6b6675ff73174df52949062c8da5]
section_id: 90756a1b-297b-4f7b-b394-1190f68ce15d_executing_search_queries
doc_type: how_to
---

To perform full-text searches across bookmark titles and descriptions, use the `SearchIndex` API. This service provides an in-memory inverted index that automatically tokenizes content, filters stop words, and ranks results by relevance.

### Performing a Search
The most common way to execute a search is through the `BookmarkService` facade, which manages the `SearchIndex` instance.

```python
from app.services.bookmark_service import BookmarkService

# Initialize the service (singleton)
service = BookmarkService()

# Search for bookmarks containing "python" and "tutorial"
# Results are ranked by the frequency of these tokens in title + description
results = service.full_text_search("python tutorial", limit=10)

for bookmark in results:
    print(f"Found: {bookmark.title} (ID: {bookmark.id})")
```

### How Search Works
The `SearchIndex` class (found in `app/services/search_service.py`) implements the search logic using the following steps:

1.  **Tokenization**: The query string is converted to lowercase and split into alphanumeric tokens using the regex `[a-z0-9]+`.
2.  **Stop Word Removal**: Common words defined in `_STOP_WORDS` (e.g., "the", "and", "is") are removed from the query.
3.  **AND Logic**: The search requires **all** query tokens to be present in a bookmark for it to be considered a match.
4.  **Ranking**: Results are ranked by the total number of times the query tokens appear in the bookmark's title and description combined.

### Incremental Indexing
The index is kept up-to-date automatically when you use `BookmarkService` to create or update bookmarks. If you are working directly with the `SearchIndex` class, you must manually index or remove items.

```python
from app.services.search_service import SearchIndex
from app.db.repository import BookmarkRepository
from app.models.bookmark import Bookmark

repo = BookmarkRepository()
search_index = SearchIndex(repo)

# Manually index a new bookmark
new_bookmark = Bookmark(
    url="https://example.com",
    title="Advanced Python Tips",
    description="A guide to advanced python programming."
)
search_index.index_bookmark(new_bookmark)

# Remove a bookmark from the index
search_index.remove_bookmark(new_bookmark.id)
```

### Integration in API Routes
The search functionality is exposed via the `/api/bookmarks/search` endpoint. The route handler demonstrates how to handle query parameters and limit results.

```python
# From app/routes/bookmarks.py
@bookmarks_bp.route("/search", methods=["GET"])
def search_bookmarks():
    query = request.args.get("q", "")
    limit = request.args.get("limit", 20, type=int)
    
    # Delegates to BookmarkService.full_text_search
    results = _service.full_text_search(query, limit=limit)
    
    return jsonify({
        "results": [b.to_dict() for b in results], 
        "count": len(results)
    })
```

### Troubleshooting and Limitations

*   **No Results for Stop Words**: If a search query consists entirely of stop words (e.g., searching for "the and"), the `_tokenize` method will return an empty list, and the search will return no results.
*   **Strict AND Matching**: If you search for "Python Java", only bookmarks containing **both** words will be returned. There is currently no support for "OR" queries.
*   **In-Memory Rebuilds**: The index is stored entirely in memory and is rebuilt from the `BookmarkRepository` every time the application starts (via the `_rebuild` method in `SearchIndex`). For very large datasets, this may cause a delay during service initialization.
*   **Maximum Search Results**: The `limit` parameter in search queries is capped by a system-defined maximum number of results, even if a higher limit is requested.
*   **Case Insensitivity**: All indexing and searching are case-insensitive as the `_tokenize` method calls `.lower()` on all input text.
