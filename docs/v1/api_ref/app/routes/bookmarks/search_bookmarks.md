---
{title: GET /api/bookmarks/search, description: API Reference for app.routes.bookmarks.search_bookmarks, section_id: app_routes_bookmarks_search_bookmarks, section_type: function_ref}
---
# GET /api/bookmarks/search

Full-text search across bookmark titles and descriptions.

Performs a full-text search across all bookmark titles and descriptions to find relevant entries based on a search string.

## Endpoint

```
GET /api/bookmarks/search
```

## Parameters

| Name | Type | Description |
|------|------|-------------|
| **q** | `string` | The search query string used to filter bookmarks by their title or description content. |
| **limit** | `integer` = 20 | The maximum number of search results to return in the response for pagination control. |

## Response

| Status | Description |
|--------|-------------|
| **200** | Successfully retrieved the list of bookmarks matching the search criteria. Returns `application/json`. |
