---
title: Filtering and Pagination
description: Learn how to use the repository to fetch paginated results and filter bookmarks by status or tags.
code_symbols: [SYM#adb8232356346a5957ff3a1a1b7ff70581f37649]
section_id: 68589dcd-b7b8-458c-ae78-a1ccd8960a2f_filtering_and_pagination
doc_type: how_to
section_type: guide
---
To fetch paginated results and filter bookmarks by status or tags in this project, you primarily interact with the `BookmarkRepository` via the `BookmarkService`.

### Fetching Paginated Bookmarks

Use the `list_bookmarks` method to retrieve a slice of bookmarks. This method handles both pagination and status filtering, returning a tuple containing the list of items and the total count of matching records.

```python
from app.db.repository import BookmarkRepository

repo = BookmarkRepository()

# Fetch the first page of active bookmarks (25 per page)
bookmarks, total = repo.list_bookmarks(
    page=1, 
    per_page=25, 
    status="active"
)

print(f"Showing {len(bookmarks)} of {total} total active bookmarks.")
```

### Filtering by Status

The `status` parameter in `list_bookmarks` accepts strings that correspond to the `BookmarkStatus` enum values: `active`, `archived`, or `trashed`.

*   **Active**: Default status for new bookmarks.
*   **Archived**: Bookmarks moved out of the main list but not deleted.
*   **Trashed**: Soft-deleted bookmarks.

If an invalid status string is provided, the repository catches the `ValueError` and returns results without applying a status filter.

```python
# Fetch archived bookmarks
archived_items, count = repo.list_bookmarks(status="archived")

# Fetch trashed bookmarks
trashed_items, count = repo.list_bookmarks(status="trashed")
```

### Filtering by Tags

To find all bookmarks associated with a specific tag, use the `get_bookmarks_with_tag` method. Unlike `list_bookmarks`, this method returns a simple list of all matching bookmarks without built-in pagination.

```python
# Get all bookmarks tagged with 'python-docs'
tag_id = "python-docs"
tagged_bookmarks = repo.get_bookmarks_with_tag(tag_id)

for b in tagged_bookmarks:
    print(f"Found: {b.title} ({b.url})")
```

This pattern is used internally by `BookmarkService.delete_tag` to clean up references when a tag is removed:

```python
# Example from app/services/bookmark_service.py
def delete_tag(self, tag_id: str) -> bool:
    # ...
    for bookmark in self._repo.get_bookmarks_with_tag(tag_id):
        bookmark.remove_tag(tag_id)
        self._repo.save_bookmark(bookmark)
    # ...
```

### API Integration Example

In a Flask route, you can expose these features by passing query parameters from the request to the `BookmarkService`.

```python
from flask import request, jsonify
from app.services.bookmark_service import BookmarkService

_service = BookmarkService()

@bookmarks_bp.route("/", methods=["GET"])
def list_bookmarks():
    # Extract parameters with defaults
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 25, type=int)
    status = request.args.get("status", None)

    # Delegate to service (which calls repository)
    bookmarks, total = _service.list_bookmarks(
        page=page, 
        per_page=per_page, 
        status=status
    )

    return jsonify({
        "bookmarks": [b.to_dict() for b in bookmarks], 
        "total": total
    })
```

### Troubleshooting and Implementation Details

*   **1-Based Indexing**: The `page` parameter is 1-indexed. Requesting `page=1` returns the first set of results.
*   **Hardcoded Sorting**: Results in `list_bookmarks` are always sorted by `created_at` in descending order (newest first).
*   **In-Memory Storage**: The `BookmarkRepository` stores data in-memory. All filters and pagination are performed on Python lists (`self._bookmarks.values()`). Data is lost when the application restarts.
*   **Tag Filter Performance**: `get_bookmarks_with_tag` performs a linear scan of all bookmarks in memory. While efficient for small datasets, performance may degrade if the number of bookmarks grows significantly.
*   **Invalid Status**: If you pass a status that does not exist in `BookmarkStatus`, the filter is silently ignored, and you will receive bookmarks of all statuses.