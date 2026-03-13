---
{title: list_bookmarks, description: API Reference for app.routes.bookmarks.list_bookmarks, section_id: app_routes_bookmarks_list_bookmarks, section_type: function_ref}
---
# list_bookmarks

Return a paginated list of bookmarks.

Return a paginated list of bookmarks.

## Parameters

| Name | Type | Description |
|------|------|-------------|
| **page** | `int` = 1 | The page number to retrieve, starting from 1. |
| **per_page** | `int` = 25 | The number of items to return per page, with a maximum limit of 100. |
| **status** | `string` = null | A filter to restrict results by their current state, such as active, archived, or trashed. |

## Returns

| Type | Description |
|------|-------------|
| `object` | A JSON object containing an array of bookmark dictionaries and the total count of matching records. |