---
title: Search Architecture
description: An overview of the inverted index implementation and how it maps tokens to bookmark identifiers for efficient retrieval.
code_symbols: [SYM#0f269a750bc62c4d874086090a88d14329456024, SYM#b0cc1ddc5c9e6b6675ff73174df52949062c8da5]
section_id: e07146ab-85be-43d8-997d-cfe49670f8e1_search_architecture
doc_type: guide
section_type: guide
---
The `SearchIndex` class in `app.services.search_service` provides an in-memory full-text search capability for bookmarks. It is designed as a lightweight, internal component that allows for efficient retrieval of bookmarks based on keywords found in their titles and descriptions.

The core of the search architecture is an **inverted index** implemented using a standard Python dictionary where keys are tokens (words) and values are sets of bookmark identifiers.

```python
# app/services/search_service.py

class SearchIndex:
    def __init__(self, repository: "BookmarkRepository") -> None:
        self._repo = repository
        self._index: Dict[str, Set[str]] = defaultdict(set)
        self._rebuild()
```

## The Indexing Pipeline

When a bookmark is indexed via `index_bookmark()`, the system processes the combined text of the bookmark's `title` and `description`. This happens automatically during bookmark creation and updates within the `BookmarkService`.

### Tokenization and Normalization
The `_tokenize` method handles the transformation of raw text into searchable terms:
1.  **Lowercasing**: All text is converted to lowercase to ensure case-insensitive matching.
2.  **Regex Splitting**: The `_TOKEN_RE` (`[a-z0-9]+`) identifies alphanumeric sequences as valid tokens.
3.  **Stop Word Filtering**: Common English words (e.g., "the", "and", "is") defined in the `_STOP_WORDS` constant are discarded to keep the index focused on meaningful terms.

```python
def _tokenize(self, text: str) -> List[str]:
    """Split text into lowercase tokens, removing stop words."""
    tokens = _TOKEN_RE.findall(text.lower())
    return [t for t in tokens if t not in _STOP_WORDS]
```

### Incremental Updates
The index supports incremental updates. When `index_bookmark` is called for an existing bookmark, it first removes the old entries for that ID using `_remove_bookmark_from_index` before re-indexing the new content. This ensures that if a bookmark's title changes, old tokens that no longer apply are purged.

## Search and Retrieval Logic

The `search` method implements a strict **AND** strategy for multi-token queries. For a bookmark to be returned as a result, it must contain every token present in the search query.

### Retrieval Process
1.  **Query Processing**: The search string is passed through the same `_tokenize` pipeline used during indexing.
2.  **Set Intersection**: The system retrieves the set of bookmark IDs for the first token. It then iterates through the remaining tokens, performing a bitwise intersection (`&=`) on the sets. This efficiently narrows down the results to only those bookmarks containing all terms.
3.  **Hydration**: The resulting IDs are used to fetch the actual `Bookmark` objects from the `BookmarkRepository`.

```python
# Logic from SearchIndex.search
candidate_ids: Set[str] = self._index.get(tokens[0], set()).copy()
for token in tokens[1:]:
    candidate_ids &= self._index.get(token, set())
```

### Relevance Ranking
After retrieving matching bookmarks, the `SearchIndex` ranks them by relevance using the `_rank_results` method. The ranking is determined by a simple frequency score: the total number of times the query tokens appear in the bookmark's combined title and description.

```python
@staticmethod
def _rank_results(bookmarks: List[Bookmark], tokens: List[str]) -> List[Bookmark]:
    """Rank results by number of token occurrences in title + description."""
    def score(b: Bookmark) -> int:
        text = f"{b.title} {b.description}".lower()
        return sum(text.count(t) for t in tokens)

    return sorted(bookmarks, key=score, reverse=True)
```

## Integration with BookmarkService

The `SearchIndex` is a critical dependency of the `BookmarkService` (found in `app/services/bookmark_service.py`). The service manages the lifecycle of the index:

*   **Initialization**: When `BookmarkService` is instantiated, it initializes the `SearchIndex`. The index immediately performs a `_rebuild()`, which fetches up to 10,000 bookmarks from the repository to populate the in-memory structure.
*   **Synchronization**: The service ensures the index stays in sync with the database. In `create_bookmark` and `update_bookmark`, the service explicitly calls `self._search.index_bookmark(bookmark)` after a successful database save.
*   **Search Delegation**: The `full_text_search` method in `BookmarkService` simply delegates the operation to the `SearchIndex.search` method.

## Architectural Constraints

As an in-memory implementation, the `SearchIndex` has specific characteristics that influence how it is used in this codebase:

1.  **Volatility**: The index is not persisted to disk. It is entirely rebuilt from the `BookmarkRepository` every time the application starts.
2.  **Memory Bound**: The index size is limited by the available RAM. While efficient for the "small datasets" mentioned in the module docstring, it is not intended for millions of records.
3.  **Removal Overhead**: Removing a bookmark requires iterating over the entire `_index` dictionary to find and discard the ID from various token sets. This is an $O(N)$ operation where $N$ is the number of unique tokens in the entire index.

For production environments requiring higher scalability or advanced features (like fuzzy matching or stemming), the implementation is designed to be replaced by external engines such as Elasticsearch or Typesense.
