---
{title: POST /api/collections/, description: API Reference for app.routes.collections.create_collection, section_id: app_routes_collections_create_collection, section_type: function_ref}
---
# POST /api/collections/

Create a new collection.

    Expects JSON with ``name`` (required) and optional ``type`` (manual|smart)
    and ``filter_rule``.

Creates a new collection for organizing bookmarks, supporting both manual and smart collection types.

## Endpoint

```
POST /api/collections/
```

## Request Body

| Field | Type | Description |
|-------|------|-------------|
| **name** | `string` | The display name of the collection to be created. |
| **type** | `string` | The classification of the collection, such as 'manual' for user-curated lists or 'smart' for automated filtering. |
| **filter_rule** | `string` | The logic or criteria used to automatically populate bookmarks if the collection type is set to 'smart'. |

## Response

| Status | Description |
|--------|-------------|
| **201** | The collection was successfully created. Returns `object`. |
| **400** | The request was invalid, typically due to missing required fields or validation errors in the service layer. Returns `object`. |