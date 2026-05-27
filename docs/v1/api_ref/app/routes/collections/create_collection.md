---
{title: POST /api/collections/api/collections/, description: API Reference for app.routes.collections.create_collection, section_id: app_routes_collections_create_collection, section_type: function_ref}
---
# POST /api/collections/api/collections/

Create a new collection.

    Expects JSON with ``name`` (required) and optional ``type`` (manual|smart)
    and ``filter_rule``.

Creates a new collection resource within the system using the provided configuration data.

## Endpoint

```
POST /api/collections/api/collections/
```

## Request Body

| Field | Type | Description |
|-------|------|-------------|
| **name** | `string` | The required display name for the new collection. |
| **type** | `string` | The classification of the collection, which can be set to 'manual' or 'smart'. |
| **filter_rule** | `string` | The logic or criteria used to automatically populate the collection if the type is set to 'smart'. |

## Response

| Status | Description |
|--------|-------------|
| **201** | The collection was successfully created. Returns `object`. |
| **400** | The request was invalid or the collection could not be created due to a business logic error. Returns `object`. |
