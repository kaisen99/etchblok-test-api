---
title: Implementing Full-Text Search
description: How to leverage the search index through the service orchestration layer to retrieve bookmarks.
code_symbols: [SYM#fdcfaed9972e477ae4585fd1b279ac107fa534cd]
section_id: 4b3d87d3-044d-451d-919d-80563d284a3c_implementing_full-text_search
doc_type: how_to
section_type: guide
---
To perform full-text searches across bookmarks in this project, you use the `BookmarkService` class. This service orchestrates an in-memory inverted index that allows for fast retrieval based on keywords found in bookmark titles and descriptions.

## Searching for Bookmarks

The most direct way to search is by calling the `full_text_search` method on the `BookmarkService` singleton.

```python
from app.services.bookmark_service import BookmarkService

# Get the singleton instance
service = BookmarkService()

# Search for bookmarks containing "python" and "tutorial"
# Results are ranked by token frequency
results = service.full_text_search(query="python tutorial", limit=10)

for bookmark in results:
    print(f"Found: {bookmark.title} ({bookmark.url})")
```

### How Search Works
The `BookmarkService` delegates search operations to an internal `SearchIndex` (found in `app/services/search_service.py`). 

1.  **Tokenization**: The query is split into lowercase tokens. Common stop words (e.g., "the", "and", "is") are filtered out using the `_STOP_WORDS` set in `search_service.py`.
2.  **AND Logic**: The search uses "AND" logic. A bookmark must contain **all** tokens from your query in either its title or description to be included in the results.
3.  **Ranking**: Results are ranked by the total number of times the query tokens appear in the bookmark's title and description combined.

## Exposing Search via API

The project includes a pre-configured Flask route in `app/routes/bookmarks.py` that exposes this functionality.

```python
from flask import Blueprint, request, jsonify
from app.services.bookmark_service import BookmarkService

bookmarks_bp = Blueprint("bookmarks", __name__)
_service = BookmarkService()

@bookmarks_bp.route("/search", methods=["GET"])
def search_bookmarks():
    """Full-text search across bookmark titles and descriptions."""
    query = request.args.get("q", "")
    limit = request.args.get("limit", 20, type=int)
    
    # Delegate to the service layer
    results = _service.full_text_search(query, limit=limit)
    
    return jsonify({
        "results": [b.to_dict() for b in results], 
        "count": len(results)
    })
```

## Automatic Indexing

You do not need to manually index bookmarks. The `BookmarkService` automatically updates the `SearchIndex` whenever a bookmark is created or modified.

### During Creation
When `create_bookmark` is called, the service persists the bookmark to the repository and immediately indexes it.

```python
# Inside BookmarkService.create_bookmark (app/services/bookmark_service.py)
bookmark = Bookmark.from_dict(data)
self._repo.save_bookmark(bookmark)
self._search.index_bookmark(bookmark) # Updates the inverted index
```

### During Updates
When `update_bookmark` is called, the service re-indexes the bookmark to ensure the search index reflects changes to the title or description.

```python
# Inside BookmarkService.update_bookmark (app/services/bookmark_service.py)
self._repo.save_bookmark(bookmark)
self._search.index_bookmark(bookmark) # Refreshes tokens in the index
```

## Troubleshooting and Limitations

### Trashed Bookmarks in Results
The `delete_bookmark` method in `BookmarkService` performs a "soft delete" by moving the bookmark to the trash. However, it does **not** currently remove the bookmark from the `SearchIndex`. 

```python
# app/services/bookmark_service.py
def delete_bookmark(self, bookmark_id: str) -> bool:
    bookmark = self._repo.get_bookmark(bookmark_id)
    if not bookmark:
        return False
    bookmark.trash() # Changes status to 'trashed'
    self._repo.save_bookmark(bookmark)
    # Note: self._search.remove_bookmark(bookmark_id) is NOT called here
    return True
```
Because the `SearchIndex` retrieves the full object from the repository during a search hit, trashed bookmarks will still appear in search results unless you manually filter them by checking `bookmark.status`.

### In-Memory Persistence
The search index is entirely in-memory. It is rebuilt from the `BookmarkRepository` every time the `BookmarkService` is initialized (e.g., on application startup).
- **Startup Delay**: For very large datasets, the initial crawl of the repository in `SearchIndex._rebuild()` may cause a delay.
- **Data Loss**: If the application crashes, the index is lost but will be safely reconstructed from the repository on the next start.

### Query Matching
If a search returns zero results, ensure that:
1.  The keywords are not in the `_STOP_WORDS` list in `app/services/search_service.py`.
2.  Every word in your query exists in either the `title` or `description` of the target bookmark. Partial word matches (substrings) are not supported; the index matches whole tokens.
