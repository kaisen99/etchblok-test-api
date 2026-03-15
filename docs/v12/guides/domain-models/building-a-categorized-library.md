---
title: Building a Categorized Library
description: A beginner-friendly tutorial on creating bookmarks, assigning tags, and organizing them into a collection.
code_symbols: [SYM#d731bc2f45cac29b2961ab00083bab5345db0a5e, SYM#e15c91e9e7eae95d052f50388a60d0bc30b3fe67, SYM#97d8a6cbf0c47108aa2beb39fafa695229654067, SYM#6d5b77b3f04288620db996a9bc18b13d3bd1ad3b, SYM#a903c58b7b9829413e7dde33ff94fc7516b965f1, SYM#664bcdae74f24d832fff86d384111517f11be0db]
section_id: b34d3b1e-85c6-46f9-a9a1-b65158f5f506_building_a_categorized_library
doc_type: tutorial
section_type: guide
---
In this tutorial, you will build a categorized digital library by creating bookmarks, labeling them with tags, and organizing them into both manual and automated collections.

### Prerequisites

To follow this tutorial, you need the `BookmarkService` (the primary interface for managing data) and the relevant model enums for status and categorization.

```python
from app.services.bookmark_service import BookmarkService
from app.models.tag import TagColor
from app.models.collection import CollectionType

# Initialize the service
service = BookmarkService()
```

### Step 1: Create a Tag

Tags allow you to label bookmarks across different categories. Each tag has a name and a color for visual identification.

```python
tag_data = {
    "name": "Python",
    "color": TagColor.BLUE.value,
    "description": "Resources related to Python programming"
}

python_tag, error = service.create_tag(tag_data)

if python_tag:
    print(f"Created tag: {python_tag.name} (ID: {python_tag.id})")
```

The `create_tag` method validates the name. Note that names like `all`, `untagged`, `archived`, and `trash` are reserved and will return an error if used. The `TagColor` enum provides preset colors like `RED`, `BLUE`, `GREEN`, and `GRAY`.

### Step 2: Create a Bookmark with Tags

Now, create a bookmark and associate it with the tag you just created. The `Bookmark` model stores tags as a list of their unique IDs.

```python
bookmark_data = {
    "url": "https://docs.python.org/3/",
    "title": "Python Documentation",
    "description": "Official documentation for Python 3",
    "tags": [python_tag.id]
}

bookmark, error = service.create_bookmark(bookmark_data)

if bookmark:
    print(f"Created bookmark: {bookmark.title}")
    print(f"Associated tags: {bookmark.tags}")
```

The `create_bookmark` method automatically validates the URL format using an internal regex pattern and persists the bookmark to the repository. If the URL is invalid (e.g., missing `http://` or `https://`), the service returns an error message.

### Step 3: Organize into a Manual Collection

Collections are groups of bookmarks. A **Manual** collection requires you to explicitly add bookmarks by their ID.

```python
# 1. Create the collection
collection_data = {
    "name": "Learning Path",
    "type": CollectionType.MANUAL.value
}
collection, error = service.create_collection(collection_data)

# 2. Add the bookmark to it
if collection and bookmark:
    success = service.add_to_collection(collection.id, bookmark.id)
    if success:
        print(f"Added '{bookmark.title}' to '{collection.name}'")
```

Manual collections are ideal for curated lists or specific projects where you want full control over the contents. The `add_to_collection` method ensures that the same bookmark isn't added twice.

### Step 4: Automate with a Smart Collection

A **Smart** collection uses a `filter_rule` to automatically include bookmarks that match a keyword in their title or description.

```python
smart_data = {
    "name": "Auto-Python",
    "type": CollectionType.SMART.value,
    "filter_rule": "python"
}

smart_collection, error = service.create_collection(smart_data)

if smart_collection:
    # Smart collections calculate their size based on the filter
    print(f"Created smart collection: {smart_collection.name}")
    print(f"Filter rule: {smart_collection.filter_rule}")
```

Note that you cannot manually add bookmarks to a smart collection; the `add_bookmark` method in the `Collection` class will return `False` if the collection type is `SMART`. These collections are populated dynamically by the service layer.

### Step 5: Manage the Bookmark Lifecycle

As your library grows, you can archive bookmarks to hide them from the main list or move them to the trash.

```python
# Archive the bookmark
archived_bookmark = service.archive_bookmark(bookmark.id)

if archived_bookmark:
    print(f"Status updated to: {archived_bookmark.status.value}")

# If you change your mind, restore it
restored = service.restore_bookmark(bookmark.id)
```

The `archive_bookmark` and `delete_bookmark` (trash) methods automatically update the `updated_at` timestamp via the `_touch()` helper and invalidate any cached versions of the bookmark to ensure data consistency.

### Summary

You have successfully:
1.  Created a **Tag** with a specific color.
2.  Created a **Bookmark** and linked it to that tag.
3.  Grouped the bookmark into a **Manual Collection**.
4.  Set up a **Smart Collection** that automatically finds "Python" resources.
5.  Managed the bookmark's visibility using **Archive** and **Restore**.

To view your complete library, you can use `service.list_bookmarks()` or `service.list_collections()` to see the organized structure you've built.