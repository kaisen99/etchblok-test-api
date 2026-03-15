---
title: Performing Your First Search
description: A beginner-friendly guide to initializing the SearchIndex and executing a basic text query to find bookmarks.
code_symbols: [SYM#b0cc1ddc5c9e6b6675ff73174df52949062c8da5]
section_id: 8d23964a-c0c1-4434-af6b-16bc7308636f_performing_your_first_search
doc_type: tutorial
section_type: guide
---
In this tutorial, you will learn how to use the `SearchIndex` to build a functional full-text search for your bookmarks. You will initialize the index, populate it with data, and execute queries that rank results by relevance.

### Prerequisites

To follow this guide, you need to have the following components from the codebase available:
- `BookmarkRepository` from `app.db.repository` to provide the data source.
- `Bookmark` from `app.models.bookmark` to create searchable entities.
- `SearchIndex` from `app.services.search_service`.

### Step 1: Initialize the Search Index

The `SearchIndex` is an in-memory inverted index. When you initialize it, it requires a `BookmarkRepository` instance. During initialization, it automatically performs a "rebuild" by fetching existing bookmarks from the repository and indexing them.

```python
from app.db.repository import BookmarkRepository
from app.services.search_service import SearchIndex

# 1. Initialize the repository (the data source)
repo = BookmarkRepository()

# 2. Initialize the search index
# This calls self._rebuild() internally to index existing data
search_index = SearchIndex(repo)
```

By passing the `repo` to `SearchIndex`, you allow the index to fetch full `Bookmark` objects when a search match is found. The `_rebuild` method specifically calls `repo.list_bookmarks(page=1, per_page=10000)` to populate the initial state. Note that because the index is in-memory, this rebuild happens every time your application starts.

### Step 2: Index New Bookmarks

While the index builds itself on startup, you must manually update it when adding new bookmarks to your application. The `index_bookmark` method processes the `title` and `description` fields, splitting them into lowercase tokens and removing common stop words.

```python
from app.models.bookmark import Bookmark

# Create a new bookmark
new_bookmark = Bookmark(
    url="https://python.org",
    title="Python Programming Language",
    description="A powerful language to build web apps and data tools."
)

# Save it to the repository first
repo.save_bookmark(new_bookmark)

# Add it to the search index
search_index.index_bookmark(new_bookmark)
```

When you call `index_bookmark`, the `SearchIndex` tokenizes the text using a regex pattern and maps each unique word (token) to the bookmark's ID. If the bookmark was already indexed, it is first removed to prevent duplicate entries. Keep in mind that only the `title` and `description` fields are searchable; the URL itself is not indexed.

### Step 3: Execute a Search Query

Now that your index is populated, you can perform a search. The `search` method returns a list of `Bookmark` objects that match your query.

```python
# Search for bookmarks containing both "python" AND "web"
results = search_index.search("python web", limit=5)

for bookmark in results:
    print(f"Match found: {bookmark.title} ({bookmark.url})")
```

The search implementation follows two critical rules:
1.  **AND Logic**: All tokens in your query must appear in the bookmark. If you search for "python web", a bookmark containing only "python" will not be returned. This can lead to empty results if your query is too specific.
2.  **Ranking**: Results are ordered by relevance. The `_rank_results` helper calculates a score based on how many times the query tokens appear in the bookmark's title and description combined.

### Step 4: Handle Updates and Deletions

To keep your search results accurate, you must update the index whenever a bookmark is modified or removed.

```python
# To update: simply call index_bookmark again with the updated object
updated_bookmark = repo.get_bookmark(new_bookmark.id)
updated_bookmark.title = "Updated Python Guide"
search_index.index_bookmark(updated_bookmark)

# To remove: use the bookmark ID
search_index.remove_bookmark(new_bookmark.id)
```

The `remove_bookmark` method cleans up the inverted index by iterating through the tokens and discarding the specific bookmark ID, ensuring that deleted items no longer appear in search results.

### Complete Example

Here is how the entire process looks when combined into a single script:

```python
from app.db.repository import BookmarkRepository
from app.services.search_service import SearchIndex
from app.models.bookmark import Bookmark

# Setup
repo = BookmarkRepository()
search_index = SearchIndex(repo)

# Populate
b1 = Bookmark(
    url="https://flask.palletsprojects.com", 
    title="Flask Documentation", 
    description="Web development with Python"
)
repo.save_bookmark(b1)
search_index.index_bookmark(b1)

# Query
query = "flask python"
matches = search_index.search(query)

if matches:
    print(f"Found {len(matches)} results for '{query}':")
    for m in matches:
        print(f"- {m.title}")
else:
    print("No matches found.")
```

### Next Steps
In a production environment, you typically don't manage the `SearchIndex` manually. Instead, you use the `BookmarkService` (found in `app/services/bookmark_service.py`), which encapsulates both the `BookmarkRepository` and `SearchIndex` to ensure that every create, update, or delete operation automatically synchronizes the search index. You can also explore the REST API implementation in `app/routes/bookmarks.py` to see how search is exposed via HTTP.