---
title: Collections and Smart Filtering
description: Explains the difference between manual bookmark grouping and automated smart collections based on filter rules.
code_symbols: [SYM#97d8a6cbf0c47108aa2beb39fafa695229654067, SYM#67d634120bee630945450829e511171fd936cf36, SYM#664bcdae74f24d832fff86d384111517f11be0db]
section_id: f6621f32-bb74-4d97-aebe-2116f70f5485_collections_and_smart_filtering
doc_type: guide
section_type: guide
---
In this project, collections provide a way to group bookmarks either through manual curation or automated rules. This functionality is primarily implemented in `app/models/collection.py` and managed via the `BookmarkService` in `app/services/bookmark_service.py`.

## Collection Types

The system distinguishes between two types of collections using the `CollectionType` enum:

1.  **Manual Collections (`CollectionType.MANUAL`)**: These act as traditional folders or playlists where users explicitly add or remove specific bookmarks.
2.  **Smart Collections (`CollectionType.SMART`)**: These are dynamic groups that automatically include bookmarks based on a defined `filter_rule`.

## Manual Collections

Manual collections are the default type. They maintain an ordered list of bookmark IDs in the `bookmark_ids` attribute.

### Managing Bookmarks
The `Collection` class provides methods to modify the membership of manual collections. Note that these methods include safety checks to ensure they are not called on smart collections.

```python
# From app/models/collection.py

def add_bookmark(self, bookmark_id: str) -> bool:
    """Add a bookmark to a manual collection.

    Returns:
        True if added, False if already present or collection is smart.
    """
    if self.is_smart or bookmark_id in self.bookmark_ids:
        return False
    self.bookmark_ids.append(bookmark_id)
    return True

def remove_bookmark(self, bookmark_id: str) -> bool:
    """Remove a bookmark from the collection."""
    if bookmark_id not in self.bookmark_ids:
        return False
    self.bookmark_ids.remove(bookmark_id)
    return True
```

### Ordering
Manual collections support custom ordering. The `reorder` method allows replacing the entire list of IDs, provided the set of bookmarks remains identical to the existing one. This prevents accidental loss of bookmarks during a reorder operation.

```python
def reorder(self, bookmark_ids: List[str]) -> None:
    """Replace the bookmark ordering."""
    if set(bookmark_ids) != set(self.bookmark_ids):
        raise ValueError("Reorder list must contain exactly the same bookmark IDs")
    self.bookmark_ids = bookmark_ids
```

## Smart Collections and Filtering

Smart collections use a `filter_rule` (a simple string keyword) to determine membership dynamically. 

### Filtering Logic
The filtering logic is encapsulated in the `_apply_filter` method. It performs a case-insensitive search against both the `title` and `description` of a bookmark.

```python
# From app/models/collection.py

def _apply_filter(self, bookmarks: list) -> List[str]:
    """Evaluate the filter_rule against a list of bookmarks.

    Internal method used by the service layer to populate smart collections.
    """
    if not self.filter_rule:
        return []
    keyword = self.filter_rule.lower()
    return [b.id for b in bookmarks if keyword in b.title.lower() or keyword in b.description.lower()]
```

### Constraints
A key architectural constraint in this codebase is that **smart collections cannot be modified manually**. The `add_bookmark` method explicitly returns `False` if `is_smart` is true. This ensures that the membership of a smart collection remains strictly defined by its `filter_rule`.

## Service and API Integration

The `BookmarkService` acts as the facade for managing collections, handling persistence through the `BookmarkRepository`. The collections are exposed via the `/api/collections` blueprint in `app/routes/collections.py`.

### Creating Collections
When creating a collection through the service, the `Collection.from_dict` factory method is used to parse the input data, defaulting to a manual collection if no type is specified.

```python
# From app/services/bookmark_service.py

def create_collection(self, data: Dict[str, Any]) -> Tuple[Optional[Collection], Optional[str]]:
    """Create a new collection."""
    name = data.get("name", "").strip()
    if not name:
        return None, "Collection name is required"
    collection = Collection.from_dict(data)
    self._repo.save_collection(collection)
    return collection, None
```

### Pinning Collections
Users can "pin" important collections to the top of their sidebar. This is a simple boolean toggle on the `Collection` model:

```python
def pin(self) -> None:
    """Pin the collection to the top of the sidebar."""
    self.is_pinned = True

def unpin(self) -> None:
    """Unpin the collection."""
    self.is_pinned = False
```

## Data Flow and Persistence

The following flow illustrates how collection data is processed:

1.  **Request**: A client sends a request to an endpoint in `app/routes/collections.py`.
2.  **Orchestration**: The route handler calls the corresponding method in `BookmarkService` (e.g., `add_to_collection`).
3.  **Domain Logic**: The service retrieves the `Collection` model from the `BookmarkRepository` and calls its domain methods (e.g., `collection.add_bookmark(id)`).
4.  **Persistence**: If the operation is successful, the service saves the updated `Collection` back to the repository.

## Key Implementation Details

*   **Internal Filtering**: While the `Collection` model contains the `_apply_filter` logic, it is currently an internal method. In the current implementation of `BookmarkService`, smart collections are stored with their rules, but the actual population of the bookmark list for a smart collection is intended to be handled by the consumer or a future service update.
*   **Membership Checking**: The `Collection` class implements `__contains__`, allowing for easy membership checks using the `in` operator: `if bookmark_id in collection: ...`.
*   **ID Generation**: Collection IDs are generated using the first 10 characters of a hex-encoded UUID: `uuid.uuid4().hex[:10]`.
*   **Serialization**: The `to_dict()` method includes a calculated `size` property, which returns the length of the `bookmark_ids` list. For smart collections, this size will reflect the number of bookmarks matching the filter rule once they are populated.

```python
def to_dict(self) -> Dict[str, Any]:
    """Serialise to JSON-safe dictionary."""
    return {
        "id": self.id,
        "name": self.name,
        "type": self.collection_type.value,
        "bookmark_ids": self.bookmark_ids,
        "filter_rule": self.filter_rule,
        "is_pinned": self.is_pinned,
        "size": self.size,
        "created_at": self.created_at.isoformat(),
    }
```

### API Endpoints Summary
The following endpoints in `app/routes/collections.py` facilitate collection management:
- `GET /api/collections/`: Lists all collections.
- `POST /api/collections/`: Creates a new collection.
- `GET /api/collections/<id>`: Retrieves a specific collection.
- `PUT /api/collections/<id>/bookmarks`: Adds a bookmark to a manual collection.
- `DELETE /api/collections/<id>/bookmarks/<bookmark_id>`: Removes a bookmark from a collection.

```python
# Example API usage for adding a bookmark
# PUT /api/collections/a1b2c3d4e5/bookmarks
# Payload: {"bookmark_id": "9f8e7d6c5b"}
```