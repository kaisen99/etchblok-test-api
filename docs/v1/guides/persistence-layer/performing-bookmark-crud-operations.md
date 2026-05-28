---
title: Performing Bookmark CRUD Operations
description: Step-by-step instructions on how to create, retrieve, update, and delete bookmarks using the repository.
code_symbols: [SYM#adb8232356346a5957ff3a1a1b7ff70581f37649]
section_id: 39c0bd7e-6701-4321-b0b0-57f152d35107_performing_bookmark_crud_operations
doc_type: how_to
section_type: guide
---
To perform CRUD (Create, Read, Update, Delete) operations on bookmarks, you interact with the `BookmarkRepository`. This repository acts as an in-memory data access layer, providing a clean interface for managing `Bookmark` entities.

### Creating and Saving Bookmarks

The `save_bookmark` method is used for both inserting new bookmarks and updating existing ones. If a bookmark with the same ID already exists, it is overwritten.

```python
from app.db.repository import BookmarkRepository
from app.models.bookmark import Bookmark

repo = BookmarkRepository()

# Create a new bookmark instance
new_bookmark = Bookmark(
    url="https://example.com",
    title="Example Domain",
    description="A simple example website"
)

# Persist to the repository
repo.save_bookmark(new_bookmark)
```

### Retrieving Bookmarks

You can retrieve a single bookmark by its unique ID or fetch a paginated list of bookmarks with optional status filtering.

```python
# Retrieve a single bookmark by ID
bookmark = repo.get_bookmark("some-id-123")
if bookmark:
    print(f"Found: {bookmark.title}")

# List bookmarks with pagination and status filtering
# Returns a Tuple: (List[Bookmark], total_count)
bookmarks, total = repo.list_bookmarks(
    page=1, 
    per_page=10, 
    status="active"
)
```

The `list_bookmarks` method supports the following parameters:
- `page`: 1-based index for pagination.
- `per_page`: Number of items to return per page (default is 25).
- `status`: Filter by `BookmarkStatus` values: `"active"`, `"archived"`, or `"trashed"`.

### Updating Bookmarks

To update a bookmark, retrieve it, modify its attributes, and call `save_bookmark` again. It is recommended to call the internal `_touch()` method (or use the service layer's update logic) to refresh the `updated_at` timestamp.

```python
bookmark = repo.get_bookmark("some-id-123")
if bookmark:
    bookmark.title = "Updated Title"
    bookmark.description = "Updated description"
    
    # Update the modification timestamp
    bookmark._touch()
    
    # Persist changes
    repo.save_bookmark(bookmark)
```

### Deleting Bookmarks

The repository provides a `delete_bookmark` method which performs a **hard delete**, removing the object entirely from memory.

```python
# Hard-delete a bookmark
success = repo.delete_bookmark("some-id-123")
if success:
    print("Bookmark permanently removed.")
```

> [!IMPORTANT]
> In this codebase, the `BookmarkService.delete_bookmark` method implements a **soft delete** pattern by moving the bookmark to the trash (`bookmark.trash()`) and saving it, rather than calling the repository's `delete_bookmark` method.

### Retrieving Bookmarks by Tag

The repository allows you to find all bookmarks associated with a specific tag ID.

```python
# Get all bookmarks that have the tag 'python'
python_bookmarks = repo.get_bookmarks_with_tag("python")
for b in python_bookmarks:
    print(b.url)
```

### Troubleshooting and Gotchas

- **In-Memory Storage**: The `BookmarkRepository` stores data in Python dictionaries (`self._bookmarks`). All data is lost when the application process restarts.
- **Pagination Indexing**: The `page` parameter in `list_bookmarks` is **1-based**. Providing a `page` of 0 or less may result in unexpected slicing behavior.
- **Silent Filter Failures**: If an invalid status string is passed to `list_bookmarks`, the filter is silently ignored, and the method returns bookmarks of all statuses.
- **Immediate Persistence**: Because the storage is in-memory, there is no transaction management. Calls to `save_bookmark` or `delete_bookmark` take effect immediately.
