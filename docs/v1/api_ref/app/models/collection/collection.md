---
title: Collection
description: API Reference for app.models.collection.Collection
code_symbols: [SYM#664bcdae74f24d832fff86d384111517f11be0db, SYM#83a9c07c5b81efb56635ee7b24d5fc4db0fb37d0, SYM#abed675aa8d3a87215bc3c5fc0908da5947a39c9, SYM#bca56aacbc9ca276d3fff4045b6ad0d7b76c779b, SYM#b317d7d2dfd888b51a6c2c688a0811657255da89, SYM#6b8d9583e920b2714d97340553d1c0074e715089, SYM#9a97bc33086e549af5602e7c0e1c19be846e9522, SYM#8f8c43c9d6bba4fcd33f13e5474e80632ba066ea, SYM#a0d61b1651e02d5c6df35be2fe32c071a2e79005, SYM#db2ce225f787bb0a466718ec1a5a94ae334d12a9, SYM#3d8dc3430ad5b723cea315bb4ff86cf07bccdeec, SYM#7ea748d60fa46fb5d6927f02bfabcc86a78900d7, SYM#74779c79ebe3d076f0eada3d4a0a317bdd5e9204]
section_id: app_models_collection_collection
section_type: class_ref
---
# Collection

A named group of bookmarks.

## Attributes

| Attribute | Type | Description |
|----------|------|-------------|
| **name** | `str` | Display name. |
| **collection_type** | `[CollectionType](collectiontype.md?sid=app_models_collection_collectiontype)` = CollectionType.MANUAL | Whether the collection is manual or smart. |
| **bookmark_ids** | `List[str]` = [] | Ordered list of bookmark IDs in the collection. |
| **filter_rule** | `str` | For smart collections, a query string that selects bookmarks. |
| **is_pinned** | `bool` = False | Whether the collection appears at the top of the sidebar. |
| **id** | `str` = uuid.uuid4().hex[:10] | Unique identifier. |
| **created_at** | `datetime` = datetime.utcnow | Creation timestamp. |

---



## Methods

---

#### `size()`

```python
@classmethod
def size() - > int
```

Number of bookmarks in the collection.

#### Returns

| Type | Description |
|------|-------------|
| `int` | The total count of bookmark IDs currently stored in the collection |

---

#### `is_smart()`

```python
@classmethod
def is_smart() - > bool
```

Whether this collection auto-populates based on a filter rule.

#### Returns

| Type | Description |
|------|-------------|
| `bool` | True if the collection type is SMART, False otherwise |

---

#### `add_bookmark()`

```python
@classmethod
def add_bookmark(
    bookmark_id: str
) - > bool
```

Add a bookmark to a manual collection.

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| **bookmark_id** | `str` | ID of the bookmark to add. |

#### Returns

| Type | Description |
|------|-------------|
| `bool` | True if added, False if already present or collection is smart. |

---

#### `remove_bookmark()`

```python
@classmethod
def remove_bookmark(
    bookmark_id: str
) - > bool
```

Remove a bookmark from the collection.

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| **bookmark_id** | `str` | The unique identifier of the bookmark to be removed |

#### Returns

| Type | Description |
|------|-------------|
| `bool` | True if the bookmark was successfully removed, False if the ID was not found |

---

#### `reorder()`

```python
@classmethod
def reorder(
    bookmark_ids: List[str]
) - > null
```

Replace the bookmark ordering.

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| **bookmark_ids** | `List[str]` | New ordered list. Must contain the same IDs. |

#### Returns

| Type | Description |
|------|-------------|
| `null` |  |

---

#### `pin()`

```python
@classmethod
def pin() - > null
```

Pin the collection to the top of the sidebar.

#### Returns

| Type | Description |
|------|-------------|
| `null` |  |

---

#### `unpin()`

```python
@classmethod
def unpin() - > null
```

Unpin the collection.

#### Returns

| Type | Description |
|------|-------------|
| `null` |  |

---

#### `to_dict()`

```python
@classmethod
def to_dict() - > Dict[str, Any]
```

Serialise to JSON-safe dictionary.

#### Returns

| Type | Description |
|------|-------------|
| `Dict[str, Any]` | A dictionary containing the collection's metadata, IDs, and state |

---

#### `from_dict()`

```python
@classmethod
def from_dict(
    data: Dict[str, Any]
) - > [Collection](collection.md?sid=app_models_collection_collection)
```

Construct from a dictionary.

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| **data** | `Dict[str, Any]` | A dictionary containing collection attributes like name and type |

#### Returns

| Type | Description |
|------|-------------|
| `[Collection](collection.md?sid=app_models_collection_collection)` | A new instance of the Collection class populated with the provided data |

---
