---
title: Bookmark
description: API Reference for app.models.bookmark.Bookmark
code_symbols: [SYM#6d5b77b3f04288620db996a9bc18b13d3bd1ad3b, SYM#2d386cc8262d6ab885c7bd52a06cfb14c0795f5e, SYM#a97e00727b040edd0493d0c32e951d35e1a3780f, SYM#a5170bb047650518dd50196f14699d1dafbb8a9e, SYM#3b369d0ccb308a6b7067c305856cda5b8b9a4d55, SYM#f2f73823fc3fb8094f6a187d9c35829fb110a4eb, SYM#0e6797f3277fab2f71a74de0185254222e4af5bd, SYM#1d9e5aafea04befee97cf4e3adc3737389d1d48e, SYM#40800f1082862bdf5d0fc68717b2fd2511a89475, SYM#e59c9322631d48a375b693db0514fa402c48c72d, SYM#0e82a0205f3ede622a7183a3ca62dc296576f8d4, SYM#c702dc0667fe1115cb4b96d2ce1d6e080e5d19c9, SYM#f5637f71798064ce2e576feb3d2e92163cde2b4f]
section_id: app_models_bookmark_bookmark
section_type: class_ref
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
    id: str = uuid.uuid4().hex[:12],
    created_at: datetime = datetime.utcnow,
    updated_at: datetime = datetime.utcnow,
    metadata: Dict[str, Any] = {}
) - > None
```

### Parameters

| Name | Type | Description |
|------|------|-------------|
| **url** | `str` | The bookmarked URL. |
| **title** | `str` | Human-readable title for the bookmark. |
| **description** | `str` = "" | Optional longer description of the bookmark content. |
| **tags** | `List[str]` = [] | List of tag IDs associated with this bookmark. |
| **status** | `[BookmarkStatus](bookmarkstatus.md?sid=app_models_bookmark_bookmarkstatus)` = BookmarkStatus.ACTIVE | The initial visibility status of the bookmark. |
| **id** | `str` = uuid.uuid4().hex[:12] | Unique identifier for the bookmark. |
| **created_at** | `datetime` = datetime.utcnow | Timestamp of creation. |
| **updated_at** | `datetime` = datetime.utcnow | Timestamp of last modification. |
| **metadata** | `Dict[str, Any]` = \{\} | Arbitrary key/value pairs for extensibility. |

---



## Methods

---

#### `archive()`

```python
@classmethod
def archive() - > None
```

Move the bookmark to the archive.

#### Returns

| Type | Description |
|------|-------------|
| `None` | Nothing |

---

#### `trash()`

```python
@classmethod
def trash() - > None
```

Soft-delete the bookmark by moving it to the trash.

#### Returns

| Type | Description |
|------|-------------|
| `None` | Nothing |

---

#### `restore()`

```python
@classmethod
def restore() - > None
```

Restore a trashed or archived bookmark to active status.

#### Returns

| Type | Description |
|------|-------------|
| `None` | Nothing |

---

#### `add_tag()`

```python
@classmethod
def add_tag(
    tag_id: str
) - > bool
```

Attach a tag. Returns False if already present.

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| **tag_id** | `str` | The unique identifier of the tag to associate with this bookmark |

#### Returns

| Type | Description |
|------|-------------|
| `bool` | True if the tag was successfully added, False if the bookmark already contained the tag |

---

#### `remove_tag()`

```python
@classmethod
def remove_tag(
    tag_id: str
) - > bool
```

Detach a tag. Returns False if not found.

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| **tag_id** | `str` | The unique identifier of the tag to remove from this bookmark |

#### Returns

| Type | Description |
|------|-------------|
| `bool` | True if the tag was successfully removed, False if the tag was not found in the bookmark's tag list |

---

#### `to_dict()`

```python
@classmethod
def to_dict() - > Dict[str, Any]
```

Serialise to a plain dictionary for JSON responses.

#### Returns

| Type | Description |
|------|-------------|
| `Dict[str, Any]` | A dictionary representation of the bookmark including its ID, URL, title, status, and timestamps |

---

#### `from_dict()`

```python
@classmethod
def from_dict(
    data: Dict[str, Any]
) - > [Bookmark](bookmark.md?sid=app_models_bookmark_bookmark)
```

Construct a Bookmark from a dictionary (e.g. JSON body).

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| **data** | `Dict[str, Any]` | Dictionary with bookmark fields. |

#### Returns

| Type | Description |
|------|-------------|
| `[Bookmark](bookmark.md?sid=app_models_bookmark_bookmark)` | A new Bookmark instance. |

---
