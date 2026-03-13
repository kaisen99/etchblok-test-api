---
{title: GET /< collection_id >, description: API Reference for app.routes.collections.get_collection, section_id: app_routes_collections_get_collection, section_type: function_ref}
---
# GET /< collection_id >

Get a collection and its bookmarks.

Retrieves the details of a specific collection along with its associated bookmarks.

## Endpoint

```
GET /< collection_id >
```

## Parameters

| Name | Type | Description |
|------|------|-------------|
| **collection_id** | `string` | The unique identifier of the collection to be retrieved. |

## Response

| Status | Description |
|--------|-------------|
| **200** | The collection was successfully found and returned. Returns `object`. |
| **404** | No collection exists with the provided identifier. Returns `object`. |