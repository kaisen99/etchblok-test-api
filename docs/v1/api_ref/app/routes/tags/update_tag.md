---
title: PUT /api/tags/< tag_id >
description: API Reference for app.routes.tags.update_tag
code_symbols: [SYM#c5e70449a6d0f7b769b90bb12453a7342673bb15]
section_id: app_routes_tags_update_tag
section_type: function_ref
---
# PUT /api/tags/< tag_id >

Rename or recolour a tag.

Updates the properties of an existing tag, such as its name or color, based on the provided identifier.

## Endpoint

```
PUT /api/tags/< tag_id >
```

## Parameters

| Name | Type | Description |
|------|------|-------------|
| **tag_id** | `string` | The unique identifier of the tag to be updated. |

## Request Body

| Field | Type | Description |
|-------|------|-------------|
| **name** | `string` | The new name to assign to the tag. |
| **color** | `string` | The new hex code or color name to assign to the tag. |

## Response

| Status | Description |
|--------|-------------|
| **200** | The tag was successfully updated and the updated object is returned. Returns `object`. |
| **400** | The update failed due to validation errors or invalid data in the request body. Returns `object`. |
| **404** | No tag was found matching the provided tag_id. Returns `object`. |
