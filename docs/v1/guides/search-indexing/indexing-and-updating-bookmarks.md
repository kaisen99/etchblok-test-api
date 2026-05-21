---
title: Indexing and Updating Bookmarks
description: Instructions for manually adding, updating, or removing bookmarks from the search index to maintain data consistency.
code_symbols: [SYM#b0cc1ddc5c9e6b6675ff73174df52949062c8da5]
section_id: 226e7eb1-5d88-4dc9-a68a-8dc03ff4bcba_indexing_and_updating_bookmarks
doc_type: how_to
---

To manually manage the search index for bookmarks, use the `SearchIndex` class. This service maintains an in-memory inverted index that maps tokens from bookmark titles and descriptions to their IDs, enabling full-text search.

### Indexing or Updating a Bookmark

YouCan add a new bookmark to the index or update an existing one using the `index_bookmark` method. If the bookmark ID already exists in the index, it is first removed and then re-indexed with the latest content.

```python
from app.services.search_service import SearchIndex
from app.models.bookmark import Bookmark

# Assuming 'repo' is an instance of BookmarkRepository
search_index = SearchIndex(repository=repo)

# Create or retrieve a bookmark
bookmark = Bookmark(
    id="b123",
    url="https://example.com",
    title="Example Site",
    description="A useful site for testing search indexing."
)

# Add or update the bookmark in the index
search_index.index_bookmark(bookmark)
```

The `index_bookmark` method performs the following:
1.  Calls `_remove_bookmark_from_index` to clear any existing tokens associated with the bookmark ID.
2.  Tokenizes the combined string of `bookmark.title` and `bookmark.description`.
3.  Adds the bookmark ID to the set of IDs for each generated token.

### Removing a Bookmark from the Index

To stop a bookmark from appearing in search results, use the `remove_bookmark` method.

```python
# Remove a bookmark by its ID
search_index.remove_bookmark("b123")
```

This method removes the bookmark ID from all token sets in the index. If a token set becomes empty after removal, the token itself is deleted from the index to save memory.

### How Search Works

The `SearchIndex.search` method uses AND-logic for multi-token queries. All tokens in the query must be present in the bookmark's title or description for it to be returned as a result. Note that the actual number of results returned is capped by an internal `MAX_SEARCH_RESULTS` constant, even if a higher `limit` is specified.

```python
# Search for bookmarks containing both "example" AND "testing"
results = search_index.search("example testing", limit=10)

for bookmark in results:
    print(f"Found: {bookmark.title}")
```

1.  **Tokenization**: The query is lowercased and split into tokens using `_TOKEN_RE`. Stop words (e.g., "the", "and", "is") are filtered out.
2.  **Intersection**: The index finds the set of bookmark IDs for each token and performs an intersection.
3.  **Ranking**: Results are ranked by relevance using `_rank_results`, which calculates a score based on the total number of occurrences of the query tokens in the bookmark's title and description.

### Troubleshooting and Limitations

#### Soft-Deletes and Status Changes
In the current implementation of `BookmarkService`, operations like `delete_bookmark` (which moves a bookmark to the trash), `archive_bookmark`, and `restore_bookmark` do **not** automatically update the `SearchIndex`.

If you need the search index to reflect these status changes, you must manually call `remove_bookmark` or `index_bookmark`:

```python
# Example: Manually removing a trashed bookmark from search
if service.delete_bookmark(bookmark_id):
    search_index.remove_bookmark(bookmark_id)
```

#### In-Memory Persistence
The `SearchIndex` is entirely in-memory. It is rebuilt from the `BookmarkRepository` every time the `SearchIndex` class is initialized (typically during the `BookmarkService` singleton initialization).

```python
# Inside SearchIndex.__init__
self._rebuild()
```

The `_rebuild` method fetches up to 10,000 bookmarks from the repository to populate the index.

#### Field Limitations
The index only considers the `title` and `description` fields. Tags, URLs, and collection names are not currently indexed for search.
