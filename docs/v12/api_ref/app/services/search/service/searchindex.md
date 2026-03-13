---
{title: SearchIndex, description: API Reference for app.services.search_service.SearchIndex, section_id: app_services_search_service_searchindex, section_type: class_ref}
---
# SearchIndex

Inverted index mapping tokens to bookmark IDs.

## Attributes

| Attribute | Type | Description |
|----------|------|-------------|
| **_repo** | `[BookmarkRepository](../../../db/repository/bookmarkrepository.md?sid=app_db_repository_bookmarkrepository)` | The bookmark repository used to fetch bookmark data during index rebuilding and search result retrieval. |
| **_index** | `Dict[str, Set[str]]` | An inverted index mapping search tokens to sets of bookmark IDs for efficient lookup. |

---

## Constructor

### Signature

```python
def SearchIndex(
    repository: [BookmarkRepository](../../../db/repository/bookmarkrepository.md?sid=app_db_repository_bookmarkrepository)
) - > None
```

### Parameters

| Name | Type | Description |
|------|------|-------------|
| **repository** | `[BookmarkRepository](../../../db/repository/bookmarkrepository.md?sid=app_db_repository_bookmarkrepository)` | The bookmark repository to index from. |

---



## Methods

---

#### `index_bookmark()`

```python
@classmethod
def index_bookmark(
    bookmark: [Bookmark](../../../models/bookmark/bookmark.md?sid=app_models_bookmark_bookmark)
) - > None
```

Add or update a bookmark in the index.

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| **bookmark** | `[Bookmark](../../../models/bookmark/bookmark.md?sid=app_models_bookmark_bookmark)` | The bookmark object containing the title and description to be indexed. |

#### Returns

| Type | Description |
|------|-------------|
| `None` | Nothing is returned; the internal index state is updated. |

---

#### `remove_bookmark()`

```python
@classmethod
def remove_bookmark(
    bookmark_id: str
) - > None
```

Remove a bookmark from the index.

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| **bookmark_id** | `str` | The unique identifier of the bookmark to be removed from the search index. |

#### Returns

| Type | Description |
|------|-------------|
| `None` | Nothing is returned; the bookmark is removed from the internal index. |

---

#### `search()`

```python
@classmethod
def search(
    query: str,
    limit: int = 20
) - > List[[Bookmark](../../../models/bookmark/bookmark.md?sid=app_models_bookmark_bookmark)]
```

Search bookmarks matching the query string. Tokens are AND-ed together — all must appear for a result to match.

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| **query** | `str` | Free-text search query used to filter bookmarks. |
| **limit** | `int` = 20 | Maximum number of results to return from the search. |

#### Returns

| Type | Description |
|------|-------------|
| `List[[Bookmark](../../../models/bookmark/bookmark.md?sid=app_models_bookmark_bookmark)]` | List of matching bookmarks, ordered by relevance (number of token hits). |

---