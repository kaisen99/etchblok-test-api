---
title: Building a Collection System
description: A step-by-step tutorial on creating collections and organizing bookmarks within them using the service layer.
code_symbols: [SYM#fdcfaed9972e477ae4585fd1b279ac107fa534cd]
section_id: aea3934c-2db4-4f1a-9832-3c624a6de066_building_a_collection_system
doc_type: tutorial
section_type: guide
---
This tutorial walks you through building a collection system to organize your bookmarks using the `BookmarkService`. You will learn how to create collections, add bookmarks to them, and manage their contents.

### Prerequisites

To follow this tutorial, you need the `BookmarkService` initialized. Since it is a singleton, you can instantiate it directly in your module.

```python
from app.services.bookmark_service import BookmarkService

# Initialize the service singleton
service = BookmarkService()
```

### Step 1: Create a Bookmark

Before you can organize bookmarks into collections, you need a bookmark to work with. Use `create_bookmark` to persist a new entry.

```python
bookmark_data = {
    "url": "https://example.com",
    "title": "Example Domain",
    "description": "A site for examples"
}

bookmark, error = service.create_bookmark(bookmark_data)

if error:
    print(f"Failed to create bookmark: {error}")
else:
    print(f"Created bookmark with ID: {bookmark.id}")
```

The `create_bookmark` method validates the URL and title before persisting the bookmark to the repository and indexing it for search.

### Step 2: Create a Manual Collection

Collections in this system can be **manual** (where you explicitly add bookmarks) or **smart** (which auto-populate based on rules). We will start by creating a manual collection.

```python
collection_data = {
    "name": "Research Project",
    "type": "manual"
}

collection, error = service.create_collection(collection_data)

if error:
    print(f"Failed to create collection: {error}")
else:
    print(f"Created collection: {collection.name} (ID: {collection.id})")
```

The `create_collection` method requires a `name`. If the `type` is not specified, it defaults to `manual`.

### Step 3: Add a Bookmark to the Collection

Now that you have both a bookmark and a collection, you can link them using `add_to_collection`.

```python
success = service.add_to_collection(collection.id, bookmark.id)

if success:
    print(f"Successfully added bookmark {bookmark.id} to collection {collection.id}")
else:
    # This might fail if the collection is 'smart' or the bookmark is already present
    print("Failed to add bookmark to collection.")
```

When you call `add_to_collection`, the service retrieves the `Collection` model and calls its internal `add_bookmark` method. Note that if the collection is a **smart** collection, this operation will return `False` because smart collections are read-only for manual additions.

### Step 4: Verify Collection Contents

You can retrieve the collection at any time to see which bookmarks it contains. The `Collection` object stores a list of bookmark IDs.

```python
# Retrieve the updated collection
updated_collection = service.get_collection(collection.id)

if updated_collection:
    print(f"Collection '{updated_collection.name}' now contains {updated_collection.size} bookmark(s).")
    print(f"Bookmark IDs: {updated_collection.bookmark_ids}")
```

The `size` property on the `Collection` class provides a quick count of the associated bookmarks.

### Step 5: Remove a Bookmark from a Collection

If you no longer need a bookmark in a specific collection, use `remove_from_collection`.

```python
removed = service.remove_from_collection(collection.id, bookmark.id)

if removed:
    print("Bookmark removed from collection.")
else:
    print("Bookmark was not in the collection or collection not found.")
```

This method updates the `Collection` model and persists the change back to the `BookmarkRepository`.

### Summary of Results

By following these steps, you have:
1.  Initialized the central `BookmarkService`.
2.  Created a persistent `Bookmark`.
3.  Created a `Collection` to group related items.
4.  Organized your bookmarks by adding and removing them from the collection.

For more advanced organization, you can explore **Smart Collections** by passing `type: "smart"` and a `filter_rule` (e.g., `"example"`) when creating a collection. Smart collections automatically include bookmarks whose title or description matches the rule.
