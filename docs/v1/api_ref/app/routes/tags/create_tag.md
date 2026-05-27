---
{title: POST /api/tags/api/tags/, description: API Reference for app.routes.tags.create_tag, section_id: app_routes_tags_create_tag, section_type: function_ref}
---
# POST /api/tags/api/tags/

Create a new tag.

    Expects JSON with ``name`` (required) and optional ``color``.

Creates a new tag for organizing content, requiring a unique name and an optional color identifier.

## Endpoint

```
POST /api/tags/api/tags/
```

## Request Body

| Field | Type | Description |
|-------|------|-------------|
| **name** | `string` | The unique name used to identify and label the tag. |
| **color** | `string` | An optional hexadecimal color code or string to visually distinguish the tag in the user interface. |

## Response

| Status | Description |
|--------|-------------|
| **201** | The tag was successfully created. Returns `object`. |
| **400** | The request was invalid, typically due to a missing required field or a validation error from the service layer. Returns `object`. |
