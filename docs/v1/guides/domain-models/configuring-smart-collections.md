---
title: Configuring Smart Collections
description: Instructions on setting up manual and smart collections, including the implementation of filter rules for automated grouping.
code_symbols: [SYM#97d8a6cbf0c47108aa2beb39fafa695229654067, SYM#664bcdae74f24d832fff86d384111517f11be0db, SYM#67d634120bee630945450829e511171fd936cf36]
section_id: 6c52a21f-fb2c-4d1a-a1e5-568adfc04d3f_configuring_smart_collections
doc_type: how_to
section_type: guide
---
Collections in this system allow you to group bookmarks either manually or automatically based on search criteria. This is controlled by the `CollectionType` enum and the `filter_rule` attribute of the `Collection` class.

## Creating a Manual Collection

Manual collections require you to explicitly add or remove bookmarks. To create one, use the `BookmarkService.create_collection` method or the `/api/collections` endpoint.

```python
from app.services.bookmark_service import BookmarkService
from app.models.collection import CollectionType

service = BookmarkService()

# Create a manual collection via the service layer
data = {
    "name": "Research Project",
    "type": "manual"
}
collection, error = service.create_collection(data)

if collection:
    print(f"Created collection: {collection.name} (ID: {collection.id})")
```

### Adding and Removing Bookmarks

For manual collections, you manage membership using the service layer methods which delegate to `Collection.add_bookmark` and `Collection.remove_bookmark`.

```python
# Add a bookmark to the collection
success = service.add_to_collection(collection_id="coll_123", bookmark_id="book_456")

# Remove a bookmark from the collection
success = service.remove_from_collection(collection_id="coll_123", bookmark_id="book_456")
```

## Configuring a Smart Collection

Smart collections automatically identify bookmarks based on a `filter_rule`. When creating a smart collection, you must set the `type` to `smart` and provide a keyword in the `filter_rule`.

```python
# Create a smart collection via the service layer
smart_data = {
    "name": "Python Articles",
    "type": "smart",
    "filter_rule": "python"
}
smart_collection, error = service.create_collection(smart_data)
```

### How Filter Rules Work

The filtering logic is implemented in `Collection._apply_filter`. It performs a case-insensitive keyword match against both the **title** and **description** of a bookmark.

```python
# Internal logic used to determine membership
def _apply_filter(self, bookmarks: list) -> List[str]:
    if not self.filter_rule:
        return []
    keyword = self.filter_rule.lower()
    return [b.id for b in bookmarks if keyword in b.title.lower() or keyword in b.description.lower()]
```

## Organizing Collections

### Pinning Collections

You can pin important collections so they appear at the top of the sidebar. This toggles the `is_pinned` attribute.

```python
collection = service.get_collection("coll_123")
collection.pin()
# To unpin: collection.unpin()

# Save the change back to the repository
service._repo.save_collection(collection)
```

### Reordering Bookmarks

In manual collections, you can define a specific order for the bookmarks. The `reorder` method requires a list containing the exact same set of bookmark IDs currently in the collection.

```python
collection = service.get_collection("coll_123")
new_order = ["id_3", "id_1", "id_2"] # Must contain all existing IDs

try:
    collection.reorder(new_order)
    service._repo.save_collection(collection)
except ValueError as e:
    print(f"Reorder failed: {e}")
```

## Troubleshooting and Limitations

### Smart Collections are Read-Only
You cannot manually add bookmarks to a smart collection. Calling `add_bookmark` on a collection where `collection_type` is `CollectionType.SMART` will return `False`.

```python
# This will fail for smart collections
success = collection.add_bookmark("some_id") 
# success is False if collection.is_smart is True
```

### Filter Rule Scope
The `filter_rule` currently only supports a single keyword match. It does not support complex queries (like `AND`/`OR` logic) or filtering by tags.

### Lazy Population
In the current implementation, the `_apply_filter` method is defined in the `Collection` model but is not automatically invoked by the `BookmarkService` during standard CRUD operations. Smart collections store their `filter_rule` but require the service layer to be extended to populate `bookmark_ids` using the filter logic.

### Reordering Constraints
The `reorder` method will raise a `ValueError` if the provided list of IDs does not match the existing `bookmark_ids` set exactly. You cannot use `reorder` to add or remove bookmarks; it is strictly for changing the sequence of existing members.
