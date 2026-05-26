---
title: Filtering and Pagination
description: A guide to using the repository's built-in pagination and status-based filtering to efficiently query large datasets.
code_symbols: [SYM#adb8232356346a5957ff3a1a1b7ff70581f37649]
section_id: 9996ea84-6674-4de2-92b6-3aedf47be263_filtering_and_pagination
doc_type: guide
section_type: guide
---
The `BookmarkRepository` provides a robust mechanism for querying bookmarks through a combination of status-based filtering, chronological sorting, and offset-based pagination. This implementation ensures that even as the in-memory dataset grows, the application can efficiently serve specific subsets of data to the frontend or API consumers.

## The Query Engine: `list_bookmarks`

The primary entry point for retrieving multiple bookmarks is the `list_bookmarks` method in `app.db.repository.BookmarkRepository`. Unlike simple list accessors, this method performs three distinct operations on the internal `_bookmarks` dictionary:

1.  **Filtering**: Narrowing the dataset based on the bookmark's lifecycle state.
2.  **Sorting**: Ordering the results by creation time.
3.  **Pagination**: Slicing the ordered list into manageable chunks.

```python
def list_bookmarks(
    self,
    page: int = 1,
    per_page: int = 25,
    status: Optional[str] = None,
) -> Tuple[List[Bookmark], int]:
    # 1. Convert dictionary values to a list for processing
    items = list(self._bookmarks.values())
    
    # 2. Apply Status Filtering
    if status:
        try:
            target = BookmarkStatus(status)
            items = [b for b in items if b.status == target]
        except ValueError:
            # If status is invalid, the filter is ignored
            pass
            
    # 3. Apply Sorting (Hardcoded to created_at DESC)
    items.sort(key=lambda b: b.created_at, reverse=True)
    
    # 4. Calculate Pagination
    total = len(items)
    start = (page - 1) * per_page
    return items[start : start + per_page], total
```

## Status-Based Filtering

Filtering is driven by the `BookmarkStatus` enumeration found in `app.models.bookmark`. The repository maps string inputs to these enum members to ensure type safety during the filtering process.

### Supported Statuses
The system recognizes three specific states defined in `BookmarkStatus`:
- `active`: The default state for new bookmarks.
- `archived`: Bookmarks moved out of the main view but preserved.
- `trashed`: Bookmarks marked for deletion (soft-delete).

The repository handles invalid status strings gracefully. If a string is provided that does not match a value in `BookmarkStatus`, the `ValueError` is caught, and the repository returns the full list (unfiltered) rather than raising an error.

## Pagination Logic

The repository implements **1-based offset pagination**. This means the first page is requested as `page=1`, not `page=0`.

### Offset Calculation
The starting index for the list slice is calculated as:
`start = (page - 1) * per_page`

The method returns a `Tuple[List[Bookmark], int]`, where the second element is the **total count of matching items** before pagination was applied. This is critical for frontend components to calculate the total number of available pages.

### Default Constraints
While the repository itself does not enforce a maximum `per_page` limit, the API layer in `app/routes/bookmarks.py` typically defaults to 25 items per page.

## Chronological Sorting

The repository enforces a strict sorting policy: bookmarks are always returned in **descending order of creation** (`created_at`). This ensures that the most recently added bookmarks appear first in the results. This sorting is applied *after* filtering but *before* pagination slicing to ensure consistency across page boundaries.

## Integration Flow

The filtering and pagination parameters typically originate from the REST API and flow through the service layer to the repository.

### API Route Example
In `app/routes/bookmarks.py`, query parameters are extracted and passed to the `BookmarkService`:

```python
@bookmarks_bp.route("/", methods=["GET"])
def list_bookmarks():
    # Extract parameters from URL query string
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 25, type=int)
    status = request.args.get("status", None)
    
    # Delegate to service, which calls the repository
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

### Service Layer Role
The `BookmarkService` in `app/services/bookmark_service.py` acts as a facade. While it currently passes these parameters directly to the `BookmarkRepository`, it provides the hook point for adding caching or cross-cutting concerns to paginated queries. For example, while individual bookmarks are cached in an `LRUCache`, the `list_bookmarks` operation always queries the repository directly to ensure the most up-to-date filtered results.
