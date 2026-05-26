---
title: Getting Started with the Bookmark Repository
description: A step-by-step tutorial on initializing the repository and performing your first save and retrieval operations.
code_symbols: [SYM#09a56e7acb86a9afef18a62134c27802cd473050, SYM#adb8232356346a5957ff3a1a1b7ff70581f37649]
section_id: c9055394-dd33-4bca-91e4-2fb81ba4b39a_getting_started_with_the_bookmark_repository
doc_type: tutorial
section_type: guide
---
This tutorial walks you through using the `BookmarkRepository` to manage your data. You will learn how to initialize the repository, create and persist bookmarks, and retrieve them using various filtering and pagination options.

### Prerequisites

To follow this tutorial, you need to have the core models and the repository class available in your environment:

*   `BookmarkRepository` from `app.db.repository`
*   `Bookmark` and `BookmarkStatus` from `app.models.bookmark`
*   `Tag` from `app.models.tag`

### Step 1: Initialize the Repository

The `BookmarkRepository` acts as an in-memory data access layer. It provides a clean interface for CRUD operations on bookmarks, tags, and collections.

```python
from app.db.repository import BookmarkRepository

# Initialize the in-memory repository
repo = BookmarkRepository()

# Verify it's empty using the internal diagnostic helper
counts = repo._count_all()
print(f"Initial counts: {counts}")
# Output: Initial counts: {'bookmarks': 0, 'tags': 0, 'collections': 0}
```

The repository uses internal dictionaries (`_bookmarks`, `_tags`, `_collections`) to store data. Since it is currently in-memory, data will persist only for the duration of the process.

### Step 2: Create and Save a Bookmark

Next, you will create a `Bookmark` instance and save it to the repository. The `Bookmark` model requires at least a `url` and a `title`.

```python
from app.models.bookmark import Bookmark

# Create a new bookmark instance
new_bookmark = Bookmark(
    url="https://github.com/features/actions",
    title="GitHub Actions",
    description="Automation for your workflow"
)

# Persist the bookmark to the repository
repo.save_bookmark(new_bookmark)

print(f"Saved bookmark with ID: {new_bookmark.id}")
```

When you call `save_bookmark`, the repository stores the object in its internal map using the bookmark's unique `id`. If a bookmark with the same ID already exists, it is updated.

### Step 3: Retrieve a Bookmark by ID

Once saved, you can retrieve the bookmark at any time using its unique identifier.

```python
# Retrieve the bookmark we just saved
retrieved = repo.get_bookmark(new_bookmark.id)

if retrieved:
    print(f"Retrieved: {retrieved.title} ({retrieved.url})")
    print(f"Status: {retrieved.status.value}")
# Output: Retrieved: GitHub Actions (https://github.com/features/actions)
# Output: Status: active
```

The `get_bookmark` method returns the `Bookmark` object if found, or `None` if the ID does not exist in the repository.

### Step 4: Organize with Tags

The repository also manages `Tag` entities. You can create a tag and associate its ID with a bookmark.

```python
from app.models.tag import Tag, TagColor

# 1. Create and save a tag
devops_tag = Tag(name="DevOps", color=TagColor.BLUE)
repo.save_tag(devops_tag)

# 2. Associate the tag with the bookmark
retrieved.add_tag(devops_tag.id)

# 3. Update the bookmark in the repository to persist the change
repo.save_bookmark(retrieved)

# 4. Verify the association using the repository helper
bookmarks_with_tag = repo.get_bookmarks_with_tag(devops_tag.id)
print(f"Bookmarks tagged '{devops_tag.name}': {len(bookmarks_with_tag)}")
# Output: Bookmarks tagged 'DevOps': 1
```

Note that `Bookmark` objects store a list of tag IDs in their `tags` attribute. The repository's `get_bookmarks_with_tag` method performs a search through all bookmarks to find matches.

### Step 5: List and Filter Bookmarks

For displaying lists of bookmarks, the repository provides `list_bookmarks`, which supports 1-based pagination and status filtering.

```python
# Add another bookmark for pagination demo
repo.save_bookmark(Bookmark(url="https://python.org", title="Python"))

# List the first page of active bookmarks (25 items per page by default)
items, total = repo.list_bookmarks(page=1, per_page=10, status="active")

print(f"Total active bookmarks: {total}")
for item in items:
    print(f"- {item.title} (Created: {item.created_at})")
```

The `list_bookmarks` method:
1.  Filters by `status` (e.g., "active", "archived", "trashed") if provided.
2.  Sorts the results by `created_at` in descending order (newest first).
3.  Returns a tuple containing the list of items for the current page and the total count of matching items.

### Complete Working Result

By combining these steps, you have a functional data management script:

```python
from app.db.repository import BookmarkRepository
from app.models.bookmark import Bookmark
from app.models.tag import Tag

# Setup
repo = BookmarkRepository()

# Create data
tag = Tag(name="Reference")
repo.save_tag(tag)

bm = Bookmark(url="https://docs.python.org", title="Python Docs")
bm.add_tag(tag.id)
repo.save_bookmark(bm)

# Query data
results, count = repo.list_bookmarks(page=1, per_page=5)
print(f"Found {count} bookmarks. First item: {results[0].title} with tags: {results[0].tags}")
```

You can now use this repository as the foundation for more complex services, such as the `BookmarkService` or `SearchIndex`, which rely on this repository for data persistence.
