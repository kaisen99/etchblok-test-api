---
{title: BookmarkStatus, description: API Reference for app.models.bookmark.BookmarkStatus, section_id: app_models_bookmark_bookmarkstatus, section_type: class_ref}
---
# BookmarkStatus

Visibility status of a bookmark.

## Attributes

| Attribute | Type | Description |
|----------|------|-------------|
| **ACTIVE** | `string` = active | Indicates the bookmark is currently visible and active in the user's main collection. |
| **ARCHIVED** | `string` = archived | Indicates the bookmark has been moved to the archive for long-term storage and is hidden from the active list. |
| **TRASHED** | `string` = trashed | Indicates the bookmark is marked for deletion and resides in the trash bin. |

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

Represents a bookmark that has been moved to storage but is not deleted.

---

#### `TRASHED()`

```python
def TRASHED()
```

Represents a bookmark that has been moved to the trash for pending deletion.

---