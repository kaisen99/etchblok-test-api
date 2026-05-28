---
title: Tag
description: API Reference for app.models.tag.Tag
code_symbols: [SYM#a903c58b7b9829413e7dde33ff94fc7516b965f1, SYM#6a03d3d0ae6ff5f594877f1f40b42f32b934808e, SYM#4b353fa499d5c4906b30897430d9d69a054c1b75, SYM#f0cc288d0c7dde565ef362480a4eef357ee21a2b, SYM#bd377a205d7fb23a6f279ba3e93c68d7a89ddc38, SYM#e9453f714a72ab8f2546d11e37761408695a0328, SYM#9754c428eeae127cfd748b7b3b910f19263c8218, SYM#024158153015912f0d9e07d937a97f611331306f, SYM#ca3301654683abc05d569ce57c6ccae6abd96d8d]
section_id: app_models_tag_tag
section_type: class_ref
---
# Tag

A label that can be attached to one or more bookmarks.

## Attributes

| Attribute | Type | Description |
|----------|------|-------------|
| **name** | `string` | Display name (must be unique per user). |
| **color** | `[TagColor](tagcolor.md?sid=app_models_tag_tagcolor)` = TagColor.GRAY | Visual colour for UI rendering. |
| **description** | `string` | Optional description of what this tag represents. |
| **id** | `string` = uuid.uuid4().hex[:8] | Unique identifier. |
| **usage_count** | `integer` = 0 | Number of bookmarks currently using this tag. |

---

## Constructor

### Signature

```python
def Tag(
    name: str,
    color: [TagColor](tagcolor.md?sid=app_models_tag_tagcolor) = TagColor.GRAY,
    description: str = "",
    id: str = uuid.uuid4().hex[:8],
    usage_count: int = 0
) - > None
```

### Parameters

| Name | Type | Description |
|------|------|-------------|
| **name** | `str` | The display name of the tag. |
| **color** | `[TagColor](tagcolor.md?sid=app_models_tag_tagcolor)` = TagColor.GRAY | The visual color assigned to the tag. |
| **description** | `str` = "" | An optional description of the tag. |
| **id** | `str` = uuid.uuid4().hex[:8] | A unique identifier for the tag. |
| **usage_count** | `int` = 0 | The initial number of bookmarks using this tag. |

---



## Methods

---

#### `rename()`

```python
@classmethod
def rename(
    new_name: str
) - > None
```

Rename the tag.

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| **new_name** | `str` | The new display name. |

#### Returns

| Type | Description |
|------|-------------|
| `None` |  |

---

#### `increment_usage()`

```python
@classmethod
def increment_usage() - > int
```

Record that a bookmark now uses this tag. Returns new count.

#### Returns

| Type | Description |
|------|-------------|
| `int` | The updated usage count after incrementing. |

---

#### `decrement_usage()`

```python
@classmethod
def decrement_usage() - > int
```

Record that a bookmark removed this tag. Returns new count.

#### Returns

| Type | Description |
|------|-------------|
| `int` | The updated usage count after decrementing, ensuring it does not fall below zero. |

---

#### `to_dict()`

```python
@classmethod
def to_dict() - > Dict[str, Any]
```

Serialise to a JSON-safe dictionary.

#### Returns

| Type | Description |
|------|-------------|
| `Dict[str, Any]` | A dictionary containing the tag's ID, name, color value, description, and usage count. |

---

#### `from_dict()`

```python
@classmethod
def from_dict(
    data: Dict[str, Any]
) - > [Tag](tag.md?sid=app_models_tag_tag)
```

Construct a Tag from a dictionary.

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| **data** | `Dict[str, Any]` | The dictionary containing tag attributes like name, color, and description. |

#### Returns

| Type | Description |
|------|-------------|
| `[Tag](tag.md?sid=app_models_tag_tag)` | A new Tag instance populated with the provided dictionary data. |

---
