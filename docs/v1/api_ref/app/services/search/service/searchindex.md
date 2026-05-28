---
title: SearchIndex
description: API Reference for app.services.search_service.SearchIndex
code_symbols: [SYM#b0cc1ddc5c9e6b6675ff73174df52949062c8da5, SYM#1bd4b53a341b1da2c0ecd10953332114c0ccff82, SYM#d1e69d9a0b3ca1f786dd730af8319a6683e66ebf, SYM#36e03a3dba574c84d630a4c7cb8c1f4b486aee53, SYM#a1c86a57d5cb58cb89774a008a9be58913ef113d, SYM#443dd312a2fbbe1ab0c4b7d77bc8ec5c10e147c4, SYM#8855d4652531da29a4beda84f4e45f7b98fcb2c6, SYM#fb4306c588e5cf706fcae912d45e5780803887c3]
section_id: app_services_search_service_searchindex
section_type: class_ref
---
# SearchIndex

Inverted index mapping tokens to bookmark IDs.

## Attributes

| Attribute | Type | Description |
|----------|------|-------------|
| **_repo** | `[BookmarkRepository](../../../db/repository/bookmarkrepository.md?sid=app_db_repository_bookmarkrepository)` | The bookmark repository used to retrieve full bookmark objects during search and initial index building. |
| **_index** | `Dict[str, Set[str]]` = defaultdict(set) | Inverted index mapping search tokens to sets of unique bookmark IDs for efficient lookup. |

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
)
```

### Parameters

| Name | Type | Description |
|------|------|-------------|
| **repository** | `[BookmarkRepository](../../../db/repository/bookmarkrepository.md?sid=app_db_repository_bookmarkrepository)` | The bookmark repository instance to index from. |

---



## Methods

---

#### `index_bookmark()`

```python
@classmethod
def index_bookmark(
    bookmark: [Bookmark](../../../models/bookmark/bookmark.md?sid=app_models_bookmark_bookmark)
)
```

Add or update a bookmark in the index.

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| **bookmark** | `[Bookmark](../../../models/bookmark/bookmark.md?sid=app_models_bookmark_bookmark)` | The bookmark object to be indexed or updated. |

---

#### `remove_bookmark()`

```python
@classmethod
def remove_bookmark(
    bookmark_id: str
)
```

Remove a bookmark from the index.

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| **bookmark_id** | `str` | The unique identifier of the bookmark to remove. |

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
| **query** | `str` | Free-text search query string. |
| **limit** | `int` = 20 | Maximum number of results to return. |

#### Returns

| Type | Description |
|------|-------------|
| `List[[Bookmark](../../../models/bookmark/bookmark.md?sid=app_models_bookmark_bookmark)]` | List of matching bookmarks, ordered by relevance (number of token hits). |

---
