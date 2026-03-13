---
{title: POST /, description: API Reference for app.routes.collections.create_collection, section_id: app_routes_collections_create_collection, section_type: function_ref}
---
# POST /

Create a new collection.

    Expects JSON with ``name`` (required) and optional ``type`` (manual|smart)
    and ``filter_rule``.

Create a new collection.

## Endpoint

```
POST /
```

## Request Body

| Field | Type | Description |
|-------|------|-------------|
| **name** | `string` | The unique name for the new collection |
| **type** | `string` | The collection type, either "manual" or "smart" |
| **filter_rule** | `string` | The rule used to automatically populate the collection if type is "smart" |

## Response

| Status | Description |
|--------|-------------|
| **201** | Collection successfully created Returns `object`. |
| **400** | Invalid request data or validation error Returns `object`. |