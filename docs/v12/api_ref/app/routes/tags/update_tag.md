---
{title: PUT /< tag_id >, description: API Reference for app.routes.tags.update_tag, section_id: app_routes_tags_update_tag, section_type: function_ref}
---
# PUT /< tag_id >

Rename or recolour a tag.

Updates the properties of an existing tag, such as its name or color, based on the provided identifier.

## Endpoint

```
PUT /< tag_id >
```

## Parameters

| Name | Type | Description |
|------|------|-------------|
| **tag_id** | `string` | The unique identifier of the tag to be updated. |

## Request Body

| Field | Type | Description |
|-------|------|-------------|
| **data** | `object` | A JSON object containing the updated fields for the tag, such as name or color. |

## Response

| Status | Description |
|--------|-------------|
| **200** | The tag was successfully updated and the updated object is returned. Returns `object`. |
| **400** | The update failed due to invalid input data or a service error. Returns `object`. |
| **404** | No tag was found matching the provided tag identifier. Returns `object`. |