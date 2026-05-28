---
title: Organizing with Collections
description: Understanding the difference between manual bookmark grouping and automated smart collections based on filter rules.
code_symbols: [SYM#97d8a6cbf0c47108aa2beb39fafa695229654067, SYM#664bcdae74f24d832fff86d384111517f11be0db, SYM#67d634120bee630945450829e511171fd936cf36]
section_id: a6792c05-7d67-43fb-9540-ef80aac4e84b_organizing_with_collections
doc_type: guide
section_type: guide
---
In this project, collections provide a way to organize bookmarks into named groups. Unlike tags, which are flat metadata attached to individual bookmarks, collections are distinct entities that maintain an ordered list of bookmarks.

The system supports two distinct behaviors for collections, defined by the `CollectionType` enum in `app/models/collection.py`:

```python
class CollectionType(Enum):
    """The kind of collection."""

    MANUAL = "manual"
    SMART = "smart"
```

## Manual Collections: Curated Lists

A manual collection (`CollectionType.MANUAL`) is a user-curated list where bookmarks are explicitly added or removed. This is the default type when creating a new collection.

### Adding and Removing Bookmarks
Manual collections maintain an internal list of `bookmark_ids`. The `Collection` class provides methods to manage this list, ensuring that duplicates are not added.

```python
def add_bookmark(self, bookmark_id: str) -> bool:
    """Add a bookmark to a manual collection."""
    if self.is_smart or bookmark_id in self.bookmark_ids:
        return False
    self.bookmark_ids.append(bookmark_id)
    return True
```

Note that `add_bookmark` will return `False` if the collection is a smart collection, as smart collections do not allow manual overrides.

### Custom Ordering
One of the primary advantages of manual collections is the ability to define a specific order for bookmarks. The `reorder` method allows users to provide a new list of IDs. To maintain data integrity, this method requires that the new list contains exactly the same set of IDs as the existing collection.

```python
def reorder(self, bookmark_ids: List[str]) -> None:
    """Replace the bookmark ordering."""
    if set(bookmark_ids) != set(self.bookmark_ids):
        raise ValueError("Reorder list must contain exactly the same bookmark IDs")
    self.bookmark_ids = bookmark_ids
```

## Smart Collections: Rule-Based Grouping

Smart collections (`CollectionType.SMART`) automate the grouping process using a `filter_rule`. Instead of manual management, these collections dynamically determine their membership based on bookmark content.

### Filter Logic
The `filter_rule` is a simple string used for case-insensitive substring matching against a bookmark's `title` and `description`. This logic is encapsulated in the `_apply_filter` method:

```python
def _apply_filter(self, bookmarks: list) -> List[str]:
    """Evaluate the filter_rule against a list of bookmarks."""
    if not self.filter_rule:
        return []
    keyword = self.filter_rule.lower()
    return [b.id for b in bookmarks if keyword in b.title.lower() or keyword in b.description.lower()]
```

In the current implementation, smart collections are primarily defined by their metadata. The `_apply_filter` method is an internal utility intended for the service layer to populate the collection's view dynamically.

## Managing Collections via BookmarkService

The `BookmarkService` in `app/services/bookmark_service.py` acts as the primary interface for creating and modifying collections. It ensures that changes are persisted to the `BookmarkRepository`.

### Creating Collections
When creating a collection through the service, the `Collection.from_dict` method is used to initialize the object from raw input data, such as a JSON request body.

```python
def create_collection(self, data: Dict[str, Any]) -> Tuple[Optional[Collection], Optional[str]]:
    """Create a new collection."""
    name = data.get("name", "").strip()
    if not name:
        return None, "Collection name is required"
    collection = Collection.from_dict(data)
    self._repo.save_collection(collection)
    return collection, None
```

### Service-Level Operations
The service layer provides `add_to_collection` and `remove_from_collection` methods that delegate to the model's logic before saving the state:

```python
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

## Serialization and API Integration

Collections are designed to be easily serialized for API responses. The `to_dict` method converts the `Collection` instance into a JSON-safe dictionary, including calculated properties like `size`.

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

This serialization is used directly in the route handlers found in `app/routes/collections.py` to return collection data to the client. For example, the `create_collection` endpoint returns the serialized dictionary with a `201 Created` status.
