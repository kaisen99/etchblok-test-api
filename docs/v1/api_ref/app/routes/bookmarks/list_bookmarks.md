---
title: GET /api/bookmarks/
description: API Reference for app.routes.bookmarks.list_bookmarks
code_symbols: [SYM#78c1893d04f589140f920602d5bbff8f291545b0]
section_id: app_routes_bookmarks_list_bookmarks
section_type: function_ref
---
# GET /api/bookmarks/

Return a paginated list of bookmarks.

Retrieves a paginated collection of bookmarks, with optional filtering by status.

## Endpoint

```
GET /api/bookmarks/
```

## Parameters

| Name | Type | Description |
|------|------|-------------|
| **page** | `int` = 1 | The page number to retrieve for paginated results. |
| **per_page** | `int` = 25 | The number of bookmark items to include in a single response page (maximum 100). |
| **status** | `string` = null | A filter to restrict results to bookmarks with a specific state, such as active, archived, or trashed. |

## Response

| Status | Description |
|--------|-------------|
| **200** | Successfully retrieved the list of bookmarks. Returns `application/json`. |
