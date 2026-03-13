---
title: Search & Discovery
description: Full-text search capabilities and inverted indexing for efficient retrieval of bookmarked content.
code_symbols: [SYM#0f269a750bc62c4d874086090a88d14329456024]
section_id: 317e49f1-d86e-46b5-b53e-64d4524493c4_search___discovery
doc_type: explanation
section_type: guide
---
The search and discovery system in this project provides full-text search capabilities across bookmarked content. It is implemented as an in-memory inverted index, designed for high-performance retrieval within the constraints of a small-to-medium dataset.

## The Inverted Index

The core of the search functionality resides in the `SearchIndex` class within `app/services/search_service.py`. This class maintains a mapping of individual words (tokens) to the IDs of bookmarks that contain them.

The index is implemented using a `defaultdict(set)`, where each key is a search token and the value is a set of bookmark IDs:

```python
# app/services/search_service.py

class SearchIndex:
    def __init__(self, repository: "BookmarkRepository") -> None:
        self._repo = repository
        self._index: Dict[str, Set[str]] = defaultdict(set)
        self._rebuild()
```

By using a set of IDs for each token, the system can perform extremely fast lookups and combine results using set operations.

## Tokenization and Processing

Before text is added to the index or used for a query, it undergoes a tokenization process. The `_tokenize` method ensures that search is case-insensitive and ignores common "stop words" that would otherwise bloat the index without adding semantic value.

The system uses a regular expression `[a-z0-9]+` to extract alphanumeric tokens and filters them against a predefined set of stop words:

```python
# app/services/search_service.py

_STOP_WORDS: Set[str] = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "is", "it"}
_TOKEN_RE = re.compile(r"[a-z0-9]+")

def _tokenize(self, text: str) -> List[str]:
    """Split text into lowercase tokens, removing stop words."""
    tokens = _TOKEN_RE.findall(text.lower())
    return [t for t in tokens if t not in _STOP_WORDS]
```

Currently, the indexer only processes the `title` and `description` fields of a bookmark. Tags and URLs are not included in the full-text index.

## Retrieval and Ranking

The search implementation follows an **AND-based matching strategy**. For a bookmark to appear in the results, it must contain *all* tokens present in the search query. This is achieved through set intersection:

```python
# app/services/search_service.py

def search(self, query: str, limit: int = 20) -> List[Bookmark]:
    tokens = self._tokenize(query)
    if not tokens:
        return []

    # Start with the set of IDs for the first token
    candidate_ids: Set[str] = self._index.get(tokens[0], set()).copy()
    
    # Intersect with sets for all subsequent tokens
    for token in tokens[1:]:
        candidate_ids &= self._index.get(token, set())

    # ... retrieval and ranking ...
```

Once matching candidates are identified, they are ranked using a simple frequency-based algorithm. The `_rank_results` method calculates a score based on how many times the query tokens appear in the combined title and description:

```python
# app/services/search_service.py

@staticmethod
def _rank_results(bookmarks: List[Bookmark], tokens: List[str]) -> List[Bookmark]:
    """Rank results by number of token occurrences in title + description."""
    def score(b: Bookmark) -> int:
        text = f"{b.title} {b.description}".lower()
        return sum(text.count(t) for t in tokens)

    return sorted(bookmarks, key=score, reverse=True)
```

## Service Integration

The `BookmarkService` acts as a facade that keeps the `SearchIndex` synchronized with the underlying data. Whenever a bookmark is created or updated, the service automatically triggers a re-indexing operation.

```python
# app/services/bookmark_service.py

def create_bookmark(self, data: Dict[str, Any]) -> Tuple[Optional[Bookmark], Optional[str]]:
    # ... validation and persistence ...
    bookmark = Bookmark.from_dict(data)
    self._repo.save_bookmark(bookmark)
    self._search.index_bookmark(bookmark)  # Update search index
    return bookmark, None
```

Because the `BookmarkRepository` is also in-memory, the `SearchIndex` is rebuilt from scratch whenever the application starts. This occurs during the singleton initialization of `BookmarkService`:

```python
# app/services/bookmark_service.py

def _init_services(self) -> None:
    """Bootstrap repository, cache, and search index."""
    self._repo = BookmarkRepository()
    self._cache: LRUCache[Bookmark] = LRUCache(max_size=256)
    self._search = SearchIndex(self._repo)
```

## API Access

The search functionality is exposed via the `/api/bookmarks/search` endpoint. It accepts a query string `q` and an optional `limit` parameter.

```python
# app/routes/bookmarks.py

@bookmarks_bp.route("/search", methods=["GET"])
def search_bookmarks():
    query = request.args.get("q", "")
    limit = request.args.get("limit", 20, type=int)
    results = _service.search(query, limit=limit)
    return jsonify({"results": [b.to_dict() for b in results], "count": len(results)})
```

## Design Tradeoffs and Constraints

The implementation makes several specific design choices that impact how search behaves:

*   **In-Memory Limitation**: The index is not persisted to disk. If the application process restarts, the index is lost and must be rebuilt. This is suitable for the project's current scope but would require a persistent solution (like SQLite FTS or Elasticsearch) for larger datasets.
*   **Soft Deletes**: When a bookmark is "deleted" via `BookmarkService.delete_bookmark`, it is moved to a `trashed` status but remains in the repository. Because the `SearchIndex` does not filter by status, trashed bookmarks will still appear in search results.
*   **Strict AND Matching**: The requirement that *all* query tokens must match can lead to zero results for long or specific queries. There is no support for "OR" matching or fuzzy searching (e.g., handling typos).
*   **Tokenization Scope**: By excluding tags from the index, the system relies on the separate tag-filtering logic in the repository for tag-based discovery, rather than the full-text search engine.