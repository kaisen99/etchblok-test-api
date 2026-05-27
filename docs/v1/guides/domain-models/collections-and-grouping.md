---
title: Collections and Grouping
description: Understanding the difference between manual and smart collections for organizing bookmarks.
code_symbols: [SYM#97d8a6cbf0c47108aa2beb39fafa695229654067, SYM#67d634120bee630945450829e511171fd936cf36, SYM#664bcdae74f24d832fff86d384111517f11be0db]
section_id: a1c2399b-d47a-41e1-823f-3c0f541b03f1_collections_and_grouping
doc_type: guide
section_type: guide
---
In this project, collections provide a way to organize bookmarks into named groups. Unlike tags, which are flat labels applied to individual bookmarks, collections are distinct entities that can either be managed manually by the user or populated dynamically based on search criteria.

## Collection Types

The behavior of a collection is determined by its `CollectionType`, defined in `app/models/collection.py`. There are two primary types:

*   **Manual (`CollectionType.MANUAL`)**: These function as traditional folders or playlists. The user explicitly adds or removes bookmarks, and the order of bookmarks is preserved.
*   **Smart (`CollectionType.SMART`)**: These are dynamic views. They use a `filter_rule` to automatically include bookmarks that match specific text in their title or description.

```python
class CollectionType(Enum):
    """The kind of collection."""
    MANUAL = "manual"
    SMART = "smart"
```

## The Collection Model

The `Collection` class (found in `app/models/collection.py`) tracks the membership and metadata for a group. 

### Core Attributes
- `bookmark_ids`: A list of strings representing the IDs of bookmarks in the collection. For manual collections, this list is ordered.
- `filter_rule`: A string used by smart collections to match bookmarks.
- `is_pinned`: A boolean flag that indicates if the collection should be featured at the top of the user interface.

### Manual Membership Management
For manual collections, the model provides methods to modify the `bookmark_ids` list. Note that `add_bookmark` will return `False` if you attempt to call it on a smart collection.

```python
def add_bookmark(self, bookmark_id: str) -> bool:
    """Add a bookmark to a manual collection."""
    if self.is_smart or bookmark_id in self.bookmark_ids:
        return False
    self.bookmark_ids.append(bookmark_id)
    return True

def reorder(self, bookmark_ids: List[str]) -> None:
    """Replace the bookmark ordering."""
    if set(bookmark_ids) != set(self.bookmark_ids):
        raise ValueError("Reorder list must contain exactly the same bookmark IDs")
    self.bookmark_ids = bookmark_ids
```

## Smart Collections and Filtering

Smart collections do not store a static list of bookmarks in the database in the same way manual ones do. Instead, they rely on the `filter_rule` attribute. The `Collection` model includes an internal method `_apply_filter` that the service layer uses to determine which bookmarks belong to the collection at runtime.

The current implementation performs a case-insensitive substring match against both the `title` and `description` of a bookmark:

```python
def _apply_filter(self, bookmarks: list) -> List[str]:
    """Evaluate the filter_rule against a list of bookmarks."""
    if not self.filter_rule:
        return []
    keyword = self.filter_rule.lower()
    return [b.id for b in bookmarks if keyword in b.title.lower() or keyword in b.description.lower()]
```

## Service Integration

The `BookmarkService` in `app/services/bookmark_service.py` acts as the primary interface for interacting with collections. It handles the orchestration between the `Collection` model and the `BookmarkRepository`.

When creating a collection via the service, the `from_dict` method is used to initialize the object. It is important to note that `from_dict` only populates the `name`, `type`, and `filter_rule`, while generating a new `id` and `created_at` timestamp automatically.

```python
# Example of creating a collection through the service
def create_collection(self, data: Dict[str, Any]) -> Tuple[Optional[Collection], Optional[str]]:
    name = data.get("name", "").strip()
    if not name:
        return None, "Collection name is required"
    collection = Collection.from_dict(data)
    self._repo.save_collection(collection)
    return collection, None
```

## Constraints and Considerations

1.  **Immutability of Smart Collections**: You cannot manually add a bookmark to a smart collection using `add_bookmark`. Membership is strictly governed by the `filter_rule`.
2.  **Reordering Validation**: The `reorder` method enforces that the new list of IDs must be an exact permutation of the existing IDs. You cannot use `reorder` to add or remove items.
3.  **Serialization**: The `to_dict` method includes a calculated `size` property (the length of `bookmark_ids`), which is useful for UI components that display item counts in the sidebar.
4.  **Persistence**: While the `Collection` model tracks `bookmark_ids`, the `BookmarkService` is responsible for calling `self._repo.save_collection(collection)` to persist changes to the underlying data store.
