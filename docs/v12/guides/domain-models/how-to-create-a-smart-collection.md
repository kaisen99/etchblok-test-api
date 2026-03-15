---
title: How to Create a Smart Collection
description: A step-by-step guide on defining filter rules to automatically populate collections with relevant bookmarks.
code_symbols: [SYM#97d8a6cbf0c47108aa2beb39fafa695229654067, SYM#664bcdae74f24d832fff86d384111517f11be0db]
section_id: a7f8a231-47d0-4084-857d-3200bf420776_how_to_create_a_smart_collection
doc_type: how_to
section_type: guide
---
To create a smart collection in this project, you define a collection with a `collection_type` of `smart` and provide a `filter_rule`. Unlike manual collections, smart collections are designed to automatically include bookmarks that match your criteria.

### Create a Smart Collection via API

The most common way to create a smart collection is through the `POST /api/collections` endpoint. You must specify the `type` as `"smart"` and provide a `filter_rule` string.

```json
// POST /api/collections
{
    "name": "Python Resources",
    "type": "smart",
    "filter_rule": "python"
}
```

### Create a Smart Collection in Python

If you are working directly with the model layer, use the `Collection` class from `app.models.collection` and the `CollectionType` enum.

```python
from app.models.collection import Collection, CollectionType

# Define a smart collection that filters for "tutorial"
smart_collection = Collection(
    name="Tutorials",
    collection_type=CollectionType.SMART,
    filter_rule="tutorial"
)

print(f"Is smart: {smart_collection.is_smart}") # True
```

### How Filtering Works

The filtering logic is implemented in the `Collection._apply_filter` method. It performs a case-insensitive search for your `filter_rule` keyword within the **title** and **description** of bookmarks.

```python
# Internal logic in app/models/collection.py
def _apply_filter(self, bookmarks: list) -> List[str]:
    """Evaluate the filter_rule against a list of bookmarks."""
    if not self.filter_rule:
        return []
    keyword = self.filter_rule.lower()
    return [b.id for b in bookmarks if keyword in b.title.lower() or keyword in b.description.lower()]
```

### Variations

#### Pinning a Smart Collection
You can pin a smart collection so it appears at the top of the sidebar. This is done using the `pin()` method on the `Collection` instance.

```python
from app.models.collection import Collection, CollectionType

collection = Collection(
    name="Urgent Reads",
    collection_type=CollectionType.SMART,
    filter_rule="urgent"
)

# Pin the collection
collection.pin()
print(collection.is_pinned) # True
```

#### Creating via BookmarkService
In the application layer, you should use the `BookmarkService` to ensure the collection is properly persisted to the repository.

```python
from app.services.bookmark_service import BookmarkService

service = BookmarkService()
data = {
    "name": "Go Projects",
    "type": "smart",
    "filter_rule": "golang"
}

collection, error = service.create_collection(data)
if not error:
    print(f"Created collection: {collection.id}")
```

### Troubleshooting

**Manual additions are failing**
If you receive an error (or a `400 Bad Request` from the API) when adding a bookmark to a collection, verify the collection type. Smart collections (type `smart`) do not allow manual additions. The `add_bookmark` method in `app/models/collection.py` explicitly blocks this:

```python
def add_bookmark(self, bookmark_id: str) -> bool:
    if self.is_smart or bookmark_id in self.bookmark_ids:
        return False
    # ...
```

**Collection appears empty**
The `_apply_filter` method is currently an internal utility. In the current version of the `BookmarkService`, smart collections are "lazy"—the service layer does not yet automatically call `_apply_filter` to populate the `bookmark_ids` list during standard retrieval or creation. You may need to manually invoke `_apply_filter` if you are implementing custom bookmark listing logic.