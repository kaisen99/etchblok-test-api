---
title: Search and Discovery Mechanisms
description: An overview of how the service layer integrates full-text search and paginated listing to help users find content efficiently.
code_symbols: [SYM#fdcfaed9972e477ae4585fd1b279ac107fa534cd]
section_id: a7569150-ad64-4922-8569-1c96eeb61eda_search_and_discovery_mechanisms
doc_type: guide
---

The service layer provides two primary mechanisms for content discovery: structured paginated listing and full-text search. These capabilities are orchestrated by the `BookmarkService` (found in `app/services/bookmark_service.py`), which acts as a facade over the persistence layer, an in-memory search index, and a performance cache.

## Paginated Listing

The `BookmarkService.list_bookmarks` method provides a structured way to browse content. It delegates the heavy lifting to the `BookmarkRepository`, allowing for efficient retrieval of data subsets.

### Implementation Details
The listing mechanism supports three primary parameters:
- **Pagination**: `page` and `per_page` control the window of results.
- **Filtering**: An optional `status` parameter (e.g., "active", "archived", "trash") allows users to filter content by its lifecycle state.

```python
def list_bookmarks(
    self, page: int = 1, per_page: int = 25, status: Optional[str] = None
) -> Tuple[List[Bookmark], int]:
    """Return a paginated list of bookmarks."""
    return self._repo.list_bookmarks(page=page, per_page=per_page, status=status)
```

The repository implementation in `app/db/repository.py` handles the slicing of the internal data structures. It sorts items by `created_at` in descending order and returns both the requested page of `Bookmark` objects and the total count, enabling front-end components to calculate pagination metadata.

## Full-Text Search

The `BookmarkService.full_text_search` method provides the public interface for full-text search. It delegates to the custom `SearchIndex` (defined in `app/services/search_service.py`), which is an in-memory inverted index that maps normalized tokens to bookmark IDs.

```python
def full_text_search(self, query: str, limit: int = 20) -> List[Bookmark]:
    """Full-text search across bookmark titles and descriptions."""
    return self._search.search(query, limit=limit)
```

### Tokenization and Indexing
When a bookmark is indexed via `SearchIndex.index_bookmark`, the system processes the `title` and `description` fields:
1.  **Normalization**: Text is converted to lowercase.
2.  **Tokenization**: A regex `[a-z0-9]+` extracts alphanumeric tokens.
3.  **Stop Word Removal**: Common words like "the", "and", and "for" (defined in `_STOP_WORDS`) are excluded to improve index relevance.

### Search Logic
The `SearchIndex.search` method implements **AND-based logic**. For a multi-word query, a bookmark must contain *all* tokens to be included in the results.

```python
def search(self, query: str, limit: int = 20) -> List[Bookmark]:
    """Search bookmarks matching the query string.
    Tokens are AND-ed together — all must appear for a result to match.
    """
    tokens = self._tokenize(query)
    if not tokens:
        return []

    candidate_ids: Set[str] = self._index.get(tokens[0], set()).copy()
    for token in tokens[1:]:
        candidate_ids &= self._index.get(token, set())
    # ...
```

Results are ranked using `_rank_results`, which calculates a score based on the frequency of the query tokens within the bookmark's metadata, ensuring that the most relevant matches appear first.

## Consistency and Synchronization

A critical responsibility of the `BookmarkService` is ensuring that the search index and cache remain synchronized with the underlying repository during write operations.

### Incremental Updates
The search index is not just a static snapshot. The `BookmarkService` performs incremental updates during the bookmark lifecycle:
- **Creation**: `create_bookmark` calls `self._search.index_bookmark(bookmark)` immediately after persistence.
- **Updates**: `update_bookmark` re-indexes the bookmark to reflect changes in the title or description.
- **Deletion**: `delete_bookmark` (which performs a soft-delete) and `delete_tag` (which modifies multiple bookmarks) trigger cache invalidations to ensure stale data is not served.

### Startup Rebuild
Because the `SearchIndex` is an in-memory structure, it is bootstrapped during the `BookmarkService` initialization. The `SearchIndex.__init__` method calls `_rebuild()`, which iterates through the repository to populate the inverted index:

```python
def _init_services(self) -> None:
    """Bootstrap repository, cache, and search index."""
    self._repo = BookmarkRepository()
    self._cache: LRUCache[Bookmark] = LRUCache(max_size=256)
    self._search = SearchIndex(self._repo)
```

This architecture ensures that while the primary data is persisted safely in the repository, discovery operations remain highly performant by operating on optimized in-memory structures.
