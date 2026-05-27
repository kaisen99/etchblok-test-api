---
{title: Collection, description: API Reference for app.models.collection.Collection, section_id: app_models_collection_collection, section_type: class_ref}
---
# Collection

A named group of bookmarks.

## Attributes

| Attribute | Type | Description |
|----------|------|-------------|
| **name** | `str` | Display name. |
| **collection_type** | `[CollectionType](collectiontype.md?sid=app_models_collection_collectiontype)` = CollectionType.MANUAL | Whether the collection is manual or smart. |
| **bookmark_ids** | `List[str]` = [] | Ordered list of bookmark IDs in the collection. |
| **filter_rule** | `str` = "" | For smart collections, a query string that selects bookmarks. |
| **is_pinned** | `bool` = false | Whether the collection appears at the top of the sidebar. |
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
)
```

Replace the bookmark ordering.

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| **bookmark_ids** | `List[str]` | New ordered list. Must contain the same IDs. |

---

#### `pin()`

```python
@classmethod
def pin()
```

Pin the collection to the top of the sidebar.

---

#### `unpin()`

```python
@classmethod
def unpin()
```

Unpin the collection.

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
