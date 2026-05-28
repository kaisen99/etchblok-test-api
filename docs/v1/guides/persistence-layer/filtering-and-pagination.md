---
title: Filtering and Pagination
description: How to use the repository to list bookmarks with status filters and paginated results.
code_symbols: [SYM#adb8232356346a5957ff3a1a1b7ff70581f37649]
section_id: 2676de11-3d9f-4271-ba22-46c0b365572d_filtering_and_pagination
doc_type: how_to
section_type: guide
---
To list bookmarks with specific filters and paginated results, use the `list_bookmarks` method provided by the `BookmarkRepository`. This method handles sorting, status filtering, and slicing the results into pages.

### Basic Pagination and Filtering

The `list_bookmarks` method returns a tuple containing the list of bookmarks for the requested page and the total count of bookmarks matching the filter (useful for calculating total pages in a UI).

```python
from app.db.repository import BookmarkRepository

repo = BookmarkRepository()

# Fetch the first page of active bookmarks (25 per page by default)
bookmarks, total = repo.list_bookmarks(
    page=1, 
    per_page=25, 
    status="active"
)

print(f"Showing {len(bookmarks)} of {total} active bookmarks.")
```

### Key Parameters and Behavior

*   **`page`**: A 1-based index. If you provide `page=1`, it starts from the beginning of the list.
*   **`per_page`**: The number of items to return in the slice.
*   **`status`**: An optional string filter. Valid values are defined in the `BookmarkStatus` enum: `"active"`, `"archived"`, or `"trashed"`.
*   **Sorting**: Results are automatically sorted by `created_at` in descending order (newest first) before pagination is applied.

### Implementation in the Service Layer

In practice, you should interact with the repository through the `BookmarkService`, which acts as a singleton facade. The service delegates the call directly to the repository:

```python
from app.services.bookmark_service import BookmarkService

service = BookmarkService()

# The service signature matches the repository signature
bookmarks, total = service.list_bookmarks(page=2, per_page=10, status="archived")
```

### Handling API Requests

When implementing an API endpoint, extract the query parameters from the request and pass them to the service. The following example from `app/routes/bookmarks.py` shows how to handle these parameters in a Flask route:

```python
from flask import Blueprint, request, jsonify
from app.services.bookmark_service import BookmarkService

bookmarks_bp = Blueprint("bookmarks", __name__)
_service = BookmarkService()

@bookmarks_bp.route("/", methods=["GET"])
def list_bookmarks():
    # Extract parameters with defaults
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 25, type=int)
    status = request.args.get("status", None)
    
    # Fetch results
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

### Troubleshooting and Edge Cases

#### Invalid Status Strings
If an invalid status string is passed to `list_bookmarks` (e.g., `status="deleted"`), the repository silently ignores the filter and returns bookmarks of all statuses. This is because the repository catches the `ValueError` when attempting to cast the string to a `BookmarkStatus` enum:

```python
# From app/db/repository.py
try:
    target = BookmarkStatus(status)
    items = [b for b in items if b.status == target]
except ValueError:
    pass  # Invalid status strings result in no filtering
```

#### Out-of-Bounds Pages
If the requested `page` and `per_page` combination results in a starting index beyond the total number of items, the method returns an empty list and the correct total count. It does not raise an error.

```python
# If total items = 10, and you request page 2 with per_page 25:
# start = (2 - 1) * 25 = 25
# items[25 : 25 + 25] returns []
bookmarks, total = repo.list_bookmarks(page=2, per_page=25)
# bookmarks is [], total is 10
```

#### Case Sensitivity
Status filtering is case-sensitive and expects lowercase strings matching the enum values (`active`, `archived`, `trashed`). Passing `"Active"` will result in the filter being ignored.
