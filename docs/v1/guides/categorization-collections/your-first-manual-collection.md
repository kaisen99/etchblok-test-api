---
title: Your First Manual Collection
description: A step-by-step tutorial on initializing a collection, adding bookmarks, and reordering them for custom display.
code_symbols: [SYM#97d8a6cbf0c47108aa2beb39fafa695229654067, SYM#664bcdae74f24d832fff86d384111517f11be0db]
section_id: f18d1e3e-fd38-4821-a380-1eed070a0375_your_first_manual_collection
doc_type: tutorial
section_type: guide
---
In this tutorial, you will learn how to create and manage a manual bookmark collection using the `Collection` model. You will initialize a collection, add specific bookmarks to it, and then reorder them for a custom display sequence.

### Prerequisites

To follow this tutorial, you need the `app.models.collection` module available in your environment. You should also have the IDs of the bookmarks you wish to group.

### Step 1: Initialize a Manual Collection

First, create a new instance of the `Collection` class. By default, collections are initialized with the `MANUAL` type, meaning you must explicitly add bookmarks to them.

```python
from app.models.collection import Collection

# Initialize a collection with a descriptive name
my_collection = Collection(name="Project Resources")

print(f"Collection Created: {my_collection.name}")
print(f"Type: {my_collection.collection_type.value}")
print(f"ID: {my_collection.id}")
```

When you initialize a `Collection`, the system automatically generates a unique 10-character hex ID (e.g., `a1b2c3d4e5`) and sets the `collection_type` to `CollectionType.MANUAL`.

### Step 2: Add Bookmarks to the Collection

Use the `add_bookmark` method to include bookmarks in your collection. This method requires the unique ID of the bookmark you want to add.

```python
# Bookmark IDs are typically 12-character hex strings in this system
bookmark_1 = "5f3a2b1c0d9e"
bookmark_2 = "1a2b3c4d5e6f"

# Add bookmarks to the collection
my_collection.add_bookmark(bookmark_1)
my_collection.add_bookmark(bookmark_2)

print(f"Collection Size: {my_collection.size}")
print(f"Bookmark IDs: {my_collection.bookmark_ids}")
```

The `add_bookmark` method returns `True` if the bookmark was successfully added. It will return `False` if the bookmark is already in the collection or if you attempt to add a bookmark to a `SMART` collection (which uses automated filters instead).

### Step 3: Reorder the Bookmarks

One of the primary benefits of a manual collection is the ability to define a custom order. You can use the `reorder` method to change the sequence of bookmarks.

```python
# Define a new order using the existing IDs
new_order = ["1a2b3c4d5e6f", "5f3a2b1c0d9e"]

# Apply the new order
try:
    my_collection.reorder(new_order)
    print("Reorder successful!")
    print(f"New Order: {my_collection.bookmark_ids}")
except ValueError as e:
    print(f"Reorder failed: {e}")
```

**Important Constraint:** The `reorder` method requires a list that contains the exact same set of bookmark IDs currently in the collection. If you provide a list with missing IDs or extra IDs, it will raise a `ValueError`.

### Step 4: Pin and Serialize for Storage

Finally, you can pin the collection so it appears at the top of the user interface and serialize it to a dictionary for saving to a database or returning via an API.

```python
# Pin the collection for quick access
my_collection.pin()

# Convert the collection to a JSON-safe dictionary
collection_data = my_collection.to_dict()

print("Serialized Collection Data:")
print(collection_data)
```

The `to_dict()` method produces a dictionary containing the `id`, `name`, `type`, `bookmark_ids`, and `is_pinned` status, along with the `created_at` timestamp in ISO format.

### Summary

You have successfully:
1. Created a manual collection using `Collection(name=...)`.
2. Populated it with bookmark IDs using `add_bookmark()`.
3. Customized the display order using `reorder()`.
4. Prepared the collection for the UI and storage using `pin()` and `to_dict()`.

To see how these collections are persisted and retrieved in a real application, explore the `app.services.bookmark_service.BookmarkService` class.
