---
title: POST /api/bookmarks/< bookmark_id >/restore
description: API Reference for app.routes.bookmarks.restore_bookmark
code_symbols: [SYM#97d1a96c6acd5581926556cfcc7388d8d3e45420]
section_id: app_routes_bookmarks_restore_bookmark
section_type: function_ref
---
# POST /api/bookmarks/< bookmark_id >/restore

Restore a bookmark from archive or trash.

Restores a previously archived or trashed bookmark to its active state using its unique identifier.

## Endpoint

```
POST /api/bookmarks/< bookmark_id >/restore
```

## Parameters

| Name | Type | Description |
|------|------|-------------|
| **bookmark_id** | `string` | The unique identifier of the bookmark to be restored. |

## Response

| Status | Description |
|--------|-------------|
| **200** | The bookmark was successfully restored. Returns `object`. |
| **404** | The bookmark with the specified ID could not be found. Returns `object`. |
