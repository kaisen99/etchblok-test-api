---
title: Understanding Ranking and Tokenization
description: A deep dive into the scoring algorithm, tokenization process, and the use of stop words to improve search relevance.
code_symbols: [SYM#b0cc1ddc5c9e6b6675ff73174df52949062c8da5]
section_id: 7e5c5e8c-02e7-4218-a7bc-66cddd4c6437_understanding_ranking_and_tokenization
doc_type: explanation
---

The `SearchIndex` class in `app/services/search_service.py` implements a custom, in-memory search engine. It uses a specific tokenization pipeline and a frequency-based ranking algorithm to provide full-text search capabilities for bookmarks.

## The Tokenization Pipeline

The `SearchIndex` processes both bookmark content and search queries through a consistent tokenization pipeline defined in the `_tokenize` method. This ensures that the search is case-insensitive and ignores common noise words.

The pipeline consists of three primary steps:
1.  **Normalization**: The input text is converted to lowercase using `text.lower()`.
2.  **Regex Splitting**: The text is split into tokens using the regular expression `_TOKEN_RE = re.compile(r"[a-z0-9]+")`. This effectively treats any non-alphanumeric character (punctuation, whitespace, special symbols) as a delimiter.
3.  **Stop Word Filtering**: Tokens are filtered against a hardcoded set of `_STOP_WORDS`.

```python
# app/services/search_service.py

_STOP_WORDS: Set[str] = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "is", "it"}
_TOKEN_RE = re.compile(r"[a-z0-9]+")

def _tokenize(self, text: str) -> List[str]:
    """Split text into lowercase tokens, removing stop words."""
    tokens = _TOKEN_RE.findall(text.lower())
    return [t for t in tokens if t not in _STOP_WORDS]
```

This approach prioritizes simplicity and speed for small datasets. However, because it uses a basic regex, it does not support stemming (e.g., "running" and "run" are treated as distinct tokens) or advanced linguistic analysis.

## Search Strategy: Boolean AND Logic

When a user performs a search, the `SearchIndex.search` method applies a strict "AND" strategy. For a bookmark to be considered a candidate result, it must contain **all** tokens present in the search query.

The implementation uses set intersection to find matching bookmark IDs:

```python
# app/services/search_service.py

def search(self, query: str, limit: int = 20) -> List[Bookmark]:
    tokens = self._tokenize(query)
    if not tokens:
        return []

    # Start with the set of IDs for the first token
    candidate_ids: Set[str] = self._index.get(tokens[0], set()).copy()
    
    # Intersect with the sets of IDs for all subsequent tokens
    for token in tokens[1:]:
        candidate_ids &= self._index.get(token, set())
    
    # ... retrieval and ranking logic ...
```
The `limit` parameter specifies the maximum number of results to return, which is further capped by a system-defined maximum to prevent excessively large result sets.

This design choice ensures high precision—results are guaranteed to contain all search terms—but it can lead to zero results for long, specific queries where a "fuzzy" or "OR" match might have been more helpful.

## Ranking and Scoring Algorithm

Once the candidate bookmarks are identified, they are ranked by relevance using the `_rank_results` static method. The scoring is based on the raw frequency of the query tokens within the combined title and description of the bookmark.

```python
# app/services/search_service.py

@staticmethod
def _rank_results(bookmarks: List[Bookmark], tokens: List[str]) -> List[Bookmark]:
    """Rank results by number of token occurrences in title + description."""
    def score(b: Bookmark) -> int:
        # Combine title and description for scoring
        text = f"{b.title} {b.description}".lower()
        # Sum the occurrences of each query token
        return sum(text.count(t) for t in tokens)

    return sorted(bookmarks, key=score, reverse=True)
```

The scoring logic is straightforward:
-   It calculates a score for each bookmark by summing the number of times each query token appears in the lowercase text.
-   Bookmarks with higher total counts are ranked higher.

### Tradeoffs in Ranking
While effective for simple use cases, this frequency-based ranking has specific characteristics:
-   **Field Weighting**: There is no distinction between a token appearing in the `title` versus the `description`. A word appearing five times in a long description will outweigh a word appearing once in a title, even though titles are typically more indicative of content.
-   **Document Length Bias**: Longer descriptions naturally have a higher probability of containing more occurrences of a token, which can bias the results toward bookmarks with verbose descriptions.
-   **Performance**: The scoring happens at query time by iterating over the full text of every candidate bookmark. For a large number of candidates, this `text.count(t)` operation becomes a bottleneck.

## In-Memory Index Management

The `SearchIndex` is an entirely in-memory structure (`Dict[str, Set[str]]`). It is initialized by fetching all bookmarks from the `BookmarkRepository` via the `_rebuild` method:

```python
def _rebuild(self) -> None:
    """Rebuild the entire index from the repository."""
    self._index.clear()
    # Fetches up to 10,000 bookmarks to populate the index
    all_bookmarks, _ = self._repo.list_bookmarks(page=1, per_page=10000)
    for bookmark in all_bookmarks:
        self.index_bookmark(bookmark)
```

This design provides extremely fast search performance for small to medium datasets because no disk I/O or database queries are required during the search itself (other than fetching the final `Bookmark` objects by ID). However, it introduces a memory overhead proportional to the size of the text content and requires a full rebuild whenever the application restarts. Incremental updates are handled via `index_bookmark` and `remove_bookmark` to keep the index synchronized with the repository during the application's lifecycle.
