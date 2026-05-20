---
title: Performing Bookmark CRUD Operations
description: Step-by-step instructions on how to create, retrieve, update, and delete bookmarks using the repository.
code_symbols: [SYM#adb8232356346a5957ff3a1a1b7ff70581f37649]
section_id: 296bd30f-6b95-4dde-bc0f-8dd5a7f9289d_performing_bookmark_crud_operations
doc_type: how_to
section_type: guide
---
You can perform CRUD operations on bookmarks using the `BookmarkRepository`. This repository provides an in-memory data access layer for bookmarks, tags, and collections.

### Creating and Saving a Bookmark

To create a bookmark, instantiate a `Bookmark` model and pass it to the `save_bookmark` method. The repository uses an "upsert" pattern where `save_bookmark` handles both new entries and updates to existing ones.

```python
from app.models.bookmark import Bookmark
from app.db.repository import BookmarkRepository

repo = BookmarkRepository()

# Create a bookmark instance
bookmark = Bookmark.from_dict({
    "url": "https://example.com",
    "title": "Example Domain",
    "description": "A site for examples"
})

# Persist to the repository
repo.save_bookmark(bookmark)
```

### Retrieving a Bookmark

Retrieve a single bookmark by its unique ID using `get_bookmark`. This returns the `Bookmark` instance or `None` if not found.

```python
bookmark_id = "some-unique-id"
bookmark = repo.get_bookmark(bookmark_id)

if bookmark:
    print(f"Found: {bookmark.title}")
```

### Updating a Bookmark

To update a bookmark, retrieve it, modify its attributes, and call `save_bookmark` again. The repository identifies the record by its `id` attribute.

```python
bookmark = repo.get_bookmark("some-id")
if bookmark:
    bookmark.title = "Updated Title"
    bookmark.description = "New description"
    
    # Persist changes
    repo.save_bookmark(bookmark)
```

### Listing and Filtering Bookmarks

The `list_bookmarks` method provides pagination and status filtering. It returns a tuple containing the list of items for the current page and the total count of matching items.

```python
# List active bookmarks, page 1, 10 per page
items, total = repo.list_bookmarks(page=1, per_page=10, status="active")

for b in items:
    print(f"{b.title} ({b.url})")

print(f"Total active bookmarks: {total}")
```

You can also retrieve all bookmarks associated with a specific tag:

```python
tag_id = "work-tag-id"
work_bookmarks = repo.get_bookmarks_with_tag(tag_id)
```

### Deleting a Bookmark

The repository supports a "hard delete" which permanently removes the record from memory.

```python
success = repo.delete_bookmark("some-id")
if success:
    print("Bookmark permanently removed.")
```

> [!IMPORTANT]
> In this codebase, the `BookmarkService` typically performs a "soft delete" by moving bookmarks to the trash status instead of calling `repo.delete_bookmark`. To soft delete, use `bookmark.trash()` and then `repo.save_bookmark(bookmark)`.

### Managing Tags and Collections

The `BookmarkRepository` also manages `Tag` and `Collection` entities using similar CRUD patterns.

```python
from app.models.tag import Tag
from app.models.collection import Collection

# Save a new tag
new_tag = Tag(name="Research", color="blue")
repo.save_tag(new_tag)

# Save a new collection
collection = Collection(name="Project Alpha")
repo.save_collection(collection)

# Retrieve all tags or collections
all_tags = repo.list_tags()
all_collections = repo.list_collections()
```

### Troubleshooting

*   **Data Persistence**: The `BookmarkRepository` is in-memory only. All data is lost when the application process restarts.
*   **Validation**: The repository does not validate data (e.g., URL format or title length). Validation is handled by the `Bookmark` model's `from_dict` method or the `BookmarkService` layer.
*   **Sorting**: `list_bookmarks` automatically sorts results by `created_at` in descending order (newest first).
*   **Hard vs Soft Delete**: If you use `delete_bookmark`, the record is gone. If you want to support a "Trash" feature, update the bookmark's `status` to `BookmarkStatus.TRASHED` and save it instead.