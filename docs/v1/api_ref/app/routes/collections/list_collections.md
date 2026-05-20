---
{title: GET /api/collections/, description: API Reference for app.routes.collections.list_collections, section_id: app_routes_collections_list_collections, section_type: function_ref}
---
# GET /api/collections/

List all collections with their bookmark counts.

Retrieves a list of all existing bookmark collections including their associated metadata and bookmark counts.

## Endpoint

```
GET /api/collections/
```

## Response

| Status | Description |
|--------|-------------|
| **200** | Successfully retrieved the list of collections. Returns `application/json`. |