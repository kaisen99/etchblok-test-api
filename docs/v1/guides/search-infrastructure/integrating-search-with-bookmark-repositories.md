---
title: Integrating Search with Bookmark Repositories
description: A step-by-step guide to initializing the SearchIndex with a repository and ensuring the index stays up-to-date as data changes.
code_symbols: [SYM#0f269a750bc62c4d874086090a88d14329456024, SYM#b0cc1ddc5c9e6b6675ff73174df52949062c8da5]
section_id: 18c036e9-8b1f-440d-850b-a39f5bd17eea_integrating_search_with_bookmark_repositories
doc_type: tutorial
section_type: guide
---
This guide demonstrates how to integrate the `SearchIndex` with a `BookmarkRepository` to provide full-text search capabilities. You will learn how to initialize the index, keep it synchronized with your data store, and execute ranked searches.

### Prerequisites

To follow this guide, you need the following components from the codebase:
- `BookmarkRepository`: The persistence layer (from `app.db.repository`).
- `SearchIndex`: The in-memory search engine (from `app.services.search_service`).
- `Bookmark`: The data model (from `app.models.bookmark`).

### Step 1: Initializing the Search Index

The `SearchIndex` is designed to sit alongside your repository. When you initialize it, it automatically performs a one-time "rebuild" by fetching existing bookmarks from the repository.

```python
from app.db.repository import BookmarkRepository
from app.services.search_service import SearchIndex

# 1. Initialize the repository
repository = BookmarkRepository()

# 2. Initialize the SearchIndex with the repository
# This calls _rebuild() internally, scanning up to 10,000 bookmarks
search_index = SearchIndex(repository)
```

The `SearchIndex.__init__` method triggers `_rebuild()`, which uses `repository.list_bookmarks(page=1, per_page=10000)` to populate the initial in-memory inverted index.

### Step 2: Indexing New Bookmarks

The `SearchIndex` does not automatically watch the repository for changes. You must manually update the index whenever a new bookmark is created. This is typically handled in a service layer like `BookmarkService`.

```python
from app.models.bookmark import Bookmark

def create_new_bookmark(data: dict):
    # Create and save the bookmark to the database
    bookmark = Bookmark.from_dict(data)
    repository.save_bookmark(bookmark)
    
    # Update the search index
    search_index.index_bookmark(bookmark)
    
    return bookmark
```

The `index_bookmark` method tokenizes the bookmark's `title` and `description`, removing common stop words and mapping the resulting tokens to the bookmark's ID.

### Step 3: Handling Updates and Re-indexing

When a bookmark's content changes, you must re-index it. The `index_bookmark` method is idempotent regarding updates: it automatically removes the old entries for that bookmark ID before adding the new tokens.

```python
def update_bookmark_content(bookmark_id: str, new_title: str):
    bookmark = repository.get_bookmark(bookmark_id)
    if bookmark:
        bookmark.title = new_title
        bookmark._touch() # Update timestamp
        
        # Save changes to persistence
        repository.save_bookmark(bookmark)
        
        # Re-index the bookmark with new content
        search_index.index_bookmark(bookmark)
```

Inside `SearchIndex.index_bookmark`, the helper `_remove_bookmark_from_index` is called first to ensure no stale tokens remain associated with the ID.

### Step 4: Executing a Search

To perform a search, use the `search()` method. It returns a list of `Bookmark` objects, ranked by how many times the query tokens appear in their title and description.

```python
# Perform a search
results = search_index.search("python tutorial", limit=10)

for bookmark in results:
    print(f"Found: {bookmark.title} ({bookmark.url})")
```

**How Search Works:**
1.  **Tokenization**: The query "python tutorial" is split into `['python', 'tutorial']`.
2.  **AND Logic**: The index finds bookmarks that contain *all* tokens. If a bookmark only has "python" but not "tutorial", it is excluded.
3.  **Ranking**: Results are sorted using `_rank_results`, which counts occurrences of the tokens in the bookmark's text.

### Step 5: Managing Deletions

If you permanently remove a bookmark, you should also remove it from the index to prevent it from appearing in search results.

```python
def delete_bookmark_permanently(bookmark_id: str):
    # Remove from repository
    # (Note: BookmarkRepository uses soft-deletes/trashing by default)
    
    # Remove from search index
    search_index.remove_bookmark(bookmark_id)
```

> [!IMPORTANT]
> In the standard `BookmarkService.delete_bookmark` implementation, bookmarks are "trashed" (a soft-delete) but are **not** removed from the `SearchIndex`. This means trashed items will still appear in search results unless you explicitly filter them or call `remove_bookmark`.

### Complete Integration Example

In practice, these steps are encapsulated within the `BookmarkService` (found in `app/services/bookmark_service.py`), which acts as a facade:

```python
class BookmarkService:
    def _init_services(self) -> None:
        self._repo = BookmarkRepository()
        self._search = SearchIndex(self._repo)

    def create_bookmark(self, data: dict):
        bookmark = Bookmark.from_dict(data)
        self._repo.save_bookmark(bookmark)
        self._search.index_bookmark(bookmark) # Sync search
        return bookmark

    def search(self, query: str, limit: int = 20):
        return self._search.search(query, limit=limit)
```

### Next Steps
- Explore `app.services.search_service._STOP_WORDS` to see which words are ignored during indexing.
- Review `app.models.bookmark.Bookmark` to see the fields available for indexing.
- Implement custom filtering in your search results to exclude bookmarks with a `trashed` status.
