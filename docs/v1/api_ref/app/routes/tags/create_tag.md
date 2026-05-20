---
{title: POST /api/tags/, description: API Reference for app.routes.tags.create_tag, section_id: app_routes_tags_create_tag, section_type: function_ref}
---
# POST /api/tags/

Create a new tag.

    Expects JSON with ``name`` (required) and optional ``color``.

Creates a new tag for organizing bookmarks, allowing for custom naming and optional color coding.

## Endpoint

```
POST /api/tags/
```

## Request Body

| Field | Type | Description |
|-------|------|-------------|
| **name** | `string` | The unique name of the tag to be created. |
| **color** | `string` | An optional hex code or color name to visually distinguish the tag. |

## Response

| Status | Description |
|--------|-------------|
| **201** | The tag was successfully created. Returns `object`. |
| **400** | The request was invalid, typically due to a missing name or a validation error from the service. Returns `object`. |