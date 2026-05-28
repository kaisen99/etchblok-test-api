---
title: Architecture of the Inverted Index
description: An overview of how the search infrastructure maps tokens to bookmark IDs and maintains synchronization with the underlying repository.
code_symbols: [SYM#0f269a750bc62c4d874086090a88d14329456024, SYM#b0cc1ddc5c9e6b6675ff73174df52949062c8da5]
section_id: 39285584-4fca-43e4-8254-5ef4e3250553_architecture_of_the_inverted_index
doc_type: guide
section_type: guide
---
The search functionality in this project is powered by an in-memory inverted index implemented in the `SearchIndex` class within `app/services/search_service.py`. This component provides full-text search capabilities across bookmark titles and descriptions without requiring an external search engine like Elasticsearch or Typesense.

## Core Data Structure

The `SearchIndex` maintains an internal mapping of tokens (words) to sets of bookmark IDs. This is implemented using a `defaultdict(set)`:

```python
# app/services/search_service.py
class SearchIndex:
    def __init__(self, repository: "BookmarkRepository") -> None:
        self._repo = repository
        self._index: Dict[str, Set[str]] = defaultdict(set)
        self._rebuild()
```

This structure allows for O(1) lookup of all bookmark IDs containing a specific word.

## The Indexing Pipeline

When a bookmark is added or updated, it passes through an indexing pipeline that extracts searchable terms.

### Tokenization and Normalization
The `_tokenize` method prepares text for the index by:
1.  Converting all text to lowercase.
2.  Using a regular expression `_TOKEN_RE = re.compile(r"[a-z0-9]+")` to extract alphanumeric words.
3.  Filtering out common "stop words" defined in the `_STOP_WORDS` set (e.g., "the", "and", "is").

### Mapping Content to IDs
The `index_bookmark` method combines the `title` and `description` of a `Bookmark` object into a single string for tokenization. Before adding new tokens, it ensures any existing entries for that bookmark ID are removed to prevent stale data:

```python
def index_bookmark(self, bookmark: Bookmark) -> None:
    self._remove_bookmark_from_index(bookmark.id)
    tokens = self._tokenize(f"{bookmark.title} {bookmark.description}")
    for token in tokens:
        self._index[token].add(bookmark.id)
```

## Search Execution and Ranking

The search process uses an "AND" strategy, meaning a bookmark must contain *all* tokens present in the query to be considered a match.

### Query Processing
The `search` method tokenizes the query string and performs a set intersection across the candidate IDs for each token:

```python
# app/services/search_service.py
tokens = self._tokenize(query)
# ...
candidate_ids: Set[str] = self._index.get(tokens[0], set()).copy()
for token in tokens[1:]:
    candidate_ids &= self._index.get(token, set())
```

### Relevance Ranking
Once matching bookmarks are retrieved from the `BookmarkRepository`, they are ranked by the `_rank_results` method. The score is calculated based on the total number of times the query tokens appear in the bookmark's title and description:

```python
@staticmethod
def _rank_results(bookmarks: List[Bookmark], tokens: List[str]) -> List[Bookmark]:
    def score(b: Bookmark) -> int:
        text = f"{b.title} {b.description}".lower()
        return sum(text.count(t) for t in tokens)

    return sorted(bookmarks, key=score, reverse=True)
```

## Synchronization and Lifecycle

The `BookmarkService` (in `app/services/bookmark_service.py`) acts as the orchestrator, ensuring the `SearchIndex` stays synchronized with the underlying `BookmarkRepository`.

1.  **Initialization**: When `BookmarkService` is first instantiated (as a singleton), it creates the `SearchIndex`. The index immediately calls `_rebuild()`, which loads up to 10,000 bookmarks from the repository to populate the memory structure.
2.  **Incremental Updates**:
    *   `create_bookmark`: Calls `self._search.index_bookmark(bookmark)` after saving to the repo.
    *   `update_bookmark`: Re-indexes the bookmark whenever the title or description is modified.
3.  **Soft Deletion Nuance**: In this implementation, `delete_bookmark` in `BookmarkService` performs a soft-delete by changing the bookmark status to `trashed`. Notably, it does **not** call `remove_bookmark` from the index. Because `SearchIndex.search` retrieves bookmarks via `self._repo.get_bookmark(bid)`, trashed bookmarks will still appear in search results if they match the query.

## Performance Considerations

*   **Memory Bound**: The index is entirely in-memory and non-persistent. It is rebuilt from scratch every time the application starts.
*   **Removal Complexity**: The `_remove_bookmark_from_index` method performs a full scan of the index dictionary (`for token, ids in self._index.items()`). While efficient for small datasets, the cost of updating or removing a bookmark grows linearly with the number of unique tokens in the entire index.
