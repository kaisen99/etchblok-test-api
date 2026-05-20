---
title: Building a Bookmark Management Workflow
description: A step-by-step tutorial on creating a bookmark, assigning it to a collection, and then searching for it using the service layer.
code_symbols: [SYM#fdcfaed9972e477ae4585fd1b279ac107fa534cd]
section_id: 993be629-3e30-4018-9aaf-e693595238e6_building_a_bookmark_management_workflow
doc_type: tutorial
---

This tutorial walks you through building a complete bookmark management workflow using the `BookmarkService`. You will learn how to initialize the service, create a new bookmark with validation, organize it into a collection, and retrieve it using full-text search.

## Prerequisites

To follow this tutorial, you need the following components from the codebase:
- `BookmarkService` from `app.services.bookmark_service`
- A dictionary of bookmark data (URL and Title are required)

## Step 1: Initialize the Bookmark Service

The `BookmarkService` is implemented as a singleton to ensure that state (like the cache and search index) is shared across your application. You obtain an instance by simply calling the class.

```python
from app.services.bookmark_service import BookmarkService

# Get the singleton instance
service = BookmarkService()
```

When you initialize the service, it automatically bootstraps the `BookmarkRepository`, an `LRUCache` for performance, and the `SearchIndex` for full-text queries.

## Step 2: Create a New Bookmark

The service handles validation for you. When creating a bookmark, you must provide at least a `url` and a `title`. The service uses internal validators (`_validate_url` and `_validate_title`) to ensure the data is correct before persisting it.

```python
bm_data = {
    "url": "https://github.com/features/actions",
    "title": "GitHub Actions Documentation",
    "description": "Learn how to automate your workflow."
}

bookmark, error = service.create_bookmark(bm_data)

if error:
    print(f"Failed to create bookmark: {error}")
else:
    print(f"Created bookmark: {bookmark.id} - {bookmark.title}")
```

The `create_bookmark` method returns a tuple: `(Bookmark, None)` on success or `(None, error_message)` on failure. On success, the bookmark is automatically saved to the repository and added to the search index.

## Step 3: Create a Collection

Collections allow you to group related bookmarks. Like bookmarks, collections are created via the service layer which handles the underlying model instantiation.

```python
collection_data = {
    "name": "DevOps Tools",
    "type": "manual"
}

collection, error = service.create_collection(collection_data)

if error:
    print(f"Failed to create collection: {error}")
else:
    print(f"Created collection: {collection.id} ({collection.name})")
```

By default, collections are `manual`, meaning you must explicitly add bookmarks to them.

## Step 4: Assign the Bookmark to the Collection

Now that you have both a bookmark and a collection, you can link them using their unique IDs.

```python
# Use the IDs from the objects created in previous steps
success = service.add_to_collection(collection.id, bookmark.id)

if success:
    print("Bookmark successfully added to collection.")
else:
    print("Could not add bookmark. It might already be in the collection.")
```

The `add_to_collection` method returns a boolean indicating success. It will return `False` if the collection ID is invalid or if the bookmark is already present in that collection.

## Step 5: Search for the Bookmark

The `BookmarkService` provides a `full_text_search` method that performs a full-text search across bookmark titles and descriptions. This is useful for finding your bookmark later without knowing its ID.

```python
# Search for the bookmark we just created
results = service.full_text_search("GitHub Actions")

for b in results:
    print(f"Found: {b.title} ({b.url})")
```

The search index is updated automatically whenever `create_bookmark` or `update_bookmark` is called, ensuring your search results are always up to date.

## Summary

You have successfully:
1.  Accessed the `BookmarkService` singleton.
2.  Created a validated `Bookmark` entity.
3.  Created a `Collection` for organization.
4.  Linked the bookmark to the collection.
5.  Verified the bookmark is discoverable via full-text search.

For next steps, you can explore `service.archive_bookmark(bookmark_id)` to manage the lifecycle of your bookmarks or `service.create_tag()` to add granular metadata.