---
{title: DELETE /api/collections/< collection_id >/bookmarks/< bookmark_id >, description: API Reference for app.routes.collections.remove_bookmark_from_collection, section_id: app_routes_collections_remove_bookmark_from_collection, section_type: function_ref}
---
# DELETE /api/collections/< collection_id >/bookmarks/< bookmark_id >

Remove a bookmark from a collection.

Removes a specific bookmark from a collection by their respective identifiers.

## Endpoint

```
DELETE /api/collections/< collection_id >/bookmarks/< bookmark_id >
```

## Parameters

| Name | Type | Description |
|------|------|-------------|
| **collection_id** | `string` | The unique identifier of the collection from which the bookmark will be removed. |
| **bookmark_id** | `string` | The unique identifier of the bookmark to be removed from the collection. |

## Response

| Status | Description |
|--------|-------------|
| **204** | The bookmark was successfully removed from the collection. |
| **404** | The specified collection or bookmark could not be found. Returns `object`. |