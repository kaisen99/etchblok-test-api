---
title: Performing and Filtering Searches
description: How to execute free-text queries, handle tokenization, and limit search results using the SearchIndex API.
code_symbols: [SYM#b0cc1ddc5c9e6b6675ff73174df52949062c8da5]
section_id: 687c0bfd-68fa-4710-86a9-ba5996b60d85_performing_and_filtering_searches
doc_type: how_to
section_type: guide
---
To perform free-text searches across bookmark titles and descriptions, use the `SearchIndex` class. This service maintains an in-memory inverted index that allows for fast retrieval and relevance-based ranking.

### Executing a Free-Text Search

You can execute a search by calling the `search` method with a query string. The results are returned as a list of `Bookmark` objects, ranked by how many times the query tokens appear in their title and description.

```python
from app.services.search_service import SearchIndex
from app.db.repository import BookmarkRepository

# Initialize with a repository
repo = BookmarkRepository()
search_index = SearchIndex(repo)

# Perform a search with a limit
results = search_index.search(query="python tutorial", limit=10)

for bookmark in results:
    print(f"Found: {bookmark.title}")
```

In the standard application flow, this is typically accessed via the `BookmarkService` or the `/search` API endpoint:

```python
# From app/routes/bookmarks.py
@bookmarks_bp.route("/search", methods=["GET"])
def search_bookmarks():
    query = request.args.get("q", "")
    limit = request.args.get("limit", 20, type=int)
    
    # _service is an instance of BookmarkService which wraps SearchIndex
    results = _service.search(query, limit=limit)
    
    return jsonify({
        "results": [b.to_dict() for b in results], 
        "count": len(results)
    })
```

### How Tokenization and Ranking Work

The `SearchIndex` processes both the indexed content and the search queries using a specific tokenization pipeline defined in `app/services/search_service.py`:

1.  **Normalization**: Text is converted to lowercase.
2.  **Regex Splitting**: The `_TOKEN_RE` (`[a-z0-9]+`) extracts alphanumeric words.
3.  **Stop Word Filtering**: Common words defined in `_STOP_WORDS` (e.g., "the", "and", "is") are removed to improve result quality.

When you perform a search, the engine applies **AND-logic**: a bookmark must contain *all* non-stop-word tokens from your query to be included in the results.

Results are then ranked using the `_rank_results` static method, which calculates a score based on the total count of token occurrences in the combined title and description:

```python
@staticmethod
def _rank_results(bookmarks: List[Bookmark], tokens: List[str]) -> List[Bookmark]:
    """Rank results by number of token occurrences in title + description."""
    def score(b: Bookmark) -> int:
        text = f"{b.title} {b.description}".lower()
        return sum(text.count(t) for t in tokens)

    return sorted(bookmarks, key=score, reverse=True)
```

### Incrementally Updating the Index

The index is automatically rebuilt from the repository when `SearchIndex` is initialized. However, to keep the index current without a full rebuild, you must update it incrementally when bookmarks change.

#### Adding or Updating a Bookmark
Use `index_bookmark` to add a new entry or refresh an existing one. The method automatically removes the old version of the bookmark ID from all token sets before re-indexing.

```python
# From app/services/bookmark_service.py
def create_bookmark(self, data: Dict[str, Any]) -> Tuple[Optional[Bookmark], Optional[str]]:
    bookmark = Bookmark.from_dict(data)
    self._repo.save_bookmark(bookmark)
    
    # Update the search index immediately
    self._search.index_bookmark(bookmark)
    
    return bookmark, None
```

#### Removing a Bookmark
Use `remove_bookmark` to purge a bookmark ID from the inverted index.

```python
def delete_bookmark(self, bookmark_id: str) -> bool:
    if self._repo.delete_bookmark(bookmark_id):
        # Clean up the index
        self._search.remove_bookmark(bookmark_id)
        return True
    return False
```

### Filtering and Result Limits

The `search` method accepts a `limit` parameter to control the size of the result set. If not provided, it defaults to 20. 

Note that the module also defines a `MAX_SEARCH_RESULTS = 100` constant, though the `search` method itself respects the `limit` passed to it. When the index is initially built or rebuilt, it fetches up to 10,000 bookmarks from the repository:

```python
def _rebuild(self) -> None:
    """Rebuild the entire index from the repository."""
    self._index.clear()
    # Fetches a large batch to populate the in-memory index
    all_bookmarks, _ = self._repo.list_bookmarks(page=1, per_page=10000)
    for bookmark in all_bookmarks:
        self.index_bookmark(bookmark)
```

### Troubleshooting and Limitations

*   **In-Memory Only**: The index is stored in RAM. If the application restarts, the index is rebuilt from the `BookmarkRepository`. It is not designed for extremely large datasets that exceed available memory.
*   **Strict AND Matching**: If your query is "Python Javascript", only bookmarks containing *both* words will appear. If you get zero results, try a broader single-word query.
*   **Stop Words**: Queries consisting only of stop words (e.g., searching for "the and") will return an empty list because `_tokenize` will filter out all tokens.
*   **Field Coverage**: The index only scans `title` and `description`. It does not currently index tags or the URL string itself.
