---
{title: POST /api/collections/collections/, description: API Reference for app.routes.collections.create_collection, section_id: app_routes_collections_create_collection, section_type: function_ref}
---
# POST /api/collections/collections/

Create a new collection.

    Expects JSON with ``name`` (required) and optional ``type`` (manual|smart)
    and ``filter_rule``.

Creates a new collection resource within the system, allowing for either manual organization or rule-based smart filtering.

## Endpoint

```
POST /api/collections/collections/
```

## Request Body

| Field | Type | Description |
|-------|------|-------------|
| **name** | `string` | The display name used to identify the collection. |
| **type** | `string` | The classification of the collection, determining if items are added manually or automatically via smart rules. |
| **filter_rule** | `string` | The logic or criteria used to automatically populate the collection when the type is set to smart. |

## Response

| Status | Description |
|--------|-------------|
| **201** | The collection was successfully created. Returns `object`. |
| **400** | The request was invalid, typically due to missing required fields or validation errors in the service layer. Returns `object`. |
