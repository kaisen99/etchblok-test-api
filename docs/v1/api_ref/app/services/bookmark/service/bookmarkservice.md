---
{title: BookmarkService, description: API Reference for app.services.bookmark_service.BookmarkService, section_id: app_services_bookmark_service_bookmarkservice, section_type: class_ref}
---
# BookmarkService

Facade over the repository and search index.

Handles validation, cache invalidation, and cross-entity operations
(e.g. removing a tag also strips it from all bookmarks).

## Constructor

### Signature

```python
def BookmarkService() - > null
```

---



## Methods

---

#### `create_bookmark()`

```python
@classmethod
def create_bookmark(
    data: Dict[str, Any]
) - > Tuple[Optional[[Bookmark](../../../models/bookmark/bookmark.md?sid=app_models_bookmark_bookmark)], Optional[str]]
```

Validate and persist a new bookmark.

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| **data** | `Dict[str, Any]` | Dict with ``url``, ``title``, and optional fields. |

#### Returns

| Type | Description |
|------|-------------|
| `Tuple[Optional[[Bookmark](../../../models/bookmark/bookmark.md?sid=app_models_bookmark_bookmark)], Optional[str]]` | Tuple of (bookmark, None) on success or (None, error_message) on failure. |

---

#### `get_bookmark()`

```python
@classmethod
def get_bookmark(
    bookmark_id: str
) - > Optional[[Bookmark](../../../models/bookmark/bookmark.md?sid=app_models_bookmark_bookmark)]
```

Retrieve a bookmark by ID, using cache when available.

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| **bookmark_id** | `str` | The unique identifier of the bookmark to retrieve. |

#### Returns

| Type | Description |
|------|-------------|
| `Optional[[Bookmark](../../../models/bookmark/bookmark.md?sid=app_models_bookmark_bookmark)]` | The Bookmark object if found, otherwise None. |

---

#### `list_bookmarks()`

```python
@classmethod
def list_bookmarks(
    page: int = 1,
    per_page: int = 25,
    status: Optional[str] = None
) - > Tuple[List[[Bookmark](../../../models/bookmark/bookmark.md?sid=app_models_bookmark_bookmark)], int]
```

Return a paginated list of bookmarks.

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| **page** | `int` = 1 | 1-based page number. |
| **per_page** | `int` = 25 | Number of items per page. |
| **status** | `Optional[str]` = None | Optional status filter. |

#### Returns

| Type | Description |
|------|-------------|
| `Tuple[List[[Bookmark](../../../models/bookmark/bookmark.md?sid=app_models_bookmark_bookmark)], int]` | Tuple of (bookmarks_list, total_count). |

---

#### `update_bookmark()`

```python
@classmethod
def update_bookmark(
    bookmark_id: str,
    data: Dict[str, Any]
) - > Tuple[Optional[[Bookmark](../../../models/bookmark/bookmark.md?sid=app_models_bookmark_bookmark)], Optional[str]]
```

Partially update a bookmark.

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| **bookmark_id** | `str` | The unique identifier of the bookmark to update. |
| **data** | `Dict[str, Any]` | Dictionary containing fields to update, such as title, description, or url. |

#### Returns

| Type | Description |
|------|-------------|
| `Tuple[Optional[[Bookmark](../../../models/bookmark/bookmark.md?sid=app_models_bookmark_bookmark)], Optional[str]]` | The updated Bookmark and None on success, or None and an error message if validation fails. |

---

#### `delete_bookmark()`

```python
@classmethod
def delete_bookmark(
    bookmark_id: str
) - > bool
```

Soft-delete by trashing the bookmark.

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| **bookmark_id** | `str` | The unique identifier of the bookmark to soft-delete. |

#### Returns

| Type | Description |
|------|-------------|
| `bool` | True if the bookmark was successfully trashed, False if it was not found. |

---

#### `archive_bookmark()`

```python
@classmethod
def archive_bookmark(
    bookmark_id: str
) - > Optional[[Bookmark](../../../models/bookmark/bookmark.md?sid=app_models_bookmark_bookmark)]
```

Archive a bookmark.

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| **bookmark_id** | `str` | The unique identifier of the bookmark to archive. |

#### Returns

| Type | Description |
|------|-------------|
| `Optional[[Bookmark](../../../models/bookmark/bookmark.md?sid=app_models_bookmark_bookmark)]` | The archived Bookmark object, or None if the bookmark was not found. |

---

#### `restore_bookmark()`

```python
@classmethod
def restore_bookmark(
    bookmark_id: str
) - > Optional[[Bookmark](../../../models/bookmark/bookmark.md?sid=app_models_bookmark_bookmark)]
```

Restore a bookmark to active status.

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| **bookmark_id** | `str` | The unique identifier of the bookmark to restore. |

#### Returns

| Type | Description |
|------|-------------|
| `Optional[[Bookmark](../../../models/bookmark/bookmark.md?sid=app_models_bookmark_bookmark)]` | The restored Bookmark object, or None if the bookmark was not found. |

---

#### `full_text_search()`

```python
@classmethod
def full_text_search(
    query: str,
    limit: int = 20
) - > List[[Bookmark](../../../models/bookmark/bookmark.md?sid=app_models_bookmark_bookmark)]
```

Full-text search across bookmark titles and descriptions.

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| **query** | `str` | The search string used to match bookmark titles and descriptions. |
| **limit** | `int` = 20 | The maximum number of search results to return. |

#### Returns

| Type | Description |
|------|-------------|
| `List[[Bookmark](../../../models/bookmark/bookmark.md?sid=app_models_bookmark_bookmark)]` | A list of bookmarks matching the search query. |

---

#### `list_tags()`

```python
@classmethod
def list_tags() - > List[[Tag](../../../models/tag/tag.md?sid=app_models_tag_tag)]
```

Return all tags.

#### Returns

| Type | Description |
|------|-------------|
| `List[[Tag](../../../models/tag/tag.md?sid=app_models_tag_tag)]` | A list of all available Tag objects. |

---

#### `create_tag()`

```python
@classmethod
def create_tag(
    data: Dict[str, Any]
) - > Tuple[Optional[[Tag](../../../models/tag/tag.md?sid=app_models_tag_tag)], Optional[str]]
```

Validate and persist a new tag.

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| **data** | `Dict[str, Any]` | Dictionary containing tag attributes, primarily the name. |

#### Returns

| Type | Description |
|------|-------------|
| `Tuple[Optional[[Tag](../../../models/tag/tag.md?sid=app_models_tag_tag)], Optional[str]]` | The created Tag and None on success, or None and an error message if validation fails. |

---

#### `delete_tag()`

```python
@classmethod
def delete_tag(
    tag_id: str
) - > bool
```

Delete a tag and strip it from all bookmarks.

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| **tag_id** | `str` | The unique identifier of the tag to remove. |

#### Returns

| Type | Description |
|------|-------------|
| `bool` | True if the tag was successfully deleted, False if the tag was not found. |

---

#### `update_tag()`

```python
@classmethod
def update_tag(
    tag_id: str,
    data: Dict[str, Any]
) - > Tuple[Optional[[Tag](../../../models/tag/tag.md?sid=app_models_tag_tag)], Optional[str]]
```

Update a tag's name or colour.

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| **tag_id** | `str` | The unique identifier of the tag to update. |
| **data** | `Dict[str, Any]` | Dictionary containing the new name or color for the tag. |

#### Returns

| Type | Description |
|------|-------------|
| `Tuple[Optional[[Tag](../../../models/tag/tag.md?sid=app_models_tag_tag)], Optional[str]]` | The updated Tag and None on success, or None and an error message if validation fails. |

---

#### `list_collections()`

```python
@classmethod
def list_collections() - > List[[Collection](../../../models/collection/collection.md?sid=app_models_collection_collection)]
```

Return all collections.

#### Returns

| Type | Description |
|------|-------------|
| `List[[Collection](../../../models/collection/collection.md?sid=app_models_collection_collection)]` | A list of all available Collection objects. |

---

#### `get_collection()`

```python
@classmethod
def get_collection(
    collection_id: str
) - > Optional[[Collection](../../../models/collection/collection.md?sid=app_models_collection_collection)]
```

Retrieve a collection by ID.

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| **collection_id** | `str` | The unique identifier of the collection to retrieve. |

#### Returns

| Type | Description |
|------|-------------|
| `Optional[[Collection](../../../models/collection/collection.md?sid=app_models_collection_collection)]` | The Collection object if found, otherwise None. |

---

#### `create_collection()`

```python
@classmethod
def create_collection(
    data: Dict[str, Any]
) - > Tuple[Optional[[Collection](../../../models/collection/collection.md?sid=app_models_collection_collection)], Optional[str]]
```

Create a new collection.

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| **data** | `Dict[str, Any]` | Dictionary containing collection attributes, including the required name. |

#### Returns

| Type | Description |
|------|-------------|
| `Tuple[Optional[[Collection](../../../models/collection/collection.md?sid=app_models_collection_collection)], Optional[str]]` | The created Collection and None on success, or None and an error message if the name is missing. |

---

#### `add_to_collection()`

```python
@classmethod
def add_to_collection(
    collection_id: str,
    bookmark_id: str
) - > bool
```

Add a bookmark to a collection.

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| **collection_id** | `str` | The unique identifier of the target collection. |
| **bookmark_id** | `str` | The unique identifier of the bookmark to add. |

#### Returns

| Type | Description |
|------|-------------|
| `bool` | True if the bookmark was successfully added, False if the collection was not found or addition failed. |

---

#### `remove_from_collection()`

```python
@classmethod
def remove_from_collection(
    collection_id: str,
    bookmark_id: str
) - > bool
```

Remove a bookmark from a collection.

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| **collection_id** | `str` | The unique identifier of the target collection. |
| **bookmark_id** | `str` | The unique identifier of the bookmark to remove. |

#### Returns

| Type | Description |
|------|-------------|
| `bool` | True if the bookmark was successfully removed, False if the collection was not found or removal failed. |

---
