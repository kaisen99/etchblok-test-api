---
title: Tokenization and Ranking Logic
description: A technical explanation of the internal text processing pipeline, including stop-word filtering and the frequency-based scoring algorithm.
code_symbols: [SYM#b0cc1ddc5c9e6b6675ff73174df52949062c8da5]
section_id: 422d71a9-c18a-482e-9fd5-84c6e3802dc6_tokenization_and_ranking_logic
doc_type: explanation
---

The `SearchIndex` class in `app.services.search_service` provides a lightweight, in-memory full-text search capability for bookmarks. It is designed for small datasets where the overhead of a dedicated search engine like Elasticsearch or Typesense is not yet justified. The implementation relies on an inverted index structure, a regex-based tokenization pipeline, and a frequency-based ranking algorithm.

## Inverted Index Structure

At its core, the `SearchIndex` maintains an inverted index using a dictionary where keys are unique tokens (words) and values are sets of bookmark IDs containing those tokens.

```python
# app/services/search_service.py

class SearchIndex:
    def __init__(self, repository: "BookmarkRepository") -> None:
        self._repo = repository
        self._index: Dict[str, Set[str]] = defaultdict(set)
        self._rebuild()
```

This structure allows for O(1) lookup of all bookmarks associated with a specific word. The index is initialized by calling `_rebuild()`, which fetches all existing bookmarks from the `BookmarkRepository` and processes them.

## Text Processing Pipeline

Before text is indexed or searched, it passes through a normalization and tokenization pipeline defined in the `_tokenize` method.

### Tokenization and Normalization
The system uses a regular expression to identify alphanumeric sequences and converts all text to lowercase to ensure case-insensitive matching.

```python
_TOKEN_RE = re.compile(r"[a-z0-9]+")

def _tokenize(self, text: str) -> List[str]:
    """Split text into lowercase tokens, removing stop words."""
    tokens = _TOKEN_RE.findall(text.lower())
    return [t for t in tokens if t not in _STOP_WORDS]
```

### Stop-Word Filtering
To improve search relevance and reduce index size, the pipeline filters out common English "stop words" that carry little semantic meaning. The current implementation uses a hardcoded set of 13 words:

```python
_STOP_WORDS: Set[str] = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "is", "it"
}
```

## Search Execution and AND-Logic

The `search` method implements a strict "AND" logic. For a bookmark to be considered a candidate result, it must contain **all** tokens present in the search query. The number of returned results is capped by the `limit` parameter, which itself cannot exceed `MAX_SEARCH_RESULTS`.

```python
def search(self, query: str, limit: int = 20) -> List[Bookmark]:
    tokens = self._tokenize(query)
    if not tokens:
        return []

    # Start with the set of IDs for the first token
    candidate_ids: Set[str] = self._index.get(tokens[0], set()).copy()
    
    # Intersect with sets for all subsequent tokens (AND logic)
    for token in tokens[1:]:
        candidate_ids &= self._index.get(token, set())

    # ... retrieval and ranking ...
```

This approach ensures high precision but may result in zero hits for long, specific queries where one minor word (not in the stop-word list) is missing from the bookmark.

## Ranking Algorithm

Once candidate bookmarks are identified, they are ranked by relevance using a simple frequency-based scoring algorithm in `_rank_results`.

The score for a bookmark is calculated as the total number of times all query tokens appear in the combined `title` and `description` fields.

```python
@staticmethod
def _rank_results(bookmarks: List[Bookmark], tokens: List[str]) -> List[Bookmark]:
    """Rank results by number of token occurrences in title + description."""
    def score(b: Bookmark) -> int:
        text = f"{b.title} {b.description}".lower()
        return sum(text.count(t) for t in tokens)

    return sorted(bookmarks, key=score, reverse=True)
```

### Tradeoffs in Ranking
*   **Simplicity vs. Sophistication**: The algorithm uses raw counts rather than more advanced metrics like TF-IDF (Term Frequency-Inverse Document Frequency) or BM25. This means it does not account for the relative rarity of a word across the entire collection.
*   **Field Weighting**: The current implementation treats the `title` and `description` with equal weight. A hit in the title contributes the same to the score as a hit in the description.
*   **Performance**: Ranking is performed in-memory on the filtered result set. While efficient for small result sets, the `text.count(t)` operation is performed for every token on every candidate bookmark during the search request.

## Index Maintenance

The index is kept in sync with the underlying data store through incremental updates. When the `BookmarkService` creates or updates a bookmark, it calls `index_bookmark`.

```python
def index_bookmark(self, bookmark: Bookmark) -> None:
    # Remove old entries to handle updates correctly
    self._remove_bookmark_from_index(bookmark.id)
    
    # Process title and description
    tokens = self._tokenize(f"{bookmark.title} {bookmark.description}")
    for token in tokens:
        self._index[token].add(bookmark.id)
```

The `_remove_bookmark_from_index` helper ensures that if a bookmark's content changes (e.g., a word is removed), the old tokens no longer point to that bookmark ID. It also performs cleanup by deleting tokens from the dictionary if their associated ID set becomes empty.
