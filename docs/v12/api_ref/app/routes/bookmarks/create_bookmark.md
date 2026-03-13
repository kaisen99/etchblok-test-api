---
{title: create_bookmark, description: API Reference for app.routes.bookmarks.create_bookmark, section_id: app_routes_bookmarks_create_bookmark, section_type: function_ref}
---
# create_bookmark

Create a new bookmark.

    Expects a JSON body with ``url`` (required) and ``title`` (required).

Create a new bookmark. Expects a JSON body with ``url`` (required) and ``title`` (required).

## Returns

| Type | Description |
|------|-------------|
| `object` | A JSON object containing the newly created bookmark details or an error message. |