---
title: POST /api/bookmarks/
description: API Reference for app.routes.bookmarks.create_bookmark
code_symbols: [SYM#3ebcf048f23a5377d4372a6fbe24781a5ca1230b]
section_id: app_routes_bookmarks_create_bookmark
section_type: function_ref
---
# POST /api/bookmarks/

Create a new bookmark.

    Expects a JSON body with ``url`` (required) and ``title`` (required).

Creates a new bookmark entry for the user based on the provided URL and title.

## Endpoint

```
POST /api/bookmarks/
```

## Request Body

| Field | Type | Description |
|-------|------|-------------|
| **url** | `string` | The full URL address that the bookmark will point to. |
| **title** | `string` | The descriptive name or label assigned to the bookmark. |

## Response

| Status | Description |
|--------|-------------|
| **201** | The bookmark was successfully created. Returns `object`. |
| **400** | The request was invalid, typically due to missing required fields or validation errors from the service layer. Returns `object`. |
