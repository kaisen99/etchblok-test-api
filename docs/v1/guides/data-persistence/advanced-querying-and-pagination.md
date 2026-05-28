---
title: Advanced Querying and Pagination
description: Explains how to use the repository to filter bookmarks by status and retrieve paginated results.
code_symbols: [SYM#adb8232356346a5957ff3a1a1b7ff70581f37649]
section_id: c10e3cb9-9fd4-4191-a794-00f7d4c4ae3c_advanced_querying_and_pagination
doc_type: guide
section_type: guide
---
The `BookmarkRepository` provides a robust interface for querying bookmarks with support for pagination and status-based filtering. Because the repository is currently an in-memory implementation, these operations are performed directly on the internal dictionary of bookmarks, ensuring high performance for the current scale of the application.

### The `list_bookmarks` Method

The primary entry point for advanced querying is the `list_bookmarks` method in `app.db.repository.BookmarkRepository`. It returns a slice of the data along with the total count of matching items, which is essential for building paginated user interfaces.

```python
def list_bookmarks(
    self,
    page: int = 1,
    per_page: int = 25,
    status: Optional[str] = None,
) -> Tuple[List[Bookmark], int]:
    """Return a paginated slice of bookmarks."""
    items = list(self._bookmarks.values())
    
    # 1. Filtering
    if status:
        try:
            target = BookmarkStatus(status)
            items = [b for b in items if b.status == target]
        except ValueError:
            # Invalid status strings are silently ignored
            pass
            
    # 2. Sorting
    items.sort(key=lambda b: b.created_at, reverse=True)
    
    # 3. Pagination
    total = len(items)
    start = (page - 1) * per_page
    return items[start : start + per_page], total
```

### Filtering by Status

The repository uses the `BookmarkStatus` enum (defined in `app.models.bookmark`) to filter results. The supported status strings are:
- `active`
- `archived`
- `trashed`

A key implementation detail is that the repository handles invalid status strings gracefully. If a string is passed that does not match a valid `BookmarkStatus`, the `ValueError` is caught, and the filter is simply not applied, returning results for all statuses instead.

### Pagination Logic

Pagination in this codebase is **1-based**. The `page` parameter starts at 1, and the offset calculation `(page - 1) * per_page` ensures that the correct slice of the list is returned.

- **Default Page Size**: 25 items.
- **Sorting**: Results are always sorted by `created_at` in descending order (newest first) before the pagination slice is taken. This ensures consistent results across different pages.

### Integration Flow

The querying logic flows from the API layer through the service layer to the repository.

1.  **Route Layer (`app.routes.bookmarks`)**: Extracts query parameters from the request.
    ```python
    @bookmarks_bp.route("/", methods=["GET"])
    def list_bookmarks():
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 25, type=int)
        status = request.args.get("status", None)
        bookmarks, total = _service.list_bookmarks(page=page, per_page=per_page, status=status)
        return jsonify({"bookmarks": [b.to_dict() for b in bookmarks], "total": total})
    ```
2.  **Service Layer (`app.services.bookmark_service`)**: The `BookmarkService` acts as a facade, delegating the call directly to the repository.
3.  **Repository Layer (`app.db.repository`)**: Performs the actual filtering, sorting, and slicing of the in-memory data.

### Performance Considerations

Since the `BookmarkRepository` stores data in a dictionary (`self._bookmarks`), the `list_bookmarks` method must convert these values to a list and sort them on every call. While efficient for the current in-memory usage, this pattern establishes the contract that any future database-backed repository implementation must follow to support the API's pagination and filtering requirements.
