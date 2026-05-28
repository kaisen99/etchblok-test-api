---
title: Search & Indexing
description: Full-text search capabilities using an inverted index to enable efficient bookmark discovery.
code_symbols: [SYM#0f269a750bc62c4d874086090a88d14329456024]
section_id: 2220cc47-d371-46bb-ae8f-0a63786e3f38_search___indexing
doc_type: explanation
section_type: guide
---
The search and indexing system provides full-text discovery capabilities for bookmarks by indexing their titles and descriptions. Rather than relying on database-level text searching, the project implements a custom in-memory inverted index to ensure fast retrieval and flexible ranking logic.

## In-Memory Inverted Index
The core of the search functionality is the `SearchIndex` class located in `app/services/search_service.py`. It maintains an inverted index—a mapping of individual tokens (words) to the IDs of bookmarks that contain them.

```python
class SearchIndex:
    """Inverted index mapping tokens to bookmark IDs."""

    def __init__(self, repository: "BookmarkRepository") -> None:
        self._repo = repository
        self._index: Dict[str, Set[str]] = defaultdict(set)
        self._rebuild()
```

On initialization, the index is built by fetching all existing bookmarks from the `BookmarkRepository` via the `_rebuild` method. This design choice prioritizes search performance at the cost of memory, making it suitable for the dataset sizes expected in this application.

## Tokenization and Indexing
When a bookmark is indexed via `index_bookmark`, its title and description are combined and processed through a tokenization pipeline. The `_tokenize` helper performs the following steps:
1. **Lowercasing**: Converts all text to lowercase to ensure case-insensitive matching.
2. **Regex Filtering**: Uses `[a-z0-9]+` to extract alphanumeric tokens, stripping punctuation.
3. **Stop Word Removal**: Filters out common words (e.g., "the", "and", "is") defined in the `_STOP_WORDS` set to reduce index noise and improve relevance.

```python
_STOP_WORDS: Set[str] = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "is", "it"}

def _tokenize(self, text: str) -> List[str]:
    """Split text into lowercase tokens, removing stop words."""
    tokens = _TOKEN_RE.findall(text.lower())
    return [t for t in tokens if t not in _STOP_WORDS]
```

## Search Logic and Ranking
The `search` method implements an **AND-based matching strategy**. For a bookmark to be returned as a result, it must contain *all* tokens present in the search query.

```python
def search(self, query: str, limit: int = 20) -> List[Bookmark]:
    tokens = self._tokenize(query)
    if not tokens:
        return []

    # Start with candidates for the first token
    candidate_ids: Set[str] = self._index.get(tokens[0], set()).copy()
    # Intersect with candidates for subsequent tokens (AND logic)
    for token in tokens[1:]:
        candidate_ids &= self._index.get(token, set())

    results = []
    for bid in candidate_ids:
        bookmark = self._repo.get_bookmark(bid)
        if bookmark:
            results.append(bookmark)

    return self._rank_results(results, tokens)[:limit]
```

Once matching bookmarks are identified, they are ordered by relevance using `_rank_results`. The ranking algorithm calculates a simple score based on the total number of times the query tokens appear in the bookmark's title and description.

## Service Integration
The `BookmarkService` acts as a facade, orchestrating the `SearchIndex` alongside the repository and cache. It ensures the index remains synchronized with the underlying data store by updating it during creation and modification operations.

In `app/services/bookmark_service.py`:
- **Creation**: `create_bookmark` calls `self._search.index_bookmark(bookmark)` after persisting to the repository.
- **Updates**: `update_bookmark` re-indexes the bookmark whenever the title or description changes.
- **Discovery**: `full_text_search` delegates directly to the `SearchIndex.search` method.

The functionality is exposed to the API via the `/api/bookmarks/search` endpoint in `app/routes/bookmarks.py`, which allows users to query the index with a `q` parameter and an optional `limit`.

## Design Tradeoffs
The implementation reflects several specific design decisions:
- **Strict Matching**: The AND-based logic means that multi-word queries are highly specific. If a user searches for "python tutorial" and a bookmark only contains "python", it will not be returned.
- **Volatility**: Because the index is in-memory, it must be rebuilt from the repository every time the application starts. While efficient for small to medium datasets, this would introduce startup latency as the number of bookmarks grows.
- **Simple Ranking**: The frequency-based ranking does not account for field weighting (e.g., a match in the title being more valuable than a match in the description).
