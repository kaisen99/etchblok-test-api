---
{title: DELETE /< bookmark_id >, description: API Reference for app.routes.bookmarks.delete_bookmark, section_id: app_routes_bookmarks_delete_bookmark, section_type: function_ref}
---
# DELETE /< bookmark_id >

Soft-delete a bookmark (moves to trash).

Soft-deletes a specific bookmark by moving it to the trash based on the provided identifier.

## Endpoint

```
DELETE /< bookmark_id >
```

## Parameters

| Name | Type | Description |
|------|------|-------------|
| **bookmark_id** | `string` | The unique identifier of the bookmark to be soft-deleted. |

## Response

| Status | Description |
|--------|-------------|
| **204** | The bookmark was successfully deleted. Returns `null`. |
| **404** | The specified bookmark identifier does not exist in the system. Returns `object`. |