---
{title: BookmarkStatus, description: API Reference for app.models.bookmark.BookmarkStatus, section_id: app_models_bookmark_bookmarkstatus, section_type: class_ref}
---
# BookmarkStatus

Visibility status of a bookmark.

## Attributes

| Attribute | Type | Description |
|----------|------|-------------|
| **ACTIVE** | `string` = active | Indicates the bookmark is currently visible and accessible in the primary user interface. |
| **ARCHIVED** | `string` = archived | Indicates the bookmark has been moved to long-term storage and is hidden from the main list. |
| **TRASHED** | `string` = trashed | Indicates the bookmark is marked for deletion and resides in the recycle bin. |

---



## Methods

---

#### `ACTIVE()`

```python
def ACTIVE()
```

Represents a bookmark that is currently visible and in use.

---

#### `ARCHIVED()`

```python
def ARCHIVED()
```

Represents a bookmark that has been moved to long-term storage and is hidden from the primary view.

---

#### `TRASHED()`

```python
def TRASHED()
```

Represents a bookmark that has been marked for deletion and is pending permanent removal.

---
