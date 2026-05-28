---
title: PUT /api/collections/< collection_id >/bookmarks
description: API Reference for app.routes.collections.add_bookmark_to_collection
code_symbols: [SYM#91a8a75c1e72351e2c510365af1e59a9984f66f8]
section_id: app_routes_collections_add_bookmark_to_collection
section_type: function_ref
---
# PUT /api/collections/< collection_id >/bookmarks

Add a bookmark to a collection.

    Expects JSON with ``bookmark_id``.

Adds an existing bookmark to a specific collection by its unique identifier.

## Endpoint

```
PUT /api/collections/< collection_id >/bookmarks
```

## Parameters

| Name | Type | Description |
|------|------|-------------|
| **collection_id** | `string` | The unique identifier of the collection where the bookmark will be added. |

## Request Body

| Field | Type | Description |
|-------|------|-------------|
| **bookmark_id** | `string` | The unique identifier of the bookmark to be added to the collection. |

## Response

| Status | Description |
|--------|-------------|
| **204** | The bookmark was successfully added to the collection. Returns `null`. |
| **400** | Returned if the bookmark_id is missing, the collection does not exist, or the bookmark is already present in the collection. Returns `object`. |
