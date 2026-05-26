---
{title: POST /api/collections/, description: API Reference for app.routes.collections.create_collection, section_id: app_routes_collections_create_collection, section_type: function_ref}
---
# POST /api/collections/

Create a new collection.

    Expects JSON with ``name`` (required) and optional ``type`` (manual|smart)
    and ``filter_rule``.

Creates a new collection for organizing items, supporting both manual and smart collection types with optional filtering rules.

## Endpoint

```
POST /api/collections/
```

## Request Body

| Field | Type | Description |
|-------|------|-------------|
| **name** | `string` | The required display name for the new collection. |
| **type** | `string` | The classification of the collection, such as 'manual' or 'smart'. |
| **filter_rule** | `string` | The logic or criteria used to automatically populate items in a smart collection. |

## Response

| Status | Description |
|--------|-------------|
| **201** | The collection was successfully created. Returns `object`. |
| **400** | The request was invalid or the collection could not be created due to provided data errors. Returns `object`. |
