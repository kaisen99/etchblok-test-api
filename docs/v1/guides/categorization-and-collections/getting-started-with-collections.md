---
title: Getting Started with Collections
description: A step-by-step tutorial on creating your first collection and adding bookmarks to it.
code_symbols: [SYM#97d8a6cbf0c47108aa2beb39fafa695229654067, SYM#dd5fd545693e00d6c0b38892bbd18ed4afa136a1]
section_id: e1503434-7390-4a34-8b8f-f3ceff7a7d0c_getting_started_with_collections
doc_type: tutorial
section_type: guide
---
Collections allow you to organize your bookmarks into logical groups. In this tutorial, you will learn how to create both manual collections (where you choose which bookmarks to include) and smart collections (which auto-populate based on keywords).

### Prerequisites

To follow this tutorial, you should have the API running and be familiar with sending JSON requests. You will interact with the following components:
- `BookmarkService`: The core logic handler for bookmarks and collections.
- `Collection`: The data model representing a group of bookmarks.
- API endpoints registered under `/api/bookmarks` and `/api/collections`.

### Step 1: Create a Bookmark

Before you can organize bookmarks into collections, you need a bookmark to work with. Use the `POST /api/bookmarks/` endpoint to create one.

```bash
curl -X POST http://localhost:5000/api/bookmarks/ \
     -H "Content-Type: application/json" \
     -d '{
           "url": "https://www.python.org",
           "title": "Python Programming Language",
           "description": "The official home of the Python Programming Language"
         }'
```

This request is handled by `create_bookmark` in `app/routes/bookmarks.py`, which delegates to `BookmarkService.create_bookmark`. It returns a JSON object containing the bookmark's `id`. Note this ID for the next steps.

### Step 2: Create a Manual Collection

A manual collection is a static list of bookmarks. You create it by sending a request to the `POST /api/collections/` endpoint.

```bash
curl -X POST http://localhost:5000/api/collections/ \
     -H "Content-Type: application/json" \
     -d '{
           "name": "Development Tools",
           "type": "manual"
         }'
```

The `BookmarkService.create_collection` method validates that a name is provided and initializes a new `Collection` object with `CollectionType.MANUAL`. The response will include a unique `id` for your new collection.

### Step 3: Add the Bookmark to the Collection

Now that you have both a bookmark and a collection, you can link them. Use the `PUT /api/collections/<collection_id>/bookmarks` endpoint.

```bash
curl -X PUT http://localhost:5000/api/collections/<collection_id>/bookmarks \
     -H "Content-Type: application/json" \
     -d '{
           "bookmark_id": "<bookmark_id>"
         }'
```

This triggers `BookmarkService.add_to_collection`. Internally, the `Collection.add_bookmark` method (found in `app/models/collection.py`) appends the ID to the `bookmark_ids` list. 

> **Note:** If you try to add the same bookmark twice, `add_bookmark` returns `False` and the API will return a `400 Bad Request` error.

### Step 4: Create a Smart Collection

Smart collections are dynamic. Instead of adding bookmarks manually, you define a `filter_rule`. Any bookmark with a title or description containing the rule's keyword will be included automatically.

```bash
curl -X POST http://localhost:5000/api/collections/ \
     -H "Content-Type: application/json" \
     -d '{
           "name": "Python News",
           "type": "smart",
           "filter_rule": "python"
         }'
```

When you retrieve this collection via `GET /api/collections/<id>`, the system uses `Collection._apply_filter` to scan all bookmarks for the word "python". 

### Summary of Results

You have successfully:
1. Created a bookmark using the `BookmarkService`.
2. Created a `MANUAL` collection for explicit organization.
3. Linked a bookmark to a collection using its unique ID.
4. Created a `SMART` collection that uses a `filter_rule` for automatic grouping.

To see all your collections and their current sizes, you can call `GET /api/collections/`. This endpoint uses `Collection.to_dict` to return metadata for every collection, including the `size` property which calculates the number of bookmarks currently matched or assigned.

### Next Steps
- Explore **Pinning**: Use the `pin()` method on a `Collection` to mark it as a favorite for sidebar display.
- **Reordering**: For manual collections, you can use the `reorder()` method to change the sequence of bookmarks by providing a new list of IDs.