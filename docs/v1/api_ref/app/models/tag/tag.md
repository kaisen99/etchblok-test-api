---
{title: Tag, description: API Reference for app.models.tag.Tag, section_id: app_models_tag_tag, section_type: class_ref}
---
# Tag

A label that can be attached to one or more bookmarks.

## Attributes

| Attribute | Type | Description |
|----------|------|-------------|
| **id** | `str` | Unique identifier. |
| **name** | `str` | Display name (must be unique per user). |
| **color** | `[TagColor](tagcolor.md?sid=app_models_tag_tagcolor)` = TagColor.GRAY | Visual colour for UI rendering. |
| **description** | `str` | Optional description of what this tag represents. |
| **usage_count** | `int` = 0 | Number of bookmarks currently using this tag. |

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
)
```

### Parameters

| Name | Type | Description |
|------|------|-------------|
| **name** | `str` | Display name of the tag. |
| **color** | `[TagColor](tagcolor.md?sid=app_models_tag_tagcolor)` = TagColor.GRAY | Visual colour for UI rendering. |
| **description** | `str` = "" | Optional description of what this tag represents. |
| **id** | `str` = uuid.uuid4().hex[:8] | Unique identifier. |
| **usage_count** | `int` = 0 | Number of bookmarks currently using this tag. |

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
| **new_name** | `str` | The new display name for the tag, which must be non-empty and under 50 characters. |

#### Returns

| Type | Description |
|------|-------------|
| `None` | Nothing is returned; the tag instance is updated in place. |

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
| `int` | The updated total number of bookmarks associated with this tag. |

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
| `int` | The updated total number of bookmarks associated with this tag, clamped to a minimum of zero. |

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
| **data** | `Dict[str, Any]` | A dictionary containing tag attributes such as name, color, and description. |

#### Returns

| Type | Description |
|------|-------------|
| `[Tag](tag.md?sid=app_models_tag_tag)` | A new instance of the Tag class populated with data from the provided dictionary. |

---
