---
title: Search & Indexing
description: Full-text search capabilities using an inverted index to query bookmark titles and descriptions.
code_symbols: [SYM#0f269a750bc62c4d874086090a88d14329456024]
section_id: b7ed9283-0190-44cf-8128-4f50950c0d74_search___indexing
doc_type: explanation
section_type: guide
---
The search and indexing system in this project provides full-text search capabilities across bookmark titles and descriptions. It is implemented as an in-memory inverted index, designed for high performance on small-to-medium datasets without the overhead of an external search engine like Elasticsearch or Typesense.

## In-Memory Inverted Index

The core of the search functionality is the `SearchIndex` class located in `app/services/search_service.py`. It maintains a mapping of tokens (words) to sets of bookmark IDs.

```python
class SearchIndex:
    def __init__(self, repository: "BookmarkRepository") -> None:
        self._repo = repository
        self._index: Dict[str, Set[str]] = defaultdict(set)
        self._rebuild()
```

When the application starts, the `SearchIndex` is initialized by the `BookmarkService` and performs a full rebuild. It fetches all existing bookmarks from the `BookmarkRepository` and indexes them one by one. This design choice ensures that the search index is always synchronized with the persistent storage upon startup, though it introduces a linear initialization cost relative to the number of bookmarks.

## Tokenization and Normalization

Before text is indexed or searched, it undergoes a normalization process in the `_tokenize` method. This process ensures that search is case-insensitive and ignores common "stop words" that do not contribute to search relevance.

1.  **Lowercasing**: All text is converted to lowercase.
2.  **Regex Filtering**: The `_TOKEN_RE` pattern (`[a-z0-9]+`) extracts alphanumeric sequences, effectively stripping punctuation.
3.  **Stop Word Removal**: Words like "the", "and", and "is" (defined in `_STOP_WORDS`) are discarded.

```python
_STOP_WORDS: Set[str] = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "is", "it"}
_TOKEN_RE = re.compile(r"[a-z0-9]+")

def _tokenize(self, text: str) -> List[str]:
    """Split text into lowercase tokens, removing stop words."""
    tokens = _TOKEN_RE.findall(text.lower())
    return [t for t in tokens if t not in _STOP_WORDS]
```

## Search Execution and Ranking

The `search` method implements an **AND-based** query logic. For a bookmark to match a multi-word query, it must contain *all* the tokens present in the query.

The implementation uses set intersection to efficiently find matching IDs:

```python
def search(self, query: str, limit: int = 20) -> List[Bookmark]:
    tokens = self._tokenize(query)
    if not tokens:
        return []

    # Start with the set of IDs for the first token
    candidate_ids: Set[str] = self._index.get(tokens[0], set()).copy()
    
    # Intersect with sets for subsequent tokens (AND logic)
    for token in tokens[1:]:
        candidate_ids &= self._index.get(token, set())
    
    # ... fetch bookmarks and rank ...
```

### Relevance Ranking
Once the candidate bookmarks are identified, they are ranked using a simple frequency-based algorithm in `_rank_results`. The score for a bookmark is the total number of times the query tokens appear in its combined title and description.

```python
@staticmethod
def _rank_results(bookmarks: List[Bookmark], tokens: List[str]) -> List[Bookmark]:
    """Rank results by number of token occurrences in title + description."""
    def score(b: Bookmark) -> int:
        text = f"{b.title} {b.description}".lower()
        return sum(text.count(t) for t in tokens)

    return sorted(bookmarks, key=score, reverse=True)
```

## Incremental Updates

To keep the index fresh without full rebuilds, the `BookmarkService` coordinates incremental updates during CRUD operations. In `app/services/bookmark_service.py`, both `create_bookmark` and `update_bookmark` trigger re-indexing.

When a bookmark is updated, the `SearchIndex.index_bookmark` method first removes the old entries for that bookmark ID before adding the new tokens. This prevents "ghost" matches from old versions of the bookmark's content.

```python
def index_bookmark(self, bookmark: Bookmark) -> None:
    """Add or update a bookmark in the index."""
    self._remove_bookmark_from_index(bookmark.id)
    tokens = self._tokenize(f"{bookmark.title} {bookmark.description}")
    for token in tokens:
        self._index[token].add(bookmark.id)
```

## Design Tradeoffs and Constraints

The implementation reflects several specific design decisions:

*   **Memory vs. Persistence**: The index is entirely in-memory. While this makes searches extremely fast, it increases the RAM footprint of the application. The codebase explicitly notes in `app/services/search_service.py` that this is "suitable for small datasets" and suggests replacing it with a dedicated engine for production scale.
*   **Strict Matching**: The AND-based logic means that a query for "python tutorial" will not return a bookmark that only contains "python". There is no support for OR logic or fuzzy matching (e.g., Levenshtein distance).
*   **Simple Ranking**: The ranking algorithm does not use advanced techniques like TF-IDF (Term Frequency-Inverse Document Frequency). A very long description that repeats a word many times will naturally rank higher than a concise, highly relevant title.
*   **Consistency**: Because the index is updated synchronously within the `BookmarkService` operations, search results are immediately consistent with the latest changes. There is no "indexing delay" typically found in larger search systems.
