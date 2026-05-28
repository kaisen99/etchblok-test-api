---
title: GET /api/bookmarks/< bookmark_id >
description: API Reference for app.routes.bookmarks.get_bookmark
code_symbols: [SYM#8671f5c2a8b47f185a60dd92d12a6ffd4665eac2]
section_id: app_routes_bookmarks_get_bookmark
section_type: function_ref
---
# GET /api/bookmarks/< bookmark_id >

Retrieve a single bookmark by ID.

Retrieves the details of a specific bookmark using its unique identifier.

## Endpoint

```
GET /api/bookmarks/< bookmark_id >
```

## Parameters

| Name | Type | Description |
|------|------|-------------|
| **bookmark_id** | `string` | The unique identifier of the bookmark to retrieve from the database. |

## Response

| Status | Description |
|--------|-------------|
| **200** | The bookmark was successfully found and returned. Returns `object`. |
| **404** | No bookmark exists with the provided identifier. Returns `object`. |
