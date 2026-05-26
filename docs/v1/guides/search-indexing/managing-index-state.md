---
title: Managing Index State
description: How to keep the search index synchronized with the bookmark repository through incremental updates and removals.
code_symbols: [SYM#b0cc1ddc5c9e6b6675ff73174df52949062c8da5]
section_id: b1420a65-38d5-4eef-9d77-4498b9c90a22_managing_index_state
doc_type: how_to
section_type: guide
---
The search index in this project is an in-memory inverted index that maps text tokens to bookmark IDs. It is managed by the `SearchIndex` class within `app.services.search_service` and is primarily orchestrated by the `BookmarkService`.

## Initializing and Rebuilding the Index

The index is automatically built from the `BookmarkRepository` when the `SearchIndex` is instantiated. This typically happens once during the bootstrap of the `BookmarkService`.

```python
# From app/services/bookmark_service.py

def _init_services(self) -> None:
    """Bootstrap repository, cache, and search index."""
    self._repo = BookmarkRepository()
    self._cache: LRUCache[Bookmark] = LRUCache(max_size=256)
    self._search = SearchIndex(self._repo)
```

When `SearchIndex(self._repo)` is called, it executes the private `_rebuild()` method, which fetches up to 10,000 bookmarks from the repository and indexes them:

```python
# From app/services/search_service.py

def _rebuild(self) -> None:
    """Rebuild the entire index from the repository."""
    self._index.clear()
    all_bookmarks, _ = self._repo.list_bookmarks(page=1, per_page=10000)
    for bookmark in all_bookmarks:
        self.index_bookmark(bookmark)
```

## Incremental Updates

To keep the index synchronized without a full rebuild, use the `index_bookmark` method. This method is called by `BookmarkService` every time a bookmark is created or updated.

```python
# From app/services/bookmark_service.py

def create_bookmark(self, data: Dict[str, Any]) -> Tuple[Optional[Bookmark], Optional[str]]:
    # ... validation ...
    bookmark = Bookmark.from_dict(data)
    self._repo.save_bookmark(bookmark)
    
    # Update the search index incrementally
    self._search.index_bookmark(bookmark)
    
    self._cache.invalidate(bookmark.id)
    return bookmark, None
```

The `index_bookmark` method handles both new bookmarks and updates by first removing any existing entries for that ID before re-tokenizing the title and description:

```python
# From app/services/search_service.py

def index_bookmark(self, bookmark: Bookmark) -> None:
    """Add or update a bookmark in the index."""
    # Ensure no stale tokens remain from a previous version
    self._remove_bookmark_from_index(bookmark.id)
    
    # Tokenize title and description
    tokens = self._tokenize(f"{bookmark.title} {bookmark.description}")
    for token in tokens:
        self._index[token].add(bookmark.id)
```

## Removing Bookmarks from the Index

If you need to manually remove a bookmark from the search results without deleting it from the repository, use the `remove_bookmark` method.

```python
# Example of manual removal
search_index.remove_bookmark("bookmark_id_123")
```

Internally, this performs a cleanup of the inverted index and removes any tokens that no longer point to any bookmarks:

```python
# From app/services/search_service.py

def _remove_bookmark_from_index(self, bookmark_id: str) -> None:
    """Remove all index entries for a bookmark ID."""
    empty_tokens = []
    for token, ids in self._index.items():
        ids.discard(bookmark_id)
        if not ids:
            empty_tokens.append(token)
    
    # Clean up tokens with no associated bookmarks
    for token in empty_tokens:
        del self._index[token]
```

## Search Mechanics and Logic

The `search` method implements an **AND-based** matching strategy. A bookmark must contain *all* tokens from the query to be included in the results.

```python
# From app/services/search_service.py

def search(self, query: str, limit: int = 20) -> List[Bookmark]:
    tokens = self._tokenize(query)
    if not tokens:
        return []

    # Start with the set of IDs for the first token
    candidate_ids: Set[str] = self._index.get(tokens[0], set()).copy()
    
    # Intersect with sets for all subsequent tokens (AND logic)
    for token in tokens[1:]:
        candidate_ids &= self._index.get(token, set())

    results = []
    for bid in candidate_ids:
        bookmark = self._repo.get_bookmark(bid)
        if bookmark:
            results.append(bookmark)

    return self._rank_results(results, tokens)[:limit]
```

### Ranking and Relevance
Results are ranked by the frequency of query tokens appearing in the bookmark's title and description using the `_rank_results` helper:

```python
@staticmethod
def _rank_results(bookmarks: List[Bookmark], tokens: List[str]) -> List[Bookmark]:
    """Rank results by number of token occurrences in title + description."""
    def score(b: Bookmark) -> int:
        text = f"{b.title} {b.description}".lower()
        return sum(text.count(t) for t in tokens)

    return sorted(bookmarks, key=score, reverse=True)
```

## Troubleshooting and Gotchas

### In-Memory Persistence
The index is entirely in-memory. If the application restarts, the index is lost and must be rebuilt from the `BookmarkRepository`. This is handled automatically by the `BookmarkService` singleton initialization.

### Soft-Deletes (Trash)
In this implementation, calling `BookmarkService.delete_bookmark` performs a "soft-delete" (moving the bookmark to the trash). It **does not** automatically call `remove_bookmark` on the search index. Consequently, trashed bookmarks will still appear in search results as long as they exist in the repository.

### Stop Words
The tokenizer filters out common stop words (e.g., "the", "and", "is"). If a search query consists only of stop words, the `search` method will return an empty list.

### Tokenization Logic
The indexer uses a regex-based tokenizer (`_TOKEN_RE`) and converts all text to lowercase. Only the `title` and `description` fields are indexed; tags and collection names are currently excluded from the search index.
