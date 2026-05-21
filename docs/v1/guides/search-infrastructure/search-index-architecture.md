---
title: Search Index Architecture
description: An overview of the inverted index implementation, explaining how bookmark data is mapped to searchable tokens and stored in memory.
code_symbols: [SYM#0f269a750bc62c4d874086090a88d14329456024, SYM#b0cc1ddc5c9e6b6675ff73174df52949062c8da5]
section_id: 3a35c420-ca11-4472-b0ae-0591ee342073_search_index_architecture
doc_type: guide
---

The search functionality in this application is powered by an in-memory inverted index implemented in the `SearchIndex` class. This architecture provides fast, full-text search capabilities across bookmark titles and descriptions without requiring an external search engine like Elasticsearch or Typesense.

## The Inverted Index Structure

At its core, the `SearchIndex` (found in `app/services/search_service.py`) maintains a mapping of searchable tokens to the IDs of bookmarks that contain them.

```python
# Internal structure of SearchIndex
self._index: Dict[str, Set[str]] = defaultdict(set)
```

When a bookmark is indexed, its title and description are combined and broken down into individual tokens. Each token becomes a key in the `_index` dictionary, and the bookmark's unique ID is added to the associated set. This structure allows the system to instantly identify all bookmarks containing a specific word.

## The Tokenization Pipeline

Before text is added to the index or used for searching, it passes through a tokenization pipeline defined in the `_tokenize` method. This ensures that searches are case-insensitive and noise-free.

1.  **Normalization**: The text is converted to lowercase.
2.  **Regex Splitting**: The `_TOKEN_RE` (defined as `re.compile(r"[a-z0-9]+")`) extracts alphanumeric sequences, effectively stripping punctuation.
3.  **Stop Word Removal**: Common English words that provide little search value (e.g., "the", "and", "is") are filtered out using the `_STOP_WORDS` set.

```python
def _tokenize(self, text: str) -> List[str]:
    """Split text into lowercase tokens, removing stop words."""
    tokens = _TOKEN_RE.findall(text.lower())
    return [t for t in tokens if t not in _STOP_WORDS]
```

## Search and Ranking Logic

The `SearchIndex.search` method implements an **AND-based** search strategy. For a bookmark to appear in the results, it must contain *all* tokens present in the search query.

### Intersection of Results
The search begins by retrieving the set of bookmark IDs for the first token and then iteratively intersecting that set with the sets for subsequent tokens:

```python
candidate_ids: Set[str] = self._index.get(tokens[0], set()).copy()
for token in tokens[1:]:
    candidate_ids &= self._index.get(token, set())
```

### Relevance Scoring
Once the matching bookmarks are retrieved from the `BookmarkRepository`, they are ranked by relevance using the `_rank_results` helper. The score is determined by the total number of times the query tokens appear in the bookmark's title and description combined.
The final list of ranked results is then truncated, respecting both the requested `limit` and an internal maximum search result constant.

```python
def score(b: Bookmark) -> int:
    text = f"{b.title} {b.description}".lower()
    return sum(text.count(t) for t in tokens)
```

## Lifecycle and Synchronization

The `SearchIndex` is managed as a singleton component within the `BookmarkService` (`app/services/bookmark_service.py`). It follows a "rebuild-on-start, update-on-change" lifecycle.

### Initialization
When the `BookmarkService` is first instantiated, it triggers `SearchIndex._rebuild()`. This method fetches all existing bookmarks from the repository and populates the in-memory index.

### Incremental Updates
To keep the search results accurate without a full rebuild, the `BookmarkService` calls `index_bookmark` during create and update operations:

*   **Creation**: In `create_bookmark`, the new bookmark is passed to the indexer immediately after being saved to the repository.
*   **Updates**: In `update_bookmark`, the indexer first removes the old entries for that bookmark ID (via `_remove_bookmark_from_index`) and then re-indexes the updated content.
*   **Deletion**: While the current implementation uses soft-deletion (trashing), the `remove_bookmark` method is available to purge IDs from the index entirely.

### Integration Example
The search capability is exposed via the `full_text_search` method in `BookmarkService`, which is called by the API routes:

```python
# app/services/bookmark_service.py
def full_text_search(self, query: str, limit: int = 20) -> List[Bookmark]:
    """Full-text search across bookmark titles and descriptions."""
    return self._search.search(query, limit=limit)
```

This architecture ensures that search results are always synchronized with the underlying data store while maintaining the performance benefits of an in-memory cache.
