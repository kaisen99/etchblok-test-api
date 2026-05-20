---
title: Performing Your First Search
description: A step-by-step guide to initializing the SearchIndex with a repository and executing a basic query.
code_symbols: [SYM#b0cc1ddc5c9e6b6675ff73174df52949062c8da5]
section_id: 7052f0b4-b120-43e3-a2b0-70528c47b820_performing_your_first_search
doc_type: tutorial
section_type: guide
---
In this tutorial, you will learn how to use the in-memory search capabilities of the codebase to index and retrieve bookmarks. You will build a script that initializes a repository, populates it with data, and executes a ranked search query using the `SearchIndex` service.

### Prerequisites

To follow this guide, you need to have the following components available in your environment:
- `Bookmark`: The core data model for saved URLs.
- `BookmarkRepository`: The in-memory storage engine.
- `SearchIndex`: The service responsible for tokenization and inverted indexing.

### Step 1: Initialize the Repository and Search Index

The `SearchIndex` requires a repository instance during initialization. When you create a `SearchIndex`, it automatically scans the repository and builds an initial index of all existing bookmarks.

```python
from app.db.repository import BookmarkRepository
from app.services.search_service import SearchIndex

# Initialize the in-memory storage
repo = BookmarkRepository()

# Initialize the search index with the repository
# This calls _rebuild() internally to index any existing data
search_index = SearchIndex(repo)
```

The `SearchIndex` maintains a `defaultdict(set)` mapping tokens (words) to bookmark IDs. By passing the `repo` to the constructor, you ensure the index stays synchronized with the underlying data source.

### Step 2: Create and Index a Bookmark

Before you can search, you need to add data. You must save the bookmark to the repository first, then manually notify the index to process the new entry.

```python
from app.models.bookmark import Bookmark

# Create a new bookmark instance
bookmark = Bookmark(
    url="https://python.org",
    title="Python Programming Language",
    description="The official home of the Python Programming Language, a great tool for indexing."
)

# Persist to the repository
repo.save_bookmark(bookmark)

# Add the bookmark to the search index
search_index.index_bookmark(bookmark)
```

When `index_bookmark` is called, the `SearchIndex` performs the following:
1.  **Tokenization**: It combines the `title` and `description` into a single string.
2.  **Normalization**: It converts the text to lowercase and removes stop words (like "the", "is", "of").
3.  **Mapping**: It adds the bookmark's ID to the set of IDs associated with each unique token found.

### Step 3: Execute a Search Query

Now that the index is populated, you can perform a search. The `search` method returns a list of `Bookmark` objects that match **all** tokens in your query.

```python
# Execute a search for "python indexing"
results = search_index.search("python indexing", limit=5)

for b in results:
    print(f"Match Found: {b.title}")
    print(f"Description: {b.description}")
```

The `search` method implements an **AND** logic:
- If you search for "python indexing", the engine looks for bookmarks that contain *both* "python" and "indexing".
- Results are ranked using the `_rank_results` helper, which scores bookmarks based on how many times the query tokens appear in their title and description.

### Step 4: Verify the Results

You can verify the ranking logic by adding a second bookmark that has fewer occurrences of the search terms.

```python
# Add a second bookmark with fewer matches
bookmark2 = Bookmark(
    url="https://docs.python.org",
    title="Python Docs",
    description="Documentation for Python."
)
repo.save_bookmark(bookmark2)
search_index.index_bookmark(bookmark2)

# Search again
results = search_index.search("python")

print(f"Total results: {len(results)}")
for i, b in enumerate(results):
    print(f"{i+1}. {b.title}")
```

In this example, "Python Programming Language" will rank higher than "Python Docs" because the word "python" (or related tokens) appears more frequently in its metadata, demonstrating the relevance-based sorting implemented in `SearchIndex._rank_results`.

### Complete Example

Here is the full script combining all the steps above:

```python
from app.db.repository import BookmarkRepository
from app.services.search_service import SearchIndex
from app.models.bookmark import Bookmark

def run_search_demo():
    # 1. Setup
    repo = BookmarkRepository()
    search_index = SearchIndex(repo)

    # 2. Indexing
    b1 = Bookmark(
        url="https://example.com",
        title="Example Domain",
        description="This is a site for examples and testing search."
    )
    repo.save_bookmark(b1)
    search_index.index_bookmark(b1)

    # 3. Searching
    query = "example testing"
    results = search_index.search(query)

    # 4. Output
    print(f"Searching for: '{query}'")
    for b in results:
        print(f"Found: {b.title} (ID: {b.id})")

if __name__ == "__main__":
    run_search_demo()
```

### Next Steps
- Explore how `BookmarkService` wraps these calls to provide a unified API for creating and searching bookmarks simultaneously.
- Check `app/services/search_service.py` to see the list of `_STOP_WORDS` that are filtered out during indexing.
- Learn how to remove bookmarks from the index using `search_index.remove_bookmark(bookmark_id)`.