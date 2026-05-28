---
title: Understanding Collections
description: 'An overview of the two primary grouping mechanisms: manual collections for curated lists and smart collections for automated filtering.'
code_symbols: [SYM#97d8a6cbf0c47108aa2beb39fafa695229654067, SYM#664bcdae74f24d832fff86d384111517f11be0db, SYM#67d634120bee630945450829e511171fd936cf36]
section_id: 8aa3643f-36cc-4774-a053-4a260266907f_understanding_collections
doc_type: guide
section_type: guide
---
Collections in this project provide a way to group bookmarks beyond simple tagging. Implemented in `app/models/collection.py`, they support two distinct modes of operation: manual curation and automated filtering.

## Collection Types

The behavior of a collection is determined by its `CollectionType` enum:

- **MANUAL**: A curated list where bookmarks are explicitly added or removed by the user.
- **SMART**: A dynamic list that identifies bookmarks based on a `filter_rule`.

### Manual Collections
Manual collections are the default type. They maintain an ordered list of bookmark IDs in the `bookmark_ids` attribute. When a bookmark is added via the `BookmarkService.add_to_collection` method, the model performs a check to ensure it isn't a smart collection before appending the ID.

```python
# From app/models/collection.py
def add_bookmark(self, bookmark_id: str) -> bool:
    """Add a bookmark to a manual collection."""
    if self.is_smart or bookmark_id in self.bookmark_ids:
        return False
    self.bookmark_ids.append(bookmark_id)
    return True
```

### Smart Collections
Smart collections use a `filter_rule` (a string keyword) to automatically select bookmarks. The `Collection` class includes an internal `_apply_filter` method that evaluates this rule against bookmark titles and descriptions.

```python
# From app/models/collection.py
def _apply_filter(self, bookmarks: list) -> List[str]:
    """Evaluate the filter_rule against a list of bookmarks."""
    if not self.filter_rule:
        return []
    keyword = self.filter_rule.lower()
    return [b.id for b in bookmarks if keyword in b.title.lower() or keyword in b.description.lower()]
```

> [!IMPORTANT]
> While the filtering logic exists within the `Collection` model, the current implementation of `BookmarkService` does not yet automatically invoke `_apply_filter` to populate smart collections. Currently, smart collections primarily serve as containers for the filter metadata.

## Organization and Ordering

Collections include built-in mechanisms for UI organization and custom sorting.

### Pinning
The `is_pinned` boolean attribute allows specific collections to be highlighted or moved to the top of a list (e.g., a sidebar). This is toggled using the `pin()` and `unpin()` methods.

### Custom Reordering
For manual collections, the order of bookmarks is preserved in the `bookmark_ids` list. The `reorder()` method allows users to update this sequence, provided the new list contains the exact same set of bookmark IDs currently in the collection.

```python
# From app/models/collection.py
def reorder(self, bookmark_ids: List[str]) -> None:
    """Replace the bookmark ordering."""
    if set(bookmark_ids) != set(self.bookmark_ids):
        raise ValueError("Reorder list must contain exactly the same bookmark IDs")
    self.bookmark_ids = bookmark_ids
```

## Service Integration

The `BookmarkService` in `app/services/bookmark_service.py` acts as the orchestrator for collection operations. It handles the lifecycle of a collection—from creation via `Collection.from_dict` to persistence in the `BookmarkRepository`.

When adding a bookmark to a collection, the service follows this flow:
1. Retrieves the `Collection` instance from the repository.
2. Calls `collection.add_bookmark(bookmark_id)`.
3. If successful (i.e., the collection is manual and the bookmark isn't already present), it saves the updated collection back to the repository.

```python
# From app/services/bookmark_service.py
def add_to_collection(self, collection_id: str, bookmark_id: str) -> bool:
    """Add a bookmark to a collection."""
    collection = self._repo.get_collection(collection_id)
    if not collection:
        return False
    if not collection.add_bookmark(bookmark_id):
        return False
    self._repo.save_collection(collection)
    return True
```

## Data Structure Summary

A `Collection` is identified by a 10-character hex string (e.g., `5f3e1a2b3c`) generated during instantiation. Its full state can be serialized for API responses using the `to_dict()` method, which includes a calculated `size` property representing the number of bookmarks currently in the group.
