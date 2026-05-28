---
title: BookmarkRepository
description: API Reference for app.db.repository.BookmarkRepository
code_symbols: [SYM#adb8232356346a5957ff3a1a1b7ff70581f37649, SYM#49e1f24ffd02e7fb48b7423f93317f802df23b5f, SYM#5b3e3715ef1a71f5a77f03d92bf6c5f51a48ad32, SYM#cf9a8e7f54f57a8cd339010d13705db8b026148f, SYM#e1849a54b7006099f2c1a44a31c94da46e4a68a8, SYM#f82b48b96fecddaa17325e209241224a683b6b1e, SYM#16a62952ebf5e363e2fe2df8d76f5e2297687ce8, SYM#587181a63788f5055d51b13321cc17c22d1fd166, SYM#98006983eea9b96cd75a67c455f085a8d8b6393a, SYM#c3c446050d26df08e7387c7b3d8639ebee63a9ae, SYM#6f0cb7bb3ce7d5a67ae8855994b59d8ac5907683, SYM#aece75f08f6ead9952affe9965e98fe31f618694, SYM#10dc4cf94d5e3181773310dea721641426f217b1, SYM#4107010ed55b4ee632caf65fe1ee3ba3fd493f86, SYM#b739368d1d2dd1698c0dc2cfe42e7cdd5a083aa2, SYM#3864efcb492a0b2d68004d16c502ecff2b8ba25c]
section_id: app_db_repository_bookmarkrepository
section_type: class_ref
---
# BookmarkRepository

In-memory storage for bookmarks, tags, and collections.

## Attributes

| Attribute | Type | Description |
|----------|------|-------------|
| **_bookmarks** | `Dict[str, [Bookmark](../../models/bookmark/bookmark.md?sid=app_models_bookmark_bookmark)]` = \{\} | Internal dictionary mapping unique bookmark IDs to Bookmark objects for persistent in-memory storage. |
| **_tags** | `Dict[str, [Tag](../../models/tag/tag.md?sid=app_models_tag_tag)]` = \{\} | Internal dictionary mapping unique tag IDs to Tag objects used for organizing and filtering bookmarks. |
| **_collections** | `Dict[str, [Collection](../../models/collection/collection.md?sid=app_models_collection_collection)]` = \{\} | Internal dictionary mapping unique collection IDs to Collection objects for grouping related bookmarks. |

---

## Constructor

### Signature

```python
def BookmarkRepository() - > None
```

---

### Signature

```python
def BookmarkRepository() - > None
```

---



## Methods

---

#### `save_bookmark()`

```python
@classmethod
def save_bookmark(
    bookmark: [Bookmark](../../models/bookmark/bookmark.md?sid=app_models_bookmark_bookmark)
) - > None
```

Insert or update a bookmark.

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| **bookmark** | `[Bookmark](../../models/bookmark/bookmark.md?sid=app_models_bookmark_bookmark)` | The Bookmark object to be persisted or updated in the repository |

#### Returns

| Type | Description |
|------|-------------|
| `None` |  |

---

#### `get_bookmark()`

```python
@classmethod
def get_bookmark(
    bookmark_id: str
) - > Optional[[Bookmark](../../models/bookmark/bookmark.md?sid=app_models_bookmark_bookmark)]
```

Retrieve a bookmark by ID, or None.

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| **bookmark_id** | `str` | The unique identifier of the bookmark to retrieve |

#### Returns

| Type | Description |
|------|-------------|
| `Optional[[Bookmark](../../models/bookmark/bookmark.md?sid=app_models_bookmark_bookmark)]` | The Bookmark object if found, otherwise None |

---

#### `delete_bookmark()`

```python
@classmethod
def delete_bookmark(
    bookmark_id: str
) - > bool
```

Hard-delete a bookmark. Returns True if it existed.

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| **bookmark_id** | `str` | The unique identifier of the bookmark to be deleted |

#### Returns

| Type | Description |
|------|-------------|
| `bool` | True if the bookmark was found and removed, False otherwise |

---

#### `list_bookmarks()`

```python
@classmethod
def list_bookmarks(
    page: int = 1,
    per_page: int = 25,
    status: Optional[str] = None
) - > Tuple[List[[Bookmark](../../models/bookmark/bookmark.md?sid=app_models_bookmark_bookmark)], int]
```

Return a paginated slice of bookmarks.

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| **page** | `int` = 1 | 1-based page index used to calculate the starting offset |
| **per_page** | `int` = 25 | The maximum number of items to return in a single page |
| **status** | `Optional[str]` = None | Optional status filter string (active, archived, trashed) to narrow down results |

#### Returns

| Type | Description |
|------|-------------|
| `Tuple[List[[Bookmark](../../models/bookmark/bookmark.md?sid=app_models_bookmark_bookmark)], int]` | A tuple containing the list of bookmarks for the current page and the total count of matching bookmarks |

---

#### `get_bookmarks_with_tag()`

```python
@classmethod
def get_bookmarks_with_tag(
    tag_id: str
) - > List[[Bookmark](../../models/bookmark/bookmark.md?sid=app_models_bookmark_bookmark)]
```

Return all bookmarks that have a specific tag attached.

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| **tag_id** | `str` | The unique identifier of the tag used to filter bookmarks |

#### Returns

| Type | Description |
|------|-------------|
| `List[[Bookmark](../../models/bookmark/bookmark.md?sid=app_models_bookmark_bookmark)]` | A list of Bookmark objects associated with the specified tag ID |

---

#### `save_tag()`

```python
@classmethod
def save_tag(
    tag: [Tag](../../models/tag/tag.md?sid=app_models_tag_tag)
) - > None
```

Insert or update a tag.

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| **tag** | `[Tag](../../models/tag/tag.md?sid=app_models_tag_tag)` | The Tag object to be persisted or updated in the repository |

#### Returns

| Type | Description |
|------|-------------|
| `None` |  |

---

#### `get_tag()`

```python
@classmethod
def get_tag(
    tag_id: str
) - > Optional[[Tag](../../models/tag/tag.md?sid=app_models_tag_tag)]
```

Retrieve a tag by ID, or None.

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| **tag_id** | `str` | The unique identifier of the tag to retrieve |

#### Returns

| Type | Description |
|------|-------------|
| `Optional[[Tag](../../models/tag/tag.md?sid=app_models_tag_tag)]` | The Tag object if found, otherwise None |

---

#### `delete_tag()`

```python
@classmethod
def delete_tag(
    tag_id: str
) - > bool
```

Hard-delete a tag.

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| **tag_id** | `str` | The unique identifier of the tag to be deleted |

#### Returns

| Type | Description |
|------|-------------|
| `bool` | True if the tag was found and removed, False otherwise |

---

#### `list_tags()`

```python
@classmethod
def list_tags() - > List[[Tag](../../models/tag/tag.md?sid=app_models_tag_tag)]
```

Return all tags.

#### Returns

| Type | Description |
|------|-------------|
| `List[[Tag](../../models/tag/tag.md?sid=app_models_tag_tag)]` | A list containing all Tag objects stored in the repository |

---

#### `save_collection()`

```python
@classmethod
def save_collection(
    collection: [Collection](../../models/collection/collection.md?sid=app_models_collection_collection)
) - > None
```

Insert or update a collection.

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| **collection** | `[Collection](../../models/collection/collection.md?sid=app_models_collection_collection)` | The Collection object to be persisted or updated in the repository |

#### Returns

| Type | Description |
|------|-------------|
| `None` |  |

---

#### `get_collection()`

```python
@classmethod
def get_collection(
    collection_id: str
) - > Optional[[Collection](../../models/collection/collection.md?sid=app_models_collection_collection)]
```

Retrieve a collection by ID, or None.

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| **collection_id** | `str` | The unique identifier of the collection to retrieve |

#### Returns

| Type | Description |
|------|-------------|
| `Optional[[Collection](../../models/collection/collection.md?sid=app_models_collection_collection)]` | The Collection object if found, otherwise None |

---

#### `delete_collection()`

```python
@classmethod
def delete_collection(
    collection_id: str
) - > bool
```

Hard-delete a collection.

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| **collection_id** | `str` | The unique identifier of the collection to be deleted |

#### Returns

| Type | Description |
|------|-------------|
| `bool` | True if the collection was found and removed, False otherwise |

---

#### `list_collections()`

```python
@classmethod
def list_collections() - > List[[Collection](../../models/collection/collection.md?sid=app_models_collection_collection)]
```

Return all collections.

#### Returns

| Type | Description |
|------|-------------|
| `List[[Collection](../../models/collection/collection.md?sid=app_models_collection_collection)]` | A list containing all Collection objects stored in the repository |

---
