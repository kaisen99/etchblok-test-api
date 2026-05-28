---
{title: POST /api/bookmarks/< bookmark_id >/archive, description: API Reference for app.routes.bookmarks.archive_bookmark, section_id: app_routes_bookmarks_archive_bookmark, section_type: function_ref}
---
# POST /api/bookmarks/< bookmark_id >/archive

Archive a bookmark.

Archives an existing bookmark by its unique identifier to hide it from the primary list without permanent deletion.

## Endpoint

```
POST /api/bookmarks/< bookmark_id >/archive
```

## Parameters

| Name | Type | Description |
|------|------|-------------|
| **bookmark_id** | `string` | The unique identifier of the bookmark to be archived. |

## Response

| Status | Description |
|--------|-------------|
| **200** | The bookmark was successfully archived. Returns `object`. |
| **404** | The specified bookmark ID does not exist in the system. Returns `object`. |
