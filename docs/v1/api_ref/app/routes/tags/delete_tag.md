---
{title: DELETE /api/tags/< tag_id >, description: API Reference for app.routes.tags.delete_tag, section_id: app_routes_tags_delete_tag, section_type: function_ref}
---
# DELETE /api/tags/< tag_id >

Delete a tag and remove it from all bookmarks.

Permanently deletes a specific tag and removes its association from all bookmarks currently using it.

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
| **204** | The tag was successfully deleted and removed from all bookmarks. |
| **404** | The specified tag ID does not exist in the system. Returns `object`. |
