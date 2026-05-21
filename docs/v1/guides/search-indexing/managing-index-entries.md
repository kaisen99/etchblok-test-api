---
title: Managing Index Entries
description: Instructions for manually adding, updating, or removing bookmarks from the search index to keep it synchronized with the repository.
code_symbols: [SYM#b0cc1ddc5c9e6b6675ff73174df52949062c8da5]
section_id: 271242e8-78a7-462e-9487-0bfaeb0af97e_managing_index_entries
doc_type: how_to
---

To keep the search functionality synchronized with your data, you must manage the `SearchIndex` entries whenever bookmarks are created, modified, or deleted. The `SearchIndex` is an in-memory inverted index that maps tokens from bookmark titles and descriptions to their IDs.

### Adding or Updating a Bookmark in the Index

The `index_bookmark` method handles both new bookmarks and updates to existing ones. It automatically removes any stale tokens associated with the bookmark ID before re-indexing the current title and description.

```python
from app.services.search_service import SearchIndex
from app.models.bookmark import Bookmark

# Assuming repo is an instance of BookmarkRepository
search_index = SearchIndex(repository=repo)

# Create or update a bookmark object
bookmark = Bookmark(
    url="https://example.com",
    title="Example Site",
    description="A site for examples and testing."
)

# Add (or update) the bookmark in the index
search_index.index_bookmark(bookmark)
```

In the `BookmarkService`, this is typically called immediately after persisting the bookmark to the repository:

```python
# From app/services/bookmark_service.py
def create_bookmark(self, data: Dict[str, Any]) -> Tuple[Optional[Bookmark], Optional[str]]:
    # ... validation and creation ...
    bookmark = Bookmark.from_dict(data)
    self._repo.save_bookmark(bookmark)
    self._search.index_bookmark(bookmark) # Synchronize index
    self._cache.invalidate(bookmark.id)
    return bookmark, None
```

### Removing a Bookmark from the Index

To stop a bookmark from appearing in search results, use the `remove_bookmark` method. This is essential when a bookmark is hard-deleted from the repository.

```python
# Remove a bookmark by its ID
search_index.remove_bookmark("bookmark-id-123")
```

Note that the `remove_bookmark` method performs a full scan of the internal index dictionary to purge the ID from all token sets. For very large indices, this operation may have a performance impact.

### Searching the Index

The `search` method allows you to retrieve bookmarks based on a free-text query. It tokenizes the query and returns bookmarks that contain **all** of the query tokens (AND logic).

```python
# Search for bookmarks containing both "example" and "testing"
results = search_index.search("example testing", limit=10)

for bookmark in results:
    print(f"Found: {bookmark.title}")
```

### Automatic Index Rebuilding

The `SearchIndex` is designed to be self-initializing. When you instantiate the class, it automatically calls its internal `_rebuild` method, which fetches all bookmarks from the repository and indexes them from scratch.

```python
# From app/services/search_service.py
def __init__(self, repository: "BookmarkRepository") -> None:
    self._repo = repository
    self._index: Dict[str, Set[str]] = defaultdict(set)
    self._rebuild() # Automatically populates the index on startup
```

### Troubleshooting and Limitations

*   **In-Memory Only**: The index is not persisted to disk. If the application restarts, the index is lost and must be rebuilt from the `BookmarkRepository`.
*   **AND Logic**: Search queries are split into tokens, and results must match every token. A search for "Python Guide" will not return a bookmark that only contains "Python".
*   **Field Limitations**: Only the `title` and `description` fields are indexed. Tags, URLs, and other metadata are currently ignored by the search engine.
*   **Result Limit**: The `limit` parameter in the `search` method is capped by an internal `MAX_SEARCH_RESULTS` constant, meaning the actual number of results returned may be less than the requested `limit` if `limit` exceeds this maximum.
*   **Stop Words**: Common words (e.g., "the", "is", "and") are filtered out during tokenization and will not yield search results.
*   **Soft Deletes**: In the current implementation of `BookmarkService.delete_bookmark`, bookmarks are "trashed" (status changed) but not explicitly removed from the `SearchIndex`. They will continue to appear in search results unless the repository's `list_bookmarks` (used during rebuild) or `get_bookmark` (used during search) filters them out.
