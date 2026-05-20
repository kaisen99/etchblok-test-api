---
title: Advanced Collection Management
description: How to pin collections for quick access and reorder bookmarks within manual collections.
code_symbols: [SYM#97d8a6cbf0c47108aa2beb39fafa695229654067]
section_id: 6c0c7d71-6dff-42f9-a7b8-71388db4a88f_advanced_collection_management
doc_type: how_to
section_type: guide
---
Advanced collection management in this project involves leveraging the `Collection` model's capabilities for pinning and custom ordering. While the core `BookmarkService` provides basic CRUD, advanced operations like reordering and pinning are handled directly on the `Collection` model instances.

## Manual vs Smart Collections

The behavior of a collection depends on its `CollectionType`, defined in `app/models/collection.py`.

*   **Manual Collections**: Users explicitly add or remove bookmarks. These support custom reordering.
*   **Smart Collections**: Automatically populated based on a `filter_rule`. These do **not** support manual bookmark addition or reordering.

```python
from app.models.collection import Collection, CollectionType

# Creating a manual collection
manual = Collection(name="Read Later", collection_type=CollectionType.MANUAL)

# Creating a smart collection
smart = Collection(
    name="Python Articles", 
    collection_type=CollectionType.SMART, 
    filter_rule="python"
)
```

## Pinning Collections

You can pin collections to ensure they appear at the top of the sidebar or UI. This is controlled by the `is_pinned` boolean attribute and managed via the `pin()` and `unpin()` methods in `app/models/collection.py`.

```python
from app.services.bookmark_service import BookmarkService

service = BookmarkService()
collection = service.get_collection("coll_123")

if collection:
    # Pin the collection
    collection.pin()
    
    # Persist the change via the repository
    service._repo.save_collection(collection)
```

## Reordering Bookmarks

Manual collections maintain an ordered list of bookmark IDs in the `bookmark_ids` attribute. To change this order, use the `reorder()` method.

### The Reorder Constraint
The `reorder()` method requires that the new list of IDs contains **exactly the same set** of IDs currently in the collection. You cannot use `reorder()` to add or remove bookmarks; you must use `add_bookmark()` or `remove_bookmark()` for that.

```python
# From app/models/collection.py
def reorder(self, bookmark_ids: List[str]) -> None:
    if set(bookmark_ids) != set(self.bookmark_ids):
        raise ValueError("Reorder list must contain exactly the same bookmark IDs")
    self.bookmark_ids = bookmark_ids
```

### Implementation Example
To implement a reorder operation, you typically fetch the collection, update the order, and save:

```python
def update_collection_order(collection_id: str, new_order: list[str]):
    service = BookmarkService()
    collection = service.get_collection(collection_id)
    
    if not collection:
        return False
        
    try:
        # This will raise ValueError if IDs don't match exactly
        collection.reorder(new_order)
        service._repo.save_collection(collection)
        return True
    except ValueError:
        return False
```

## Extending the Service Layer

Since `BookmarkService` (in `app/services/bookmark_service.py`) does not currently expose pinning or reordering via its public API, you can extend it to support these operations:

```python
# Example of how to extend BookmarkService logic
class EnhancedBookmarkService(BookmarkService):
    def set_collection_pin(self, collection_id: str, pinned: bool) -> bool:
        collection = self.get_collection(collection_id)
        if not collection:
            return False
            
        if pinned:
            collection.pin()
        else:
            collection.unpin()
            
        self._repo.save_collection(collection)
        return True

    def reorder_collection(self, collection_id: str, bookmark_ids: list[str]) -> bool:
        collection = self.get_collection(collection_id)
        if not collection or collection.is_smart:
            return False
            
        try:
            collection.reorder(bookmark_ids)
            self._repo.save_collection(collection)
            return True
        except ValueError:
            return False
```

## Troubleshooting

*   **Smart Collection Reordering**: If you attempt to call `add_bookmark()` or `reorder()` on a collection where `collection_type == CollectionType.SMART`, the operation will either return `False` or fail to have an effect on the dynamic list.
*   **ValueError in Reorder**: If `reorder()` raises a `ValueError`, verify that you haven't accidentally included a new bookmark ID or omitted an existing one. The sets must be identical.
*   **Persistence**: Changes made to a `Collection` object in memory are not saved until `service._repo.save_collection(collection)` is called.