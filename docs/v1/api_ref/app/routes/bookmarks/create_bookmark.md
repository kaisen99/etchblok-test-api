---
{title: POST /api/bookmarks/, description: API Reference for app.routes.bookmarks.create_bookmark, section_id: app_routes_bookmarks_create_bookmark, section_type: function_ref}
---
# POST /api/bookmarks/

Create a new bookmark.

    Expects a JSON body with ``url`` (required) and ``title`` (required).

Creates a new bookmark entry for the user by providing a URL and a descriptive title.

## Endpoint

```
POST /api/bookmarks/
```

## Request Body

| Field | Type | Description |
|-------|------|-------------|
| **url** | `string` | The destination URL address for the bookmark. |
| **title** | `string` | A user-defined title or label for the bookmark. |

## Response

| Status | Description |
|--------|-------------|
| **201** | The bookmark was successfully created. Returns `object`. |
| **400** | The request was invalid or the bookmark could not be created due to a service error. Returns `object`. |
