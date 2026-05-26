---
title: Curating Collections
description: A guide to grouping bookmarks into named collections and managing their membership.
code_symbols: [SYM#fdcfaed9972e477ae4585fd1b279ac107fa534cd]
section_id: e538f109-4414-4699-9261-d13552e69f49_curating_collections
doc_type: how_to
section_type: guide
---
To group bookmarks into named collections and manage their membership, use the `BookmarkService` facade. This service provides a high-level API for creating collections, adding or removing bookmarks, and retrieving collection data while handling persistence and validation.

### Creating a Collection

You can create two types of collections: **Manual** (where you explicitly add bookmarks) and **Smart** (which auto-populates based on a filter rule).

```python
from app.services.bookmark_service import BookmarkService

service = BookmarkService()

# Create a Manual collection (default)
manual_data = {
    "name": "Reading List",
    "type": "manual"
}
collection, error = service.create_collection(manual_data)

# Create a Smart collection based on a filter
smart_data = {
    "name": "Python Articles",
    "type": "smart",
    "filter_rule": "python"
}
smart_collection, error = service.create_collection(smart_data)
```

The `create_collection` method returns a tuple of `(Collection, None)` on success or `(None, error_message)` if the name is missing or invalid.

### Managing Bookmark Membership

For manual collections, you can add or remove bookmarks using their unique IDs.

```python
collection_id = "coll_123"
bookmark_id = "book_456"

# Add a bookmark to a collection
success = service.add_to_collection(collection_id, bookmark_id)
if not success:
    print("Failed to add: Collection not found, bookmark already present, or collection is SMART")

# Remove a bookmark from a collection
removed = service.remove_from_collection(collection_id, bookmark_id)
if not removed:
    print("Failed to remove: Collection or bookmark not found in collection")
```

### Advanced Collection Management

While the `BookmarkService` handles membership, the `Collection` model itself provides methods for pinning and reordering. To use these, retrieve the collection, modify it, and save it via the repository (accessible through the service's internal state or by extending the service).

#### Pinning Collections
Pinning a collection allows it to be flagged for priority display (e.g., at the top of a sidebar).

```python
collection = service.get_collection("coll_123")
if collection:
    collection.pin()
    # Note: You must persist the change back to the repository
    service._repo.save_collection(collection)
```

#### Reordering Bookmarks
You can manually define the order of bookmarks within a collection by providing a complete list of IDs.

```python
collection = service.get_collection("coll_123")
new_order = ["id_3", "id_1", "id_2"]

try:
    collection.reorder(new_order)
    service._repo.save_collection(collection)
except ValueError as e:
    # Raised if the new_order list doesn't match the existing bookmark IDs
    print(f"Reorder failed: {e}")
```

### Troubleshooting

*   **Smart Collection Restrictions**: You cannot manually add bookmarks to a "smart" collection. The `add_to_collection` method will return `False` if the collection's `collection_type` is `CollectionType.SMART`.
*   **Duplicate Membership**: `add_to_collection` returns `False` if the bookmark is already a member of the collection to prevent duplicates in the `bookmark_ids` list.
*   **Validation**: The `create_collection` method requires a non-empty `name`. It automatically strips whitespace from the name before creation.
*   **Persistence**: Always ensure you are using the `BookmarkService` singleton (via `BookmarkService()`) to ensure that changes are reflected across all modules, as it manages the internal `BookmarkRepository` and `LRUCache`.
