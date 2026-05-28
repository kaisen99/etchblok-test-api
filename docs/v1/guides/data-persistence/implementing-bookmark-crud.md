---
title: Implementing Bookmark CRUD
description: A practical guide on how to create, retrieve, update, and delete bookmark entities using the repository.
code_symbols: [SYM#adb8232356346a5957ff3a1a1b7ff70581f37649]
section_id: c42a5e63-2fd2-444c-8e6d-7d30c989eae6_implementing_bookmark_crud
doc_type: how_to
section_type: guide
---
To manage bookmark entities in this project, you use the `BookmarkRepository` class. This repository provides an in-memory data access layer for creating, retrieving, updating, and deleting bookmarks, as well as managing tags and collections.

### Basic CRUD Operations

The `BookmarkRepository` uses a single `save_bookmark` method for both creation and updates. It persists the `Bookmark` entity immediately to an internal dictionary.

```python
from app.db.repository import BookmarkRepository
from app.models.bookmark import Bookmark

repo = BookmarkRepository()

# 1. Create a bookmark
new_bookmark = Bookmark(
    url="https://example.com",
    title="Example Domain"
)
repo.save_bookmark(new_bookmark)

# 2. Retrieve a bookmark
bookmark = repo.get_bookmark(new_bookmark.id)
if bookmark:
    print(f"Found: {bookmark.title}")

# 3. Update a bookmark
bookmark.title = "Updated Title"
repo.save_bookmark(bookmark)

# 4. Hard delete a bookmark
success = repo.delete_bookmark(bookmark.id)
```

### Listing and Filtering Bookmarks

The `list_bookmarks` method supports 1-based pagination and filtering by status (active, archived, or trashed). It returns a tuple containing the list of items and the total count of matching records.

```python
# List active bookmarks, page 1, 10 per page
bookmarks, total = repo.list_bookmarks(
    page=1, 
    per_page=10, 
    status="active"
)

print(f"Showing {len(bookmarks)} of {total} active bookmarks")
```

### Implementing Soft Delete vs. Hard Delete

In this codebase, the `BookmarkRepository` performs **hard deletes** (removing the object from memory), while the `BookmarkService` implements **soft deletes** by updating the bookmark's status to `trashed`.

#### Soft Delete (Recommended Pattern)
Use the `trash()` method on the `Bookmark` model and then save the entity. This is the pattern used in `BookmarkService.delete_bookmark`.

```python
bookmark = repo.get_bookmark("some-id")
if bookmark:
    bookmark.trash()  # Sets status to BookmarkStatus.TRASHED
    repo.save_bookmark(bookmark)
```

#### Hard Delete
Use the repository's `delete_bookmark` method to permanently remove the record.

```python
repo.delete_bookmark("some-id")
```

### Filtering by Tags

You can retrieve all bookmarks associated with a specific tag using `get_bookmarks_with_tag`.

```python
tag_id = "python-tag-id"
tagged_bookmarks = repo.get_bookmarks_with_tag(tag_id)

for b in tagged_bookmarks:
    print(f"Bookmark {b.title} has tag {tag_id}")
```

### Troubleshooting and Gotchas

*   **In-Memory Storage**: The `BookmarkRepository` is currently in-memory. All data is lost when the application process restarts.
*   **1-Based Pagination**: The `page` argument in `list_bookmarks` starts at `1`. Providing `0` or a negative number will result in incorrect slicing of the data.
*   **Default Sorting**: `list_bookmarks` automatically sorts results by `created_at` in descending order (newest first).
*   **Manual Persistence**: When modifying a `Bookmark` object (e.g., changing its title or adding a tag), you must call `repo.save_bookmark(bookmark)` to ensure the changes are "persisted" in the repository's internal storage, even though it is in-memory.
