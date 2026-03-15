---
title: Search System Architecture
description: An overview of the inverted index implementation and its lifecycle within the application, explaining how it maps tokens to bookmark IDs.
code_symbols: [SYM#0f269a750bc62c4d874086090a88d14329456024, SYM#b0cc1ddc5c9e6b6675ff73174df52949062c8da5]
section_id: b2635610-fcf3-4489-9998-f562afb65a8b_search_system_architecture
doc_type: guide
section_type: guide
---
The search system in this application is powered by a lightweight, in-memory inverted index implemented in the `SearchIndex` class. It provides full-text search capabilities across bookmark titles and descriptions without requiring an external search engine like Elasticsearch or Typesense.

## Core Architecture: The Inverted Index

The heart of the search system is the `_index` attribute within `SearchIndex` (found in `app/services/search_service.py`). This is a dictionary where keys are unique tokens (words) and values are sets of bookmark IDs containing those tokens.

```python
# app/services/search_service.py

class SearchIndex:
    def __init__(self, repository: "BookmarkRepository") -> None:
        self._repo = repository
        self._index: Dict[str, Set[str]] = defaultdict(set)
        self._rebuild()
```

This structure allows for O(1) lookups of all bookmarks associated with a specific word, making it highly efficient for small to medium datasets.

## Index Lifecycle and Bootstrapping

The `SearchIndex` is tightly coupled with the `BookmarkRepository`. Because the index is entirely in-memory, it must be bootstrapped whenever the application starts or the service is initialized.

### Initial Rebuild
When `SearchIndex` is instantiated, it calls `_rebuild()`, which fetches all existing bookmarks from the repository and indexes them one by one.

```python
def _rebuild(self) -> None:
    """Rebuild the entire index from the repository."""
    self._index.clear()
    all_bookmarks, _ = self._repo.list_bookmarks(page=1, per_page=10000)
    for bookmark in all_bookmarks:
        self.index_bookmark(bookmark)
```

### Incremental Updates
The index is kept in sync with the database through the `BookmarkService`. Whenever a bookmark is created or updated, the service calls `index_bookmark()`.

```python
# app/services/bookmark_service.py

def create_bookmark(self, data: Dict[str, Any]) -> Tuple[Optional[Bookmark], Optional[str]]:
    # ... validation and persistence ...
    self._repo.save_bookmark(bookmark)
    self._search.index_bookmark(bookmark) # Update the index
    self._cache.invalidate(bookmark.id)
    return bookmark, None
```

## Tokenization and Indexing Logic

Before a bookmark is added to the index, its content is processed into searchable tokens.

1.  **Normalization**: The text is converted to lowercase.
2.  **Regex Filtering**: The `_TOKEN_RE` (`[a-z0-9]+`) extracts alphanumeric sequences.
3.  **Stop Word Removal**: Common words defined in `_STOP_WORDS` (e.g., "the", "and", "is") are discarded to reduce noise.

```python
# app/services/search_service.py

_STOP_WORDS: Set[str] = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "is", "it"}
_TOKEN_RE = re.compile(r"[a-z0-9]+")

def _tokenize(self, text: str) -> List[str]:
    """Split text into lowercase tokens, removing stop words."""
    tokens = _TOKEN_RE.findall(text.lower())
    return [t for t in tokens if t not in _STOP_WORDS]
```

When `index_bookmark` is called, it first removes any existing entries for that bookmark ID using `_remove_bookmark_from_index` to prevent stale data, then maps the new tokens to the ID.

## Search Execution and Ranking

The `search` method implements an **AND-based** matching strategy. For a bookmark to appear in the results, it must contain *all* tokens present in the search query.

### Query Processing
The system retrieves the set of IDs for the first token and then performs a set intersection with the IDs of every subsequent token.

```python
def search(self, query: str, limit: int = 20) -> List[Bookmark]:
    tokens = self._tokenize(query)
    if not tokens:
        return []

    # Start with IDs matching the first token
    candidate_ids: Set[str] = self._index.get(tokens[0], set()).copy()
    
    # Intersect with IDs matching all other tokens (AND logic)
    for token in tokens[1:]:
        candidate_ids &= self._index.get(token, set())

    # ... retrieval and ranking ...
```

### Relevance Ranking
Once the matching bookmarks are retrieved from the repository, they are ranked using the `_rank_results` static method. The score is determined by the total number of times the query tokens appear in the bookmark's title and description.

```python
@staticmethod
def _rank_results(bookmarks: List[Bookmark], tokens: List[str]) -> List[Bookmark]:
    """Rank results by number of token occurrences in title + description."""
    def score(b: Bookmark) -> int:
        text = f"{b.title} {b.description}".lower()
        return sum(text.count(t) for t in tokens)

    return sorted(bookmarks, key=score, reverse=True)
```

## Implementation Considerations

*   **In-Memory Only**: The index does not persist to disk. If the application process restarts, the index is lost and must be rebuilt from the `BookmarkRepository`.
*   **Removal Performance**: The `_remove_bookmark_from_index` method performs a full scan of the index keys (`self._index.items()`). While acceptable for small collections, this operation's complexity grows linearly with the number of unique tokens in the system.
*   **Field Scope**: Currently, only the `title` and `description` fields are indexed. Tags and URLs are ignored by the search system.
*   **Singleton Pattern**: The `BookmarkService` (which holds the `SearchIndex`) is implemented as a singleton, ensuring that all parts of the application share the same warmed-up search index.