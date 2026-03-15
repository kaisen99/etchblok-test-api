---
title: Managing Bookmark Data
description: Instructions on how to perform CRUD operations on bookmarks, including status filtering and pagination.
code_symbols: [SYM#adb8232356346a5957ff3a1a1b7ff70581f37649]
section_id: c0f1339d-449a-47a8-93ac-9d839f797af9_managing_bookmark_data
doc_type: how_to
section_type: guide
---
To manage bookmark data in this application, you interact with the `BookmarkRepository` class. This repository provides an in-memory storage abstraction for bookmarks, tags, and collections, supporting CRUD operations, status-based filtering, and pagination.

## Creating and Updating Bookmarks

There are two ways to persist bookmark data: using the low-level `BookmarkRepository` directly or using the `BookmarkService` facade.

### Using the Repository (Direct Access)
The repository's `save_bookmark` method handles both insertion and updates. It expects a `Bookmark` model instance and performs no validation.

```python
from app.db.repository import BookmarkRepository
from app.models.bookmark import Bookmark

repo = BookmarkRepository()

# Create a new instance
new_bookmark = Bookmark(
    url="https://example.com",
    title="Example Domain"
)

# Persist to in-memory storage
repo.save_bookmark(new_bookmark)
```

### Using the Service (Recommended)
The `BookmarkService` in `app/services/bookmark_service.py` is the preferred interface. It handles validation (via `_validate_url` and `_validate_title`), updates the search index, and manages the cache.

```python
from app.services.bookmark_service import BookmarkService

service = BookmarkService()

# Create via dictionary (includes validation and indexing)
bookmark, error = service.create_bookmark({
    "url": "https://github.com",
    "title": "GitHub",
    "description": "Development platform"
})

if error:
    print(f"Validation failed: {error}")
```

## Retrieving and Filtering Bookmarks

The repository provides methods for both single-item retrieval and paginated listing.

### Single Item Retrieval
```python
# Get by ID (returns None if not found)
bookmark = repo.get_bookmark("bookmark-id-123")
```

### Paginated Listing with Status Filtering
The `list_bookmarks` method returns a tuple containing a list of items and the total count of matching records. Results are always sorted by `created_at` in descending order.

```python
from app.models.bookmark import BookmarkStatus

# Retrieve the first page of active bookmarks
# Returns (List[Bookmark], total_count)
bookmarks, total = repo.list_bookmarks(
    page=1, 
    per_page=10, 
    status="active"
)

# Valid status strings: "active", "archived", "trashed"
archived_items, _ = repo.list_bookmarks(status="archived")
```

## Deleting Bookmarks

This project distinguishes between "soft" and "hard" deletes.

### Soft Delete (Trashing)
The `BookmarkService` performs a soft delete by moving the bookmark to the "trash" status. This keeps the data in the repository but excludes it from "active" listings.

```python
# Soft delete via service
service.delete_bookmark("bookmark-id-123")

# Equivalent manual operation on the model
bookmark = repo.get_bookmark("bookmark-id-123")
if bookmark:
    bookmark.trash()
    repo.save_bookmark(bookmark)
```

### Hard Delete (Removal)
The `BookmarkRepository.delete_bookmark` method removes the record entirely from the in-memory storage.

```python
# Permanently remove from memory
existed = repo.delete_bookmark("bookmark-id-123")
```

## Managing Tags and Collections

The repository also manages `Tag` and `Collection` entities, which are used to organize bookmarks.

### Working with Tags
```python
from app.models.tag import Tag, TagColor

# Create and save a tag
new_tag = Tag(name="Research", color=TagColor.BLUE)
repo.save_tag(new_tag)

# Find all bookmarks associated with this tag
tagged_bookmarks = repo.get_bookmarks_with_tag(new_tag.id)
```

### Working with Collections
```python
from app.models.collection import Collection

# Create a collection
collection = Collection(name="Project Alpha")
repo.save_collection(collection)

# Add a bookmark to the collection via service
service.add_to_collection(collection.id, "bookmark-id-123")
```

## Diagnostics and Testing

The repository includes internal helpers for checking state and resetting data during tests.

```python
# Get counts of all entities
counts = repo._count_all()
print(f"Bookmarks: {counts['bookmarks']}")

# Wipe all data (used in test teardowns)
repo._clear_all()
```

## Troubleshooting

*   **Data Persistence:** The `BookmarkRepository` is entirely in-memory. All data is lost when the application process terminates.
*   **Invalid Status Filters:** If an invalid string is passed to the `status` parameter in `list_bookmarks`, the repository catches the `ValueError` and silently ignores the filter, returning bookmarks of all statuses.
*   **Search Index Sync:** If you use `repo.save_bookmark` directly instead of `service.create_bookmark`, the `SearchIndex` will not be updated automatically. You must manually call `service._search.index_bookmark(bookmark)` to keep search results accurate.
*   **Pagination Limits:** The `list_bookmarks` method uses list slicing. While efficient for small in-memory datasets, performance may degrade if the `_bookmarks` dictionary grows to tens of thousands of entries.