---
{title: BookmarkRepository, description: API Reference for app.db.repository.BookmarkRepository, section_id: app_db_repository_bookmarkrepository, section_type: class_ref}
---
# BookmarkRepository

In-memory storage for bookmarks, tags, and collections.

## Attributes

| Attribute | Type | Description |
|----------|------|-------------|
| **_bookmarks** | `Dict[str, [Bookmark](../../models/bookmark/bookmark.md?sid=app_models_bookmark_bookmark)]` = \{\} | Internal dictionary mapping unique bookmark IDs to Bookmark objects for in-memory storage and retrieval. |
| **_tags** | `Dict[str, [Tag](../../models/tag/tag.md?sid=app_models_tag_tag)]` = \{\} | Internal dictionary mapping unique tag IDs to Tag objects used to manage bookmark categorization. |
| **_collections** | `Dict[str, [Collection](../../models/collection/collection.md?sid=app_models_collection_collection)]` = \{\} | Internal dictionary mapping unique collection IDs to Collection objects for organizing bookmarks into groups. |

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
| `None` | Nothing |

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
| **bookmark_id** | `str` | The unique identifier of the bookmark to be permanently removed |

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
| **page** | `int` = 1 | The 1-based page index for pagination |
| **per_page** | `int` = 25 | The maximum number of bookmark items to return per page |
| **status** | `Optional[str]` = None | An optional filter string to restrict results by status, such as 'active', 'archived', or 'trashed' |

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
| `None` | Nothing |

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
| **tag_id** | `str` | The unique identifier of the tag to be permanently removed |

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
| `List[[Tag](../../models/tag/tag.md?sid=app_models_tag_tag)]` | A list of all Tag objects stored in the repository |

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
| `None` | Nothing |

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
| **collection_id** | `str` | The unique identifier of the collection to be permanently removed |

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
| `List[[Collection](../../models/collection/collection.md?sid=app_models_collection_collection)]` | A list of all Collection objects stored in the repository |

---
