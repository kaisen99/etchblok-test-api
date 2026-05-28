---
title: Grouping with Collections
description: Covers the organization of bookmarks into manual and smart collections, including pinning and reordering logic.
code_symbols: [SYM#97d8a6cbf0c47108aa2beb39fafa695229654067, SYM#664bcdae74f24d832fff86d384111517f11be0db, SYM#67d634120bee630945450829e511171fd936cf36]
section_id: d38aab5f-df15-487e-800f-d55358c8b6e2_grouping_with_collections
doc_type: guide
section_type: guide
---
Bookmarks in this project can be organized into logical groups using the `Collection` model. Collections provide a way to categorize bookmarks either through explicit manual selection or automatic filtering rules.

## Collection Types

The behavior of a collection is determined by its `CollectionType` (defined in `app/models/collection.py`), which can be either `MANUAL` or `SMART`.

### Manual Collections
A manual collection (`CollectionType.MANUAL`) acts as a static container. Users explicitly add or remove bookmarks from these collections. The membership is stored as an ordered list of IDs in the `bookmark_ids` attribute.

```python
# Example of adding a bookmark to a manual collection in app/models/collection.py
def add_bookmark(self, bookmark_id: str) -> bool:
    if self.is_smart or bookmark_id in self.bookmark_ids:
        return False
    self.bookmark_ids.append(bookmark_id)
    return True
```

### Smart Collections
A smart collection (`CollectionType.SMART`) is intended to auto-populate based on a `filter_rule`. While the current implementation primarily stores the rule, the `Collection` class includes a `_apply_filter` method that demonstrates how these rules are evaluated against bookmark metadata.

```python
# Logic for smart collection filtering in app/models/collection.py
def _apply_filter(self, bookmarks: list) -> List[str]:
    if not self.filter_rule:
        return []
    keyword = self.filter_rule.lower()
    return [b.id for b in bookmarks if keyword in b.title.lower() or keyword in b.description.lower()]
```

Note that `add_bookmark` will return `False` if called on a smart collection, as membership is governed by the filter rule rather than manual insertion.

## Organization and UI State

The `Collection` model includes built-in support for managing how collections are displayed in a user interface, specifically regarding their priority and the internal order of their contents.

### Pinning
Collections can be "pinned" to indicate they should appear at the top of a list (e.g., a sidebar). This is managed via the `is_pinned` boolean attribute and the `pin()`/`unpin()` methods.

```python
def pin(self) -> None:
    """Pin the collection to the top of the sidebar."""
    self.is_pinned = True
```

### Reordering
For manual collections, the order of bookmarks is preserved in the `bookmark_ids` list. The `reorder()` method allows updating this sequence, provided the new list contains the exact same set of bookmark IDs currently in the collection.

```python
def reorder(self, bookmark_ids: List[str]) -> None:
    if set(bookmark_ids) != set(self.bookmark_ids):
        raise ValueError("Reorder list must contain exactly the same bookmark IDs")
    self.bookmark_ids = bookmark_ids
```

## Service Layer Integration

The `BookmarkService` (in `app/services/bookmark_service.py`) provides the public API for managing collections. It orchestrates the interaction between the `Collection` models and the `BookmarkRepository`.

### Creating a Collection
When creating a collection, the service validates the name and uses `Collection.from_dict` to instantiate the model before persisting it.

```python
def create_collection(self, data: Dict[str, Any]) -> Tuple[Optional[Collection], Optional[str]]:
    name = data.get("name", "").strip()
    if not name:
        return None, "Collection name is required"
    collection = Collection.from_dict(data)
    self._repo.save_collection(collection)
    return collection, None
```

### Managing Membership
The service provides methods like `add_to_collection` and `remove_from_collection` which retrieve the collection from the repository, perform the operation on the model, and then save the updated state.

```python
def add_to_collection(self, collection_id: str, bookmark_id: str) -> bool:
    collection = self._repo.get_collection(collection_id)
    if not collection:
        return False
    if not collection.add_bookmark(bookmark_id):
        return False
    self._repo.save_collection(collection)
    return True
```

## API Endpoints

Collections are exposed via the REST API in `app/routes/collections.py` under the `/api/collections` prefix:

- `GET /`: Lists all collections.
- `POST /`: Creates a new collection (accepts `name`, `type`, and `filter_rule`).
- `GET /<collection_id>`: Retrieves details for a specific collection.
- `PUT /<collection_id>/bookmarks`: Adds a bookmark to a collection (expects `bookmark_id`).
- `DELETE /<collection_id>/bookmarks/<bookmark_id>`: Removes a bookmark from a collection.
