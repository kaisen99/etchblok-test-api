---
title: Setting Up the Search Index
description: A step-by-step tutorial on initializing the SearchIndex with a BookmarkRepository and performing the initial index rebuild.
code_symbols: [SYM#0f269a750bc62c4d874086090a88d14329456024, SYM#b0cc1ddc5c9e6b6675ff73174df52949062c8da5]
section_id: 28b10c3d-6852-4b63-96b2-4f755b11cee6_setting_up_the_search_index
doc_type: tutorial
---

In this tutorial, you will learn how to set up and use the in-memory search engine for your bookmarks. You will initialize a repository, populate it with data, and use the `SearchIndex` class to perform full-text searches with relevance ranking.

### Prerequisites

To follow this tutorial, you need to have the following components available in your environment:
- `BookmarkRepository` for data storage.
- `Bookmark` model for creating bookmark entities.
- `SearchIndex` service for indexing and searching.

### Step 1: Initialize the Bookmark Repository

The `SearchIndex` requires a `BookmarkRepository` to fetch data during its initial build. First, create an instance of the repository and add some sample bookmarks.

```python
from app.db.repository import BookmarkRepository
from app.models.bookmark import Bookmark

# Initialize the repository
repository = BookmarkRepository()

# Create and save a few bookmarks
python_bookmark = Bookmark(
    url="https://python.org",
    title="Python Programming Language",
    description="The official home of the Python Programming Language"
)
repository.save_bookmark(python_bookmark)

fastapi_bookmark = Bookmark(
    url="https://fastapi.tiangolo.com",
    title="FastAPI Framework",
    description="High performance, easy to learn, fast to code, ready for production"
)
repository.save_bookmark(fastapi_bookmark)
```

The `BookmarkRepository` acts as the source of truth. When you call `save_bookmark`, the entity is stored in the repository's internal dictionary.

### Step 2: Initialize the Search Index

Now, initialize the `SearchIndex` by passing the repository instance to its constructor.

```python
from app.services.search_service import SearchIndex

# Initialize the SearchIndex with the repository
search_index = SearchIndex(repository)
```

When you instantiate `SearchIndex`, it automatically triggers an internal `_rebuild()` process. This process calls `repository.list_bookmarks()` to fetch all existing bookmarks (up to 10,000) and indexes them by tokenizing their titles and descriptions.

### Step 3: Perform a Search

With the index initialized, you can now perform free-text searches. The search engine splits your query into tokens, filters out common stop words, and returns bookmarks where **all** query tokens are present.

```python
# Search for bookmarks matching "python"
results = search_index.search("python")

for bookmark in results:
    print(f"Found: {bookmark.title} ({bookmark.url})")

# Search with multiple terms (AND logic)
results = search_index.search("fast performance")
# This will return the FastAPI bookmark because both tokens appear in its description
```

The `search` method ranks results based on relevance. It calculates a score by counting how many times the query tokens appear in the bookmark's title and description, returning the most relevant matches first. The `limit` parameter specifies the maximum number of results to return, though this is also capped by an internal maximum.

### Step 4: Update the Index Incrementally

You don't need to rebuild the entire index when a single bookmark changes. The `SearchIndex` provides methods for incremental updates.

```python
# Create a new bookmark
new_bookmark = Bookmark(
    url="https://rust-lang.org",
    title="Rust Programming Language",
    description="A language empowering everyone to build reliable and efficient software."
)

# 1. Save to repository
repository.save_bookmark(new_bookmark)

# 2. Update the index manually
search_index.index_bookmark(new_bookmark)

# Verify the new bookmark is searchable
results = search_index.search("rust efficient")
print(len(results)) # Output: 1
```

If you delete a bookmark, you must also remove it from the index to prevent it from appearing in search results:

```python
# Remove from repository
repository.delete_bookmark(new_bookmark.id)

# Remove from index
search_index.remove_bookmark(new_bookmark.id)
```

### Summary

You have successfully set up an in-memory search system. By combining `BookmarkRepository` and `SearchIndex`, you can:
1.  **Bootstrap** the index from existing data automatically.
2.  **Search** using multi-token queries with relevance ranking.
3.  **Maintain** the index incrementally as your data changes.

As a next step, you can explore how `BookmarkService` automates these steps by wrapping both the repository and the search index into a single unified API.
