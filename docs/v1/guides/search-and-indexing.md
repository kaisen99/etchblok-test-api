---
title: Search and Indexing
description: Technical overview of the inverted index and full-text search capabilities used to discover bookmarks by content.
code_symbols: [SYM#0f269a750bc62c4d874086090a88d14329456024]
section_id: 62e68241-e07f-4062-a7dd-bcd2beaf937d_search_and_indexing
doc_type: explanation
section_type: guide
---
The search functionality in this project is implemented using a custom in-memory inverted index. This design provides fast, full-text search capabilities without the overhead of an external search engine like Elasticsearch or Typesense, making it ideal for the project's current scale and architectural simplicity.

## Inverted Index Architecture

The core of the search system is the `SearchIndex` class located in `app/services/search_service.py`. It maintains a mapping where keys are unique tokens (words) and values are sets of bookmark IDs containing those tokens.

```python
class SearchIndex:
    def __init__(self, repository: "BookmarkRepository") -> None:
        self._repo = repository
        self._index: Dict[str, Set[str]] = defaultdict(set)
        self._rebuild()
```

This structure allows for O(1) lookup of all bookmarks containing a specific word. The index is entirely volatile; it is rebuilt from the `BookmarkRepository` every time the application starts via the `_rebuild()` method, which iterates through all existing bookmarks and indexes them.

## Tokenization and Preprocessing

Before text is indexed or searched, it undergoes a normalization process in the `_tokenize` method. This ensures that search is case-insensitive and ignores common "stop words" that do not add semantic value to the search.

1.  **Lowercasing**: All text is converted to lowercase.
2.  **Regex Splitting**: The pattern `[a-z0-9]+` is used to extract alphanumeric tokens, effectively stripping punctuation.
3.  **Stop Word Filtering**: Tokens matching a hardcoded list of common words (e.g., "the", "and", "is") are discarded.

```python
_STOP_WORDS: Set[str] = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "is", "it"}
_TOKEN_RE = re.compile(r"[a-z0-9]+")

def _tokenize(self, text: str) -> List[str]:
    """Split text into lowercase tokens, removing stop words."""
    tokens = _TOKEN_RE.findall(text.lower())
    return [t for t in tokens if t not in _STOP_WORDS]
```

## Search Strategy and Ranking

The `SearchIndex.search` method implements a strict **AND** strategy. When a user provides a multi-word query, the system tokenizes the query and finds the intersection of the ID sets for every token. This means a bookmark must contain *all* search terms to be considered a match.

```python
candidate_ids: Set[str] = self._index.get(tokens[0], set()).copy()
for token in tokens[1:]:
    candidate_ids &= self._index.get(token, set())
```

Once candidate bookmarks are identified, they are ranked using a simple frequency-based scoring mechanism in `_rank_results`. The score is calculated by counting how many times the search tokens appear in the combined title and description of the bookmark.

```python
def _rank_results(bookmarks: List[Bookmark], tokens: List[str]) -> List[Bookmark]:
    """Rank results by number of token occurrences in title + description."""
    def score(b: Bookmark) -> int:
        text = f"{b.title} {b.description}".lower()
        return sum(text.count(t) for t in tokens)

    return sorted(bookmarks, key=score, reverse=True)
```

## Integration and Consistency

The `BookmarkService` in `app/services/bookmark_service.py` acts as an orchestrator to ensure the search index remains synchronized with the underlying data store. It follows a "write-through" pattern where any operation that modifies a bookmark also updates the index.

*   **Creation**: `create_bookmark` calls `self._search.index_bookmark(bookmark)` after saving to the repository.
*   **Updates**: `update_bookmark` re-indexes the bookmark, which internally removes old tokens and adds new ones.
*   **Deletion**: While the current implementation primarily uses soft-deletion (trashing), the `SearchIndex` provides a `remove_bookmark` method to prune the index when necessary.

## Design Tradeoffs

The choice of a custom in-memory index involves several technical tradeoffs:

*   **Performance vs. Memory**: Search lookups are extremely fast because they happen entirely in RAM. However, memory usage scales linearly with the number of bookmarks and the size of their descriptions.
*   **Startup Latency**: Because the index is rebuilt on initialization, application startup time increases as the database grows. This is managed in `SearchIndex._rebuild` by fetching bookmarks in bulk.
*   **Query Flexibility**: The current implementation does not support fuzzy matching, stemming (e.g., matching "running" with "run"), or complex boolean queries (OR/NOT). It prioritizes a predictable "exact match" experience for tokens.
*   **Consistency**: Since the index is not persistent, there is a risk of it becoming out of sync if the service layer is bypassed (e.g., manual database edits). The project mitigates this by making `BookmarkService` the sole entry point for data modifications.