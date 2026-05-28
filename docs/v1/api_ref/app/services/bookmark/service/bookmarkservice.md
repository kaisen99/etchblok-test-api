---
title: BookmarkService
description: API Reference for app.services.bookmark_service.BookmarkService
code_symbols: [SYM#fdcfaed9972e477ae4585fd1b279ac107fa534cd, SYM#a4f4e46393c52bd550c8604d6063bfb3d56ec021, SYM#7aa21f711ae8472f0b7ffb20064b5f0267d90a90, SYM#63702c3e97cf912270cfa0b7f4632068af698a35, SYM#0ccdb0cd1e6fc755e7d952d6cd2e1330e7e66b91, SYM#6e7eff8c5633d73f1e879494828837aaf9dfae5e, SYM#0782fb10296acc7689d8453733717aae64f29eaf, SYM#8562038c56d0c341ab61238128b95859cd9a244f, SYM#c62e41c0008b978216607273270a50a38da1df06, SYM#4709ff002d230924b24153bf20d1f83310f8c3f8, SYM#39a079ae5ea40c44f17a07022fa11574c1cf0351, SYM#e8fe14736e45d16d922e395fb810a2b6719da74f, SYM#1762351671b87f41a4953377fdf34c5898694aa9, SYM#c603e51532c896347b65aa6efee878156dbf314f, SYM#59cf9fbb3db769a04daad4a2983f9da7e978a3f1, SYM#c360a5eaa7ba692bce1848a44f8f468a9657f1c0, SYM#9f3a49cd434603bf30468cd737c8bdd09125b28a, SYM#bc95aa9ea1151a3149cb0e17f03a804bc214e133, SYM#f4464e853186d610bd6c67b657f28308fbf1e35f, SYM#8e82b2ee2bb5ddd4c5781fab17c26b0bff874531, SYM#742793f9a2ce4ca72f43af9faa398731af50654f]
section_id: app_services_bookmark_service_bookmarkservice
section_type: class_ref
---
# BookmarkService

Facade over the repository and search index.

Handles validation, cache invalidation, and cross-entity operations
(e.g. removing a tag also strips it from all bookmarks).



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
| **data** | `Dict[str, Any]` | Dictionary containing tag attributes, primarily the 'name'. |

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
| **data** | `Dict[str, Any]` | Dictionary containing the new 'name' or 'color' for the tag. |

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
| **data** | `Dict[str, Any]` | Dictionary containing collection attributes, including the required 'name'. |

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
