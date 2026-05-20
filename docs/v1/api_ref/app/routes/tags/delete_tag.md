---
{title: DELETE /api/tags/< tag_id >, description: API Reference for app.routes.tags.delete_tag, section_id: app_routes_tags_delete_tag, section_type: function_ref}
---
# DELETE /api/tags/< tag_id >

Delete a tag and remove it from all bookmarks.

Deletes a specific tag by its unique identifier and removes its association from all bookmarks.

## Endpoint

```
DELETE /api/tags/< tag_id >
```

## Parameters

| Name | Type | Description |
|------|------|-------------|
| **tag_id** | `string` | The unique identifier of the tag to be deleted. |

## Response

| Status | Description |
|--------|-------------|
| **204** | The tag was successfully deleted. |
| **404** | The specified tag identifier does not exist in the system. Returns `object`. |