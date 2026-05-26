---
title: Managing Bookmark States
description: A step-by-step guide to creating bookmarks and transitioning them between active, archived, and trashed states.
code_symbols: [SYM#d731bc2f45cac29b2961ab00083bab5345db0a5e, SYM#d570461c1ff2b0eb81e078e185a46de87938f933, SYM#6d5b77b3f04288620db996a9bc18b13d3bd1ad3b]
section_id: 37c147d9-dbbf-4feb-9fe2-89a46b015296_managing_bookmark_states
doc_type: tutorial
section_type: guide
---
In this tutorial, you will learn how to manage the lifecycle of a bookmark by transitioning it between active, archived, and trashed states. You will use the `Bookmark` model and the `BookmarkStatus` enumeration to control visibility and organization.

### Prerequisites

To follow this guide, you should be familiar with the following classes in the `app.models.bookmark` module:
- `Bookmark`: The core entity representing a saved URL.
- `BookmarkStatus`: An Enum defining the states `ACTIVE`, `ARCHIVED`, and `TRASHED`.

### Step 1: Create an Active Bookmark

When you create a new `Bookmark` instance, it defaults to the `ACTIVE` status. This is the standard state for bookmarks that appear in your main list.

```python
from app.models.bookmark import Bookmark, BookmarkStatus

# Create a new bookmark
bookmark = Bookmark(
    url="https://example.com",
    title="Example Domain",
    description="A site for testing examples"
)

print(f"ID: {bookmark.id}")
print(f"Status: {bookmark.status}")
# Output: Status: BookmarkStatus.ACTIVE
```

The `Bookmark` class automatically generates a unique `id` and sets the `status` to `BookmarkStatus.ACTIVE` upon initialization.

### Step 2: Archive a Bookmark

If you want to keep a bookmark but remove it from your primary view, you can move it to the archive.

```python
# Transition to archived state
bookmark.archive()

print(f"New Status: {bookmark.status}")
print(f"Updated At: {bookmark.updated_at}")
# Output: New Status: BookmarkStatus.ARCHIVED
```

Calling `.archive()` updates the `status` attribute and triggers an internal `_touch()` call, which refreshes the `updated_at` timestamp.

### Step 3: Soft-Delete (Trash) a Bookmark

To "delete" a bookmark without immediately removing it from the database, you can move it to the trash. This is considered a "soft-delete."

```python
# Transition to trashed state
bookmark.trash()

print(f"New Status: {bookmark.status}")
# Output: New Status: BookmarkStatus.TRASHED
```

The `.trash()` method works similarly to `.archive()`, updating the status to `BookmarkStatus.TRASHED` and refreshing the modification timestamp.

### Step 4: Restore a Bookmark

If you accidentally trashed or archived a bookmark, you can return it to the `ACTIVE` state using the `.restore()` method.

```python
# Restore to active state
bookmark.restore()

print(f"Restored Status: {bookmark.status}")
# Output: Restored Status: BookmarkStatus.ACTIVE
```

### Step 5: Manage States via the Service Layer

While you can call methods directly on the `Bookmark` model, the recommended way to manage states in this application is through the `BookmarkService`. The service ensures that changes are persisted to the repository and that the cache is invalidated.

```python
from app.services.bookmark_service import BookmarkService

service = BookmarkService()

# 1. Archive via service
service.archive_bookmark(bookmark.id)

# 2. Soft-delete (trash) via service
# Note: delete_bookmark in the service layer performs a soft-delete
service.delete_bookmark(bookmark.id)

# 3. Restore via service
service.restore_bookmark(bookmark.id)
```

The `BookmarkService` methods (like `archive_bookmark` and `delete_bookmark`) retrieve the bookmark from the `BookmarkRepository`, call the appropriate transition method on the model, save the updated object, and then call `self._cache.invalidate(bookmark_id)` to ensure subsequent lookups return the fresh state.

### Summary and Next Steps

You have successfully moved a bookmark through its entire lifecycle. By using the `archive()`, `trash()`, and `restore()` methods, you can precisely control how bookmarks are categorized.

Next, you might want to explore:
- **Filtering by Status**: Use `service.list_bookmarks(status="archived")` to retrieve bookmarks in a specific state.
- **Tagging**: Use `bookmark.add_tag(tag_id)` to further organize your active or archived bookmarks.
- **Hard Deletion**: Use `BookmarkRepository.delete_bookmark(bookmark_id)` if you need to permanently remove a record from the database.
