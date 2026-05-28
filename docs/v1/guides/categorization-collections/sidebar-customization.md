---
title: Sidebar Customization
description: How to use pinning and unpinning methods to manage the visibility and priority of collections in the user interface.
code_symbols: [SYM#97d8a6cbf0c47108aa2beb39fafa695229654067, SYM#664bcdae74f24d832fff86d384111517f11be0db]
section_id: e7c6f8a0-d72a-414e-a81d-a96c494ddd70_sidebar_customization
doc_type: how_to
section_type: guide
---
To manage the visibility and priority of collections in the sidebar, use the pinning methods provided by the `Collection` model. Pinning a collection sets its `is_pinned` attribute to `True`, which the user interface uses to prioritize that collection at the top of the sidebar.

### Pinning and Unpinning a Collection

You can toggle the pinned status of any collection instance using the `pin()` and `unpin()` methods.

```python
from app.models.collection import Collection

# Initialize a collection
collection = Collection(name="Urgent Reading")

# Pin the collection to the top of the sidebar
collection.pin()
print(collection.is_pinned)  # True

# Unpin the collection to return it to standard sorting
collection.unpin()
print(collection.is_pinned)  # False
```

### Pinning Smart Collections

Pinning works identically for both `MANUAL` and `SMART` collections. This allows you to prioritize auto-populated collections (like those based on a specific keyword) alongside manually curated ones.

```python
from app.models.collection import Collection, CollectionType

# Create a smart collection for Python-related bookmarks
python_col = Collection(
    name="Python News",
    collection_type=CollectionType.SMART,
    filter_rule="python"
)

# Pin it so it stays at the top of the sidebar
python_col.pin()
```

### Persisting Pin Status

Because the `BookmarkService` does not currently expose a dedicated pinning method, you must interact with the `BookmarkRepository` directly or extend the service to persist the change after calling `pin()` or `unpin()`.

```python
from app.services.bookmark_service import BookmarkService
from app.db.repository import BookmarkRepository

service = BookmarkService()
repo = BookmarkRepository()

# 1. Retrieve the collection via the service
collection = service.get_collection("col_123abc")

if collection:
    # 2. Update the pin status on the model instance
    collection.pin()
    
    # 3. Persist the change using the repository
    repo.save_collection(collection)
```

### Serialization for the UI

When a collection is serialized using `to_dict()`, the `is_pinned` status is included. This allows the frontend to correctly position the collection in the sidebar.

```python
collection = Collection(name="Favorites")
collection.pin()

# The dictionary representation includes the pin status
data = collection.to_dict()
# {
#   "id": "...",
#   "name": "Favorites",
#   "is_pinned": True,
#   ...
# }
```

### Troubleshooting

**Pinning via REST API**
The current REST API routes in `app/routes/collections.py` do not provide an endpoint to pin or unpin collections. To support this in the UI, you must add a new route that calls the model's `pin()` method and saves the collection via the repository.

**Manual vs. Smart Collections**
While `add_bookmark()` returns `False` for smart collections, `pin()` and `unpin()` are always available regardless of the `collection_type`. Pinning only affects UI placement and does not interfere with the `filter_rule` logic of smart collections.
