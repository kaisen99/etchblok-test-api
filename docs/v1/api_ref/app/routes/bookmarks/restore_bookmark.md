---
{title: POST /api/bookmarks/< bookmark_id >/restore, description: API Reference for app.routes.bookmarks.restore_bookmark, section_id: app_routes_bookmarks_restore_bookmark, section_type: function_ref}
---
# POST /api/bookmarks/< bookmark_id >/restore

Restore a bookmark from archive or trash.

Restores a previously archived or trashed bookmark to its active state using its unique identifier.

## Endpoint

```
POST /api/bookmarks/< bookmark_id >/restore
```

## Parameters

| Name | Type | Description |
|------|------|-------------|
| **bookmark_id** | `string` | The unique identifier of the bookmark to be restored. |

## Response

| Status | Description |
|--------|-------------|
| **200** | The bookmark was successfully found and restored. Returns `object`. |
| **404** | No bookmark was found matching the provided identifier. Returns `object`. |
