---
title: Getting Started with Search
description: A step-by-step tutorial on initializing the SearchIndex with a repository and performing your first query.
code_symbols: [SYM#0f269a750bc62c4d874086090a88d14329456024, SYM#b0cc1ddc5c9e6b6675ff73174df52949062c8da5]
section_id: 7b20e3dc-256b-4863-8f00-e274a3159fe_getting_started_with_search
doc_type: tutorial
---

The `SearchIndex` class provides an in-memory, full-text search capability for bookmarks. It uses an inverted index to map keywords (tokens) to bookmark IDs, allowing for fast retrieval and relevance ranking based on the frequency of terms in titles and descriptions.

In this tutorial, you will learn how to initialize the search service, index your first bookmark, and perform a ranked search query.

### Prerequisites

To follow this tutorial, you need to import the core components from the application:

```python
from app.db.repository import BookmarkRepository
from app.services.search_service import SearchIndex
from app.models.bookmark import Bookmark
```

### Step 1: Initialize the Repository and Search Index

The `SearchIndex` requires a `BookmarkRepository` instance to function. When you initialize the index, it automatically scans the repository and builds an initial index of all existing bookmarks.

```python
# Create the data store
repo = BookmarkRepository()

# Initialize the search index with the repository
search_index = SearchIndex(repo)
```

The `SearchIndex.__init__` method calls an internal `_rebuild()` function. This ensures that even if your repository already contains data, the index is ready to use immediately upon instantiation.

### Step 2: Create and Index a Bookmark

To make a bookmark searchable, you must first save it to the repository and then explicitly add it to the index. The indexer processes both the `title` and the `description` fields.

```python
# 1. Create a new bookmark
bookmark = Bookmark(
    url="https://github.com/features/actions",
    title="GitHub Actions",
    description="Automate, customize, and execute your software development workflows right in your repository."
)

# 2. Persist it to the repository
repo.save_bookmark(bookmark)

# 3. Add it to the search index
search_index.index_bookmark(bookmark)
```

When `index_bookmark` is called, the service tokenizes the text, removes common "stop words" (like 'and', 'the', 'is'), and maps the remaining tokens to the bookmark's ID.

### Step 3: Perform a Search Query

You can now query the index using the `search` method. The `limit` parameter specifies the maximum number of results to return, which is capped by an internal maximum. By default, the search returns up to 20 results.

```python
# Perform a search for "workflow automation"
results = search_index.search("workflow automation")

for res in results:
    print(f"Match found: {res.title} (ID: {res.id})")
```

The search logic follows two key rules:
1.  **AND Logic**: All tokens in your query must be present in the bookmark for it to be returned. A search for "GitHub Actions" will only return bookmarks containing both "github" and "actions".
2.  **Relevance Ranking**: Results are ordered by the number of times the query tokens appear in the bookmark's title and description.

### Step 4: Update or Remove Bookmarks

If a bookmark is modified or deleted, you must update the index to keep it in sync with the repository.

```python
# Update a bookmark
bookmark.description = "Updated description with new keywords like CI/CD."
repo.save_bookmark(bookmark)
search_index.index_bookmark(bookmark)  # Re-indexing replaces the old entries

# Remove a bookmark
search_index.remove_bookmark(bookmark.id)
```

### Complete Example

Here is the complete code for setting up a repository, indexing multiple items, and performing a search.

```python
from app.db.repository import BookmarkRepository
from app.services.search_service import SearchIndex
from app.models.bookmark import Bookmark

# Setup
repo = BookmarkRepository()
search_index = SearchIndex(repo)

# Add data
b1 = Bookmark(url="1.com", title="Python Docs", description="Official Python documentation.")
b2 = Bookmark(url="2.com", title="Python Tutorial", description="A great tutorial for Python beginners.")

for b in [b1, b2]:
    repo.save_bookmark(b)
    search_index.index_bookmark(b)

# Search
# "Python" matches both, but "Tutorial" matches only b2
query_results = search_index.search("Python Tutorial")

for match in query_results:
    print(f"Found: {match.title}")

# Output:
# Found: Python Tutorial
```

### Next Steps
The `SearchIndex` is typically managed automatically by the `BookmarkService`. To see how this is integrated into the full application lifecycle, explore the `app.services.bookmark_service.BookmarkService` class.
