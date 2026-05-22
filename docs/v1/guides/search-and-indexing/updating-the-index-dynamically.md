---
title: Updating the Index Dynamically
description: Instructions on how to keep the search index in sync with the bookmark repository when items are added or deleted.
code_symbols: [SYM#b0cc1ddc5c9e6b6675ff73174df52949062c8da5]
section_id: 409952f0-fa9f-494c-8b7f-aa99dba10e0a_updating_the_index_dynamically
doc_type: how_to
section_type: guide
---
To keep the search index in sync with your bookmark repository, you must update the `SearchIndex` whenever a bookmark is created, modified, or deleted. In this project, the `BookmarkService` acts as a facade that orchestrates these updates automatically.

## Indexing a Bookmark
To add a new bookmark or update an existing one in the search index, use the `index_bookmark` method. This method automatically handles re-indexing by removing any stale entries for the bookmark ID before processing the new content.

```python
from app.services.search_service import SearchIndex
from app.models.bookmark import Bookmark

# Assuming search_index and repository are already initialized
bookmark = Bookmark(
    url="https://example.com",
    title="Example Site",
    description="A useful example website for testing."
)

# Add or update the bookmark in the index
search_index.index_bookmark(bookmark)
```

The `index_bookmark` method tokenizes the `title` field twice (to give it higher weighting) and the `description` field once, converts them to lowercase, and maps each token to the bookmark's ID.

## Removing a Bookmark from the Index
To completely remove a bookmark from the search results, use the `remove_bookmark` method with the bookmark's unique ID.

```python
# Remove a bookmark by its ID
search_index.remove_bookmark("bookmark-id-123")
```

This method iterates through the inverted index and discards the ID from all associated token sets. If a token no longer points to any bookmarks, it is removed from the index entirely.

## Automatic Synchronization in BookmarkService
In practice, you should use the `BookmarkService` to manage bookmarks. It ensures that the `SearchIndex` is updated immediately after the repository is updated.

### During Creation
When `create_bookmark` is called, the service persists the bookmark to the repository and then indexes it:

```python
# app/services/bookmark_service.py

def create_bookmark(self, data: Dict[str, Any]) -> Tuple[Optional[Bookmark], Optional[str]]:
    # ... validation logic ...
    bookmark = Bookmark.from_dict(data)
    self._repo.save_bookmark(bookmark)
    
    # Update the search index
    self._search.index_bookmark(bookmark)
    
    self._cache.invalidate(bookmark.id)
    return bookmark, None
```

### During Updates
When `update_bookmark` is called, the service updates the model, saves it, and triggers a re-index:

```python
# app/services/bookmark_service.py

def update_bookmark(self, bookmark_id: str, data: Dict[str, Any]) -> Tuple[Optional[Bookmark], Optional[str]]:
    bookmark = self._repo.get_bookmark(bookmark_id)
    # ... update fields (title, description, etc.) ...
    
    self._repo.save_bookmark(bookmark)
    
    # Re-index the bookmark with new content
    self._search.index_bookmark(bookmark)
    
    self._cache.invalidate(bookmark.id)
    return bookmark, None
```

## Troubleshooting and Gotchas

### Soft Deletes and Search Results
The `BookmarkService.delete_bookmark` method performs a **soft delete** (moving the bookmark to the trash). Currently, this method does **not** call `remove_bookmark`.

```python
# app/services/bookmark_service.py

def delete_bookmark(self, bookmark_id: str) -> bool:
    bookmark = self._repo.get_bookmark(bookmark_id)
    if not bookmark:
        return False
    bookmark.trash() # Status changes to 'trash'
    self._repo.save_bookmark(bookmark)
    self._cache.invalidate(bookmark_id)
    # NOTE: self._search.remove_bookmark(bookmark_id) is NOT called here
    return True
```

**Consequence:** Trashed bookmarks will still appear in search results until the application is restarted or the index is manually updated. To fix this, you must manually call `remove_bookmark` if you want trashed items hidden from search immediately.

### In-Memory Persistence
The `SearchIndex` is entirely in-memory. It is rebuilt from scratch using `_rebuild()` every time the `SearchIndex` (or the `BookmarkService` singleton) is initialized.

```python
# app/services/search_service.py

def _rebuild(self) -> None:
    """Rebuild the entire index from the repository."""
    self._index.clear()
    all_bookmarks, _ = self._repo.list_bookmarks(page=1, per_page=10000)
    for bookmark in all_bookmarks:
        self.index_bookmark(bookmark)
```

### Stop Words
The indexer filters out common "stop words" (e.g., "the", "and", "is"). If a search query consists only of stop words, the `search` method will return an empty list because no tokens will be generated for the query.
