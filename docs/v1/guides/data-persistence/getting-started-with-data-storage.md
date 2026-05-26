---
title: Getting Started with Data Storage
description: A step-by-step tutorial on initializing the BookmarkRepository and performing your first save and retrieval operations.
code_symbols: [SYM#09a56e7acb86a9afef18a62134c27802cd473050, SYM#adb8232356346a5957ff3a1a1b7ff70581f37649]
section_id: 67c894f6-c29d-4846-98f6-5684aa1f8e7a_getting_started_with_data_storage
doc_type: tutorial
section_type: guide
---
This tutorial guides you through using the `BookmarkRepository` to manage your data. You will learn how to initialize the repository, perform CRUD (Create, Read, Update, Delete) operations on bookmarks and tags, and handle pagination.

### Prerequisites

To follow this tutorial, ensure you have the core models available in your environment:
- `BookmarkRepository` from `app.db.repository`
- `Bookmark` and `BookmarkStatus` from `app.models.bookmark`
- `Tag` from `app.models.tag`

### Step 1: Initialize the Repository

The `BookmarkRepository` is an in-memory data store. In a production environment, this is typically managed as a singleton within a service, but for this tutorial, we will instantiate it directly.

```python
from app.db.repository import BookmarkRepository

# Initialize the in-memory storage
repo = BookmarkRepository()
```

The repository provides separate storage for bookmarks, tags, and collections. Since it is in-memory, all data will be lost when the process terminates.

### Step 2: Create and Save a Bookmark

To store data, you first create a `Bookmark` model instance and then pass it to the repository's `save_bookmark` method.

```python
from app.models.bookmark import Bookmark

# Create a new bookmark instance
new_bookmark = Bookmark(
    url="https://github.com/kaisen99",
    title="Kaisen99 GitHub",
    description="Project repository"
)

# Persist it to the repository
repo.save_bookmark(new_bookmark)

print(f"Saved bookmark with ID: {new_bookmark.id}")
```

The `save_bookmark` method handles both inserts and updates. If a bookmark with the same `id` already exists in the repository, it will be overwritten with the new data.

### Step 3: Retrieve and List Bookmarks

Once saved, you can retrieve a single bookmark by its ID or list multiple bookmarks using pagination.

```python
# Retrieve by ID
retrieved = repo.get_bookmark(new_bookmark.id)
if retrieved:
    print(f"Found: {retrieved.title}")

# List bookmarks with pagination (1-based index)
# Returns a tuple: (list_of_items, total_count)
items, total = repo.list_bookmarks(page=1, per_page=10)

print(f"Total bookmarks: {total}")
for item in items:
    print(f"- {item.title} ({item.url})")
```

Note that `list_bookmarks` uses **1-based indexing** for the `page` parameter. It also supports an optional `status` filter (e.g., "active", "archived", "trashed") to narrow down results.

### Step 4: Organize with Tags

The repository also manages `Tag` entities. You can save tags and then associate their IDs with bookmarks.

```python
from app.models.tag import Tag, TagColor

# 1. Create and save a tag
dev_tag = Tag(name="Development", color=TagColor.BLUE)
repo.save_tag(dev_tag)

# 2. Associate the tag with the bookmark
new_bookmark.add_tag(dev_tag.id)
repo.save_bookmark(new_bookmark) # Update the bookmark in storage

# 3. Query bookmarks by tag
tagged_bookmarks = repo.get_bookmarks_with_tag(dev_tag.id)
print(f"Bookmarks tagged with '{dev_tag.name}': {len(tagged_bookmarks)}")
```

When you call `get_bookmarks_with_tag`, the repository filters its internal collection to return only bookmarks that include the specified `tag_id` in their `tags` list.

### Step 5: Delete Data

The repository provides a `delete_bookmark` method for permanent removal.

```python
# Hard delete from the repository
success = repo.delete_bookmark(new_bookmark.id)

if success:
    print("Bookmark permanently removed.")
else:
    print("Bookmark not found.")
```

**Important Note on Deletion:**
The `BookmarkRepository.delete_bookmark` method performs a **hard delete**, removing the record entirely from memory. If you want to perform a **soft delete** (moving a bookmark to the "Trash"), you should use the `Bookmark.trash()` method and then save the updated bookmark, or use the higher-level `BookmarkService`.

### Summary

You have successfully:
1. Initialized a `BookmarkRepository`.
2. Created and persisted a `Bookmark`.
3. Retrieved data using both direct ID lookups and paginated lists.
4. Created `Tag` entities and linked them to bookmarks.
5. Performed a hard delete.

For more advanced operations like full-text search or complex validation, look into the `SearchIndex` and `BookmarkService` classes.
