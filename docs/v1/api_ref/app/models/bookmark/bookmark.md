---
{title: Bookmark, description: API Reference for app.models.bookmark.Bookmark, section_id: app_models_bookmark_bookmark, section_type: class_ref}
---
# Bookmark

A saved URL with metadata, tags, and full-text content.

## Attributes

| Attribute | Type | Description |
|----------|------|-------------|
| **url** | `str` | The bookmarked URL. |
| **title** | `str` | Human-readable title. |
| **description** | `str` | Optional longer description. |
| **tags** | `List[str]` = [] | List of tag IDs associated with this bookmark. |
| **status** | `[BookmarkStatus](bookmarkstatus.md?sid=app_models_bookmark_bookmarkstatus)` = BookmarkStatus.ACTIVE | Current visibility status. |
| **id** | `str` = uuid.uuid4().hex[:12] | Unique identifier. |
| **created_at** | `datetime` = datetime.utcnow | Timestamp of creation. |
| **updated_at** | `datetime` = datetime.utcnow | Timestamp of last modification. |
| **metadata** | `Dict[str, Any]` = \{\} | Arbitrary key/value pairs for extensibility. |

---

## Constructor

### Signature

```python
def Bookmark(
    url: str,
    title: str,
    description: str = "",
    tags: List[str] = [],
    status: [BookmarkStatus](bookmarkstatus.md?sid=app_models_bookmark_bookmarkstatus) = BookmarkStatus.ACTIVE,
    metadata: Dict[str, Any] = {}
) - > null
```

### Parameters

| Name | Type | Description |
|------|------|-------------|
| **url** | `str` | The bookmarked URL. |
| **title** | `str` | Human-readable title. |
| **description** | `str` = "" | Optional longer description. |
| **tags** | `List[str]` = [] | List of tag IDs associated with this bookmark. |
| **status** | `[BookmarkStatus](bookmarkstatus.md?sid=app_models_bookmark_bookmarkstatus)` = BookmarkStatus.ACTIVE | Current visibility status. |
| **metadata** | `Dict[str, Any]` = \{\} | Arbitrary key/value pairs for extensibility. |

---



## Methods

---

#### `archive()`

```python
@classmethod
def archive() - > null
```

Move the bookmark to the archive.

#### Returns

| Type | Description |
|------|-------------|
| `null` | Nothing |

---

#### `trash()`

```python
@classmethod
def trash() - > null
```

Soft-delete the bookmark by moving it to the trash.

#### Returns

| Type | Description |
|------|-------------|
| `null` | Nothing |

---

#### `restore()`

```python
@classmethod
def restore() - > null
```

Restore a trashed or archived bookmark to active status.

#### Returns

| Type | Description |
|------|-------------|
| `null` | Nothing |

---

#### `add_tag()`

```python
@classmethod
def add_tag(
    tag_id: string
) - > boolean
```

Attach a tag. Returns False if already present.

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| **tag_id** | `string` | The unique identifier of the tag to associate with this bookmark |

#### Returns

| Type | Description |
|------|-------------|
| `boolean` | True if the tag was successfully added, False if the tag ID already exists in the collection |

---

#### `remove_tag()`

```python
@classmethod
def remove_tag(
    tag_id: string
) - > boolean
```

Detach a tag. Returns False if not found.

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| **tag_id** | `string` | The unique identifier of the tag to remove from this bookmark |

#### Returns

| Type | Description |
|------|-------------|
| `boolean` | True if the tag was successfully removed, False if the tag ID was not found |

---

#### `to_dict()`

```python
@classmethod
def to_dict() - > object
```

Serialise to a plain dictionary for JSON responses.

#### Returns

| Type | Description |
|------|-------------|
| `object` | A dictionary containing all bookmark attributes including ID, URL, title, and timestamps in ISO format |

---

#### `from_dict()`

```python
@classmethod
def from_dict(
    data: object
) - > [Bookmark](bookmark.md?sid=app_models_bookmark_bookmark)
```

Construct a Bookmark from a dictionary (e.g. JSON body).

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| **data** | `object` | Dictionary with bookmark fields. |

#### Returns

| Type | Description |
|------|-------------|
| `[Bookmark](bookmark.md?sid=app_models_bookmark_bookmark)` | A new Bookmark instance. |

---
