---
{title: POST /api/bookmarks/, description: API Reference for app.routes.bookmarks.create_bookmark, section_id: app_routes_bookmarks_create_bookmark, section_type: function_ref}
---
# POST /api/bookmarks/

Create a new bookmark.

    Expects a JSON body with ``url`` (required) and ``title`` (required).

Creates a new bookmark entry for the user based on a provided URL and title.

## Endpoint

```
POST /api/bookmarks/
```

## Request Body

| Field | Type | Description |
|-------|------|-------------|
| **url** | `string` | The full URL of the website to be bookmarked. |
| **title** | `string` | The display title or name assigned to the bookmark. |

## Response

| Status | Description |
|--------|-------------|
| **201** | The bookmark was successfully created. Returns `object`. |
| **400** | The request was invalid, likely due to missing required fields or a malformed URL. Returns `object`. |
