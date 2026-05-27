---
{title: PUT /api/bookmarks/< bookmark_id >, description: API Reference for app.routes.bookmarks.update_bookmark, section_id: app_routes_bookmarks_update_bookmark, section_type: function_ref}
---
# PUT /api/bookmarks/< bookmark_id >

Update an existing bookmark.

    Only the fields present in the JSON body are updated.

Updates an existing bookmark's information by its unique identifier, applying only the fields provided in the request body.

## Endpoint

```
PUT /api/bookmarks/< bookmark_id >
```

## Parameters

| Name | Type | Description |
|------|------|-------------|
| **bookmark_id** | `string` | The unique identifier of the bookmark to be updated. |

## Request Body

| Field | Type | Description |
|-------|------|-------------|
| **data** | `object` | A JSON object containing the bookmark fields to be updated. |

## Response

| Status | Description |
|--------|-------------|
| **200** | The bookmark was successfully updated. Returns `object`. |
| **400** | The update failed due to validation errors or invalid input data. Returns `object`. |
| **404** | No bookmark was found with the provided identifier. Returns `object`. |
