---
{title: SearchIndex, description: API Reference for app.services.search_service.SearchIndex, section_id: app_services_search_service_searchindex, section_type: class_ref}
---
# SearchIndex

Inverted index mapping tokens to bookmark IDs.

## Attributes

| Attribute | Type | Description |
|----------|------|-------------|
| **_repo** | `[BookmarkRepository](../../../db/repository/bookmarkrepository.md?sid=app_db_repository_bookmarkrepository)` | The bookmark repository used to retrieve full bookmark objects during search and initial index building. |
| **_index** | `Dict[str, Set[str]]` = defaultdict(set) | An inverted index mapping search tokens to sets of bookmark IDs for efficient lookup during query execution. |

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

### Signature

```python
def SearchIndex(
    repository: [BookmarkRepository](../../../db/repository/bookmarkrepository.md?sid=app_db_repository_bookmarkrepository)
) - > None
```

### Parameters

| Name | Type | Description |
|------|------|-------------|
| **repository** | `[BookmarkRepository](../../../db/repository/bookmarkrepository.md?sid=app_db_repository_bookmarkrepository)` | The bookmark repository instance used to fetch bookmark data for indexing and retrieval. |

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
| **bookmark** | `[Bookmark](../../../models/bookmark/bookmark.md?sid=app_models_bookmark_bookmark)` | The bookmark object containing the title and description to be tokenized and indexed. |

#### Returns

| Type | Description |
|------|-------------|
| `None` |  |

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
| **bookmark_id** | `str` | The unique identifier of the bookmark to be purged from the inverted index. |

#### Returns

| Type | Description |
|------|-------------|
| `None` |  |

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
| **query** | `str` | Free-text search query containing the terms to match against indexed bookmarks. |
| **limit** | `int` = 20 | Maximum number of results to return from the ranked search results. |

#### Returns

| Type | Description |
|------|-------------|
| `List[[Bookmark](../../../models/bookmark/bookmark.md?sid=app_models_bookmark_bookmark)]` | List of matching bookmarks, ordered by relevance (number of token hits). |

---
